# subplan013: Strict Attachability And Low-To-High Killing Audit

## 0. Plan Boundary

This plan creates a new experiment, EXP013.  It does not extend the EXP011 or
EXP012 claim boundary.  EXP011 remains the baseline source of candidate
degree-2 cells, and EXP012 remains the high-weight rank-backend validation
experiment.

EXP013 asks whether the EXP011 candidates can be used as genuine dg Jordan
attaching generators, and only then whether lower-weight attached generators
kill higher-weight candidates.

The target directory is:

```text
experiments/013-strict-attachability-killing-audit/
```

## 1. Mathematical Object

Work in the same ordinary low-weight Jordan backend as EXP011/EXP012:

```text
J = Jord<x,y> / (x^2, xy, y^2)
```

The first-layer model is:

```text
A^(1) = Jord<x, y, r_xx, r_xy, r_yy>
```

with:

```text
d(x) = d(y) = 0
d(r_xx) = x^2
d(r_xy) = xy
d(r_yy) = y^2
```

EXP011 found weight-local representatives:

```text
z_i in ker(d1,w) / im(d2_old,w)
```

These representatives are candidates for:

```text
d(s_i) = z_i.
```

EXP013 checks whether this assignment is strict enough to define a dg
attachment through a bounded weight range.

## 2. Strict Attachability Audit

For every base generator, record a sanity check that `d^2 = 0`.

For every EXP011 candidate `s_i` with boundary representative `z_i`, test the
multiplicative closure condition through the requested bound `W`:

```text
for every degree-0 multiplier m with wt(z_i) + wt(m) <= W:
    reduce(d(z_i * m)) in C0,wt(z_i)+wt(m)
```

Also test the generator-level case `m = 1`, i.e.:

```text
reduce(d(z_i)) in C0,wt(z_i)
```

If all defects vanish, mark:

```text
strictly_attachable_through_W = true
```

If a defect is found, mark:

```text
strictly_attachable_through_W = false
```

and record:

```text
cell_name
cell_weight
first_bad_multiplier
target_weight
defect_normal_form
```

This first phase is a gate.  A candidate that fails strict attachability is a
valid EXP011 weight-local homology representative, but it is not accepted as a
strict dg attaching generator in EXP013.

## 3. Low-To-High Killing Audit

Process target candidates by increasing weight.

For a target weight `w`, only use source cells satisfying both:

```text
source_cell_weight < w
source_cell is strictly attachable through w
```

This is the strict-prefix rule.  Same-weight cells are not allowed to kill each
other.

Construct the augmented model:

```text
A^(2)_strict(prefix < w)
```

by adjoining only the allowed strict lower-weight cells.  Before making any
killing statement, verify the source-row chain condition:

```text
d2_aug_matrix @ d1_matrix = 0.
```

If the chain condition holds, test whether each target candidate lies in:

```text
im(d2_aug,w)
```

The candidate status is one of:

```text
killed_by_strict_low_weight_cells
survives_strict_low_weight_cells
not_tested_no_strict_low_cells
not_tested_chain_condition_failed
not_strictly_attachable
```

If the chain condition fails, EXP013 must not report a homology killing
conclusion for that weight.

## 4. Outputs

EXP013 writes:

```text
results.json
data/strict_attachability_W{W}.json
data/killing_audit_W{W}.json
logs/run_W{W}.log
tex/exp013_strict_attachability_killing_audit.tex
```

The output must explicitly record:

```text
applies_Q = false
constructs_V3_plus = false
strictly_attachable_cell_count
homology_killing_claim_count
candidate-level obstruction records
```

## 5. Interpretation Boundary

EXP013 is bounded computational evidence only.  It does not apply `Q`, does not
construct `V3,V4,...`, and does not prove a global theorem about all weights.

A failed strict attachability check means:

```text
the chosen EXP011 raw representative cannot be naively attached as a dg
generator through the tested weight range.
```

It does not mean that no alternative representative or corrected lift exists.

If any optional span diagnostic is added later, it must be labelled:

```text
diagnostic_only_not_homology_evidence
```

and must not contribute to homology killing claims.

## 6. Default Run

Use the EXP011 W10 reference:

```powershell
python experiments/013-strict-attachability-killing-audit/run.py `
  --max-weight 10 `
  --mode validation `
  --reference-v2-cells experiments/011-v2-cells-no-Q/data/v2_cells_W10.json `
  --reference-by-weight experiments/011-v2-cells-no-Q/data/by_weight_W10.json `
  --attach-policy strict-prefix `
  --rank-backend modular_sparse_v2 `
  --max-memory-gb 20 `
  --workers 6 `
  --matrix-workers 4
```

## 7. Verification

Run:

```powershell
python -m pytest
python -m ruff check .
python scripts/check_claims.py
```

Required tests:

- `s2_00001_w4` records a strict attachability obstruction at multiplier `x`
  and target weight `5`.
- A non-strict cell is never used as a killing source.
- The strict-prefix rule only allows source weights `< target weight`.
- The TeX report preserves bounded, no-`Q`, no-`V3+` language.
