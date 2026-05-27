from fractions import Fraction

from jordan_qh.h1_presentation_stress import (
    EXP010_ID,
    canonical_sym2_matrix,
    exp010_results,
    render_latex_report,
)


def _case(results: dict, case_id: str) -> dict:
    return {case["case_id"]: case for case in results["cases"]}[case_id]


def test_exp010_mvp_distinguishes_stable_h1_from_missing_syzygy() -> None:
    results = exp010_results()

    assert results["experiment"] == EXP010_ID
    assert results["summary"]["minimum_passed"] is True
    assert results["summary"]["evidence_only"] is True
    assert results["summary"]["claim_files_modified"] is False

    minimal = _case(results, "A_minimal_presentation")
    assert minimal["outcome"] == "pass_strong"
    assert minimal["dim_H1"] == 3
    assert minimal["basis_alignment_passed"] is True

    naive = _case(results, "C_redundant_relation_without_syzygy")
    assert naive["outcome"] == "expected_fail_observed"
    assert naive["is_expected_fail_control"] is True
    assert naive["dim_H1"] == 4
    assert naive["basis_alignment_passed"] is False

    repaired = _case(results, "D_redundant_relation_with_syzygy")
    assert repaired["outcome"] == "pass_strong"
    assert repaired["rank_partial_2_Q"] == 1
    assert repaired["dim_H1"] == 3
    assert repaired["basis_alignment_passed"] is True


def test_exp010_records_truncation_depth_h1_pattern() -> None:
    results = exp010_results()
    truncation = _case(results, "F_truncation_depth_diagnostic")

    assert truncation["outcome"] == "pass_strong"
    assert truncation["h1_by_depth"] == {
        "minimal_presentation": {"N=1": 3, "N=2": 3, "N=3": 3},
        "redundant_without_syzygy": {"N=1": 4, "N=2": 4, "N=3": 4},
        "redundant_with_syzygy": {"N=1": 4, "N=2": 3, "N=3": 3},
    }


def test_exp010_gl2_cases_match_exact_sym2_matrices() -> None:
    results = exp010_results()

    for label, matrix in {
        "g1": ((1, 1), (1, -1)),
        "g2": ((1, 2), (0, 1)),
        "g3": ((2, 1), (1, 1)),
    }.items():
        case = _case(results, f"B_linear_change_{label}")
        expected = canonical_sym2_matrix(matrix)
        assert case["outcome"] == "pass_strong"
        assert case["sym2_check"]["passed"] is True
        assert case["sym2_check"]["expected_sym2_matrix_source_rows"] == expected
        assert case["sym2_check"]["observed_h1_basis_matrix_source_rows"] == expected


def test_exp010_multiple_redundant_relations_are_killed_by_matching_syzygies() -> None:
    results = exp010_results()

    for m in (1, 2, 3, 5):
        case = _case(results, f"E_multiple_redundant_relations_m{m}")
        assert case["outcome"] == "pass_strong"
        assert case["dim_C1"] == 3 + m
        assert case["rank_partial_2_Q"] == m
        assert case["dim_H1"] == 3
        assert case["basis_alignment_passed"] is True


def test_exp010_sym2_matrix_uses_source_rows_target_coordinates() -> None:
    assert canonical_sym2_matrix(((1, 2), (0, 1))) == (
        (Fraction(1), Fraction(4), Fraction(4)),
        (Fraction(0), Fraction(1), Fraction(2)),
        (Fraction(0), Fraction(0), Fraction(1)),
    )


def test_exp010_latex_report_summarizes_results_without_overclaiming() -> None:
    tex = render_latex_report(exp010_results())

    assert "\\title{Experiment 010: H1 Presentation-Stress Report}" in tex
    assert "\\href{results.json}{\\texttt{results.json}}" in tex
    assert "C\\_redundant\\_relation\\_without\\_syzygy" in tex
    assert "expected\\_fail\\_observed" in tex
    assert "false extra $H_1$ class" in tex
    assert "does not prove presentation invariance" in tex
    assert "E\\_multiple\\_redundant\\_relations\\_m5" in tex
