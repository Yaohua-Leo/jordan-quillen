# Experiment 101: One-Generator Generator Legality Audit

This experiment follows `researchplan/subplan101.md`.

It audits the generator candidates computed by EXP100 for:

```text
J = Jord<x> / (x^2)
```

The default audit bound is `W=12`.  The experiment reads EXP100's W10
candidate cells, checks the `V1` relation generators as target-kernel data, and
checks the `V2` attaching generators with an EXP013-style strict attachability
test.

## Command

```text
python experiments/101-one-generator-generator-legality-audit/run.py --max-weight 12
```

## Outputs

```text
results.json
data/v1_legality_W12.json
data/v2_strict_attachability_W12.json
data/chain_audit_W12.json
logs/run_W12.log
tex/exp101_one_generator_generator_legality_audit.tex
```

## Interpretation Boundary

EXP101 is bounded computational evidence only.  It does not apply `Q`, does
not construct higher layers, and does not prove a global theorem.  A strict
attachability obstruction for a chosen `V2` representative means that this
representative is not accepted as a strict dg attaching differential in the
tested backend and range; it does not rule out alternate representatives.
