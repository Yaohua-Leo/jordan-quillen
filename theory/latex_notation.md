# LaTeX Notation

This file is the repository's canonical human-readable notation table for the
Jordan Quillen homology and cohomology project. `paper/macros.tex` may provide
LaTeX shortcuts, but mathematical writing should follow the conventions here.

| Object | Standard notation | Preferred LaTeX source | Meaning and scope | Status |
| --- | --- | --- | --- | --- |
| Base field | `k` | `k` | The ground field; characteristic `0` unless a file states different hypotheses. | fixed |
| Jordan algebra | `J` | `J` | A Jordan algebra over `k`, usually nonunital unless context says otherwise. | fixed |
| Module | `M` | `M` | A Jordan module or Beck module, with the precise convention determined by the local context. | fixed name, convention-sensitive |
| Jordan product | `xy` or `x * y` | `xy` or `x * y` | The commutative Jordan product. Use juxtaposition in prose and displayed mathematics when unambiguous; use `x * y` in code-oriented text. | fixed |
| Product span | `J^2` | `J^2` | The linear span of all products `xy` in `J`. | fixed |
| Indecomposables | `Q(J) = J/J^2` | `Q(J) = J/J^2` | The expected abelianization or indecomposables functor in the absolute nonunital setting. | proof-draft |
| Jordan cotangent complex | `L^{\mathrm{Jord}}_{B/A}` | `L^{\mathrm{Jord}}_{B/A}` | The Jordan cotangent complex of a morphism `A -> B`. | provisional |
| Quillen homology | `D_n^{\mathrm{Jord}}(B/A,M)` | `D_n^{\mathrm{Jord}}(B/A,M)` | The homology groups obtained from the Jordan cotangent complex with coefficients in `M`. | provisional |
| Quillen cohomology | `D^n_{\mathrm{Jord}}(B/A,M)` | `D^n_{\mathrm{Jord}}(B/A,M)` | The cohomology groups represented by maps from the Jordan cotangent complex to `M`. | provisional |
| Universal Jordan differentials | `\Omega_{B/A}` | `\Omega_{B/A}` | Universal Jordan differentials for `A -> B`; exact construction depends on the final module convention. | provisional |
