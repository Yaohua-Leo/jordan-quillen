# On Homology of Jordan Algebras

Status: source-read

Local file: `literature/papers-local/on_homology_of_jordan_algebras(1).pdf`

## Core Idea

This short note proposes the intrinsic homology of Jordan algebras as Quillen
homology: derive the indecomposables functor

```text
Q(J) = J / J^2
```

where `J^2` is the linear span of all Jordan products `xy`.

Because Jordan algebras are already commutative, quotienting by commutators is
not the correct abelianization. The abelian objects in the absolute category
should instead be the Jordan algebras with zero multiplication, and the
left-adjoint candidate is `Q`.

## Operadic Setup

Over a field of characteristic zero, Jordan algebras can be treated as algebras
over the Jordan operad. The note cites the multilinearized Jordan identity and
uses transferred model structures for algebras over operads in chain complexes.

## Relation To TKK

The Tits-Kantor-Koecher construction gives a Lie algebra associated to a
Jordan object. Its Lie homology is a useful external invariant, but it is not
the same as intrinsic Quillen homology of Jordan algebras.

## Project Consequence

The absolute homology `H_n LQ(J)` is a good entry point, but the research
project should also construct the relative cotangent complex over a base
Jordan algebra so that low-degree cohomology can classify derivations and
extensions.
