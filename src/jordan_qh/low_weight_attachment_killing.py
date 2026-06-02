"""Experiment 013: strict attachability and low-to-high killing audit."""

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
    reduce_sparse_row,
    sparse_rref,
    term_to_str,
)
from jordan_qh.v2_cells_no_q import (
    ARITHMETIC,
    FIELD,
    MATRIX_CONVENTION,
    TARGET_ALGEBRA,
    Exp011Thresholds,
    _source_row_composition_is_zero,
    _sparse_row_formula,
    initial_generators_and_differentials,
)

EXP013_ID = "EXP-013-strict-attachability-killing-audit"
EXP013_DIRECTORY = "experiments/013-strict-attachability-killing-audit/"
EXP013_PLAN_PATH = "researchplan/subplan013.md"
EXP013_TEX_REPORT = "tex/exp013_strict_attachability_killing_audit.tex"
DEFAULT_REFERENCE_V2_CELLS = "experiments/011-v2-cells-no-Q/data/v2_cells_W10.json"
DEFAULT_REFERENCE_BY_WEIGHT = "experiments/011-v2-cells-no-Q/data/by_weight_W10.json"
REPORT_FORBIDDEN_PHRASES = (
    "all EXP011 candidates are genuine attaching cells",
    "global stabilization",
    "all higher-weight cells are killed",
    "proves no future cells",
)


@dataclass(frozen=True)
class Exp013Run:
    """In-memory result bundle for EXP013."""

    results: dict[str, Any]
    strict_attachability: dict[str, Any]
    killing_audit: dict[str, Any]
    tex_report: str
    log_text: str


def compute_exp013(
    *,
    max_weight: int,
    mode: str,
    output_dir: Path,
    reference_v2_cells: Path,
    reference_by_weight: Path,
    thresholds: Exp011Thresholds | None = None,
    attach_policy: str = "strict-prefix",
) -> Exp013Run:
    """Compute the EXP013 bounded strict attachability and killing audit."""

    if max_weight < 1:
        msg = "max_weight must be positive"
        raise ValueError(msg)
    if attach_policy != "strict-prefix":
        msg = "EXP013 currently supports only attach_policy='strict-prefix'"
        raise ValueError(msg)
    if thresholds is None:
        thresholds = Exp011Thresholds(rank_backend="modular_sparse_v2")

    started = perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    log_lines = [
        "EXP013 strict attachability and low-to-high killing audit",
        f"started_at: {datetime.now().isoformat(timespec='seconds')}",
        f"mode: {mode}",
        f"max_weight: {max_weight}",
        f"attach_policy: {attach_policy}",
        f"reference_v2_cells: {reference_v2_cells.as_posix()}",
        f"reference_by_weight: {reference_by_weight.as_posix()}",
    ]

    v2_reference = _read_json(reference_v2_cells)
    by_weight_reference = _read_json(reference_by_weight)
    cells = [
        cell
        for cell in v2_reference.get("cells", [])
        if int(cell.get("weight", 0)) <= max_weight
    ]
    reference_weights = [
        record
        for record in by_weight_reference.get("weights", [])
        if int(record.get("weight", 0)) <= max_weight
    ]
    log_lines.append(f"candidate_cells_loaded: {len(cells)}")

    base_generators, base_differentials = initial_generators_and_differentials()
    base_model = build_low_weight_jordan_model(
        base_generators,
        base_differentials,
        weight_bound=max_weight,
        max_degree=2,
        workers=max(1, thresholds.workers),
        progress=lambda message: log_lines.append(f"base_model: {message}"),
    )
    candidate_raw = _lift_candidate_raw_vectors(base_model, cells)
    strict_attachability = _audit_strict_attachability(
        model=base_model,
        cells=cells,
        candidate_raw=candidate_raw,
        max_weight=max_weight,
    )
    killing_audit = _audit_low_to_high_killing(
        base_generators=base_generators,
        base_differentials=base_differentials,
        cells=cells,
        candidate_raw=candidate_raw,
        strict_attachability=strict_attachability,
        max_weight=max_weight,
        thresholds=thresholds,
        log_lines=log_lines,
    )

    strictly_attachable_count = sum(
        1
        for record in strict_attachability["cells"]
        if record["strictly_attachable"]
    )
    homology_killing_claim_count = sum(
        1
        for record in killing_audit["candidate_results"]
        if record["status"] == "killed_by_strict_low_weight_cells"
    )
    runtime_seconds = round(perf_counter() - started, 3)
    results = {
        "experiment_id": EXP013_ID,
        "experiment_directory": EXP013_DIRECTORY,
        "plan": EXP013_PLAN_PATH,
        "field": FIELD,
        "arithmetic": ARITHMETIC,
        "target_algebra": TARGET_ALGEBRA,
        "matrix_convention": MATRIX_CONVENTION,
        "max_weight_requested": max_weight,
        "mode": mode,
        "applies_Q": False,
        "constructs_V3_plus": False,
        "attach_policy": attach_policy,
        "reference_v2_cells": reference_v2_cells.as_posix(),
        "reference_by_weight": reference_by_weight.as_posix(),
        "reference_completed_weights": [
            int(record["weight"])
            for record in reference_weights
            if record.get("status") == "completed"
        ],
        "candidate_cell_count": len(cells),
        "strictly_attachable_cell_count": strictly_attachable_count,
        "strict_attachability_failure_count": len(cells)
        - strictly_attachable_count,
        "homology_killing_claim_count": homology_killing_claim_count,
        "runtime_seconds": runtime_seconds,
        "thresholds": _threshold_record(thresholds),
        "strict_attachability_file": f"data/strict_attachability_W{max_weight}.json",
        "killing_audit_file": f"data/killing_audit_W{max_weight}.json",
        "tex_report": EXP013_TEX_REPORT,
        "checks": {
            "exact_rational_arithmetic": True,
            "applies_Q_is_false": True,
            "constructs_V3_plus_is_false": True,
            "all_non_strict_cells_excluded_as_sources": (
                _all_non_strict_cells_excluded(killing_audit)
            ),
            "strict_prefix_rule_enforced": _strict_prefix_rule_enforced(
                killing_audit,
            ),
            "killing_claims_require_chain_condition": (
                _killing_claims_require_chain_condition(killing_audit)
            ),
        },
    }
    results["passed"] = all(results["checks"].values())
    tex_report = render_exp013_tex_report(
        results,
        strict_attachability,
        killing_audit,
    )
    log_lines.append(f"runtime_seconds: {runtime_seconds}")
    log_lines.append(f"passed: {results['passed']}")
    return Exp013Run(
        results=results,
        strict_attachability=strict_attachability,
        killing_audit=killing_audit,
        tex_report=tex_report,
        log_text="\n".join(log_lines) + "\n",
    )


