# subplan011: Experiment 011 For V2-Cell Search Without Applying Q

## 0. Plan-Only Boundary

This file is only an experiment plan. It does not run Experiment 011, create a
new experiment directory, write result files, modify Experiment 009 or
Experiment 010 outputs, or change any claim status.

The future experiment target is:

```text
experiments/011-v2-cells-no-Q/
```

The intended runner is:

```text
experiments/011-v2-cells-no-Q/run.py
```

An optional helper module may be added later if the implementation needs a
narrow reusable surface:

```text
src/jordan_qh/v2_cells_no_q.py
```

Experiment 011 is a bounded computational search for formal degree `2`
attaching-cell candidates in the first-layer full dg Jordan algebra. It is not
a Quillen homology computation after applying indecomposables, and it must not
grow into a general Jordan operad resolution framework.

## 1. Stage Goal

Work over:

```text
QQ
```

with the nonunital square-zero Jordan algebra:

```text
J = Jord<x,y> / (x^2, xy, y^2).
```

The first-layer dg Jordan algebra is:

```text
A^(1) = Jord<x, y, r_xx, r_xy, r_yy>
```

with:

```text
|x| = |y| = 0
|r_xx| = |r_xy| = |r_yy| = 1
```

and differential:

```text
d(x) = d(y) = 0
d(r_xx) = x^2
d(r_xy) = xy
d(r_yy) = y^2
```

The primary object is the old first homology in the full first-layer algebra,
computed weight-by-weight:

```text
H1_old,w = ker(d1,w) / im(d2_old,w).
```

More invariantly, this is the weight-`w` part of the ordinary homology of the
first-layer dg algebra:

```text
H_{1,w}^{(1)} := H_1(A^(1))_w
              = ker(d : A^(1)_{1,w} -> A^(1)_{0,w})
                / im(d : A^(1)_{2,w} -> A^(1)_{1,w}).
```

The runner-friendly name `H1_old,w` is not a new homology theory. The word
`old` only emphasizes that no degree `2` `s`-cells have been attached yet.

Here:

```text
C0,w = A^(1)_{0,w}
C1,w = A^(1)_{1,w}
C2_old,w = A^(1)_{2,w}
d1,w = d restricted to C1,w -> C0,w
d2_old,w = d restricted to C2_old,w -> C1,w
```

The word `old` means that `C2_old,w` uses only the old generators:

```text
x, y, r_xx, r_xy, r_yy
```

No new degree `2` cells are included when computing `C2_old,w`.

For every nonzero class:

```text
[z_i] in H1_old,w
```

the future experiment records a formal degree `2` cell candidate:

```text
|s_i| = 2
wt(s_i) = w
d(s_i) = z_i
```

The experiment stops there. It does not attach the `s_i`, does not construct
`A^(2)`, does not search for `V3, V4, ...`, and does not apply `Q`.

Allowed result language:

```text
For completed weights among the requested range w <= W, Experiment 011 found
the listed formal V2-cell candidates in A^(1).
```

Forbidden result language:

```text
Experiment 011 proves the full V2 layer.
No further degree 2 cells occur after weight W.
The infinite-weight computation is complete.
```

## 2. Source Evidence And Relation To Earlier Experiments

This plan is based on prior design discussion and is intended to stand alone as
a repo-local experiment plan.

Local repo evidence fixes the boundary:

- `researchplan/subplan009.md` computes a bounded quasi-free replacement for
  the same two-generator square-zero algebra and then applies `Q` to obtain a
  bounded chain complex through higher degrees.
- `researchplan/subplan010.md` narrows to a low-degree `H1` presentation-stress
  diagnostic after applying `Q`.
- Experiment 011 is different from both: it stays inside the full old
  first-layer dg Jordan algebra `A^(1)` and computes
  `ker(d1,w) / im(d2_old,w)` before applying `Q`.
- Agreement with Experiment 009 in low weights is only a sanity check.
  Experiment 011 must not use Experiment 009 output as an input or authority.

This plan produces bounded computational evidence only. It should not modify
files in:

```text
theory/claims/
```

## 3. Scope Boundary

In scope:

