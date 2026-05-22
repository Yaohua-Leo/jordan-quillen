# CLAIM-0002: Indecomposables Left Adjoint

Status: draft

Statement:
The functor `Q(J) = J/J^2` is expected to be left adjoint to the inclusion of
vector spaces as zero-multiplication Jordan algebras.

Dependencies:
- `CLAIM-0001-zero-multiplication-abelian-objects.md`

Proof sketch:
Any Jordan homomorphism from `J` to a zero-multiplication algebra kills every
product `xy`, hence factors uniquely through `J/J^2`.

References:
- `literature/notes/on-homology-of-jordan-algebras.md`

Verification notes:
The proof is straightforward but should be written with the chosen unital or
nonunital convention.
