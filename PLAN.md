# PLAN

## Jordan Quillen Homology Project

Last aligned with the workspace: 2026-05-24.

## 0. Project Thesis

This project develops the intrinsic Quillen homology and cohomology theory of
Jordan algebras.

The guiding idea is that, for nonunital or augmented Jordan algebras, the
indecomposables functor should be

\[
Q(J) = J / J^2,
\]

and the desired homology theory should be the left derived functor of `Q`.
The goal is not just to record this slogan, but to make it usable by
constructing and comparing:

1. Beck modules over a Jordan algebra;
2. square-zero extensions;
3. Jordan derivations and universal Jordan differentials;
4. the Jordan cotangent complex;
5. low-degree Quillen cohomology;
6. comparison with Glassman cohomology;
7. comparison with TKK/Lie-theoretic homology;
8. computable exact examples.

The default base field is a field `k` of characteristic `0`. Computations should
usually use exact arithmetic over `\mathbb Q`.
Complex examples are treated as base changes
`J_\mathbb C = J_\mathbb Q \otimes_\mathbb Q \mathbb C`
whenever possible. If genuinely complex coefficients are needed, use exact
number fields or algebraic numbers rather than floating-point complex numbers.

## 1. Scope

### In Scope

- Nonunital Jordan algebras.
- Augmented unital Jordan algebras via the augmentation ideal.
- Finite-dimensional examples over `\mathbb Q`.
- Square-zero extensions.
- Beck modules.
- Universal differentials.
- Cotangent complexes.
- Low-degree Quillen cohomology.
- Comparison with Glassman and TKK theories in small degrees or small examples.

### Out Of Scope For The First Stage

- Full minimal models of the Jordan operad.
- Complete computation of arbitrary free Jordan algebras.
- Full equivalence with TKK Lie algebra homology.
- General characteristic.
- Full Lean formalization of operadic model categories.
- Any claim that intrinsic Jordan Quillen homology equals TKK Lie homology
  without an explicit proof or counterexample.

## 2. Current Workspace Baseline

This plan is written against the current repository, not a blank scaffold.

Existing project surfaces:

- `AGENTS.md` contains the local research and verification rules.
- `README.md` explains the current repository purpose and quick checks.
- `pyproject.toml` defines a Python package named `jordan-quillen`, Python
  `>=3.11`, no runtime dependencies, and development extras for `pytest`,
  `ruff`, and `pre-commit`.
- `Makefile` exposes `test`, `lint`, `claims`, `literature-index`, and
  `experiments` targets.
- `theory/` already contains `00` through `11` theory notes.
- `theory/claims/` currently contains claim files `CLAIM-0001` through
  `CLAIM-0005`.
- `src/jordan_qh/` already contains a small exact Python scaffold for algebras,
  tensors, identities, derivations, modules, omega, low-degree expectations,
  and TKK comparison placeholders.
- `tests/` already contains smoke tests for the Python scaffold.
- `experiments/` currently contains numbered experiment directories. The
  numbers are stable workspace identifiers, not a logical dependency order:
  later-numbered experiments may be run or reviewed before earlier ones.
- `experiments/005-quillen-derived-indecomposables/` has a pure-Python toy
  benchmark result for one-generator derived indecomposables.
- `experiments/006-presentation-invariance-j3/` has a first-pass result for
  Presentation A of `J_3=(t)/(t^3)` and explicitly records that Presentation B
  is not implemented in the toy model.
- `paper/` already contains a LaTeX skeleton with section files.
- `formal/lean/` contains a Lean scaffold, but formalization is not part of the
  default verification path.
- `codex/local-math-tools.md` is the current local tool snapshot for Sage,
  CAS, Lean, and related tools. Re-check paths before relying on them.

Current verification commands:

```powershell
python -m pytest
python -m ruff check .
python scripts/check_claims.py
```

For plan-only or Markdown-only edits, use at least `git diff --check` on the
changed file. For claim-file edits, also run `python scripts/check_claims.py`.
For Python changes, run the full Python test suite.

