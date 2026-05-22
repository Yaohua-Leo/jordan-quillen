"""Report experiment status without fabricating results."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    experiments_dir = root / "experiments"
    for path in sorted(experiments_dir.glob("[0-9][0-9][0-9]-*")):
        print(f"{path.name}: not run by default")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
