"""Experiment 010 H1 presentation-stress diagnostics."""

from __future__ import annotations

from collections.abc import Sequence
from fractions import Fraction
from typing import Any

from jordan_qh.chain_complex import (
    FiniteChainComplex,
    MatrixRows,
    analyze_homology,
    kernel_basis,
    row_space_basis,
)
from jordan_qh.linear_algebra import row_rank

EXP010_ID = "EXP-010-h1-stability-square-zero-two-generator"
SOURCE_PLAN = "researchplan/subplan010.md"
BASE_FIELD = "QQ"
CATEGORY = "nonunital Jordan algebras"
TARGET_ALGEBRA = "k{x,y}/(x^2, xy, y^2)"
C0_BASIS = ("x", "y")
CANONICAL_RELATION_BASIS = ("x^2", "xy", "y^2")
MINIMAL_RELATION_CELL_BASIS = ("r_xx", "r_xy", "r_yy")
MATRIX_CONVENTION = "source_rows_target_coordinates"
EXPECTED_STABLE_DIM_H1 = 3
OUTCOME_STATUSES = (
    "pass_strong",
    "pass_weak_dimension_only",
    "expected_fail_observed",
    "unexpected_fail",
    "unexpected_pass",
)

ZERO_PARTIAL_1_MINIMAL = (
    (Fraction(0), Fraction(0)),
    (Fraction(0), Fraction(0)),
    (Fraction(0), Fraction(0)),
)
IDENTITY_RHO = (
    (Fraction(1), Fraction(0), Fraction(0)),
    (Fraction(0), Fraction(1), Fraction(0)),
    (Fraction(0), Fraction(0), Fraction(1)),
)
REDUNDANT_Q_ROW = (Fraction(1), Fraction(2), Fraction(1))
MULTIPLE_REDUNDANT_ROWS = (
    (Fraction(1), Fraction(2), Fraction(1)),
    (Fraction(1), Fraction(0), Fraction(-1)),
    (Fraction(2), Fraction(1), Fraction(0)),
    (Fraction(0), Fraction(1), Fraction(3)),
    (Fraction(-1), Fraction(1), Fraction(1)),
)
GL2_MATRICES = {
    "g1": ((Fraction(1), Fraction(1)), (Fraction(1), Fraction(-1))),
    "g2": ((Fraction(1), Fraction(2)), (Fraction(0), Fraction(1))),
    "g3": ((Fraction(2), Fraction(1)), (Fraction(1), Fraction(1))),
}


def exp010_results() -> dict[str, Any]:
    """Return the complete Experiment 010 result object."""
    cases = [
        minimal_presentation_case(),
        redundant_without_syzygy_case(),
        redundant_with_syzygy_case(),
        truncation_depth_case(),
        *linear_change_cases(),
        *multiple_redundant_relation_cases(),
    ]
    case_by_id = {case["case_id"]: case for case in cases}
    minimum_ids = (
        "A_minimal_presentation",
        "C_redundant_relation_without_syzygy",
        "D_redundant_relation_with_syzygy",
        "F_truncation_depth_diagnostic",
    )
    extended_ids = tuple(
        case["case_id"]
        for case in cases
        if case["case_group"]
        in {"B_linear_change_of_generators", "E_multiple_redundant_relations"}
    )
    minimum_passed = (
        case_by_id["A_minimal_presentation"]["outcome"] == "pass_strong"
        and case_by_id["C_redundant_relation_without_syzygy"]["outcome"]
        == "expected_fail_observed"
        and case_by_id["D_redundant_relation_with_syzygy"]["outcome"] == "pass_strong"
        and case_by_id["F_truncation_depth_diagnostic"]["outcome"] == "pass_strong"
    )
    full_stress_test_passed = minimum_passed and all(
        case_by_id[case_id]["outcome"] == "pass_strong"
        for case_id in extended_ids
    )
    return {
        "status": "run",
        "passed": full_stress_test_passed,
        "experiment": EXP010_ID,
        "plan": SOURCE_PLAN,
        "base_field": BASE_FIELD,
        "category": CATEGORY,
        "target_algebra": TARGET_ALGEBRA,
        "focus": "low-degree H1 presentation-stress diagnostic",
        "matrix_convention": MATRIX_CONVENTION,
        "canonical_relation_basis": CANONICAL_RELATION_BASIS,
        "minimal_relation_cell_basis": MINIMAL_RELATION_CELL_BASIS,
        "expected_stable_dim_H1": EXPECTED_STABLE_DIM_H1,
        "outcome_statuses": OUTCOME_STATUSES,
        "cases": cases,
        "summary": {
            "minimum_passed": minimum_passed,
            "full_stress_test_passed": full_stress_test_passed,
            "minimum_case_ids": minimum_ids,
            "extended_case_ids": extended_ids,
            "evidence_only": True,
            "claim_files_modified": False,
            "interpretation": _interpretation(full_stress_test_passed, minimum_passed),
        },
        "limitations": (
            "This is a bounded low-degree diagnostic for one square-zero "
            "example. It supports H1 stability under the listed presentation "
            "stresses but does not prove presentation invariance."
        ),
    }


