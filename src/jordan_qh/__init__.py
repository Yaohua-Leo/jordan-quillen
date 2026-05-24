"""Lightweight scaffold for Jordan Quillen homology experiments."""

from jordan_qh.algebras import FiniteDimensionalAlgebra, JordanAlgebra
from jordan_qh.examples import (
    one_dimensional_square_zero_algebra,
    one_dimensional_unital_algebra,
    zero_multiplication_algebra,
)
from jordan_qh.indecomposables import indecomposables_dimension

__all__ = [
    "FiniteDimensionalAlgebra",
    "JordanAlgebra",
    "indecomposables_dimension",
    "one_dimensional_square_zero_algebra",
    "one_dimensional_unital_algebra",
    "zero_multiplication_algebra",
]

__version__ = "0.1.0"
