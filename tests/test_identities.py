from jordan_qh import examples
from jordan_qh.identities import is_commutative, jordan_identity_holds


def test_zero_multiplication_is_jordan_on_basis() -> None:
    algebra = examples.zero_multiplication_algebra(3)

    assert is_commutative(algebra.basis_vectors(), algebra.product)
    assert jordan_identity_holds(algebra.basis_vectors(), algebra.product)


def test_one_dimensional_unital_is_jordan_on_basis() -> None:
    algebra = examples.one_dimensional_unital_algebra()

    assert algebra.is_commutative_on_basis()
    assert algebra.satisfies_jordan_identity_on_basis()
