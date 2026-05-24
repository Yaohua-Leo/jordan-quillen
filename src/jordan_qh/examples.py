"""Small examples used by tests and future experiments."""

from collections.abc import Iterable
from itertools import product

from jordan_qh.algebras import JordanAlgebra
from jordan_qh.fields import ScalarLike, scalar
from jordan_qh.modules import SquareZeroExtensionSpec
from jordan_qh.tensors import Vector, vector


def zero_multiplication_algebra(dimension: int) -> JordanAlgebra:
    """Return the zero-multiplication Jordan algebra of a fixed dimension."""
    return JordanAlgebra.zero_multiplication(dimension)


def one_dimensional_unital_algebra() -> JordanAlgebra:
    """Return `k e` with `e * e = e`."""
    return JordanAlgebra.one_dimensional_unital()


def one_dimensional_square_zero_algebra() -> JordanAlgebra:
    """Return `k x` with `x * x = 0`."""
    return JordanAlgebra(basis=("x",), structure_constants={})


def square_zero_extension_shape(
    base_dimension: int,
    module_dimension: int,
) -> SquareZeroExtensionSpec:
    """Record the dimension data for a planned square-zero extension."""
    return SquareZeroExtensionSpec(base_dimension, module_dimension)


def one_dimensional_scalar_action_extension(
    base_square: ScalarLike,
    action: ScalarLike,
) -> JordanAlgebra:
    """Return `ke plus km` with `e^2 = base_square e` and `e m = action m`."""
    square = scalar(base_square)
    action_scalar = scalar(action)
    return JordanAlgebra(
        basis=("e", "m"),
        structure_constants={
            (0, 0): (square, 0),
            (0, 1): (0, action_scalar),
            (1, 0): (0, action_scalar),
        },
    )


def finite_vector_grid(
    dimension: int,
    coefficients: Iterable[ScalarLike],
) -> tuple[Vector, ...]:
    """Return all exact vectors with entries drawn from a finite coefficient set."""
    if dimension < 0:
        msg = "dimension must be nonnegative"
        raise ValueError(msg)
    exact_coefficients = tuple(scalar(coefficient) for coefficient in coefficients)
    return tuple(
        vector(entries)
        for entries in product(exact_coefficients, repeat=dimension)
    )
