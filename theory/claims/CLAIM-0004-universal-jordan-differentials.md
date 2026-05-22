# CLAIM-0004: Universal Jordan Differentials

Status: conjectural

Statement:
There should be a Jordan module `Omega_{J/A}` representing `A`-linear Jordan
derivations from `J` to any `J`-module `M`.

Dependencies:
- `CLAIM-0003-beck-modules-vs-jordan-modules.md`
- `theory/05-derivations-and-omega.md`

Proof sketch:
Start from formal symbols `d x` and impose linearity, base relations, and the
Leibniz relation `d(xy) = x d(y) + y d(x)`. Then verify the resulting object is
initial among derivations.

References:
- `literature/notes/quillen-1970.md`

Verification notes:
The construction depends on the final Jordan module convention.
