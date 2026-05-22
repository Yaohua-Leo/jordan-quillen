# 05. Derivations And Omega

A Jordan derivation from a Jordan algebra `J` to a `J`-module `M` should satisfy

```text
d(xy) = x d(y) + y d(x).
```

The universal object `Omega_{J/A}` should represent these derivations:

```text
Hom_J(Omega_{J/A}, M) ~= Der_A(J, M).
```

## Open Points

- Fix the precise category of `J`-modules.
- Construct `Omega_{J/A}` by generators and relations.
- Check compatibility with `Q(J) = J/J^2` in the absolute zero-base case.
