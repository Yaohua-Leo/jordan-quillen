# Experiment 001: Split Square-Zero Extension Sanity Checks

Status: run

Goal: run the first minimal exact-arithmetic workflow for split square-zero
extensions `E = J plus M` with `M^2 = 0`.

Scope:

- This is a sanity check for one-dimensional toy families.
- This is not a proof of the Beck module equivalence.
- This does not change the status of `CLAIM-0003`.

Inputs:

- `e^2 = e`, `L_e(m) = lambda m`;
- `e^2 = 0`, `L_e(m) = lambda m`;
- `lambda in {-2, -1, -1/2, 0, 1/2, 1, 2}`.

Checker:

- exact rational arithmetic with `Fraction`;
- Jordan identity checked on a finite grid of linear combinations;
- basis-only checks are treated as smoke tests only.

Run:

```powershell
python experiments/001-square-zero/run.py
```

Expected output:

- for `e^2 = e`, tested Jordan scalar actions are `0`, `1/2`, and `1`;
- for `e^2 = 0`, the tested Jordan scalar action is `0`;
- the unital extension condition for `e^2 = e` selects `lambda = 1`;
- `results.json` records the real generated output and the claim boundary.
