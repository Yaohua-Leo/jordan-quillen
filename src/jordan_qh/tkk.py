"""TKK comparison placeholders."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TKKComparisonTarget:
    """A small example marked for intrinsic-versus-TKK comparison."""

    jordan_example: str
    expected_use: str
    status: str = "not run yet"
