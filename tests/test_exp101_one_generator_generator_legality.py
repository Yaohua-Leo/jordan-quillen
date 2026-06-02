from pathlib import Path

from jordan_qh.one_generator_cofibrant import compute_exp100, write_run_outputs
from jordan_qh.one_generator_generator_legality import (
    EXP101_ID,
    compute_exp101,
    report_language_has_no_forbidden_exp101_phrasing,
    write_exp101_outputs,
)


def _reference_paths(tmp_path: Path) -> tuple[Path, Path]:
    reference_dir = tmp_path / "exp100_reference"
    reference_run = compute_exp100(max_weight=10, output_dir=reference_dir)
    write_run_outputs(reference_run, reference_dir)
    return (
        reference_dir / "data" / "cells_W10.json",
        reference_dir / "results.json",
    )


def test_exp101_validates_v1_generators_and_records_v2_obstructions(
    tmp_path: Path,
) -> None:
    reference_cells, reference_results = _reference_paths(tmp_path)

    run = compute_exp101(
        max_weight=12,
        output_dir=tmp_path / "exp101",
        reference_cells=reference_cells,
        reference_results=reference_results,
    )

    assert run.results["experiment_id"] == EXP101_ID
    assert run.results["passed"] is True
    assert run.results["applies_Q"] is False
    assert run.results["constructs_V3_plus"] is False
    assert run.results["v1_candidate_count"] == 3
    assert run.results["v1_legal_generator_count"] == 3
    assert run.results["v2_candidate_count"] == 5
    assert run.results["v2_strictly_attachable_cell_count"] == 0
    assert run.results["homology_killing_claim_count"] == 0

    assert all(
        record["legal_through_weight"]
        for record in run.v1_legality["cells"]
    )
    assert all(
        record["generator_level_cycle"]
        for record in run.v2_strict_attachability["cells"]
    )


def test_exp101_records_known_first_strict_v2_defects(tmp_path: Path) -> None:
    reference_cells, reference_results = _reference_paths(tmp_path)

    run = compute_exp101(
        max_weight=12,
        output_dir=tmp_path / "exp101",
        reference_cells=reference_cells,
        reference_results=reference_results,
    )

    by_name = {
        record["cell_name"]: record
        for record in run.v2_strict_attachability["cells"]
    }
    first = by_name["s2_00001_w4"]["first_defect"]
    assert first["target_weight"] == 6
    assert first["multiplier"] == "(x*x)"
    assert first["defect_nonzero"] is True
    assert (
        first["defect_normal_form"]
        == "(((x*x)*(x*x))*(x*x)) - (((x*x)*x)*((x*x)*x))"
    )

    weight_10_names = {"s2_00004_w10", "s2_00005_w10"}
    for name in weight_10_names:
        defect = by_name[name]["first_defect"]
        assert defect["target_weight"] == 11
        assert defect["multiplier"] == "x"
        assert defect["defect_nonzero"] is True


def test_exp101_chain_condition_and_report_boundary(tmp_path: Path) -> None:
    reference_cells, reference_results = _reference_paths(tmp_path)

    run = compute_exp101(
        max_weight=12,
        output_dir=tmp_path / "exp101",
        reference_cells=reference_cells,
        reference_results=reference_results,
    )

    assert all(
        record["d2_matrix_times_d1_matrix_is_zero"]
        for record in run.chain_audit["weights"]
    )
    assert "does not apply $Q$" in run.tex_report
    assert "does not construct $V_3,V_4,\\ldots$" in run.tex_report
    assert "makes no homology killing claim" in run.tex_report
    assert report_language_has_no_forbidden_exp101_phrasing(run.tex_report)


def test_exp101_writes_outputs(tmp_path: Path) -> None:
    reference_cells, reference_results = _reference_paths(tmp_path)
    output_dir = tmp_path / "exp101"

    run = compute_exp101(
        max_weight=12,
        output_dir=output_dir,
        reference_cells=reference_cells,
        reference_results=reference_results,
    )
    write_exp101_outputs(run, output_dir)

    assert (output_dir / "results.json").exists()
    assert (output_dir / "data" / "v1_legality_W12.json").exists()
    assert (output_dir / "data" / "v2_strict_attachability_W12.json").exists()
    assert (output_dir / "data" / "chain_audit_W12.json").exists()
    assert (
        output_dir
        / "tex"
        / "exp101_one_generator_generator_legality_audit.tex"
    ).exists()
    assert (output_dir / "logs" / "run_W12.log").exists()
