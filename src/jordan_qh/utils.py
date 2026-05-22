"""Small shared helpers."""

from pathlib import Path


def repo_root_from(path: Path) -> Path:
    """Find the nearest ancestor containing `pyproject.toml`."""
    current = path.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    msg = f"could not find repository root from {path}"
    raise FileNotFoundError(msg)
