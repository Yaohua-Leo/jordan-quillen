from fractions import Fraction

from jordan_qh.examples import (
    one_dimensional_unital_algebra,
    zero_multiplication_algebra,
)
from jordan_qh.tensors import basis_vector


def test_one_dimensional_product() -> None:
    algebra = one_dimensional_unital_algebra()
    e = basis_vector(1, 0)

    assert algebra.product(e, e) == (Fraction(1),)


def test_zero_multiplication_product() -> None:
    algebra = zero_multiplication_algebra(2)
    e0 = basis_vector(2, 0)
    e1 = basis_vector(2, 1)

    assert algebra.product(e0, e1) == (Fraction(0), Fraction(0))