- exact rational arithmetic over `QQ`;
- the nonunital square-zero convention;
- homogeneous product-weight blocks in `A^(1)`;
- enumeration of commutative nonassociative monomials modulo the linearized
  Jordan identity;
- the chain fragment `C2_old,w -> C1,w -> C0,w`;
- mandatory non-boundary certificates for every reported cycle;
- JSON, cache, checkpoint, log, and TeX report artifacts generated from the
  same result object;
- independent per-weight completion, failure, skip, and resume behavior.

Out of scope:

- applying indecomposables `Q`;
- computing `Q(A^(1))`, `Q(tilde J)`, or a `Q`-complex differential;
- attaching the reported `s_i` and continuing to `A^(2)`;
- constructing `V3, V4, ...`;
- computing `H2_new` or any higher new-cell layer;
- adding new default package dependencies;
- using floating-point rank, kernel, RREF, or certificate computations;
- claiming stabilization, termination, or global completeness from finite
  weights;
- marking any theory claim as `checked`.

The default committed runner should stay pure Python and exact, reusing
existing local exact-arithmetic and low-weight Jordan surfaces where practical:

```text
src/jordan_qh/linear_algebra.py
src/jordan_qh/low_weight_jordan.py
```

Exploratory tools listed in `codex/local-math-tools.md` may be used as
non-authoritative support only after re-verifying their paths. Any promoted
tool output must be replayable and must record backend, version or path,
input, output location, and reproducibility notes.

## 4. Fixed Mathematical Conventions

### 4.1 Backend Convention Audit

This experiment follows the existing low-weight Jordan backend convention: it
treats the algebra as an ordinary commutative nonassociative Jordan algebra
equipped with a signed derivation differential.

The output should be interpreted relative to that backend convention. A
separate theory check is required before identifying this bounded backend
exactly with the fully graded operadic dg Jordan convention, where Koszul signs
may affect products involving odd-degree generators.

### 4.2 Weight, Homology, And Matrix Conventions

Use product weight:

```text
wt(x) = wt(y) = 1
wt(r_xx) = wt(r_xy) = wt(r_yy) = 2
wt(ab) = wt(a) + wt(b)
```

The differential is extended by the signed derivation rule:

```text
d(ab) = d(a)b + (-1)^|a| a d(b).
```

The differential preserves product weight. Therefore each weight `w` can be
processed independently.

For each tested weight, define:

```text
Z1,w = ker(d1,w)
B_old,w = im(d2_old,w)
H1_old,w = Z1,w / B_old,w
```

A formal cell is recorded exactly when:

```text
z_i in ker(d1,w)
z_i not in im(d2_old,w)
```

Equivalently:

```text
[z_i] != 0 in H1_old,w.
```

Use deterministic formal cell names:

```text
s2_{global_index:05d}_w{w}
```

where `global_index` starts at `00001` and increments over all accepted cells in
deterministic weight-then-representative order. This follows the existing
Experiment 009 naming pattern. For example:

```text
s2_00001_w8
s2_00002_w8
```

Use this matrix convention wherever possible:

```text
source_rows_target_coordinates
```

For a map `d: S -> T`, each row corresponds to a basis element of `S`, and the
row entries are coordinates in the chosen basis of `T`.

Use mathematical comma notation in prose, but never in runner keys or JSON
fields. Use these runner-friendly names:

```text
math notation     runner/cache key
C0,w              C0_w
C1,w              C1_w
C2_old,w          C2_old_w
d1,w              d1_w
d2_old,w          d2_old_w
Z1,w              Z1_w
B_old,w           B_old_w
H1_old,w          H1_old_w
rem_B_old,w       rem_B_old_w
```

The JSON examples below use underscore-style keys when a name appears as a
field name. Formula text may still use the mathematical shorthand.

## 5. Algorithm

The computation is weight-blocked. For each tested weight `w`, run the
following steps independently.

### 5.1 Enumerate Homogeneous Spaces

Enumerate raw commutative nonassociative monomials in:

```text
x, y, r_xx, r_xy, r_yy
```

with fixed homological degree and product weight:

```text
A^(1)_{0,w}
A^(1)_{1,w}
A^(1)_{2,w}
```

