# PLAN

## Milestone 0: Scaffold

Status: in progress

- Initialize the repository in the current directory.
- Move local PDFs to `literature/papers-local/` and ignore them.
- Create substantive placeholders for literature, theory, claims, examples,
  experiments, paper, and formalization.
- Keep the computation backend undecided.

## Milestone 1: Definitions

Goal: make the Jordan version of Quillen's setup precise.

- Fix conventions: base field, characteristic assumptions, grading, signs, and
  unital versus nonunital Jordan algebras.
- Prove or refute that zero multiplication objects are the abelian objects in
  the absolute category.
- Identify Beck modules over a Jordan algebra with the correct notion of Jordan
  module through square-zero extensions.
- Define Jordan derivations and universal Jordan differentials.

## Milestone 2: Cotangent Complex

Goal: define the object that controls both homology and cohomology.

- Choose a resolution framework: simplicial Jordan algebras, dg Jordan
  algebras over the Jordan operad, or an equivalent comparison.
- Define `L^Jord_{J/A}` and its homology groups.
- State expected transitivity and base-change properties with exact
  hypotheses.
- Record every proof obligation as a claim file.

## Milestone 3: Computation and Comparison

Goal: connect definitions to examples and existing theories.

- Compute zero multiplication and one-dimensional examples.
- Test square-zero extensions and low-degree derivations.
- Compare intrinsic Quillen homology with TKK Lie algebra homology.
- Decide whether the compute layer should be pure Python, Sage, or a hybrid.

## Milestone 4: Writeup

Goal: turn stable definitions and examples into a paper-style note.

- Draft the introduction and motivation.
- Write the modules, cotangent complex, low-degree, comparison, and examples
  sections.
- Keep the paper synchronized with claim statuses.
