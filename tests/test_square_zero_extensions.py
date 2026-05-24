from fractions import Fraction

from jordan_qh import examples
from jordan_qh.identities import jordan_identity_holds
from jordan_qh.tensors import Vector

TESTED_LAMBDAS = (
    Fraction(-2),
    Fraction(-1),
    Fraction(-1, 2),
    Fraction(0),
    Fraction(1, 2),
    Fraction(1),
    Fraction(2),
)


def _grid() -> tuple[Vector, ...]:
    return examples.finite_vector_grid(2, (Fraction(-1), Fraction(0), Fraction(1)))


def _jordan_lambdas(base_square: Fraction) -> tuple[Fraction, ...]:
    return tuple(
        action
        for action in TESTED_LAMBDAS
        if jordan_identity_holds(
            _grid(),
            examples.one_dimensional_scalar_action_extension(
                base_square=base_square,
                action=action,
            ).product,
        )
    )


def _base_unit_is_extension_unit(algebra: examples.JordanAlgebra) -> bool:
    unit: Vector = (Fraction(1), Fraction(0))
    return all(
        algebra.product(unit, basis_vector) == basis_vector
        and algebra.product(basis_vector, unit) == basis_vector
        for basis_vector in algebra.basis_vectors()
    )


def test_unital_base_scalar_actions_are_classified_on_finite_grid() -> None:
    assert _jordan_lambdas(Fraction(1)) == (
        Fraction(0),
        Fraction(1, 2),
        Fraction(1),
    )


def test_zero_base_scalar_actions_are_classified_on_finite_grid() -> None:
    assert _jordan_lambdas(Fraction(0)) == (Fraction(0),)


def test_unital_extension_condition_selects_lambda_one() -> None:
    unital_actions = tuple(
        action
        for action in TESTED_LAMBDAS
        if _base_unit_is_extension_unit(
            examples.one_dimensional_scalar_action_extension(
                base_square=Fraction(1),
                action=action,
            )
        )
    )

    assert unital_actions == (Fraction(1),)


def test_basis_only_check_can_miss_bad_scalar_actions() -> None:
    algebra = examples.one_dimensional_scalar_action_extension(
        base_square=Fraction(1),
        action=Fraction(2),
    )

    assert algebra.satisfies_jordan_identity_on_basis()
    assert not jordan_identity_holds(_grid(), algebra.product)
