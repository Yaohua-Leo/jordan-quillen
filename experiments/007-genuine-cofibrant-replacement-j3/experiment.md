# Experiment 007: Two-Step Cofibrant Replacement Toy For J3

Status: run

Plan: `researchplan/subplan007.md`

Goal: repair the naive one-step Presentation B diagnostic for:

```text
J_3 = (t)/(t^3)
```

Experiment 006 compared:

```text
Presentation A: F(x)/(x^3)
Presentation B: F(x, y)/(y - x^2, x*y, y^2)
```

The one-step diagnostic computed:

```text
Presentation A: H0 = 1, H1 = 1
Presentation B: H0 = 1, H1 = 2
```

This experiment adds one explicit degree 2 generator to Presentation B to kill
the redundant `a3` class coming from `y^2 = 0`.

## Replacement Data

Degree 0 generators:

```text
x, y
```

Degree 1 generators:

```text
a1, a2, a3
```

Differential:

```text
d(a1) = y - x^2
d(a2) = x*y
d(a3) = y^2
```

Degree 2 generator:

```text
b
```

with:

```text
d(b) = a3 - x*a2 - (y + x^2)*a1 + x*(x*a1)
```

After applying indecomposables `Q`, the chain complex is:

```text
Q2 = [b]
Q1 = [a1, a2, a3]
Q0 = [x, y]

d1(a1) = y
d1(a2) = 0
d1(a3) = 0
d2(b) = a3
```

Expected homology:

```text
H0 = 1
H1 = 1
H2 = 0
```

The symbolic reason that `d^2(b)=0` for this fixed example is:

```text
d(d(b)) = x^2*x^2 - x*(x*x^2) = 0
```

by power-associativity in the one-generated Jordan subalgebra.

## Boundary

This is a hand-coded two-step toy replacement for `J_3` Presentation B. It is
not an automatic syzygy search and not a general cofibrant replacement
algorithm.

The output may record:

```text
presentation_invariance_verified_through_degree = 1
full_presentation_invariance_verified = false
```

It must not claim full presentation invariance.

## Run Command

```text
python experiments/007-genuine-cofibrant-replacement-j3/run.py
```

## Current Result

- `d_Q^2 = 0` for the fixed indecomposable complex.
- The degree 2 generator `b` kills the extra naive `a3` class.
- Computed homology dimensions are `H0 = 1`, `H1 = 1`, `H2 = 0`.
- Compared with Experiment 006, Presentation B's naive `H1` dimension drops
  from `2` to `1` after the two-step correction.
- `presentation_invariance_verified_through_degree` is `1`.
- `full_presentation_invariance_verified` remains `false`.