def minimal_presentation_case() -> dict[str, Any]:
    """Return Group A, the minimal presentation baseline."""
    return _presentation_case(
        case_id="A_minimal_presentation",
        case_group="A_minimal_presentation_baseline",
        c1_basis=MINIMAL_RELATION_CELL_BASIS,
        c2_basis=(),
        partial_2_rows=(),
        rho_rows=IDENTITY_RHO,
        expected_dim_h1=3,
        required_rank_partial_2=0,
    )


def redundant_without_syzygy_case() -> dict[str, Any]:
    """Return Group C, the expected-fail missing-syzygy control."""
    c1_basis = (*MINIMAL_RELATION_CELL_BASIS, "r_q")
    rho_rows = (*IDENTITY_RHO, REDUNDANT_Q_ROW)
    return _presentation_case(
        case_id="C_redundant_relation_without_syzygy",
        case_group="C_naive_redundant_relation_control",
        c1_basis=c1_basis,
        c2_basis=(),
        partial_2_rows=(),
        rho_rows=rho_rows,
        expected_dim_h1=4,
        required_rank_partial_2=0,
        is_expected_fail_control=True,
    )


def redundant_with_syzygy_case() -> dict[str, Any]:
    """Return Group D, the repaired redundant-relation case."""
    c1_basis = (*MINIMAL_RELATION_CELL_BASIS, "r_q")
    rho_rows = (*IDENTITY_RHO, REDUNDANT_Q_ROW)
    return _presentation_case(
        case_id="D_redundant_relation_with_syzygy",
        case_group="D_repaired_redundant_relation",
        c1_basis=c1_basis,
        c2_basis=("s_q",),
        partial_2_rows=((Fraction(-1), Fraction(-2), Fraction(-1), Fraction(1)),),
        rho_rows=rho_rows,
        expected_dim_h1=3,
        required_rank_partial_2=1,
    )


def truncation_depth_case() -> dict[str, Any]:
    """Return Group F, the truncation-depth diagnostic for H1."""
    minimal = minimal_presentation_case()
    naive = redundant_without_syzygy_case()
    repaired = redundant_with_syzygy_case()
    h1_by_depth = {
        "minimal_presentation": {
            "N=1": _h1_at_depth(minimal, include_c2=False),
            "N=2": _h1_at_depth(minimal, include_c2=True),
            "N=3": _h1_at_depth(minimal, include_c2=True),
        },
        "redundant_without_syzygy": {
            "N=1": _h1_at_depth(naive, include_c2=False),
            "N=2": _h1_at_depth(naive, include_c2=True),
            "N=3": _h1_at_depth(naive, include_c2=True),
        },
        "redundant_with_syzygy": {
            "N=1": _h1_at_depth(repaired, include_c2=False),
            "N=2": _h1_at_depth(repaired, include_c2=True),
            "N=3": _h1_at_depth(repaired, include_c2=True),
        },
    }
    expected = {
        "minimal_presentation": {"N=1": 3, "N=2": 3, "N=3": 3},
        "redundant_without_syzygy": {"N=1": 4, "N=2": 4, "N=3": 4},
        "redundant_with_syzygy": {"N=1": 4, "N=2": 3, "N=3": 3},
    }
    case = dict(repaired)
    case.update(
        {
            "case_id": "F_truncation_depth_diagnostic",
            "case_group": "F_truncation_depth_diagnostic",
            "outcome": "pass_strong" if h1_by_depth == expected else "unexpected_fail",
            "h1_by_depth": h1_by_depth,
            "expected_h1_by_depth": expected,
            "truncation_depth_pattern_passed": h1_by_depth == expected,
        }
    )
    return case


