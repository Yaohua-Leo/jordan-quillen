"""Run Experiment 101: one-generator generator legality audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-weight", type=int, default=12)
    parser.add_argument(
        "--reference-results",
        type=Path,
        default=(
            REPO_ROOT
            / "experiments"
            / "100-square-zero-nonunital-cofibrant-weight10"
            / "results.json"
        ),
    )
    parser.add_argument(
        "--reference-cells",
        type=Path,
        default=(
            REPO_ROOT
            / "experiments"
            / "100-square-zero-nonunital-cofibrant-weight10"
            / "data"
            / "cells_W10.json"
        ),
    )
    return parser.parse_args()


def main() -> int:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from jordan_qh.one_generator_generator_legality import (
        compute_exp101,
        write_exp101_outputs,
    )

    args = parse_args()
    run = compute_exp101(
        max_weight=args.max_weight,
        output_dir=EXPERIMENT_DIR,
        reference_cells=args.reference_cells,
        reference_results=args.reference_results,
    )
    write_exp101_outputs(run, EXPERIMENT_DIR)
    print(
        "EXP101 completed "
        f"W={run.results['max_weight_requested']} "
        f"V1_legal={run.results['v1_legal_generator_count']}/"
        f"{run.results['v1_candidate_count']} "
        f"V2_strict={run.results['v2_strictly_attachable_cell_count']}/"
        f"{run.results['v2_candidate_count']} "
        f"passed={run.results['passed']}",
    )
    return 0 if run.results["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
