# subplan009: Experiment 009 For Two-Generator Square-Zero Quillen Homology

## 0. Numbering Note

`subplan007` already reserved a possible Experiment 008 for automatic
low-degree cell attachment in the `J_3` Presentation B toy workflow.

This plan therefore uses the matching plan filename:

```text
researchplan/subplan009.md
```

but assigns the new square-zero two-generator experiment to:

```text
experiments/009-square-zero-two-generator-quillen-homology/
```

This follows the user instruction that, if there is a numbering conflict, this
experiment should be named `009`.

## 1. Stage Goal

`subplan009` turns the source plan:

```text
jordan_square_zero_quillen_experiment_plan.md
```

into a bounded, auditable experiment plan for the nonunital square-zero Jordan
algebra:

```text
J = k{x,y}/(x^2, xy, y^2)
```

over a characteristic `0` field, implemented with exact rational arithmetic
over `QQ`.

The target computation is the intrinsic Jordan Quillen homology:

```text
H_n^Jord(J) = H_n(Q(tilde J))
```

for `0 <= n <= 5`, where `tilde J -> J` is represented by a truncated
quasi-free dg Jordan replacement through resolution degree `6`.

The deliverable is not just dimensions. The experiment must produce an
auditable chain complex:

```text
C6 -> C5 -> C4 -> C3 -> C2 -> C1 -> C0
```

with bases, boundary formulas, boundary matrices, kernel bases, image bases,
homology representatives, and a generated TeX report.

## 2. Source Evidence

The source plan fixes these constraints:

- Work over `QQ`, not floating-point arithmetic.
- Use the nonunital convention unless an explicit augmented-unital variant is
  added later.
- The target algebra has basis `x, y` and all products vanish.
- `H0` is fixed by the indecomposables calculation:

  ```text
  H0 = Q(J) = J/J^2 = <x,y> ~= k^2.
  ```

- Degree `1` relation cells are:

  ```text
  r_xx, r_xy, r_yy
  ```

  with full differentials:

  ```text
  d(r_xx) = x^2
  d(r_xy) = x*y
  d(r_yy) = y^2
  ```

- After applying `Q`, product terms vanish, so:

  ```text
  partial_1 = 0 : C1 -> C0.
  ```

- Computing through `H5` requires the boundary:

  ```text
  partial_6 : C6 -> C5.
  ```

  Therefore the replacement must be constructed through resolution degree `6`,
  not only through chain degree `5`.

Prior experiments also supply warnings:

- `experiments/006-presentation-invariance-j3/` shows that a one-step
  presentation diagnostic can produce false extra homology.
- `experiments/007-genuine-cofibrant-replacement-j3/` repairs one fixed J3
  presentation by adding an explicit degree `2` cell, but remains a hand-coded
  toy and not a general cofibrant replacement algorithm.

Experiment 009 must therefore keep the distinction between:

```text
naive one-step relation complex
```

and:

```text
Quillen homology computed from a cofibrant or quasi-free replacement.
```

## 3. Scope Boundary

This stage may create a new experiment directory and, during implementation,
supporting code for exact finite chain complexes and report generation.

It may use existing local code when suitable:

```text
src/jordan_qh/linear_algebra.py
src/jordan_qh/semi_free_toy.py
src/jordan_qh/quillen_toy.py
```

It may add narrowly scoped helpers if the existing toy surface is too small,
for example:

```text
src/jordan_qh/chain_complex.py
src/jordan_qh/reporting.py
tests/test_exp009_square_zero_two_generator.py
```

This stage must not:

- add a new dependency to the default Python package, required runner, or
  required test path;
- use floating-point arithmetic for ranks, kernels, or images;
- claim a general Jordan cofibrant replacement algorithm if only this example
  is implemented;
- identify intrinsic Jordan Quillen homology with TKK or Lie homology;
- fabricate cell lists, matrices, homology dimensions, or TeX tables before
  the runner has produced them;
- mark any claim file as `checked` from this experiment alone.

If the replacement backend is not implemented yet, the runner must write an
honest `not run yet` or `backend not implemented` result rather than a fake
successful output.

### Backend Policy

