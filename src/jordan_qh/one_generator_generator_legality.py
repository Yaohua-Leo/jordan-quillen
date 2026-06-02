"""Experiment 101: legality audit for EXP100 generators.

This module validates EXP100 generator candidates in the spirit of EXP013.
The audit has two layers:

* V1 relation generators are checked as target-kernel relations whose
  degree-zero multiplicative closure still maps to zero in
  ``Jord<x>/(x^2)`` through the requested bound.
* V2 attaching generators are checked strictly: for a proposed differential
  ``d(s)=z``, every tested degree-zero multiplier ``m`` must satisfy
  ``d(z*m)=0`` in the bounded ``A^(1)`` backend.

The result is bounded computational evidence only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Any

from jordan_qh.low_weight_jordan import (
    LowWeightJordanModel,
    RawVector,
    SparseRow,
    WeightedGenerator,
    build_low_weight_jordan_model,
    product_term,
    raw_vector_to_terms,
    sparse_echelon,
    term_to_str,
)
from jordan_qh.one_generator_cofibrant import (
    ARITHMETIC,
    FIELD,
    MATRIX_CONVENTION,
    TARGET_ALGEBRA,
)

EXP101_ID = "EXP-101-one-generator-generator-legality-audit"
EXP101_DIRECTORY = "experiments/101-one-generator-generator-legality-audit/"
EXP101_PLAN_PATH = "researchplan/subplan101.md"
EXP101_TEX_REPORT = "tex/exp101_one_generator_generator_legality_audit.tex"
DEFAULT_REFERENCE_RESULTS = (
    "experiments/100-square-zero-nonunital-cofibrant-weight10/results.json"
)
DEFAULT_REFERENCE_CELLS = (
    "experiments/100-square-zero-nonunital-cofibrant-weight10/data/cells_W10.json"
)
REPORT_FORBIDDEN_PHRASES = (
    "all generators are globally legal",
    "proves the full cofibrant replacement",
    "global stabilization",
    "all higher cells are absent",
    "no future obstruction",
)


@dataclass(frozen=True)
class Exp101Run:
    """In-memory result bundle for EXP101."""

    results: dict[str, Any]
    v1_legality: dict[str, Any]
    v2_strict_attachability: dict[str, Any]
    chain_audit: dict[str, Any]
    tex_report: str
    log_text: str


def compute_exp101(
    *,
    max_weight: int,
    output_dir: Path,
    reference_cells: Path,
    reference_results: Path,
) -> Exp101Run:
    """Compute the EXP101 bounded generator legality audit."""

    if max_weight < 1:
        msg = "max_weight must be positive"
        raise ValueError(msg)

    start = perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    log_lines = [
        "EXP101 one-generator generator legality audit",
        f"started_at: {datetime.now().isoformat(timespec='seconds')}",
        f"max_weight: {max_weight}",
        f"reference_cells: {reference_cells.as_posix()}",
        f"reference_results: {reference_results.as_posix()}",
    ]

    reference_results_payload = _read_json(reference_results)
    reference_cells_payload = _read_json(reference_cells)
    v1_cells = [
        cell
        for cell in reference_cells_payload.get("V1_cells", [])
        if int(cell.get("weight", 0)) <= max_weight
    ]
    v2_cells = [
        cell
        for cell in reference_cells_payload.get("V2_cells", [])
        if int(cell.get("weight", 0)) <= max_weight
    ]

    degree_zero_model = build_low_weight_jordan_model(
        (WeightedGenerator("x", degree=0, weight=1),),
        {},
        weight_bound=max_weight,
        max_degree=0,
    )
    v1_raw = _lift_v1_raw_vectors(degree_zero_model, v1_cells)
    v1_legality = _audit_v1_legality(
        model=degree_zero_model,
        v1_cells=v1_cells,
        v1_raw=v1_raw,
        max_weight=max_weight,
    )

    a1_generators, a1_differentials = _a1_generators_and_differentials(
        v1_cells,
        v1_raw,
    )
    a1_model = build_low_weight_jordan_model(
        a1_generators,
        a1_differentials,
        weight_bound=max_weight,
        max_degree=2,
    )
    v2_raw = _lift_v2_raw_vectors(a1_model, v2_cells)
    v2_strict_attachability = _audit_v2_strict_attachability(
        model=a1_model,
        v2_cells=v2_cells,
        v2_raw=v2_raw,
        max_weight=max_weight,
    )
    chain_audit = _audit_chain_condition(a1_model, max_weight=max_weight)
    generator_d_squared = _generator_d_squared_records(a1_model)

    v1_legal_count = sum(
        1 for record in v1_legality["cells"] if record["legal_through_weight"]
    )
    v2_strict_count = sum(
        1
        for record in v2_strict_attachability["cells"]
        if record["strictly_attachable"]
    )
    runtime_seconds = round(perf_counter() - start, 3)
    results = {
        "experiment_id": EXP101_ID,
        "experiment_directory": EXP101_DIRECTORY,
        "plan": EXP101_PLAN_PATH,
        "field": FIELD,
        "arithmetic": ARITHMETIC,
        "target_algebra": TARGET_ALGEBRA,
        "matrix_convention": MATRIX_CONVENTION,
        "max_weight_requested": max_weight,
        "reference_results": reference_results.as_posix(),
        "reference_cells": reference_cells.as_posix(),
        "reference_experiment_id": reference_results_payload.get("experiment_id"),
        "reference_exp100_passed": bool(reference_results_payload.get("passed")),
        "applies_Q": False,
        "constructs_V3_plus": False,
        "constructs_homology_killing_claims": False,
        "v1_candidate_count": len(v1_cells),
        "v1_legal_generator_count": v1_legal_count,
        "v1_legality_failure_count": len(v1_cells) - v1_legal_count,
        "v2_candidate_count": len(v2_cells),
        "v2_strictly_attachable_cell_count": v2_strict_count,
        "v2_strict_attachability_failure_count": len(v2_cells) - v2_strict_count,
        "homology_killing_claim_count": 0,
        "generator_d_squared": generator_d_squared,
        "runtime_seconds": runtime_seconds,
        "v1_legality_file": f"data/v1_legality_W{max_weight}.json",
        "v2_strict_attachability_file": (
            f"data/v2_strict_attachability_W{max_weight}.json"
        ),
        "chain_audit_file": f"data/chain_audit_W{max_weight}.json",
        "tex_report": EXP101_TEX_REPORT,
        "checks": {
            "reference_exp100_passed": bool(reference_results_payload.get("passed")),
            "exact_rational_arithmetic": True,
            "applies_Q_is_false": True,
            "constructs_V3_plus_is_false": True,
            "all_v1_generators_legal_through_bound": all(
                record["legal_through_weight"] for record in v1_legality["cells"]
            ),
            "all_declared_generators_d_squared_zero": all(
                record["d_squared_zero"] for record in generator_d_squared
            ),
            "all_v2_generator_level_differentials_are_cycles": all(
                record["generator_level_cycle"] for record in (
                    v2_strict_attachability["cells"]
                )
            ),
            "v2_strict_attachability_audit_completed": (
                len(v2_strict_attachability["cells"]) == len(v2_cells)
            ),
            "chain_condition_checks_passed": all(
                record["d2_matrix_times_d1_matrix_is_zero"]
                for record in chain_audit["weights"]
            ),
            "does_not_make_homology_killing_claims": True,
        },
    }
    tex_report = render_exp101_tex_report(
        results=results,
        v1_legality=v1_legality,
        v2_strict_attachability=v2_strict_attachability,
        chain_audit=chain_audit,
    )
    results["checks"]["report_language_has_no_forbidden_global_phrasing"] = (
        report_language_has_no_forbidden_exp101_phrasing(tex_report)
    )
    results["passed"] = all(results["checks"].values())
    tex_report = render_exp101_tex_report(
        results=results,
        v1_legality=v1_legality,
        v2_strict_attachability=v2_strict_attachability,
        chain_audit=chain_audit,
    )
    log_lines.append(f"v1_candidate_count: {len(v1_cells)}")
    log_lines.append(f"v1_legal_generator_count: {v1_legal_count}")
    log_lines.append(f"v2_candidate_count: {len(v2_cells)}")
    log_lines.append(f"v2_strictly_attachable_cell_count: {v2_strict_count}")
    log_lines.append(f"runtime_seconds: {runtime_seconds}")
    log_lines.append(f"passed: {results['passed']}")
    return Exp101Run(
        results=results,
        v1_legality=v1_legality,
        v2_strict_attachability=v2_strict_attachability,
        chain_audit=chain_audit,
        tex_report=tex_report,
        log_text="\n".join(log_lines) + "\n",
    )


def write_exp101_outputs(run: Exp101Run, output_dir: Path) -> None:
    """Write EXP101 JSON, TeX, and log artifacts."""

    data_dir = output_dir / "data"
    tex_dir = output_dir / "tex"
    log_dir = output_dir / "logs"
    data_dir.mkdir(parents=True, exist_ok=True)
    tex_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    max_weight = int(run.results["max_weight_requested"])
    _write_json(output_dir / "results.json", run.results)
    _write_json(data_dir / f"v1_legality_W{max_weight}.json", run.v1_legality)
    _write_json(
        data_dir / f"v2_strict_attachability_W{max_weight}.json",
        run.v2_strict_attachability,
    )
    _write_json(data_dir / f"chain_audit_W{max_weight}.json", run.chain_audit)
    (tex_dir / "exp101_one_generator_generator_legality_audit.tex").write_text(
        run.tex_report,
        encoding="utf-8",
    )
    (log_dir / f"run_W{max_weight}.log").write_text(
        run.log_text,
        encoding="utf-8",
    )


def render_exp101_tex_report(
    *,
    results: dict[str, Any],
    v1_legality: dict[str, Any],
    v2_strict_attachability: dict[str, Any],
    chain_audit: dict[str, Any],
) -> str:
    """Render a concise bounded-evidence TeX report for EXP101."""

    lines = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{booktabs}",
        r"\usepackage{url}",
        r"\begin{document}",
        r"\section*{Experiment 101: Generator Legality Audit}",
        (
            "This experiment audits EXP100 generator candidates through a "
            "bounded weight range. It does not apply $Q$, does not construct "
            r"$V_3,V_4,\ldots$, and makes no homology killing claim."
        ),
        r"\paragraph{Reference artifacts.}",
        r"\begin{description}",
        (
            r"\item[results] \path|"
            + _tex_path(_short_reference_path(results["reference_results"]))
            + "|"
        ),
        (
            r"\item[cells] \path|"
            + _tex_path(_short_reference_path(results["reference_cells"]))
            + "|"
        ),
        r"\end{description}",
        r"\paragraph{Summary.}",
        (
            f"V1 candidates: {results['v1_candidate_count']}; "
            f"legal through W: {results['v1_legal_generator_count']}."
        ),
        (
            f"V2 candidates: {results['v2_candidate_count']}; "
            "strictly attachable through W: "
            f"{results['v2_strictly_attachable_cell_count']}."
        ),
        r"\section*{V1 Relation-Generator Audit}",
        r"\begin{center}",
        r"\begin{tabular}{rll}",
        r"\toprule weight & cell & status \\",
        r"\midrule",
    ]
    for record in v1_legality["cells"]:
        status = (
            "legal through W"
            if record["legal_through_weight"]
            else "failed at W="
            + str(record["first_failure"]["target_weight"])
        )
        lines.append(
            f"{record['cell_weight']} & "
            f"{_tex_escape(record['cell_name'])} & "
            f"{_tex_escape(status)} \\\\",
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{center}",
            r"\section*{V2 Strict Attachability Audit}",
            r"\begin{center}",
            r"\begin{tabular}{rlll}",
            r"\toprule weight & cell & status & first defect \\",
            r"\midrule",
        ],
    )
    for record in v2_strict_attachability["cells"]:
        if record["strictly_attachable"]:
            status = "strict through W"
            defect = "none"
        else:
            status = "obstructed"
            first = record["first_defect"]
            defect = (
                "W="
                + str(first["target_weight"])
                + ", m="
                + str(first["multiplier"])
            )
        lines.append(
            f"{record['cell_weight']} & "
            f"{_tex_escape(record['cell_name'])} & "
            f"{_tex_escape(status)} & "
            f"{_tex_escape(defect)} \\\\",
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{center}",
            r"\section*{Chain Condition}",
            r"\begin{center}",
            r"\begin{tabular}{rrrrc}",
            (
                r"\toprule weight & $\dim C_0$ & $\dim C_1$ & "
                r"$\dim C_2$ & $d_2d_1=0$ \\"
            ),
            r"\midrule",
        ],
    )
    for record in chain_audit["weights"]:
        lines.append(
            f"{record['weight']} & {record['dim_C0']} & "
            f"{record['dim_C1']} & {record['dim_C2']} & "
            f"{record['d2_matrix_times_d1_matrix_is_zero']} \\\\",
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{center}",
            r"\section*{Checks}",
            r"\begin{verbatim}",
            json.dumps(results["checks"], indent=2, sort_keys=True),
            r"\end{verbatim}",
            r"\section*{Interpretation Boundary}",
            (
                "A V2 obstruction means the chosen EXP100 representative is "
                "not accepted as a strict dg attaching differential in this "
                "bounded backend and audit range. It does not rule out an "
                "alternative representative, a corrected lift, or behavior "
                "outside the tested bound."
            ),
            r"\end{document}",
            "",
        ],
    )
    return "\n".join(lines)


def report_language_has_no_forbidden_exp101_phrasing(report: str) -> bool:
    """Return true when the report avoids forbidden global interpretations."""

    return not any(phrase in report for phrase in REPORT_FORBIDDEN_PHRASES)


def _audit_v1_legality(
    *,
    model: LowWeightJordanModel,
    v1_cells: list[dict[str, Any]],
    v1_raw: dict[str, RawVector],
    max_weight: int,
) -> dict[str, Any]:
    records = []
    for cell in v1_cells:
        name = str(cell["name"])
        weight = int(cell["weight"])
        checks = _target_multiplicative_closure_checks(
            model=model,
            raw_relation=v1_raw[name],
            relation_weight=weight,
            max_weight=max_weight,
        )
        first_failure = next(
            (check for check in checks if not check["maps_to_zero_in_target"]),
            None,
        )
        records.append(
            {
                "cell_name": name,
                "cell_weight": weight,
                "degree": int(cell["degree"]),
                "differential": raw_vector_to_terms(v1_raw[name]),
                "legal_through_weight": first_failure is None,
                "strictly_legal_through_weight": (
                    max_weight
                    if first_failure is None
                    else int(first_failure["target_weight"]) - 1
                ),
                "first_failure": first_failure,
                "multiplier_checks": checks,
            },
        )
    return {
        "experiment_id": EXP101_ID,
        "max_weight_requested": max_weight,
        "cells": records,
    }


def _audit_v2_strict_attachability(
    *,
    model: LowWeightJordanModel,
    v2_cells: list[dict[str, Any]],
    v2_raw: dict[str, RawVector],
    max_weight: int,
) -> dict[str, Any]:
    records = []
    for cell in v2_cells:
        name = str(cell["name"])
        weight = int(cell["weight"])
        checks = _v2_strict_checks(
            model=model,
            raw_cycle=v2_raw[name],
            cell_weight=weight,
            max_weight=max_weight,
        )
        first_defect = next(
            (check for check in checks if check["defect_nonzero"]),
            None,
        )
        generator_level = next(
            check for check in checks if check["multiplier"] == "1"
        )
        records.append(
            {
                "cell_name": name,
                "cell_weight": weight,
                "degree": int(cell["degree"]),
                "boundary": raw_vector_to_terms(v2_raw[name]),
                "generator_level_cycle": not generator_level["defect_nonzero"],
                "strictly_attachable": first_defect is None,
                "strictly_attachable_through_weight": (
                    max_weight
                    if first_defect is None
                    else int(first_defect["target_weight"]) - 1
                ),
                "first_defect": first_defect,
                "multiplier_checks": checks,
            },
        )
    return {
        "experiment_id": EXP101_ID,
        "max_weight_requested": max_weight,
        "cells": records,
    }


def _audit_chain_condition(
    model: LowWeightJordanModel,
    *,
    max_weight: int,
) -> dict[str, Any]:
    records = []
    for weight in range(1, max_weight + 1):
        c0 = model.quotient_space(0, weight)
        c1 = model.quotient_space(1, weight)
        c2 = model.quotient_space(2, weight)
        d1_rows = model.differential_sparse_matrix(1, weight)
        d2_rows = model.differential_sparse_matrix(2, weight)
        records.append(
            {
                "weight": weight,
                "dim_C0": c0.dimension(),
                "dim_C1": c1.dimension(),
                "dim_C2": c2.dimension(),
                "rank_d1": len(sparse_echelon(d1_rows)),
                "rank_d2": len(sparse_echelon(d2_rows)),
                "d2_matrix_times_d1_matrix_is_zero": (
                    _source_row_composition_is_zero(
                        first_rows=d2_rows,
                        second_rows=d1_rows,
                    )
                ),
            },
        )
    return {
        "experiment_id": EXP101_ID,
        "max_weight_requested": max_weight,
        "weights": records,
    }


def _target_multiplicative_closure_checks(
    *,
    model: LowWeightJordanModel,
    raw_relation: RawVector,
    relation_weight: int,
    max_weight: int,
) -> list[dict[str, Any]]:
    checks = []
    for target_weight in range(relation_weight, max_weight + 1):
        multiplier_weight = target_weight - relation_weight
        products = [(raw_relation, "1")]
        if multiplier_weight > 0:
            products = [
                (_raw_product(raw_relation, {term: Fraction(1)}), term_to_str(term))
                for term in model.quotient_space(0, multiplier_weight).basis_terms()
            ]
        for product, multiplier_name in products:
            source_space = model.quotient_space(0, target_weight)
            source_row = source_space.reduce_vector_sparse(product)
            target_dimension, epsilon_rows = _presentation_rows(
                source_space,
                target_weight,
            )
            epsilon_image = _apply_source_row_map(source_row, epsilon_rows)
            checks.append(
                {
                    "target_weight": target_weight,
                    "multiplier": multiplier_name,
                    "source_normal_form": _sparse_row_formula(
                        source_row,
                        _basis_names(source_space),
                    ),
                    "epsilon_image": _sparse_row_formula(
                        epsilon_image,
                        ("x_bar",) if target_dimension else (),
                    ),
                    "maps_to_zero_in_target": not epsilon_image,
                    "epsilon_sparse_coordinates": _sparse_row_json(epsilon_image),
                },
            )
    return checks


def _v2_strict_checks(
    *,
    model: LowWeightJordanModel,
    raw_cycle: RawVector,
    cell_weight: int,
    max_weight: int,
) -> list[dict[str, Any]]:
    checks = []
    for target_weight in range(cell_weight, max_weight + 1):
        multiplier_weight = target_weight - cell_weight
        products = [(raw_cycle, "1")]
        if multiplier_weight > 0:
            products = [
                (_raw_product(raw_cycle, {term: Fraction(1)}), term_to_str(term))
                for term in model.quotient_space(0, multiplier_weight).basis_terms()
            ]
        for product, multiplier_name in products:
            differential = _raw_vector_differential(model, product)
            target_space = model.quotient_space(0, target_weight)
            reduced = target_space.reduce_vector_sparse(differential)
            checks.append(
                {
                    "target_weight": target_weight,
                    "multiplier": multiplier_name,
                    "defect_nonzero": bool(reduced),
                    "defect_normal_form": _sparse_row_formula(
                        reduced,
                        _basis_names(target_space),
                    ),
                    "defect_sparse_coordinates": _sparse_row_json(reduced),
                    "raw_differential": raw_vector_to_terms(differential),
                },
            )
    return checks


def _generator_d_squared_records(
    model: LowWeightJordanModel,
) -> list[dict[str, Any]]:
    records = []
    for generator in model.generators:
        term = ("g", generator.name)
        first = model.differential_of_term(term)
        second = _raw_vector_differential(model, first)
        records.append(
            {
                "name": generator.name,
                "degree": generator.degree,
                "weight": generator.weight,
                "differential": raw_vector_to_terms(first),
                "d_squared_zero": not second,
                "d_squared_raw": raw_vector_to_terms(second),
            },
        )
    return records


def _lift_v1_raw_vectors(
    model: LowWeightJordanModel,
    cells: list[dict[str, Any]],
) -> dict[str, RawVector]:
    raw_vectors: dict[str, RawVector] = {}
    for cell in cells:
        weight = int(cell["weight"])
        sparse = _parse_sparse_coordinates(cell["differential_sparse_coordinates"])
        raw_vectors[str(cell["name"])] = model.quotient_space(
            0,
            weight,
        ).lift_sparse_coordinates(sparse)
    return raw_vectors


def _lift_v2_raw_vectors(
    model: LowWeightJordanModel,
    cells: list[dict[str, Any]],
) -> dict[str, RawVector]:
    raw_vectors: dict[str, RawVector] = {}
    for cell in cells:
        weight = int(cell["weight"])
        sparse = _parse_sparse_coordinates(cell["differential_sparse_coordinates"])
        raw_vectors[str(cell["name"])] = model.quotient_space(
            1,
            weight,
        ).lift_sparse_coordinates(sparse)
    return raw_vectors


def _a1_generators_and_differentials(
    v1_cells: list[dict[str, Any]],
    v1_raw: dict[str, RawVector],
) -> tuple[tuple[WeightedGenerator, ...], dict[str, RawVector]]:
    generators = [WeightedGenerator("x", degree=0, weight=1)]
    differentials: dict[str, RawVector] = {}
    for cell in v1_cells:
        name = str(cell["name"])
        generators.append(
            WeightedGenerator(name, degree=1, weight=int(cell["weight"])),
        )
        differentials[name] = v1_raw[name]
    return tuple(generators), differentials


def _raw_vector_differential(
    model: LowWeightJordanModel,
    vector: RawVector,
) -> RawVector:
    result: RawVector = {}
    for term, coefficient in vector.items():
        for d_term, d_coefficient in model.differential_of_term(term).items():
            _add_raw(result, d_term, coefficient * d_coefficient)
    return result


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


def _presentation_rows(
    space: Any,
    weight: int,
) -> tuple[int, tuple[SparseRow, ...]]:
    if weight != 1:
        return 0, tuple({} for _ in range(space.dimension()))
    rows: list[SparseRow] = []
    for term in space.basis_terms():
        rows.append({0: Fraction(1)} if term_to_str(term) == "x" else {})
    return 1, tuple(rows)


def _source_row_composition_is_zero(
    *,
    first_rows: tuple[SparseRow, ...],
    second_rows: tuple[SparseRow, ...],
) -> bool:
    return all(not _apply_source_row_map(row, second_rows) for row in first_rows)


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


def _basis_names(space: Any) -> tuple[str, ...]:
    return tuple(term_to_str(term) for term in space.basis_terms())


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


def _parse_sparse_coordinates(raw: dict[str, Any]) -> SparseRow:
    return {int(index): Fraction(value) for index, value in raw.items()}


def _sparse_row_json(row: SparseRow) -> dict[str, int | str]:
    return {
        str(index): _fraction_to_json(coefficient)
        for index, coefficient in sorted(row.items())
        if coefficient != 0
    }


def _fraction_to_json(value: Fraction) -> int | str:
    value = Fraction(value)
    if value.denominator == 1:
        return value.numerator
    return f"{value.numerator}/{value.denominator}"


def _add_raw(vector: RawVector, term: Any, coefficient: Fraction) -> None:
    if coefficient == 0:
        return
    vector[term] = vector.get(term, Fraction(0)) + coefficient
    if vector[term] == 0:
        del vector[term]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
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
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    return value


def _tex_escape(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "_": r"\_",
        "%": r"\%",
        "&": r"\&",
        "#": r"\#",
        "{": r"\{",
        "}": r"\}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _tex_path(value: str) -> str:
    return value.replace("|", "/")


def _short_reference_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    marker = "experiments/"
    if marker in normalized:
        return normalized[normalized.index(marker) :]
    return normalized
