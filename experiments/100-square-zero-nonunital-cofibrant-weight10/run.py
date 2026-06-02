"""Run Experiment 100: one-generator bounded cofibrant cell computation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-weight", type=int, default=10)
    return parser.parse_args()


def main() -> int:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from jordan_qh.one_generator_cofibrant import compute_exp100, write_run_outputs

    args = parse_args()
    run = compute_exp100(max_weight=args.max_weight, output_dir=EXPERIMENT_DIR)
    write_run_outputs(run, EXPERIMENT_DIR)
    print(
        "EXP100 completed "
        f"weights={run.results['completed_weights']} "
        f"skipped={run.results['skipped_weights']} "
        f"failed={run.results['failed_weights']} "
        f"V1={len(run.results['computed_V1_cells'])} "
        f"V2={len(run.results['computed_V2_cells'])} "
        f"passed={run.results['passed']}",
    )
    return 0 if run.results["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
