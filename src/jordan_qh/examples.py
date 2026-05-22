"""Small examples used by tests and future experiments."""

from jordan_qh.algebras import JordanAlgebra
from jordan_qh.modules import SquareZeroExtensionSpec


def zero_multiplication_algebra(dimension: int) -> JordanAlgebra:
    """Return the zero-multiplication Jordan algebra of a fixed dimension."""
    return JordanAlgebra.zero_multiplication(dimension)


def one_dimensional_unital_algebra() -> JordanAlgebra:
    """Return `k e` with `e * e = e`."""
    return JordanAlgebra.one_dimensional_unital()


def square_zero_extension_shape(
    base_dimension: int,
    module_dimension: int,
) -> SquareZeroExtensionSpec:
    """Record the dimension data for a planned square-zero extension."""
    return SquareZeroExtensionSpec(base_dimension, module_dimension)
