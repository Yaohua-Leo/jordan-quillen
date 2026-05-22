from jordan_qh.derivations import is_derivation_on_basis
from jordan_qh.examples import (
    one_dimensional_unital_algebra,
    zero_multiplication_algebra,
)
from jordan_qh.tensors import identity_linear_map, zero_linear_map


def test_zero_map_is_derivation() -> None:
    algebra = one_dimensional_unital_algebra()

    assert is_derivation_on_basis(algebra, zero_linear_map(algebra.dimension))


def test_identity_map_is_not_unital_one_dimensional_derivation() -> None:
    algebra = one_dimensional_unital_algebra()

    assert not is_derivation_on_basis(algebra, identity_linear_map(algebra.dimension))


def test_every_checked_endomorphism_of_zero_multiplication_is_derivation() -> None:
    algebra = zero_multiplication_algebra(2)

    assert is_derivation_on_basis(algebra, identity_linear_map(algebra.dimension))
