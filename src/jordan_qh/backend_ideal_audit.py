"""Experiment 014: backend relation-ideal stability audit."""

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
    build_low_weight_jordan_model,
    generate_terms_by_degree_weight,
    jordan_relation_rows,
    product_term,
    raw_vector_to_terms,
    term_to_str,
)
from jordan_qh.v2_cells_no_q import (
    ARITHMETIC,
    FIELD,
    MATRIX_CONVENTION,
    TARGET_ALGEBRA,
    _sparse_row_formula,
    initial_generators_and_differentials,
)

EXP014_ID = "EXP-014-backend-differential-ideal-audit"
EXP014_DIRECTORY = "experiments/014-backend-differential-ideal-audit/"
EXP014_PLAN_PATH = "researchplan/subplan014.md"
EXP014_TEX_REPORT = "tex/exp014_backend_differential_ideal_audit.tex"
REPORT_FORBIDDEN_PHRASES = (
    "global theorem",
    "infinite weight",
    "fully graded operadic conclusion",
    "all future weights",
    "cofibrant replacement proved",
)
DEFAULT_MULTIPLIER_DEGREES = (0, 1, 2)


@dataclass(frozen=True)
class Exp014Run:
    """In-memory result bundle for EXP014."""

    results: dict[str, Any]
    relation_stability: dict[str, Any]
    first_failures: dict[str, Any]
    tex_report: str
    log_text: str