def linear_change_cases() -> tuple[dict[str, Any], ...]:
    """Return Group B, deterministic GL2(QQ) generator changes."""
    cases: list[dict[str, Any]] = []
    for label, matrix in GL2_MATRICES.items():
        c1_basis = (f"r_{label}_u2", f"r_{label}_uv", f"r_{label}_v2")
        expected_sym2 = canonical_sym2_matrix(matrix)
        case = _presentation_case(
            case_id=f"B_linear_change_{label}",
            case_group="B_linear_change_of_generators",
            c1_basis=c1_basis,
            c2_basis=(),
            partial_2_rows=(),
            rho_rows=expected_sym2,
            expected_dim_h1=3,
            required_rank_partial_2=0,
        )
        observed = _representatives_to_relation_matrix(
            case["H1_representatives_source_rows"],
            expected_sym2,
        )
        sym2_passed = observed == expected_sym2
        case["sym2_check"] = {
            "generator_change_matrix": matrix,
            "expected_sym2_matrix_source_rows": expected_sym2,
            "observed_h1_basis_matrix_source_rows": observed,
            "passed": sym2_passed,
        }
        if case["dim_H1"] == 3 and sym2_passed:
            case["outcome"] = "pass_strong"
        elif case["dim_H1"] == 3:
            case["outcome"] = "pass_weak_dimension_only"
        else:
            case["outcome"] = "unexpected_fail"
        cases.append(case)
    return tuple(cases)


def multiple_redundant_relation_cases() -> tuple[dict[str, Any], ...]:
    """Return Group E, prefixes of repaired redundant quadratic relations."""
    cases: list[dict[str, Any]] = []
    for m in (1, 2, 3, 5):
        redundant_rows = MULTIPLE_REDUNDANT_ROWS[:m]
        c1_basis = (
            *MINIMAL_RELATION_CELL_BASIS,
            *(f"r_q_{index}" for index in range(1, m + 1)),
        )
        c2_basis = tuple(f"s_q_{index}" for index in range(1, m + 1))
        partial_2_rows = tuple(
            (
                -row[0],
                -row[1],
                -row[2],
                *(
                    Fraction(1) if index == row_index else Fraction(0)
                    for index in range(m)
                ),
            )
            for row_index, row in enumerate(redundant_rows)
        )
        case = _presentation_case(
            case_id=f"E_multiple_redundant_relations_m{m}",
            case_group="E_multiple_redundant_relations",
            c1_basis=c1_basis,
            c2_basis=c2_basis,
            partial_2_rows=partial_2_rows,
            rho_rows=(*IDENTITY_RHO, *redundant_rows),
            expected_dim_h1=3,
            required_rank_partial_2=m,
        )
        cases.append(case)
    return tuple(cases)


def canonical_sym2_matrix(
    matrix: Sequence[Sequence[int | Fraction]],
) -> MatrixRows:
    """Return the source-row Sym^2 matrix for a GL2 generator change."""
    (a_raw, b_raw), (c_raw, d_raw) = matrix
    a = Fraction(a_raw)
    b = Fraction(b_raw)
    c = Fraction(c_raw)
    d = Fraction(d_raw)
    return (
        (a * a, 2 * a * b, b * b),
        (a * c, a * d + b * c, b * d),
        (c * c, 2 * c * d, d * d),
    )


