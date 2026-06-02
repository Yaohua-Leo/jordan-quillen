# Experiment 012: Higher-Weight Rank Backend Validation

This experiment executes `researchplan/subplan012.md`.

It computes the same bounded weight-wise object as Experiment 011:

```text
H1_old,w = ker(d1,w) / im(d2_old,w)
```

inside `A^(1)` for the two-generator square-zero Jordan algebra
`Jord<x,y>/(x^2,xy,y^2)`.

The purpose is rank-backend validation for higher weights.  EXP012 first
recomputes the EXP011 reference range through weight `10` using
`rank_backend=modular_sparse_v2`.  Only after that reproduction gate matches
the EXP011 reference does the runner treat weight `11` or higher as eligible
for completed bounded evidence.

## Commands

Reproduce EXP011 through weight `10`:

```text
python experiments/012-high-weight-rank-backend-validation/run.py --max-weight 10 --mode validation --reference-exp011 experiments/011-v2-cells-no-Q/data/by_weight_W10.json --max-memory-gb 20 --workers 6 --matrix-workers 4 --rank-backend modular_sparse_v2
```

Attempt weight `11` after the reproduction gate:

```text
python experiments/012-high-weight-rank-backend-validation/run.py --max-weight 11 --mode validation --resume --reference-exp011 experiments/011-v2-cells-no-Q/data/by_weight_W10.json --max-raw-terms-per-space 500000 --max-quotient-dim 1000000 --max-matrix-nnz 100000000 --max-memory-gb 20 --workers 6 --matrix-workers 4 --rank-backend modular_sparse_v2
```

## Outputs

Primary outputs:

```text
experiments/012-high-weight-rank-backend-validation/results.json
experiments/012-high-weight-rank-backend-validation/data/by_weight_W{W}.json
experiments/012-high-weight-rank-backend-validation/data/v2_cells_W{W}.json
experiments/012-high-weight-rank-backend-validation/tex/exp012_high_weight_rank_backend_validation.tex
experiments/012-high-weight-rank-backend-validation/logs/run_W{W}.log
```

Caches and checkpoints are written under `cache/` and `checkpoints/`.

## Interpretation Boundary

All conclusions are restricted to completed weights.  EXP012 does not apply
`Q`, does not attach the formal `s_i`, does not construct `V3` or higher
layers, and does not prove any global stabilization statement.
