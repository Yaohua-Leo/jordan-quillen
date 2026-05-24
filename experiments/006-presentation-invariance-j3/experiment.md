# Experiment 006: Presentation-Invariance Stress Test For J3

Status: run

Plan: `researchplan/subplan006.md`

Goal: record a presentation-invariance stress test for:

```text
J_3 = (t)/(t^3).
```

Presentation A:

```text
F(x)/(x^3)
```

Presentation B:

```text
F(x, y)/(y - x^2, xy, y^2)
```

Warning: a naive one-step relation complex for Presentation B may produce
extra false homology classes. Presentation invariance should only be expected
after a genuine cofibrant replacement with the needed higher syzygy
generators.

First-pass rule:

- Presentation A may be computed by the one-generator toy model after
  `src/jordan_qh/quillen_toy.py` exists.
- Presentation B is run only as a naive one-step relation diagnostic.
- The genuine cofibrant replacement for Presentation B is not implemented in
  this experiment.
- `results.json` must not claim that presentation invariance has been
  verified.

Current run command:

```text
python experiments/006-presentation-invariance-j3/run.py
```

Current result:

- Presentation A computes `H0 = 1, H1 = 1`.
- The naive one-step Presentation B diagnostic computes `H0 = 1, H1 = 2`,
  exposing the expected extra H1 class from the incomplete relation complex.
- `presentation_invariance_verified` remains `false`.