def compute_exp014(
    *,
    max_weight: int,
    max_degree: int,
    mode: str,
    output_dir: Path,
    workers: int = 1,
    max_memory_gb: float = 20.0,
    multiplier_degrees: tuple[int, ...] = DEFAULT_MULTIPLIER_DEGREES,
) -> Exp014Run:
    """Compute the bounded EXP014 backend relation-ideal stability audit."""

    if max_weight < 1:
        msg = "max_weight must be positive"
        raise ValueError(msg)
    if max_degree < 0:
        msg = "max_degree must be nonnegative"
        raise ValueError(msg)

    started = perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    log_lines = [
        "EXP014 backend differential and multiplicative-ideal audit",
        f"started_at: {datetime.now().isoformat(timespec='seconds')}",
        f"mode: {mode}",
        f"max_weight: {max_weight}",
        f"max_degree: {max_degree}",
        f"workers: {workers}",
        f"max_memory_gb: {max_memory_gb}",
        f"multiplier_degrees: {','.join(str(value) for value in multiplier_degrees)}",
    ]

    generators, differentials = initial_generators_and_differentials()
    model = build_low_weight_jordan_model(
        generators,
        differentials,
        weight_bound=max_weight,
        max_degree=max_degree,
        workers=max(1, workers),
        progress=lambda message: log_lines.append(f"model: {message}"),
    )
    terms_by_key = generate_terms_by_degree_weight(
        generators,
        weight_bound=max_weight,
        max_degree=max_degree,
    )
    relation_rows = jordan_relation_rows(terms_by_key, max_weight, max_degree)
    relation_count = sum(len(rows) for rows in relation_rows.values())
    log_lines.append(f"relation_rows_to_audit: {relation_count}")

    relation_records: list[dict[str, Any]] = []
    relation_reduction_failures = 0
    differential_failures = 0
    multiplication_failures = 0
    first_relation_reduction_failure: dict[str, Any] | None = None
    first_differential_failure: dict[str, Any] | None = None
    first_multiplication_failure: dict[str, Any] | None = None

    checked = 0
    for source_key in sorted(relation_rows):
        source_degree, source_weight = source_key
        for relation_index, relation in enumerate(relation_rows[source_key]):
            record = audit_relation_row(
                model=model,
                relation=relation,
                source_degree=source_degree,
                source_weight=source_weight,
                relation_index=relation_index,
                max_weight=max_weight,
                max_degree=max_degree,
                multiplier_degrees=multiplier_degrees,
            )
            relation_records.append(record)
            checked += 1

            if not record["relation_reduces_to_zero"]:
                relation_reduction_failures += 1
                if first_relation_reduction_failure is None:
                    first_relation_reduction_failure = record
            if not record["differential_stable"]:
                differential_failures += 1
                if first_differential_failure is None:
                    first_differential_failure = record
            if not record["multiplication_stable"]:
                multiplication_failures += 1
                if first_multiplication_failure is None:
                    first_multiplication_failure = record

            if checked % 1_000 == 0:
                log_lines.append(
                    "audit_progress "
                    f"checked={checked} relation_failures="
                    f"{relation_reduction_failures} differential_failures="
                    f"{differential_failures} multiplication_failures="
                    f"{multiplication_failures}",
                )

    runtime_seconds = round(perf_counter() - started, 3)
    passed = (
        relation_reduction_failures == 0
        and differential_failures == 0
        and multiplication_failures == 0
    )
    first_failures = {
        "experiment_id": EXP014_ID,
        "max_weight_requested": max_weight,
        "max_degree_requested": max_degree,
        "first_relation_reduction_failure": first_relation_reduction_failure,
        "first_differential_failure": first_differential_failure,
        "first_multiplication_failure": first_multiplication_failure,
    }
    relation_stability = {
        "experiment_id": EXP014_ID,
        "max_weight_requested": max_weight,
        "max_degree_requested": max_degree,
        "multiplier_degrees": list(multiplier_degrees),
        "relation_records": relation_records,
    }
    results = {
        "experiment_id": EXP014_ID,
        "experiment_directory": EXP014_DIRECTORY,
        "plan": EXP014_PLAN_PATH,
        "field": FIELD,
        "arithmetic": ARITHMETIC,
        "target_algebra": TARGET_ALGEBRA,
        "matrix_convention": MATRIX_CONVENTION,
        "max_weight_requested": max_weight,
        "max_degree_requested": max_degree,
        "mode": mode,
        "workers": workers,
        "max_memory_gb": max_memory_gb,
        "multiplier_degrees": list(multiplier_degrees),
        "applies_Q": False,
        "constructs_V3_plus": False,
        "relation_rows_checked": checked,
        "relation_reduction_failures": relation_reduction_failures,
        "differential_failures": differential_failures,
        "multiplication_failures": multiplication_failures,
        "passed": passed,
        "backend_dg_quotient_evidence": (
            "bounded pass: no relation-ideal stability failure found"
            if passed
            else "bounded failure: backend quotient is not stable in the audit"
        ),
        "runtime_seconds": runtime_seconds,
        "relation_stability_file": (
            f"data/relation_stability_W{max_weight}.json"
        ),
        "first_failures_file": f"data/first_failures_W{max_weight}.json",
        "tex_report": EXP014_TEX_REPORT,
        "checks": {
            "exact_rational_arithmetic": True,
            "applies_Q_is_false": True,
            "constructs_V3_plus_is_false": True,
            "bounded_backend_audit_only": True,
            "relation_rows_self_reduce": relation_reduction_failures == 0,
            "backend_relation_ideal_differential_stable": (
                differential_failures == 0
            ),
            "backend_relation_ideal_multiplication_stable": (
                multiplication_failures == 0
            ),
        },
    }
    tex_report = render_exp014_tex_report(
        results=results,
        first_failures=first_failures,
    )
    log_lines.append(f"runtime_seconds: {runtime_seconds}")
    log_lines.append(f"passed: {passed}")
    log_lines.append(
        "failures: "
        f"relation={relation_reduction_failures} "
        f"differential={differential_failures} "
        f"multiplication={multiplication_failures}",
    )
    return Exp014Run(
        results=results,
        relation_stability=relation_stability,
        first_failures=first_failures,
        tex_report=tex_report,
        log_text="\n".join(log_lines) + "\n",
    )


