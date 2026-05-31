# Experiment 011: V2 Cells Before Q

This experiment executes `researchplan/subplan011.md`.

It computes the bounded weight-wise spaces

```text
H1_old,w = ker(d1,w) / im(d2_old,w)
```

inside `A^(1)` for the two-generator square-zero Jordan algebra
`Jord<x,y>/(x^2,xy,y^2)`.

The run uses exact rational arithmetic over `QQ`, the source-row matrix
convention, and the existing ordinary low-weight Jordan backend.  It does not
apply `Q`, does not attach the formal `s_i`, and does not construct `V3`,
`V4`, or higher layers.

## Commands

Low-weight dry run:

```text
python experiments/011-v2-cells-no-Q/run.py --max-weight 8 --mode dry
```

Adaptive overnight request:

```text
python experiments/011-v2-cells-no-Q/run.py --max-weight 20 --mode overnight --resume
```

The default adaptive threshold is `--max-raw-terms-per-space 10000`, which is
intended to complete through weight `8` in the current backend and record
higher requested weights as skipped rather than silently omitting them.

## Outputs

Primary outputs:

```text
experiments/011-v2-cells-no-Q/results.json
experiments/011-v2-cells-no-Q/data/by_weight_W{W}.json
experiments/011-v2-cells-no-Q/data/v2_cells_W{W}.json
experiments/011-v2-cells-no-Q/tex/exp011_v2_cells_no_Q.tex
experiments/011-v2-cells-no-Q/logs/run_W{W}.log
```

Caches and checkpoints are written under `cache/` and `checkpoints/`.

## Interpretation Boundary

All conclusions are restricted to weights whose status is `completed`.
Skipped, failed, and untested weights are not used to infer global
stabilization, termination, or absence of further degree-2 cell candidates.
