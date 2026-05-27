# subplan010: Experiment 010 For H1 Presentation-Stress Diagnostics

## 0. Plan-Only Boundary

This file is only an experiment plan. It does not run Experiment 010, create a
new experiment directory, write result files, modify Experiment 009 outputs, or
change any claim status.

The future experiment target is:

```text
experiments/010-h1-stability-square-zero-two-generator/
```

Experiment 010 is a low-degree presentation-stress diagnostic. It is not a new
quasi-free replacement runner and must not grow into a general Jordan operad
resolution framework.

The plan follows Experiment 009 but narrows the question. Experiment 009
computed a bounded chain complex through `H5`; Experiment 010 should test only
whether the computed `H1` remains stable under controlled presentation changes
and redundant-relation refinements.

## 1. Stage Goal

Work over `QQ` with the nonunital square-zero Jordan algebra:

```text
J = k{x,y}/(x^2, xy, y^2)
```

The diagnostic target is:

```text
H1 = ker(partial_1^Q) / im(partial_2^Q).
```

The expected stable dimension is:

```text
dim H1 = 3.
```

The stronger target is not merely dimension `3`; it is a machine-checkable
identification of the stable `H1` classes with the canonical quadratic relation
space:

```text
Sym^2(<x,y>) = <x^2, xy, y^2>.
```

Allowed result language:

```text
Experiment 010 supports H1 stability in this bounded square-zero example.
```

Forbidden result language:

```text
Experiment 010 proves H1 presentation invariance.
```

## 2. Source Evidence And Trust Boundary

This plan is based on the shared ChatGPT design note titled:

```text
ChatGPT - H_1 stability experiment design
```

The useful design points from that note are:

- do not merely recompute `H1`;
- test dimension stability, basis-class stability, and presentation-change
  stability separately;
- include a naive redundant-relation case expected to produce a false extra
  `H1` class;
- repair that false class by adding the corresponding degree `2` syzygy cell;
- test deterministic linear changes of generators and check the induced
  `Sym^2(GL2)` action on the relation space;
- treat the result as evidence, not theorem-level proof.

Local repo evidence fixes the boundary:

- `researchplan/subplan009.md` fixes the algebra as nonunital square-zero over
  `QQ`.
- Experiment 009 records `H1 = 3` for `W = 6, 7, 8`, but its full `H0` through
  `H5` output is not stable across those weight bounds.
- The Experiment 009 `W = 6, 7, 8` fact is supporting context only. It is not
  an Experiment 010 acceptance condition.
- `experiments/006-presentation-invariance-j3/` shows that a naive one-step
  presentation diagnostic can create a false extra `H1` class.
- `theory/claims/CLAIM-0002-indecomposables-left-adjoint.md` is still `draft`,
  so this experiment should not upgrade claims about `Q(J)=J/J^2`.

## 3. Scope Boundary

In scope:

- exact rational arithmetic over `QQ`;
- nonunital square-zero convention;
- only the low-degree complex needed for `H1`, normally `C2 -> C1 -> C0`;
- deterministic presentation changes and deterministic redundant relations;
- expected-fail controls that demonstrate how missing syzygies create false
  classes;
- JSON and Markdown or TeX summaries that distinguish strong passes, weak
  dimension-only passes, expected-fail controls, and unexpected failures.

Out of scope:

- computing or reinterpreting `H2` through `H5`;
- increasing Experiment 009 weight bounds to `W = 9` or `W = 10`;
- treating Experiment 010 as a full cofibrant replacement computation;
- changing files in `theory/claims/`;
- adding new default package dependencies;
- treating CAS output as authoritative unless a later plan promotes a
  replayable backend.

The default committed runner, if implemented later, should stay pure Python and
exact. Exploratory tools listed in `codex/local-math-tools.md` may be used as
non-authoritative cross-checks only after re-verifying their paths.

## 4. Fixed Conventions And Certificates

Use:

```text
C0 = <x, y>
C1_min = <r_xx, r_xy, r_yy>
```

with full differentials:

```text
d(r_xx) = x*x
d(r_xy) = x*y
d(r_yy) = y*y
```

After applying indecomposables:

```text
partial_1^Q = 0 : C1 -> C0.
```

