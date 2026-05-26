from fractions import Fraction

from jordan_qh.chain_complex import FiniteChainComplex, analyze_homology
from jordan_qh.square_zero_two_gen import (
    C0_BASIS,
    C1_BASIS,
    PARTIAL_1_ROWS,
    exp009_bounded_chain_record,
    exp009_degree_one_complex,
)


def test_exp009_locks_nonunital_square_zero_degree_one_data() -> None:
    complex_ = exp009_degree_one_complex()

    assert complex_.bases[0] == C0_BASIS == ("x", "y")
    assert complex_.bases[1] == C1_BASIS == ("r_xx", "r_xy", "r_yy")
    assert complex_.differentials[1] == PARTIAL_1_ROWS
    assert complex_.differentials[1] == (
        (Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0)),
    )
    assert complex_.d_squared_zero()


def test_exp009_h0_is_two_dimensional_before_higher_backend() -> None:
    complex_ = exp009_degree_one_complex()
    homology = analyze_homology(complex_, max_degree=0)

    assert homology[0].kernel_basis == (
        (Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(1)),
    )
    assert homology[0].image_basis == ()
    assert homology[0].homology_representatives == homology[0].kernel_basis
    assert homology[0].homology_dimension == 2


def test_chain_complex_quotient_representatives_use_images() -> None:
    complex_ = FiniteChainComplex(
        bases={0: ("x", "y"), 1: ("a", "b"), 2: ("c",)},
        differentials={
            1: (
                (Fraction(1), Fraction(0)),
                (Fraction(0), Fraction(0)),
            ),
            2: ((Fraction(0), Fraction(1)),),
        },
    )

    homology = analyze_homology(complex_, max_degree=2)

    assert complex_.d_squared_zero()
    assert homology[0].homology_dimension == 1
    assert homology[1].kernel_basis == ((Fraction(0), Fraction(1)),)
    assert homology[1].image_basis == ((Fraction(0), Fraction(1)),)
    assert homology[1].homology_representatives == ()
    assert homology[1].homology_dimension == 0
    assert homology[2].homology_dimension == 0


def test_exp009_bounded_backend_records_degree_six_for_w6() -> None:
    record = exp009_bounded_chain_record(weight_bound=6)

    assert record["status"] == "run"
    assert record["passed"] is True
    assert record["checks"]["partial_1_through_partial_6_recorded"] is True
    assert record["checks"]["constructs_through_resolution_degree_6"] is True
    assert record["linear_algebra"]["H5_image_source"] == "im(partial_6)"
    assert "partial_6" in record["boundary_matrices_source_rows"]
    assert record["linear_algebra"]["homology_dimensions"] == {
        "H0": 2,
        "H1": 3,
        "H2": 8,
        "H3": 41,
        "H4": 0,
        "H5": 0,
    }
