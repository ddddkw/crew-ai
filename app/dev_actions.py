import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from workspace_fs import WorkspacePathError, ensure_within_workspace, normalize_workspace_path


class DevActionError(RuntimeError):
    pass


@dataclass
class FileActionResult:
    applied_files: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


@dataclass
class CommandActionResult:
    command: str
    returncode: int
    stdout: str
    stderr: str

    def format(self) -> str:
        parts = [f"$ {self.command}", f"exit code: {self.returncode}"]
        if self.stdout.strip():
            parts.append("stdout:")
            parts.append(_trim_output(self.stdout))
        if self.stderr.strip():
            parts.append("stderr:")
            parts.append(_trim_output(self.stderr))
        return "\n".join(parts)


FILE_BLOCK_RE = re.compile(r"```file(?P<header>[^\n]*)\n(?P<content>.*?)```", re.DOTALL)
COMMAND_BLOCK_RE = re.compile(r"```(?:command|shell|bash|powershell)(?P<header>[^\n]*)\n(?P<content>.*?)```", re.DOTALL)


def _trim_output(text: str, limit: int = 12000) -> str:
    text = text or ""
    if len(text) <= limit:
        return text.rstrip()
    return f"{text[:limit].rstrip()}\n... output truncated ..."


def _parse_file_path(header: str) -> str:
    header = str(header or "").strip()
    match = re.search(r"""path=(?:"([^"]+)"|'([^']+)'|(\S+))""", header)
    if match:
        path = next(group for group in match.groups() if group)
    else:
        path = header
    path = path.strip().strip('"').strip("'")
    if not path:
        raise DevActionError("file block is missing a path")
    return path


def _relative_to_workspace(root: str, target: str) -> str:
    workspace_root = Path(normalize_workspace_path(root))
    return Path(target).resolve(strict=False).relative_to(workspace_root).as_posix()


def _resolve_workspace_target(root: str, requested_path: str) -> tuple[str, str]:
    workspace_root = Path(normalize_workspace_path(root))
    requested = Path(requested_path)
    target = requested if requested.is_absolute() else workspace_root / requested
    try:
        resolved = ensure_within_workspace(str(workspace_root), str(target))
    except WorkspacePathError as exc:
        raise DevActionError(str(exc)) from exc
    return resolved, _relative_to_workspace(str(workspace_root), resolved)


def _extract_file_blocks(text: str) -> list[tuple[str, str]]:
    blocks = []
    for match in FILE_BLOCK_RE.finditer(text or ""):
        blocks.append((_parse_file_path(match.group("header")), match.group("content")))
    return blocks


def _extract_command_blocks(text: str) -> list[str]:
    return [match.group("content").strip() for match in COMMAND_BLOCK_RE.finditer(text or "") if match.group("content").strip()]


def apply_file_blocks(workspace, assistant_text: str) -> FileActionResult:
    result = FileActionResult()
    file_blocks = _extract_file_blocks(assistant_text)
    if not file_blocks:
        return result

    if not workspace.allow_write:
        result.skipped.append("write permission is disabled")
        return result

    for requested_path, content in file_blocks:
        target, relative_path = _resolve_workspace_target(workspace.path, requested_path)
        target_path = Path(target)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        result.applied_files.append(relative_path)

    return result


def run_workspace_test_command(workspace, timeout: int = 120) -> CommandActionResult:
    if not workspace.allow_command:
        raise DevActionError("command permission is disabled")
    command = str(workspace.test_command or "").strip()
    if not command:
        raise DevActionError("workspace test command is not configured")

    try:
        completed = subprocess.run(
            command,
            cwd=normalize_workspace_path(workspace.path),
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise DevActionError(f"test command timed out after {timeout} seconds") from exc

    return CommandActionResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


def _run_requested_commands(workspace, assistant_text: str) -> list[CommandActionResult]:
    configured_command = str(workspace.test_command or "").strip()
    command_results = []
    for requested_command in _extract_command_blocks(assistant_text):
        if requested_command != configured_command:
            raise DevActionError("development sessions can only run the configured workspace test command")
        command_results.append(run_workspace_test_command(workspace))
    return command_results


def apply_development_actions(session, workspace, assistant_text: str) -> str:
    file_result = apply_file_blocks(workspace, assistant_text)
    command_results = _run_requested_commands(workspace, assistant_text)

    if file_result.applied_files and workspace.allow_command and workspace.test_command and not command_results:
        command_results.append(run_workspace_test_command(workspace))

    summary_lines = []
    if file_result.applied_files:
        summary_lines.append("已写入文件: " + ", ".join(file_result.applied_files))
        session.logs = list(session.logs) + [f"已写入文件: {', '.join(file_result.applied_files)}"]
    if file_result.skipped:
        summary_lines.append("已跳过动作: " + "; ".join(file_result.skipped))
        session.logs = list(session.logs) + [f"已跳过动作: {'; '.join(file_result.skipped)}"]
    for command_result in command_results:
        formatted = command_result.format()
        session.test_result = formatted
        summary_lines.append("已运行测试命令:\n" + formatted)
        session.logs = list(session.logs) + [f"已运行测试命令，退出码: {command_result.returncode}"]

    return "\n\n".join(summary_lines)