## 3. Repository Principles

Every mathematical claim must be tracked. Substantial statements belong in:

```text
theory/claims/
```

Each claim file must contain at least the metadata required by
`scripts/check_claims.py`:

- `Status:`
- `Statement:`
- `Dependencies:`
- `Proof sketch:`
- `References:`
- `Verification notes:`

Allowed working statuses include:

```text
idea
draft
conjecture
conjectural
proof-draft
checked
false
blocked
abandoned
```

The current claim files use `draft` and `conjectural`. Prefer those spellings
unless the repository later enforces a stricter enum. No claim should be marked
`checked` unless the proof has been manually reviewed.

Every computational result must be reproducible from code or a notebook.
Final examples should use exact arithmetic over `\mathbb Q`, not floating-point
arithmetic. A result file may honestly say `not run yet`; it must not contain
fabricated output.

Use `theory/latex_notation.md` as the notation reference before normalizing
paper or theory notation.

## 4. Milestone 0: Scaffold

Status: scaffold present; content and verification discipline remain active.

### Goal

Maintain a repository that can support literature review, mathematical theory,
computations, experiments, paper writing, and limited formalization.

### Existing Deliverables

- `README.md`
- `AGENTS.md`
- `PLAN.md`
- `Makefile`
- `pyproject.toml`
- `.gitignore`
- `theory/00-conventions.md`
- `theory/03-abelianization.md`
- `theory/claims/CLAIM-0001-zero-multiplication-abelian-objects.md`
- `theory/claims/CLAIM-0002-indecomposables-left-adjoint.md`
- `literature/papers-local/` ignored for local PDF-style source material
- `src/`, `tests/`, `experiments/`, `paper/`, `formal/`, `codex/`, and
  `scripts/`

### Remaining Tasks

- Keep `AGENTS.md`, `README.md`, `PLAN.md`, and `theory/latex_notation.md`
  synchronized when conventions change.
- Keep local PDFs and private notes out of git.
- Keep experiment output honest when a backend has not been selected or run.
- Avoid renumbering existing claim files unless there is a deliberate migration.

### Success Criteria

- The repository structure remains stable.
- Codex can understand the project from `AGENTS.md`, `README.md`, and this
  plan.
- PDFs are not committed to git.
- There is a clear place for each future claim, experiment, computation, paper
  section, and formalization fragment.

## 5. Milestone 1: Conventions And Abelianization

Status: active draft. `CLAIM-0001` and `CLAIM-0002` exist but are not checked.

### Goal

Make the Jordan version of Quillen's setup precise.

### Main Questions

1. What base category is being used?
2. Are algebras unital, nonunital, augmented, or relative?
3. What are the abelian objects?
4. Is

   \[
   Q(J) = J / J^2
   \]

   the correct abelianization functor in the chosen category?
5. What degenerates in the unital case?

### Tasks

- Fix the default assumptions:
  - base field `k`;
  - characteristic assumptions;
  - grading convention;
  - homological versus cohomological indexing;
  - sign convention;
  - unital, nonunital, augmented, and relative conventions.
- Prove or refute that zero-multiplication Jordan algebras are the abelian
  objects in the absolute nonunital category.
- Prove or refute that

  \[
  Q(J) = J / J^2
  \]

  is left adjoint to the inclusion of zero-product vector spaces or complexes.
- Record the unital degeneration:

  \[
  1 \cdot x = x
  \quad\Rightarrow\quad
  J^2 = J
  \quad\Rightarrow\quad
  Q(J) = 0.
  \]

- Decide the first working setting:
  - nonunital Jordan algebras;
  - augmented unital Jordan algebras;
  - relative Jordan algebras over a base.

### Deliverables

- `theory/00-conventions.md`
- `theory/03-abelianization.md`
- `theory/claims/CLAIM-0001-zero-multiplication-abelian-objects.md`
- `theory/claims/CLAIM-0002-indecomposables-left-adjoint.md`

