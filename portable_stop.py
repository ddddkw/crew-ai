from __future__ import annotations

import ctypes
import json
import os
import sys
import time
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROCESS_STATE_FILENAME = "portable-processes.json"
ALLOWED_PROCESS_NAMES = {"crewai studio.exe", "python.exe", "pythonw.exe"}
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
SYNCHRONIZE = 0x00100000
WAIT_TIMEOUT_MS = 5000


@dataclass(frozen=True)
class ProcessEntry:
    label: str
    pid: int


@dataclass(frozen=True)
class StopResult:
    pid: int
    label: str
    status: str
    detail: str


def runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def process_state_path(root: Path) -> Path:
    return root / "logs" / PROCESS_STATE_FILENAME


def _normalize_path(path: str | Path) -> str:
    return str(Path(path).resolve()).rstrip("\\/").casefold()


def path_is_under_root(path: str | Path, root: str | Path) -> bool:
    root_text = _normalize_path(root)
    path_text = _normalize_path(path)
    return path_text == root_text or path_text.startswith(root_text + "\\")


def _safe_int(value: Any) -> int | None:
    try:
        pid = int(value)
    except (TypeError, ValueError):
        return None
    return pid if pid > 0 else None


def load_process_entries(root: Path) -> list[ProcessEntry]:
    path = process_state_path(root)
    if not path.exists():
        return []

    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    state_root = state.get("root")
    if state_root and not path_is_under_root(state_root, root):
        return []

    entries: list[ProcessEntry] = []
    seen: set[int] = set()
    for label, key in (("Streamlit runtime", "streamlit_pid"), ("CrewAI Studio launcher", "launcher_pid")):
        pid = _safe_int(state.get(key))
        if pid is not None and pid not in seen:
            entries.append(ProcessEntry(label=label, pid=pid))
            seen.add(pid)
    return entries


def _kernel32() -> ctypes.WinDLL:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel32.TerminateProcess.restype = wintypes.BOOL
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    return kernel32


def _open_process(pid: int, access: int) -> wintypes.HANDLE | None:
    handle = _kernel32().OpenProcess(access, False, pid)
    return handle or None


def process_image_path(pid: int) -> str | None:
    if os.name != "nt":
        return None

    kernel32 = _kernel32()
    handle = _open_process(pid, PROCESS_QUERY_LIMITED_INFORMATION)
    if not handle:
        return None

    try:
        size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if not kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return None
        return buffer.value
    finally:
        kernel32.CloseHandle(handle)


def terminate_pid(pid: int) -> bool:
    if os.name != "nt":
        return False

    kernel32 = _kernel32()
    access = PROCESS_TERMINATE | SYNCHRONIZE
    handle = _open_process(pid, access)
    if not handle:
        return False

    try:
        if not kernel32.TerminateProcess(handle, 0):
            return False
        kernel32.WaitForSingleObject(handle, WAIT_TIMEOUT_MS)
        return True
    finally:
        kernel32.CloseHandle(handle)


def stop_entry(entry: ProcessEntry, root: Path) -> StopResult:
    image_path = process_image_path(entry.pid)
    if not image_path:
        return StopResult(entry.pid, entry.label, "not-running", "Process is not running or cannot be queried.")

    if not path_is_under_root(image_path, root):
        return StopResult(entry.pid, entry.label, "skipped", f"Process is outside this portable folder: {image_path}")

    process_name = Path(image_path).name.casefold()
    if process_name not in ALLOWED_PROCESS_NAMES:
        return StopResult(entry.pid, entry.label, "skipped", f"Unexpected process name: {Path(image_path).name}")

    if terminate_pid(entry.pid):
        return StopResult(entry.pid, entry.label, "stopped", image_path)
    return StopResult(entry.pid, entry.label, "failed", "Process matched this folder, but termination failed.")


def stop_from_state(root: Path) -> list[StopResult]:
    entries = load_process_entries(root)
    if not entries:
        return [StopResult(0, "CrewAI Studio", "not-running", "No running process state was found.")]

    results = [stop_entry(entry, root) for entry in entries]
    try:
        process_state_path(root).unlink()
    except FileNotFoundError:
        pass
    return results


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _print_results(results: list[StopResult]) -> None:
    for result in results:
        if result.status == "stopped":
            print(f"Stopped {result.label} ({result.pid})")
        elif result.status == "not-running":
            print(result.detail)
        else:
            print(f"{result.status}: {result.label} ({result.pid}) - {result.detail}")


def _pause_if_interactive() -> None:
    if _truthy_env("CREWAI_STUDIO_STOP_NO_PAUSE"):
        return
    if os.name == "nt" and sys.stdin and sys.stdin.isatty():
        try:
            input("Press Enter to close...")
        except EOFError:
            time.sleep(1.5)


def main() -> int:
    root = runtime_root()
    results = stop_from_state(root)
    _print_results(results)
    _pause_if_interactive()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