def audit_relation_row(
    *,
    model: LowWeightJordanModel,
    relation: RawVector,
    source_degree: int,
    source_weight: int,
    relation_index: int,
    max_weight: int,
    max_degree: int,
    multiplier_degrees: tuple[int, ...] = DEFAULT_MULTIPLIER_DEGREES,
) -> dict[str, Any]:
    """Audit one homogeneous backend relation row."""

    source_quotient = model.quotient_space(source_degree, source_weight)
    relation_remainder = source_quotient.reduce_vector_sparse(relation)
    relation_reduces_to_zero = not relation_remainder

    differential_defect = _differential_defect(
        model=model,
        relation=relation,
        source_degree=source_degree,
        source_weight=source_weight,
    )
    multiplication_defect = _first_multiplication_defect(
        model=model,
        relation=relation,
        source_degree=source_degree,
        source_weight=source_weight,
        max_weight=max_weight,
        max_degree=max_degree,
        multiplier_degrees=multiplier_degrees,
    )
    return {
        "source_degree": source_degree,
        "source_weight": source_weight,
        "relation_index": relation_index,
        "relation_formula": raw_vector_to_terms(relation),
        "relation_reduces_to_zero": relation_reduces_to_zero,
        "relation_reduction_defect": (
            _defect_payload(
                quotient_basis=source_quotient.basis_terms(),
                remainder=relation_remainder,
                target_degree=source_degree,
                target_weight=source_weight,
                raw_vector=relation,
            )
            if relation_remainder
            else None
        ),
        "differential_stable": differential_defect is None,
        "multiplication_stable": multiplication_defect is None,
        "first_differential_defect": differential_defect,
        "first_multiplication_defect": multiplication_defect,
    }


def write_exp014_outputs(run: Exp014Run, output_dir: Path) -> None:
    """Write EXP014 JSON, TeX, and log artifacts."""

    data_dir = output_dir / "data"
    tex_dir = output_dir / "tex"
    log_dir = output_dir / "logs"
    data_dir.mkdir(parents=True, exist_ok=True)
    tex_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    max_weight = int(run.results["max_weight_requested"])
    _write_json(output_dir / "results.json", run.results)
    _write_json(
        data_dir / f"relation_stability_W{max_weight}.json",
        run.relation_stability,
    )
    _write_json(data_dir / f"first_failures_W{max_weight}.json", run.first_failures)
    (tex_dir / "exp014_backend_differential_ideal_audit.tex").write_text(
        run.tex_report,
        encoding="utf-8",
    )
    (log_dir / f"run_W{max_weight}.log").write_text(
        run.log_text,
        encoding="utf-8",
    )


def render_exp014_tex_report(
    *,
    results: dict[str, Any],
    first_failures: dict[str, Any],
) -> str:
    """Render a concise bounded backend-audit TeX report."""

    lines = [
        r"\documentclass{article}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage{booktabs}",
        r"\usepackage{longtable}",
        r"\begin{document}",
        r"\section*{Experiment 014: Backend Ideal Audit}",
        (
            "This is a bounded backend audit only. It checks whether the "
            r"`low\_weight\_jordan' ordinary relation quotient is stable under "
            "the signed derivation differential and under multiplication in "
            "the tested range. It does not apply $Q$ and does not construct "
            r"$V_3,V_4,\ldots$. It makes no unbounded or theorem-level claim."
        ),
        r"\paragraph{Boundary.}",
        (
            "The output is bounded computational evidence about the current "
            "backend convention. A failure means later EXP011 or EXP013 "
            "diagnostics should remain backend-relative until the quotient "
            "convention is repaired or separately justified."
        ),
        r"\paragraph{Summary.}",
        (
            "Relation rows checked: "
            + str(results["relation_rows_checked"])
            + r"\\ Relation reduction failures: "
            + str(results["relation_reduction_failures"])
            + r"\\ Differential failures: "
            + str(results["differential_failures"])
            + r"\\ Multiplication failures: "
            + str(results["multiplication_failures"])
            + r"\\ Passed: "
            + str(results["passed"])
        ),
        r"\section*{First Failures}",
        r"\begin{verbatim}",
        json.dumps(_first_failure_summary(first_failures), indent=2, sort_keys=True),
        r"\end{verbatim}",
        r"\section*{Checks}",
        r"\begin{verbatim}",
        json.dumps(results["checks"], indent=2, sort_keys=True),
        r"\end{verbatim}",
        r"\end{document}",
    ]
    return "\n".join(lines)


