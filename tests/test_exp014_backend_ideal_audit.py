from jordan_qh.backend_ideal_audit import (
    EXP014_ID,
    compute_exp014,
    report_language_has_no_forbidden_exp014_phrasing,
)


def test_exp014_relation_rows_reduce_to_zero(tmp_path) -> None:
    run = compute_exp014(
        max_weight=4,
        max_degree=2,
        mode="dry",
        output_dir=tmp_path / "exp014",
        workers=1,
        max_memory_gb=20,
    )

    assert run.results["experiment_id"] == EXP014_ID
    assert run.results["applies_Q"] is False
    assert run.results["constructs_V3_plus"] is False
    assert run.results["relation_rows_checked"] > 0
    assert run.results["relation_reduction_failures"] == 0
    assert all(
        record["relation_reduces_to_zero"]
        for record in run.relation_stability["relation_records"]
    )


def test_exp014_records_multiplication_stability_defect(tmp_path) -> None:
    run = compute_exp014(
        max_weight=5,
        max_degree=2,
        mode="dry",
        output_dir=tmp_path / "exp014",
        workers=1,
        max_memory_gb=20,
    )

    assert run.results["multiplication_failures"] > 0
    first = run.first_failures["first_multiplication_failure"]
    assert first["source_degree"] == 0
    assert first["source_weight"] == 4
    assert first["relation_index"] == 0
    assert first["first_multiplication_defect"]["multiplier"] == "y"
    assert first["first_multiplication_defect"]["target_weight"] == 5
    assert first["first_multiplication_defect"]["defect_nonzero"] is True
    assert run.results["passed"] is False


def test_exp014_records_differential_stability_defect(tmp_path) -> None:
    run = compute_exp014(
        max_weight=6,
        max_degree=2,
        mode="dry",
        output_dir=tmp_path / "exp014",
        workers=1,
        max_memory_gb=20,
    )

    assert run.results["differential_failures"] > 0
    first = run.first_failures["first_differential_failure"]
    assert first["source_degree"] == 2
    assert first["source_weight"] == 6
    assert first["relation_index"] == 0
    assert first["first_differential_defect"]["target_degree"] == 1
    assert first["first_differential_defect"]["target_weight"] == 6
    assert first["first_differential_defect"]["defect_nonzero"] is True
    assert run.results["passed"] is False


def test_exp014_report_language_preserves_backend_audit_boundary(tmp_path) -> None:
    run = compute_exp014(
        max_weight=5,
        max_degree=2,
        mode="dry",
        output_dir=tmp_path / "exp014",
        workers=1,
        max_memory_gb=20,
    )

    assert "does not apply $Q$" in run.tex_report
    assert "does not construct $V_3,V_4,\\ldots$" in run.tex_report
    assert "bounded backend audit only" in run.tex_report
    assert report_language_has_no_forbidden_exp014_phrasing(run.tex_report)
