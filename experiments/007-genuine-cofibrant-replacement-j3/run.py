"""Run Experiment 007 for the fixed J3 two-step toy replacement."""

from __future__ import annotations

import json
import sys
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
        from jordan_qh.semi_free_toy import j3_two_step_result
    except (ImportError, ModuleNotFoundError) as exc:
        write_results(
            {
                "status": "not run yet",
                "passed": None,
                "notes": (
                    "src/jordan_qh/semi_free_toy.py is not available yet; "
                    "the two-step Presentation B correction is uncomputed."
                ),
                "error": str(exc),
            }
        )
        return 0

    result = j3_two_step_result()
    expected_dimensions = expected["expected_homology_dimensions"]
    passed = (
        result["passed"]
        and result["computed_homology_dimensions"] == expected_dimensions
        and result["homology_representatives"]
        == expected["expected_representatives"]
    )
    result["passed"] = passed
    write_results(result)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