The intended enumeration should reuse the low-weight Jordan backend pattern:

1. Generate canonical commutative nonassociative terms.
2. Assign each term `(degree, weight)`.
3. Group terms by `(degree, weight)`.
4. Construct the quotient by the linearized Jordan identity.

### 5.2 Quotient By Linearized Jordan Identities

For `p in {0, 1, 2}`, construct:

```text
A^(1)_{p,w}
= raw terms of degree p and weight w
  modulo linearized Jordan identity relations.
```

All linear algebra must use exact rational arithmetic. The output must record
the chosen quotient basis for each completed `(p,w)`, or record a reproducible
basis identifier with enough cached data to reconstruct it.

### 5.3 Construct Differential Matrices

Construct:

```text
d1,w : C1,w -> C0,w
d2_old,w : C2_old,w -> C1,w
```

Every JSON result file must record the matrix convention:

```text
source_rows_target_coordinates
```

### 5.4 Compute Cycles

Compute:

```text
Z1,w = ker(d1,w).
```

Since matrices use source rows, the kernel calculation must solve the linear
equations for the map `C1,w -> C0,w`.

Record:

```text
dim C1,w
rank d1,w
dim Z1,w
```

and verify:

```text
dim Z1,w = dim C1,w - rank d1,w.
```

### 5.5 Compute Old Boundaries

Compute:

```text
B_old,w = im(d2_old,w) subset C1,w.
```

Record:

```text
dim C2_old,w
rank d2_old,w
dim B_old,w
```

and verify:

```text
dim B_old,w = rank d2_old,w.
```

Also verify the chain condition:

```text
mathematically: d1,w o d2_old,w = 0
```

With the `source_rows_target_coordinates` convention, implement this as:

```text
d2_old_matrix @ d1_matrix = 0
```

Using the existing Python helper, this is:

```text
compose_rows(d2_old_rows, d1_rows)
```

Equivalently:

```text
B_old,w subset Z1,w.
```

### 5.6 Compute Quotient Representatives

Compute:

```text
H1_old,w = Z1,w / B_old,w.
```

Recommended exact sparse procedure:

1. Compute a sparse basis of `Z1,w`.
2. Compute an RREF row basis of `B_old,w`.
3. Initialize the quotient-selection row space with the RREF row basis of
   `B_old,w`.
4. Iterate through the cycle basis in deterministic order.
5. For each candidate cycle `z`, reduce it only against the RREF row basis of
   `B_old,w` and call the result `boundary_remainder`.
6. Reduce the same candidate cycle against the current quotient-selection row
   space and call the result `selection_remainder`.
7. Accept `z` as a quotient representative exactly when
   `selection_remainder != 0`.
8. For an accepted `z`, record `boundary_remainder != 0` as the mandatory
   non-boundary certificate.
9. After acceptance, add a normalized form of `selection_remainder` to the
   quotient-selection row space for later independence testing.

Do not overwrite `boundary_remainder` with `selection_remainder`: the first is
the certificate that `z` is not in `B_old,w`; the second is only the running
selection test for independence modulo already accepted representatives.

Record:

```text
n_w = dim H1_old,w.
```

The number `n_w` is basis-independent inside the completed finite computation,
but the displayed representatives `z_i` form one deterministic choice depending
on the chosen term order, quotient basis, representative-selection order, and
RREF convention.

This is also the number of formal degree `2` cells in weight `w`:

```text
#{s_i : wt(s_i) = w} = n_w.
```

### 5.7 Generate Formal V2-Cell Records

For each accepted quotient representative `z_i`, generate:

```text
name = s2_{global_index:05d}_w{w}
degree = 2
weight = w
d(name) = z_i
```

The record must include:

- full cycle formula for `z_i` in the chosen quotient basis;
- coordinate vector of `z_i` in the `C1,w` basis;
- raw lifted expression in old generators when feasible;
- mandatory RREF remainder certificate proving `z_i not in B_old,w`.

### 5.8 Stop After V2

Do not attach the formal `s_i`. Do not compute:

```text
H2_new
V3
V4
...
```

Do not apply:

```text
Q(A^(1)).
```

The primary result is only the completed-weight collection of:

