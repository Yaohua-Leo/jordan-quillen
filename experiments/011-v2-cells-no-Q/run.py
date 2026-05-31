"""Run Experiment 011: V2-cell candidates before applying Q."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-weight", type=int, default=8)
    parser.add_argument(
        "--mode",
        choices=("dry", "validation", "overnight"),
        default="dry",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-raw-terms-per-space", type=int, default=10_000)
    parser.add_argument("--max-quotient-dim", type=int, default=3_000)
    parser.add_argument("--max-matrix-nnz", type=int, default=250_000)
    parser.add_argument("--max-runtime-per-weight", type=float, default=None)
    parser.add_argument("--max-memory-gb", type=float, default=None)
    return parser.parse_args()


def main() -> int:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from jordan_qh.v2_cells_no_q import (
        Exp011Thresholds,
        compute_exp011,
        write_run_outputs,
    )

    args = parse_args()
    thresholds = Exp011Thresholds(
        max_raw_terms_per_space=args.max_raw_terms_per_space,
        max_quotient_dim=args.max_quotient_dim,
        max_matrix_nnz=args.max_matrix_nnz,
        max_runtime_per_weight=args.max_runtime_per_weight,
        max_memory_gb=args.max_memory_gb,
    )
    run = compute_exp011(
        max_weight=args.max_weight,
        mode=args.mode,
        output_dir=EXPERIMENT_DIR,
        thresholds=thresholds,
        resume=args.resume,
    )
    write_run_outputs(run, EXPERIMENT_DIR)
    print(
        "EXP011 completed "
        f"weights={run.results['completed_weights']} "
        f"skipped={run.results['skipped_weights']} "
        f"failed={run.results['failed_weights']} "
        f"passed={run.results['passed']}",
    )
    return 0 if run.results["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
