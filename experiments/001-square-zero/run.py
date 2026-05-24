"""Run exact one-dimensional split square-zero sanity checks."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jordan_qh import examples  # noqa: E402
from jordan_qh.identities import jordan_identity_holds  # noqa: E402
from jordan_qh.tensors import Vector  # noqa: E402

TESTED_LAMBDAS = (
    Fraction(-2),
    Fraction(-1),
    Fraction(-1, 2),
    Fraction(0),
    Fraction(1, 2),
    Fraction(1),
    Fraction(2),
)
GRID_COEFFICIENTS = (Fraction(-1), Fraction(0), Fraction(1))


def format_fraction(value: Fraction) -> str:
    """Format a rational number deterministically for JSON output."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def finite_grid() -> tuple[Vector, ...]:
    """Return the finite grid used by this experiment."""
    return examples.finite_vector_grid(2, GRID_COEFFICIENTS)


def jordan_lambdas(base_square: Fraction) -> tuple[Fraction, ...]:
    """Return tested actions for which the extension passes the grid check."""
    grid = finite_grid()
    return tuple(
        action
        for action in TESTED_LAMBDAS
        if jordan_identity_holds(
            grid,
            examples.one_dimensional_scalar_action_extension(
                base_square=base_square,
                action=action,
            ).product,
        )
    )


def base_unit_is_extension_unit(base_square: Fraction, action: Fraction) -> bool:
    """Check whether `(e, 0)` acts as a two-sided unit on basis vectors."""
    algebra = examples.one_dimensional_scalar_action_extension(base_square, action)
    unit: Vector = (Fraction(1), Fraction(0))
    return all(
        algebra.product(unit, basis_vector) == basis_vector
        and algebra.product(basis_vector, unit) == basis_vector
        for basis_vector in algebra.basis_vectors()
    )


def build_results() -> dict[str, Any]:
    """Build the deterministic result object for this experiment."""
    lambda_two_algebra = examples.one_dimensional_scalar_action_extension(
        base_square=Fraction(1),
        action=Fraction(2),
    )
    lambda_two_basis_only = lambda_two_algebra.satisfies_jordan_identity_on_basis()
    lambda_two_grid = jordan_identity_holds(finite_grid(), lambda_two_algebra.product)
    unital_extension_lambdas = tuple(
        action
        for action in TESTED_LAMBDAS
        if base_unit_is_extension_unit(Fraction(1), action)
    )
    return {
        "experiment": "001-square-zero",
        "status": "run",
        "command": "python experiments/001-square-zero/run.py",
        "checker": {
            "type": "finite_grid_jordan_identity",
            "grid_coefficients": [
                format_fraction(value) for value in GRID_COEFFICIENTS
            ],
            "grid_size": len(finite_grid()),
            "basis_only_warning": (
                "Basis-vector checks are smoke tests only and can miss bad "
                "scalar actions."
            ),
            "basis_only_false_positive_example": {
                "base_square": "1",
                "lambda": "2",
                "basis_only_passes": lambda_two_basis_only,
                "finite_grid_passes": lambda_two_grid,
            },
        },
        "tested_lambdas": [format_fraction(value) for value in TESTED_LAMBDAS],
        "unital_base_e2_equals_e": {
            "base_square": "1",
            "jordan_lambdas": [
                format_fraction(value) for value in jordan_lambdas(Fraction(1))
            ],
            "unital_extension_lambdas": [
                format_fraction(value) for value in unital_extension_lambdas
            ],
            "interpretation": (
                "In the nonunital Jordan algebra category, the tested scalar "
                "actions that pass are lambda = 0, 1/2, 1. Requiring (e, 0) "
                "to remain a unit selects lambda = 1."
            ),
        },
        "zero_base_e2_equals_0": {
            "base_square": "0",
            "jordan_lambdas": [
                format_fraction(value) for value in jordan_lambdas(Fraction(0))
            ],
            "interpretation": (
                "For the one-dimensional zero-multiplication base, the tested "
                "scalar action is forced to lambda = 0."
            ),
        },
        "claim_boundary": (
            "These toy checks support the split square-zero workflow for "
            "CLAIM-0003, but they do not prove the Beck module equivalence."
        ),
    }


def main() -> None:
    results = build_results()
    results_path = Path(__file__).with_name("results.json")
    text = json.dumps(results, indent=2, sort_keys=False)
    results_path.write_text(f"{text}\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