def write_exp013_outputs(run: Exp013Run, output_dir: Path) -> None:
    """Write EXP013 JSON, TeX, and log artifacts."""

    data_dir = output_dir / "data"
    tex_dir = output_dir / "tex"
    log_dir = output_dir / "logs"
    data_dir.mkdir(parents=True, exist_ok=True)
    tex_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    max_weight = int(run.results["max_weight_requested"])
    _write_json(output_dir / "results.json", run.results)
    _write_json(
        data_dir / f"strict_attachability_W{max_weight}.json",
        run.strict_attachability,
    )
    _write_json(
        data_dir / f"killing_audit_W{max_weight}.json",
        run.killing_audit,
    )
    (tex_dir / "exp013_strict_attachability_killing_audit.tex").write_text(
        run.tex_report,
        encoding="utf-8",
    )
    (log_dir / f"run_W{max_weight}.log").write_text(
        run.log_text,
        encoding="utf-8",
    )


def render_exp013_tex_report(
    results: dict[str, Any],
    strict_attachability: dict[str, Any],
    killing_audit: dict[str, Any],
) -> str:
    """Render a concise bounded-evidence EXP013 TeX report."""

    lines = [
        r"\documentclass{article}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage{booktabs}",
        r"\usepackage{longtable}",
        r"\begin{document}",
        r"\section*{Experiment 013: Strict Attachability Killing Audit}",
        (
            "This experiment tests whether EXP011 candidate degree-2 cells "
            "are strict dg attaching data through a bounded weight range. "
            "It does not apply $Q$ and does not construct "
            r"$V_3,V_4,\ldots$."
        ),
        r"\paragraph{Boundary.}",
        (
            "A failed strict attachability check means the chosen raw "
            "representative is not accepted as a dg attaching differential "
            "in this bounded backend. It does not rule out another lift."
        ),
        r"\paragraph{Summary.}",
        (
            "Candidate cells: "
            + str(results["candidate_cell_count"])
            + r"\\ Strictly attachable through W: "
            + str(results["strictly_attachable_cell_count"])
            + r"\\ Homology killing claims: "
            + str(results["homology_killing_claim_count"])
        ),
        r"\section*{Strict Attachability}",
        r"\begin{longtable}{rll}",
        r"\toprule weight & cell & status \\",
        r"\midrule",
    ]
    for record in strict_attachability["cells"]:
        status = (
            "strict"
            if record["strictly_attachable"]
            else "obstructed at W="
            + str(record["first_defect"]["target_weight"])
        )
        lines.append(
            f"{record['cell_weight']} & "
            f"{_tex_escape(record['cell_name'])} & "
            f"{_tex_escape(status)} \\\\",
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\section*{Killing Audit}",
            r"\begin{longtable}{rlll}",
            r"\toprule weight & cell & status & sources \\",
            r"\midrule",
        ],
    )
    for record in killing_audit["candidate_results"]:
        lines.append(
            f"{record['target_weight']} & "
            f"{_tex_escape(record['cell_name'])} & "
            f"{_tex_escape(record['status'])} & "
            f"{_tex_escape(record['allowed_source_cell_names'])} \\\\",
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\section*{Checks}",
            r"\begin{verbatim}",
            json.dumps(results["checks"], indent=2, sort_keys=True),
            r"\end{verbatim}",
            r"\end{document}",
        ],
    )
    return "\n".join(lines)


