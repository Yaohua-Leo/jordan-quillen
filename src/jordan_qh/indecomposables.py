"""Indecomposables for finite-dimensional Jordan algebra examples."""

from jordan_qh.algebras import FiniteDimensionalAlgebra
from jordan_qh.linear_algebra import row_rank
from jordan_qh.tensors import Vector


def product_span_generators(algebra: FiniteDimensionalAlgebra) -> tuple[Vector, ...]:
    """Return all basis products spanning `J^2`."""
    basis = algebra.basis_vectors()
    return tuple(algebra.product(left, right) for left in basis for right in basis)


def product_span_rank(algebra: FiniteDimensionalAlgebra) -> int:
    """Return `dim J^2`."""
    return row_rank(product_span_generators(algebra), algebra.dimension)


def indecomposables_dimension(algebra: FiniteDimensionalAlgebra) -> int:
    """Return `dim Q(J) = dim J/J^2`."""
    return algebra.dimension - product_span_rank(algebra)
