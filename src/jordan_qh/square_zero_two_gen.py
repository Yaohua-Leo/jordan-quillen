"""Experiment 009 helpers for the two-generator square-zero Jordan algebra."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from jordan_qh.chain_complex import FiniteChainComplex, analyze_homology
from jordan_qh.low_weight_jordan import (
    LowWeightJordanModel,
    RawVector,
    WeightedGenerator,
    bounded_homology_representatives,
    build_low_weight_jordan_model,
    product_term,
    raw_vector_to_terms,
)

EXP009_ID = "EXP-009-square-zero-two-generator-quillen-homology"
C0_BASIS = ("x", "y")
C1_BASIS = ("r_xx", "r_xy", "r_yy")
PARTIAL_1_ROWS = (
    (Fraction(0), Fraction(0)),
    (Fraction(0), Fraction(0)),
    (Fraction(0), Fraction(0)),
)
WEIGHT_BOUNDS = (6, 7, 8)
RESOLUTION_DEGREE = 6
MAX_HOMOLOGY_DEGREE = 5


def exp009_degree_one_complex(*, resolution_degree: int = 6) -> FiniteChainComplex:
    """Return the recorded degree 0/1 indecomposable complex for Experiment 009."""
    bases = {0: C0_BASIS, 1: C1_BASIS}
    for degree in range(2, resolution_degree + 1):
        bases[degree] = ()
    return FiniteChainComplex(bases=bases, differentials={1: PARTIAL_1_ROWS})


def exp009_initial_chain_record(*, weight_bound: int) -> dict[str, Any]:
    """Return an honest chain-complex record when the higher backend is absent."""
    complex_ = exp009_degree_one_complex()
    homology_0 = analyze_homology(complex_, max_degree=0)[0]
    return {
        "status": "backend_not_implemented",
        "experiment": EXP009_ID,
        "field": "QQ",
        "category": "nonunital Jordan algebras",
        "matrix_convention": "source_rows_target_coordinates",
        "resolution_degree": 6,
        "max_homology_degree": 5,
        "weight_bound": weight_bound,
        "backend": {
            "name": "exp009_degree_one_sanity_surface",
            "scope": (
                "Records the fixed degree 0 and degree 1 data only; it is "
                "not a bounded quasi-free Jordan replacement backend."
            ),
            "higher_replacement_backend_available": False,
        },
        "target_algebra": {
            "basis": list(C0_BASIS),
            "products": {
                "x*x": "0",
                "x*y": "0",
                "y*y": "0",
            },
        },
        "bases": {
            "C0": list(C0_BASIS),
            "C1": list(C1_BASIS),
        },
        "full_differentials": {
            "d(r_xx)": "x*x",
            "d(r_xy)": "x*y",
            "d(r_yy)": "y*y",
        },
        "indecomposable_differentials": {
            "partial_1(r_xx)": "0",
            "partial_1(r_xy)": "0",
            "partial_1(r_yy)": "0",
        },
        "boundary_matrices_source_rows": {
            "partial_1": _matrix_to_json(PARTIAL_1_ROWS),
        },
        "linear_algebra": {
            "kernels": {"H0_kernel_basis": _matrix_to_json(homology_0.kernel_basis)},
            "images": {"H0_image_basis": _matrix_to_json(homology_0.image_basis)},
            "homology_representatives": {
                "H0": _matrix_to_json(homology_0.homology_representatives),
            },
            "homology_dimensions": {"H0": homology_0.homology_dimension},
            "uncomputed": ["H1", "H2", "H3", "H4", "H5"],
        },
        "checks": {
            "partial_1_is_zero": True,
            "H0_dimension_is_2": homology_0.homology_dimension == 2,
            "recorded_degree_one_d_squared_zero": complex_.d_squared_zero(),
            "full_replacement_d_squared_zero": None,
            "stable_across_weight_bounds": None,
        },
        "warning": (
            "Higher cells, partial_2 through partial_6, and H1 through H5 "
            "are intentionally not filled because the bounded quasi-free "
            "Jordan replacement backend has not been implemented."
        ),
    }


def exp009_run_weight_bounds(
    *,
    weight_bounds: tuple[int, ...] = WEIGHT_BOUNDS,
) -> dict[str, Any]:
    """Run the fixed low-weight backend for all requested weight bounds."""
    records = [
        exp009_bounded_chain_record(weight_bound=weight_bound)
        for weight_bound in weight_bounds
    ]
    selected = records[-1]
    stability = _stability_summary(records)
    selected["checks"]["stable_across_weight_bounds"] = stability["stable"]
    selected["weight_bound_stability"] = stability
    return {
        "selected": selected,
        "summaries": [_record_summary(record) for record in records],
        "stability": stability,
    }


def exp009_bounded_chain_record(*, weight_bound: int) -> dict[str, Any]:
    """Construct the fixed low-weight ordinary Jordan replacement through degree 6."""
    generators, differentials, cells_by_degree = _initial_backend_state()
    boundary_rows_by_degree: dict[int, list[tuple[Fraction, ...]]] = {
        1: list(PARTIAL_1_ROWS),
    }
    cell_records = _initial_cell_records()

    for degree in range(2, RESOLUTION_DEGREE + 1):
        model = build_low_weight_jordan_model(
            tuple(generators),
            differentials,
            weight_bound=weight_bound,
            max_degree=degree,
        )
        representatives = bounded_homology_representatives(
            model,
            degree=degree - 1,
        )
        previous_basis = cells_by_degree[degree - 1]
        cells_by_degree[degree] = []
        boundary_rows_by_degree[degree] = []
        for index, (cell_weight, _coordinates, raw_cycle) in enumerate(
            representatives,
            start=1,
        ):
            cell_name = f"s{degree}_{index:05d}_w{cell_weight}"
            linear_part = _linear_part(raw_cycle, previous_basis)
            d_squared_zero = _raw_vector_is_cycle(
                model,
                raw_cycle,
                degree=degree - 1,
                weight=cell_weight,
            )
            generators.append(
                WeightedGenerator(cell_name, degree=degree, weight=cell_weight),
            )
            differentials[cell_name] = raw_cycle
            cells_by_degree[degree].append(cell_name)
            boundary_rows_by_degree[degree].append(linear_part)
            cell_records.append(
                {
                    "name": cell_name,
                    "degree": degree,
                    "weight": cell_weight,
                    "full_differential": raw_vector_to_terms(raw_cycle),
                    "linear_part_after_Q": _vector_to_basis_expr(
                        linear_part,
                        previous_basis,
                    ),
                    "cycle_killed": raw_vector_to_terms(raw_cycle),
                    "d_squared_zero_checked": d_squared_zero,
                },
            )

    complex_ = FiniteChainComplex(
        bases={degree: tuple(basis) for degree, basis in cells_by_degree.items()},
        differentials={
            degree: tuple(rows)
            for degree, rows in boundary_rows_by_degree.items()
        },
    )
    homology = analyze_homology(complex_, max_degree=MAX_HOMOLOGY_DEGREE)
    d_squared_zero = complex_.d_squared_zero()
    return {
        "status": "run",
        "passed": (
            d_squared_zero
            and homology[0].homology_dimension == 2
            and all(record["d_squared_zero_checked"] for record in cell_records)
        ),
        "experiment": EXP009_ID,
        "field": "QQ",
        "category": "nonunital Jordan algebras",
        "matrix_convention": "source_rows_target_coordinates",
        "resolution_degree": RESOLUTION_DEGREE,
        "max_homology_degree": MAX_HOMOLOGY_DEGREE,
        "weight_bound": weight_bound,
        "backend": {
            "name": "example_specific_low_weight_ordinary_jordan_backend",
            "scope": (
                "Fixed two-generator square-zero example; enumerates the "
                "ordinary commutative nonassociative free algebra modulo the "
                "linearized Jordan identity through the selected weight bound."
            ),
            "higher_replacement_backend_available": True,
            "general_cofibrant_replacement_algorithm": False,
            "leibniz_rule": "d(a*b)=d(a)*b+(-1)^|a| a*d(b)",
            "caveat": (
                "This is bounded computational evidence for this example, "
                "not a general Jordan operad resolution framework."
            ),
        },
        "target_algebra": {
            "basis": list(C0_BASIS),
            "products": {
                "x*x": "0",
                "x*y": "0",
                "y*y": "0",
            },
        },
        "bases": {
            f"C{degree}": list(cells_by_degree.get(degree, ()))
            for degree in range(RESOLUTION_DEGREE + 1)
        },
        "cells": cell_records,
        "full_differentials": {
            f"d({record['name']})": record["full_differential"]
            for record in cell_records
            if record["degree"] > 0
        },
        "indecomposable_differentials": _indecomposable_formulas(
            cells_by_degree,
            boundary_rows_by_degree,
        ),
        "boundary_matrices_source_rows": {
            f"partial_{degree}": _matrix_to_json(tuple(rows))
            for degree, rows in boundary_rows_by_degree.items()
        },
        "linear_algebra": _linear_algebra_record(
            complex_,
            homology,
            boundary_rows_by_degree,
        ),
        "checks": {
            "partial_1_is_zero": all(
                all(entry == 0 for entry in row) for row in PARTIAL_1_ROWS
            ),
            "H0_dimension_is_2": homology[0].homology_dimension == 2,
            "d_squared_zero": d_squared_zero,
            "all_attached_cell_d_squared_zero": all(
                record["d_squared_zero_checked"] for record in cell_records
            ),
            "constructs_through_resolution_degree_6": (
                RESOLUTION_DEGREE in cells_by_degree
            ),
            "partial_1_through_partial_6_recorded": all(
                degree in boundary_rows_by_degree
                for degree in range(1, RESOLUTION_DEGREE + 1)
            ),
            "H5_uses_im_partial_6": True,
            "stable_across_weight_bounds": None,
        },
        "warning": (
            "The weight-bound comparison decides whether this bounded output "
            "is stable or truncated evidence only."
        ),
    }


def _matrix_to_json(rows: tuple[tuple[Fraction, ...], ...]) -> list[list[int | str]]:
    return [[_fraction_to_json(entry) for entry in row] for row in rows]


def _fraction_to_json(value: Fraction) -> int | str:
    if value.denominator == 1:
        return value.numerator
    return f"{value.numerator}/{value.denominator}"


def _initial_backend_state() -> tuple[
    list[WeightedGenerator],
    dict[str, RawVector],
    dict[int, list[str]],
]:
    x = ("g", "x")
    y = ("g", "y")
    generators = [
        WeightedGenerator("x", degree=0, weight=1),
        WeightedGenerator("y", degree=0, weight=1),
        WeightedGenerator("r_xx", degree=1, weight=2),
        WeightedGenerator("r_xy", degree=1, weight=2),
        WeightedGenerator("r_yy", degree=1, weight=2),
    ]
    differentials = {
        "r_xx": {product_term(x, x): Fraction(1)},
        "r_xy": {product_term(x, y): Fraction(1)},
        "r_yy": {product_term(y, y): Fraction(1)},
    }
    cells_by_degree = {
        0: list(C0_BASIS),
        1: list(C1_BASIS),
    }
    return generators, differentials, cells_by_degree


def _initial_cell_records() -> list[dict[str, Any]]:
    records = [
        {
            "name": "x",
            "degree": 0,
            "weight": 1,
            "full_differential": "0",
            "linear_part_after_Q": "0",
            "cycle_killed": None,
            "d_squared_zero_checked": True,
        },
        {
            "name": "y",
            "degree": 0,
            "weight": 1,
            "full_differential": "0",
            "linear_part_after_Q": "0",
            "cycle_killed": None,
            "d_squared_zero_checked": True,
        },
    ]
    for name, differential in [
        ("r_xx", "x*x"),
        ("r_xy", "x*y"),
        ("r_yy", "y*y"),
    ]:
        records.append(
            {
                "name": name,
                "degree": 1,
                "weight": 2,
                "full_differential": differential,
                "linear_part_after_Q": "0",
                "cycle_killed": differential,
                "d_squared_zero_checked": True,
            },
        )
    return records


def _linear_part(
    raw_vector: RawVector,
    previous_basis: list[str],
) -> tuple[Fraction, ...]:
    row = [Fraction(0) for _ in previous_basis]
    basis_index = {name: index for index, name in enumerate(previous_basis)}
    for term, coefficient in raw_vector.items():
        if term[0] != "g":
            continue
        name = str(term[1])
        if name in basis_index:
            row[basis_index[name]] += coefficient
    return tuple(row)


def _raw_vector_is_cycle(
    model: LowWeightJordanModel,
    raw_vector: RawVector,
    *,
    degree: int,
    weight: int,
) -> bool:
    differential: RawVector = {}
    for term, coefficient in raw_vector.items():
        for d_term, d_coefficient in model.differential_of_term(term).items():
            differential[d_term] = (
                differential.get(d_term, Fraction(0)) + coefficient * d_coefficient
            )
            if differential[d_term] == 0:
                del differential[d_term]
    target = model.quotient_space(degree - 1, weight)
    return not target.reduce_vector_sparse(differential)


def _indecomposable_formulas(
    cells_by_degree: dict[int, list[str]],
    boundary_rows_by_degree: dict[int, list[tuple[Fraction, ...]]],
) -> dict[str, str]:
    formulas: dict[str, str] = {}
    for degree, rows in sorted(boundary_rows_by_degree.items()):
        target_basis = cells_by_degree.get(degree - 1, [])
        source_basis = cells_by_degree.get(degree, [])
        for source, row in zip(source_basis, rows, strict=True):
            formulas[f"partial_{degree}({source})"] = _vector_to_basis_expr(
                row,
                target_basis,
            )
    return formulas


def _linear_algebra_record(
    complex_: FiniteChainComplex,
    homology: dict[int, Any],
    boundary_rows_by_degree: dict[int, list[tuple[Fraction, ...]]],
) -> dict[str, Any]:
    ranks = {}
    kernels = {}
    images = {}
    representatives = {}
    representative_formulas = {}
    dimensions = {}
    for degree in range(MAX_HOMOLOGY_DEGREE + 1):
        analysis = homology[degree]
        basis = complex_.bases.get(degree, ())
        ranks[f"partial_{degree}"] = analysis.boundary_rank
        kernels[f"ker_partial_{degree}"] = _matrix_to_json(analysis.kernel_basis)
        images[f"im_partial_{degree + 1}"] = _matrix_to_json(analysis.image_basis)
        representatives[f"H{degree}"] = _matrix_to_json(
            analysis.homology_representatives,
        )
        representative_formulas[f"H{degree}"] = [
            _vector_to_basis_expr(row, list(basis))
            for row in analysis.homology_representatives
        ]
        dimensions[f"H{degree}"] = analysis.homology_dimension
    ranks["partial_6"] = _rank_for_rows(
        tuple(boundary_rows_by_degree[6]),
        len(complex_.bases.get(5, ())),
    )
    return {
        "ranks": ranks,
        "kernels": kernels,
        "images": images,
        "homology_representatives": representatives,
        "homology_representative_formulas": representative_formulas,
        "homology_dimensions": dimensions,
        "H5_image_source": "im(partial_6)",
    }


def _rank_for_rows(rows: tuple[tuple[Fraction, ...], ...], dimension: int) -> int:
    from jordan_qh.linear_algebra import row_rank

    return row_rank(rows, dimension)


def _record_summary(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "weight_bound": record["weight_bound"],
        "status": record["status"],
        "passed": record["passed"],
        "basis_sizes": {
            degree: len(basis) for degree, basis in record["bases"].items()
        },
        "homology_dimensions": record["linear_algebra"]["homology_dimensions"],
        "checks": record["checks"],
    }


def _stability_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    dimensions = [
        record["linear_algebra"]["homology_dimensions"] for record in records
    ]
    representatives = [
        record["linear_algebra"]["homology_representative_formulas"]
        for record in records
    ]
    stable = (
        all(item == dimensions[0] for item in dimensions)
        and all(item == representatives[0] for item in representatives)
    )
    return {
        "stable": stable,
        "weight_bounds": [record["weight_bound"] for record in records],
        "dimension_comparison": {
            str(record["weight_bound"]): record["linear_algebra"][
                "homology_dimensions"
            ]
            for record in records
        },
        "representatives_agree": all(
            item == representatives[0] for item in representatives
        ),
        "interpretation": (
            "stable across W = 6, 7, 8"
            if stable
            else "truncated evidence only; selected weight bounds disagree"
        ),
    }


def _vector_to_basis_expr(row: tuple[Fraction, ...], basis: list[str]) -> str:
    parts: list[str] = []
    for coefficient, name in zip(row, basis, strict=True):
        if coefficient == 0:
            continue
        if coefficient == 1:
            parts.append(name)
        elif coefficient == -1:
            parts.append(f"-{name}")
        else:
            parts.append(f"{coefficient}*{name}")
    if not parts:
        return "0"
    return " + ".join(parts).replace("+ -", "- ")
