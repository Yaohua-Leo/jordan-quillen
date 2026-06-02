"""Run Experiment 014: backend differential and ideal-stability audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-weight", type=int, default=10)
    parser.add_argument("--max-degree", type=int, default=2)
    parser.add_argument(
        "--mode",
        choices=("dry", "validation", "overnight"),
        default="dry",
    )
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--max-memory-gb", type=float, default=20.0)
    parser.add_argument(
        "--multiplier-degrees",
        default="0,1,2",
        help="Comma-separated multiplier degrees to audit.",
    )
    return parser.parse_args()


def _parse_multiplier_degrees(raw: str) -> tuple[int, ...]:
    values = tuple(
        sorted({int(value.strip()) for value in raw.split(",") if value.strip()})
    )
    if not values:
        msg = "multiplier-degrees must contain at least one integer"
        raise ValueError(msg)
    if any(value < 0 for value in values):
        msg = "multiplier-degrees must be nonnegative"
        raise ValueError(msg)
    return values


def main() -> int:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from jordan_qh.backend_ideal_audit import compute_exp014, write_exp014_outputs

    args = parse_args()
    run = compute_exp014(
        max_weight=args.max_weight,
        max_degree=args.max_degree,
        mode=args.mode,
        output_dir=EXPERIMENT_DIR,
        workers=args.workers,
        max_memory_gb=args.max_memory_gb,
        multiplier_degrees=_parse_multiplier_degrees(args.multiplier_degrees),
    )
    write_exp014_outputs(run, EXPERIMENT_DIR)
    print(
        "EXP014 relation_rows_checked="
        f"{run.results['relation_rows_checked']} "
        "differential_failures="
        f"{run.results['differential_failures']} "
        "multiplication_failures="
        f"{run.results['multiplication_failures']} "
        f"passed={run.results['passed']}",
    )
    return 0 if run.results["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
