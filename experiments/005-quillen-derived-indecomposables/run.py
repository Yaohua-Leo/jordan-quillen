"""Run Experiment 005 when the Quillen toy module exists."""

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


def expected_dimensions_by_name(expected: dict[str, Any]) -> dict[str, dict[str, int]]:
    return {
        example["name"]: example["expected_homology_dimensions"]
        for example in expected["examples"]
    }


def dimensions_from_record(record: dict[str, Any]) -> dict[str, int] | None:
    dimensions = (
        record.get("homology_dimensions")
        or record.get("expected_homology_dimensions")
        or record.get("dimensions")
    )
    if dimensions is not None:
        return {"H0": int(dimensions["H0"]), "H1": int(dimensions["H1"])}
    if "H0" in record and "H1" in record:
        return {"H0": int(record["H0"]), "H1": int(record["H1"])}
    return None


def main() -> int:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    expected = load_expected()

    try:
        from jordan_qh.quillen_toy import benchmark_examples
    except (ImportError, ModuleNotFoundError) as exc:
        write_results(
            {
                "status": "not run yet",
                "passed": None,
                "notes": (
                    "src/jordan_qh/quillen_toy.py is not available yet; "
                    "expected values remain recorded but unverified."
                ),
                "error": str(exc),
            }
        )
        return 0

    computed = benchmark_examples()
    expected_dimensions = expected_dimensions_by_name(expected)
    comparisons = []
    for record in computed:
        name = record["name"]
        actual = dimensions_from_record(record)
        expected_value = expected_dimensions.get(name)
        comparisons.append(
            {
                "name": name,
                "computed_homology_dimensions": actual,
                "expected_homology_dimensions": expected_value,
                "passed": actual == expected_value,
            }
        )

    passed = (
        {entry["name"] for entry in comparisons} == set(expected_dimensions)
        and all(entry["passed"] for entry in comparisons)
    )
    write_results({"status": "run", "passed": passed, "examples": comparisons})
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
