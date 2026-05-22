# Quillen 1970: On the (co-)homology of commutative rings

Status: source-read partial

Local file: `literature/papers-local/On_the_cohomology_of_commutative_rings(1).pdf`

## Core Idea

Quillen defines homology and cohomology for algebraic categories by choosing a
simplicial cofibrant resolution and deriving abelianization. For commutative
rings this becomes the cotangent complex `L_{B/A}`.

For a morphism of commutative rings `A -> B` and a `B`-module `M`, the theory
recovers:

- `D^0(B/A, M) = Der_A(B, M)`.
- `D^1(B/A, M) = Exalcomm_A(B, M)`.
- `D^q(B/A, M) = H^q Hom_B(L_{B/A}, M)`.
- `D_q(B/A, M) = H_q(L_{B/A} tensor_B M)`.

## Structural Results To Port

- Transitivity: for `A -> B -> C`, there is a distinguished triangle involving
  `C tensor_B L_{B/A}`, `L_{C/A}`, and `L_{C/B}`.
- Flat base change: under Tor-vanishing hypotheses, cotangent complexes commute
  with base change.
- Vanishing criteria: etale, smooth, and local complete intersection morphisms
  are detected by the shape of `L_{B/A}`.
- Characteristic zero: Harrison cohomology computes commutative algebra
  cohomology under projectivity/flatness hypotheses.

## Relevance For Jordan Algebras

The paper suggests the order of attack:

1. Identify abelian group objects over a Jordan algebra.
2. Identify the abelianization functor in the slice category.
3. Derive that functor by a simplicial or dg resolution.
4. Use the resulting cotangent complex as the primary invariant.

The Jordan project should not begin by guessing a cochain formula. It should
first construct the object whose Hom and tensor groups define cohomology and
homology.

## Open Reading Tasks

- Compare Quillen's general algebraic-category hypotheses with operadic model
  structures for Jordan algebras.
- Check how Andre's method phrases the same objects.
- Extract the exact hypotheses needed for transitivity and base change.
