# Experiment 013: Strict Attachability And Low-To-High Killing Audit

Plan: `researchplan/subplan013.md`

Status: implemented runner

## Question

EXP011 reports bounded weight-local degree-2 candidates `s2_i` with
`d(s2_i)=z_i`, where `z_i` represents a class in
`ker(d1,w) / im(d2_old,w)`.  EXP013 checks whether those chosen raw
representatives can be used as strict dg attaching data through a bounded
weight range, and only then whether lower-weight strict cells kill
higher-weight candidates.

## Method

The experiment uses the same `low_weight_jordan` ordinary backend as EXP011
and EXP012.  It works over `QQ`, does not apply `Q`, and does not construct
`V3,V4,...`.

The strict attachability audit checks, for each candidate `z_i`, whether
`d(z_i*m)` reduces to zero for all degree-0 multipliers `m` in the requested
bounded range.  If a defect appears, the candidate remains an EXP011
weight-local representative but is not accepted as a strict dg attaching
generator in EXP013.

The low-to-high killing audit uses only strict-prefix sources: a target of
weight `w` may only use strict source cells of weight `< w`.  Before any
killing conclusion is recorded, the runner verifies
`d2_aug_matrix @ d1_matrix = 0` with the source-row matrix convention.

## Run

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

## Outputs

- `results.json`
- `data/strict_attachability_W{W}.json`
- `data/killing_audit_W{W}.json`
- `logs/run_W{W}.log`
- `tex/exp013_strict_attachability_killing_audit.tex`

## Interpretation Boundary

All conclusions are bounded computational evidence.  A failed strict
attachability check is an obstruction for the chosen raw representative in this
backend and bound; it does not rule out another representative or corrected
lift.
