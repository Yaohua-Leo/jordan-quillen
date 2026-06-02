# subplan101: One-Generator Generator Legality Audit

## 0. Boundary

This plan creates EXP101.  It audits the generator candidates computed by
EXP100 and does not change EXP100 results.  It does not apply \(Q\), does not
construct \(V_3,V_4,\ldots\), and does not make homology killing claims.

The target directory is:

```text
experiments/101-one-generator-generator-legality-audit/
```

## 1. Input

Use the EXP100 W10 output as the candidate source:

```text
experiments/100-square-zero-nonunital-cofibrant-weight10/results.json
experiments/100-square-zero-nonunital-cofibrant-weight10/data/cells_W10.json
```

The candidates are:

```text
V1: r1_00001_w2, r1_00002_w10, r1_00003_w10
V2: s2_00001_w4, s2_00002_w7, s2_00003_w8, s2_00004_w10, s2_00005_w10
```

The default audit bound is \(W=12\).  This is intentionally wider than EXP100's
\(W=10\), because a same-weight check alone cannot test whether a weight-10
candidate stays legal after multiplication by \(x\).

## 2. V1 Relation-Generator Legality

For each EXP100 \(V_1\) cell with differential \(p_i\), check through the
requested bound:

```text
for every degree-0 multiplier m with wt(p_i) + wt(m) <= W:
    epsilon(p_i * m) = 0 in J = Jord<x>/(x^2)
```

Also build the \(A^{(1)}\) model with all EXP100 \(V_1\) cells and record
\(d^2(r_i)=0\) for each declared generator.

## 3. V2 Strict Attachability

For each EXP100 \(V_2\) cell with proposed differential \(z_i\), run the
EXP013-style strict attachability audit:

```text
for every degree-0 multiplier m with wt(z_i) + wt(m) <= W:
    reduce(d(z_i * m)) = 0 in A^(1)_0
```

The generator-level case \(m=1\) must be recorded separately.  If a later
multiplier produces a nonzero defect, record:

```text
cell_name
cell_weight
target_weight
multiplier
defect_normal_form
defect_sparse_coordinates
raw_differential
```

A failed strict attachability check means that the chosen EXP100 representative
is not accepted as a strict dg attaching differential in the tested bounded
backend.  It does not rule out an alternate representative or corrected lift.

## 4. Chain Condition

In the \(A^{(1)}\) model built from the EXP100 \(V_1\) cells, verify for every
weight \(1\leq w\leq W\):

```text
d2_matrix @ d1_matrix = 0
```

Record \(\dim C_0\), \(\dim C_1\), \(\dim C_2\), `rank_d1`, `rank_d2`, and the
chain-condition boolean.

## 5. Outputs

For \(W=12\), EXP101 writes:

```text
results.json
data/v1_legality_W12.json
data/v2_strict_attachability_W12.json
data/chain_audit_W12.json
logs/run_W12.log
tex/exp101_one_generator_generator_legality_audit.tex
```

## 6. Default Run

```powershell
python experiments/101-one-generator-generator-legality-audit/run.py `
  --max-weight 12 `
  --reference-results experiments/100-square-zero-nonunital-cofibrant-weight10/results.json `
  --reference-cells experiments/100-square-zero-nonunital-cofibrant-weight10/data/cells_W10.json
```

## 7. Verification

Run:

```powershell
python -m pytest
python -m ruff check .
python scripts/check_claims.py
```

Required checks:

- all EXP100 \(V_1\) relation generators are legal through \(W=12\);
- all declared generators in \(A^{(1)}\) have \(d^2=0\);
- every EXP100 \(V_2\) candidate is checked by the strict attachability audit;
- `s2_00001_w4` records its first strict defect at target weight `6` with
  multiplier `(x*x)`;
- both weight-10 \(V_2\) candidates are tested after multiplication by `x` at
  target weight `11`;
- report language preserves the bounded, no-\(Q\), no-\(V_3+\) boundary.
