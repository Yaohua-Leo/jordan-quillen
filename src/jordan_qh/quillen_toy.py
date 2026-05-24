"""One-generator toy model for derived indecomposables benchmarks."""

from dataclasses import dataclass
from fractions import Fraction

from jordan_qh.linear_algebra import row_rank


@dataclass(frozen=True)
class OneGeneratorRelation:
    """A relation `r(x) = sum_m c_m x^m` in one generator."""

    name: str
    relation_coefficients: dict[int, Fraction]


def linear_part_coefficient(relation: OneGeneratorRelation) -> Fraction:
    """Return the coefficient of `x` in `r(x)`."""
    return Fraction(relation.relation_coefficients.get(1, Fraction(0)))


def one_relation_toy_homology_dimensions(
    relation: OneGeneratorRelation,
) -> dict[str, int]:
    """Return homology dimensions of the two-term complex `Q_1 -> Q_0`."""
    return one_step_relation_toy_homology_dimensions(
        generator_count=1,
        relation_linear_parts=((linear_part_coefficient(relation),),),
    )


def free_one_generator_homology_dimensions() -> dict[str, int]:
    """Return homology dimensions for `F(x)`."""
    return one_step_relation_toy_homology_dimensions(
        generator_count=1,
        relation_linear_parts=(),
    )


def one_step_relation_toy_homology_dimensions(
    generator_count: int,
    relation_linear_parts: tuple[tuple[Fraction, ...], ...],
) -> dict[str, int]:
    """Return dimensions for the naive one-step relation complex.

    The complex is `k^relations -> k^generators`, with differential given by
    the linear parts of the relations after applying indecomposables.
    """
    if generator_count < 0:
        msg = "generator_count must be nonnegative"
        raise ValueError(msg)
    normalized_rows = tuple(
        tuple(Fraction(entry) for entry in row) for row in relation_linear_parts
    )
    for row in normalized_rows:
        if len(row) != generator_count:
            msg = "each relation linear part must match generator_count"
            raise ValueError(msg)

    rank = row_rank(normalized_rows, generator_count)
    return {
        "H0": generator_count - rank,
        "H1": len(normalized_rows) - rank,
    }


def benchmark_examples() -> list[dict]:
    """Return the planned one-generator benchmark examples."""
    examples: list[dict] = [
        {
            "name": "free_one_generator",
            "presentation": "F(x)",
            "relation_coefficients": None,
            "linear_part_coefficient": None,
            "homology_dimensions": free_one_generator_homology_dimensions(),
        }
    ]
    for relation, presentation in [
        (
            OneGeneratorRelation(
                name="one_dimensional_idempotent",
                relation_coefficients={2: Fraction(1), 1: Fraction(-1)},
            ),
            "F(x)/(x^2 - x)",
        ),
        (
            OneGeneratorRelation(
                name="one_dimensional_square_zero",
                relation_coefficients={2: Fraction(1)},
            ),
            "F(x)/(x^2)",
        ),
        (
            OneGeneratorRelation(
                name="truncated_x3",
                relation_coefficients={3: Fraction(1)},
            ),
            "F(x)/(x^3)",
        ),
        (
            OneGeneratorRelation(
                name="truncated_x4",
                relation_coefficients={4: Fraction(1)},
            ),
            "F(x)/(x^4)",
        ),
    ]:
        examples.append(_benchmark_record(relation, presentation))
    return examples


def _benchmark_record(
    relation: OneGeneratorRelation,
    presentation: str,
) -> dict:
    linear_coefficient = linear_part_coefficient(relation)
    return {
        "name": relation.name,
        "presentation": presentation,
        "relation_coefficients": {
            str(degree): str(coefficient)
            for degree, coefficient in sorted(relation.relation_coefficients.items())
        },
        "linear_part_coefficient": str(linear_coefficient),
        "homology_dimensions": one_relation_toy_homology_dimensions(relation),
    }
