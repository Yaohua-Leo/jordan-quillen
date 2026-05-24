# AGENTS.md

This repository develops the intrinsic Quillen homology and cohomology theory
of Jordan algebras. Work here should preserve the distinction between proved
claims, plausible conjectures, proof drafts, and computational experiments.

## Project Identity

The intended mathematical setting is usually a field `k` of characteristic
`0`, unless a file states different hypotheses.

The central objects are:

- Jordan algebras
- square-zero extensions
- Beck modules
- Jordan derivations
- universal Jordan differentials
- Jordan cotangent complexes
- low-degree Quillen cohomology
- comparison with Glassman cohomology
- comparison with TKK/Lie-theoretic constructions

## Local Rules

- Do not modify global Codex, OMX, skill governance, plugin, or routing
  configuration from this repository.
- Treat PDFs under `literature/papers-local/` as local source material only;
  they are intentionally ignored by git.
- Prefer small, reviewable changes. A theory edit that changes a definition
  should update the relevant claim file or mark the claim as stale.
- Do not invent literature conclusions. Use `status: unread`, `status:
  partial`, or `status: conjectural` when a source has not been checked.
- Keep experiments honest. A results file may say `not run yet`; it must not
  contain fabricated numerical output.

## Rules For Mathematical Work

1. Do not invent references.
2. Every mathematical claim must be recorded in `theory/claims/`.
3. Every theorem must have a precise statement, assumptions, dependencies, a
   proof sketch, and known gaps.
4. Mark uncertain claims as `draft`, `conjectural`, or `proof-draft`; do not
   mark them as checked or proved until evidence has been supplied.
5. Distinguish carefully between nonunital Jordan algebras, unital Jordan
   algebras, augmented Jordan algebras, Jordan pairs/triples, and TKK Lie
   algebras.
6. Do not identify intrinsic Jordan Quillen homology with TKK Lie homology
   unless a proof or counterexample is supplied.

## Rules For Computational Work

1. Use exact arithmetic whenever possible.
2. Prefer rational examples over floating-point examples.
3. Core code belongs in `src/jordan_qh/`.
4. Notebooks are exploratory only; reusable code must be moved into `src/`.
5. Every implemented mathematical function needs a pytest test.
6. Every experiment must have an `experiment.md` describing the question,
   method, and result.
7. Do not optimize before correctness is established.
8. Before non-Python mathematical computation, check
   `codex/local-math-tools.md` for the current local tool snapshot.
9. Re-verify tool paths before relying on them; the snapshot is not a permanent
   cross-machine guarantee.
10. Do not store licenses, API keys, account details, or other credentials in
    this repository.

## Rules For Writing

1. Use English filenames.
2. Mathematical notes may be written in English or Chinese.
3. Paper text should be in English.
4. Use the notation table in `theory/latex_notation.md`.

## Preferred Workflow

For any task:

1. Read the relevant claim file.
2. State what will be changed.
3. Make the smallest useful change.
4. Run tests or explain why no test applies.
5. Update the claim status or proof gap list when mathematical content
   changes.
6. Never silently delete open problems.

## Verification

- For Python changes, run `python -m pytest`.
- For style changes, run `python -m ruff check .` when ruff is available.
- For claim-file changes, run `python scripts/check_claims.py`.
- Lean and Sage files are not part of the default verification path until their
  toolchains are explicitly selected.
