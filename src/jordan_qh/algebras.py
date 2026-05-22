"""Finite-dimensional algebra data structures for small examples."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from jordan_qh import identities
from jordan_qh.fields import ScalarLike
from jordan_qh.tensors import Vector, add, basis_vector, scale, vector, zero

StructureConstants = Mapping[tuple[int, int], Sequence[ScalarLike]]


@dataclass(frozen=True)
class FiniteDimensionalAlgebra:
    """A finite-dimensional algebra encoded by structure constants."""

    basis: tuple[str, ...]
    structure_constants: StructureConstants
    _table: dict[tuple[int, int], Vector] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        dimension = len(self.basis)
        table: dict[tuple[int, int], Vector] = {}
        for key, value in self.structure_constants.items():
            i, j = key
            if i < 0 or j < 0 or i >= dimension or j >= dimension:
                msg = f"structure constant index {key} out of range"
                raise IndexError(msg)
            entry = vector(value)
            if len(entry) != dimension:
                msg = "structure constant vector has wrong dimension"
                raise ValueError(msg)
            table[(i, j)] = entry
        object.__setattr__(self, "_table", table)

    @property
    def dimension(self) -> int:
        """Return the vector-space dimension."""
        return len(self.basis)

    def basis_vectors(self) -> tuple[Vector, ...]:
        """Return the standard basis vectors."""
        return tuple(basis_vector(self.dimension, i) for i in range(self.dimension))

    def product(self, left: Vector, right: Vector) -> Vector:
        """Multiply two vectors bilinearly from the structure constants."""
        if len(left) != self.dimension or len(right) != self.dimension:
            msg = "vector dimension does not match algebra dimension"
            raise ValueError(msg)
        result = zero(self.dimension)
        for i, left_coefficient in enumerate(left):
            if left_coefficient == 0:
                continue
            for j, right_coefficient in enumerate(right):
                if right_coefficient == 0:
                    continue
                basis_product = self._table.get((i, j), zero(self.dimension))
                result = add(
                    result,
                    scale(left_coefficient * right_coefficient, basis_product),
                )
        return result

    def is_commutative_on_basis(self) -> bool:
        """Check commutativity on basis vectors."""
        return identities.is_commutative(self.basis_vectors(), self.product)

    def satisfies_jordan_identity_on_basis(self) -> bool:
        """Check the Jordan identity on basis vectors."""
        return identities.jordan_identity_holds(self.basis_vectors(), self.product)


class JordanAlgebra(FiniteDimensionalAlgebra):
    """Finite-dimensional algebra intended to satisfy the Jordan identity."""

    @classmethod
    def zero_multiplication(cls, dimension: int) -> "JordanAlgebra":
        """Create the zero-multiplication Jordan algebra."""
        basis = tuple(f"e{i}" for i in range(dimension))
        return cls(basis=basis, structure_constants={})

    @classmethod
    def one_dimensional_unital(cls) -> "JordanAlgebra":
        """Create the algebra `k e` with `e * e = e`."""
        return cls(basis=("e",), structure_constants={(0, 0): (1,)})
