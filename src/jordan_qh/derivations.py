"""Derivation checks for finite-dimensional scaffold examples."""

from collections.abc import Sequence

from jordan_qh.algebras import FiniteDimensionalAlgebra
from jordan_qh.tensors import Vector, add, apply_linear_map, sub

LinearMap = Sequence[Vector]


def derivation_defect(
    algebra: FiniteDimensionalAlgebra,
    linear_map: LinearMap,
    left: Vector,
    right: Vector,
) -> Vector:
    """Return `D(xy) - D(x)y - xD(y)` for an endomorphism `D`."""
    product = algebra.product
    d_left = apply_linear_map(linear_map, left)
    d_right = apply_linear_map(linear_map, right)
    d_product = apply_linear_map(linear_map, product(left, right))
    return sub(d_product, add(product(d_left, right), product(left, d_right)))


def is_derivation_on_basis(
    algebra: FiniteDimensionalAlgebra,
    linear_map: LinearMap,
) -> bool:
    """Check the derivation rule on basis vectors."""
    basis = algebra.basis_vectors()
    return all(
        derivation_defect(algebra, linear_map, x, y) == (0,) * algebra.dimension
        for x in basis
        for y in basis
    )
