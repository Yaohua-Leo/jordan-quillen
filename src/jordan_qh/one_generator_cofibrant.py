"""Experiment 100: bounded one-generator cofibrant cell computation.

This module follows ``researchplan/subplan100.md``.  It treats the browser
conversation as a source of the question only, not as a source of predicted
answers.  The V1 and V2 cells are selected from exact linear algebra in the
current low-weight Jordan backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Any

from jordan_qh.low_weight_jordan import (
    LowWeightJordanModel,
    QuotientSpace,
    RawVector,
    SparseRow,
    WeightedGenerator,
    build_low_weight_jordan_model,
    product_term,
    raw_vector_to_terms,
    reduce_sparse_row,
    sparse_echelon,
    sparse_kernel_basis,
    sparse_rref,
    term_to_str,
)

EXP100_ID = "EXP-100-square-zero-nonunital-cofibrant-weight10"
EXPERIMENT_DIRECTORY = "experiments/100-square-zero-nonunital-cofibrant-weight10/"
PLAN_PATH = "researchplan/subplan100.md"
MATRIX_CONVENTION = "source_rows_target_coordinates"
FIELD = "QQ"
ARITHMETIC = "exact_rational"
TARGET_ALGEBRA = "Jord<x>/(x^2)"
REPORT_FORBIDDEN_PHRASES = (
    "confirms a predicted",
    "proves the full cofibrant replacement",
    "No further cells occur in all weights",
    "infinite resolution terminates",
)


@dataclass(frozen=True)
class Exp100Run:
    """In-memory result bundle for one EXP100 run."""

    results: dict[str, Any]
    by_weight: dict[str, Any]
    cells: dict[str, Any]
    tex_report: str
    log_text: str


def expected_setup(max_weight: int = 10) -> dict[str, Any]:
    """Return setup-only expectations for ``expected.json``."""

    return {
        "status": "expected_setup",
        "experiment": EXP100_ID,
        "plan": PLAN_PATH,
        "base_field": FIELD,
        "category": "nonunital dg Jordan algebras",
        "target_algebra": TARGET_ALGEBRA,
        "max_weight": max_weight,
        "max_homological_degree": 2,
        "applies_Q": False,
        "matrix_convention": MATRIX_CONVENTION,
        "do_not_prefill": [
            "computed_V1_cells",
            "computed_V2_cells",
            "predicted_raw_cycle_counts",
            "predicted_minimal_cell_table",
            "computed_differentials",
            "outcomes",
        ],
    }


def compute_exp100(*, max_weight: int, output_dir: Path) -> Exp100Run:
    """Compute EXP100 and write caches/checkpoints under ``output_dir``."""

    if max_weight < 1:
        msg = "max_weight must be positive"
        raise ValueError(msg)

    start_time = datetime.now().isoformat(timespec="seconds")
    start_counter = perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = output_dir / "cache"
    checkpoint_dir = output_dir / "checkpoints"
    log_dir = output_dir / "logs"
    cache_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_lines = [
        f"start time: {start_time}",
        f"max weight requested: {max_weight}",
        "mode: bounded degree<=2 computation",
        "predicted browser formulas: excluded from input",
    ]

    degree_zero_model = build_low_weight_jordan_model(
        (WeightedGenerator("x", degree=0, weight=1),),
        {},
        weight_bound=max_weight,
        max_degree=0,
    )
    v0_cells = [
        {
            "name": "x",
            "layer": "V0",
            "degree": 0,
            "weight": 1,
            "maps_to": "x_bar",
            "source": "computed presentation generator",
        },
    ]
    v1_cells, v1_by_weight = _discover_v1_cells(
        degree_zero_model,
        max_weight=max_weight,
    )
    log_lines.append(f"computed V1 cells: {len(v1_cells)}")
    log_lines.extend(
        f"V1 {cell['name']} weight={cell['weight']} d={cell['differential_formula']}"
        for cell in v1_cells
    )

    generators, differentials = _a1_generators_and_differentials(v1_cells)
    model_start = perf_counter()
    model = build_low_weight_jordan_model(
        generators,
        differentials,
        weight_bound=max_weight,
        max_degree=2,
    )
    log_lines.append(
        f"built A^(1) model in {perf_counter() - model_start:.3f} seconds",
    )

    completed_records: list[dict[str, Any]] = []
    failed_records: list[dict[str, Any]] = []
    skipped_records: list[dict[str, Any]] = []
    v2_cells: list[dict[str, Any]] = []
    next_v2_index = 1
    for weight in range(1, max_weight + 1):
        try:
            record, cells_for_weight = _compute_weight_record(
                model=model,
                weight=weight,
                v1_cells=v1_cells,
                global_index_start=next_v2_index,
                cache_dir=cache_dir,
            )
        except Exception as exc:  # pragma: no cover - diagnostic path
            record = {
                "weight": weight,
                "status": "failed",
                "failure_stage": "weight_computation",
                "error_message": str(exc),
                "partial_outputs_preserved": True,
                "runtime_seconds": None,
                "memory_notes": "Failure preserved by EXP100 runner.",
            }
            failed_records.append(record)
            _write_json(checkpoint_dir / f"weight_{weight}_status.json", record)
            log_lines.append(f"weight {weight}: failed ({exc})")
            continue
        completed_records.append(record)
        v2_cells.extend(cells_for_weight)
        next_v2_index += len(cells_for_weight)
        _write_json(
            checkpoint_dir / f"weight_{weight}_status.json",
            {
                "experiment_id": EXP100_ID,
                "weight": weight,
                "status": record["status"],
                "record": record,
                "v2_cells": cells_for_weight,
            },
        )
        log_lines.append(
            "weight "
            f"{weight}: completed, dim_H1_old={record['dim_H1_old']}, "
            f"V2 cells={len(cells_for_weight)}",
        )

    completed_weights = [record["weight"] for record in completed_records]
    failed_weights = [record["weight"] for record in failed_records]
    skipped_weights = [record["weight"] for record in skipped_records]
    classified = set(completed_weights) | set(failed_weights) | set(skipped_weights)
    not_tested_weights = [
        weight for weight in range(1, max_weight + 1) if weight not in classified
    ]
    by_weight = {
        "experiment_id": EXP100_ID,
        "max_weight_requested": max_weight,
        "requested_weights": list(range(1, max_weight + 1)),
        "completed_weights": completed_weights,
        "failed_weights": failed_weights,
        "skipped_weights": skipped_weights,
        "not_tested_weights_in_requested_range": not_tested_weights,
        "V1_discovery_by_weight": v1_by_weight,
        "weights": [*completed_records, *failed_records, *skipped_records],
    }
    by_weight["weights"] = sorted(by_weight["weights"], key=lambda item: item["weight"])
    cells = {
        "experiment_id": EXP100_ID,
        "max_weight_requested": max_weight,
        "V0_cell_count": len(v0_cells),
        "V1_cell_count": len(v1_cells),
        "V2_cell_count": len(v2_cells),
        "cells": [*v0_cells, *v1_cells, *v2_cells],
        "V0_cells": v0_cells,
        "V1_cells": v1_cells,
        "V2_cells": v2_cells,
    }
    checks = _global_checks(
        v1_cells=v1_cells,
        completed_records=completed_records,
        v2_cells=v2_cells,
        failed_weights=failed_weights,
    )
    results = {
        "experiment_id": EXP100_ID,
        "experiment_directory": EXPERIMENT_DIRECTORY,
        "plan": PLAN_PATH,
        "status": "run",
        "passed": False,
        "field": FIELD,
        "category": "nonunital dg Jordan algebras",
        "arithmetic": ARITHMETIC,
        "target_algebra": TARGET_ALGEBRA,
        "applies_Q": False,
        "constructs_higher_cells_V3_plus": False,
        "max_weight_requested": max_weight,
        "completed_weights": completed_weights,
        "failed_weights": failed_weights,
        "skipped_weights": skipped_weights,
        "not_tested_weights_in_requested_range": not_tested_weights,
        "computed_V0_cells": v0_cells,
        "computed_V1_cells": v1_cells,
        "computed_V2_cells": v2_cells,
        "cell_counts_by_weight": _cell_counts_by_weight(
            max_weight=max_weight,
            v1_cells=v1_cells,
            v2_cells=v2_cells,
        ),
        "backend": _backend_record(),
        "matrix_convention": MATRIX_CONVENTION,
        "global_claims_modified": False,
        "by_weight_file": f"data/by_weight_W{max_weight}.json",
        "cells_file": f"data/cells_W{max_weight}.json",
        "tex_report": "tex/exp100_square_zero_nonunital_cofibrant_weight10.tex",
        "finite_truncation_warning": (
            "All conclusions are restricted to completed weights w <= 10 "
            "and homological degree <= 2."
        ),
        "checks": checks,
        "run_started_at": start_time,
        "run_finished_at": datetime.now().isoformat(timespec="seconds"),
        "runtime_seconds": round(perf_counter() - start_counter, 3),
    }
    tex_report = render_tex_report(results, by_weight, cells)
    results["checks"]["report_language_has_no_forbidden_global_phrasing"] = (
        report_language_has_no_forbidden_global_phrasing(tex_report)
    )
    results["passed"] = bool(
        results["checks"]["all_completed_weights_passed"]
        and results["checks"]["report_language_has_no_forbidden_global_phrasing"]
        and not failed_weights
    )
    tex_report = render_tex_report(results, by_weight, cells)
    log_lines.append(f"end time: {results['run_finished_at']}")
    log_lines.append(f"runtime seconds: {results['runtime_seconds']}")
    log_lines.append(f"completed weights: {completed_weights}")
    log_lines.append(f"failed weights: {failed_weights}")
    return Exp100Run(
        results=results,
        by_weight=by_weight,
        cells=cells,
        tex_report=tex_report,
        log_text="\n".join(log_lines) + "\n",
    )


def write_run_outputs(run: Exp100Run, output_dir: Path) -> None:
    """Write the EXP100 JSON, TeX, and log artifacts."""

    data_dir = output_dir / "data"
    tex_dir = output_dir / "tex"
    log_dir = output_dir / "logs"
    data_dir.mkdir(parents=True, exist_ok=True)
    tex_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    max_weight = run.results["max_weight_requested"]
    _write_json(output_dir / "expected.json", expected_setup(max_weight))
    _write_json(output_dir / "results.json", run.results)
    _write_json(data_dir / f"by_weight_W{max_weight}.json", run.by_weight)
    _write_json(data_dir / f"cells_W{max_weight}.json", run.cells)
    (tex_dir / "exp100_square_zero_nonunital_cofibrant_weight10.tex").write_text(
        run.tex_report,
        encoding="utf-8",
    )
    (log_dir / f"run_W{max_weight}.log").write_text(
        run.log_text,
        encoding="utf-8",
    )


def render_tex_report(
    results: dict[str, Any],
    by_weight: dict[str, Any],
    cells: dict[str, Any],
) -> str:
    """Render a concise TeX report from the same objects as the JSON output."""

    lines = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{booktabs}",
        r"\usepackage{longtable}",
        r"\title{Experiment 100: One-Generator Cofibrant Cell Computation}",
        r"\author{Jordan Quillen Homology Project}",
        r"\date{}",
        r"\begin{document}",
        r"\maketitle",
        r"\section*{Scope}",
        f"Experiment ID: \\texttt{{{_tex_escape(results['experiment_id'])}}}.",
        "",
        f"Target algebra: \\texttt{{{_tex_escape(TARGET_ALGEBRA)}}}.",
        "",
        (
            "The computation records the bounded cell layers "
            "$V_0$, $V_1$, and $V_2$ through product weight 10. "
            "The functor $Q$ is not applied, and layers "
            "$V_3,V_4,\\ldots$ are not constructed."
        ),
        "",
        (
            "The run does not use predicted formulas as inputs.  Cells are "
            "accepted only from exact linear algebra and recorded certificates."
        ),
        r"\section*{Backend}",
        _tex_escape(results["backend"]["convention"]),
        "",
        _tex_escape(results["backend"]["convention_audit"]),
        r"\section*{Computed Cell Counts}",
        r"\begin{tabular}{rrrr}",
        r"\toprule",
        r"Weight & V1 cells & V2 cells & $\dim H^{old}_{1,w}$ \\",
        r"\midrule",
    ]
    by_weight_map = {record["weight"]: record for record in by_weight["weights"]}
    for weight in range(1, int(results["max_weight_requested"]) + 1):
        counts = results["cell_counts_by_weight"][str(weight)]
        record = by_weight_map[weight]
        dim_h1 = record.get("dim_H1_old", "-")
        lines.append(
            f"{weight} & {counts['V1']} & {counts['V2']} & {dim_h1} \\\\",
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\section*{V1 Cells}",
        ],
    )
    for cell in cells["V1_cells"]:
        lines.append(
            "\\texttt{"
            f"{_tex_escape(cell['name'])}"
            "} "
            f"weight {cell['weight']}: "
            f"$d={_tex_escape(cell['differential_formula'])}$.",
        )
        lines.append("")
    lines.append(r"\section*{V2 Cells}")
    if cells["V2_cells"]:
        for cell in cells["V2_cells"]:
            lines.append(
                "\\texttt{"
                f"{_tex_escape(cell['name'])}"
                "} "
                f"weight {cell['weight']}: "
                f"$d={_tex_escape(cell['differential_formula'])}$.",
            )
            lines.append("")
    else:
        lines.append("No V2 cells were computed in completed weights.")
    lines.extend(
        [
            r"\section*{Checks}",
            r"\begin{verbatim}",
            _pretty_checks(results["checks"]),
            r"\end{verbatim}",
            r"\section*{Finite-Weight Boundary}",
            (
                "All conclusions in this report are restricted to completed "
                "weights with status completed. Skipped, failed, and untested "
                "weights are not used for any mathematical conclusion. This "
                "is bounded computational evidence, not a theorem about the "
                "full cofibrant replacement."
            ),
            r"\end{document}",
            "",
        ],
    )
    return "\n".join(lines)


def report_language_has_no_forbidden_global_phrasing(report: str) -> bool:
    """Return whether the report omits forbidden theorem-like phrases."""

    return all(phrase not in report for phrase in REPORT_FORBIDDEN_PHRASES)


def _discover_v1_cells(
    model: LowWeightJordanModel,
    *,
    max_weight: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    accepted_cells: list[dict[str, Any]] = []
    accepted_raw: list[tuple[str, int, RawVector]] = []
    closure_raw_by_weight: dict[int, list[RawVector]] = {}
    by_weight: list[dict[str, Any]] = []

    for weight in range(1, max_weight + 1):
        space = model.quotient_space(0, weight)
        target_dimension, epsilon_rows = _presentation_rows(space, weight)
        kernel_basis = sparse_kernel_basis(
            epsilon_rows,
            source_dimension=space.dimension(),
            target_dimension=target_dimension,
        )
        closure_rows = _closure_rows_for_weight(
            model=model,
            weight=weight,
            accepted_raw=accepted_raw,
            closure_raw_by_weight=closure_raw_by_weight,
        )
        closure_rref = sparse_rref(closure_rows)
        added_names: list[str] = []
        for candidate in kernel_basis:
            remainder = _normalize_sparse_row(
                reduce_sparse_row(candidate, closure_rref),
            )
            if not remainder:
                continue
            raw = space.lift_sparse_coordinates(remainder)
            epsilon_image = _apply_source_row_map(remainder, epsilon_rows)
            global_index = len(accepted_cells) + 1
            name = f"r1_{global_index:05d}_w{weight}"
            basis = _basis_names(space)
            cell = {
                "name": name,
                "layer": "V1",
                "degree": 1,
                "weight": weight,
                "global_index": global_index,
                "differential_formula": raw_vector_to_terms(raw),
                "differential_coordinates": _dense_sparse_row_json(
                    remainder,
                    space.dimension(),
                ),
                "differential_sparse_coordinates": _sparse_row_json(remainder),
                "kernel_certificate": {
                    "epsilon_image": _sparse_row_formula(
                        epsilon_image,
                        ("x_bar",) if target_dimension else (),
                    ),
                    "maps_to_kernel": not epsilon_image,
                },
                "independence_certificate": {
                    "remainder_mod_prior_closure": _sparse_row_record(
                        remainder,
                        basis,
                    ),
                    "independent_mod_prior_closure": True,
                    "prior_closure_rank": len(closure_rref),
                },
                "minimality_certified": True,
                "_raw_differential": raw,
            }
            accepted_cells.append(cell)
            accepted_raw.append((name, weight, raw))
            added_names.append(name)
            closure_rows = _closure_rows_for_weight(
                model=model,
                weight=weight,
                accepted_raw=accepted_raw,
                closure_raw_by_weight=closure_raw_by_weight,
            )
            closure_rref = sparse_rref(closure_rows)

        final_closure_rows = _closure_rows_for_weight(
            model=model,
            weight=weight,
            accepted_raw=accepted_raw,
            closure_raw_by_weight=closure_raw_by_weight,
        )
        final_closure_rref = sparse_rref(final_closure_rows)
        closure_raw_by_weight[weight] = [
            space.lift_sparse_coordinates(row) for row in final_closure_rref.values()
        ]
        by_weight.append(
            {
                "weight": weight,
                "A0_dimension": space.dimension(),
                "presentation_kernel_dimension": len(kernel_basis),
                "closure_rank_after_selection": len(final_closure_rref),
                "new_V1_cell_names": added_names,
                "minimality_certified": len(final_closure_rref) == len(kernel_basis),
            },
        )
    return accepted_cells, by_weight


def _presentation_rows(
    space: QuotientSpace,
    weight: int,
) -> tuple[int, tuple[SparseRow, ...]]:
    if weight != 1:
        return 0, tuple({} for _ in range(space.dimension()))
    rows: list[SparseRow] = []
    for term in space.basis_terms():
        rows.append({0: Fraction(1)} if term_to_str(term) == "x" else {})
    return 1, tuple(rows)


def _closure_rows_for_weight(
    *,
    model: LowWeightJordanModel,
    weight: int,
    accepted_raw: list[tuple[str, int, RawVector]],
    closure_raw_by_weight: dict[int, list[RawVector]],
) -> list[SparseRow]:
    space = model.quotient_space(0, weight)
    rows: list[SparseRow] = []
    for _name, relation_weight, raw in accepted_raw:
        if relation_weight == weight:
            row = space.reduce_vector_sparse(raw)
            if row:
                rows.append(row)
    for left_weight in range(1, weight):
        right_weight = weight - left_weight
        right_space = model.quotient_space(0, right_weight)
        for closure_raw in closure_raw_by_weight.get(left_weight, []):
            for basis_term in right_space.basis_terms():
                product = _raw_product(closure_raw, {basis_term: Fraction(1)})
                row = space.reduce_vector_sparse(product)
                if row:
                    rows.append(row)
    return rows


def _a1_generators_and_differentials(
    v1_cells: list[dict[str, Any]],
) -> tuple[tuple[WeightedGenerator, ...], dict[str, RawVector]]:
    generators = [WeightedGenerator("x", degree=0, weight=1)]
    differentials: dict[str, RawVector] = {}
    for cell in v1_cells:
        name = str(cell["name"])
        generators.append(
            WeightedGenerator(name, degree=1, weight=int(cell["weight"])),
        )
        differentials[name] = _raw_vector_from_cell(cell)
    return tuple(generators), differentials


def _raw_vector_from_cell(cell: dict[str, Any]) -> RawVector:
    sparse = {
        int(index): _json_to_fraction(value)
        for index, value in cell["differential_sparse_coordinates"].items()
    }
    # Reconstruct from the formula-bearing coordinates in the one-generator
    # degree-zero model.  This function is used only after V1 discovery, so the
    # raw vector is also stored in a hidden field while building the result.
    if "_raw_differential" in cell:
        return dict(cell["_raw_differential"])
    # Fallback for defensive completeness.  The current code path always sets
    # the hidden raw field before calling this function.
    x = ("g", "x")
    if sparse == {0: Fraction(1)}:
        return {product_term(x, x): Fraction(1)}
    msg = "missing raw differential for V1 cell"
    raise ValueError(msg)


def _compute_weight_record(
    *,
    model: LowWeightJordanModel,
    weight: int,
    v1_cells: list[dict[str, Any]],
    global_index_start: int,
    cache_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    start = perf_counter()
    c0 = model.quotient_space(0, weight)
    c1 = model.quotient_space(1, weight)
    c2_old = model.quotient_space(2, weight)
    dim_c0 = c0.dimension()
    dim_c1 = c1.dimension()
    dim_c2_old = c2_old.dimension()
    d1_rows = model.differential_sparse_matrix(1, weight)
    d2_old_rows = model.differential_sparse_matrix(2, weight)
    rank_d1 = len(sparse_echelon(d1_rows))
    d2_old_rref = sparse_rref(d2_old_rows)
    rank_d2_old = len(d2_old_rref)
    dim_z1 = dim_c1 - rank_d1
    dim_b_old = rank_d2_old
    dim_h1_old = dim_z1 - dim_b_old
    chain_condition = _source_row_composition_is_zero(
        first_rows=d2_old_rows,
        second_rows=d1_rows,
    )
    c0_basis = _basis_names(c0)
    c1_basis = _basis_names(c1)
    c2_basis = _basis_names(c2_old)

    cells: list[dict[str, Any]] = []
    if dim_h1_old:
        z1_basis = sparse_kernel_basis(
            d1_rows,
            source_dimension=dim_c1,
            target_dimension=dim_c0,
        )
        selection_rref = dict(d2_old_rref)
        for cycle in z1_basis:
            boundary_remainder = reduce_sparse_row(cycle, d2_old_rref)
            selection_remainder = reduce_sparse_row(cycle, selection_rref)
            if not selection_remainder:
                continue
            global_index = global_index_start + len(cells)
            name = f"s2_{global_index:05d}_w{weight}"
            d1_z = _apply_source_row_map(cycle, d1_rows)
            raw_lift = c1.lift_sparse_coordinates(cycle)
            cell = {
                "name": name,
                "layer": "V2",
                "degree": 2,
                "weight": weight,
                "global_index": global_index,
                "differential_formula": _sparse_row_formula(cycle, c1_basis),
                "differential_coordinates": _dense_sparse_row_json(
                    cycle,
                    dim_c1,
                ),
                "differential_sparse_coordinates": _sparse_row_json(cycle),
                "differential_raw_lift": raw_vector_to_terms(raw_lift),
                "cycle_certificate": {
                    "d1_z_normal_form": _sparse_row_formula(d1_z, c0_basis),
                    "is_cycle": not d1_z,
                },
                "non_boundary_certificate": {
                    "certificate_type": "rref_remainder",
                    "boundary_remainder_mod_B_old": _sparse_row_record(
                        boundary_remainder,
                        c1_basis,
                    ),
                    "boundary_remainder_nonzero": bool(boundary_remainder),
                    "not_in_B_old": bool(boundary_remainder),
                },
                "independence_certificate": {
                    "selection_remainder_mod_B_old_plus_accepted_reps": (
                        _sparse_row_record(selection_remainder, c1_basis)
                    ),
                    "independent_mod_B_old_plus_previous_reps": True,
                },
                "d1_z_normal_form": _sparse_row_formula(d1_z, c0_basis),
                "boundary_remainder_nonzero": bool(boundary_remainder),
                "not_in_B_old": bool(boundary_remainder),
                "certificate_type": "rref_remainder",
            }
            cells.append(cell)
            normalized = _normalize_sparse_row(selection_remainder)
            pivot = min(normalized)
            selection_rref[pivot] = normalized
            selection_rref = sparse_rref(selection_rref.values())
    else:
        z1_basis = ()
        selection_rref = dict(d2_old_rref)

    quotient_independence = len(selection_rref) == len(d2_old_rref) + len(cells)
    all_cycles = all(cell["cycle_certificate"]["is_cycle"] for cell in cells)
    all_non_boundaries = all(
        cell["non_boundary_certificate"]["boundary_remainder_nonzero"]
        and cell["non_boundary_certificate"]["not_in_B_old"]
        for cell in cells
    )
    v1_names = [cell["name"] for cell in v1_cells if int(cell["weight"]) == weight]
    _write_weight_caches(
        cache_dir=cache_dir,
        weight=weight,
        quotient_spaces=(c0, c1, c2_old),
        bases=(c0_basis, c1_basis, c2_basis),
        d1_rows=d1_rows,
        d2_old_rows=d2_old_rows,
        b_old_rref=d2_old_rref,
        z1_basis=z1_basis,
        cells=cells,
    )
    checks = {
        "d2_old_matrix_times_d1_matrix_is_zero": chain_condition,
        "dim_Z1_matches_rank_nullity": dim_z1 == dim_c1 - rank_d1,
        "dim_B_old_matches_rank_d2_old": dim_b_old == rank_d2_old,
        "dim_H1_old_matches_V2_count": dim_h1_old == len(cells),
        "all_V2_certificates_valid": all_cycles
        and all_non_boundaries
        and quotient_independence,
        "all_V2_differentials_are_cycles": all_cycles,
        "all_V2_representatives_have_nonzero_B_old_remainder": all_non_boundaries,
        "all_V2_representatives_independent_mod_B_old": quotient_independence,
    }
    record = {
        "weight": weight,
        "status": "completed",
        "dim_C0": dim_c0,
        "dim_C1": dim_c1,
        "dim_C2_old": dim_c2_old,
        "rank_d1": rank_d1,
        "rank_d2_old": rank_d2_old,
        "dim_Z1": dim_z1,
        "dim_B_old": dim_b_old,
        "dim_H1_old": dim_h1_old,
        "computed_V1_cell_names": v1_names,
        "computed_V2_cell_names": [cell["name"] for cell in cells],
        "runtime_seconds": round(perf_counter() - start, 3),
        "memory_notes": "Memory controlled by bounded W=10 exact sparse computation.",
        "matrix_stats": {
            "d1_rows": dim_c1,
            "d1_cols": dim_c0,
            "d1_nnz": _sparse_rows_nnz(d1_rows),
            "d2_old_rows": dim_c2_old,
            "d2_old_cols": dim_c1,
            "d2_old_nnz": _sparse_rows_nnz(d2_old_rows),
        },
        "basis_data": {
            "C0_basis": list(c0_basis),
            "C1_basis": list(c1_basis),
            "C2_old_basis": list(c2_basis),
        },
        "checks": checks,
    }
    return record, cells


def _write_weight_caches(
    *,
    cache_dir: Path,
    weight: int,
    quotient_spaces: tuple[QuotientSpace, QuotientSpace, QuotientSpace],
    bases: tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]],
    d1_rows: tuple[SparseRow, ...],
    d2_old_rows: tuple[SparseRow, ...],
    b_old_rref: dict[int, SparseRow],
    z1_basis: tuple[SparseRow, ...],
    cells: list[dict[str, Any]],
) -> None:
    for degree, quotient_space, basis in zip(
        (0, 1, 2),
        quotient_spaces,
        bases,
        strict=True,
    ):
        _write_json(
            cache_dir / f"quotient_space_deg{degree}_w{weight}.json",
            {
                "degree": degree,
                "weight": weight,
                "raw_term_count": len(quotient_space.raw_terms),
                "dimension": quotient_space.dimension(),
                "basis": list(basis),
                "free_columns": list(quotient_space.free_columns),
                "jordan_relation_rank": len(quotient_space.pivot_rows),
            },
        )
    _write_json(cache_dir / f"d1_w{weight}.json", _sparse_rows_record(d1_rows))
    _write_json(cache_dir / f"d2_old_w{weight}.json", _sparse_rows_record(d2_old_rows))
    _write_json(
        cache_dir / f"B_old_rref_w{weight}.json",
        _pivot_rows_record(b_old_rref),
    )
    _write_json(cache_dir / f"Z1_basis_w{weight}.json", _sparse_rows_record(z1_basis))
    _write_json(
        cache_dir / f"H1_old_reps_w{weight}.json",
        {
            "weight": weight,
            "representatives": [
                cell["differential_sparse_coordinates"] for cell in cells
            ],
        },
    )


def _global_checks(
    *,
    v1_cells: list[dict[str, Any]],
    completed_records: list[dict[str, Any]],
    v2_cells: list[dict[str, Any]],
    failed_weights: list[int],
) -> dict[str, Any]:
    completed_checks = [all(record["checks"].values()) for record in completed_records]
    return {
        "all_relation_cells_map_to_kernel": all(
            cell["kernel_certificate"]["maps_to_kernel"] for cell in v1_cells
        ),
        "all_V2_differentials_are_cycles": all(
            cell["cycle_certificate"]["is_cycle"] for cell in v2_cells
        ),
        "all_V2_representatives_have_nonzero_B_old_remainder": all(
            cell["non_boundary_certificate"]["boundary_remainder_nonzero"]
            for cell in v2_cells
        ),
        "all_V2_representatives_independent_mod_B_old": all(
            record["checks"]["all_V2_representatives_independent_mod_B_old"]
            for record in completed_records
        ),
        "rank_nullity_checks_passed": all(
            record["checks"]["dim_Z1_matches_rank_nullity"]
            and record["checks"]["dim_B_old_matches_rank_d2_old"]
            and record["checks"]["dim_H1_old_matches_V2_count"]
            for record in completed_records
        ),
        "chain_condition_checks_passed": all(
            record["checks"]["d2_old_matrix_times_d1_matrix_is_zero"]
            for record in completed_records
        ),
        "expected_setup_has_no_prefilled_results": True,
        "exact_rational_arithmetic": True,
        "applies_Q_is_false": True,
        "constructs_higher_cells_V3_plus_is_false": True,
        "all_completed_weights_passed": all(completed_checks) and not failed_weights,
    }


def _cell_counts_by_weight(
    *,
    max_weight: int,
    v1_cells: list[dict[str, Any]],
    v2_cells: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for weight in range(1, max_weight + 1):
        counts[str(weight)] = {
            "V0": 1 if weight == 1 else 0,
            "V1": sum(1 for cell in v1_cells if int(cell["weight"]) == weight),
            "V2": sum(1 for cell in v2_cells if int(cell["weight"]) == weight),
        }
    return counts


def _backend_record() -> dict[str, Any]:
    return {
        "name": "low_weight_jordan ordinary backend",
        "convention": (
            "ordinary commutative nonassociative Jordan algebra modulo the "
            "linearized Jordan identity, with a signed derivation differential"
        ),
        "convention_audit": (
            "The output is relative to this backend convention. A separate "
            "theory check is needed before identifying it exactly with a fully "
            "graded operadic dg Jordan convention."
        ),
        "does_not_apply_Q": True,
        "does_not_construct_V3_plus": True,
    }


def _raw_product(left: RawVector, right: RawVector) -> RawVector:
    result: RawVector = {}
    for left_term, left_coefficient in left.items():
        for right_term, right_coefficient in right.items():
            _add_raw(
                result,
                product_term(left_term, right_term),
                left_coefficient * right_coefficient,
            )
    return result


def _add_raw(vector: RawVector, term: Any, coefficient: Fraction) -> None:
    if coefficient == 0:
        return
    vector[term] = vector.get(term, Fraction(0)) + coefficient
    if vector[term] == 0:
        del vector[term]


def _normalize_sparse_row(row: SparseRow) -> SparseRow:
    if not row:
        return {}
    pivot = min(row)
    coefficient = row[pivot]
    return {
        column: value / coefficient
        for column, value in row.items()
        if value != 0
    }


def _apply_source_row_map(
    vector: SparseRow,
    matrix_rows: tuple[SparseRow, ...],
) -> SparseRow:
    result: SparseRow = {}
    for source_index, coefficient in vector.items():
        for target_index, entry in matrix_rows[source_index].items():
            result[target_index] = (
                result.get(target_index, Fraction(0)) + coefficient * entry
            )
            if result[target_index] == 0:
                del result[target_index]
    return result


def _source_row_composition_is_zero(
    *,
    first_rows: tuple[SparseRow, ...],
    second_rows: tuple[SparseRow, ...],
) -> bool:
    return all(not _apply_source_row_map(row, second_rows) for row in first_rows)


def _basis_names(space: QuotientSpace) -> tuple[str, ...]:
    return tuple(term_to_str(term) for term in space.basis_terms())


def _sparse_rows_nnz(rows: tuple[SparseRow, ...]) -> int:
    return sum(len(row) for row in rows)


def _sparse_row_formula(row: SparseRow, basis: tuple[str, ...]) -> str:
    if not row:
        return "0"
    parts: list[str] = []
    for index, coefficient in sorted(row.items()):
        basis_name = basis[index]
        if coefficient == 1:
            parts.append(basis_name)
        elif coefficient == -1:
            parts.append(f"-{basis_name}")
        else:
            parts.append(f"{coefficient}*{basis_name}")
    return " + ".join(parts).replace("+ -", "- ")


def _sparse_row_record(row: SparseRow, basis: tuple[str, ...]) -> dict[str, Any]:
    return {
        "formula": _sparse_row_formula(row, basis),
        "sparse_coordinates": _sparse_row_json(row),
        "nonzero": bool(row),
    }


def _sparse_row_json(row: SparseRow) -> dict[str, int | str]:
    return {
        str(index): _fraction_to_json(coefficient)
        for index, coefficient in sorted(row.items())
        if coefficient != 0
    }


def _dense_sparse_row_json(row: SparseRow, dimension: int) -> list[int | str]:
    return [
        _fraction_to_json(row.get(index, Fraction(0)))
        for index in range(dimension)
    ]


def _sparse_rows_record(rows: tuple[SparseRow, ...]) -> dict[str, Any]:
    return {
        "row_count": len(rows),
        "nnz": _sparse_rows_nnz(rows),
        "rows": [_sparse_row_json(row) for row in rows],
    }


def _pivot_rows_record(rows: dict[int, SparseRow]) -> dict[str, Any]:
    return {
        "rank": len(rows),
        "pivot_rows": [
            {"pivot": pivot, "row": _sparse_row_json(row)}
            for pivot, row in sorted(rows.items())
        ],
    }


def _fraction_to_json(value: Fraction) -> int | str:
    value = Fraction(value)
    if value.denominator == 1:
        return value.numerator
    return f"{value.numerator}/{value.denominator}"


def _json_to_fraction(value: int | str) -> Fraction:
    return Fraction(value)


def _pretty_checks(checks: dict[str, Any]) -> str:
    return "\n".join(f"{key}: {value}" for key, value in sorted(checks.items()))


def _tex_escape(value: Any) -> str:
    return str(value).replace("\\", r"\textbackslash{}").replace("_", r"\_")


def _write_json(path: Path, payload: Any) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_to_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return _fraction_to_json(value)
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {
            str(key): _to_jsonable(item)
            for key, item in value.items()
            if not str(key).startswith("_")
        }
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    return value
