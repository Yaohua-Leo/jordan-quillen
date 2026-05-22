# 06. Cotangent Complex

The Jordan cotangent complex should be the derived version of universal
Jordan differentials.

Working notation:

```text
L^Jord_{J/A} = L Ab_A(J)
```

or equivalently, after choosing a cofibrant/simplicial resolution `P -> J`,

```text
L^Jord_{J/A} = Omega_{P/A} tensor_P J.
```

This formula is provisional until the module category and resolution category
are fixed.

## Homology And Cohomology

Expected definitions:

```text
D_q^Jord(J/A, M) = H_q(L^Jord_{J/A} tensor_J M)
D^q_Jord(J/A, M) = H^q Hom_J(L^Jord_{J/A}, M)
```
