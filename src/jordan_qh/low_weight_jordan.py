"""Low-weight ordinary Jordan algebra enumeration for fixed experiments.

This module is intentionally small and experimental.  It enumerates the free
commutative nonassociative algebra on weighted generators up to a product
weight bound, quotients by the linearized ordinary Jordan identity, and
computes the differential induced by declared generator differentials.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from fractions import Fraction
from functools import cache
from itertools import combinations_with_replacement
from time import perf_counter
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
    term_index: dict[Term, int]
    free_index: dict[int, int]

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
        for term, coefficient in vector.items():
            if coefficient == 0:
                continue
            index = self.term_index.get(term)
            if index is None:
                msg = f"term {term_to_str(term)} is not in this quotient space"
                raise ValueError(msg)
            indexed[index] = indexed.get(index, Fraction(0)) + coefficient
        remainder = reduce_sparse_row(indexed, self.pivot_rows)
        return {
            self.free_index[column]: coefficient
            for column, coefficient in remainder.items()
            if coefficient != 0 and column in self.free_index
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
    _differential_cache: dict[Term, tuple[tuple[Term, Fraction], ...]] = field(
        default_factory=dict,
        compare=False,
        repr=False,
    )

    def quotient_space(self, degree: int, weight: int) -> QuotientSpace:
        key = (degree, weight)
        if key not in self.spaces:
            return _make_quotient_space(
                degree=degree,
                weight=weight,
                raw_terms=(),
                pivot_rows={},
                free_columns=(),
            )
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
        *,
        workers: int = 1,
    ) -> tuple[SparseRow, ...]:
        """Return sparse source-row coordinates for a homogeneous differential."""
        source = self.quotient_space(degree, weight)
        target = self.quotient_space(degree - 1, weight)
        basis_terms = source.basis_terms()
        if workers > 1 and len(basis_terms) > 1:
            return _parallel_differential_sparse_matrix(
                model=self,
                target=target,
                basis_terms=basis_terms,
                workers=workers,
            )
        rows: list[SparseRow] = []
        for term in basis_terms:
            raw_differential = self.differential_of_term(term)
            rows.append(target.reduce_vector_sparse(raw_differential))
        return tuple(rows)

    def differential_of_term(self, term: Term) -> RawVector:
        """Compute the derivation differential of a raw term."""
        if term in self._differential_cache:
            return _thaw_raw_vector(self._differential_cache[term])
        tag = term[0]
        if tag == "g":
            result = dict(self.generator_differentials.get(str(term[1]), {}))
        else:
            left = term[1]
            right = term[2]
            if not isinstance(left, tuple) or not isinstance(right, tuple):
                msg = "product term children must be terms"
                raise TypeError(msg)
            result = {}
            for d_left, coefficient in self.differential_of_term(left).items():
                _add_raw(result, product_term(d_left, right), coefficient)
            sign = Fraction(-1 if self.term_degree(left) % 2 else 1)
            for d_right, coefficient in self.differential_of_term(right).items():
                _add_raw(result, product_term(left, d_right), sign * coefficient)
        self._differential_cache[term] = _freeze_raw_vector(result)
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
    workers: int = 1,
    progress: Callable[[str], None] | None = None,
) -> LowWeightJordanModel:
    """Build all homogeneous quotient spaces for a bounded generator set."""
    terms_by_key = generate_terms_by_degree_weight(
        generators,
        weight_bound=weight_bound,
        max_degree=max_degree,
    )
    if progress is not None:
        progress(
            "generated terms: "
            f"{sum(len(terms) for terms in terms_by_key.values())} raw terms "
            f"across {len(terms_by_key)} homogeneous spaces",
        )
    relation_rows = jordan_relation_rows(terms_by_key, weight_bound, max_degree)
    if progress is not None:
        progress(
            "generated relation rows: "
            f"{sum(len(rows) for rows in relation_rows.values())} rows",
        )
    spaces: dict[tuple[int, int], QuotientSpace] = {}
    space_inputs = tuple(
        (key, tuple(terms), relation_rows.get(key, ()))
        for key, terms in sorted(terms_by_key.items())
    )
    if workers > 1 and len(space_inputs) > 1:
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=workers) as executor:
            for key, space in executor.map(
                _build_quotient_space_from_payload,
                space_inputs,
                chunksize=1,
            ):
                spaces[key] = space
                if progress is not None:
                    progress(
                        "built quotient space "
                        f"degree={key[0]} weight={key[1]} "
                        f"dim={space.dimension()} raw={len(space.raw_terms)}",
                    )
    else:
        for payload in space_inputs:
            key, space = _build_quotient_space_from_payload(payload)
            spaces[key] = space
            if progress is not None:
                progress(
                    "built quotient space "
                    f"degree={key[0]} weight={key[1]} "
                    f"dim={space.dimension()} raw={len(space.raw_terms)}",
                )
    return LowWeightJordanModel(
        generators=generators,
        generator_differentials=generator_differentials,
        weight_bound=weight_bound,
        max_degree=max_degree,
        terms_by_degree_weight=terms_by_key,
        spaces=spaces,
    )


def _build_quotient_space_from_payload(
    payload: tuple[tuple[int, int], tuple[Term, ...], tuple[RawVector, ...]],
) -> tuple[tuple[int, int], QuotientSpace]:
    key, raw_terms, relations = payload
    term_index = {term: index for index, term in enumerate(raw_terms)}
    sparse_rows = []
    for relation in relations:
        row: SparseRow = {}
        for term, coefficient in relation.items():
            index = term_index.get(term)
            if index is not None and coefficient != 0:
                row[index] = row.get(index, Fraction(0)) + coefficient
        if row:
            sparse_rows.append(row)
    pivot_rows = sparse_echelon(sparse_rows)
    free_columns = tuple(
        column for column in range(len(raw_terms)) if column not in pivot_rows
    )
    return (
        key,
        _make_quotient_space(
            degree=key[0],
            weight=key[1],
            raw_terms=raw_terms,
            pivot_rows=pivot_rows,
            free_columns=free_columns,
        )
    )


def _make_quotient_space(
    *,
    degree: int,
    weight: int,
    raw_terms: tuple[Term, ...],
    pivot_rows: dict[int, SparseRow],
    free_columns: tuple[int, ...],
) -> QuotientSpace:
    return QuotientSpace(
        degree=degree,
        weight=weight,
        raw_terms=raw_terms,
        pivot_rows=pivot_rows,
        free_columns=free_columns,
        term_index={term: index for index, term in enumerate(raw_terms)},
        free_index={column: index for index, column in enumerate(free_columns)},
    )


def _freeze_raw_vector(vector: RawVector) -> tuple[tuple[Term, Fraction], ...]:
    return tuple(
        sorted(
            (
                (term, Fraction(coefficient))
                for term, coefficient in vector.items()
                if coefficient != 0
            ),
            key=lambda item: term_sort_key(item[0]),
        ),
    )


def _thaw_raw_vector(vector: tuple[tuple[Term, Fraction], ...]) -> RawVector:
    return {term: coefficient for term, coefficient in vector}


_MATRIX_WORKER_MODEL: LowWeightJordanModel | None = None
_MATRIX_WORKER_TARGET: QuotientSpace | None = None


def _initialize_matrix_worker(
    model: LowWeightJordanModel,
    target: QuotientSpace,
) -> None:
    global _MATRIX_WORKER_MODEL, _MATRIX_WORKER_TARGET
    _MATRIX_WORKER_MODEL = model
    _MATRIX_WORKER_TARGET = target


def _matrix_rows_for_terms(terms: tuple[Term, ...]) -> tuple[SparseRow, ...]:
    if _MATRIX_WORKER_MODEL is None or _MATRIX_WORKER_TARGET is None:
        msg = "matrix worker was not initialized"
        raise RuntimeError(msg)
    rows: list[SparseRow] = []
    for term in terms:
        raw_differential = _MATRIX_WORKER_MODEL.differential_of_term(term)
        rows.append(_MATRIX_WORKER_TARGET.reduce_vector_sparse(raw_differential))
    return tuple(rows)


def _parallel_differential_sparse_matrix(
    *,
    model: LowWeightJordanModel,
    target: QuotientSpace,
    basis_terms: tuple[Term, ...],
    workers: int,
) -> tuple[SparseRow, ...]:
    from concurrent.futures import ProcessPoolExecutor

    worker_count = min(max(1, workers), len(basis_terms))
    chunks = _split_terms(basis_terms, worker_count * 4)
    rows: list[SparseRow] = []
    with ProcessPoolExecutor(
        max_workers=worker_count,
        initializer=_initialize_matrix_worker,
        initargs=(model, target),
    ) as executor:
        for chunk_rows in executor.map(_matrix_rows_for_terms, chunks, chunksize=1):
            rows.extend(chunk_rows)
    return tuple(rows)


def _split_terms(
    terms: tuple[Term, ...],
    max_chunks: int,
) -> tuple[tuple[Term, ...], ...]:
    chunk_count = min(max(1, max_chunks), len(terms))
    chunk_size = (len(terms) + chunk_count - 1) // chunk_count
    return tuple(
        terms[start : start + chunk_size]
        for start in range(0, len(terms), chunk_size)
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
    grouped: dict[tuple[int, int], list[Term]] = defaultdict(list)
    for generator in sorted(generators, key=lambda item: item.name):
        if generator.weight <= weight_bound and generator.degree <= max_degree:
            term: Term = ("g", generator.name)
            terms.append(term)
            metadata[term] = (generator.degree, generator.weight)
            grouped[(generator.degree, generator.weight)].append(term)

    for weight in range(2, weight_bound + 1):
        group_keys = tuple(sorted(grouped))
        new_terms: list[Term] = []
        for left_index, left_key in enumerate(group_keys):
            left_degree, left_weight = left_key
            for right_key in group_keys[left_index:]:
                right_degree, right_weight = right_key
                total_degree = left_degree + right_degree
                if total_degree > max_degree:
                    continue
                if left_weight + right_weight != weight:
                    continue
                for left, right in _product_pairs_for_keys(
                    left_key,
                    right_key,
                    grouped,
                ):
                    term = product_term(left, right)
                    if term in metadata:
                        continue
                    metadata[term] = (total_degree, weight)
                    new_terms.append(term)
        terms.extend(sorted(new_terms, key=term_sort_key))
        for term in new_terms:
            grouped[metadata[term]].append(term)

    result: dict[tuple[int, int], list[Term]] = defaultdict(list)
    for term in sorted(terms, key=term_sort_key):
        result[metadata[term]].append(term)
    return {key: tuple(value) for key, value in result.items()}


def _product_pairs_for_keys(
    left_key: tuple[int, int],
    right_key: tuple[int, int],
    grouped: dict[tuple[int, int], list[Term]],
) -> Iterable[tuple[Term, Term]]:
    left_terms = grouped[left_key]
    right_terms = grouped[right_key]
    if left_key == right_key:
        yield from combinations_with_replacement(left_terms, 2)
        return
    for left in left_terms:
        for right in right_terms:
            yield (left, right)


def jordan_relation_rows(
    terms_by_key: dict[tuple[int, int], tuple[Term, ...]],
    weight_bound: int,
    max_degree: int,
) -> dict[tuple[int, int], tuple[RawVector, ...]]:
    """Generate sparse linearized ordinary Jordan identity rows."""
    rows: dict[tuple[int, int], list[RawVector]] = defaultdict(list)
    abc_keys = tuple(
        key
        for key, terms in sorted(terms_by_key.items())
        if terms and key[1] <= weight_bound - 3 and key[0] <= max_degree
    )
    d_terms_by_key = {
        key: terms
        for key, terms in sorted(terms_by_key.items())
        if terms
    }
    for left_index, left_key in enumerate(abc_keys):
        for middle_index in range(left_index, len(abc_keys)):
            middle_key = abc_keys[middle_index]
            for right_index in range(middle_index, len(abc_keys)):
                right_key = abc_keys[right_index]
                abc_degree = left_key[0] + middle_key[0] + right_key[0]
                abc_weight = left_key[1] + middle_key[1] + right_key[1]
                if abc_degree > max_degree or abc_weight > weight_bound - 1:
                    continue
                for a, b, c in _relation_triples_for_keys(
                    left_key,
                    middle_key,
                    right_key,
                    d_terms_by_key,
                ):
                    _append_relation_rows_for_triple(
                        rows,
                        d_terms_by_key,
                        weight_bound,
                        max_degree,
                        a,
                        b,
                        c,
                        abc_degree,
                        abc_weight,
                    )
    return {key: tuple(value) for key, value in rows.items()}


def _relation_triples_for_keys(
    left_key: tuple[int, int],
    middle_key: tuple[int, int],
    right_key: tuple[int, int],
    terms_by_key: dict[tuple[int, int], tuple[Term, ...]],
) -> Iterable[tuple[Term, Term, Term]]:
    left_terms = terms_by_key[left_key]
    middle_terms = terms_by_key[middle_key]
    right_terms = terms_by_key[right_key]
    if left_key == middle_key == right_key:
        yield from combinations_with_replacement(left_terms, 3)
        return
    if left_key == middle_key:
        for a, b in combinations_with_replacement(left_terms, 2):
            for c in right_terms:
                yield (a, b, c)
        return
    if middle_key == right_key:
        for a in left_terms:
            for b, c in combinations_with_replacement(middle_terms, 2):
                yield (a, b, c)
        return
    for a in left_terms:
        for b in middle_terms:
            for c in right_terms:
                yield (a, b, c)


def _append_relation_rows_for_triple(
    rows: dict[tuple[int, int], list[RawVector]],
    d_terms_by_key: dict[tuple[int, int], tuple[Term, ...]],
    weight_bound: int,
    max_degree: int,
    a: Term,
    b: Term,
    c: Term,
    abc_degree: int,
    abc_weight: int,
) -> None:
    if abc_degree > max_degree or abc_weight > weight_bound - 1:
        return
    for d_key, d_terms in d_terms_by_key.items():
        total_degree = abc_degree + d_key[0]
        total_weight = abc_weight + d_key[1]
        if total_degree > max_degree or total_weight > weight_bound:
            continue
        for d in d_terms:
            row = linearized_jordan_relation(a, b, c, d)
            if row:
                rows[(total_degree, total_weight)].append(row)


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


@cache
def product_term(left: Term, right: Term) -> Term:
    """Return a canonical commutative product term."""
    if term_sort_key(right) < term_sort_key(left):
        left, right = right, left
    return ("*", left, right)


@cache
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


@cache
def term_sort_key(term: Term) -> str:
    """Return a stable ordering key for canonical products."""
    return term_to_str(term)


def sparse_rref(rows: Iterable[SparseRow]) -> dict[int, SparseRow]:
    """Return normalized sparse echelon rows keyed by pivot column."""
    pivot_rows = sparse_echelon(rows)

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


def sparse_echelon(
    rows: Iterable[SparseRow],
    *,
    max_rank: int | None = None,
) -> dict[int, SparseRow]:
    """Return normalized sparse row-echelon rows keyed by pivot column."""
    pivot_rows: dict[int, SparseRow] = {}
    for input_row in rows:
        row = reduce_sparse_row(input_row, pivot_rows)
        if not row:
            continue
        pivot = min(row)
        coefficient = row[pivot]
        pivot_rows[pivot] = {
            column: value / coefficient for column, value in row.items()
        }
        if max_rank is not None and len(pivot_rows) >= max_rank:
            break
    return dict(sorted(pivot_rows.items()))


def sparse_modular_rank(
    rows: Iterable[SparseRow],
    *,
    prime: int,
    max_rank: int | None = None,
) -> int:
    """Return a sparse row rank lower bound by reducing modulo ``prime``."""
    pivot_rows: dict[int, dict[int, int]] = {}
    for input_row in rows:
        row = _fraction_row_to_mod(input_row, prime)
        while row:
            pivot = min(row)
            pivot_row = pivot_rows.get(pivot)
            if pivot_row is None:
                break
            coefficient = row[pivot]
            for column, value in pivot_row.items():
                updated = (row.get(column, 0) - coefficient * value) % prime
                if updated:
                    row[column] = updated
                elif column in row:
                    del row[column]
        if not row:
            continue
        pivot = min(row)
        inverse = pow(row[pivot], -1, prime)
        pivot_rows[pivot] = {
            column: (value * inverse) % prime
            for column, value in row.items()
            if value % prime
        }
        if max_rank is not None and len(pivot_rows) >= max_rank:
            break
    return len(pivot_rows)


def sparse_modular_rank_v2(
    rows: Iterable[SparseRow],
    *,
    prime: int,
    max_rank: int | None = None,
    progress: Callable[[str], None] | None = None,
    progress_interval: int = 10_000,
    progress_seconds: float = 15.0,
    max_seconds: float | None = None,
) -> int:
    """Return a modular sparse rank lower bound with cached row conversion.

    This backend keeps the same rank-certificate semantics as
    ``sparse_modular_rank`` but converts all input rows to ``F_p`` once and
    stores normalized pivot rows as immutable item tuples.  The optional
    progress callback is intended for long high-weight experiment runs.
    """

    start = perf_counter()
    last_progress = start
    inverse_cache: dict[int, int] = {}
    converted_rows: list[dict[int, int]] = []
    input_nnz = 0
    for row_index, input_row in enumerate(rows, start=1):
        _raise_if_rank_timeout(start=start, max_seconds=max_seconds)
        mod_row = _fraction_row_to_mod_cached(input_row, prime, inverse_cache)
        input_nnz += len(mod_row)
        converted_rows.append(mod_row)
        now = perf_counter()
        if progress is not None and _should_report_progress(
            row_index=row_index,
            now=now,
            last_progress=last_progress,
            progress_interval=progress_interval,
            progress_seconds=progress_seconds,
        ):
            progress(
                "conversion "
                f"processed_rows={row_index} input_nnz={input_nnz} "
                f"elapsed_seconds={now - start:.3f}",
            )
            last_progress = now
    if progress is not None:
        progress(
            "conversion complete "
            f"processed_rows={len(converted_rows)} input_nnz={input_nnz} "
            f"elapsed_seconds={perf_counter() - start:.3f}",
        )

    rank_start = perf_counter()
    last_progress = rank_start
    pivot_rows: dict[int, tuple[tuple[int, int], ...]] = {}
    max_live_row_nnz = 0
    reductions = 0
    for row_index, input_row in enumerate(converted_rows, start=1):
        _raise_if_rank_timeout(start=start, max_seconds=max_seconds)
        row = dict(input_row)
        while row:
            _raise_if_rank_timeout(start=start, max_seconds=max_seconds)
            pivot = min(row)
            pivot_row = pivot_rows.get(pivot)
            if pivot_row is None:
                break
            coefficient = row[pivot]
            reductions += 1
            for column, value in pivot_row:
                updated = (row.get(column, 0) - coefficient * value) % prime
                if updated:
                    row[column] = updated
                elif column in row:
                    del row[column]
        if row:
            max_live_row_nnz = max(max_live_row_nnz, len(row))
            pivot = min(row)
            inverse = pow(row[pivot], -1, prime)
            pivot_rows[pivot] = tuple(
                sorted(
                    (
                        (column, (value * inverse) % prime)
                        for column, value in row.items()
                        if value % prime
                    ),
                ),
            )
            if max_rank is not None and len(pivot_rows) >= max_rank:
                break
        now = perf_counter()
        if progress is not None and _should_report_progress(
            row_index=row_index,
            now=now,
            last_progress=last_progress,
            progress_interval=progress_interval,
            progress_seconds=progress_seconds,
        ):
            elapsed = now - rank_start
            rows_per_second = row_index / elapsed if elapsed > 0 else 0.0
            progress(
                "elimination "
                f"processed_rows={row_index} current_rank={len(pivot_rows)} "
                f"pivot_count={len(pivot_rows)} reductions={reductions} "
                f"max_live_row_nnz={max_live_row_nnz} "
                f"rows_per_second={rows_per_second:.3f} "
                f"elapsed_seconds={elapsed:.3f}",
            )
            last_progress = now
    if progress is not None:
        progress(
            "elimination complete "
            f"processed_rows={row_index if converted_rows else 0} "
            f"current_rank={len(pivot_rows)} pivot_count={len(pivot_rows)} "
            f"reductions={reductions} max_live_row_nnz={max_live_row_nnz} "
            f"elapsed_seconds={perf_counter() - rank_start:.3f}",
        )
    return len(pivot_rows)


def reduce_sparse_row(row: SparseRow, pivot_rows: dict[int, SparseRow]) -> SparseRow:
    """Reduce a sparse row by normalized pivot rows."""
    reduced = _clean_sparse(row)
    while reduced:
        pivot = min(
            (column for column in reduced if column in pivot_rows),
            default=None,
        )
        if pivot is None:
            break
        coefficient = reduced[pivot]
        pivot_row = pivot_rows[pivot]
        for column, value in pivot_row.items():
            reduced[column] = reduced.get(column, Fraction(0)) - coefficient * value
        reduced = _clean_sparse(reduced)
    return reduced


def _fraction_row_to_mod(row: SparseRow, prime: int) -> dict[int, int]:
    mod_row: dict[int, int] = {}
    for column, value in row.items():
        value = Fraction(value)
        denominator = value.denominator % prime
        if denominator == 0:
            msg = f"denominator is not invertible modulo {prime}"
            raise ValueError(msg)
        coefficient = (value.numerator % prime) * pow(denominator, -1, prime)
        coefficient %= prime
        if coefficient:
            mod_row[column] = coefficient
    return mod_row


def _fraction_row_to_mod_cached(
    row: SparseRow,
    prime: int,
    inverse_cache: dict[int, int],
) -> dict[int, int]:
    mod_row: dict[int, int] = {}
    for column, value in row.items():
        value = Fraction(value)
        denominator = value.denominator % prime
        if denominator == 0:
            msg = f"denominator is not invertible modulo {prime}"
            raise ValueError(msg)
        inverse = inverse_cache.get(denominator)
        if inverse is None:
            inverse = pow(denominator, -1, prime)
            inverse_cache[denominator] = inverse
        coefficient = (value.numerator % prime) * inverse
        coefficient %= prime
        if coefficient:
            mod_row[column] = coefficient
    return mod_row


def _should_report_progress(
    *,
    row_index: int,
    now: float,
    last_progress: float,
    progress_interval: int,
    progress_seconds: float,
) -> bool:
    interval_hit = progress_interval > 0 and row_index % progress_interval == 0
    time_hit = progress_seconds > 0 and now - last_progress >= progress_seconds
    return interval_hit or time_hit


def _raise_if_rank_timeout(
    *,
    start: float,
    max_seconds: float | None,
) -> None:
    if max_seconds is not None and perf_counter() - start > max_seconds:
        msg = f"modular rank exceeded max_rank_seconds={max_seconds}"
        raise TimeoutError(msg)


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