### Success Criteria

- The functor `Q(J) = J / J^2` is precisely stated.
- The adjunction is written down with assumptions.
- The unital problem is explicitly documented.
- The project has chosen a default convention for the next milestones.

## 6. Milestone 2: Beck Modules And Square-Zero Extensions

Status: scaffolded; central comparison remains conjectural.

### Goal

Identify the correct coefficient objects for Jordan Quillen cohomology.

### Main Question

Are Beck modules over a Jordan algebra `J` equivalent to the appropriate
classical category of Jordan `J`-modules?

### Tasks

- Define square-zero extensions:

  \[
  J \ltimes M.
  \]

- Define the multiplication:

  \[
  (x,m)(y,n) = (xy,\; x \cdot n + y \cdot m).
  \]

- Expand the Jordan identity in `J \ltimes M` modulo `M^2 = 0`.
- Extract the identities forced on the `J`-action on `M`.
- Compare these identities with classical definitions of Jordan modules in
  Jacobson, McCrimmon, Glassman, and the checked literature notes.
- Decide whether the coefficient category should be called:

  ```text
  J-Mod
  J-Bimod
  Beck(J)
  ```

  or something else.

### Current Workspace Anchors

- `theory/04-beck-modules.md`
- `theory/claims/CLAIM-0003-beck-modules-vs-jordan-modules.md`
- `experiments/003-beck-module-identities/experiment.md`
- `experiments/003-beck-module-identities/derive_relations.py`
- `src/jordan_qh/modules.py`
- `tests/test_modules.py`

### Success Criteria

- The category of coefficient objects is precisely defined.
- The square-zero extension condition is expanded explicitly.
- The relationship between Beck modules and classical Jordan modules is proved,
  refuted, or isolated as a precise open claim.

### Risks

- Classical Jordan module conventions may differ between sources.
- The nonunital and unital cases may require different formulations.
- The Beck module category may not coincide exactly with the most familiar
  Jordan module category.

## 7. Milestone 3: Jordan Derivations And Universal Differentials

Status: scaffolded; universal property remains conjectural.

### Goal

Construct the Jordan analogue of Kahler differentials.

### Main Questions

1. What is a Jordan derivation `d: B -> M`?
2. Is there a universal object

   \[
   \Omega^{\mathrm{Jord}}_{B/A}?
   \]

3. What relations must

   \[
   \Omega^{\mathrm{Jord}}_{B/A}
   \]

   satisfy?

### Tasks

- Define relative Jordan derivations:

  \[
  \operatorname{Der}^{\mathrm{Jord}}_A(B,M).
  \]

- Construct a candidate universal differential module
  `\Omega^{\mathrm{Jord}}_{B/A}` by generators and relations.
- Include the Leibniz relation:

  \[
  d(xy) = x\,dy + y\,dx.
  \]

- Add all relations forced by the Jordan identity and by the chosen module
  identities.
- Prove or refute the universal property:

  \[
  \operatorname{Der}^{\mathrm{Jord}}_A(B,M)
  \cong
  \operatorname{Hom}_{B\text{-mod}}
  (\Omega^{\mathrm{Jord}}_{B/A},M).
  \]

### Current Workspace Anchors

- `theory/05-derivations-and-omega.md`
- `theory/claims/CLAIM-0004-universal-jordan-differentials.md`
- `src/jordan_qh/derivations.py`
- `src/jordan_qh/omega.py`
- `tests/test_derivations.py`
- `tests/test_omega.py`

### Success Criteria

- Jordan derivations are precisely defined.
- A candidate `\Omega^{\mathrm{Jord}}_{B/A}` is written.
- The universal property is proved or reduced to explicit module relations.
- Small examples can compute derivation spaces exactly.

## 8. Milestone 4: Resolution Framework And Cotangent Complex

Status: theory placeholder exists; framework decision remains open.

### Goal

Define the Jordan cotangent complex.