```text
H1_old,w = ker(d1,w) / im(d2_old,w).
```

## 6. Mandatory Non-Boundary Certificates

Every reported representative `z_i` must have an auditable certificate proving:

```text
z_i not in B_old,w.
```

### 6.1 RREF Remainder Certificate

Let `R_B,w` be the RREF row basis for:

```text
B_old,w = im(d2_old,w) subset C1,w.
```

Reduce `z_i` against `R_B,w` and record:

```text
rem_B_old,w(z_i).
```

The certificate is valid exactly when:

```text
rem_B_old,w(z_i) != 0.
```

For each `z_i`, store at least:

```json
{
  "certificate_type": "rref_remainder",
  "B_old_rref_pivots": ["..."],
  "boundary_remainder_mod_B_old": "...",
  "boundary_remainder_nonzero": true,
  "not_in_B_old": true
}
```

If the RREF basis is large, store the full sparse RREF in a cache file and
record a stable checksum or cache path in the cell record.

### 6.2 Optional Dual Functional Certificate

As a secondary verification, the runner may construct a linear functional:

```text
lambda_i : C1,w -> QQ
```

such that:

```text
lambda_i(B_old,w) = 0
lambda_i(z_i) = 1.
```

If implemented, record:

```json
{
  "optional_dual_certificate": {
    "status": "computed",
    "lambda_sparse_coordinates": "...",
    "lambda_on_B_old": "0",
    "lambda_on_z": "1"
  }
}
```

If not implemented, record:

```json
{
  "optional_dual_certificate": {
    "status": "not_computed"
  }
}
```

The RREF remainder certificate remains mandatory.

## 7. Future Output Files

If implemented later, the experiment should write:

```text
experiments/011-v2-cells-no-Q/results.json
experiments/011-v2-cells-no-Q/data/v2_cells_W{W}.json
experiments/011-v2-cells-no-Q/data/by_weight_W{W}.json
experiments/011-v2-cells-no-Q/tex/exp011_v2_cells_no_Q.tex
experiments/011-v2-cells-no-Q/logs/run_W{W}.log
```

Recommended cache and checkpoint locations:

```text
experiments/011-v2-cells-no-Q/cache/
experiments/011-v2-cells-no-Q/checkpoints/
```

### 7.1 `results.json`

The main result object should include:

```json
{
  "experiment_id": "EXP-011-v2-cells-no-Q",
  "experiment_directory": "experiments/011-v2-cells-no-Q/",
  "plan": "researchplan/subplan011.md",
  "field": "QQ",
  "arithmetic": "exact_rational",
  "applies_Q": false,
  "constructs_higher_cells_V3_plus": false,
  "primary_object": "H1_old in A^(1)",
  "matrix_convention": "source_rows_target_coordinates",
  "max_weight_requested": "...",
  "requested_weights": ["..."],
  "completed_weights": ["..."],
  "failed_weights": ["..."],
  "skipped_weights": ["..."],
  "not_tested_weights_in_requested_range": ["..."],
  "global_claims_modified": false,
  "finite_truncation_warning": "All conclusions are only for completed weights.",
  "by_weight_file": "data/by_weight_W{W}.json",
  "v2_cells_file": "data/v2_cells_W{W}.json",
  "tex_report": "tex/exp011_v2_cells_no_Q.tex",
  "checks": {
    "all_completed_weights_passed": "...",
    "all_reported_z_are_cycles": "...",
    "all_reported_z_have_nonzero_B_old_remainder": "...",
    "all_reported_classes_independent_mod_B_old": "...",
    "d_squared_zero_on_formal_s_cells": "..."
  }
}
```

### 7.2 `data/by_weight_W{W}.json`

Each completed weight record must contain at least:

```json
{
  "weight": "...",
  "status": "completed",
  "dim_C0": "...",
  "dim_C1": "...",
  "dim_C2_old": "...",
  "rank_d1": "...",
  "rank_d2_old": "...",
  "dim_Z1": "...",
  "dim_B_old": "...",
  "dim_H1_old": "...",
  "number_of_new_s_cells": "...",
  "runtime_seconds": "...",
  "memory_notes": "...",
  "matrix_stats": {
    "d1_rows": "...",
    "d1_cols": "...",
    "d1_nnz": "...",
    "d2_old_rows": "...",
    "d2_old_cols": "...",
    "d2_old_nnz": "..."
  },
  "basis_data": {
    "C0_basis": "...",
    "C1_basis": "...",
    "C2_old_basis": "..."
  },
  "cache_paths": {
    "quotient_space_cache": "...",
    "B_old_rref_cache": "..."
  },
  "checks": {
    "d2_old_matrix_times_d1_matrix_is_zero": "...",
    "dim_Z1_matches_rank_nullity": "...",
    "dim_B_old_matches_rank_d2_old": "...",
    "dim_H1_old_matches_quotient_count": "...",
    "all_cell_certificates_valid": "..."
  }
}
```

Failed weights must preserve diagnostic state:

```json
{
  "weight": "...",
  "status": "failed",
  "failure_stage": "...",
  "error_message": "...",
  "partial_outputs_preserved": true,
  "runtime_seconds": "...",
  "memory_notes": "..."
}
```

Skipped weights must record the threshold:

```json
{
  "weight": "...",
  "status": "skipped",
  "skip_reason": "...",
  "threshold_triggered": "...",
  "previous_completed_weight": "..."
}
```

### 7.3 `data/v2_cells_W{W}.json`

Each formal cell record must contain at least:

```json
{
  "name": "s2_{global_index:05d}_w{w}",
  "degree": 2,
  "weight": "...",
  "global_index": "...",
  "cycle_z": "...",
  "cycle_z_coordinates_in_C1_basis": "...",
  "cycle_z_raw_lift": "...",
  "d1_z_normal_form": "0",
  "boundary_remainder_mod_B_old": "...",
  "boundary_remainder_nonzero": true,
  "selection_remainder_mod_B_old_plus_accepted_reps": "...",
  "independent_mod_B_old_plus_previous_reps": true,
  "not_in_B_old": true,
  "certificate_type": "rref_remainder",
  "optional_dual_certificate": "..."
}
```

The value:

```json
"d1_z_normal_form": "0"
```

means that `d1,w(z_i)` reduces to zero in the quotient basis for `C0,w`.

The value:

```json
"boundary_remainder_mod_B_old": "..."
```

must be a nonzero coordinate vector in the chosen `C1,w` basis, or a reference
to a cache object containing that vector.

### 7.4 TeX Report

The TeX report:

```text
tex/exp011_v2_cells_no_Q.tex
```

must be generated from the same in-memory result object as the JSON files. It
must include:

- experiment ID;
- target algebra;
- definition of `A^(1)`;
- statement that `Q` is not applied;
- statement that `V3, V4, ...` are not constructed;
- table by weight;
- list of formal `s_i`;
- formula for every `d(s_i) = z_i`;
- non-boundary certificate for every `z_i`;
- validation summary;
- finite-weight boundary statement.

The report must contain this finite-weight boundary:

```text
All conclusions in this report are restricted to weights with status completed.
Weights not tested, skipped, or failed are not used to infer any global
statement. This computation does not prove stabilization, termination, or
absence of further degree 2 attaching generators in untested weights.
```

### 7.5 Logs, Caches, And Checkpoints

Recommended log fields:

```text
start time
end time
mode
max weight
per-weight status
raw term counts
quotient dimensions
matrix dimensions
matrix nnz
rank computations
RREF timings
memory notes
checkpoint paths
failure or skip reasons
```

Recommended cache objects:

```text
cache/quotient_space_deg{p}_w{w}.json
cache/d1_w{w}.json
cache/d2_old_w{w}.json
cache/B_old_rref_w{w}.json
cache/Z1_basis_w{w}.json
cache/H1_old_reps_w{w}.json
```

Recommended checkpoint object:

```text
checkpoints/weight_{w}_status.json
```

A completed checkpoint must contain enough information to skip recomputation of
weight `w` during resume mode.

## 8. Planned Run Modes And Performance Controls

The computation must not assume stabilization or high-weight termination.
Conclusions are restricted to completed weights.

### 8.1 Low-Weight Dry Run

Run first with:

```text
W = 8
```

or:

```text
W = 10
```