def render_markdown_report(results: dict[str, Any]) -> str:
    """Render a concise Markdown report from the Experiment 010 result object."""
    rows = [
        "| Case | Group | Outcome | dim H1 | Certificate |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for case in results["cases"]:
        certificate = "yes" if case.get("basis_alignment_passed") else "no"
        if case.get("sym2_check"):
            certificate = "yes" if case["sym2_check"]["passed"] else "no"
        rows.append(
            "| {case_id} | {group} | {outcome} | {dim_h1} | {certificate} |".format(
                case_id=case["case_id"],
                group=case["case_group"],
                outcome=case["outcome"],
                dim_h1=case["dim_H1"],
                certificate=certificate,
            )
        )
    return "\n".join(
        [
            "# Experiment 010 Report",
            "",
            f"Plan: `{results['plan']}`",
            "",
            "This report summarizes the same in-memory result object written to "
            "`results.json`. It is computational evidence only and does not "
            "claim presentation invariance.",
            "",
            "## Conventions",
            "",
            f"- Base field: `{results['base_field']}`",
            f"- Category: `{results['category']}`",
            f"- Target algebra: `{results['target_algebra']}`",
            f"- Matrix convention: `{results['matrix_convention']}`",
            "- Canonical relation basis: "
            + ", ".join(f"`{item}`" for item in results["canonical_relation_basis"]),
            "",
            "## Outcome Statuses",
            "",
            ", ".join(f"`{status}`" for status in results["outcome_statuses"]),
            "",
            "## Diagnostics",
            "",
            *rows,
            "",
            "## Truncation Depth",
            "",
            "```text",
            _format_truncation_case(results),
            "```",
            "",
            "## Limitations",
            "",
            results["limitations"],
            "",
            "## Interpretation",
            "",
            results["summary"]["interpretation"],
            "",
        ]
    )


def render_latex_report(results: dict[str, Any]) -> str:
    """Render a concise LaTeX report from the Experiment 010 result object."""
    return "\n".join(
        [
            r"\documentclass[11pt]{article}",
            r"\usepackage[T1]{fontenc}",
            r"\usepackage{amsmath,amssymb}",
            r"\usepackage{booktabs}",
            r"\usepackage{geometry}",
            r"\usepackage[hidelinks]{hyperref}",
            r"\geometry{margin=1in}",
            "",
            r"\title{Experiment 010: H1 Presentation-Stress Report}",
            r"\author{Generated by run.py}",
            r"\date{}",
            "",
            r"\begin{document}",
            r"\maketitle",
            "",
            r"\section{Audit Data}",
            "This TeX file is a compact report generated from the same "
            "in-memory result object written to "
            r"\href{results.json}{\texttt{results.json}}.  It is "
            "computational evidence only and does not prove presentation "
            "invariance.",
            "",
            r"\section{Conventions}",
            r"\begin{itemize}",
            r"\item Base field: \(\mathbb{Q}\).",
            rf"\item Category: \texttt{{{_latex_escape(results['category'])}}}.",
            rf"\item Target algebra: \(J={_target_algebra_latex()}\).",
            r"\item Matrix convention: source rows, target coordinates.",
            r"\item Canonical relation basis: "
            r"\((x^2,\ xy,\ y^2)\).",
            r"\item Minimal relation cells: "
            r"\((r_{xx},\ r_{xy},\ r_{yy})\).",
            r"\end{itemize}",
            "",
            r"\section{Outcome Summary}",
            _latex_case_table(results["cases"]),
            "",
            r"\section{MVP Diagnostics}",
            _latex_mvp_summary(results),
            "",
            r"\section{Extended Stress Tests}",
            _latex_extended_summary(results),
            "",
            r"\section{Truncation Depth}",
            _latex_truncation_table(results),
            "",
            r"\section{Basis-Alignment Certificates}",
            "For redundant-relation cases, the strong certificate checks "
            r"\(\operatorname{im}(\partial_2^Q)=\ker(\rho)\) exactly over "
            r"\(\mathbb{Q}\).  The naive control intentionally omits the "
            "syzygy, so the kernel of \\(\\rho\\) is not killed and the "
            "false extra $H_1$ class remains.",
            "",
            _latex_certificate_table(results["cases"]),
            "",
            r"\section{Limitations}",
            _latex_escape(results["limitations"]),
            "",
            r"\section{Interpretation}",
            _latex_escape(results["summary"]["interpretation"]),
            "",
            r"\end{document}",
            "",
        ]
    )


def to_jsonable(value: Any) -> Any:
    """Convert exact Python objects in a result record to JSON-safe values."""
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return value.numerator
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, tuple | list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    return value


def _presentation_case(
    *,
    case_id: str,
    case_group: str,
    c1_basis: tuple[str, ...],
    c2_basis: tuple[str, ...],
    partial_2_rows: MatrixRows,
    rho_rows: MatrixRows,
    expected_dim_h1: int,
    required_rank_partial_2: int,
    is_expected_fail_control: bool = False,
) -> dict[str, Any]:
    partial_1_rows = tuple(
        (Fraction(0), Fraction(0)) for _ in c1_basis
    )
    complex_ = FiniteChainComplex(
        bases={0: C0_BASIS, 1: c1_basis, 2: c2_basis},
        differentials={1: partial_1_rows, 2: partial_2_rows},
    )
    homology = analyze_homology(complex_, max_degree=1)
    rank_partial_2 = row_rank(partial_2_rows, len(c1_basis))
    image_partial_2 = row_space_basis(partial_2_rows, len(c1_basis))
    kernel_rho = kernel_basis(
        rho_rows,
        source_dimension=len(c1_basis),
        target_dimension=len(CANONICAL_RELATION_BASIS),
    )
    basis_alignment_passed = _same_subspace(
        image_partial_2,
        kernel_rho,
        dimension=len(c1_basis),
    )
    dim_h1 = homology[1].homology_dimension
    rank_ok = rank_partial_2 == required_rank_partial_2
    if is_expected_fail_control:
        outcome = (
            "expected_fail_observed"
            if dim_h1 == expected_dim_h1 and not basis_alignment_passed
            else "unexpected_pass"
        )
    elif dim_h1 == expected_dim_h1 and rank_ok and basis_alignment_passed:
        outcome = "pass_strong"
    elif dim_h1 == expected_dim_h1:
        outcome = "pass_weak_dimension_only"
    else:
        outcome = "unexpected_fail"
    return {
        "case_id": case_id,
        "case_group": case_group,
        "outcome": outcome,
        "is_expected_fail_control": is_expected_fail_control,
        "C0_basis": C0_BASIS,
        "C1_basis": c1_basis,
        "C2_basis": c2_basis,
        "dim_C0": len(C0_BASIS),
        "dim_C1": len(c1_basis),
        "dim_C2": len(c2_basis),
        "partial_1_Q_source_rows": partial_1_rows,
        "partial_2_Q_source_rows": partial_2_rows,
        "rank_partial_1_Q": homology[1].boundary_rank,
        "rank_partial_2_Q": rank_partial_2,
        "dim_H0": homology[0].homology_dimension,
        "dim_H1": dim_h1,
        "H1_representatives_source_rows": homology[1].homology_representatives,
        "H1_representative_formulas": tuple(
            _vector_to_basis_expr(row, c1_basis)
            for row in homology[1].homology_representatives
        ),
        "relation_coefficient_map_source_rows": rho_rows,
        "basis_alignment_passed": basis_alignment_passed,
        "basis_alignment_certificate": {
            "image_partial_2_basis": image_partial_2,
            "kernel_rho_basis": kernel_rho,
            "image_partial_2_equals_kernel_rho": basis_alignment_passed,
        },
        "d_squared_zero": complex_.d_squared_zero(),
    }


def _h1_at_depth(case: dict[str, Any], *, include_c2: bool) -> int:
    c1_basis = case["C1_basis"]
    c2_basis = case["C2_basis"] if include_c2 else ()
    partial_2_rows = case["partial_2_Q_source_rows"] if include_c2 else ()
    partial_1_rows = tuple(
        (Fraction(0), Fraction(0)) for _ in c1_basis
    )
    complex_ = FiniteChainComplex(
        bases={0: C0_BASIS, 1: c1_basis, 2: c2_basis},
        differentials={1: partial_1_rows, 2: partial_2_rows},
    )
    return analyze_homology(complex_, max_degree=1)[1].homology_dimension


def _same_subspace(
    left_basis: MatrixRows,
    right_basis: MatrixRows,
    *,
    dimension: int,
) -> bool:
    left_rank = row_rank(left_basis, dimension)
    right_rank = row_rank(right_basis, dimension)
    combined_rank = row_rank((*left_basis, *right_basis), dimension)
    return left_rank == right_rank == combined_rank


def _representatives_to_relation_matrix(
    representatives: MatrixRows,
    rho_rows: MatrixRows,
) -> MatrixRows:
    rows: list[tuple[Fraction, ...]] = []
    for representative in representatives:
        target = [Fraction(0) for _ in CANONICAL_RELATION_BASIS]
        for coefficient, rho_row in zip(representative, rho_rows, strict=True):
            for index, entry in enumerate(rho_row):
                target[index] += coefficient * entry
        rows.append(tuple(target))
    return tuple(rows)


def _vector_to_basis_expr(row: tuple[Fraction, ...], basis: tuple[str, ...]) -> str:
    parts: list[str] = []
    for coefficient, name in zip(row, basis, strict=True):
        if coefficient == 0:
            continue
        if coefficient == 1:
            parts.append(name)
        elif coefficient == -1:
            parts.append(f"-{name}")
        else:
            parts.append(f"{coefficient}*{name}")
    if not parts:
        return "0"
    return " + ".join(parts).replace("+ -", "- ")


def _format_truncation_case(results: dict[str, Any]) -> str:
    case = next(
        item
        for item in results["cases"]
        if item["case_id"] == "F_truncation_depth_diagnostic"
    )
    return "\n".join(
        f"{name}: {values}" for name, values in case["h1_by_depth"].items()
    )


def _latex_case_table(cases: list[dict[str, Any]]) -> str:
    rows = [
        r"\begin{center}",
        r"\scriptsize",
        r"\begin{tabular}{p{0.42\linewidth}p{0.21\linewidth}rrc}",
        r"\toprule",
        r"Case & Outcome & \(\dim C_1\) & \(\dim H_1\) & Cert. \\",
        r"\midrule",
    ]
    for case in cases:
        rows.append(
            r"\texttt{"
            + _latex_escape(case["case_id"])
            + "} & \\texttt{"
            + _latex_escape(case["outcome"])
            + f"}} & {case['dim_C1']} & {case['dim_H1']} & "
            + ("yes" if _case_certificate_passed(case) else "no")
            + r" \\"
        )
    rows.extend([r"\bottomrule", r"\end{tabular}", r"\end{center}"])
    return "\n".join(rows)


def _latex_mvp_summary(results: dict[str, Any]) -> str:
    cases = {case["case_id"]: case for case in results["cases"]}
    minimal = cases["A_minimal_presentation"]
    naive = cases["C_redundant_relation_without_syzygy"]
    repaired = cases["D_redundant_relation_with_syzygy"]
    minimum = results["summary"]["minimum_passed"]
    return "\n".join(
        [
            r"\begin{itemize}",
            r"\item Minimal presentation: "
            + f"outcome \\texttt{{{_latex_escape(minimal['outcome'])}}}, "
            + rf"\(\dim H_1={minimal['dim_H1']}\).",
            r"\item Naive redundant-relation control: "
            + f"outcome \\texttt{{{_latex_escape(naive['outcome'])}}}, "
            + rf"\(\dim H_1={naive['dim_H1']}\).  This is the planned "
            "false extra $H_1$ class.",
            r"\item Repaired redundant relation: "
            + f"outcome \\texttt{{{_latex_escape(repaired['outcome'])}}}, "
            + r"\(\operatorname{rank}\partial_2^Q="
            + f"{repaired['rank_partial_2_Q']}\\), "
            + rf"\(\dim H_1={repaired['dim_H1']}\).",
            r"\item Minimum passed: "
            + (r"\texttt{true}." if minimum else r"\texttt{false}."),
            r"\end{itemize}",
        ]
    )


def _latex_extended_summary(results: dict[str, Any]) -> str:
    gl2_rows = []
    redundant_rows = []
    for case in results["cases"]:
        if case["case_group"] == "B_linear_change_of_generators":
            gl2_rows.append(
                r"\texttt{"
                + _latex_escape(case["case_id"])
                + "} & "
                + f"\\texttt{{{_latex_escape(case['outcome'])}}} & "
                + ("yes" if case["sym2_check"]["passed"] else "no")
                + r" \\"
            )
        if case["case_group"] == "E_multiple_redundant_relations":
            redundant_rows.append(
                r"\texttt{"
                + _latex_escape(case["case_id"])
                + "} & "
                + str(case["rank_partial_2_Q"])
                + " & "
                + str(case["dim_H1"])
                + " & "
                + ("yes" if case["basis_alignment_passed"] else "no")
                + r" \\"
            )
    return "\n".join(
        [
            r"\subsection{Linear Changes Of Generators}",
            r"\begin{center}",
            r"\begin{tabular}{llc}",
            r"\toprule",
            r"Case & Outcome & \(\operatorname{Sym}^2(g)\) check \\",
            r"\midrule",
            *gl2_rows,
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{center}",
            "",
            r"\subsection{Multiple Redundant Relations}",
            r"\begin{center}",
            r"\begin{tabular}{lrrc}",
            r"\toprule",
            r"Case & \(\operatorname{rank}\partial_2^Q\) & "
            r"\(\dim H_1\) & Cert. \\",
            r"\midrule",
            *redundant_rows,
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{center}",
        ]
    )


def _latex_truncation_table(results: dict[str, Any]) -> str:
    truncation = next(
        case
        for case in results["cases"]
        if case["case_id"] == "F_truncation_depth_diagnostic"
    )
    rows = [
        r"\begin{center}",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Presentation model & \(N=1\) & \(N=2\) & \(N=3\) \\",
        r"\midrule",
    ]
    for name, values in truncation["h1_by_depth"].items():
        rows.append(
            r"\texttt{"
            + _latex_escape(name)
            + f"}} & {values['N=1']} & {values['N=2']} & {values['N=3']} \\\\"
        )
    rows.extend([r"\bottomrule", r"\end{tabular}", r"\end{center}"])
    return "\n".join(rows)


def _latex_certificate_table(cases: list[dict[str, Any]]) -> str:
    rows = [
        r"\begin{center}",
        r"\small",
        r"\begin{tabular}{p{0.44\linewidth}rrc}",
        r"\toprule",
        r"Case & \(\dim C_2\) & \(\operatorname{rank}\partial_2^Q\) & "
        r"\(\operatorname{im}\partial_2^Q=\ker\rho\) \\",
        r"\midrule",
    ]
    for case in cases:
        if case["case_group"] not in {
            "C_naive_redundant_relation_control",
            "D_repaired_redundant_relation",
            "E_multiple_redundant_relations",
        }:
            continue
        rows.append(
            r"\texttt{"
            + _latex_escape(case["case_id"])
            + f"}} & {case['dim_C2']} & {case['rank_partial_2_Q']} & "
            + ("yes" if case["basis_alignment_passed"] else "no")
            + r" \\"
        )
    rows.extend([r"\bottomrule", r"\end{tabular}", r"\end{center}"])
    return "\n".join(rows)


def _case_certificate_passed(case: dict[str, Any]) -> bool:
    if "sym2_check" in case:
        return bool(case["sym2_check"]["passed"])
    return bool(case["basis_alignment_passed"])


def _target_algebra_latex() -> str:
    return r"k\{x,y\}/(x^2,xy,y^2)"


def _latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "_": r"\_",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "^": r"\^{}",
        "~": r"\textasciitilde{}",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in value)


def _interpretation(full_passed: bool, minimum_passed: bool) -> str:
    if full_passed:
        return (
            "Experiment 010 supports the stability of the computed H1 for the "
            "two-generator square-zero Jordan algebra under deterministic "
            "linear generator changes and controlled redundant-relation "
            "refinements. The expected-fail control reproduces the false "
            "extra H1 class that appears when a redundant relation is added "
            "without the corresponding syzygy. This supports, but does not "
            "prove, the identification of the stable H1 with Sym^2(k^2) in "
            "this bounded example."
        )
    if minimum_passed:
        return (
            "Experiment 010-MVP supports the low-degree diagnosis that the "
            "two-generator square-zero example has stable H1 after the "
            "redundant-relation syzygy is included, and it reproduces the "
            "planned false extra H1 class when that syzygy is omitted. This "
            "is computational evidence, not a proof of presentation "
            "invariance."
        )
    return (
        "Experiment 010 did not meet the MVP acceptance criteria. Inspect "
        "the case outcomes before using it as evidence."
    )