### Main Decision

Choose the main resolution framework:

1. simplicial Jordan algebras;
2. dg Jordan algebras over the Jordan operad;
3. both, with a comparison statement.

### Tasks

- Decide the primary framework.
- State the model-categorical assumptions needed.
- Define cofibrant or projective resolutions in the chosen setting.
- For a morphism `A -> B`, define:

  \[
  L^{\mathrm{Jord}}_{B/A}.
  \]

- Candidate formula:

  \[
  L^{\mathrm{Jord}}_{B/A}
  =
  B \otimes_P \Omega^{\mathrm{Jord}}_{P/A},
  \]

  where `P -> B` is a suitable resolution.
- Prove homotopy invariance or record the exact proof obligation.
- Add a cotangent-complex claim file using the next available claim ID. Do not
  reuse `CLAIM-0005`, which already records the transitivity triangle.

### Current Workspace Anchors

- `theory/02-operadic-setup.md`
- `theory/06-cotangent-complex.md`
- `src/jordan_qh/cohomology_low.py`

### Success Criteria

- `L^{\mathrm{Jord}}_{B/A}` is defined precisely.
- The definition clearly states the required hypotheses.
- The relation with derived indecomposables is explained.
- All unresolved model-categorical assumptions are recorded as claim files.

## 9. Milestone 5: Formal Properties

Status: placeholder and conjectural claim exist for transitivity.

### Goal

Test whether the Jordan cotangent complex satisfies the expected
Quillen-style properties.

### Main Properties

For morphisms

\[
A \to B \to C,
\]

expect a transitivity triangle:

\[
C \otimes_B^{\mathbb L} L^{\mathrm{Jord}}_{B/A}
\to
L^{\mathrm{Jord}}_{C/A}
\to
L^{\mathrm{Jord}}_{C/B}
\to
\Sigma C \otimes_B^{\mathbb L} L^{\mathrm{Jord}}_{B/A}.
\]

Also investigate base change and vanishing for free or cofibrant objects.

### Tasks

- State transitivity with exact hypotheses.
- State base change with exact hypotheses.
- Prove vanishing for free or cofibrant Jordan algebras where possible.
- Derive long exact sequences in cohomology.
- Record each proof obligation as a separate claim.

### Current Workspace Anchors

- `theory/07-transitivity-and-base-change.md`
- `theory/claims/CLAIM-0005-transitivity-triangle.md`

### Future Claim Files

Use next available claim IDs for:

- base change;
- free or cofibrant vanishing;
- long exact sequences;
- any corrected cotangent-complex definition claim not yet represented by an
  existing claim file.

### Success Criteria

- The formal properties are stated with exact assumptions.
- Missing technical conditions are explicitly recorded.
- The theory has enough structure to support low-degree cohomology.

## 10. Milestone 6: Low-Degree Quillen Cohomology

Status: placeholder theory note and Python expectation scaffold exist.

### Goal

Give mathematical meaning to the first few cohomology groups.

### Main Expected Statements

\[
D^0_{\mathrm{Jord}}(B/A,M)
\cong
\operatorname{Der}^{\mathrm{Jord}}_A(B,M).
\]

\[
D^1_{\mathrm{Jord}}(B/A,M)
\cong
\operatorname{Exal}^{\mathrm{Jord}}_A(B,M).
\]

Investigate whether `D^2` controls obstructions to extensions or deformations.

### Tasks

- Define Jordan square-zero extensions.
- Define equivalence of extensions.
- Prove the `D^0` statement.
- Prove or formulate the `D^1` classification.
- Investigate the role of `D^2`.
- Compare with deformation-theoretic interpretations.
- Add claim files with next available IDs for the low-degree statements.

### Current Workspace Anchors

- `theory/08-low-degree-interpretation.md`
- `src/jordan_qh/cohomology_low.py`
- `paper/sections/04-low-degree.tex`

### Success Criteria

