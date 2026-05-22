"""Validate claim files for required research metadata."""

from __future__ import annotations

from pathlib import Path

REQUIRED_MARKERS = (
    "Status:",
    "Statement:",
    "Dependencies:",
    "Proof sketch:",
    "References:",
    "Verification notes:",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    claim_dir = root / "theory" / "claims"
    failures: list[str] = []

    for path in sorted(claim_dir.glob("CLAIM-*.md")):
        text = path.read_text(encoding="utf-8")
        missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
        if missing:
            failures.append(f"{path.relative_to(root)} missing {', '.join(missing)}")

    if not list(claim_dir.glob("CLAIM-*.md")):
        failures.append("no claim files found")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("claim metadata ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
