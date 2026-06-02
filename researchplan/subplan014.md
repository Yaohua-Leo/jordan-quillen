# subplan014: Backend Differential And Multiplicative-Ideal Audit

## 0. Plan Boundary

This plan creates a new experiment, EXP014.  It does not extend EXP011,
EXP012, or EXP013, and it does not change their stored results.  The purpose is
to audit whether the current `low_weight_jordan` ordinary backend quotient can
be interpreted as a dg Jordan quotient in the bounded range under test.

EXP014 does not search for new generators, does not apply `Q`, and does not
construct `V3,V4,...`.

The target directory is:

```text
experiments/014-backend-differential-ideal-audit/
```

## 1. Mathematical Object

Work in the same square-zero two-generator first-layer model used by EXP011:

```text
A^(1) = Jord<x, y, r_xx, r_xy, r_yy>
```

with:

```text
d(x) = d(y) = 0
d(r_xx) = x^2
d(r_xy) = xy
d(r_yy) = y^2
```

The backend is the existing ordinary commutative nonassociative Jordan backend:
relations are imposed by the `low_weight_jordan` relation rows, and the
differential is the signed derivation differential already used in EXP011 and
EXP013.

## 2. Audit Questions

For every bounded homogeneous backend relation row `R`, EXP014 checks:

```text
reduce(R) = 0
reduce(d(R)) = 0
reduce(R*m) = 0
```

Here `m` ranges over quotient basis multipliers whose degree and weight keep the
product inside the requested audit bounds.

The two structural questions are:

```text
1. Is the relation ideal stable under multiplication?
2. Is the relation ideal stable under the differential?
```

The default bounded range is:

```text
max_weight = 10
max_degree = 2
multiplier_degrees = 0,1,2 where total_degree <= max_degree
```

Degree-0 multipliers are especially important, because EXP013 found
obstructions of the form `d(z*x)` for chosen EXP011 candidate representatives.

## 3. Required Record Fields

Each relation audit record should include at least:

```text
source_degree
source_weight
relation_index
relation_formula
relation_reduces_to_zero
differential_stable
multiplication_stable
first_differential_defect
first_multiplication_defect
```

The global result should include:

```text
relation_rows_checked
differential_failures
multiplication_failures
passed
backend_dg_quotient_evidence
```

## 4. Output Files

For `W=10`, EXP014 should write:

```text
results.json
data/relation_stability_W10.json
data/first_failures_W10.json
logs/run_W10.log
tex/exp014_backend_differential_ideal_audit.tex
```

## 5. Result Semantics

If:

```text
passed = true
```

then EXP014 has found no bounded relation-ideal stability failure in the tested
range.  This is bounded computational evidence only; it is not a global theorem.

If:

```text
passed = false
```

then the current bounded backend should not be interpreted as a strict dg
Jordan quotient in the tested range.  EXP011 `H1_old` and EXP013 strict
attachability obstructions should then be treated as backend-relative
diagnostics until the backend quotient convention is repaired or separately
justified.

## 6. Test Plan

The implementation should add tests for:

- relation rows reducing to zero in the backend quotient;
- differential stability defects being reported when present;
- multiplication stability defects being reported when present;
- the EXP013-style phenomenon where a weight-local zero multiplied by `x`
  becomes nonzero in the next weight;
- report language stating no `Q`, no `V3+`, no global theorem, and bounded
  backend audit only.

Full verification:

```powershell
python -m pytest
python -m ruff check .
python scripts/check_claims.py
```

## 7. Default Run

```powershell
python experiments/014-backend-differential-ideal-audit/run.py `
  --max-weight 10 `
  --max-degree 2 `
  --mode validation `
  --workers 6 `
  --max-memory-gb 20
```

## 8. Follow-Up Boundary

If EXP014 fails, the next step should be a backend correction experiment, not a
stronger interpretation of EXP011 candidates as genuine attaching cells.

If EXP014 passes in the requested bounded range, the next natural experiment is
EXP015: directly compute bounded full homology `H_d(A^(1))_w` and test whether
`A^(1) -> J` is a quasi-isomorphism in that range.
