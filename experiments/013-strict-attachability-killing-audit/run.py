"""Run Experiment 013: strict attachability and low-to-high killing audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-weight", type=int, default=10)
    parser.add_argument(
        "--mode",
        choices=("dry", "validation", "overnight"),
        default="dry",
    )
    parser.add_argument(
        "--reference-v2-cells",
        type=Path,
        default=REPO_ROOT
        / "experiments"
        / "011-v2-cells-no-Q"
        / "data"
        / "v2_cells_W10.json",
    )
    parser.add_argument(
        "--reference-by-weight",
        type=Path,
        default=REPO_ROOT
        / "experiments"
        / "011-v2-cells-no-Q"
        / "data"
        / "by_weight_W10.json",
    )
    parser.add_argument(
        "--attach-policy",
        choices=("strict-prefix",),
        default="strict-prefix",
    )
    parser.add_argument(
        "--rank-backend",
        choices=("modular_sparse", "modular_sparse_v2"),
        default="modular_sparse_v2",
    )
    parser.add_argument("--max-raw-terms-per-space", type=int, default=500_000)
    parser.add_argument("--max-quotient-dim", type=int, default=1_000_000)
    parser.add_argument("--max-matrix-nnz", type=int, default=100_000_000)
    parser.add_argument("--max-runtime-per-weight", type=float, default=None)
    parser.add_argument("--max-memory-gb", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--matrix-workers", type=int, default=1)
    parser.add_argument("--rank-progress-interval", type=int, default=10_000)
    parser.add_argument("--rank-progress-seconds", type=float, default=15.0)
    parser.add_argument("--max-rank-seconds", type=float, default=None)
    return parser.parse_args()


def main() -> int:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from jordan_qh.low_weight_attachment_killing import (
        compute_exp013,
        write_exp013_outputs,
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
    run = compute_exp013(
        max_weight=args.max_weight,
        mode=args.mode,
        output_dir=EXPERIMENT_DIR,
        reference_v2_cells=args.reference_v2_cells,
        reference_by_weight=args.reference_by_weight,
        thresholds=thresholds,
        attach_policy=args.attach_policy,
    )
    write_exp013_outputs(run, EXPERIMENT_DIR)
    print(
        "EXP013 strict cells="
        f"{run.results['strictly_attachable_cell_count']} "
        "killing_claims="
        f"{run.results['homology_killing_claim_count']} "
        f"passed={run.results['passed']}",
    )
    return 0 if run.results["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
