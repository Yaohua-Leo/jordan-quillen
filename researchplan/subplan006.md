# subplan006: Presentation-Invariance Stress Test For J3

## 0. Stage Goal

`subplan006` isolates the presentation-invariance warning from the extracted
ChatGPT plan.

The target experiment directory is:

```text
experiments/006-presentation-invariance-j3/
```

The mathematical object is:

```text
J_3 = (t)/(t^3).
```

The purpose is to document a future stress test: the same algebra can be
presented in more than one way, and a naive one-step relation complex may not
give presentation-invariant homology.

## 1. Scope Boundary

This stage is a warning and experiment scaffold, not a proof.

It may compute Presentation A using the one-generator toy model from
`subplan005` after that model exists. It may also compute a clearly labelled
naive one-step diagnostic for Presentation B. It must not pretend that this
diagnostic is a genuine cofibrant replacement; the needed higher syzygy data
remain unimplemented.

## 2. Presentations

Presentation A:

```text
F(x)/(x^3).
```

Expected one-generator toy dimensions:

```text
H0 = 1, H1 = 1.
```

Presentation B:

```text
F(x, y)/(y - x^2, xy, y^2).
```

Expected mathematical warning:

```text
Presentation B should agree with Presentation A only after a genuine
cofibrant replacement. A naive one-step relation complex may produce false
extra homology classes.
```

## 3. Experiment Target

Planned files:

```text
experiments/006-presentation-invariance-j3/experiment.md
experiments/006-presentation-invariance-j3/expected.json
experiments/006-presentation-invariance-j3/run.py
experiments/006-presentation-invariance-j3/results.json
```

The first-pass `run.py` may:

- compute Presentation A if `src/jordan_qh/quillen_toy.py` exists;
- compute a naive one-step diagnostic for Presentation B, explicitly labelled
  as incomplete;
- record the genuine Presentation B cofibrant replacement as `not implemented`;
- explicitly state that presentation invariance has not been verified.

## 4. Acceptance Criteria

This stage is complete only when:

1. The experiment record separates Presentation A from Presentation B.
2. `expected.json` records the theory expectation without claiming it has been
   checked.
3. `results.json` does not claim full presentation invariance.
4. If `run.py` is executed before the toy model exists, it exits cleanly and
   writes or preserves an honest `not run yet` result.
5. After `subplan005` is implemented, Presentation A and the naive one-step
   Presentation B diagnostic can be computed and compared against the expected
   dimensions.

## 5. Non-Goals

- Do not implement a two-generator cofibrant replacement in this stage.
- Do not resolve the higher syzygies for Presentation B.
- Do not treat the toy one-relation model as presentation-invariant.
- Do not mark any claim file as proved from this scaffold alone.
