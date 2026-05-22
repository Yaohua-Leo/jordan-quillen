# 07. Transitivity And Base Change

Quillen's commutative-ring theory suggests two primary structural tests.

## Transitivity

For `A -> B -> C`, expect a distinguished triangle of `C`-modules:

```text
C tensor_B L^Jord_{B/A} -> L^Jord_{C/A} -> L^Jord_{C/B} -> Sigma(...)
```

This is a claim, not yet a theorem in this repository.

## Base Change

For a square of Jordan algebras, expect base-change compatibility under
flatness or Tor-vanishing hypotheses. The correct flatness notion depends on
the chosen Jordan module category.
