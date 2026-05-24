"""Exact linear algebra helpers."""

from collections.abc import Sequence
from fractions import Fraction


def row_rank(rows: Sequence[Sequence[Fraction]], dimension: int) -> int:
    """Return the exact row rank of a matrix over the rationals."""
    matrix: list[list[Fraction]] = []
    for row in rows:
        if len(row) != dimension:
            msg = "each row length must match dimension"
            raise ValueError(msg)
        normalized_row = [Fraction(entry) for entry in row]
        if any(entry != 0 for entry in normalized_row):
            matrix.append(normalized_row)

    rank = 0
    pivot_column = 0

    while rank < len(matrix) and pivot_column < dimension:
        pivot_row = _find_pivot_row(matrix, rank, pivot_column)
        if pivot_row is None:
            pivot_column += 1
            continue

        matrix[rank], matrix[pivot_row] = matrix[pivot_row], matrix[rank]
        pivot = matrix[rank][pivot_column]
        matrix[rank] = [entry / pivot for entry in matrix[rank]]

        for row_index, row in enumerate(matrix):
            if row_index == rank:
                continue
            coefficient = row[pivot_column]
            if coefficient == 0:
                continue
            matrix[row_index] = [
                entry - coefficient * pivot_entry
                for entry, pivot_entry in zip(row, matrix[rank], strict=True)
            ]

        rank += 1
        pivot_column += 1

    return rank


def _find_pivot_row(
    matrix: list[list[Fraction]],
    start_row: int,
    column: int,
) -> int | None:
    for row_index in range(start_row, len(matrix)):
        if matrix[row_index][column] != 0:
            return row_index
    return None
