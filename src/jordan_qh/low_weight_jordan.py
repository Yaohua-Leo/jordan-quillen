"""Low-weight ordinary Jordan algebra enumeration for fixed experiments.

This module is intentionally small and experimental.  It enumerates the free
commutative nonassociative algebra on weighted generators up to a product
weight bound, quotients by the linearized ordinary Jordan identity, and
computes the differential induced by declared generator differentials.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations_with_replacement
from typing import TypeAlias

from jordan_qh.chain_complex import (
    FiniteChainComplex,
    MatrixRows,
)

Term: TypeAlias = tuple[str, str] | tuple[str, object, object]
RawVector: TypeAlias = dict[Term, Fraction]
SparseRow: TypeAlias = dict[int, Fraction]


@dataclass(frozen=True)
class WeightedGenerator:
    """A generator in the bounded quasi-free ordinary Jordan model."""

    name: str
    degree: int
    weight: int


@dataclass(frozen=True)
class AttachedCell:
    """A cell attached to kill one bounded homology representative."""

    name: str
    degree: int
    weight: int
    differential: RawVector
    linear_part: tuple[Fraction, ...]
    d_squared_zero: bool


@dataclass(frozen=True)
class QuotientSpace:
    """One homogeneous quotient space of the free ordinary Jordan algebra."""

    degree: int
    weight: int
    raw_terms: tuple[Term, ...]
    pivot_rows: dict[int, SparseRow]
    free_columns: tuple[int, ...]

    def dimension(self) -> int:
        return len(self.free_columns)

    def basis_terms(self) -> tuple[Term, ...]:
        return tuple(self.raw_terms[column] for column in self.free_columns)

    def reduce_vector(self, vector: RawVector) -> tuple[Fraction, ...]:
        """Reduce a raw vector modulo Jordan identities into quotient coords."""
        remainder = self.reduce_vector_sparse(vector)
        return tuple(
            remainder.get(index, Fraction(0)) for index in range(self.dimension())
        )

    def reduce_vector_sparse(self, vector: RawVector) -> SparseRow:
        """Reduce a raw vector modulo Jordan identities into sparse coords."""
        indexed: SparseRow = {}
        term_index = {term: index for index, term in enumerate(self.raw_terms)}
        for term, coefficient in vector.items():
            if coefficient == 0:
                continue
            index = term_index.get(term)
            if index is None:
                msg = f"term {term_to_str(term)} is not in this quotient space"
                raise ValueError(msg)
            indexed[index] = indexed.get(index, Fraction(0)) + coefficient
        remainder = reduce_sparse_row(indexed, self.pivot_rows)
        free_index = {column: index for index, column in enumerate(self.free_columns)}
        return {
            free_index[column]: coefficient
            for column, coefficient in remainder.items()
            if coefficient != 0 and column in free_index
        }

    def lift_coordinates(self, coordinates: Iterable[Fraction]) -> RawVector:
        """Lift quotient coordinates to the chosen free-column raw terms."""
        vector: RawVector = {}
        coords = tuple(Fraction(entry) for entry in coordinates)
        if len(coords) != len(self.free_columns):
            msg = "coordinate length must match quotient dimension"
            raise ValueError(msg)
        for coefficient, column in zip(coords, self.free_columns, strict=True):
            if coefficient != 0:
                vector[self.raw_terms[column]] = coefficient
        return vector

    def lift_sparse_coordinates(self, coordinates: SparseRow) -> RawVector:
        """Lift sparse quotient coordinates to the chosen free-column raw terms."""
        vector: RawVector = {}
        for index, coefficient in coordinates.items():
            if index < 0 or index >= len(self.free_columns):
                msg = "sparse coordinate index is outside the quotient basis"
                raise ValueError(msg)
            if coefficient != 0:
                vector[self.raw_terms[self.free_columns[index]]] = coefficient
        return vector


@dataclass(frozen=True)
class LowWeightJordanModel:
    """A bounded ordinary Jordan model for one generator set."""

    generators: tuple[WeightedGenerator, ...]
    generator_differentials: dict[str, RawVector]
    weight_bound: int
    max_degree: int
    terms_by_degree_weight: dict[tuple[int, int], tuple[Term, ...]]
    spaces: dict[tuple[int, int], QuotientSpace]

    def quotient_space(self, degree: int, weight: int) -> QuotientSpace:
        key = (degree, weight)
        if key not in self.spaces:
            return QuotientSpace(degree, weight, (), {}, ())
        return self.spaces[key]

    def differential_matrix(self, degree: int, weight: int) -> MatrixRows:
        """Return source-row coordinates for d: A_degree,weight -> A_degree-1,weight."""
        source = self.quotient_space(degree, weight)
        target = self.quotient_space(degree - 1, weight)
        rows: list[tuple[Fraction, ...]] = []
        for term in source.basis_terms():
            raw_differential = self.differential_of_term(term)
            rows.append(target.reduce_vector(raw_differential))
        return tuple(rows)

    def differential_sparse_matrix(
        self,
        degree: int,
        weight: int,
    ) -> tuple[SparseRow, ...]:
        """Return sparse source-row coordinates for a homogeneous differential."""
        source = self.quotient_space(degree, weight)
        target = self.quotient_space(degree - 1, weight)
        rows: list[SparseRow] = []
        for term in source.basis_terms():
            raw_differential = self.differential_of_term(term)
            rows.append(target.reduce_vector_sparse(raw_differential))
        return tuple(rows)

    def differential_of_term(self, term: Term) -> RawVector:
        """Compute the derivation differential of a raw term."""
        tag = term[0]
        if tag == "g":
            return dict(self.generator_differentials.get(str(term[1]), {}))
        left = term[1]
        right = term[2]
        if not isinstance(left, tuple) or not isinstance(right, tuple):
            msg = "product term children must be terms"
            raise TypeError(msg)
        result: RawVector = {}
        for d_left, coefficient in self.differential_of_term(left).items():
            _add_raw(result, product_term(d_left, right), coefficient)
        sign = Fraction(-1 if self.term_degree(left) % 2 else 1)
        for d_right, coefficient in self.differential_of_term(right).items():
            _add_raw(result, product_term(left, d_right), sign * coefficient)
        return result

    def term_degree(self, term: Term) -> int:
        if term[0] == "g":
            return self._generator_by_name()[str(term[1])].degree
        left = term[1]
        right = term[2]
        if not isinstance(left, tuple) or not isinstance(right, tuple):
            msg = "product term children must be terms"
            raise TypeError(msg)
        return self.term_degree(left) + self.term_degree(right)

    def term_weight(self, term: Term) -> int:
        if term[0] == "g":
            return self._generator_by_name()[str(term[1])].weight
        left = term[1]
        right = term[2]
        if not isinstance(left, tuple) or not isinstance(right, tuple):
            msg = "product term children must be terms"
            raise TypeError(msg)
        return self.term_weight(left) + self.term_weight(right)

    def _generator_by_name(self) -> dict[str, WeightedGenerator]:
        return {generator.name: generator for generator in self.generators}


def build_low_weight_jordan_model(
    generators: tuple[WeightedGenerator, ...],
    generator_differentials: dict[str, RawVector],
    *,
    weight_bound: int,
    max_degree: int,
) -> LowWeightJordanModel:
    """Build all homogeneous quotient spaces for a bounded generator set."""
    terms_by_key = generate_terms_by_degree_weight(
        generators,
        weight_bound=weight_bound,
        max_degree=max_degree,
    )
    relation_rows = jordan_relation_rows(terms_by_key, weight_bound, max_degree)
    spaces: dict[tuple[int, int], QuotientSpace] = {}
    for key, terms in terms_by_key.items():
        raw_terms = tuple(terms)
        term_index = {term: index for index, term in enumerate(raw_terms)}
        sparse_rows = []
        for relation in relation_rows.get(key, ()):
            row: SparseRow = {}
            for term, coefficient in relation.items():
                index = term_index.get(term)
                if index is not None and coefficient != 0:
                    row[index] = row.get(index, Fraction(0)) + coefficient
            if row:
                sparse_rows.append(row)
        pivot_rows = sparse_rref(sparse_rows)
        free_columns = tuple(
            column for column in range(len(raw_terms)) if column not in pivot_rows
        )
        spaces[key] = QuotientSpace(
            degree=key[0],
            weight=key[1],
            raw_terms=raw_terms,
            pivot_rows=pivot_rows,
            free_columns=free_columns,
        )
    return LowWeightJordanModel(
        generators=generators,
        generator_differentials=generator_differentials,
        weight_bound=weight_bound,
        max_degree=max_degree,
        terms_by_degree_weight=terms_by_key,
        spaces=spaces,
    )


def bounded_homology_representatives(
    model: LowWeightJordanModel,
    *,
    degree: int,
) -> list[tuple[int, tuple[Fraction, ...], RawVector]]:
    """Return bounded full-algebra homology representatives in one degree."""
    representatives: list[tuple[int, tuple[Fraction, ...], RawVector]] = []
    for weight in range(1, model.weight_bound + 1):
        source_dim = model.quotient_space(degree, weight).dimension()
        target_dim = model.quotient_space(degree - 1, weight).dimension()
        if source_dim == 0:
            continue
        reps = sparse_homology_representatives(
            model.differential_sparse_matrix(degree, weight),
            model.differential_sparse_matrix(degree + 1, weight),
            source_dimension=source_dim,
            target_dimension=target_dim,
        )
        for sparse_coords in reps:
            raw = model.quotient_space(degree, weight).lift_sparse_coordinates(
                sparse_coords,
            )
            dense_coords = tuple(
                sparse_coords.get(index, Fraction(0)) for index in range(source_dim)
            )
            representatives.append((weight, dense_coords, raw))
    return representatives


def sparse_homology_representatives(
    boundary_rows_current: tuple[SparseRow, ...],
    boundary_rows_next: tuple[SparseRow, ...],
    *,
    source_dimension: int,
    target_dimension: int,
) -> tuple[SparseRow, ...]:
    """Return sparse representatives for ker(d_current) / im(d_next)."""
    kernel = sparse_kernel_basis(
        boundary_rows_current,
        source_dimension=source_dimension,
        target_dimension=target_dimension,
    )
    quotient_rows = sparse_rref(boundary_rows_next)
    representatives: list[SparseRow] = []
    for vector in kernel:
        remainder = reduce_sparse_row(vector, quotient_rows)
        if not remainder:
            continue
        representatives.append(vector)
        pivot = min(remainder)
        coefficient = remainder[pivot]
        normalized = {
            column: value / coefficient for column, value in remainder.items()
        }
        quotient_rows[pivot] = normalized
        quotient_rows = sparse_rref(quotient_rows.values())
    return tuple(representatives)


def sparse_kernel_basis(
    rows: tuple[SparseRow, ...],
    *,
    source_dimension: int,
    target_dimension: int,
) -> tuple[SparseRow, ...]:
    """Return a sparse basis for the kernel of a source-row map."""
    equations: list[SparseRow] = [dict() for _ in range(target_dimension)]
    for source_index, row in enumerate(rows):
        for target_index, coefficient in row.items():
            if coefficient != 0:
                equations[target_index][source_index] = (
                    equations[target_index].get(source_index, Fraction(0))
                    + coefficient
                )
    pivot_rows = sparse_rref(equations)
    pivot_columns = set(pivot_rows)
    basis: list[SparseRow] = []
    for free_column in range(source_dimension):
        if free_column in pivot_columns:
            continue
        vector: SparseRow = {free_column: Fraction(1)}
        for pivot, row in pivot_rows.items():
            coefficient = row.get(free_column, Fraction(0))
            if coefficient != 0:
                vector[pivot] = -coefficient
        basis.append(_clean_sparse(vector))
    return tuple(basis)


def generate_terms_by_degree_weight(
    generators: tuple[WeightedGenerator, ...],
    *,
    weight_bound: int,
    max_degree: int,
) -> dict[tuple[int, int], tuple[Term, ...]]:
    """Generate canonical commutative nonassociative terms."""
    terms: list[Term] = []
    metadata: dict[Term, tuple[int, int]] = {}
    for generator in sorted(generators, key=lambda item: item.name):
        if generator.weight <= weight_bound and generator.degree <= max_degree:
            term: Term = ("g", generator.name)
            terms.append(term)
            metadata[term] = (generator.degree, generator.weight)

    for weight in range(2, weight_bound + 1):
        existing = list(terms)
        new_terms: list[Term] = []
        for left in existing:
            left_degree, left_weight = metadata[left]
            for right in existing:
                right_degree, right_weight = metadata[right]
                if left_weight + right_weight != weight:
                    continue
                if left_degree + right_degree > max_degree:
                    continue
                term = product_term(left, right)
                if term in metadata:
                    continue
                metadata[term] = (
                    left_degree + right_degree,
                    left_weight + right_weight,
                )
                new_terms.append(term)
        terms.extend(sorted(new_terms, key=term_sort_key))

    grouped: dict[tuple[int, int], list[Term]] = defaultdict(list)
    for term in sorted(terms, key=term_sort_key):
        grouped[metadata[term]].append(term)
    return {key: tuple(value) for key, value in grouped.items()}


def jordan_relation_rows(
    terms_by_key: dict[tuple[int, int], tuple[Term, ...]],
    weight_bound: int,
    max_degree: int,
) -> dict[tuple[int, int], tuple[RawVector, ...]]:
    """Generate sparse linearized ordinary Jordan identity rows."""
    all_terms = tuple(term for terms in terms_by_key.values() for term in terms)
    term_metadata = {
        term: key for key, terms in terms_by_key.items() for term in terms
    }
    rows: dict[tuple[int, int], list[RawVector]] = defaultdict(list)
    abc_terms = tuple(
        term
        for term in all_terms
        if term_metadata[term][1] <= weight_bound - 3
        and term_metadata[term][0] <= max_degree
    )
    triples = combinations_with_replacement(abc_terms, 3)
    for a, b, c in triples:
        abc_degree = (
            term_metadata[a][0] + term_metadata[b][0] + term_metadata[c][0]
        )
        abc_weight = (
            term_metadata[a][1] + term_metadata[b][1] + term_metadata[c][1]
        )
        if abc_degree > max_degree or abc_weight > weight_bound - 1:
            continue
        for d in all_terms:
            total_degree = abc_degree + term_metadata[d][0]
            total_weight = abc_weight + term_metadata[d][1]
            if total_degree > max_degree or total_weight > weight_bound:
                continue
            row = linearized_jordan_relation(a, b, c, d)
            if row:
                rows[(total_degree, total_weight)].append(row)
    return {key: tuple(value) for key, value in rows.items()}


def linearized_jordan_relation(a: Term, b: Term, c: Term, d: Term) -> RawVector:
    """Return the ordinary linearized Jordan identity relation."""
    row: RawVector = {}
    for term in (
        product_term(product_term(product_term(a, b), d), c),
        product_term(product_term(product_term(a, c), d), b),
        product_term(product_term(product_term(b, c), d), a),
    ):
        _add_raw(row, term, Fraction(1))
    for term in (
        product_term(product_term(a, b), product_term(d, c)),
        product_term(product_term(a, c), product_term(d, b)),
        product_term(product_term(b, c), product_term(d, a)),
    ):
        _add_raw(row, term, Fraction(-1))
    return row


def product_term(left: Term, right: Term) -> Term:
    """Return a canonical commutative product term."""
    if term_sort_key(right) < term_sort_key(left):
        left, right = right, left
    return ("*", left, right)


def term_to_str(term: Term) -> str:
    """Render a term for experiment output."""
    if term[0] == "g":
        return str(term[1])
    left = term[1]
    right = term[2]
    if not isinstance(left, tuple) or not isinstance(right, tuple):
        msg = "product term children must be terms"
        raise TypeError(msg)
    return f"({term_to_str(left)}*{term_to_str(right)})"


def term_sort_key(term: Term) -> str:
    """Return a stable ordering key for canonical products."""
    return term_to_str(term)


def sparse_rref(rows: Iterable[SparseRow]) -> dict[int, SparseRow]:
    """Return normalized sparse echelon rows keyed by pivot column."""
    pivot_rows: dict[int, SparseRow] = {}
    for input_row in rows:
        row = _clean_sparse(input_row)
        row = reduce_sparse_row(row, pivot_rows)
        if not row:
            continue
        pivot = min(row)
        coefficient = row[pivot]
        normalized = {
            column: value / coefficient for column, value in row.items()
        }
        pivot_rows[pivot] = normalized

    for pivot in sorted(pivot_rows, reverse=True):
        row = pivot_rows[pivot]
        for earlier_pivot in sorted(
            column for column in pivot_rows if column < pivot
        ):
            earlier = pivot_rows[earlier_pivot]
            coefficient = earlier.get(pivot, Fraction(0))
            if coefficient == 0:
                continue
            updated = dict(earlier)
            for column, value in row.items():
                updated[column] = updated.get(column, Fraction(0)) - coefficient * value
            pivot_rows[earlier_pivot] = _clean_sparse(updated)
    return dict(sorted(pivot_rows.items()))


def reduce_sparse_row(row: SparseRow, pivot_rows: dict[int, SparseRow]) -> SparseRow:
    """Reduce a sparse row by normalized pivot rows."""
    reduced = _clean_sparse(row)
    for pivot, pivot_row in sorted(pivot_rows.items()):
        coefficient = reduced.get(pivot, Fraction(0))
        if coefficient == 0:
            continue
        for column, value in pivot_row.items():
            reduced[column] = reduced.get(column, Fraction(0)) - coefficient * value
        reduced = _clean_sparse(reduced)
    return reduced


def raw_vector_to_terms(vector: RawVector) -> str:
    """Render a raw vector as a compact sum of terms."""
    if not vector:
        return "0"
    parts: list[str] = []
    sorted_terms = sorted(
        vector.items(),
        key=lambda item: term_sort_key(item[0]),
    )
    for term, coefficient in sorted_terms:
        if coefficient == 1:
            parts.append(term_to_str(term))
        elif coefficient == -1:
            parts.append(f"-{term_to_str(term)}")
        else:
            parts.append(f"{coefficient}*{term_to_str(term)}")
    return " + ".join(parts).replace("+ -", "- ")


def vector_from_term(term: Term, coefficient: Fraction = Fraction(1)) -> RawVector:
    """Return a one-term raw vector."""
    return {term: coefficient}


def _add_raw(vector: RawVector, term: Term, coefficient: Fraction) -> None:
    if coefficient == 0:
        return
    vector[term] = vector.get(term, Fraction(0)) + coefficient
    if vector[term] == 0:
        del vector[term]


def _clean_sparse(row: SparseRow) -> SparseRow:
    return {
        column: coefficient
        for column, coefficient in row.items()
        if coefficient != 0
    }


def chain_complex_for_cells(
    cells_by_degree: dict[int, tuple[str, ...]],
) -> FiniteChainComplex:
    """Create an empty source-row chain complex for named cell groups."""
    return FiniteChainComplex(bases=cells_by_degree, differentials={})