Therefore, for each presentation model with `partial_1^Q = 0`:

```text
H1 = C1 / im(partial_2^Q).
```

Fix these canonical orders for every future artifact:

```text
canonical_relation_basis = ["x^2", "xy", "y^2"]
minimal_relation_cell_basis = ["r_xx", "r_xy", "r_yy"]
matrix_convention = "source_rows_target_coordinates"
```

For redundant-relation cases, the runner must record a relation-coefficient
map:

```text
rho : C1 -> <x^2, xy, y^2>
```

where source rows are `C1` basis elements and target coordinates use
`canonical_relation_basis`.

A redundant-relation case passes the strong basis-alignment certificate only
when:

```text
im(partial_2^Q) = ker(rho)
```

as exact subspaces over `QQ`.

For `GL2(QQ)` generator-change cases, the runner must record:

```text
expected_sym2_matrix_source_rows
observed_h1_basis_matrix_source_rows
```

with rows ordered by the changed relation basis and columns ordered by
`canonical_relation_basis`. Strong pass requires exact matrix equality over
`QQ`.

## 5. Outcome Statuses

Every case in the future `results.json` must use exactly one of these outcome
statuses:

```text
pass_strong
pass_weak_dimension_only
expected_fail_observed
unexpected_fail
unexpected_pass
```

Definitions:

- `pass_strong`: the expected dimension and all required basis-alignment or
  matrix certificates pass.
- `pass_weak_dimension_only`: `dim H1 = 3`, but basis alignment is absent or
  not certified.
- `expected_fail_observed`: the missing-syzygy control produces the planned
  false class, normally `dim H1 = 4`.
- `unexpected_fail`: a normal case fails its expected dimension, rank, or
  certificate check.
- `unexpected_pass`: an expected-fail control does not produce the planned
  false class.

The overall experiment should report:

```text
minimum_passed = true
```

only when the MVP groups pass with exact arithmetic and correct expected-fail
semantics.

The overall experiment should report:

```text
full_stress_test_passed = true
```

only when both MVP and extended groups pass.

## 6. Planned Test Groups

### MVP Group A: Minimal Presentation Baseline

Use:

```text
P_min = k{x,y}/(x^2, xy, y^2).
```

Record:

```text
rank partial_1^Q
rank partial_2^Q
dim H0
dim H1
H1 representatives
rho
```

Expected:

```text
rank partial_1^Q = 0
rank partial_2^Q = 0
dim H0 = 2
dim H1 = 3
outcome = pass_strong
```

The certificate is that the three minimal relation cells map to the identity
matrix under `rho`, using the canonical relation basis.

### MVP Group C: Naive Redundant-Relation Control

Add one redundant relation:

```text
q = (x+y)^2 = x^2 + 2xy + y^2
```

by adding a degree `1` cell:

```text
r_q
d(r_q) = (x+y)^2
```

Do not add the corresponding syzygy cell.

After applying `Q`, this creates:

```text
partial_1^Q(r_q) = 0
```

and therefore a false extra class.

Expected:

```text
C1_basis = ["r_xx", "r_xy", "r_yy", "r_q"]
C2_basis = []
rank partial_2^Q = 0
dim H1 = 4
is_expected_fail_control = true
outcome = expected_fail_observed
```

This is a calibration control. It is not a failed experiment when the false
extra class appears.

### MVP Group D: Repaired Redundant Relation

Start from Group C and add one degree `2` syzygy cell:

```text
s_q
d(s_q) = r_q - r_xx - 2*r_xy - r_yy + decomposable terms
```

After applying `Q`:

```text
partial_2^Q(s_q) = r_q - r_xx - 2*r_xy - r_yy.
```

Expected:

```text
C1_basis = ["r_xx", "r_xy", "r_yy", "r_q"]
C2_basis = ["s_q"]
rank partial_2^Q = 1
dim H1 = 3
outcome = pass_strong
```

The basis-alignment certificate is:

```text
im(partial_2^Q) = ker(rho)
```

where:

```text
rho(r_xx) = [1, 0, 0]
rho(r_xy) = [0, 1, 0]
rho(r_yy) = [0, 0, 1]
rho(r_q)  = [1, 2, 1]
```

