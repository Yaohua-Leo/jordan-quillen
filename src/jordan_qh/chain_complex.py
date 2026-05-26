"""Exact finite chain-complex helpers over the rationals."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from jordan_qh.linear_algebra import row_rank

Vector = tuple[Fraction, ...]
MatrixRows = tuple[Vector, ...]


@dataclass(frozen=True)
class FiniteChainComplex:
    """A finite chain complex with source-row boundary matrices.

    The matrix for ``d_n: C_n -> C_{n-1}`` has one row for each source basis
    vector in ``C_n`` and target coordinates in the basis of ``C_{n-1}``.
    """

    bases: dict[int, tuple[str, ...]]
    differentials: dict[int, MatrixRows]

    def validate(self) -> None:
        """Validate that boundary matrices match the recorded bases."""
        for degree, rows in self.differentials.items():
            source_dimension = len(self.bases.get(degree, ()))
            target_dimension = len(self.bases.get(degree - 1, ()))
            if len(rows) != source_dimension:
                msg = (
                    f"d_{degree} row count {len(rows)} does not match "
                    f"dim C_{degree} = {source_dimension}"
                )
                raise ValueError(msg)
            for row in rows:
                if len(row) != target_dimension:
                    msg = (
                        f"d_{degree} row length {len(row)} does not match "
                        f"dim C_{degree - 1} = {target_dimension}"
                    )
                    raise ValueError(msg)

    def d_squared_zero(self) -> bool:
        """Return whether adjacent differentials compose to zero."""
        self.validate()
        for degree in sorted(self.differentials):
            if degree - 1 not in self.differentials:
                continue
            for row in compose_rows(
                self.differentials[degree],
                self.differentials[degree - 1],
            ):
                if any(entry != 0 for entry in row):
                    return False
        return True


@dataclass(frozen=True)
class HomologyDegree:
    """Linear algebra data for one homological degree."""

    degree: int
    chain_basis: tuple[str, ...]
    boundary_rank: int
    kernel_basis: MatrixRows
    image_basis: MatrixRows
    homology_representatives: MatrixRows
    homology_dimension: int


def analyze_homology(
    complex_: FiniteChainComplex,
    *,
    max_degree: int,
) -> dict[int, HomologyDegree]:
    """Compute exact kernel, image, and homology representatives."""
    complex_.validate()
    analyses: dict[int, HomologyDegree] = {}
    for degree in range(max_degree + 1):
        chain_dimension = len(complex_.bases.get(degree, ()))
        boundary = boundary_rows(complex_, degree)
        next_boundary = boundary_rows(complex_, degree + 1)
        boundary_rank = row_rank(boundary, len(complex_.bases.get(degree - 1, ())))
        kernel = kernel_basis(
            boundary,
            source_dimension=chain_dimension,
            target_dimension=len(complex_.bases.get(degree - 1, ())),
        )
        image = row_space_basis(next_boundary, chain_dimension)
        representatives = quotient_representatives(
            kernel,
            image,
            ambient_dimension=chain_dimension,
        )
        analyses[degree] = HomologyDegree(
            degree=degree,
            chain_basis=complex_.bases.get(degree, ()),
            boundary_rank=boundary_rank,
            kernel_basis=kernel,
            image_basis=image,
            homology_representatives=representatives,
            homology_dimension=len(representatives),
        )
    return analyses


def boundary_rows(complex_: FiniteChainComplex, degree: int) -> MatrixRows:
    """Return the boundary matrix for ``d_degree`` or a zero-size matrix."""
    if degree in complex_.differentials:
        return complex_.differentials[degree]
    return tuple(
        tuple(Fraction(0) for _ in complex_.bases.get(degree - 1, ()))
        for _ in complex_.bases.get(degree, ())
    )


def kernel_basis(
    rows: MatrixRows,
    *,
    source_dimension: int,
    target_dimension: int,
) -> MatrixRows:
    """Return a basis for the kernel of a source-row map."""
    _validate_rows(rows, source_dimension, target_dimension)
    if source_dimension == 0:
        return ()

    equations = [
        [rows[source_index][target_index] for source_index in range(source_dimension)]
        for target_index in range(target_dimension)
    ]
    rref_rows, pivot_columns = _rref(equations, source_dimension)
    pivot_set = set(pivot_columns)
    free_columns = [
        column for column in range(source_dimension) if column not in pivot_set
    ]
    basis: list[Vector] = []
    for free_column in free_columns:
        vector = [Fraction(0) for _ in range(source_dimension)]
        vector[free_column] = Fraction(1)
        for row_index, pivot_column in enumerate(pivot_columns):
            vector[pivot_column] = -rref_rows[row_index][free_column]
        basis.append(tuple(vector))
    return tuple(basis)


def row_space_basis(rows: MatrixRows, dimension: int) -> MatrixRows:
    """Return a reduced basis for the row span."""
    normalized = _normalize_rows(rows, dimension)
    reduced, _ = _rref(normalized, dimension)
    return tuple(tuple(row) for row in reduced)


def quotient_representatives(
    subspace_basis: MatrixRows,
    quotient_by_basis: MatrixRows,
    *,
    ambient_dimension: int,
) -> MatrixRows:
    """Choose representatives for span(subspace_basis) / span(quotient_by_basis)."""
    span = list(row_space_basis(quotient_by_basis, ambient_dimension))
    current_rank = row_rank(span, ambient_dimension)
    representatives: list[Vector] = []
    for vector in subspace_basis:
        trial = [*span, vector]
        trial_rank = row_rank(trial, ambient_dimension)
        if trial_rank <= current_rank:
            continue
        representatives.append(vector)
        span.append(vector)
        current_rank = trial_rank
    return tuple(representatives)


def compose_rows(first_rows: MatrixRows, second_rows: MatrixRows) -> MatrixRows:
    """Compose source-row maps ``first`` then ``second``."""
    if not first_rows:
        return ()
    if not second_rows:
        return tuple(() for _ in first_rows)
    target_dimension = len(second_rows[0])
    composed: list[Vector] = []
    for row in first_rows:
        image = [Fraction(0) for _ in range(target_dimension)]
        for coefficient, second_row in zip(row, second_rows, strict=True):
            for index, entry in enumerate(second_row):
                image[index] += coefficient * entry
        composed.append(tuple(image))
    return tuple(composed)


def _validate_rows(
    rows: MatrixRows,
    source_dimension: int,
    target_dimension: int,
) -> None:
    if len(rows) != source_dimension:
        msg = "row count must match source dimension"
        raise ValueError(msg)
    for row in rows:
        if len(row) != target_dimension:
            msg = "row length must match target dimension"
            raise ValueError(msg)


def _normalize_rows(
    rows: MatrixRows | list[list[Fraction]],
    dimension: int,
) -> list[list[Fraction]]:
    matrix: list[list[Fraction]] = []
    for row in rows:
        if len(row) != dimension:
            msg = "each row length must match dimension"
            raise ValueError(msg)
        matrix.append([Fraction(entry) for entry in row])
    return matrix


def _rref(
    rows: MatrixRows | list[list[Fraction]],
    dimension: int,
) -> tuple[list[list[Fraction]], list[int]]:
    matrix = _normalize_rows(rows, dimension)
    pivot_columns: list[int] = []
    rank = 0
    for column in range(dimension):
        pivot_row = _find_pivot_row(matrix, rank, column)
        if pivot_row is None:
            continue
        matrix[rank], matrix[pivot_row] = matrix[pivot_row], matrix[rank]
        pivot = matrix[rank][column]
        matrix[rank] = [entry / pivot for entry in matrix[rank]]
        for row_index, row in enumerate(matrix):
            if row_index == rank:
                continue
            coefficient = row[column]
            if coefficient == 0:
                continue
            matrix[row_index] = [
                entry - coefficient * pivot_entry
                for entry, pivot_entry in zip(row, matrix[rank], strict=True)
            ]
        pivot_columns.append(column)
        rank += 1
        if rank == len(matrix):
            break
    nonzero_rows = [
        row for row in matrix if any(entry != 0 for entry in row)
    ]
    return nonzero_rows, pivot_columns


def _find_pivot_row(
    matrix: list[list[Fraction]],
    start_row: int,
    column: int,
) -> int | None:
    for row_index in range(start_row, len(matrix)):
        if matrix[row_index][column] != 0:
            return row_index
    return None
