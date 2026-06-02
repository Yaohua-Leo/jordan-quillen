# subplan012: Experiment 012 For Higher-Weight Rank Backend Validation

## 0. Plan Boundary

This plan creates a new experiment, not an extension of the EXP011 result
claim.  EXP011 remains the baseline bounded computation through weight `10`.
EXP012 tests a revised rank backend on the same mathematical object and uses
EXP011 as a reproduction reference before attempting higher weights.

The target directory is:

```text
experiments/012-high-weight-rank-backend-validation/
```

## 1. Mathematical Object

The object is unchanged from EXP011.  Work over `QQ` with:

```text
J = Jord<x,y> / (x^2, xy, y^2).
```

The first-layer dg Jordan algebra is:

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

For each product weight `w`, compute:

```text
H1_old,w = ker(d1,w) / im(d2_old,w).
```

The matrix convention remains `source_rows_target_coordinates`, so the chain
condition is implemented as:

```text
d2_old_matrix @ d1_matrix = 0.
```

## 2. New Experimental Purpose

EXP012 validates a higher-weight rank backend:

```text
rank_backend = modular_sparse_v2
```

This backend should:

- log finer modular-rank progress;
- cache conversion from rational sparse rows to finite-field sparse rows;
- store pivot rows in a representation optimized for repeated modular row
  reductions;
- preserve exact certificate semantics: modular rank is only used as a lower
  bound, and a completed result is accepted only when this lower bound meets a
  mathematically known upper bound.

## 3. Reproduction Gate

EXP012 must first recompute weights `1..10` and compare against:

```text
experiments/011-v2-cells-no-Q/data/by_weight_W10.json
```

The comparison fields are:

```text
dim_C0
dim_C1
dim_C2_old
rank_d1
rank_d2_old
dim_Z1
dim_H1_old
number_of_new_s_cells
```

Only if all recomputed weights match the EXP011 reference may EXP012 report
weight `11` or higher as completed bounded evidence.  If the reproduction gate
fails, higher requested weights must be marked skipped with an explicit
`exp011_reproduction_gate` reason.

## 4. Outputs

EXP012 writes:

```text
results.json
data/by_weight_W{W}.json
data/v2_cells_W{W}.json
tex/exp012_high_weight_rank_backend_validation.tex
logs/run_W{W}.log
```

The outputs must include a reproduction section with:

```text
exp011_reference_file
recomputed_weights
matches_exp011_reference
per_weight comparison records
```

## 5. Interpretation Boundary

EXP012 is still bounded computational evidence.  It does not apply `Q`, does
not attach the formal `s_i`, does not build `V3,V4,\ldots`, and does not prove
that no higher-weight cells exist.
