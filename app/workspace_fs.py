import os
from pathlib import Path


IGNORED_DIR_NAMES = {
    ".crewai_storage",
    ".git",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".streamlit",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}


class WorkspacePathError(ValueError):
    pass


def normalize_workspace_path(path: str) -> str:
    if not path or not str(path).strip():
        raise WorkspacePathError("Workspace path cannot be empty.")

    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise WorkspacePathError(f"Workspace path does not exist: {resolved}")
    if not resolved.is_dir():
        raise WorkspacePathError(f"Workspace path is not a directory: {resolved}")
    return str(resolved)


def ensure_within_workspace(root: str, target: str) -> str:
    workspace_root = Path(normalize_workspace_path(root))
    resolved_target = Path(target).expanduser().resolve(strict=False)

    try:
        os.path.commonpath([str(workspace_root), str(resolved_target)])
    except ValueError as exc:
        raise WorkspacePathError("Target path is outside the workspace.") from exc

    if os.path.commonpath([str(workspace_root), str(resolved_target)]) != str(workspace_root):
        raise WorkspacePathError("Target path is outside the workspace.")
    return str(resolved_target)


def _should_skip_dir(path: Path) -> bool:
    return path.name in IGNORED_DIR_NAMES or path.name.startswith(".")


def get_parent_directory(path: str) -> str:
    resolved = Path(path).expanduser().resolve()
    parent = resolved.parent
    return str(parent if parent != resolved else resolved)


def list_selectable_directories(path: str, max_items: int = 120) -> list[dict]:
    current = Path(normalize_workspace_path(path))
    directories = []

    try:
        children = sorted(current.iterdir(), key=lambda item: item.name.lower())
    except OSError:
        return []

    for child in children:
        if len(directories) >= max_items:
            break
        if not child.is_dir() or _should_skip_dir(child):
            continue
        directories.append(
            {
                "name": child.name,
                "path": str(child.resolve()),
                "type": "dir",
            }
        )
    return directories


def build_file_tree(root: str, max_depth: int = 3, max_items: int = 120) -> list[dict]:
    workspace_root = Path(normalize_workspace_path(root))
    items = []

    def visit(directory: Path, depth: int) -> None:
        if len(items) >= max_items or depth > max_depth:
            return

        try:
            children = sorted(directory.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
        except OSError:
            return

        for child in children:
            if len(items) >= max_items:
                return
            if child.is_dir() and _should_skip_dir(child):
                continue

            relative_path = child.relative_to(workspace_root).as_posix()
            item_type = "dir" if child.is_dir() else "file"
            items.append(
                {
                    "name": child.name,
                    "path": relative_path,
                    "type": item_type,
                    "depth": depth,
                }
            )

            if child.is_dir() and depth < max_depth:
                visit(child, depth + 1)

    visit(workspace_root, 0)
    return items


def format_file_tree(tree: list[dict]) -> str:
    if not tree:
        return "(empty)"

    lines = []
    for item in tree:
        indent = "  " * int(item.get("depth", 0))
        suffix = "/" if item.get("type") == "dir" else ""
        lines.append(f"{indent}{item.get('name', '')}{suffix}")
    return "\n".join(lines)