Purpose:

- verify enumeration;
- verify quotient-space construction;
- verify `d^2 = 0`;
- verify RREF remainder certificates;
- inspect output size;
- check TeX generation.

Recommended command shape:

```text
python experiments/011-v2-cells-no-Q/run.py --max-weight 8 --mode dry
```

### 8.2 Medium Validation Run

Run next with:

```text
W = 12
```

or:

```text
W = 14
```

Purpose:

- validate checkpointing;
- validate resume mode;
- compare low-weight records against the dry run;
- test memory behavior;
- test report generation with larger tables.

Recommended command shape:

```text
python experiments/011-v2-cells-no-Q/run.py --max-weight 14 --mode validation
```

### 8.3 Overnight Long Run

Run overnight with:

```text
W = 16
W = 18
W = 20
```

or use an adaptive feasible upper bound selected from matrix-size and memory
thresholds.

Recommended command shape:

```text
python experiments/011-v2-cells-no-Q/run.py --max-weight 20 --mode overnight --resume
```

### 8.4 Adaptive Stopping

The runner should support thresholds such as:

```text
--max-raw-terms-per-space
--max-quotient-dim
--max-matrix-nnz
--max-runtime-per-weight
--max-memory-gb
```

If a weight exceeds a threshold, record it as:

```text
skipped
```

or:

```text
failed
```

with a reason. Do not delete completed lower-weight data.

### 8.5 Per-Weight Independence

Each weight `w` must be processed and checkpointed independently. A failure at
weight `w+1` must not corrupt the completed result for weight `w`.

For every completed weight, record:

```text
dim C0,w
dim C1,w
dim C2_old,w
rank d1,w
rank d2_old,w
dim Z1,w
dim B_old,w
dim H1_old,w
runtime_seconds
memory_notes
matrix_nnz
basis_cache_paths
rref_cache_paths
```

### 8.6 Resume Mode

The runner should support:

```text
--resume
```

Resume mode should:

1. Read checkpoint files.
2. Skip completed weights whose checks passed.
3. Recompute failed weights only if requested.
4. Continue from the next incomplete weight.
5. Preserve earlier completed records.

## 9. Validation Requirements

All completed weights must pass the following checks.

### 9.1 Cycle Check

For every reported representative `z_i`:

```text
d1,w(z_i) = 0.
```

The normal form of `d1,w(z_i)` in `C0,w` must be recorded as zero.

### 9.2 Non-Boundary Check

For every reported representative `z_i`:

```text
rem_B_old,w(z_i) != 0.
```

This proves:

```text
z_i not in B_old,w.
```

### 9.3 Quotient Independence Check

The reported representatives in weight `w` must be linearly independent in:

```text
Z1,w / B_old,w.
```

Equivalently, if the representatives are `z_1, ..., z_n`, then:

```text
dim(B_old,w + <z_1, ..., z_n>) = dim B_old,w + n.
```

Also verify:

```text
n = dim Z1,w - dim B_old,w.
```

### 9.4 Formal d-Squared Check

Because `d(s_i) = z_i`, verify:

```text
d^2(s_i) = d(z_i) = 0.
```

This is the same as the cycle check and should be recorded as a formal
attaching-cell check.

### 9.5 Chain Condition Check

Verify:

```text
mathematically: d1,w o d2_old,w = 0
source-row matrix implementation: d2_old_matrix @ d1_matrix = 0
existing helper implementation: compose_rows(d2_old_rows, d1_rows)
```

for every completed weight.

### 9.6 Rank-Nullity Checks

For every completed weight, verify:

```text
dim Z1,w = dim C1,w - rank d1,w
dim B_old,w = rank d2_old,w
dim H1_old,w = dim Z1,w - dim B_old,w
```

### 9.7 Sanity Comparison With Experiment 009

For low weights, compare the number of degree `2` cells found by Experiment
011 with the degree `2` cell count produced during Experiment 009.

Rules:

- Experiment 011 must not use Experiment 009 output as input.
- Experiment 011 must not treat Experiment 009 as an authority.
- Any discrepancy must be recorded as a diagnostic issue.
- Any agreement must be recorded only as compatibility of two bounded
  computations.

