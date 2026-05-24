from fractions import Fraction

from jordan_qh.semi_free_toy import (
    homology_dimensions,
    j3_two_step_complex,
    j3_two_step_result,
)


def test_j3_two_step_complex_kills_redundant_a3_class() -> None:
    complex_ = j3_two_step_complex()

    assert complex_.bases == {
        0: ("x", "y"),
        1: ("a1", "a2", "a3"),
        2: ("b",),
    }
    assert complex_.differentials[1] == (
        (Fraction(0), Fraction(1)),
        (Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0)),
    )
    assert complex_.differentials[2] == (
        (Fraction(0), Fraction(0), Fraction(1)),
    )
    assert complex_.d_squared_zero()
    assert homology_dimensions(complex_, max_degree=2) == {
        "H0": 1,
        "H1": 1,
        "H2": 0,
    }


def test_j3_two_step_result_records_limited_presentation_invariance() -> None:
    result = j3_two_step_result()

    assert result["passed"] is True
    assert result["computed_homology_dimensions"] == {
        "H0": 1,
        "H1": 1,
        "H2": 0,
    }
    assert result["comparison_with_experiment_006"] == {
        "naive_presentation_B_H1": 2,
        "two_step_presentation_B_H1": 1,
        "extra_naive_class_killed": "a3",
    }
    assert result["presentation_invariance_verified_through_degree"] == 1
    assert result["full_presentation_invariance_verified"] is False
