"""Experiment 011: bounded V2-cell candidates before applying Q.

This module intentionally works in the same ordinary low-weight Jordan backend
used by Experiment 009.  It computes, weight by weight, the finite quotient

    H1_old,w = ker(d1,w) / im(d2_old,w)

inside A^(1), without attaching the resulting formal degree-2 cells and
without applying Q.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Any

from jordan_qh.chain_complex import compose_rows
from jordan_qh.low_weight_jordan import (
    LowWeightJordanModel,
    RawVector,
    SparseRow,
    WeightedGenerator,
    build_low_weight_jordan_model,
    product_term,
    raw_vector_to_terms,
    reduce_sparse_row,
    sparse_echelon,
    sparse_kernel_basis,
    sparse_modular_rank,
    sparse_modular_rank_v2,
    sparse_rref,
    term_to_str,
)

EXP011_ID = "EXP-011-v2-cells-no-Q"
EXPERIMENT_DIRECTORY = "experiments/011-v2-cells-no-Q/"
PLAN_PATH = "researchplan/subplan011.md"
MATRIX_CONVENTION = "source_rows_target_coordinates"
FIELD = "QQ"
ARITHMETIC = "exact_rational"
PRIMARY_OBJECT = "H1_old in A^(1)"
TARGET_ALGEBRA = "Jord<x,y>/(x^2,xy,y^2)"
CHECKPOINT_SCHEMA_VERSION = 1
DEFAULT_MAX_RAW_TERMS_PER_SPACE = 10_000
DEFAULT_MAX_QUOTIENT_DIM = 3_000
DEFAULT_MAX_MATRIX_NNZ = 250_000
REPORT_FORBIDDEN_PHRASES = (
    "No more cells occur after weight W.",
    "The computation proves the full V2 layer.",
    "The infinite-weight case is complete.",
    "H1_old has global dimension",
)
RANK_CERTIFICATE_PRIMES = (1_000_003, 1_000_033, 1_000_037)


@dataclass(frozen=True)
class Exp011Thresholds:
    """Adaptive stopping thresholds for the bounded computation."""

    max_raw_terms_per_space: int = DEFAULT_MAX_RAW_TERMS_PER_SPACE
    max_quotient_dim: int = DEFAULT_MAX_QUOTIENT_DIM
    max_matrix_nnz: int = DEFAULT_MAX_MATRIX_NNZ
    max_runtime_per_weight: float | None = None
    max_memory_gb: float | None = None
    workers: int = 1
    matrix_workers: int = 1
    rank_backend: str = "modular_sparse"
    rank_progress_interval: int = 10_000
    rank_progress_seconds: float = 15.0
    max_rank_seconds: float | None = None


@dataclass(frozen=True)
class Exp011Run:
    """In-memory result bundle for one EXP011 run."""

    results: dict[str, Any]
    by_weight: dict[str, Any]
    v2_cells: dict[str, Any]
    tex_report: str
    log_text: str


class WeightSkipped(RuntimeError):
    """Raised internally when a per-weight threshold is exceeded."""

    def __init__(self, reason: str, threshold: str) -> None:
        super().__init__(reason)
        self.reason = reason
        self.threshold = threshold


def initial_generators_and_differentials() -> tuple[
    tuple[WeightedGenerator, ...],
    dict[str, RawVector],
]:
    """Return A^(1) generators and the old differential."""

    x = ("g", "x")
    y = ("g", "y")
    generators = (
        WeightedGenerator("x", degree=0, weight=1),
        WeightedGenerator("y", degree=0, weight=1),
        WeightedGenerator("r_xx", degree=1, weight=2),
        WeightedGenerator("r_xy", degree=1, weight=2),
        WeightedGenerator("r_yy", degree=1, weight=2),
    )
    differentials: dict[str, RawVector] = {
        "r_xx": {product_term(x, x): Fraction(1)},
        "r_xy": {product_term(x, y): Fraction(1)},
        "r_yy": {product_term(y, y): Fraction(1)},
    }
    return generators, differentials


def raw_count_estimates(max_weight: int) -> dict[int, dict[str, Any]]:
    """Count raw commutative nonassociative terms by degree and weight.

    The recurrence counts unordered products in the free commutative
    nonassociative magma.  It is used only as a pre-quotient feasibility guard.
    """

    if max_weight < 1:
        msg = "max_weight must be positive"
        raise ValueError(msg)

    counts: defaultdict[tuple[int, int], int] = defaultdict(int)
    counts[(0, 1)] = 2
    counts[(1, 2)] = 3
    for weight in range(2, max_weight + 1):
        keys = [
            key
            for key, count in counts.items()
            if count and key[1] < weight
        ]
        for degree in range(3):
            total = 0
            for left_index, left_key in enumerate(keys):
                left_degree, left_weight = left_key
                for right_key in keys[left_index:]:
                    right_degree, right_weight = right_key
                    if left_degree + right_degree != degree:
                        continue
                    if left_weight + right_weight != weight:
                        continue
                    left_count = counts[left_key]
                    right_count = counts[right_key]
                    if left_key == right_key:
                        total += left_count * (left_count + 1) // 2
                    else:
                        total += left_count * right_count
            counts[(degree, weight)] += total

    estimates: dict[int, dict[str, Any]] = {}
    for weight in range(1, max_weight + 1):
        by_degree = {
            f"degree_{degree}": counts[(degree, weight)]
            for degree in range(3)
        }
        estimates[weight] = {
            "weight": weight,
            "raw_terms_by_degree": by_degree,
            "max_raw_terms_per_space": max(by_degree.values()),
            "total_raw_terms": sum(by_degree.values()),
        }
    return estimates


def select_feasible_weight(
    max_weight: int,
    thresholds: Exp011Thresholds,
) -> tuple[int, dict[str, Any] | None, dict[int, dict[str, Any]]]:
    """Choose the highest weight attempted before preflight raw-term skipping."""

    estimates = raw_count_estimates(max_weight)
    for weight in range(1, max_weight + 1):
        max_raw = estimates[weight]["max_raw_terms_per_space"]
        if max_raw > thresholds.max_raw_terms_per_space:
            reason = (
                f"estimated max raw terms per homogeneous space is {max_raw}, "
                f"exceeding max_raw_terms_per_space="
                f"{thresholds.max_raw_terms_per_space}"
            )
            return (
                weight - 1,
                {
                    "first_skipped_weight": weight,
                    "skip_reason": reason,
                    "threshold_triggered": "max_raw_terms_per_space",
                    "estimate": estimates[weight],
                },
                estimates,
            )
    return max_weight, None, estimates


def compute_exp011(
    *,
    max_weight: int,
    mode: str,
    output_dir: Path,
    thresholds: Exp011Thresholds | None = None,
    resume: bool = False,
    force_recompute_weights: tuple[int, ...] = (),
) -> Exp011Run:
    """Compute EXP011 and write caches/checkpoints under ``output_dir``."""

    if max_weight < 1:
        msg = "max_weight must be positive"
        raise ValueError(msg)
    if thresholds is None:
        thresholds = Exp011Thresholds()
    forced_weights = frozenset(force_recompute_weights)
    if any(weight < 1 for weight in forced_weights):
        msg = "force_recompute_weights must contain positive weights"
        raise ValueError(msg)

    start_time = datetime.now().isoformat(timespec="seconds")
    start_counter = perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = output_dir / "cache"
    checkpoint_dir = output_dir / "checkpoints"
    log_dir = output_dir / "logs"
    cache_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    feasible_weight, preflight_skip, raw_estimates = select_feasible_weight(
        max_weight,
        thresholds,
    )
    log_lines = [
        f"start time: {start_time}",
        f"mode: {mode}",
        f"max weight requested: {max_weight}",
        f"resume: {resume}",
        f"force recompute weights: {sorted(forced_weights)}",
        f"thresholds: {asdict(thresholds)}",
        f"preflight feasible upper bound: {feasible_weight}",
    ]
    if preflight_skip is not None:
        log_lines.append(f"preflight skip: {preflight_skip['skip_reason']}")

    completed_records: list[dict[str, Any]] = []
    failed_records: list[dict[str, Any]] = []
    skipped_records: list[dict[str, Any]] = []
    all_cells: list[dict[str, Any]] = []
    next_global_index = 1
    previous_completed_weight: int | None = None

    need_model = any(
        weight in forced_weights
        or not _valid_resume_checkpoint(
            checkpoint_dir / f"weight_{weight}_status.json",
        )
        for weight in range(1, feasible_weight + 1)
    )
    model: LowWeightJordanModel | None = None
    if need_model and feasible_weight > 0:
        generators, differentials = initial_generators_and_differentials()
        model_start = perf_counter()
        progress_path = log_dir / f"model_W{feasible_weight}_progress.log"
        progress_path.write_text("", encoding="utf-8")

        def progress(message: str) -> None:
            with progress_path.open("a", encoding="utf-8") as handle:
                handle.write(
                    f"{datetime.now().isoformat(timespec='seconds')} {message}\n",
                )

        model = build_low_weight_jordan_model(
            generators,
            differentials,
            weight_bound=feasible_weight,
            max_degree=2,
            workers=max(1, thresholds.workers),
            progress=progress,
        )
        log_lines.append(
            f"model build seconds for W={feasible_weight}: "
            f"{perf_counter() - model_start:.3f}",
        )
        log_lines.append(f"model progress log: {progress_path.as_posix()}")

    for weight in range(1, max_weight + 1):
        checkpoint_path = checkpoint_dir / f"weight_{weight}_status.json"
        if weight > feasible_weight:
            record = _skip_record_after_preflight(
                weight=weight,
                feasible_weight=feasible_weight,
                preflight_skip=preflight_skip,
                previous_completed_weight=previous_completed_weight,
            )
            skipped_records.append(record)
            _write_json(checkpoint_path, _checkpoint_payload(record, []))
            log_lines.append(
                f"weight {weight}: skipped ({record['skip_reason']})",
            )
            continue

        if resume and weight not in forced_weights and _valid_resume_checkpoint(
            checkpoint_path,
        ):
            checkpoint = _read_json(checkpoint_path)
            record = checkpoint["record"]
            cells = checkpoint.get("cells", [])
            completed_records.append(record)
            all_cells.extend(cells)
            previous_completed_weight = weight
            if cells:
                next_global_index = max(
                    next_global_index,
                    max(int(cell["global_index"]) for cell in cells) + 1,
                )
            log_lines.append(f"weight {weight}: completed from checkpoint")
            continue

        if model is None:
            msg = "internal error: missing model for uncheckpointed weight"
            raise RuntimeError(msg)

        weight_attempt_start = perf_counter()
        try:
            record, cells = _compute_weight_record(
                model=model,
                weight=weight,
                global_index_start=next_global_index,
                thresholds=thresholds,
                cache_dir=cache_dir,
            )
        except WeightSkipped as exc:
            record = {
                "weight": weight,
                "status": "skipped",
                "skip_reason": exc.reason,
                "threshold_triggered": exc.threshold,
                "previous_completed_weight": previous_completed_weight,
                "partial_outputs_preserved": True,
                "runtime_seconds": round(perf_counter() - weight_attempt_start, 3),
                "memory_notes": _memory_notes(thresholds),
            }
            skipped_records.append(record)
            _write_json(checkpoint_path, _checkpoint_payload(record, []))
            log_lines.append(f"weight {weight}: skipped ({exc.reason})")
            continue
        except Exception as exc:  # pragma: no cover - diagnostic preservation path
            record = {
                "weight": weight,
                "status": "failed",
                "failure_stage": "weight_computation",
                "error_message": str(exc),
                "partial_outputs_preserved": True,
                "runtime_seconds": round(perf_counter() - weight_attempt_start, 3),
                "memory_notes": _memory_notes(thresholds),
            }
            failed_records.append(record)
            _write_json(checkpoint_path, _checkpoint_payload(record, []))
            log_lines.append(f"weight {weight}: failed ({exc})")
            continue

        completed_records.append(record)
        all_cells.extend(cells)
        next_global_index += len(cells)
        previous_completed_weight = weight
        _write_json(checkpoint_path, _checkpoint_payload(record, cells))
        log_lines.append(
            "weight "
            f"{weight}: completed, dim_H1_old={record['dim_H1_old']}, "
            f"new_s_cells={record['number_of_new_s_cells']}, "
            f"runtime_seconds={record['runtime_seconds']}",
        )

    completed_weights = [record["weight"] for record in completed_records]
    failed_weights = [record["weight"] for record in failed_records]
    skipped_weights = [record["weight"] for record in skipped_records]
    classified = set(completed_weights) | set(failed_weights) | set(skipped_weights)
    not_tested_weights = [
        weight for weight in range(1, max_weight + 1) if weight not in classified
    ]

    by_weight = {
        "experiment_id": EXP011_ID,
        "max_weight_requested": max_weight,
        "requested_weights": list(range(1, max_weight + 1)),
        "completed_weights": completed_weights,
        "failed_weights": failed_weights,
        "skipped_weights": skipped_weights,
        "not_tested_weights_in_requested_range": not_tested_weights,
        "raw_count_estimates": raw_estimates,
        "weights": [*completed_records, *failed_records, *skipped_records],
    }
    by_weight["weights"] = sorted(by_weight["weights"], key=lambda item: item["weight"])

    v2_cells = {
        "experiment_id": EXP011_ID,
        "max_weight_requested": max_weight,
        "cell_count": len(all_cells),
        "cells": all_cells,
    }

    by_weight_file = f"data/by_weight_W{max_weight}.json"
    v2_cells_file = f"data/v2_cells_W{max_weight}.json"
    tex_report_file = "tex/exp011_v2_cells_no_Q.tex"
    checks = _global_checks(completed_records, all_cells)
    checks["sanity_exp009_low_weight_agreement"] = _exp009_sanity_comparison(
        output_dir,
        completed_records,
        all_cells,
    )
    results = {
        "experiment_id": EXP011_ID,
        "experiment_directory": EXPERIMENT_DIRECTORY,
        "plan": PLAN_PATH,
        "status": "run",
        "passed": bool(checks["all_completed_weights_passed"] and not failed_weights),
        "field": FIELD,
        "arithmetic": ARITHMETIC,
        "applies_Q": False,
        "constructs_higher_cells_V3_plus": False,
        "primary_object": PRIMARY_OBJECT,
        "matrix_convention": MATRIX_CONVENTION,
        "target_algebra": TARGET_ALGEBRA,
        "backend": _backend_record(),
        "mode": mode,
        "resume": resume,
        "force_recompute_weights": sorted(forced_weights),
        "thresholds": asdict(thresholds),
        "adaptive_feasible_upper_bound": feasible_weight,
        "preflight_skip": preflight_skip,
        "max_weight_requested": max_weight,
        "requested_weights": list(range(1, max_weight + 1)),
        "completed_weights": completed_weights,
        "failed_weights": failed_weights,
        "skipped_weights": skipped_weights,
        "not_tested_weights_in_requested_range": not_tested_weights,
        "global_claims_modified": False,
        "finite_truncation_warning": (
            "All conclusions are only for completed weights."
        ),
        "by_weight_file": by_weight_file,
        "v2_cells_file": v2_cells_file,
        "tex_report": tex_report_file,
        "checks": checks,
        "run_started_at": start_time,
        "run_finished_at": datetime.now().isoformat(timespec="seconds"),
        "runtime_seconds": round(perf_counter() - start_counter, 3),
    }
    tex_report = render_tex_report(results, by_weight, v2_cells)
    results["checks"]["report_language_has_no_forbidden_global_phrasing"] = (
        report_language_has_no_forbidden_global_phrasing(tex_report)
    )
    results["passed"] = bool(
        results["passed"]
        and results["checks"]["report_language_has_no_forbidden_global_phrasing"]
    )
    tex_report = render_tex_report(results, by_weight, v2_cells)
    log_lines.append(f"end time: {results['run_finished_at']}")
    log_lines.append(f"runtime seconds: {results['runtime_seconds']}")
    log_lines.append(f"completed weights: {completed_weights}")
    log_lines.append(f"skipped weights: {skipped_weights}")
    log_lines.append(f"failed weights: {failed_weights}")

    return Exp011Run(
        results=results,
        by_weight=by_weight,
        v2_cells=v2_cells,
        tex_report=tex_report,
        log_text="\n".join(log_lines) + "\n",
    )


def render_tex_report(
    results: dict[str, Any],
    by_weight: dict[str, Any],
    v2_cells: dict[str, Any],
) -> str:
    """Render a concise LaTeX report from the same object as the JSON output."""

    lines = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{booktabs}",
        r"\usepackage{hyperref}",
        r"\usepackage{longtable}",
        r"\usepackage{verbatim}",
        r"\title{Experiment 011: V2 Cells Before Q}",
        r"\author{Jordan Quillen Homology Project}",
        r"\date{}",
        r"\begin{document}",
        r"\maketitle",
        r"\section*{Scope}",
        f"Experiment ID: \\texttt{{{_tex_escape(results['experiment_id'])}}}.",
        "",
        f"Target algebra: \\texttt{{{_tex_escape(TARGET_ALGEBRA)}}}.",
        "",
        (
            "The computation uses "
            "$A^{(1)}=\\mathrm{Jord}\\langle x,y,r_{xx},r_{xy},r_{yy}\\rangle$ "
            "with $|x|=|y|=0$, $|r_{xx}|=|r_{xy}|=|r_{yy}|=1$, "
            "and $d(r_{xx})=x^2$, $d(r_{xy})=xy$, $d(r_{yy})=y^2$."
        ),
        "",
        "The functor $Q$ is not applied in this experiment.",
        "",
        "The layers $V_3,V_4,\\ldots$ are not constructed.",
        "",
        (
            "Backend convention: this run follows the existing ordinary "
            "commutative nonassociative low-weight Jordan backend with a "
            "signed derivation differential.  It is backend-relative bounded "
            "evidence, not a fully graded operadic convention audit."
        ),
        r"\section*{Finite-Weight Boundary}",
        (
            "All conclusions in this report are restricted to weights with "
            "status completed. Weights not tested, skipped, or failed are not "
            "used to infer any global statement. This computation does not "
            "prove stabilization, termination, or absence of further degree 2 "
            "attaching generators in untested weights."
        ),
        r"\section*{Weight Summary}",
        r"\begin{longtable}{rrrrrrrrl}",
        r"\toprule",
        (
            "w & $\\dim C_0$ & $\\dim C_1$ & $\\dim C_2^{old}$ & "
            "$\\operatorname{rank} d_1$ & $\\operatorname{rank} d_2$ & "
            "$\\dim Z_1$ & $\\dim H_1^{old}$ & status \\\\"
        ),
        r"\midrule",
    ]
    for record in by_weight["weights"]:
        if record["status"] == "completed":
            lines.append(
                f"{record['weight']} & {record['dim_C0']} & "
                f"{record['dim_C1']} & {record['dim_C2_old']} & "
                f"{record['rank_d1']} & {record['rank_d2_old']} & "
                f"{record['dim_Z1']} & {record['dim_H1_old']} & "
                f"{_tex_escape(record['status'])} \\\\",
            )
        else:
            lines.append(
                f"{record['weight']} & -- & -- & -- & -- & -- & -- & -- & "
                f"{_tex_escape(record['status'])} \\\\",
            )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\section*{Skipped, Failed, And Not Tested Weights}",
        ],
    )
    lines.append(
        "\\begin{verbatim}\n"
        f"skipped_weights = {results['skipped_weights']}\n"
        f"failed_weights = {results['failed_weights']}\n"
        "not_tested_weights_in_requested_range = "
        f"{results['not_tested_weights_in_requested_range']}\n"
        "\\end{verbatim}",
    )
    lines.extend(
        [
            r"\section*{Formal Degree 2 Cell Candidates}",
            (
                "Each listed record is a formal candidate only: the cell is "
                "not attached during this experiment."
            ),
        ],
    )
    if not v2_cells["cells"]:
        lines.append(
            "No formal degree 2 cell candidates were found in completed weights.",
        )
    for cell in v2_cells["cells"]:
        lines.append(f"\\paragraph{{\\texttt{{{_tex_escape(cell['name'])}}}}}")
        lines.append(
            "\\begin{verbatim}\n"
            f"degree = {cell['degree']}\n"
            f"weight = {cell['weight']}\n"
            f"d({cell['name']}) = {cell['cycle_z']}\n"
            "boundary_remainder_mod_B_old = "
            f"{cell['boundary_remainder_mod_B_old']['formula']}\n"
            "selection_remainder_mod_B_old_plus_accepted_reps = "
            f"{cell['selection_remainder_mod_B_old_plus_accepted_reps']['formula']}\n"
            "\\end{verbatim}",
        )
    lines.extend(
        [
            r"\section*{Validation Summary}",
            "\\begin{verbatim}",
            _pretty_checks(results["checks"]),
            "\\end{verbatim}",
            r"\end{document}",
            "",
        ],
    )
    return "\n".join(lines)


def report_language_has_no_forbidden_global_phrasing(report: str) -> bool:
    """Return whether the report omits forbidden theorem-like phrases."""

    return all(phrase not in report for phrase in REPORT_FORBIDDEN_PHRASES)


def write_run_outputs(run: Exp011Run, output_dir: Path) -> None:
    """Write the EXP011 JSON, TeX, and log artifacts."""

    data_dir = output_dir / "data"
    tex_dir = output_dir / "tex"
    log_dir = output_dir / "logs"
    data_dir.mkdir(parents=True, exist_ok=True)
    tex_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    max_weight = run.results["max_weight_requested"]
    _write_json(output_dir / "results.json", run.results)
    _write_json(data_dir / f"by_weight_W{max_weight}.json", run.by_weight)
    _write_json(data_dir / f"v2_cells_W{max_weight}.json", run.v2_cells)
    (tex_dir / "exp011_v2_cells_no_Q.tex").write_text(
        run.tex_report,
        encoding="utf-8",
    )
    (log_dir / f"run_W{max_weight}.log").write_text(
        run.log_text,
        encoding="utf-8",
    )


def _modular_rank_certificate(
    rows: tuple[SparseRow, ...],
    *,
    target_rank: int,
    label: str,
    progress: Callable[[str], None],
    thresholds: Exp011Thresholds,
) -> tuple[int, int] | None:
    for prime in RANK_CERTIFICATE_PRIMES:
        try:
            if thresholds.rank_backend == "modular_sparse":
                rank = sparse_modular_rank(rows, prime=prime, max_rank=target_rank)
            elif thresholds.rank_backend == "modular_sparse_v2":
                rank = sparse_modular_rank_v2(
                    rows,
                    prime=prime,
                    max_rank=target_rank,
                    progress=lambda message, prime=prime: progress(
                        f"{label} modular_sparse_v2 mod {prime}: {message}",
                    ),
                    progress_interval=thresholds.rank_progress_interval,
                    progress_seconds=thresholds.rank_progress_seconds,
                    max_seconds=thresholds.max_rank_seconds,
                )
            else:
                msg = f"unknown rank backend: {thresholds.rank_backend}"
                raise ValueError(msg)
        except TimeoutError as exc:
            progress(f"{label} modular rank timed out mod {prime}: {exc}")
            raise WeightSkipped(str(exc), "rank_timeout") from exc
        except ValueError as exc:
            progress(f"{label} modular rank skipped mod {prime}: {exc}")
            continue
        progress(
            f"{label} modular rank mod {prime}: {rank} "
            f"backend={thresholds.rank_backend}",
        )
        if rank >= target_rank:
            return rank, prime
    return None


def _compute_weight_record(
    *,
    model: LowWeightJordanModel,
    weight: int,
    global_index_start: int,
    thresholds: Exp011Thresholds,
    cache_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    weight_start = perf_counter()
    progress_path = cache_dir.parent / "logs" / f"weight_{weight}_progress.log"
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text("", encoding="utf-8")

    def progress(message: str) -> None:
        with progress_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{datetime.now().isoformat(timespec='seconds')} {message}\n")

    c0 = model.quotient_space(0, weight)
    c1 = model.quotient_space(1, weight)
    c2_old = model.quotient_space(2, weight)
    dim_c0 = c0.dimension()
    dim_c1 = c1.dimension()
    dim_c2_old = c2_old.dimension()
    max_quotient_dim = max(dim_c0, dim_c1, dim_c2_old)
    if max_quotient_dim > thresholds.max_quotient_dim:
        raise WeightSkipped(
            (
                f"max quotient dimension {max_quotient_dim} exceeds "
                f"max_quotient_dim={thresholds.max_quotient_dim}"
            ),
            "max_quotient_dim",
        )

    progress(
        "quotient dimensions: "
        f"C0={dim_c0} C1={dim_c1} C2_old={dim_c2_old}",
    )
    matrix_worker_count = max(1, thresholds.matrix_workers)
    progress(f"matrix_workers={matrix_worker_count}")
    d1_matrix_start = perf_counter()
    d1_rows = model.differential_sparse_matrix(
        1,
        weight,
        workers=matrix_worker_count,
    )
    d1_matrix_seconds = perf_counter() - d1_matrix_start
    progress(
        f"built d1 matrix rows={len(d1_rows)} "
        f"nnz={_sparse_rows_nnz(d1_rows)} "
        f"seconds={d1_matrix_seconds:.3f}",
    )
    d2_matrix_start = perf_counter()
    d2_old_rows = model.differential_sparse_matrix(
        2,
        weight,
        workers=matrix_worker_count,
    )
    d2_matrix_seconds = perf_counter() - d2_matrix_start
    progress(
        f"built d2_old matrix rows={len(d2_old_rows)} "
        f"nnz={_sparse_rows_nnz(d2_old_rows)} "
        f"seconds={d2_matrix_seconds:.3f}",
    )
    d1_nnz = _sparse_rows_nnz(d1_rows)
    d2_old_nnz = _sparse_rows_nnz(d2_old_rows)
    if max(d1_nnz, d2_old_nnz) > thresholds.max_matrix_nnz:
        raise WeightSkipped(
            (
                f"matrix nnz {max(d1_nnz, d2_old_nnz)} exceeds "
                f"max_matrix_nnz={thresholds.max_matrix_nnz}"
            ),
            "max_matrix_nnz",
        )

    rank_certificates: dict[str, Any] = {}
    d1_rank_start = perf_counter()
    d1_certificate = _modular_rank_certificate(
        d1_rows,
        target_rank=dim_c0,
        label="d1",
        progress=progress,
        thresholds=thresholds,
    )
    if d1_certificate is not None:
        rank_d1, prime = d1_certificate
        rank_certificates["d1"] = {
            "method": "modular_full_target_rank",
            "backend": thresholds.rank_backend,
            "prime": prime,
            "rank": rank_d1,
            "target_rank": dim_c0,
        }
        progress(f"certified rank d1={rank_d1} by modular target-rank lower bound")
    else:
        d1_rank_basis = sparse_echelon(d1_rows, max_rank=dim_c0)
        rank_d1 = len(d1_rank_basis)
        rank_certificates["d1"] = {"method": "rational_sparse_echelon"}
        progress(f"computed rank d1={rank_d1}")
    d1_rank_seconds = perf_counter() - d1_rank_start
    progress(f"d1 rank seconds={d1_rank_seconds:.3f}")
    dim_z1 = dim_c1 - rank_d1
    d2_old_rank_basis: dict[int, SparseRow] = {}
    d2_rank_start = perf_counter()
    d2_certificate = (
        _modular_rank_certificate(
            d2_old_rows,
            target_rank=dim_z1,
            label="d2_old",
            progress=progress,
            thresholds=thresholds,
        )
        if dim_z1 >= 0
        else None
    )
    if d2_certificate is not None:
        rank_d2_old, prime = d2_certificate
        rank_certificates["d2_old"] = {
            "method": "modular_dim_z1_lower_bound",
            "backend": thresholds.rank_backend,
            "prime": prime,
            "rank": rank_d2_old,
            "target_rank": dim_z1,
        }
        progress(
            f"certified rank d2_old>={rank_d2_old} "
            "by modular lower bound",
        )
    else:
        d2_rank_stop = dim_z1 if dim_z1 >= 0 else None
        d2_old_rank_basis = sparse_echelon(d2_old_rows, max_rank=d2_rank_stop)
        rank_d2_old = len(d2_old_rank_basis)
        rank_certificates["d2_old"] = {"method": "rational_sparse_echelon"}
        progress(f"computed rank d2_old={rank_d2_old}")
    d2_rank_seconds = perf_counter() - d2_rank_start
    progress(f"d2_old rank seconds={d2_rank_seconds:.3f}")
    dim_b_old = rank_d2_old
    dim_h1_old = dim_z1 - dim_b_old
    chain_start = perf_counter()
    chain_condition = _source_row_composition_is_zero(
        first_rows=d2_old_rows,
        second_rows=d1_rows,
        first_target_dimension=dim_c1,
        second_target_dimension=dim_c0,
    )
    chain_seconds = perf_counter() - chain_start
    progress(f"chain condition seconds={chain_seconds:.3f}")
    progress(
        "rank precheck: "
        f"dim_Z1={dim_z1} dim_B_old={dim_b_old} "
        f"dim_H1_old={dim_h1_old} chain_condition={chain_condition}",
    )

    cells: list[dict[str, Any]] = []
    c0_basis = tuple(term_to_str(term) for term in c0.basis_terms())
    c1_basis = tuple(term_to_str(term) for term in c1.basis_terms())
    c2_old_basis = tuple(term_to_str(term) for term in c2_old.basis_terms())

    z1_omitted_reason: str | None = None
    b_old_basis_type = "rref"
    if dim_h1_old == 0 and chain_condition:
        d2_old_rref = d2_old_rank_basis
        z1_basis: tuple[SparseRow, ...] = ()
        quotient_independence = True
        z1_omitted_reason = (
            "Full Z1 basis omitted because rank-nullity gives dim_H1_old=0."
        )
        b_old_basis_type = (
            "row_echelon_rank_basis"
            if d2_old_rank_basis
            else "modular_rank_certificate_no_basis"
        )
        progress("used zero-H1 rank fast path; no cell representatives needed")
    else:
        d2_old_rref = sparse_rref(d2_old_rows)
        progress(f"computed B_old RREF rank={len(d2_old_rref)}")
        z1_basis = sparse_kernel_basis(
            d1_rows,
            source_dimension=dim_c1,
            target_dimension=dim_c0,
        )
        progress(f"computed full Z1 basis size={len(z1_basis)}")
        selection_rref = dict(d2_old_rref)
        for cycle in z1_basis:
            boundary_remainder = reduce_sparse_row(cycle, d2_old_rref)
            selection_remainder = reduce_sparse_row(cycle, selection_rref)
            if not selection_remainder:
                continue
            global_index = global_index_start + len(cells)
            name = f"s2_{global_index:05d}_w{weight}"
            d1_z = _apply_source_row_map(cycle, d1_rows)
            raw_lift = c1.lift_sparse_coordinates(cycle)
            cells.append(
                {
                    "name": name,
                    "degree": 2,
                    "weight": weight,
                    "global_index": global_index,
                    "cycle_z": _sparse_row_formula(cycle, c1_basis),
                    "cycle_z_coordinates_in_C1_basis": _dense_sparse_row_json(
                        cycle,
                        dim_c1,
                    ),
                    "cycle_z_sparse_coordinates_in_C1_basis": _sparse_row_json(cycle),
                    "cycle_z_raw_lift": raw_vector_to_terms(raw_lift),
                    "d1_z_normal_form": _sparse_row_formula(d1_z, c0_basis),
                    "boundary_remainder_mod_B_old": _sparse_row_record(
                        boundary_remainder,
                        c1_basis,
                    ),
                    "boundary_remainder_nonzero": bool(boundary_remainder),
                    "selection_remainder_mod_B_old_plus_accepted_reps": (
                        _sparse_row_record(selection_remainder, c1_basis)
                    ),
                    "independent_mod_B_old_plus_previous_reps": True,
                    "not_in_B_old": bool(boundary_remainder),
                    "certificate_type": "rref_remainder",
                    "optional_dual_certificate": None,
                },
            )
            pivot = min(selection_remainder)
            coefficient = selection_remainder[pivot]
            selection_rref[pivot] = {
                column: value / coefficient
                for column, value in selection_remainder.items()
            }
            selection_rref = sparse_rref(selection_rref.values())

        quotient_independence = len(selection_rref) == len(d2_old_rref) + len(cells)
    all_cycles = all(cell["d1_z_normal_form"] == "0" for cell in cells)
    all_non_boundaries = all(
        cell["boundary_remainder_nonzero"] and cell["not_in_B_old"]
        for cell in cells
    )
    runtime_seconds = round(perf_counter() - weight_start, 3)
    runtime_within_threshold = (
        thresholds.max_runtime_per_weight is None
        or runtime_seconds <= thresholds.max_runtime_per_weight
    )

    cache_paths = {
        "quotient_space_cache": f"cache/quotient_space_deg{{p}}_w{weight}.json",
        "d1_matrix_cache": f"cache/d1_w{weight}.json",
        "d2_old_matrix_cache": f"cache/d2_old_w{weight}.json",
        "B_old_rref_cache": f"cache/B_old_rref_w{weight}.json",
        "Z1_basis_cache": f"cache/Z1_basis_w{weight}.json",
        "H1_old_reps_cache": f"cache/H1_old_reps_w{weight}.json",
    }
    _write_weight_caches(
        cache_dir=cache_dir,
        weight=weight,
        quotient_spaces=(c0, c1, c2_old),
        bases=(c0_basis, c1_basis, c2_old_basis),
        d1_rows=d1_rows,
        d2_old_rows=d2_old_rows,
        b_old_rref=d2_old_rref,
        b_old_rank=rank_d2_old,
        b_old_basis_type=b_old_basis_type,
        z1_basis=z1_basis,
        z1_expected_dimension=dim_z1,
        z1_omitted_reason=z1_omitted_reason,
        cells=cells,
    )

    checks = {
        "d2_old_matrix_times_d1_matrix_is_zero": chain_condition,
        "dim_Z1_matches_rank_nullity": dim_z1 == dim_c1 - rank_d1,
        "dim_B_old_matches_rank_d2_old": dim_b_old == rank_d2_old,
        "dim_H1_old_matches_quotient_count": dim_h1_old == len(cells),
        "all_cell_certificates_valid": all_cycles
        and all_non_boundaries
        and quotient_independence,
        "all_cells_are_cycles": all_cycles,
        "all_cells_have_nonzero_B_old_remainder": all_non_boundaries,
        "representatives_independent_mod_B_old": quotient_independence,
        "formal_d_squared_zero_on_s_cells": all_cycles,
        "runtime_within_threshold": runtime_within_threshold,
    }
    record = {
        "weight": weight,
        "status": "completed",
        "dim_C0": dim_c0,
        "dim_C1": dim_c1,
        "dim_C2_old": dim_c2_old,
        "rank_d1": rank_d1,
        "rank_d2_old": rank_d2_old,
        "dim_Z1": dim_z1,
        "dim_B_old": dim_b_old,
        "dim_H1_old": dim_h1_old,
        "number_of_new_s_cells": len(cells),
        "runtime_seconds": runtime_seconds,
        "memory_notes": _memory_notes(thresholds),
        "matrix_stats": {
            "d1_rows": dim_c1,
            "d1_cols": dim_c0,
            "d1_nnz": d1_nnz,
            "d2_old_rows": dim_c2_old,
            "d2_old_cols": dim_c1,
            "d2_old_nnz": d2_old_nnz,
            "matrix_workers": matrix_worker_count,
            "d1_build_seconds": round(d1_matrix_seconds, 3),
            "d2_old_build_seconds": round(d2_matrix_seconds, 3),
            "d1_rank_seconds": round(d1_rank_seconds, 3),
            "d2_old_rank_seconds": round(d2_rank_seconds, 3),
            "chain_condition_seconds": round(chain_seconds, 3),
        },
        "rank_certificates": rank_certificates,
        "raw_term_counts": {
            "C0_raw_terms": len(c0.raw_terms),
            "C1_raw_terms": len(c1.raw_terms),
            "C2_old_raw_terms": len(c2_old.raw_terms),
        },
        "basis_data": {
            "C0_basis": list(c0_basis),
            "C1_basis": list(c1_basis),
            "C2_old_basis": list(c2_old_basis),
        },
        "cache_paths": cache_paths,
        "checks": checks,
    }
    return record, cells


def _write_weight_caches(
    *,
    cache_dir: Path,
    weight: int,
    quotient_spaces: tuple[Any, Any, Any],
    bases: tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]],
    d1_rows: tuple[SparseRow, ...],
    d2_old_rows: tuple[SparseRow, ...],
    b_old_rref: dict[int, SparseRow],
    b_old_rank: int,
    b_old_basis_type: str,
    z1_basis: tuple[SparseRow, ...],
    z1_expected_dimension: int,
    z1_omitted_reason: str | None,
    cells: list[dict[str, Any]],
) -> None:
    for degree, quotient_space, basis in zip(
        (0, 1, 2),
        quotient_spaces,
        bases,
        strict=True,
    ):
        _write_json(
            cache_dir / f"quotient_space_deg{degree}_w{weight}.json",
            {
                "degree": degree,
                "weight": weight,
                "raw_term_count": len(quotient_space.raw_terms),
                "dimension": quotient_space.dimension(),
                "basis": list(basis),
                "free_columns": list(quotient_space.free_columns),
                "jordan_relation_rank": len(quotient_space.pivot_rows),
            },
        )
    _write_json(cache_dir / f"d1_w{weight}.json", _sparse_rows_record(d1_rows))
    _write_json(
        cache_dir / f"d2_old_w{weight}.json",
        _sparse_rows_record(d2_old_rows),
    )
    b_old_record = _pivot_rows_record(b_old_rref) | {
        "rank": b_old_rank,
        "basis_type": b_old_basis_type,
        "basis_available": bool(b_old_rref) or b_old_rank == 0,
    }
    _write_json(cache_dir / f"B_old_rref_w{weight}.json", b_old_record)
    z1_record = _sparse_rows_record(z1_basis) | {
        "expected_dimension": z1_expected_dimension,
        "full_basis_available": z1_omitted_reason is None,
    }
    if z1_omitted_reason is not None:
        z1_record["omitted_reason"] = z1_omitted_reason
    _write_json(cache_dir / f"Z1_basis_w{weight}.json", z1_record)
    _write_json(
        cache_dir / f"H1_old_reps_w{weight}.json",
        {
            "weight": weight,
            "representatives": [
                cell["cycle_z_sparse_coordinates_in_C1_basis"] for cell in cells
            ],
        },
    )


def _global_checks(
    completed_records: list[dict[str, Any]],
    cells: list[dict[str, Any]],
) -> dict[str, Any]:
    completed_checks = [
        all(record["checks"].values()) for record in completed_records
    ]
    return {
        "all_completed_weights_passed": all(completed_checks),
        "all_reported_z_are_cycles": all(
            cell["d1_z_normal_form"] == "0" for cell in cells
        ),
        "all_reported_z_have_nonzero_B_old_remainder": all(
            cell["boundary_remainder_nonzero"] for cell in cells
        ),
        "all_reported_classes_independent_mod_B_old": all(
            record["checks"]["representatives_independent_mod_B_old"]
            for record in completed_records
        ),
        "d_squared_zero_on_formal_s_cells": all(
            cell["d1_z_normal_form"] == "0" for cell in cells
        ),
        "exact_rational_arithmetic": True,
        "applies_Q_is_false": True,
        "constructs_higher_cells_V3_plus_is_false": True,
    }


def _exp009_sanity_comparison(
    output_dir: Path,
    completed_records: list[dict[str, Any]],
    cells: list[dict[str, Any]],
) -> dict[str, Any]:
    repo_root = output_dir.parents[1] if len(output_dir.parents) >= 2 else None
    if repo_root is None:
        return {"status": "not_checked", "reason": "repo root not available"}
    exp009_path = (
        repo_root
        / "experiments"
        / "009-square-zero-two-generator-quillen-homology"
        / "results.json"
    )
    if not exp009_path.exists():
        return {"status": "not_checked", "reason": "EXP009 results.json absent"}
    try:
        exp009 = _read_json(exp009_path)
    except ValueError as exc:
        return {"status": "not_checked", "reason": str(exc)}
    selected_weight = int(exp009.get("selected_weight_bound", 0))
    summaries = exp009.get("weight_bound_summaries", [])
    selected_summary = next(
        (
            summary
            for summary in summaries
            if int(summary.get("weight_bound", -1)) == selected_weight
        ),
        None,
    )
    if selected_weight <= 0 or selected_summary is None:
        return {"status": "not_checked", "reason": "EXP009 summary unavailable"}
    completed_weights = {record["weight"] for record in completed_records}
    if not all(weight in completed_weights for weight in range(1, selected_weight + 1)):
        return {
            "status": "not_checked",
            "reason": "EXP011 has not completed all low weights used by EXP009",
            "exp009_selected_weight_bound": selected_weight,
        }
    exp009_c2 = int(selected_summary["basis_sizes"]["C2"])
    exp011_cumulative = sum(
        1 for cell in cells if int(cell["weight"]) <= selected_weight
    )
    return {
        "status": "checked",
        "interpretation": (
            "Compatibility check only; EXP011 does not use EXP009 as input "
            "or as mathematical authority."
        ),
        "exp009_selected_weight_bound": selected_weight,
        "exp009_degree_2_cell_count": exp009_c2,
        "exp011_cumulative_v2_cell_count": exp011_cumulative,
        "agrees": exp009_c2 == exp011_cumulative,
    }


def _backend_record() -> dict[str, Any]:
    return {
        "name": "low_weight_jordan ordinary backend",
        "convention": (
            "ordinary commutative nonassociative Jordan algebra modulo the "
            "linearized Jordan identity, with a signed derivation differential"
        ),
        "convention_audit": (
            "The output is relative to this backend convention.  A separate "
            "theory check is needed before identifying it exactly with a fully "
            "graded operadic dg Jordan convention."
        ),
        "does_not_apply_Q": True,
        "does_not_attach_s_cells": True,
        "does_not_construct_V3_plus": True,
    }


def _skip_record_after_preflight(
    *,
    weight: int,
    feasible_weight: int,
    preflight_skip: dict[str, Any] | None,
    previous_completed_weight: int | None,
) -> dict[str, Any]:
    if preflight_skip is not None and weight == preflight_skip["first_skipped_weight"]:
        skip_reason = preflight_skip["skip_reason"]
        threshold = preflight_skip["threshold_triggered"]
    else:
        skip_reason = (
            f"adaptive stop after feasible upper bound W={feasible_weight}; "
            "higher weights were not enumerated"
        )
        threshold = "adaptive_stop_after_preflight_skip"
    return {
        "weight": weight,
        "status": "skipped",
        "skip_reason": skip_reason,
        "threshold_triggered": threshold,
        "previous_completed_weight": previous_completed_weight,
        "partial_outputs_preserved": True,
        "runtime_seconds": 0,
        "memory_notes": "Skipped before quotient-space construction.",
    }


def _valid_resume_checkpoint(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        checkpoint = _read_json(path)
    except ValueError:
        return False
    return (
        checkpoint.get("checkpoint_schema_version") == CHECKPOINT_SCHEMA_VERSION
        and checkpoint.get("experiment_id") == EXP011_ID
        and checkpoint.get("record", {}).get("status") == "completed"
        and bool(checkpoint.get("record", {}).get("checks", {}))
        and all(checkpoint["record"]["checks"].values())
    )


def _checkpoint_payload(
    record: dict[str, Any],
    cells: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "checkpoint_schema_version": CHECKPOINT_SCHEMA_VERSION,
        "experiment_id": EXP011_ID,
        "weight": record["weight"],
        "status": record["status"],
        "record": record,
        "cells": cells,
    }


def _apply_source_row_map(
    vector: SparseRow,
    matrix_rows: tuple[SparseRow, ...],
) -> SparseRow:
    result: SparseRow = {}
    for source_index, coefficient in vector.items():
        for target_index, entry in matrix_rows[source_index].items():
            result[target_index] = (
                result.get(target_index, Fraction(0)) + coefficient * entry
            )
            if result[target_index] == 0:
                del result[target_index]
    return result


def _sparse_rows_nnz(rows: tuple[SparseRow, ...]) -> int:
    return sum(len(row) for row in rows)


def _source_row_composition_is_zero(
    *,
    first_rows: tuple[SparseRow, ...],
    second_rows: tuple[SparseRow, ...],
    first_target_dimension: int,
    second_target_dimension: int,
) -> bool:
    sparse_result = _compose_sparse_rows(first_rows, second_rows)
    sparse_zero = all(not row for row in sparse_result)
    dense_work = len(first_rows) * max(first_target_dimension, 1)
    dense_work *= max(second_target_dimension, 1)
    if dense_work > 2_000_000:
        return sparse_zero

    dense_result = compose_rows(
        _dense_rows(first_rows, first_target_dimension),
        _dense_rows(second_rows, second_target_dimension),
    )
    return sparse_zero and _all_dense_zero(dense_result)


def _compose_sparse_rows(
    first_rows: tuple[SparseRow, ...],
    second_rows: tuple[SparseRow, ...],
) -> tuple[SparseRow, ...]:
    composed: list[SparseRow] = []
    for row in first_rows:
        image: SparseRow = {}
        for middle_index, coefficient in row.items():
            for target_index, entry in second_rows[middle_index].items():
                image[target_index] = (
                    image.get(target_index, Fraction(0)) + coefficient * entry
                )
                if image[target_index] == 0:
                    del image[target_index]
        composed.append(image)
    return tuple(composed)


def _dense_rows(
    rows: tuple[SparseRow, ...],
    dimension: int,
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(row.get(index, Fraction(0)) for index in range(dimension))
        for row in rows
    )


def _all_dense_zero(rows: tuple[tuple[Fraction, ...], ...]) -> bool:
    return all(all(entry == 0 for entry in row) for row in rows)


def _sparse_row_formula(row: SparseRow, basis: tuple[str, ...]) -> str:
    if not row:
        return "0"
    parts: list[str] = []
    for index, coefficient in sorted(row.items()):
        basis_name = basis[index]
        if coefficient == 1:
            parts.append(basis_name)
        elif coefficient == -1:
            parts.append(f"-{basis_name}")
        else:
            parts.append(f"{coefficient}*{basis_name}")
    return " + ".join(parts).replace("+ -", "- ")


def _sparse_row_record(row: SparseRow, basis: tuple[str, ...]) -> dict[str, Any]:
    return {
        "formula": _sparse_row_formula(row, basis),
        "sparse_coordinates": _sparse_row_json(row),
        "nonzero": bool(row),
    }


def _sparse_row_json(row: SparseRow) -> dict[str, int | str]:
    return {
        str(index): _fraction_to_json(coefficient)
        for index, coefficient in sorted(row.items())
        if coefficient != 0
    }


def _dense_sparse_row_json(row: SparseRow, dimension: int) -> list[int | str]:
    return [
        _fraction_to_json(row.get(index, Fraction(0)))
        for index in range(dimension)
    ]


def _sparse_rows_record(rows: tuple[SparseRow, ...]) -> dict[str, Any]:
    return {
        "row_count": len(rows),
        "nnz": _sparse_rows_nnz(rows),
        "rows": [_sparse_row_json(row) for row in rows],
    }


def _pivot_rows_record(rows: dict[int, SparseRow]) -> dict[str, Any]:
    return {
        "rank": len(rows),
        "pivot_rows": [
            {"pivot": pivot, "row": _sparse_row_json(row)}
            for pivot, row in sorted(rows.items())
        ],
    }


def _fraction_to_json(value: Fraction) -> int | str:
    value = Fraction(value)
    if value.denominator == 1:
        return value.numerator
    return f"{value.numerator}/{value.denominator}"


def _memory_notes(thresholds: Exp011Thresholds) -> str:
    if thresholds.max_memory_gb is None:
        return "Memory was controlled indirectly by raw-term and matrix thresholds."
    return (
        "max_memory_gb was recorded as a requested threshold; this no-new-"
        "dependency runner controls memory indirectly by raw-term and matrix "
        "thresholds."
    )


def _pretty_checks(checks: dict[str, Any]) -> str:
    return "\n".join(f"{key}: {value}" for key, value in sorted(checks.items()))


def _tex_escape(value: Any) -> str:
    return str(value).replace("\\", r"\textbackslash{}").replace("_", r"\_")


def _read_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_to_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return _fraction_to_json(value)
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    return value
