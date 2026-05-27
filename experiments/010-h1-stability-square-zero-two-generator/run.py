"""Run Experiment 010 H1 presentation-stress diagnostics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[1]
EXPECTED_PATH = EXPERIMENT_DIR / "expected.json"
RESULTS_PATH = EXPERIMENT_DIR / "results.json"
REPORT_PATH = EXPERIMENT_DIR / "report.md"
TEX_PATH = EXPERIMENT_DIR / "exp010_h1_presentation_stress_report.tex"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))

    try:
        from jordan_qh.h1_presentation_stress import (
            exp010_results,
            render_latex_report,
            render_markdown_report,
            to_jsonable,
        )
    except (ImportError, ModuleNotFoundError) as exc:
        write_json(
            RESULTS_PATH,
            {
                "status": "not run yet",
                "passed": None,
                "experiment": expected["experiment"],
                "notes": (
                    "src/jordan_qh/h1_presentation_stress.py is not available; "
                    "Experiment 010 has not produced H1 diagnostics."
                ),
                "error": str(exc),
            },
        )
        return 0

    results = exp010_results()
    REPORT_PATH.write_text(render_markdown_report(results), encoding="utf-8")
    TEX_PATH.write_text(render_latex_report(results), encoding="utf-8")
    results_with_paths = {
        **results,
        "paths": {
            "results_json": str(RESULTS_PATH.relative_to(REPO_ROOT)),
            "report_markdown": str(REPORT_PATH.relative_to(REPO_ROOT)),
            "report_latex": str(TEX_PATH.relative_to(REPO_ROOT)),
        },
        "report_generated": True,
        "latex_report_generated": True,
    }
    write_json(RESULTS_PATH, to_jsonable(results_with_paths))
    return 0 if results["summary"]["full_stress_test_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
