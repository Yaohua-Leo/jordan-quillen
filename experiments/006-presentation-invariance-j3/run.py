"""Run Experiment 006 when the one-generator Quillen toy model exists."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[1]
EXPECTED_PATH = EXPERIMENT_DIR / "expected.json"
RESULTS_PATH = EXPERIMENT_DIR / "results.json"


def load_expected() -> dict[str, Any]:
    return json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))


def write_results(payload: dict[str, Any]) -> None:
    RESULTS_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    expected = load_expected()

    try:
        from jordan_qh.quillen_toy import (
            OneGeneratorRelation,
            one_relation_toy_homology_dimensions,
            one_step_relation_toy_homology_dimensions,
        )
    except (ImportError, ModuleNotFoundError) as exc:
        write_results(
            {
                "status": "not run yet",
                "passed": None,
                "presentation_invariance_verified": False,
                "notes": (
                    "src/jordan_qh/quillen_toy.py is not available yet; "
                    "Presentation A and the naive Presentation B diagnostic "
                    "are uncomputed."
                ),
                "error": str(exc),
            }
        )
        return 0

    relation = OneGeneratorRelation(
        name="truncated_x3",
        relation_coefficients={3: Fraction(1)},
    )
    computed_a = one_relation_toy_homology_dimensions(relation)
    expected_a = expected["presentation_A"]["expected_homology_dimensions"]
    passed_a = computed_a == expected_a

    computed_b_naive = one_step_relation_toy_homology_dimensions(
        generator_count=2,
        relation_linear_parts=(
            (Fraction(0), Fraction(1)),
            (Fraction(0), Fraction(0)),
            (Fraction(0), Fraction(0)),
        ),
    )
    expected_b_naive = expected["presentation_B"][
        "naive_one_step_expected_homology_dimensions"
    ]
    passed_b_naive = computed_b_naive == expected_b_naive
    passed = passed_a and passed_b_naive

    write_results(
        {
            "status": "run",
            "passed": passed,
            "presentation_invariance_verified": False,
            "completed_scope": (
                "Presentation A and the naive one-step Presentation B "
                "diagnostic were run; genuine cofibrant replacement is not "
                "implemented."
            ),
            "presentation_A": {
                "name": expected["presentation_A"]["name"],
                "computed_homology_dimensions": computed_a,
                "expected_homology_dimensions": expected_a,
                "passed": passed_a,
            },
            "presentation_B": {
                "name": expected["presentation_B"]["name"],
                "status": "naive one-step diagnostic run",
                "computed_naive_one_step_homology_dimensions": computed_b_naive,
                "expected_naive_one_step_homology_dimensions": expected_b_naive,
                "passed": passed_b_naive,
                "cofibrant_replacement_status": expected["presentation_B"][
                    "cofibrant_replacement_status"
                ],
                "note": expected["presentation_B"]["expected_note"],
            },
        }
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
