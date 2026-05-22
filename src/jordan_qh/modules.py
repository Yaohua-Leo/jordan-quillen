"""Placeholders for Jordan module and square-zero extension data."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SquareZeroExtensionSpec:
    """A recorded square-zero extension shape, not yet a full implementation."""

    base_dimension: int
    module_dimension: int
    status: str = "not implemented"

    @property
    def total_dimension(self) -> int:
        """Return the vector-space dimension of `J plus M`."""
        return self.base_dimension + self.module_dimension