- Low-degree groups are connected to concrete algebraic objects.
- The first nontrivial examples are computed exactly.
- Any index shifts are clearly documented.

## 11. Milestone 7: Computation Layer

Status: Python scaffold exists. The current active computation focus is
`experiments/005-quillen-derived-indecomposables/` and
`experiments/006-presentation-invariance-j3/`, not the numeric first
experiment directory.

### Goal

Build enough computation to test definitions on small examples.

### Backend Decision

The computation backend remains open. Candidate options:

1. pure Python with exact rational linear algebra;
2. SageMath;
3. hybrid Python plus Sage;
4. Maple, Wolfram Language, GAP, Singular, Macaulay2, OSCAR, or Magma for
   special tasks.

Default principle:

```text
Use exact arithmetic for mathematical verification.
Use floating point only for exploratory searches.
```

Before using non-Python tools, check `codex/local-math-tools.md` and re-verify
the route if the exact command matters.

### Core Computations

Implement or prototype:

- finite-dimensional Jordan algebras by structure constants;
- Jordan identity checker;
- `J^2` and `J/J^2`;
- derivation spaces;
- square-zero extension checks;
- one-generator derived indecomposables toy checks;
- presentation-invariance stress tests that do not overclaim full cofibrant
  replacement;
- candidate universal differential module;
- small TKK Lie algebra construction where feasible.

### Test Examples

Start with:

1. zero multiplication algebra;
2. one-dimensional algebra `ke` with `e^2 = 0`;
3. one-dimensional algebra `ke` with `e^2 = e`;
4. two-dimensional nilpotent Jordan algebras;
5. Jordan algebra obtained from an associative algebra by symmetrization;
6. small square-zero extensions.

### Current Workspace Anchors

- `src/jordan_qh/algebras.py`
- `src/jordan_qh/identities.py`
- `src/jordan_qh/derivations.py`
- `src/jordan_qh/modules.py`
- `src/jordan_qh/omega.py`
- `src/jordan_qh/indecomposables.py`
- `src/jordan_qh/quillen_toy.py`
- `src/jordan_qh/tkk.py`
- `tests/`
- `experiments/001-square-zero/`
- `experiments/002-two-dimensional-jordan/`
- `experiments/003-beck-module-identities/`
- `experiments/004-tkk-comparison-small-examples/`
- `experiments/005-quillen-derived-indecomposables/`
- `experiments/006-presentation-invariance-j3/`

### Experiment Numbering And Current Priority

Experiment directory numbers are chronological or administrative labels, not a
mathematical prerequisite graph. `001` remains a square-zero workflow surface,
but it is not a blocker for reviewing or rerunning `005` and `006`.

The immediate computation priority is:

1. rerun and manually review `005`, the one-generator derived
   indecomposables benchmark;
2. rerun and manually review `006`, the `J_3=(t)/(t^3)` presentation-warning
   stress test;
3. keep the limitation visible that `006` does not verify presentation
   invariance, because Presentation B is not implemented by the toy model.

### Success Criteria

- Every example is reproducible.
- Every computed dimension is obtained by exact linear algebra.
- Results are written into experiment notes.
- The computation layer supports the theory rather than replacing proofs.

## 12. Milestone 8: Comparison With Existing Theories

Status: comparison notes exist as placeholders or early notes; no comparison
theorem is checked.

### Goal

Understand how intrinsic Jordan Quillen theory relates to existing Jordan
cohomology and TKK/Lie-theoretic constructions.

### Part A: Glassman Comparison

Tasks:

- Extract Glassman's definitions of Jordan cochains and differentials.
- Compare coefficient conventions.
- Compare degrees `0`, `1`, and `2`.
- Identify possible index shifts.
- Determine whether low-degree Quillen cohomology agrees with Glassman
  cohomology.

Deliverable:

```text
theory/09-glassman-comparison.md
```

### Part B: TKK Comparison

Tasks:

