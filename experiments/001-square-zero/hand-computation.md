# Hand Computation For Experiment 001

This note records the calculation used by `experiments/001-square-zero/`.
It is a split square-zero sanity check, not a proof of the full Beck module
comparison.

## Setup

Let `J` be a Jordan algebra and let `M` be a vector space. Consider the split
square-zero extension:

```text
E = J plus M,
M^2 = 0.
```

Write the candidate action as:

```text
L_x(m) = x . m.
```

The multiplication on `E` is:

```text
(x, m) * (y, n) = (xy, L_x(n) + L_y(m)).
```

## Linear Terms In The Jordan Identity

Use the Jordan identity:

```text
((a*a)*b)*a = (a*a)*(b*a).
```

Set:

```text
a = (x, m),
b = (y, n).
```

Since `M^2 = 0`, the square of `a` is:

```text
a^2 = (x^2, 2 L_x m).
```

Keeping only the `M`-linear terms gives:

```text
((a^2 b)a)_M
= L_{x^2 y}(m) + L_x L_{x^2}(n) + 2 L_x L_y L_x(m),

(a^2(ba))_M
= L_{x^2} L_y(m) + L_{x^2} L_x(n) + 2 L_{xy} L_x(m).
```

Equating the coefficients of `n` gives:

```text
L_x L_{x^2} = L_{x^2} L_x.
```

Equating the coefficients of `m` gives:

```text
L_{x^2 y} + 2 L_x L_y L_x
= L_{x^2} L_y + 2 L_{xy} L_x.
```

These are the action identities used by this experiment.

## One-Dimensional Idempotent Base

Let:

```text
J = k e,
e^2 = e,
M = k m,
L_e(m) = lambda m.
```

The extension has:

```text
e^2 = e,
e m = lambda m,
m^2 = 0.
```

The nontrivial scalar condition is:

```text
lambda(lambda - 1)(2 lambda - 1) = 0.
```

Thus the nonunital Jordan condition allows:

```text
lambda in {0, 1/2, 1}.
```

If `(e, 0)` must remain the unit in the extension, then:

```text
lambda = 1.
```

## One-Dimensional Zero-Multiplication Base

Let:

```text
J = k e,
e^2 = 0,
M = k m,
L_e(m) = lambda m.
```

The scalar condition becomes:

```text
2 lambda^3 = 0.
```

In characteristic `0`, this forces:

```text
lambda = 0.
```

## Basis-Only Warning

A basis-vector Jordan identity check is only a smoke test. In this experiment,
the value `lambda = 2` for the idempotent base can pass the basis-only check
but fails on a finite grid of linear combinations. The experiment runner records
this as a false-positive example.
