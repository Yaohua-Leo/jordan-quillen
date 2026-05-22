"""Low-degree expectation records for the research scaffold."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LowDegreeExpectation:
    """A textual low-degree interpretation to be proved later."""

    degree: int
    object_name: str
    expected_interpretation: str
    status: str = "conjectural"