### MVP Group F: Truncation-Depth Diagnostic

Track:

```text
h1(N) = dim H1(C_{<=N}^Q)
```

for `N = 1, 2, 3`, where `N` means the maximum available resolution degree.

Expected patterns:

Minimal presentation:

```text
h1(1) = 3
h1(2) = 3
h1(3) = 3
```

Redundant relation without syzygy:

```text
h1(1) = 4
outcome = expected_fail_observed
```

Redundant relation with syzygy:

```text
h1(1) = 4
h1(2) = 3
h1(3) = 3
outcome = pass_strong
```

If a repaired redundant case remains unstable for `N >= 2`, the likely problem
is that the syzygy layer is missing or the extracted linear differential is
wrong.

### Extended Group B: Linear Change Of Generators

Choose deterministic matrices in `GL2(QQ)`:

```text
g1 = [[1, 1], [1, -1]]
g2 = [[1, 2], [0, 1]]
g3 = [[2, 1], [1, 1]]
```

For:

```text
u = a*x + b*y
v = c*x + d*y
```

the quadratic relation basis transforms as:

```text
u^2 = a^2*x^2 + 2ab*xy + b^2*y^2
uv  = ac*x^2 + (ad+bc)*xy + bd*y^2
v^2 = c^2*x^2 + 2cd*xy + d^2*y^2
```

Expected:

```text
dim H1 = 3
observed_h1_basis_matrix_source_rows = expected_sym2_matrix_source_rows
outcome = pass_strong
```

A case with dimension `3` but without exact `Sym^2(g)` certification must be:

```text
outcome = pass_weak_dimension_only
```

### Extended Group E: Multiple Redundant Relations

Add `m` deterministic redundant quadratic relations:

```text
q_i = a_i*x^2 + b_i*xy + c_i*y^2
```

with corresponding degree `1` cells `r_q_i` and degree `2` syzygy cells:

```text
d(s_i) = r_q_i - a_i*r_xx - b_i*r_xy - c_i*r_yy + decomposable terms.
```

Use deterministic coefficient rows in this order:

```text
q_1 = x^2 + 2xy + y^2
q_2 = x^2 - y^2
q_3 = 2x^2 + xy
q_4 = xy + 3y^2
q_5 = -x^2 + xy + y^2
```

Run prefixes with:

```text
m = 1, 2, 3, 5
```

Expected for each repaired case:

```text
dim C1 = 3 + m
rank partial_2^Q = m
dim H1 = 3
im(partial_2^Q) = ker(rho)
outcome = pass_strong
```

The purpose is to verify that redundant relation cells can enlarge `C1`, while
the matching syzygies remove exactly the artificial `H1` classes.

## 7. Future Result Record Shape

If implemented later, `expected.json` should contain setup expectations only:

```json
{
  "status": "expected_setup",
  "experiment": "EXP-010-h1-stability-square-zero-two-generator",
  "plan": "researchplan/subplan010.md",
  "base_field": "QQ",
  "category": "nonunital Jordan algebras",
  "target_algebra": "k{x,y}/(x^2, xy, y^2)",
  "focus": "low-degree H1 presentation-stress diagnostic",
  "canonical_relation_basis": ["x^2", "xy", "y^2"],
  "minimal_relation_cell_basis": ["r_xx", "r_xy", "r_yy"],
  "matrix_convention": "source_rows_target_coordinates",
  "expected_stable_dim_H1": 3,
  "expected_fail_controls": ["redundant_relation_without_syzygy"],
  "do_not_prefill": [
    "computed_case_results",
    "matrices",
    "basis_alignment_certificates",
    "outcomes"
  ]
}
```

`results.json` should be produced only by the future runner. Each case entry
must include:

```text
case_id
case_group
outcome
is_expected_fail_control
C1_basis
C2_basis
partial_2_Q_source_rows
rank_partial_2_Q
dim_H1
relation_coefficient_map_source_rows
basis_alignment_passed
```

Optional for `GL2` cases:

```text
sym2_check.expected_sym2_matrix_source_rows
sym2_check.observed_h1_basis_matrix_source_rows
sym2_check.passed
```

The top-level summary should include:

```text
minimum_passed
full_stress_test_passed
evidence_only = true
claim_files_modified = false
```

## 8. Future Implementation Phases

### Phase 1: Scaffold Experiment 010

Create only future experiment files:

```text
experiments/010-h1-stability-square-zero-two-generator/experiment.md
experiments/010-h1-stability-square-zero-two-generator/expected.json
experiments/010-h1-stability-square-zero-two-generator/run.py
experiments/010-h1-stability-square-zero-two-generator/results.json
```

Initial `results.json` may honestly say:

```json
{
  "status": "not run yet",
  "passed": null,
  "notes": "Experiment 010 is planned but has not been executed."
}
```

### Phase 2: Implement Minimal Low-Degree Linear Algebra

Implement only the low-degree chain complex needed for:

```text
C2 -> C1 -> C0.
```

Use exact row reduction and `fractions.Fraction` or existing exact helpers.
Do not add a new dependency.

### Phase 3: Implement MVP Groups

Implement Groups A, C, D, and F first. These groups establish that the future
runner can distinguish:

```text
stable H1 = 3
```

from:

```text
false extra H1 = 4 caused by a missing syzygy.
```

### Phase 4: Implement Extended Stress Groups

Implement Groups B and E only after the MVP passes. Record matrices in stable
source-row target-coordinate order so that future diffs remain readable.

### Phase 5: Generate A Short Report

Generate a concise Markdown or TeX report from the same result object as
`results.json`. The report should include:

```text
Conventions
Outcome statuses
MVP diagnostics
Extended stress tests
Basis-alignment certificates
Limitations
```

The report must not duplicate large raw JSON payloads.

## 9. Acceptance Criteria For Future Experiment 010

The future experiment has a useful MVP only when:

1. The experiment directory points back to `researchplan/subplan010.md`.
2. The runner uses exact rational arithmetic over `QQ`.
3. Group A returns `outcome = pass_strong`.
4. Group C returns `outcome = expected_fail_observed`.
5. Group D returns `outcome = pass_strong`.
6. Group F records the expected truncation-depth pattern.
7. `minimum_passed = true`.
8. The report labels the output as computational evidence only.

The full stress test is complete only when the MVP criteria pass and:

1. Group B returns `pass_strong` for all listed `GL2(QQ)` matrices, or clearly
   records `pass_weak_dimension_only` for any dimension-only case.
2. Group E records `pass_strong` for `m = 1, 2, 3, 5`.
3. `full_stress_test_passed = true`.

Future implementation verification:

```text
python -m pytest
python -m ruff check .
python experiments/010-h1-stability-square-zero-two-generator/run.py
python scripts/check_claims.py
```

For this plan-only change, the required verification is only:

```text
git diff --check -- researchplan/subplan010.md
```

## 10. Non-Goals

- Do not run Experiment 010 as part of creating or editing this plan.
- Do not create `experiments/010-h1-stability-square-zero-two-generator/`
  while only optimizing the plan.
- Do not modify Experiment 009 result files.
- Do not use this plan to rerun or reinterpret `H2` through `H5`.
- Do not promote `CLAIM-0002` or any other claim to `checked`.
- Do not claim presentation invariance for all cofibrant replacements.
- Do not add a general Jordan operad resolution implementation.
- Do not add new default dependencies.

## 11. Interpretation Template

If the future MVP passes but extended groups are not implemented, use:

```text
Experiment 010-MVP supports the low-degree diagnosis that the two-generator
square-zero example has stable H1 after the redundant-relation syzygy is
included, and it reproduces the planned false extra H1 class when that syzygy
is omitted. This is computational evidence, not a proof of presentation
invariance.
```

If the future full stress test passes, use:

```text
Experiment 010 supports the stability of the computed H1 for the
two-generator square-zero Jordan algebra under deterministic linear generator
changes and controlled redundant-relation refinements. The expected-fail
control reproduces the false extra H1 class that appears when a redundant
relation is added without the corresponding syzygy. This supports, but does
not prove, the identification of the stable H1 with Sym^2(k^2) in this
bounded example.
```

If only dimensions pass but a basis-alignment certificate fails or is missing,
use:

```text
The case is a weak dimension pass only. It does not yet support H1 basis-class
stability.
```
