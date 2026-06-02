"""Run Experiment 012: high-weight rank backend validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[1]


def parse_weight_list(value: str) -> tuple[int, ...]:
    if not value.strip():
        return ()
    weights: set[int] = set()
    for part in value.split(","):
        item = part.strip()
        if not item:
            continue
        try:
            weight = int(item)
        except ValueError as exc:
            msg = "--force-recompute-weights must contain positive integers"
            raise argparse.ArgumentTypeError(msg) from exc
        if weight < 1:
            msg = "--force-recompute-weights must contain positive integers"
            raise argparse.ArgumentTypeError(msg)
        weights.add(weight)
    return tuple(sorted(weights))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-weight", type=int, default=10)
    parser.add_argument(
        "--mode",
        choices=("dry", "validation", "overnight"),
        default="dry",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--reference-exp011",
        type=Path,
        default=Path("experiments/011-v2-cells-no-Q/data/by_weight_W10.json"),
    )
    parser.add_argument("--max-raw-terms-per-space", type=int, default=120_000)
    parser.add_argument("--max-quotient-dim", type=int, default=500_000)
    parser.add_argument("--max-matrix-nnz", type=int, default=50_000_000)
    parser.add_argument("--max-runtime-per-weight", type=float, default=None)
    parser.add_argument("--max-memory-gb", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--matrix-workers", type=int, default=1)
    parser.add_argument(
        "--rank-backend",
        choices=("modular_sparse_v2",),
        default="modular_sparse_v2",
    )
    parser.add_argument("--rank-progress-interval", type=int, default=10_000)
    parser.add_argument("--rank-progress-seconds", type=float, default=15.0)
    parser.add_argument("--max-rank-seconds", type=float, default=None)
    parser.add_argument(
        "--force-recompute-weights",
        type=parse_weight_list,
        default=(),
        help="Comma-separated weights to recompute even when --resume is set.",
    )
    return parser.parse_args()


def main() -> int:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from jordan_qh.high_weight_rank_backend_validation import (
        compute_exp012,
        write_exp012_outputs,
    )
    from jordan_qh.v2_cells_no_q import Exp011Thresholds

    args = parse_args()
    thresholds = Exp011Thresholds(
        max_raw_terms_per_space=args.max_raw_terms_per_space,
        max_quotient_dim=args.max_quotient_dim,
        max_matrix_nnz=args.max_matrix_nnz,
        max_runtime_per_weight=args.max_runtime_per_weight,
        max_memory_gb=args.max_memory_gb,
        workers=args.workers,
        matrix_workers=args.matrix_workers,
        rank_backend=args.rank_backend,
        rank_progress_interval=args.rank_progress_interval,
        rank_progress_seconds=args.rank_progress_seconds,
        max_rank_seconds=args.max_rank_seconds,
    )
    run = compute_exp012(
        max_weight=args.max_weight,
        mode=args.mode,
        output_dir=EXPERIMENT_DIR,
        reference_exp011=args.reference_exp011,
        thresholds=thresholds,
        resume=args.resume,
        force_recompute_weights=args.force_recompute_weights,
    )
    write_exp012_outputs(run, EXPERIMENT_DIR)
    print(
        "EXP012 completed "
        f"weights={run.results['completed_weights']} "
        f"skipped={run.results['skipped_weights']} "
        f"failed={run.results['failed_weights']} "
        f"reproduction={run.results['reproduction']['matches_exp011_reference']} "
        f"passed={run.results['passed']}",
    )
    return 0 if run.results["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
