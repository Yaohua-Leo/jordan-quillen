# subplan001: Align Experiment 001 With Split Square-Zero Sanity Checks

## 0. Stage Goal

`subplan001` is the first minimal workflow test for this repository. It should
not prove the Jordan-Quillen theory, define the full Beck module category, or
settle `CLAIM-0003`.

The target directory is:

```text
experiments/001-square-zero/
```

The goal is to replace the placeholder experiment with a small, reproducible,
exact-arithmetic sanity check for split square-zero extensions

```text
E = J plus M,        M^2 = 0.
```

The workflow to test is:

```text
repository conventions -> hand computation -> minimal code -> toy checks
-> real result file -> tests and claim checks -> human review
```

The central question for this stage is:

```text
Given a Jordan algebra J and a vector space M, which scalar actions in tiny
examples make J plus M into a Jordan algebra with M^2 = 0?
```

This stage may support later Beck module work, but it is only toy evidence and
workflow validation.

## 1. Scope Boundary

`subplan001` is smaller than the general Beck module derivation:

- It studies only split extensions.
- It uses only one-dimensional toy families.
- It uses exact rational arithmetic through Python `Fraction`.
- It does not introduce Sage, SymPy, NumPy, or any new dependency.
- It does not introduce a full `SquareZeroExtension` public API.
- It does not change the status of `CLAIM-0003`.

Relationship to nearby work:

- `experiments/001-square-zero/` is the first runnable sanity check.
- `experiments/003-beck-module-identities/` remains the later symbolic or
  general derivation surface.
- `subplan002` and `experiments/002-two-dimensional-jordan/` focus on a
  two-dimensional nilpotent Jordan algebra and should not be folded into this
  stage.

## 2. Mathematical Conventions

Use the repository default unless a file states otherwise:

- The base field `k` has characteristic `0`, or at least `char(k) != 2,3`.
- Jordan algebras may be nonunital unless unitality is explicitly required.
- The product is commutative and is written as `xy` or `x * y`.
- The split square-zero extension has underlying vector space `E = J plus M`.
- The multiplication on `E` is:

```text
(x, m) * (y, n) = (xy, L_x(n) + L_y(m)).
```

Here `L_x(m) = x . m` is the candidate action of `J` on `M`.

Non-split extensions and extension classification are out of scope.

## 3. Hand Computation Target

Use the Jordan identity in the form:

```text
((a*a)*b)*a = (a*a)*(b*a).
```

Set:

```text
a = (x, m),
b = (y, n).
```

Keeping only the `M`-linear terms gives:

```text
a^2 = (x^2, 2 L_x m).
```

The two sides have `M`-parts:

```text
((a^2 b)a)_M
= L_{x^2 y}(m) + L_x L_{x^2}(n) + 2 L_x L_y L_x(m),

(a^2(ba))_M
= L_{x^2} L_y(m) + L_{x^2} L_x(n) + 2 L_{xy} L_x(m).
```

Therefore the split square-zero extension should satisfy:

```text
L_x L_{x^2} = L_{x^2} L_x
```

and:

```text
L_{x^2 y} + 2 L_x L_y L_x
= L_{x^2} L_y + 2 L_{xy} L_x.
```

These are the formulas to record in the experiment. They are not yet a proof
that Beck modules equal any chosen classical Jordan module category.

## 4. Toy Families

### Zero action

If `L_x = 0` for every `x in J`, then `M` is an annihilator ideal. If `J`
itself is Jordan, this gives the most basic smoke test.

### Idempotent one-dimensional base

Let:

```text
J = k e,
e^2 = e,
M = k m,
L_e(m) = lambda m.
```

Then:

```text
e^2 = e,
e m = lambda m,
m^2 = 0.
```

Substituting into the action identity gives:

```text
lambda(lambda - 1)(2 lambda - 1) = 0.
```

For nonunital Jordan algebras, the expected tested values are:

```text
lambda in {0, 1/2, 1}.
```

If `(e, 0)` is required to remain the unit in the extension, then:

```text
lambda = 1.
```

### Zero-multiplication one-dimensional base

Let:

```text
J = k e,
e^2 = 0,
M = k m,
L_e(m) = lambda m.
```

The action identity gives:

```text
2 lambda^3 = 0.
```

In characteristic `0`, the expected tested value is:

```text
lambda = 0.
```

This example is useful because it shows that even a zero-multiplication base
does not allow an arbitrary scalar action.

## 5. Implementation Target

Touch only the narrow files needed for this stage:

```text
researchplan/subplan001.md
experiments/001-square-zero/experiment.md
experiments/001-square-zero/hand-computation.md
experiments/001-square-zero/run.py
experiments/001-square-zero/results.json
src/jordan_qh/examples.py
tests/test_square_zero_extensions.py
```

Implementation requirements:

- `run.py` must work from the repository root with:

```text
python experiments/001-square-zero/run.py
```

- `run.py` must enumerate:

```text
lambda in {-2, -1, -1/2, 0, 1/2, 1, 2}.
```

- The checker must use a finite grid of linear combinations, not only basis
  vectors.
- `results.json` must be written by the actual script run.
- The result must record the tested lambdas, passing lambdas, checker type,
  basis-only warning, and interpretation.

The existing basis-only checker is useful as a smoke test, but it can miss bad
actions. In particular, for `e^2 = e` and `lambda = 2`, a basis-only check can
pass while a finite grid check fails. This false-positive risk must remain
visible in the plan, tests, and result file.

## 6. Acceptance Criteria

The stage is complete when:

1. `subplan001.md` is in English and states the narrow stage boundary.
2. `experiments/001-square-zero/experiment.md` describes a split square-zero
   sanity check, not a proof.
3. `hand-computation.md` records the action identities and toy predictions.
4. `run.py` generates deterministic `results.json`.
5. For `e^2 = e`, the tested Jordan scalar actions are exactly
   `{0, 1/2, 1}`.
6. For `e^2 = 0`, the tested Jordan scalar action is exactly `{0}`.
7. The result distinguishes the nonunital Jordan condition from the unital
   extension condition.
8. Tests cover the lambda classifications and the basis-only false-positive
   example.
9. Verification passes:

```text
python experiments/001-square-zero/run.py
python -m pytest
python scripts/check_claims.py
python -m ruff check .
```

## 7. Non-Goals

Do not do the following in this stage:

- Do not prove the full Beck module equivalence.
- Do not define the full module category.
- Do not define `Omega_{J/A}`.
- Do not construct a cotangent complex.
- Do not compute higher Quillen homology.
- Do not do TKK comparison.
- Do not add new dependencies.
- Do not treat finite-grid checks as general algebraic proofs.
- Do not mark `CLAIM-0003` as proved.
- Do not rewrite unread or partial literature notes as checked conclusions.

## 8. Human Review Questions

After implementation, review:

1. Did the workflow correctly separate experiment, claim, and proof?
2. Is the `results.json` shape stable enough for later experiments?
3. Should the basis-only checker be renamed more broadly, or is the docstring
   warning enough for now?
4. Should `experiments/003-beck-module-identities/` reuse the one-dimensional
   helper, or wait for a general symbolic derivation?
5. Is `subplan002` still cleanly separated from this first sanity check?
