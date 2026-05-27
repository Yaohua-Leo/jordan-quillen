# Experiment 010: H1 Stability For The Two-Generator Square-Zero Algebra

Plan: `researchplan/subplan010.md`

Status: `run`

## Question

Test whether the computed low-degree `H1` for

```text
J = k{x,y}/(x^2, xy, y^2)
```

remains stable under deterministic presentation changes, using exact rational
linear algebra over `QQ`.

## Scope

This experiment only uses the indecomposable low-degree complex

```text
C2 -> C1 -> C0
```

needed for `H1 = ker(partial_1^Q) / im(partial_2^Q)`. It is not a general
Jordan operad resolution framework and does not compute `H2` through `H5`.

## Test Groups

- Group A: minimal presentation baseline.
- Group C: naive redundant-relation expected-fail control.
- Group D: redundant relation repaired by the matching degree-2 syzygy.
- Group F: truncation-depth diagnostic for `N = 1, 2, 3`.
- Group B: deterministic `GL2(QQ)` linear generator changes with exact
  `Sym^2` matrix certificates.
- Group E: multiple repaired redundant-relation prefixes.

## Current Run Command

```text
python experiments/010-h1-stability-square-zero-two-generator/run.py
```

## Interpretation Boundary

The result may say that Experiment 010 supports `H1` stability in this bounded
square-zero example. It must not say that it proves presentation invariance.
