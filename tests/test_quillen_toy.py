from fractions import Fraction

from jordan_qh.quillen_toy import (
    OneGeneratorRelation,
    benchmark_examples,
    free_one_generator_homology_dimensions,
    linear_part_coefficient,
    one_relation_toy_homology_dimensions,
    one_step_relation_toy_homology_dimensions,
)


def test_linear_part_coefficient_reads_degree_one_term() -> None:
    assert (
        linear_part_coefficient(
            OneGeneratorRelation(
                name="x2_minus_x",
                relation_coefficients={2: Fraction(1), 1: Fraction(-1)},
            )
        )
        == Fraction(-1)
    )
    assert (
        linear_part_coefficient(
            OneGeneratorRelation(name="x2", relation_coefficients={2: Fraction(1)})
        )
        == 0
    )
    assert (
        linear_part_coefficient(
            OneGeneratorRelation(name="x3", relation_coefficients={3: Fraction(1)})
        )
        == 0
    )
    assert (
        linear_part_coefficient(
            OneGeneratorRelation(name="x4", relation_coefficients={4: Fraction(1)})
        )
        == 0
    )


def test_one_generator_toy_homology_dimensions() -> None:
    assert free_one_generator_homology_dimensions() == {"H0": 1, "H1": 0}
    assert one_relation_toy_homology_dimensions(
        OneGeneratorRelation(
            name="x2_minus_x",
            relation_coefficients={2: Fraction(1), 1: Fraction(-1)},
        )
    ) == {"H0": 0, "H1": 0}
    assert one_relation_toy_homology_dimensions(
        OneGeneratorRelation(name="x2", relation_coefficients={2: Fraction(1)})
    ) == {"H0": 1, "H1": 1}
    assert one_relation_toy_homology_dimensions(
        OneGeneratorRelation(name="x3", relation_coefficients={3: Fraction(1)})
    ) == {"H0": 1, "H1": 1}
    assert one_relation_toy_homology_dimensions(
        OneGeneratorRelation(name="x4", relation_coefficients={4: Fraction(1)})
    ) == {"H0": 1, "H1": 1}


def test_naive_two_generator_relation_toy_records_extra_h1_class() -> None:
    assert one_step_relation_toy_homology_dimensions(
        generator_count=2,
        relation_linear_parts=(
            (Fraction(0), Fraction(1)),
            (Fraction(0), Fraction(0)),
            (Fraction(0), Fraction(0)),
        ),
    ) == {"H0": 1, "H1": 2}


def test_benchmark_examples_match_expected_dimensions() -> None:
    dimensions = {
        entry["name"]: entry["homology_dimensions"]
        for entry in benchmark_examples()
    }

    assert dimensions == {
        "free_one_generator": {"H0": 1, "H1": 0},
        "one_dimensional_idempotent": {"H0": 0, "H1": 0},
        "one_dimensional_square_zero": {"H0": 1, "H1": 1},
        "truncated_x3": {"H0": 1, "H1": 1},
        "truncated_x4": {"H0": 1, "H1": 1},
    }
