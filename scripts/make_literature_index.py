"""Print a lightweight literature note index."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    notes_dir = root / "literature" / "notes"
    print("# Literature Index")
    for path in sorted(notes_dir.glob("*.md")):
        title = path.read_text(encoding="utf-8").splitlines()[0].removeprefix("# ")
        print(f"- [{title}]({path.relative_to(root).as_posix()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
