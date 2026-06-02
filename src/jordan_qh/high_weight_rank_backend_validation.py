"""Experiment 012: high-weight rank backend validation for EXP011's object."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any

from jordan_qh.v2_cells_no_q import (
    ARITHMETIC,
    FIELD,
    MATRIX_CONVENTION,
    PRIMARY_OBJECT,
    TARGET_ALGEBRA,
    Exp011Run,
    Exp011Thresholds,
    compute_exp011,
    report_language_has_no_forbidden_global_phrasing,
)

EXP012_ID = "EXP-012-high-weight-rank-backend-validation"
EXP012_DIRECTORY = "experiments/012-high-weight-rank-backend-validation/"
EXP012_PLAN_PATH = "researchplan/subplan012.md"
EXP012_TEX_REPORT = "tex/exp012_high_weight_rank_backend_validation.tex"
EXP011_REFERENCE_DEFAULT = "experiments/011-v2-cells-no-Q/data/by_weight_W10.json"
REPRODUCTION_GATE_WEIGHT = 10
REPRODUCTION_FIELDS = (
    "dim_C0",
    "dim_C1",
    "dim_C2_old",
    "rank_d1",
    "rank_d2_old",
    "dim_Z1",
    "dim_H1_old",
    "number_of_new_s_cells",
)


def compute_exp012(
    *,
    max_weight: int,
    mode: str,
    output_dir: Path,
    reference_exp011: Path,
    thresholds: Exp011Thresholds | None = None,
    resume: bool = False,
    force_recompute_weights: tuple[int, ...] = (),
) -> Exp011Run:
    """Compute EXP012 with a reproduction gate against EXP011 W<=10 output."""

    if thresholds is None:
        thresholds = Exp011Thresholds(rank_backend="modular_sparse_v2")
    elif thresholds.rank_backend != "modular_sparse_v2":
        thresholds = replace(thresholds, rank_backend="modular_sparse_v2")

    output_dir.mkdir(parents=True, exist_ok=True)
    gate_weight = min(max_weight, REPRODUCTION_GATE_WEIGHT)
    phase1 = compute_exp011(
        max_weight=gate_weight,
        mode=mode,
        output_dir=output_dir,
        thresholds=thresholds,
        resume=resume,
        force_recompute_weights=tuple(
            weight for weight in force_recompute_weights if weight <= gate_weight
        ),
    )
    reproduction = build_reproduction_report(
        reference_exp011=reference_exp011,
        by_weight=phase1.by_weight,
        recomputed_weights=tuple(range(1, gate_weight + 1)),
    )

    if max_weight > gate_weight and reproduction["matches_exp011_reference"]:
        final_run = compute_exp011(
            max_weight=max_weight,
            mode=mode,
            output_dir=output_dir,
            thresholds=thresholds,
            resume=True,
            force_recompute_weights=tuple(
                weight for weight in force_recompute_weights if weight > gate_weight
            ),
        )
    elif max_weight > gate_weight:
        final_run = _with_reproduction_gate_skips(
            phase1,
            max_weight=max_weight,
            gate_weight=gate_weight,
        )
    else:
        final_run = phase1

    return _as_exp012_run(
        final_run,
        max_weight=max_weight,
        output_dir=output_dir,
        reference_exp011=reference_exp011,
        reproduction=reproduction,
    )


def build_reproduction_report(
    *,
    reference_exp011: Path,
    by_weight: dict[str, Any],
    recomputed_weights: tuple[int, ...],
) -> dict[str, Any]:
    """Compare EXP012 recomputation against EXP011 reference records."""

    report: dict[str, Any] = {
        "exp011_reference_file": reference_exp011.as_posix(),
        "recomputed_weights": list(recomputed_weights),
        "comparison_fields": list(REPRODUCTION_FIELDS),
        "matches_exp011_reference": False,
        "per_weight": [],
    }
    if not reference_exp011.exists():
        report["error"] = "reference file does not exist"
        return report

    reference = _read_json(reference_exp011)
    reference_records = {
        int(record["weight"]): record for record in reference.get("weights", [])
    }
    current_records = {
        int(record["weight"]): record for record in by_weight.get("weights", [])
    }
    all_match = True
    for weight in recomputed_weights:
        current = current_records.get(weight)
        expected = reference_records.get(weight)
        weight_report: dict[str, Any] = {
            "weight": weight,
            "matches": False,
            "current": _field_subset(current),
            "reference": _field_subset(expected),
            "mismatches": {},
        }
        if current is None or expected is None:
            weight_report["mismatches"]["record"] = {
                "current": current is not None,
                "reference": expected is not None,
            }
            all_match = False
        else:
            mismatches = {
                field: {
                    "current": current.get(field),
                    "reference": expected.get(field),
                }
                for field in REPRODUCTION_FIELDS
                if current.get(field) != expected.get(field)
            }
            weight_report["mismatches"] = mismatches
            weight_report["matches"] = not mismatches
            all_match = all_match and not mismatches
        report["per_weight"].append(weight_report)
    report["matches_exp011_reference"] = all_match
    return report


def write_exp012_outputs(run: Exp011Run, output_dir: Path) -> None:
    """Write EXP012 result bundle to its experiment directory."""

    data_dir = output_dir / "data"
    tex_dir = output_dir / "tex"
    log_dir = output_dir / "logs"
    data_dir.mkdir(parents=True, exist_ok=True)
    tex_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    max_weight = int(run.results["max_weight_requested"])
    _write_json(output_dir / "results.json", run.results)
    _write_json(data_dir / f"by_weight_W{max_weight}.json", run.by_weight)
    _write_json(data_dir / f"v2_cells_W{max_weight}.json", run.v2_cells)
    (tex_dir / "exp012_high_weight_rank_backend_validation.tex").write_text(
        run.tex_report,
        encoding="utf-8",
    )
    (log_dir / f"run_W{max_weight}.log").write_text(
        run.log_text,
        encoding="utf-8",
    )


def render_exp012_tex_report(
    results: dict[str, Any],
    by_weight: dict[str, Any],
    v2_cells: dict[str, Any],
) -> str:
    """Render a concise bounded-evidence EXP012 TeX report."""

    reproduction = results["reproduction"]
    lines = [
        r"\documentclass{article}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage{booktabs}",
        r"\usepackage{longtable}",
        r"\usepackage{hyperref}",
        r"\begin{document}",
        r"\section*{Experiment 012: High-Weight Rank Backend Validation}",
        (
            "This experiment recomputes the EXP011 bounded object "
            r"$H_{1,w}^{old}$ using the modular sparse v2 rank backend. "
            "It does not apply $Q$, does not attach the formal cells, and "
            r"does not construct $V_3,V_4,\ldots$."
        ),
        r"\paragraph{Boundary.}",
        (
            "All statements are bounded computational evidence for completed "
            "weights only. Skipped, failed, and untested weights are not used "
            "to infer global stabilization or absence of future cells."
        ),
        r"\paragraph{Reproduction gate.}",
        (
            "Reference file: "
            + _tex_escape(reproduction["exp011_reference_file"])
            + r"\\"
        ),
        (
            "Recomputed weights: "
            + _tex_escape(reproduction["recomputed_weights"])
            + r"\\"
        ),
        (
            "Matches EXP011 reference: "
            + _tex_escape(reproduction["matches_exp011_reference"])
        ),
        r"\section*{Weight Summary}",
        r"\begin{longtable}{rrrrrrrrl}",
        (
            r"\toprule "
            r"$w$ & $\dim C_0$ & $\dim C_1$ & $\dim C_2^{old}$ & "
            r"$\operatorname{rank} d_1$ & $\operatorname{rank} d_2$ & "
            r"$\dim Z_1$ & $\dim H_1^{old}$ & status \\"
        ),
        r"\midrule",
    ]
    for record in by_weight["weights"]:
        lines.append(
            " & ".join(
                [
                    str(record["weight"]),
                    str(record.get("dim_C0", "-")),
                    str(record.get("dim_C1", "-")),
                    str(record.get("dim_C2_old", "-")),
                    str(record.get("rank_d1", "-")),
                    str(record.get("rank_d2_old", "-")),
                    str(record.get("dim_Z1", "-")),
                    str(record.get("dim_H1_old", "-")),
                    _tex_escape(record["status"]),
                ],
            )
            + r" \\",
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\section*{Formal V2 Candidates}",
            (
                "Total candidates reported in completed weights: "
                f"{v2_cells['cell_count']}."
            ),
            r"\section*{Checks}",
            r"\begin{verbatim}",
            "\n".join(
                f"{key}: {value}" for key, value in sorted(results["checks"].items())
            ),
            r"\end{verbatim}",
            r"\end{document}",
        ],
    )
    return "\n".join(lines) + "\n"


def _as_exp012_run(
    run: Exp011Run,
    *,
    max_weight: int,
    output_dir: Path,
    reference_exp011: Path,
    reproduction: dict[str, Any],
) -> Exp011Run:
    results = deepcopy(run.results)
    by_weight = deepcopy(run.by_weight)
    v2_cells = deepcopy(run.v2_cells)
    by_weight_file = f"data/by_weight_W{max_weight}.json"
    v2_cells_file = f"data/v2_cells_W{max_weight}.json"

    by_weight["experiment_id"] = EXP012_ID
    by_weight["max_weight_requested"] = max_weight
    by_weight["requested_weights"] = list(range(1, max_weight + 1))
    by_weight["reproduction"] = reproduction
    v2_cells["experiment_id"] = EXP012_ID
    v2_cells["max_weight_requested"] = max_weight

    checks = dict(results["checks"])
    checks["exp011_reproduction_matches_reference"] = reproduction[
        "matches_exp011_reference"
    ]
    results.update(
        {
            "experiment_id": EXP012_ID,
            "experiment_directory": EXP012_DIRECTORY,
            "plan": EXP012_PLAN_PATH,
            "primary_object": PRIMARY_OBJECT,
            "matrix_convention": MATRIX_CONVENTION,
            "target_algebra": TARGET_ALGEBRA,
            "field": FIELD,
            "arithmetic": ARITHMETIC,
            "applies_Q": False,
            "constructs_higher_cells_V3_plus": False,
            "rank_backend_validation": True,
            "exp011_reference_file": reference_exp011.as_posix(),
            "reproduction": reproduction,
            "max_weight_requested": max_weight,
            "requested_weights": list(range(1, max_weight + 1)),
            "by_weight_file": by_weight_file,
            "v2_cells_file": v2_cells_file,
            "tex_report": EXP012_TEX_REPORT,
            "checks": checks,
            "run_finished_at": datetime.now().isoformat(timespec="seconds"),
        },
    )
    results["passed"] = bool(
        run.results["passed"]
        and checks["exp011_reproduction_matches_reference"]
        and not results["failed_weights"]
    )
    tex_report = render_exp012_tex_report(results, by_weight, v2_cells)
    checks["report_language_has_no_forbidden_global_phrasing"] = (
        report_language_has_no_forbidden_global_phrasing(tex_report)
    )
    results["passed"] = bool(
        results["passed"]
        and checks["report_language_has_no_forbidden_global_phrasing"]
    )
    tex_report = render_exp012_tex_report(results, by_weight, v2_cells)
    log_text = (
        "EXP012 wrapper\n"
        f"reference_exp011: {reference_exp011.as_posix()}\n"
        f"matches_exp011_reference: {reproduction['matches_exp011_reference']}\n"
        f"rank_backend: {results['thresholds'].get('rank_backend')}\n"
        + run.log_text
    )
    return Exp011Run(
        results=results,
        by_weight=by_weight,
        v2_cells=v2_cells,
        tex_report=tex_report,
        log_text=log_text,
    )


def _with_reproduction_gate_skips(
    run: Exp011Run,
    *,
    max_weight: int,
    gate_weight: int,
) -> Exp011Run:
    results = deepcopy(run.results)
    by_weight = deepcopy(run.by_weight)
    skipped_records = [
        {
            "weight": weight,
            "status": "skipped",
            "skip_reason": (
                "EXP012 reproduction gate failed for EXP011 weights; "
                "higher weights were not computed."
            ),
            "threshold_triggered": "exp011_reproduction_gate",
            "previous_completed_weight": gate_weight,
            "partial_outputs_preserved": True,
            "runtime_seconds": 0,
            "memory_notes": "Skipped before high-weight computation.",
        }
        for weight in range(gate_weight + 1, max_weight + 1)
    ]
    by_weight["weights"] = sorted(
        [*by_weight["weights"], *skipped_records],
        key=lambda record: record["weight"],
    )
    by_weight["max_weight_requested"] = max_weight
    by_weight["requested_weights"] = list(range(1, max_weight + 1))
    skipped_weights = [
        *by_weight.get("skipped_weights", []),
        *[record["weight"] for record in skipped_records],
    ]
    by_weight["skipped_weights"] = sorted(
        skipped_weights,
    )
    by_weight["not_tested_weights_in_requested_range"] = []
    results["max_weight_requested"] = max_weight
    results["requested_weights"] = list(range(1, max_weight + 1))
    results["skipped_weights"] = by_weight["skipped_weights"]
    results["not_tested_weights_in_requested_range"] = []
    return Exp011Run(
        results=results,
        by_weight=by_weight,
        v2_cells=run.v2_cells,
        tex_report=run.tex_report,
        log_text=run.log_text,
    )


def _field_subset(record: dict[str, Any] | None) -> dict[str, Any] | None:
    if record is None:
        return None
    return {field: record.get(field) for field in REPRODUCTION_FIELDS}


def _tex_escape(value: Any) -> str:
    return str(value).replace("\\", r"\textbackslash{}").replace("_", r"\_")


def _read_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_to_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _to_jsonable(entry) for key, entry in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(entry) for entry in value]
    return value
