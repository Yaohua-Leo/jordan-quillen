# Experiment 009: Two-Generator Square-Zero Quillen Homology

Plan: `researchplan/subplan009.md`

Source plan: `jordan_square_zero_quillen_experiment_plan.md`

Status: `run`

## Question

Compute the intrinsic Jordan Quillen homology of the nonunital square-zero
Jordan algebra

```text
J = k{x,y}/(x^2, xy, y^2)
```

over `QQ`, using derived indecomposables of a truncated quasi-free dg Jordan
replacement through resolution degree `6`.

## Convention

The experiment uses the nonunital Jordan convention. The target algebra has
basis `[x, y]` and all products vanish. Therefore the fixed sanity check is

```text
H0 = Q(J) = J/J^2 = <x,y>
```

and the degree `1` relation cells are

```text
r_xx, r_xy, r_yy
```

with full differentials

```text
d(r_xx) = x*x
d(r_xy) = x*y
d(r_yy) = y*y
```

After applying indecomposables, `partial_1 = 0`.

## Current Implementation

The current runner implements an example-specific bounded ordinary Jordan
backend. It enumerates the commutative nonassociative free algebra modulo the
linearized Jordan identity through the selected product-weight bound, extends
the differential by the signed Leibniz rule, attaches cells through resolution
degree `6`, and extracts the linear part after applying indecomposables.

This is not a general cofibrant replacement algorithm. It is a fixed
low-weight backend for this experiment only.

The runner compares weight bounds:

```text
W = 6, 7, 8
```

The selected detailed output is `W = 8`. The comparison is not stable, so the
result is truncated evidence only.

Selected `W = 8` homology dimensions in the bounded model:

```text
H0 = 2
H1 = 3
H2 = 8
H3 = 307
H4 = 8
H5 = 18
```

These values are computed from the recorded kernels and images in
`data/chain_complex.json`; they should not be read as a theorem about all
cofibrant replacements.

## Output Files

- `results.json` records the run summary, checks, and stability comparison.
- `data/chain_complex.json` records bases, full differentials, boundary
  matrices, kernels, images, and homology representatives for the selected
  `W = 8` run.
- `tex/exp009_square_zero_two_gen_quillen.tex` is generated from the same
  in-memory result object as the JSON output.

## Remaining Mathematical Risk

The output is bounded computational evidence. The instability between
`W = 6`, `W = 7`, and `W = 8` means a later backend review is needed before
promoting any high-degree value to a claim file.