The default committed runner for this experiment remains pure Python. Required
results should use `fractions.Fraction` and existing exact row-reduction
patterns unless a later plan explicitly promotes a different backend.

During exploration, LLM agents may call currently verified tools listed in
`codex/local-math-tools.md`, including Sage, SymPy, Maple, Wolfram Language,
GAP, Singular, Maxima, OSCAR, or similar registered routes. Re-check each tool's
path and version before relying on it.

CAS or tool output may inform notes, debugging, and cross-checks. It is
`exploratory evidence` unless this experiment explicitly promotes that backend
and includes a replayable script or log. Any formal experiment artifact that
uses CAS or tool output must record the backend, version or path,
command/input, output location or summary, and exact reproducibility notes.

## 4. Mathematical Setup

Use the nonunital square-zero algebra:

```text
basis(J) = [x, y]
x*x = 0
x*y = 0
y*y = 0
```

The degree `0` generators are:

```text
V0 = <x, y>
```

The degree `1` relation cells are:

```text
V1 = <r_xx, r_xy, r_yy>
```

with full differential:

```text
d(r_xx) = x*x
d(r_xy) = x*y
d(r_yy) = y*y
```

The indecomposable chain complex starts as:

```text
C1 = <r_xx, r_xy, r_yy> --partial_1=0--> C0 = <x, y>.
```

The experiment must not conclude:

```text
H1 ~= C1
```

until `im(partial_2)` has been computed from the next layer of the
replacement.

For `2 <= n <= 6`, the intended resolution procedure is:

1. compute cycles representing positive homology in the current truncated
   quasi-free dg Jordan algebra;
2. attach degree `n` cells to kill those cycles;
3. record each full differential;
4. extract the linear part after applying `Q`;
5. append the corresponding boundary matrix:

   ```text
   partial_n : Cn -> C(n-1).
   ```

The source plan requires internal/product weight bounds:

```text
W = 6, 7, 8
```

and a stability comparison across these runs. If the outputs differ across
weight bounds, the TeX report must label the result as truncated evidence, not
as a stable computation.

## 5. Planned Experiment Files

Target files:

```text
experiments/009-square-zero-two-generator-quillen-homology/experiment.md
experiments/009-square-zero-two-generator-quillen-homology/expected.json
experiments/009-square-zero-two-generator-quillen-homology/run.py
experiments/009-square-zero-two-generator-quillen-homology/results.json
experiments/009-square-zero-two-generator-quillen-homology/data/chain_complex.json
experiments/009-square-zero-two-generator-quillen-homology/tex/exp009_square_zero_two_gen_quillen.tex
```

Optional generated file if TeX compilation is selected later:

```text
experiments/009-square-zero-two-generator-quillen-homology/tex/exp009_square_zero_two_gen_quillen.pdf
```

Potential supporting files, only if implementation needs them:

```text
src/jordan_qh/chain_complex.py
src/jordan_qh/reporting.py
tests/test_exp009_square_zero_two_generator.py
```

The experiment note must explicitly point back to this plan:

```text
Plan: researchplan/subplan009.md
Source plan: jordan_square_zero_quillen_experiment_plan.md
```

## 6. Expected Record Shape

`expected.json` should record only fixed setup and sanity expectations, not
uncomputed high-degree homology.

Suggested shape:

```json
{
  "status": "expected_setup",
  "experiment": "EXP-009-square-zero-two-generator-quillen-homology",
  "base_field": "QQ",
  "category": "nonunital Jordan algebras",
  "target_algebra": {
    "basis": ["x", "y"],
    "products": {
      "x*x": "0",
      "x*y": "0",
      "y*y": "0"
    }
  },
  "method": "derived indecomposables of a truncated quasi-free dg Jordan replacement",
  "max_homology_degree": 5,
  "required_resolution_degree": 6,
  "weight_bounds": [6, 7, 8],
  "fixed_sanity_expectations": {
    "dim_H0": 2,
    "partial_1_is_zero": true,
    "C0": ["x", "y"],
    "C1": ["r_xx", "r_xy", "r_yy"]
  },
  "do_not_prefill": [
    "higher_cells",
    "higher_boundary_matrices",
    "kernel_bases",
    "image_bases",
    "homology_dimensions_H1_to_H5",
    "homology_representatives_H1_to_H5"
  ],
  "warning": "High-degree values are valid only when generated by run.py from recorded chain-complex data."
}
```