def report_language_has_no_forbidden_exp014_phrasing(report: str) -> bool:
    """Return true when the report avoids forbidden global interpretations."""

    return not any(phrase in report for phrase in REPORT_FORBIDDEN_PHRASES)


def _differential_defect(
    *,
    model: LowWeightJordanModel,
    relation: RawVector,
    source_degree: int,
    source_weight: int,
) -> dict[str, Any] | None:
    differential = _raw_vector_differential(model, relation)
    target_degree = source_degree - 1
    if not differential:
        return None
    if target_degree < 0:
        return {
            "target_degree": target_degree,
            "target_weight": source_weight,
            "defect_nonzero": True,
            "defect_normal_form": raw_vector_to_terms(differential),
            "defect_sparse_coordinates": None,
            "raw_vector": raw_vector_to_terms(differential),
        }
    target_quotient = model.quotient_space(target_degree, source_weight)
    reduced = target_quotient.reduce_vector_sparse(differential)
    if not reduced:
        return None
    return _defect_payload(
        quotient_basis=target_quotient.basis_terms(),
        remainder=reduced,
        target_degree=target_degree,
        target_weight=source_weight,
        raw_vector=differential,
    )


def _first_multiplication_defect(
    *,
    model: LowWeightJordanModel,
    relation: RawVector,
    source_degree: int,
    source_weight: int,
    max_weight: int,
    max_degree: int,
    multiplier_degrees: tuple[int, ...],
) -> dict[str, Any] | None:
    for multiplier_degree in sorted(set(multiplier_degrees)):
        target_degree = source_degree + multiplier_degree
        if target_degree > max_degree:
            continue
        for multiplier_weight in range(1, max_weight - source_weight + 1):
            target_weight = source_weight + multiplier_weight
            multipliers = model.quotient_space(
                multiplier_degree,
                multiplier_weight,
            ).basis_terms()
            for multiplier in multipliers:
                product_vector = _multiply_raw_vector(relation, multiplier)
                target_quotient = model.quotient_space(target_degree, target_weight)
                reduced = target_quotient.reduce_vector_sparse(product_vector)
                if reduced:
                    payload = _defect_payload(
                        quotient_basis=target_quotient.basis_terms(),
                        remainder=reduced,
                        target_degree=target_degree,
                        target_weight=target_weight,
                        raw_vector=product_vector,
                    )
                    payload.update(
                        {
                            "multiplier": term_to_str(multiplier),
                            "multiplier_degree": multiplier_degree,
                            "multiplier_weight": multiplier_weight,
                        },
                    )
                    return payload
    return None


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


def _defect_payload(
    *,
    quotient_basis: tuple[Any, ...],
    remainder: SparseRow,
    target_degree: int,
    target_weight: int,
    raw_vector: RawVector,
) -> dict[str, Any]:
    basis = tuple(term_to_str(term) for term in quotient_basis)
    return {
        "target_degree": target_degree,
        "target_weight": target_weight,
        "defect_nonzero": bool(remainder),
        "defect_normal_form": _sparse_row_formula(remainder, basis),
        "defect_sparse_coordinates": _sparse_row_json(remainder),
        "raw_vector": raw_vector_to_terms(raw_vector),
    }


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


def _first_failure_summary(first_failures: dict[str, Any]) -> dict[str, Any]:
    return {
        key: _compact_failure(value)
        for key, value in first_failures.items()
        if key.startswith("first_")
    }


def _compact_failure(value: Any) -> Any:
    if value is None:
        return None
    if not isinstance(value, dict):
        return value
    return {
        "source_degree": value.get("source_degree"),
        "source_weight": value.get("source_weight"),
        "relation_index": value.get("relation_index"),
        "first_differential_defect": value.get("first_differential_defect"),
        "first_multiplication_defect": value.get("first_multiplication_defect"),
        "relation_reduction_defect": value.get("relation_reduction_defect"),
    }


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True),
        encoding="utf-8",
    )