def report_language_has_no_forbidden_exp013_phrasing(report: str) -> bool:
    """Return true when the report avoids forbidden global interpretations."""

    return not any(phrase in report for phrase in REPORT_FORBIDDEN_PHRASES)


def _audit_strict_attachability(
    *,
    model: LowWeightJordanModel,
    cells: list[dict[str, Any]],
    candidate_raw: dict[str, RawVector],
    max_weight: int,
) -> dict[str, Any]:
    records = []
    for cell in cells:
        name = str(cell["name"])
        weight = int(cell["weight"])
        raw_cycle = candidate_raw[name]
        first_defect = _first_strict_attachability_defect(
            model=model,
            raw_cycle=raw_cycle,
            cell_weight=weight,
            max_weight=max_weight,
        )
        records.append(
            {
                "cell_name": name,
                "cell_weight": weight,
                "degree": int(cell["degree"]),
                "boundary": raw_vector_to_terms(raw_cycle),
                "strictly_attachable": first_defect is None,
                "strictly_attachable_through_weight": (
                    max_weight
                    if first_defect is None
                    else int(first_defect["target_weight"]) - 1
                ),
                "first_defect": first_defect,
            },
        )
    return {
        "experiment_id": EXP013_ID,
        "max_weight_requested": max_weight,
        "base_generator_d_squared_zero": _base_generator_d_squared_zero(model),
        "cells": records,
    }


