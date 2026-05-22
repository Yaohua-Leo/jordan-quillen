# jordan-quillen

Research scaffold for Jordan algebra homology and cohomology in the
Quillen/Andre-Quillen style.

The working hypothesis is that the useful object is not a direct analogue of
the Chevalley-Eilenberg complex, but a Jordan cotangent complex obtained from
derived abelianization. The first milestone is to make the definitions precise
enough that low-degree examples and comparison results can be checked.

## Current Scope

- Build a literature-backed map from Quillen cohomology of commutative rings to
  Jordan algebras.
- Isolate the correct abelian objects, Beck modules, derivations, and
  universal differentials for Jordan algebras.
- Keep computation provisional until the best engine is clear.

## Repository Map

- `literature/` stores notes, bibliographic metadata, and local-only PDF
  placement instructions.
- `theory/` stores the mathematical development, including explicit claim
  records.
- `src/jordan_qh/` stores a lightweight Python scaffold for small examples.
- `tests/` keeps smoke tests for the scaffold and identity helpers.
- `experiments/` records planned computations without fabricating results.
- `paper/` and `formal/` are placeholders for later writeup and formalization.

## Local PDFs

PDFs belong in `literature/papers-local/` and are ignored by git. Keep notes and
citations in git; keep copyrighted or locally obtained PDFs out of git.

## Quick Checks

```powershell
python -m pytest
python -m ruff check .
python scripts/check_claims.py
```

`ruff` and `pre-commit` are development tools. If they are unavailable in the
local Python environment, install the development extras after deciding on the
compute stack.
