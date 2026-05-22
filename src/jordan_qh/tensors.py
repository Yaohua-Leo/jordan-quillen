"""Tiny exact vector utilities for finite-dimensional examples."""

from collections.abc import Iterable, Sequence
from fractions import Fraction

from jordan_qh.fields import ScalarLike, scalar

Vector = tuple[Fraction, ...]


def vector(values: Iterable[ScalarLike]) -> Vector:
    """Create an exact vector."""
    return tuple(scalar(value) for value in values)


def zero(dimension: int) -> Vector:
    """Return the zero vector of a fixed dimension."""
    if dimension < 0:
        msg = "dimension must be nonnegative"
        raise ValueError(msg)
    return tuple(Fraction(0) for _ in range(dimension))


def basis_vector(dimension: int, index: int) -> Vector:
    """Return the `index`th standard basis vector."""
    if index < 0 or index >= dimension:
        msg = "basis index out of range"
        raise IndexError(msg)
    return tuple(Fraction(1) if i == index else Fraction(0) for i in range(dimension))


def add(left: Vector, right: Vector) -> Vector:
    """Add two vectors."""
    _require_same_dimension(left, right)
    return tuple(a + b for a, b in zip(left, right, strict=True))


def neg(value: Vector) -> Vector:
    """Negate a vector."""
    return tuple(-entry for entry in value)


def sub(left: Vector, right: Vector) -> Vector:
    """Subtract two vectors."""
    return add(left, neg(right))


def scale(coefficient: ScalarLike, value: Vector) -> Vector:
    """Scale a vector."""
    c = scalar(coefficient)
    return tuple(c * entry for entry in value)


def linear_combination(
    terms: Iterable[tuple[ScalarLike, Vector]],
    dimension: int,
) -> Vector:
    """Compute a finite linear combination."""
    total = zero(dimension)
    for coefficient, value in terms:
        total = add(total, scale(coefficient, value))
    return total


def apply_linear_map(columns: Sequence[Vector], value: Vector) -> Vector:
    """Apply a linear map encoded by its basis-image columns."""
    if len(columns) != len(value):
        msg = "number of columns must match vector dimension"
        raise ValueError(msg)
    if not columns:
        return ()
    dimension = len(columns[0])
    return linear_combination(zip(value, columns, strict=True), dimension)


def zero_linear_map(dimension: int) -> tuple[Vector, ...]:
    """Return the zero endomorphism encoded by columns."""
    return tuple(zero(dimension) for _ in range(dimension))


def identity_linear_map(dimension: int) -> tuple[Vector, ...]:
    """Return the identity endomorphism encoded by columns."""
    return tuple(basis_vector(dimension, i) for i in range(dimension))


def _require_same_dimension(left: Vector, right: Vector) -> None:
    if len(left) != len(right):
        msg = "vector dimensions do not match"
        raise ValueError(msg)
