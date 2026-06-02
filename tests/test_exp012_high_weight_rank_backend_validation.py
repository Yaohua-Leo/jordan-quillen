import json
from fractions import Fraction

from jordan_qh.high_weight_rank_backend_validation import (
    EXP012_ID,
    build_reproduction_report,
    compute_exp012,
)
from jordan_qh.low_weight_jordan import sparse_modular_rank, sparse_modular_rank_v2
from jordan_qh.v2_cells_no_q import (
    Exp011Thresholds,
    compute_exp011,
    report_language_has_no_forbidden_global_phrasing,
)


def test_exp012_weight_4_reproduces_exp011_known_values(tmp_path) -> None:
    reference_run = compute_exp011(
        max_weight=4,
        mode="dry",
        output_dir=tmp_path / "reference",
        thresholds=Exp011Thresholds(),
    )
    reference_path = tmp_path / "by_weight_W4.json"
    reference_path.write_text(json.dumps(reference_run.by_weight), encoding="utf-8")

    run = compute_exp012(
        max_weight=4,
        mode="dry",
        output_dir=tmp_path / "exp012",
        reference_exp011=reference_path,
        thresholds=Exp011Thresholds(
            rank_backend="modular_sparse_v2",
            rank_progress_interval=1,
            rank_progress_seconds=999,
        ),
    )

    assert run.results["experiment_id"] == EXP012_ID
    assert run.results["applies_Q"] is False
    assert run.results["constructs_higher_cells_V3_plus"] is False
    assert run.results["reproduction"]["matches_exp011_reference"] is True
    assert run.results["checks"]["exp011_reproduction_matches_reference"] is True
    assert run.results["passed"] is True

    weight_4 = next(
        record for record in run.by_weight["weights"] if record["weight"] == 4
    )
    assert weight_4["dim_H1_old"] == 8
    assert weight_4["number_of_new_s_cells"] == 8
    assert len(run.v2_cells["cells"]) == 8
    assert report_language_has_no_forbidden_global_phrasing(run.tex_report)


def test_sparse_modular_rank_v2_matches_legacy_rank_and_reports_progress() -> None:
    rows = (
        {0: Fraction(1, 2), 1: Fraction(1, 3)},
        {0: Fraction(1, 2), 1: Fraction(2, 3)},
        {0: Fraction(1), 1: Fraction(1)},
    )
    progress: list[str] = []

    legacy = sparse_modular_rank(rows, prime=1_000_003)
    v2 = sparse_modular_rank_v2(
        rows,
        prime=1_000_003,
        progress=progress.append,
        progress_interval=1,
        progress_seconds=999,
    )

    assert v2 == legacy == 2
    assert any("conversion" in message for message in progress)
    assert any("elimination" in message for message in progress)
    assert any("current_rank" in message for message in progress)


def test_exp012_reproduction_mismatch_fails_global_pass(tmp_path) -> None:
    reference_run = compute_exp011(
        max_weight=1,
        mode="dry",
        output_dir=tmp_path / "reference",
        thresholds=Exp011Thresholds(),
    )
    reference = reference_run.by_weight
    reference["weights"][0]["dim_C0"] = 999
    reference_path = tmp_path / "bad_reference.json"
    reference_path.write_text(json.dumps(reference), encoding="utf-8")

    run = compute_exp012(
        max_weight=1,
        mode="dry",
        output_dir=tmp_path / "exp012",
        reference_exp011=reference_path,
        thresholds=Exp011Thresholds(rank_backend="modular_sparse_v2"),
    )

    assert run.results["reproduction"]["matches_exp011_reference"] is False
    assert run.results["checks"]["exp011_reproduction_matches_reference"] is False
    assert run.results["passed"] is False


def test_build_reproduction_report_detects_missing_reference(tmp_path) -> None:
    report = build_reproduction_report(
        reference_exp011=tmp_path / "missing.json",
        by_weight={"weights": []},
        recomputed_weights=(1,),
    )

    assert report["matches_exp011_reference"] is False
    assert report["error"] == "reference file does not exist"