### 9.8 Exact Arithmetic Check

All computations must use exact rational arithmetic. In Python, this means
`fractions.Fraction` or an equivalent exact rational backend. Floating-point
rank, kernel, RREF, or certificate computation is not acceptable.

### 9.9 Report-Language Check

The generated report must be scanned for forbidden global phrasing.

Forbidden statements include:

```text
No more cells occur after weight W.
The computation proves the full V2 layer.
The infinite-weight case is complete.
H1_old has global dimension ...
```

Allowed statements include:

```text
For completed weights among the requested range w <= W, the computed values are ...
Weight w was skipped.
Weight w failed at stage ...
No conclusion is drawn for untested weights.
```

### 9.10 Reproducibility Check

Each completed weight must be independently reproducible from:

- old generator list;
- weight convention;
- quotient basis construction;
- differential construction;
- exact rational matrices;
- RREF cache or reproducible RREF computation.

The result for weight `w` must not depend on successful completion of any
higher weight.

## 10. Acceptance Criteria For Future Experiment 011

The future experiment has a useful completed run only when:

1. The experiment directory points back to `researchplan/subplan011.md`.
2. The runner uses exact rational arithmetic over `QQ`.
3. Every completed weight outputs `dim H1_old,w`.
4. Every reported formal cell outputs `|s_i| = 2`, `wt(s_i) = w`, and
   `d(s_i) = z_i`.
5. Every reported `s_i` has a full cycle formula for `z_i`.
6. Every reported `z_i` has a mandatory RREF remainder certificate showing
   `z_i not in B_old,w`.
7. `results.json` distinguishes completed, failed, skipped, and not-tested
   weights.
8. The TeX report distinguishes completed, failed, skipped, and not-tested
   weights.
9. All completed weights pass the cycle, non-boundary, chain-condition,
   rank-nullity, and quotient-independence checks.
10. The report contains no conclusion about untested weights.
11. The report contains no theorem-like statement about the infinite-weight
    object.
12. The report explicitly states that Experiment 011 does not apply `Q`.
13. The report explicitly states that Experiment 011 does not construct
    `V3, V4, ...`.
14. Each completed weight is independently reproducible.

Future implementation verification:

```text
python -m pytest
python -m ruff check .
python experiments/011-v2-cells-no-Q/run.py --max-weight 8 --mode dry
python scripts/check_claims.py
```

For this plan-only change, the required verification is only:

```text
git diff --check -- researchplan/subplan011.md
```

## 11. Non-Goals

- Do not run Experiment 011 as part of creating or editing this plan.
- Do not create `experiments/011-v2-cells-no-Q/` while only writing the plan.
- Do not modify Experiment 009 or Experiment 010 result files.
- Do not use this plan to reinterpret `H2` through `H5` from Experiment 009.
- Do not promote `CLAIM-0002` or any other claim to `checked`.
- Do not claim presentation invariance for all cofibrant replacements.
- Do not claim the full infinite `V2` layer has been computed.
- Do not add a general Jordan operad resolution implementation.
- Do not add new default dependencies.

## 12. Interpretation Template

If the future dry run completes for `W = 8`, use:

```text
Experiment 011 completed the V2-cell candidate search inside A^(1) for
completed weights among the requested range w <= 8. The listed cells are
representatives for nonzero classes in H1_old,w = ker(d1,w) / im(d2_old,w) for
completed weights only. This is bounded computational evidence, not a global
statement about all weights.
```

If a higher-weight run skips or fails at some weight, use:

```text
Experiment 011 completed the listed lower weights and preserved their
certificates. Weights marked skipped or failed are not used for any mathematical
conclusion.
```

If the Experiment 009 sanity comparison agrees in low weights, use:

```text
The low-weight cell counts agree with the corresponding bounded Experiment 009
diagnostic. This is a compatibility check between two finite computations, not
an independent proof of the infinite object.
```

If the sanity comparison disagrees, use:

```text
The Experiment 011 low-weight output disagrees with the corresponding
Experiment 009 diagnostic. Treat this as a diagnostic issue and inspect the
enumeration, quotient basis, matrix convention, and boundary-certificate
construction before drawing any conclusion.
```
