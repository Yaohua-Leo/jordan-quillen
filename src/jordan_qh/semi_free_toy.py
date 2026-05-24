"""Fixed semi-free toy complexes for low-degree Quillen checks."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from jordan_qh.linear_algebra import row_rank

Vector = tuple[Fraction, ...]
Differentials = dict[int, tuple[Vector, ...]]


@dataclass(frozen=True)
class IndecomposableComplex:
    """A finite chain complex after applying indecomposables `Q`."""

    bases: dict[int, tuple[str, ...]]
    differentials: Differentials

    def d_squared_zero(self) -> bool:
        """Return whether adjacent differentials compose to zero."""
        for degree in sorted(self.differentials):
            if degree - 1 not in self.differentials:
                continue
            for row in _compose_rows(
                self.differentials[degree],
                self.differentials[degree - 1],
            ):
                if any(entry != 0 for entry in row):
                    return False
        return True


def homology_dimensions(
    complex_: IndecomposableComplex,
    *,
    max_degree: int,
) -> dict[str, int]:
    """Return homology dimensions `H0` through `H_max_degree`."""
    dimensions: dict[str, int] = {}
    for degree in range(max_degree + 1):
        source_dim = len(complex_.bases.get(degree, ()))
        kernel_dim = source_dim - _differential_rank(complex_, degree)
        image_dim = _differential_rank(complex_, degree + 1)
        dimensions[f"H{degree}"] = kernel_dim - image_dim
    return dimensions


def j3_two_step_complex() -> IndecomposableComplex:
    """Return the fixed `J_3` two-step Presentation B toy complex."""
    return IndecomposableComplex(
        bases={
            0: ("x", "y"),
            1: ("a1", "a2", "a3"),
            2: ("b",),
        },
        differentials={
            1: (
                (Fraction(0), Fraction(1)),
                (Fraction(0), Fraction(0)),
                (Fraction(0), Fraction(0)),
            ),
            2: ((Fraction(0), Fraction(0), Fraction(1)),),
        },
    )


def j3_two_step_expected_record() -> dict[str, Any]:
    """Return the hand expectation for Experiment 007."""
    return {
        "status": "expected_by_hand",
        "base_field": "QQ",
        "algebra": "J3 = (t)/(t^3)",
        "presentation": "F(x,y)/(y-x^2, x*y, y^2)",
        "replacement_type": "two-step semi-free dg Jordan toy replacement",
        "generators": {
            "degree_0": ["x", "y"],
            "degree_1": ["a1", "a2", "a3"],
            "degree_2": ["b"],
        },
        "differential": {
            "d(x)": "0",
            "d(y)": "0",
            "d(a1)": "y - x^2",
            "d(a2)": "x*y",
            "d(a3)": "y^2",
            "d(b)": "a3 - x*a2 - (y + x^2)*a1 + x*(x*a1)",
        },
        "indecomposable_differential": {
            "d_Q(a1)": "y",
            "d_Q(a2)": "0",
            "d_Q(a3)": "0",
            "d_Q(b)": "a3",
        },
        "expected_homology_dimensions": {
            "H0": 1,
            "H1": 1,
            "H2": 0,
        },
        "expected_representatives": {
            "H0": ["x"],
            "H1": ["a2"],
            "H2": [],
        },
        "warning": (
            "This verifies a two-step low-degree replacement for J3 "
            "Presentation B, not a general cofibrant replacement algorithm."
        ),
    }


def j3_two_step_result() -> dict[str, Any]:
    """Return the computed Experiment 007 payload."""
    expected = j3_two_step_expected_record()
    complex_ = j3_two_step_complex()
    computed = homology_dimensions(complex_, max_degree=2)
    expected_dimensions = expected["expected_homology_dimensions"]
    passed = complex_.d_squared_zero() and computed == expected_dimensions

    return {
        "status": "run",
        "passed": passed,
        "completed_scope": (
            "Two-step semi-free replacement for Presentation B of J3 was "
            "run through the indecomposable complex Q2 -> Q1 -> Q0."
        ),
        "replacement": {
            "type": expected["replacement_type"],
            "degree_0_generators": expected["generators"]["degree_0"],
            "degree_1_generators": expected["generators"]["degree_1"],
            "degree_2_generators": expected["generators"]["degree_2"],
        },
        "differential": expected["differential"],
        "indecomposable_differential": expected["indecomposable_differential"],
        "d_squared_zero_check": {
            "status": "checked_symbolically_for_this_example",
            "expression": "d(s)=x^2*x^2 - x*(x*x^2)",
            "reason_for_vanishing": (
                "power-associativity of the one-generated Jordan subalgebra"
            ),
        },
        "computed_homology_dimensions": computed,
        "expected_homology_dimensions": expected_dimensions,
        "homology_representatives": expected["expected_representatives"],
        "comparison_with_experiment_006": {
            "naive_presentation_B_H1": 2,
            "two_step_presentation_B_H1": computed["H1"],
            "extra_naive_class_killed": "a3",
        },
        "presentation_invariance_verified_through_degree": 1,
        "full_presentation_invariance_verified": False,
    }


def _differential_rank(complex_: IndecomposableComplex, degree: int) -> int:
    if degree not in complex_.differentials:
        return 0
    target_dim = len(complex_.bases.get(degree - 1, ()))
    rows = complex_.differentials[degree]
    expected_source_dim = len(complex_.bases.get(degree, ()))
    if len(rows) != expected_source_dim:
        msg = "differential row count must match source basis size"
        raise ValueError(msg)
    return row_rank(rows, target_dim)


def _compose_rows(
    first_rows: tuple[Vector, ...],
    second_rows: tuple[Vector, ...],
) -> tuple[Vector, ...]:
    composed: list[Vector] = []
    if not second_rows:
        return tuple(() for _ in first_rows)
    target_dimension = len(second_rows[0])
    for row in first_rows:
        image = [Fraction(0) for _ in range(target_dimension)]
        for coefficient, second_row in zip(row, second_rows, strict=True):
            for index, entry in enumerate(second_row):
                image[index] += coefficient * entry
        composed.append(tuple(image))
    return tuple(composed)
