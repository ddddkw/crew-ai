from __future__ import annotations

import logging
import os
import importlib
import json
import shutil
import socket
import subprocess
import sys
import threading
import time
import traceback
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_PORT = 8501
PORT_SEARCH_LIMIT = 25
PROCESS_STATE_FILENAME = "portable-processes.json"
_DLL_DIRECTORY_HANDLES = []


@dataclass(frozen=True)
class PortableRuntime:
    root: Path
    app_script: Path
    env_path: Path
    database_path: Path
    knowledge_dir: Path
    logs_dir: Path


def runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _existing_paths(value: str) -> list[str]:
    return [item for item in value.split(os.pathsep) if item]


def _prepend_env_path(variable: str, paths: list[Path]) -> None:
    existing = _existing_paths(os.environ.get(variable, ""))
    additions = [str(path) for path in paths if path.exists() and str(path) not in existing]
    if additions:
        os.environ[variable] = os.pathsep.join(additions + existing)


def _prepend_import_paths(paths: list[Path]) -> None:
    valid_paths = [str(path) for path in paths if path.exists()]
    for path in reversed(valid_paths):
        if path in sys.path:
            sys.path.remove(path)
        sys.path.insert(0, path)
    _prepend_env_path("PYTHONPATH", [Path(path) for path in valid_paths])


def _runtime_import_paths(root: Path) -> list[Path]:
    python_runtime = root / "python-runtime"
    site_packages = python_runtime / "Lib" / "site-packages"
    return [
        site_packages,
        site_packages / "win32",
        site_packages / "win32" / "lib",
        site_packages / "Pythonwin",
        python_runtime / "Lib",
        python_runtime / "DLLs",
        root / "app",
        root,
    ]


def _runtime_dll_paths(root: Path) -> list[Path]:
    python_runtime = root / "python-runtime"
    return [
        python_runtime / "DLLs",
        python_runtime / "Lib" / "site-packages" / "torch" / "lib",
        python_runtime / "Lib" / "site-packages" / "onnxruntime" / "capi",
        python_runtime / "Lib" / "site-packages" / "cv2",
        python_runtime / "Lib" / "site-packages" / "pywin32_system32",
    ]


def _add_dll_search_paths(paths: list[Path]) -> None:
    valid_paths = [path for path in paths if path.exists()]
    _prepend_env_path("PATH", valid_paths)
    add_dll_directory = getattr(os, "add_dll_directory", None)
    if add_dll_directory is None:
        return
    for path in valid_paths:
        _DLL_DIRECTORY_HANDLES.append(add_dll_directory(str(path)))


def _ensure_env_file(root: Path) -> Path:
    env_path = root / ".env"
    if env_path.exists():
        return env_path

    example_path = root / ".env_example"
    if example_path.exists():
        shutil.copyfile(example_path, env_path)
    else:
        env_path.write_text('AGENTOPS_ENABLED="False"\n', encoding="utf-8")
    return env_path


def _load_env_file(env_path: Path) -> None:
    try:
        dotenv_module_name = os.environ.get("CREWAI_STUDIO_DOTENV_MODULE", "dotenv")
        dotenv = importlib.import_module(dotenv_module_name)
    except ModuleNotFoundError:
        return
    dotenv.load_dotenv(env_path, override=False)


def _sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def prepare_runtime(root: str | Path | None = None) -> PortableRuntime:
    portable_root = Path(root).resolve() if root is not None else runtime_root()
    app_script = portable_root / "app" / "app.py"
    if not app_script.exists():
        raise FileNotFoundError(f"Streamlit entrypoint not found: {app_script}")

    os.chdir(portable_root)

    env_path = _ensure_env_file(portable_root)
    logs_dir = portable_root / "logs"
    knowledge_dir = portable_root / "knowledge"
    database_path = portable_root / "crewai.db"
    logs_dir.mkdir(exist_ok=True)
    knowledge_dir.mkdir(exist_ok=True)

    _prepend_import_paths(_runtime_import_paths(portable_root))
    _add_dll_search_paths(_runtime_dll_paths(portable_root))
    _load_env_file(env_path)

    os.environ["CREWAI_STUDIO_PORTABLE_ROOT"] = str(portable_root)
    os.environ.setdefault("DB_URL", _sqlite_url(database_path))

    return PortableRuntime(
        root=portable_root,
        app_script=app_script,
        env_path=env_path,
        database_path=database_path,
        knowledge_dir=knowledge_dir,
        logs_dir=logs_dir,
    )


def _port_is_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def find_available_port(preferred_port: int = DEFAULT_PORT) -> int:
    for port in range(preferred_port, preferred_port + PORT_SEARCH_LIMIT):
        if _port_is_available(port):
            return port
    raise RuntimeError(f"No available local port found from {preferred_port} to {preferred_port + PORT_SEARCH_LIMIT - 1}")


