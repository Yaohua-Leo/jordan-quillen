# Experiment 100: One-Generator Cofibrant Cell Computation

This experiment executes `researchplan/subplan100.md`.

It computes bounded cell layers for the nonunital Jordan algebra:

```text
J = Jord<x> / (x^2)
```

The run is bounded by product weight `10` and homological degree `2`.  It
records computed `V0`, `V1`, and `V2` cells weight by weight.  The experiment
does not use predicted formulas from the browser conversation as inputs.

## Commands

Run the planned bounded computation:

```text
python experiments/100-square-zero-nonunital-cofibrant-weight10/run.py --max-weight 10
```

## Outputs

Primary outputs:

```text
experiments/100-square-zero-nonunital-cofibrant-weight10/results.json
experiments/100-square-zero-nonunital-cofibrant-weight10/data/by_weight_W10.json
experiments/100-square-zero-nonunital-cofibrant-weight10/data/cells_W10.json
experiments/100-square-zero-nonunital-cofibrant-weight10/tex/exp100_square_zero_nonunital_cofibrant_weight10.tex
experiments/100-square-zero-nonunital-cofibrant-weight10/logs/run_W10.log
```

Caches and checkpoints are written under `cache/` and `checkpoints/`.

## Interpretation Boundary

All conclusions are restricted to completed weights.  Skipped, failed, and
untested weights are not used to infer global stabilization, termination, or
absence of further cells.  This is bounded computational evidence, not a proof
of the full cofibrant replacement.
