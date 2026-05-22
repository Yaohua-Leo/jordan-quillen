"""Draft objects for universal Jordan differentials."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UniversalDifferentialsDraft:
    """Metadata for a not-yet-implemented universal differential object."""

    algebra_name: str
    base_name: str = "k"
    status: str = "definition pending"

    def represents(self) -> str:
        """Return the intended representing property."""
        return f"Hom_J(Omega_{{{self.algebra_name}/{self.base_name}}}, M) ~= Der(M)"
