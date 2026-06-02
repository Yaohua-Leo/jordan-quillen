from fractions import Fraction

from jordan_qh.low_weight_jordan import (
    build_low_weight_jordan_model,
    product_term,
    sparse_modular_rank,
)
from jordan_qh.v2_cells_no_q import (
    EXP011_ID,
    Exp011Thresholds,
    compute_exp011,
    initial_generators_and_differentials,
    raw_count_estimates,
    report_language_has_no_forbidden_global_phrasing,
    select_feasible_weight,
)


def test_raw_count_preflight_selects_weight_8_before_large_weight_9() -> None:
    thresholds = Exp011Thresholds(max_raw_terms_per_space=10_000)

    feasible_weight, skip, estimates = select_feasible_weight(9, thresholds)

    assert feasible_weight == 8
    assert skip is not None
    assert skip["first_skipped_weight"] == 9
    assert estimates[8]["max_raw_terms_per_space"] == 5142
    assert estimates[9]["max_raw_terms_per_space"] == 21426


def test_raw_count_estimates_match_existing_low_weight_backend_counts() -> None:
    estimates = raw_count_estimates(4)

    assert estimates[1]["raw_terms_by_degree"] == {
        "degree_0": 2,
        "degree_1": 0,
        "degree_2": 0,
    }
    assert estimates[4]["raw_terms_by_degree"] == {
        "degree_0": 18,
        "degree_1": 21,
        "degree_2": 6,
    }


def test_quotient_space_uses_resident_indices_for_reduction() -> None:
    generators, differentials = initial_generators_and_differentials()
    model = build_low_weight_jordan_model(
        generators,
        differentials,
        weight_bound=4,
        max_degree=2,
    )
    quotient = model.quotient_space(1, 4)
    basis_term = quotient.basis_terms()[0]

    assert quotient.term_index[basis_term] == quotient.free_columns[0]
    assert quotient.free_index[quotient.free_columns[0]] == 0
    assert quotient.reduce_vector_sparse({basis_term: Fraction(1)}) == {
        0: Fraction(1),
    }


def test_differential_cache_returns_fresh_vectors() -> None:
    generators, differentials = initial_generators_and_differentials()
    model = build_low_weight_jordan_model(
        generators,
        differentials,
        weight_bound=4,
        max_degree=2,
    )
    term = product_term(("g", "r_xx"), ("g", "x"))

    first = model.differential_of_term(term)
    first[("g", "x")] = Fraction(99)

    assert model.differential_of_term(term) == {
        product_term(product_term(("g", "x"), ("g", "x")), ("g", "x")): Fraction(1),
    }


def test_parallel_sparse_matrix_matches_serial_matrix() -> None:
    generators, differentials = initial_generators_and_differentials()
    model = build_low_weight_jordan_model(
        generators,
        differentials,
        weight_bound=4,
        max_degree=2,
    )

    serial = model.differential_sparse_matrix(1, 4)
    parallel = model.differential_sparse_matrix(1, 4, workers=2)

    assert parallel == serial


def test_exp011_weight_4_finds_eight_formal_v2_candidates(tmp_path) -> None:
    run = compute_exp011(
        max_weight=4,
        mode="dry",
        output_dir=tmp_path,
        thresholds=Exp011Thresholds(),
    )

    assert run.results["experiment_id"] == EXP011_ID
    assert run.results["field"] == "QQ"
    assert run.results["arithmetic"] == "exact_rational"
    assert run.results["applies_Q"] is False
    assert run.results["constructs_higher_cells_V3_plus"] is False
    assert run.results["completed_weights"] == [1, 2, 3, 4]
    assert run.results["failed_weights"] == []
    assert run.results["skipped_weights"] == []
    assert run.results["checks"]["all_completed_weights_passed"] is True

    weight_4 = next(
        record for record in run.by_weight["weights"] if record["weight"] == 4
    )
    assert weight_4["dim_H1_old"] == 8
    assert weight_4["number_of_new_s_cells"] == 8
    assert weight_4["checks"]["d2_old_matrix_times_d1_matrix_is_zero"] is True
    assert weight_4["checks"]["all_cell_certificates_valid"] is True

    cells = run.v2_cells["cells"]
    assert len(cells) == 8
    assert [cell["name"] for cell in cells] == [
        f"s2_{index:05d}_w4" for index in range(1, 9)
    ]
    assert all(cell["degree"] == 2 for cell in cells)
    assert all(cell["weight"] == 4 for cell in cells)
    assert all(cell["d1_z_normal_form"] == "0" for cell in cells)
    assert all(cell["boundary_remainder_nonzero"] for cell in cells)
    assert all(cell["not_in_B_old"] for cell in cells)
    assert all(cell["certificate_type"] == "rref_remainder" for cell in cells)

    assert "Q$ is not applied" in run.tex_report
    assert "The layers $V_3,V_4,\\ldots$ are not constructed." in run.tex_report
    assert report_language_has_no_forbidden_global_phrasing(run.tex_report)


def test_force_recompute_weights_ignores_valid_checkpoint(tmp_path) -> None:
    compute_exp011(
        max_weight=1,
        mode="dry",
        output_dir=tmp_path,
        thresholds=Exp011Thresholds(),
    )

    run = compute_exp011(
        max_weight=1,
        mode="dry",
        output_dir=tmp_path,
        thresholds=Exp011Thresholds(),
        resume=True,
        force_recompute_weights=(1,),
    )

    assert run.results["force_recompute_weights"] == [1]
    assert "force recompute weights: [1]" in run.log_text
    assert "weight 1: completed from checkpoint" not in run.log_text


def test_sparse_modular_rank_certifies_fractional_rank() -> None:
    rows = (
        {0: Fraction(1, 2), 1: Fraction(1, 3)},
        {0: Fraction(1, 2), 1: Fraction(2, 3)},
        {0: 1, 1: 1},
    )

    assert sparse_modular_rank(rows, prime=1_000_003) == 2
    assert sparse_modular_rank(rows, prime=1_000_003, max_rank=1) == 1