def _audit_low_to_high_killing(
    *,
    base_generators: tuple[WeightedGenerator, ...],
    base_differentials: dict[str, RawVector],
    cells: list[dict[str, Any]],
    candidate_raw: dict[str, RawVector],
    strict_attachability: dict[str, Any],
    max_weight: int,
    thresholds: Exp011Thresholds,
    log_lines: list[str],
) -> dict[str, Any]:
    strict_by_name = {
        record["cell_name"]: record for record in strict_attachability["cells"]
    }
    cells_by_weight: dict[int, list[dict[str, Any]]] = {}
    for cell in cells:
        cells_by_weight.setdefault(int(cell["weight"]), []).append(cell)

    weight_records: list[dict[str, Any]] = []
    candidate_results: list[dict[str, Any]] = []
    for target_weight in sorted(cells_by_weight):
        target_cells = cells_by_weight[target_weight]
        allowed_cells = [
            cell
            for cell in cells
            if int(cell["weight"]) < target_weight
            and int(
                strict_by_name[str(cell["name"])][
                    "strictly_attachable_through_weight"
                ],
            )
            >= target_weight
        ]
        allowed_names = [str(cell["name"]) for cell in allowed_cells]
        allowed_weights = sorted({int(cell["weight"]) for cell in allowed_cells})
        chain_condition = None
        chain_failure_reason = None
        b_aug_rref: dict[int, SparseRow] | None = None
        c1_basis: tuple[str, ...] = ()

        if allowed_cells:
            model = _build_augmented_model(
                base_generators=base_generators,
                base_differentials=base_differentials,
                allowed_cells=allowed_cells,
                candidate_raw=candidate_raw,
                max_weight=target_weight,
                thresholds=thresholds,
                log_lines=log_lines,
            )
            c0 = model.quotient_space(0, target_weight)
            c1 = model.quotient_space(1, target_weight)
            d1_rows = model.differential_sparse_matrix(
                1,
                target_weight,
                workers=max(1, thresholds.matrix_workers),
            )
            d2_aug_rows = model.differential_sparse_matrix(
                2,
                target_weight,
                workers=max(1, thresholds.matrix_workers),
            )
            chain_condition = _source_row_composition_is_zero(
                first_rows=d2_aug_rows,
                second_rows=d1_rows,
                first_target_dimension=c1.dimension(),
                second_target_dimension=c0.dimension(),
            )
            c1_basis = tuple(term_to_str(term) for term in c1.basis_terms())
            if chain_condition:
                b_aug_rref = sparse_rref(d2_aug_rows)
            else:
                chain_failure_reason = "d2_aug_matrix_times_d1_matrix_nonzero"
            log_lines.append(
                "target_weight "
                f"{target_weight}: allowed_sources={len(allowed_cells)} "
                f"chain_condition={chain_condition}",
            )

        record_candidates = []
        for cell in target_cells:
            name = str(cell["name"])
            target_strict = bool(strict_by_name[name]["strictly_attachable"])
            if not allowed_cells:
                status = "not_tested_no_strict_low_cells"
                remainder = None
            elif chain_condition is not True or b_aug_rref is None:
                status = "not_tested_chain_condition_failed"
                remainder = None
            else:
                c1 = model.quotient_space(1, target_weight)
                candidate_coords = c1.reduce_vector_sparse(candidate_raw[name])
                remainder_row = reduce_sparse_row(candidate_coords, b_aug_rref)
                remainder = {
                    "formula": _sparse_row_formula(remainder_row, c1_basis),
                    "nonzero": bool(remainder_row),
                    "sparse_coordinates": _sparse_row_json(remainder_row),
                }
                status = (
                    "killed_by_strict_low_weight_cells"
                    if not remainder_row
                    else "survives_strict_low_weight_cells"
                )
            candidate_record = {
                "cell_name": name,
                "target_weight": target_weight,
                "target_strictly_attachable": target_strict,
                "allowed_source_weights": allowed_weights,
                "allowed_source_cell_names": allowed_names,
                "chain_condition_verified": chain_condition,
                "status": status,
                "remainder_mod_augmented_boundaries": remainder,
            }
            record_candidates.append(candidate_record)
            candidate_results.append(candidate_record)
        weight_records.append(
            {
                "weight": target_weight,
                "candidate_count": len(target_cells),
                "allowed_source_weights": allowed_weights,
                "allowed_source_cell_names": allowed_names,
                "chain_condition_verified": chain_condition,
                "chain_failure_reason": chain_failure_reason,
                "candidates": record_candidates,
            },
        )
    return {
        "experiment_id": EXP013_ID,
        "max_weight_requested": max_weight,
        "weights": weight_records,
        "candidate_results": candidate_results,
    }


def _first_strict_attachability_defect(
    *,
    model: LowWeightJordanModel,
    raw_cycle: RawVector,
    cell_weight: int,
    max_weight: int,
) -> dict[str, Any] | None:
    generator_defect = _strict_defect_for_raw_product(
        model=model,
        raw_product=raw_cycle,
        target_weight=cell_weight,
        multiplier="1",
    )
    if generator_defect is not None:
        return generator_defect

    for target_weight in range(cell_weight + 1, max_weight + 1):
        multiplier_weight = target_weight - cell_weight
        multipliers = model.quotient_space(0, multiplier_weight).basis_terms()
        for multiplier in multipliers:
            product_vector = _multiply_raw_vector(raw_cycle, multiplier)
            defect = _strict_defect_for_raw_product(
                model=model,
                raw_product=product_vector,
                target_weight=target_weight,
                multiplier=term_to_str(multiplier),
            )
            if defect is not None:
                return defect
    return None


def _strict_defect_for_raw_product(
    *,
    model: LowWeightJordanModel,
    raw_product: RawVector,
    target_weight: int,
    multiplier: str,
) -> dict[str, Any] | None:
    differential = _raw_vector_differential(model, raw_product)
    quotient = model.quotient_space(0, target_weight)
    reduced = quotient.reduce_vector_sparse(differential)
    if not reduced:
        return None
    basis = tuple(term_to_str(term) for term in quotient.basis_terms())
    return {
        "target_weight": target_weight,
        "multiplier": multiplier,
        "defect_nonzero": True,
        "defect_normal_form": _sparse_row_formula(reduced, basis),
        "defect_sparse_coordinates": _sparse_row_json(reduced),
        "raw_differential": raw_vector_to_terms(differential),
    }