- Define the TKK Lie algebra for the examples under consideration.
- Compute or record Lie algebra homology in small examples.
- Compare with intrinsic derived indecomposables.
- Look for natural maps, spectral sequences, or counterexamples.
- Distinguish clearly between:
  - intrinsic Jordan Quillen homology;
  - Lie homology of the TKK algebra.

Deliverables:

```text
theory/10-tkk-comparison.md
experiments/004-tkk-comparison-small-examples/
src/jordan_qh/tkk.py
```

### Success Criteria

- The project does not conflate intrinsic Quillen homology with TKK homology.
- At least one small example is fully worked out.
- A comparison theorem, conjecture, or counterexample is formulated.

## 13. Milestone 9: Paper Draft

Status: LaTeX skeleton exists; content must stay synchronized with checked
claims.

### Goal

Turn stable definitions, claims, and computations into a paper-style note.

### Possible Title

```text
Intrinsic Quillen Cohomology of Jordan Algebras:
Beck Modules, Differentials, and Low-Degree Comparisons
```

### Current Paper Skeleton

```text
paper/main.tex
paper/preamble.tex
paper/macros.tex
paper/sections/01-introduction.tex
paper/sections/02-jordan-modules.tex
paper/sections/03-cotangent-complex.tex
paper/sections/04-low-degree.tex
paper/sections/05-comparison.tex
paper/sections/06-examples.tex
```

### Target Mathematical Structure

```text
1. Introduction
2. Jordan algebras and conventions
3. Abelianization and derived indecomposables
4. Beck modules and square-zero extensions
5. Jordan derivations and universal differentials
6. The Jordan cotangent complex
7. Low-degree Quillen cohomology
8. Comparison with Glassman cohomology
9. Comparison with TKK Lie homology
10. Examples and computations
```

The current paper skeleton may either be expanded to this structure or kept as a
more compact first note. Rename section files only as a deliberate paper
organization task.

### Minimum Publishable Unit

A first note should aim to prove at least:

1. the Beck module classification, or a precise non-equivalence result;
2. the construction and universal property of Jordan differentials;
3. a low-degree interpretation of Quillen cohomology;
4. several exact computations in small examples;
5. a precise comparison or non-comparison with Glassman or TKK theory.

### Success Criteria

- Every theorem in the paper links back to a checked claim file.
- Every example in the paper links back to a reproducible experiment.
- No uncertain statement is presented as proved.

## 14. Optional Milestone: Formalization

Status: Lean scaffold exists; formalization is optional.

### Goal

Formalize small, stable fragments of the theory.

### Good Candidates

- finite-dimensional Jordan algebra structure;
- square-zero extensions;
- derivations;
- basic facts about `J^2`;
- `Q(J) = J/J^2` for nonunital algebras;
- simple examples.

### Not First-Stage Candidates

- model categories;
- general operads;
- cotangent complexes;
- full Quillen cohomology.

### Current Workspace Anchors

- `formal/lean/JordanQuillen/Basic.lean`
- `formal/lean/JordanQuillen/JordanAlgebra.lean`
- `formal/lean/JordanQuillen/SquareZeroExtension.lean`
- `formal/lean/JordanQuillen/Derivations.lean`
- `formal/lean/lakefile.lean`

### Success Criteria

- Formalization supports the mathematical writing.
- Formalization does not become the main bottleneck.
- Lean checks are run only when a formalization task is explicitly selected.

## 15. Decision Log

### D-001: Working Category

Status: open.

Options:

1. nonunital Jordan algebras;
2. augmented unital Jordan algebras;
3. relative Jordan algebras;
4. dg Jordan algebras over the Jordan operad.

Decision needed before the cotangent-complex definition is treated as stable.

### D-002: Resolution Framework

Status: open.

Options:

1. simplicial Jordan algebras;
2. dg Jordan algebras;
3. both with comparison.

Decision needed before defining `L^{\mathrm{Jord}}_{B/A}` as more than a
candidate.

### D-003: Computation Backend

Status: open.

Options:

1. pure Python;
2. SageMath;
3. hybrid Python plus Sage;
4. CAS-specific routes for special experiments.

Decision needed after the first exact prototypes for `J^2`, derivations, and
square-zero extensions.

### D-004: Coefficient Category Notation

Status: open.

Options:

1. `J`-Mod;
2. `J`-Bimod;
3. `\operatorname{Beck}(J)`;
4. another notation.

Decision needed after Milestone 2.

### D-005: Claim Numbering

Status: active convention.

Existing claim IDs should not be silently repurposed. Since `CLAIM-0005` is
already the transitivity triangle, any missing cotangent-complex, base-change,
or low-degree claim should use the next available ID.

## 16. Risk Register

### Risk 1: Abstract Quillen Theory Is Too Formal To Be Useful

Mitigation: focus on Beck modules, universal differentials, low-degree groups,
and exact examples.

### Risk 2: The Jordan Operad Is Cubic And Explicit Resolutions Are Hard

Mitigation: do not attempt a full minimal operadic resolution at the beginning.
Work first with low-degree consequences and small examples.

### Risk 3: Unital Algebras Make `J/J^2` Vanish

Mitigation: separate nonunital, augmented, and relative theories from the
start.

### Risk 4: Beck Modules May Not Match Classical Jordan Modules Exactly

Mitigation: treat this as a central research question, not as an assumption.

### Risk 5: TKK Homology May Not Match Intrinsic Quillen Homology

Mitigation: a counterexample or non-comparison result is still valuable.

### Risk 6: Computations May Become Misleading

Mitigation: use exact arithmetic over `\mathbb Q`. Record all assumptions and
verify identities exactly.

### Risk 7: OCR And Literature Notes May Corrupt Formulas

Mitigation: treat OCR as search/index material. Verify claim-facing formulas,
arrows, theorem statements, and references against the PDF rendering or another
trusted source before writing them into claim files or paper text.

## 17. Weekly Workflow

Each week should produce at least one of the following:

1. one updated claim file;
2. one checked proof gap;
3. one exact computation;
4. one literature note;
5. one paper paragraph.

Recommended weekly loop:

```text
Read -> formulate claim -> test example -> write proof draft -> update paper.
```

When a result is still exploratory, keep the labels honest:

```text
not run yet
draft
conjectural
proof-draft
```

## 18. Immediate Next Tasks

1. Rerun and manually review `experiments/005-quillen-derived-indecomposables/`
   and `experiments/006-presentation-invariance-j3/`. Treat their experiment
   numbers as workspace labels, not as logical stage ordering.
2. Record whether the `005` toy benchmark should remain only experimental
   evidence or be promoted into a draft claim after manual proof review.
3. Keep `006` explicitly limited: Presentation A is computed by the
   one-generator toy model, while Presentation B remains a planned
   cofibrant-replacement stress test.
4. Review `theory/00-conventions.md` against `theory/latex_notation.md` and
   freeze the default working category for the next phase.
5. Expand `theory/03-abelianization.md` around `Q(J) = J/J^2`, the adjunction,
   the unital degeneration, and the augmented case.
6. Move `CLAIM-0001` and `CLAIM-0002` from draft toward `proof-draft` or
   `checked`, but only after manual proof review.
7. Expand `theory/04-beck-modules.md` and
   `experiments/003-beck-module-identities/` with explicit square-zero
   identity calculations.
8. Treat pure Python exact arithmetic as the current path for `J^2` and the
   toy derived-indecomposables checks; revisit Sage only if later examples
   exceed the pure-Python scaffold.
9. Add a cotangent-complex claim file with the next available claim ID if the
   definition in `theory/06-cotangent-complex.md` becomes mathematically
   substantive.
10. Add base-change, free-vanishing, and low-degree interpretation claims using
   next available IDs.
11. Synchronize the paper skeleton with stable claim statuses before drafting
   theorem-like prose.
12. Keep `PLAN.md` as the roadmap, not as proof evidence.
