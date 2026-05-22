"""Field helpers for exact small examples."""

from fractions import Fraction

ScalarLike = int | Fraction


def scalar(value: ScalarLike) -> Fraction:
    """Normalize a scalar to `Fraction` for exact arithmetic."""
    if isinstance(value, Fraction):
        return value
    return Fraction(value)