def build_streamlit_options(port: int = DEFAULT_PORT) -> dict[str, Any]:
    return {
        "server.address": "127.0.0.1",
        "server.port": port,
        "server.headless": True,
        "server.fileWatcherType": "none",
        "browser.gatherUsageStats": False,
        "global.developmentMode": False,
    }


def portable_python_executable(root: Path) -> Path:
    override = os.environ.get("CREWAI_STUDIO_PYTHON")
    if override:
        candidate = Path(override)
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"Configured Python executable not found: {candidate}")

    runtime_dir = root / "python-runtime"
    candidates = [
        runtime_dir / "python.exe",
        runtime_dir / "pythonw.exe",
        runtime_dir / "Scripts" / "python.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Portable Python executable not found under: {runtime_dir}")


def build_streamlit_command(runtime: PortableRuntime, port: int) -> list[str]:
    return [
        str(portable_python_executable(runtime.root)),
        "-m",
        "streamlit",
        "run",
        str(runtime.app_script),
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        "--server.headless=true",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
    ]


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _child_creation_flags() -> int:
    if os.name != "nt" or _truthy_env("CREWAI_STUDIO_SHOW_CHILD_CONSOLE"):
        return 0
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def launch_streamlit_process(runtime: PortableRuntime, port: int) -> subprocess.Popen:
    command = build_streamlit_command(runtime, port)
    logging.info("Launching Streamlit child process: %s", " ".join(command))

    stdout_handle = None
    stderr_handle = None
    try:
        if not _truthy_env("CREWAI_STUDIO_SHOW_CHILD_CONSOLE"):
            stdout_handle = (runtime.logs_dir / "streamlit.stdout.log").open("ab")
            stderr_handle = (runtime.logs_dir / "streamlit.stderr.log").open("ab")

        return subprocess.Popen(
            command,
            cwd=runtime.root,
            env=os.environ.copy(),
            stdout=stdout_handle,
            stderr=stderr_handle,
            creationflags=_child_creation_flags(),
        )
    finally:
        if stdout_handle is not None:
            stdout_handle.close()
        if stderr_handle is not None:
            stderr_handle.close()


def process_state_path(runtime: PortableRuntime) -> Path:
    return runtime.logs_dir / PROCESS_STATE_FILENAME


def write_process_state(runtime: PortableRuntime, process: subprocess.Popen, port: int, url: str) -> None:
    state = {
        "root": str(runtime.root),
        "launcher_pid": os.getpid(),
        "streamlit_pid": process.pid,
        "port": port,
        "url": url,
        "started_at": time.time(),
    }
    path = process_state_path(runtime)
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    os.replace(temporary_path, path)


def remove_process_state(runtime: PortableRuntime) -> None:
    try:
        process_state_path(runtime).unlink()
    except FileNotFoundError:
        pass


def open_browser_later(url: str, delay_seconds: float = 2.0) -> None:
    def _open() -> None:
        time.sleep(delay_seconds)
        webbrowser.open(url)

    threading.Thread(target=_open, daemon=True).start()


def should_open_browser() -> bool:
    return os.environ.get("CREWAI_STUDIO_NO_BROWSER", "").strip().lower() not in {"1", "true", "yes", "on"}


def configure_logging(logs_dir: Path) -> None:
    logging.basicConfig(
        filename=logs_dir / "launcher.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
    )


def write_emergency_crash_report(exc: BaseException) -> None:
    report = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    candidate_roots = []
    try:
        candidate_roots.append(runtime_root())
    except BaseException:
        pass
    try:
        candidate_roots.append(Path.cwd())
    except BaseException:
        pass

    for root in candidate_roots:
        try:
            logs_dir = root / "logs"
            logs_dir.mkdir(exist_ok=True)
            (logs_dir / "launcher-crash.log").write_text(report, encoding="utf-8")
        except BaseException:
            continue


def main() -> None:
    runtime = prepare_runtime()
    configure_logging(runtime.logs_dir)

    preferred_port = int(os.environ.get("CREWAI_STUDIO_PORT", DEFAULT_PORT))
    port = find_available_port(preferred_port)
    url = f"http://127.0.0.1:{port}"
    logging.info("Starting CrewAI Studio at %s", url)
    if should_open_browser():
        open_browser_later(url)

    process = launch_streamlit_process(runtime, port)
    write_process_state(runtime, process, port, url)
    try:
        exit_code = process.wait()
    finally:
        remove_process_state(runtime)

    logging.info("Streamlit child process exited with code %s", exit_code)
    if exit_code != 0:
        raise RuntimeError(f"Streamlit exited with code {exit_code}. See logs/streamlit.stderr.log for details.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        write_emergency_crash_report(exc)
        fallback_logs = runtime_root() / "logs"
        fallback_logs.mkdir(exist_ok=True)
        configure_logging(fallback_logs)
        logging.exception("CrewAI Studio portable launcher failed")
        raise
