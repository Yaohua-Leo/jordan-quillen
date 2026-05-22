# AGENTS.md

This repository studies Jordan algebra homology and cohomology through the
Quillen/Andre-Quillen lens. Work should preserve the distinction between
proved claims, plausible conjectures, and computational experiments.

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

## Verification

- For Python changes, run `python -m pytest`.
- For style changes, run `python -m ruff check .` when ruff is available.
- For claim-file changes, run `python scripts/check_claims.py`.
- Lean and Sage files are not part of the default verification path until their
  toolchains are explicitly selected.

## Mathematical Posture

The default roadmap is:

1. Identify abelian objects and Beck modules for Jordan algebras.
2. Define derivations and universal Jordan differentials.
3. Build the Jordan cotangent complex from a cofibrant or simplicial
   resolution.
4. Extract low-degree homology and cohomology.
5. Compare with Glassman-style cohomology and TKK/Lie-theoretic invariants.
