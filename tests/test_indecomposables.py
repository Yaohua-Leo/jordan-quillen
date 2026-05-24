from jordan_qh import JordanAlgebra, examples
from jordan_qh.indecomposables import (
    indecomposables_dimension,
    product_span_rank,
)


def test_zero_multiplication_algebra_is_all_indecomposable() -> None:
    algebra = examples.zero_multiplication_algebra(4)

    assert product_span_rank(algebra) == 0
    assert indecomposables_dimension(algebra) == 4


def test_one_dimensional_idempotent_has_no_indecomposables() -> None:
    algebra = examples.one_dimensional_unital_algebra()

    assert product_span_rank(algebra) == 1
    assert indecomposables_dimension(algebra) == 0


def test_one_dimensional_square_zero_has_one_indecomposable() -> None:
    algebra = JordanAlgebra(basis=("x",), structure_constants={})

    assert product_span_rank(algebra) == 0
    assert indecomposables_dimension(algebra) == 1
