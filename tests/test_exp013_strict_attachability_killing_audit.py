import json
from pathlib import Path

from jordan_qh.low_weight_attachment_killing import (
    EXP013_ID,
    compute_exp013,
    report_language_has_no_forbidden_exp013_phrasing,
)
from jordan_qh.v2_cells_no_q import Exp011Thresholds, compute_exp011


def _reference_paths(tmp_path: Path) -> tuple[Path, Path]:
    reference_run = compute_exp011(
        max_weight=8,
        mode="dry",
        output_dir=tmp_path / "reference",
        thresholds=Exp011Thresholds(),
    )
    v2_path = tmp_path / "v2_cells_W8.json"
    by_weight_path = tmp_path / "by_weight_W8.json"
    v2_path.write_text(json.dumps(reference_run.v2_cells), encoding="utf-8")
    by_weight_path.write_text(json.dumps(reference_run.by_weight), encoding="utf-8")
    return v2_path, by_weight_path


def test_exp013_records_known_strict_attachability_obstruction(tmp_path) -> None:
    v2_path, by_weight_path = _reference_paths(tmp_path)

    run = compute_exp013(
        max_weight=5,
        mode="dry",
        output_dir=tmp_path / "exp013",
        reference_v2_cells=v2_path,
        reference_by_weight=by_weight_path,
        thresholds=Exp011Thresholds(),
    )

    assert run.results["experiment_id"] == EXP013_ID
    assert run.results["applies_Q"] is False
    assert run.results["constructs_V3_plus"] is False
    assert run.results["passed"] is True

    first_cell = run.strict_attachability["cells"][0]
    assert first_cell["cell_name"] == "s2_00001_w4"
    assert first_cell["strictly_attachable"] is False
    assert first_cell["first_defect"]["target_weight"] == 5
    assert first_cell["first_defect"]["multiplier"] == "x"
    assert first_cell["first_defect"]["defect_nonzero"] is True
    assert (
        first_cell["first_defect"]["defect_normal_form"]
        == "-3/2*((((x*x)*y)*x)*x) + 3/2*(((x*y)*x)*(x*x))"
    )


def test_exp013_rejects_non_strict_cells_as_killing_sources(tmp_path) -> None:
    v2_path, by_weight_path = _reference_paths(tmp_path)

    run = compute_exp013(
        max_weight=8,
        mode="dry",
        output_dir=tmp_path / "exp013",
        reference_v2_cells=v2_path,
        reference_by_weight=by_weight_path,
        thresholds=Exp011Thresholds(),
    )

    target_weight_7 = next(
        record for record in run.killing_audit["weights"] if record["weight"] == 7
    )
    assert "s2_00001_w4" not in target_weight_7["allowed_source_cell_names"]
    assert all(
        "s2_00001_w4" not in candidate["allowed_source_cell_names"]
        for candidate in target_weight_7["candidates"]
    )


def test_exp013_low_to_high_uses_only_strict_lower_weight_cells(tmp_path) -> None:
    v2_path, by_weight_path = _reference_paths(tmp_path)

    run = compute_exp013(
        max_weight=8,
        mode="dry",
        output_dir=tmp_path / "exp013",
        reference_v2_cells=v2_path,
        reference_by_weight=by_weight_path,
        thresholds=Exp011Thresholds(),
    )

    for record in run.killing_audit["weights"]:
        target_weight = record["weight"]
        assert all(
            weight < target_weight
            for weight in record["allowed_source_weights"]
        )
        for candidate in record["candidates"]:
            assert candidate["target_weight"] == target_weight
            assert (
                candidate["allowed_source_weights"]
                == record["allowed_source_weights"]
            )


def test_exp013_report_language_preserves_bounded_non_q_boundary(tmp_path) -> None:
    v2_path, by_weight_path = _reference_paths(tmp_path)

    run = compute_exp013(
        max_weight=5,
        mode="dry",
        output_dir=tmp_path / "exp013",
        reference_v2_cells=v2_path,
        reference_by_weight=by_weight_path,
        thresholds=Exp011Thresholds(),
    )

    assert "does not apply $Q$" in run.tex_report
    assert "does not construct $V_3,V_4,\\ldots$" in run.tex_report
    assert report_language_has_no_forbidden_exp013_phrasing(run.tex_report)