def _build_augmented_model(
    *,
    base_generators: tuple[WeightedGenerator, ...],
    base_differentials: dict[str, RawVector],
    allowed_cells: list[dict[str, Any]],
    candidate_raw: dict[str, RawVector],
    max_weight: int,
    thresholds: Exp011Thresholds,
    log_lines: list[str],
) -> LowWeightJordanModel:
    generators = list(base_generators)
    differentials = dict(base_differentials)
    for cell in allowed_cells:
        name = str(cell["name"])
        generators.append(
            WeightedGenerator(
                name,
                degree=int(cell["degree"]),
                weight=int(cell["weight"]),
            ),
        )
        differentials[name] = candidate_raw[name]
    return build_low_weight_jordan_model(
        tuple(generators),
        differentials,
        weight_bound=max_weight,
        max_degree=2,
        workers=max(1, thresholds.workers),
        progress=lambda message: log_lines.append(
            f"augmented_W{max_weight}: {message}",
        ),
    )


def _lift_candidate_raw_vectors(
    model: LowWeightJordanModel,
    cells: list[dict[str, Any]],
) -> dict[str, RawVector]:
    raw_vectors: dict[str, RawVector] = {}
    for cell in cells:
        weight = int(cell["weight"])
        sparse = _parse_sparse_coordinates(
            cell["cycle_z_sparse_coordinates_in_C1_basis"],
        )
        raw_vectors[str(cell["name"])] = model.quotient_space(
            1,
            weight,
        ).lift_sparse_coordinates(sparse)
    return raw_vectors


def _base_generator_d_squared_zero(model: LowWeightJordanModel) -> list[dict[str, Any]]:
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
                "d_squared_zero": not second,
                "d_squared_raw": raw_vector_to_terms(second),
            },
        )
    return records


def _raw_vector_differential(
    model: LowWeightJordanModel,
    vector: RawVector,
) -> RawVector:
    result: RawVector = {}
    for term, coefficient in vector.items():
        for d_term, d_coefficient in model.differential_of_term(term).items():
            _add_raw(result, d_term, coefficient * d_coefficient)
    return result


def _multiply_raw_vector(vector: RawVector, multiplier: Any) -> RawVector:
    result: RawVector = {}
    for term, coefficient in vector.items():
        _add_raw(result, product_term(term, multiplier), coefficient)
    return result


def _all_non_strict_cells_excluded(killing_audit: dict[str, Any]) -> bool:
    for record in killing_audit["candidate_results"]:
        if record["target_strictly_attachable"]:
            continue
        if record["cell_name"] in record["allowed_source_cell_names"]:
            return False
    return True


def _strict_prefix_rule_enforced(killing_audit: dict[str, Any]) -> bool:
    for record in killing_audit["candidate_results"]:
        if any(
            weight >= record["target_weight"]
            for weight in record["allowed_source_weights"]
        ):
            return False
    return True


def _killing_claims_require_chain_condition(killing_audit: dict[str, Any]) -> bool:
    for record in killing_audit["candidate_results"]:
        if (
            record["status"] == "killed_by_strict_low_weight_cells"
            and record["chain_condition_verified"] is not True
        ):
            return False
    return True


def _threshold_record(thresholds: Exp011Thresholds) -> dict[str, Any]:
    return {
        "max_raw_terms_per_space": thresholds.max_raw_terms_per_space,
        "max_quotient_dim": thresholds.max_quotient_dim,
        "max_matrix_nnz": thresholds.max_matrix_nnz,
        "max_runtime_per_weight": thresholds.max_runtime_per_weight,
        "max_memory_gb": thresholds.max_memory_gb,
        "workers": thresholds.workers,
        "matrix_workers": thresholds.matrix_workers,
        "rank_backend": thresholds.rank_backend,
        "rank_progress_interval": thresholds.rank_progress_interval,
        "rank_progress_seconds": thresholds.rank_progress_seconds,
        "max_rank_seconds": thresholds.max_rank_seconds,
    }


def _parse_sparse_coordinates(raw: dict[str, Any]) -> SparseRow:
    return {int(index): Fraction(value) for index, value in raw.items()}


def _sparse_row_json(row: SparseRow) -> dict[str, int | str]:
    return {
        str(index): _fraction_to_json(coefficient)
        for index, coefficient in sorted(row.items())
        if coefficient != 0
    }


def _fraction_to_json(value: Fraction) -> int | str:
    fraction = Fraction(value)
    if fraction.denominator == 1:
        return fraction.numerator
    return str(fraction)


def _add_raw(vector: RawVector, term: Any, coefficient: Fraction) -> None:
    if coefficient == 0:
        return
    vector[term] = vector.get(term, Fraction(0)) + coefficient
    if vector[term] == 0:
        del vector[term]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True),
        encoding="utf-8",
    )


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