Initial `results.json` may honestly be:

```json
{
  "status": "not run yet",
  "passed": null,
  "notes": "Experiment 009 is planned but the truncated quasi-free replacement runner has not been executed."
}
```

After a real run, `results.json` must include at least:

- `status`;
- `passed`;
- selected `weight_bound`;
- stability comparison for `W = 6, 7, 8`;
- whether the TeX report was generated;
- whether the result is stable or only truncated evidence;
- `dim_H0` through `dim_H5`;
- checks for `partial_1 = 0`, `d^2 = 0`, and `H0 = 2`;
- paths to `data/chain_complex.json` and the generated TeX file.

## 7. Chain Complex Data Contract

`data/chain_complex.json` should be generated by the runner and should record
the convention that each matrix row is the image of one source basis element in
target coordinates. This matches the existing `semi_free_toy.py` convention.

Suggested shape:

```json
{
  "experiment": "EXP-009-square-zero-two-generator-quillen-homology",
  "field": "QQ",
  "matrix_convention": "source_rows_target_coordinates",
  "resolution_degree": 6,
  "max_homology_degree": 5,
  "weight_bound": 8,
  "bases": {
    "C0": ["x", "y"],
    "C1": ["r_xx", "r_xy", "r_yy"]
  },
  "full_differentials": {
    "d(r_xx)": "x*x",
    "d(r_xy)": "x*y",
    "d(r_yy)": "y*y"
  },
  "indecomposable_differentials": {
    "partial_1(r_xx)": "0",
    "partial_1(r_xy)": "0",
    "partial_1(r_yy)": "0"
  },
  "boundary_matrices_source_rows": {
    "partial_1": [[0, 0], [0, 0], [0, 0]]
  },
  "linear_algebra": {
    "kernels": {},
    "images": {},
    "homology_representatives": {},
    "homology_dimensions": {}
  },
  "checks": {
    "partial_1_is_zero": true,
    "H0_dimension_is_2": true,
    "d_squared_zero": null,
    "stable_across_weight_bounds": null
  }
}
```

The degree `2` through degree `6` cell lists and matrices must be populated by
the actual run. They should not be copied from the template by hand.

## 8. TeX Report Requirements

The generated TeX report should be:

```text
experiments/009-square-zero-two-generator-quillen-homology/tex/exp009_square_zero_two_gen_quillen.tex
```

It must contain these sections:

```text
Conventions
The algebra J
Quillen method
Why degree 6 is needed for H5
Construction of the truncated replacement
The indecomposable chain complex
Boundary matrices
Kernels, images, and homology
Weight-bound stability
Interpretation of classes
Limitations
```

The report must state:

```text
H0 = Q(J) ~= k^2
```

and:

```text
partial_1 = 0
```

as sanity checks.

For `H1` through `H5`, it must use only data from `chain_complex.json`.

The interpretation section must say that homology classes are universal
syzygy classes. Extension interpretations require dual cochains and a chosen
coefficient module; the report must not call homology classes themselves
ordinary square-zero extensions.

## 9. Implementation Phases

### Phase 1: Scaffold the experiment record

Create:

```text
experiments/009-square-zero-two-generator-quillen-homology/experiment.md
experiments/009-square-zero-two-generator-quillen-homology/expected.json
experiments/009-square-zero-two-generator-quillen-homology/results.json
experiments/009-square-zero-two-generator-quillen-homology/run.py
```

The first `run.py` should be safe to execute before the replacement backend is
complete. It may write `backend not implemented` and exit successfully, as long
as it does not claim computed homology.

### Phase 2: Add exact finite chain-complex support

If existing helpers are insufficient, add a small exact chain-complex module
that can compute:

- rank;
- kernel basis;
- image basis;
- homology dimension;
- representative bookkeeping;
- `d^2 = 0` checks.

