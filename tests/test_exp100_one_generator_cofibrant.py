from pathlib import Path

from jordan_qh.one_generator_cofibrant import (
    EXP100_ID,
    compute_exp100,
    expected_setup,
    report_language_has_no_forbidden_global_phrasing,
    write_run_outputs,
)


def test_expected_setup_does_not_prefill_computed_cells() -> None:
    setup = expected_setup()

    assert setup["experiment"] == EXP100_ID
    assert setup["status"] == "expected_setup"
    assert setup["applies_Q"] is False
    assert "computed_V1_cells" in setup["do_not_prefill"]
    assert "computed_V2_cells" in setup["do_not_prefill"]
    assert "predicted_minimal_cell_table" in setup["do_not_prefill"]
    assert "cell_generators" not in setup
    assert "new_cell_generators_by_weight" not in setup
    assert "raw_cycle_counts_by_weight" not in setup


def test_exp100_computes_v1_and_v2_from_certified_linear_algebra(
    tmp_path: Path,
) -> None:
    run = compute_exp100(max_weight=10, output_dir=tmp_path)

    assert run.results["experiment_id"] == EXP100_ID
    assert run.results["passed"] is True
    assert run.results["applies_Q"] is False
    assert run.results["constructs_higher_cells_V3_plus"] is False
    assert run.results["completed_weights"] == list(range(1, 11))
    assert run.results["failed_weights"] == []
    assert run.results["skipped_weights"] == []
    assert run.results["checks"]["all_completed_weights_passed"] is True
    assert run.results["checks"]["expected_setup_has_no_prefilled_results"] is True

    assert run.results["computed_V0_cells"] == [
        {
            "name": "x",
            "layer": "V0",
            "degree": 0,
            "weight": 1,
            "maps_to": "x_bar",
            "source": "computed presentation generator",
        },
    ]
    assert run.results["computed_V1_cells"]
    assert run.results["computed_V2_cells"]
    assert all(
        cell["kernel_certificate"]["maps_to_kernel"]
        for cell in run.results["computed_V1_cells"]
    )
    assert all(
        cell["cycle_certificate"]["is_cycle"]
        for cell in run.results["computed_V2_cells"]
    )
    assert all(
        cell["non_boundary_certificate"]["boundary_remainder_nonzero"]
        for cell in run.results["computed_V2_cells"]
    )

    for record in run.by_weight["weights"]:
        if record["status"] != "completed":
            continue
        assert record["checks"]["d2_old_matrix_times_d1_matrix_is_zero"] is True
        assert record["checks"]["dim_H1_old_matches_V2_count"] is True
        assert len(record["computed_V2_cell_names"]) == record["dim_H1_old"]

    assert report_language_has_no_forbidden_global_phrasing(run.tex_report)


def test_exp100_writes_expected_results_data_report_and_log(tmp_path: Path) -> None:
    run = compute_exp100(max_weight=4, output_dir=tmp_path)
    write_run_outputs(run, tmp_path)

    assert (tmp_path / "expected.json").exists()
    assert (tmp_path / "results.json").exists()
    assert (tmp_path / "data" / "by_weight_W4.json").exists()
    assert (tmp_path / "data" / "cells_W4.json").exists()
    assert (
        tmp_path
        / "tex"
        / "exp100_square_zero_nonunital_cofibrant_weight10.tex"
    ).exists()
    assert (tmp_path / "logs" / "run_W4.log").exists()