Use `fractions.Fraction` and existing exact row-reduction patterns. The default
chain-complex module must not add dependencies. Companion cross-check scripts
or logs may use registered tools from the Backend Policy, but they must stay
outside the required runner and test path unless a later plan explicitly
promotes that backend.

### Phase 3: Lock degree 0 and degree 1 sanity checks

Write tests that assert:

```text
C0 = [x, y]
C1 = [r_xx, r_xy, r_yy]
partial_1 = 0
dim H0 = 2
```

These tests protect the nonunital square-zero convention before any higher
cell attachment is attempted.

### Phase 4: Implement the bounded replacement backend

Add the narrowest code needed to construct the truncated quasi-free dg Jordan
replacement through degree `6` for this example and chosen weight bound.

Every new cell must record:

- name;
- homological degree;
- internal/product weight;
- full differential;
- linear part after applying `Q`;
- the cycle it kills;
- whether `d^2 = 0` was checked.

If the backend only supports this fixed square-zero two-generator example,
name and document it as example-specific.

### Phase 5: Run weight bounds and compare stability

Run:

```text
W = 6
W = 7
W = 8
```

For each run, record:

- bases `C0` through `C6`;
- matrices `partial_1` through `partial_6`;
- ranks;
- kernel bases;
- image bases;
- representatives and dimensions for `H0` through `H5`.

The final report may say `stable` only if the relevant `H0` through `H5`
dimensions and representatives agree across the selected bounds.

### Phase 6: Generate JSON and TeX from the same data

Generate:

```text
data/chain_complex.json
tex/exp009_square_zero_two_gen_quillen.tex
```

The TeX report must be data-driven from the JSON or the same in-memory result
object. Do not maintain a separate hand-edited TeX result table.

### Phase 7: Review mathematical language

Before marking the experiment complete, inspect the TeX and experiment note
for overclaims.

Allowed language:

```text
computed in this truncated model
stable across W = 6, 7, 8
truncated evidence only
example-specific backend
```

Forbidden language unless separately proved:

```text
the theorem is proved
all cofibrant replacements give this result
presentation invariance is proved
Jordan Quillen homology equals TKK Lie homology
```

## 10. Acceptance Criteria

Experiment 009 is complete only when:

1. The experiment directory exists and points to
   `researchplan/subplan009.md`.
2. The setup fixes the nonunital square-zero convention over `QQ`.
3. The runner does not fabricate a successful result when the backend is
   missing.
4. `C0`, `C1`, and `partial_1 = 0` are tested.
5. A real successful run constructs through resolution degree `6`.
6. `partial_1` through `partial_6` are recorded.
7. `H0` through `H5` are computed from kernels and images, not from
   prefilled dimensions.
8. `H5` uses `im(partial_6)`.
9. Weight bounds `6`, `7`, and `8` are compared.
10. The TeX report is generated from the recorded data.
11. The final report distinguishes stable output from truncated evidence.
12. Verification passes:

```text
python -m pytest
python -m ruff check .
python experiments/009-square-zero-two-generator-quillen-homology/run.py
python scripts/check_claims.py
```

For a plan-only change, the minimum verification is:

```text
git diff --check -- researchplan/subplan009.md
```

## 11. Non-Goals

- Do not implement a full Jordan operad resolution framework unless a later
  plan explicitly scopes it.
- Do not use this experiment to upgrade claim files to `checked`.
- Do not replace the J3 automatic-cell-attachment candidate reserved by
  `subplan007`.
- Do not silently make a new computation backend mandatory.
- Do not promote CAS-only output to official results without backend
  declaration and reproducibility evidence.
- Do not present a one-step relation complex as Quillen homology.
- Do not publish generated high-degree values without `d^2 = 0`, `H0 = 2`,
  and weight-bound checks.

## 12. Next Stage Candidate

After this plan is implemented, a later plan may split one of two ways:

1. If Experiment 009 remains blocked by the bounded replacement backend, write
   a backend-specific plan for exact low-weight free Jordan algebra and syzygy
   enumeration.
2. If Experiment 009 runs successfully, write a review plan to compare the
   stable output with the square-zero extension and cohomology interpretation
   notes before adding any claim file.
