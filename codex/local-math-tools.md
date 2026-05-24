# Local Math Tools

This file is a local Windows snapshot for agent-driven mathematical
computation in this repository. Re-check paths and versions before relying on
them, especially after tool upgrades or PATH changes.

Last checked: 2026-05-24, Asia/Shanghai.

Do not record licenses, API keys, account details, or credentials here.

## Verified Tools

| Tool | Status | Executable or route | Verified command | Intended use in this repo | Caveats |
| --- | --- | --- | --- | --- | --- |
| Python | `verified` | `C:\Python314\python.exe` | `python --version` -> `Python 3.14.3` | Default runtime for `src/jordan_qh/`, scripts, and tests. | Project requires `>=3.11`; Python 3.14 may expose compatibility issues in dependencies. |
| pytest | `verified` | `C:\Users\Leo\AppData\Roaming\Python\Python314\Scripts\pytest.exe` | `python -m pytest --version` -> `pytest 9.0.2` | Default Python regression tests. | Prefer `python -m pytest` so the interpreter is explicit. |
| uv | `verified` | `D:\kimi-code-cli\uv\uv.exe` | `uv --version` -> `uv 0.10.7` | Optional Python environment and package management. | Do not use it to mutate environments unless the task asks for setup work. |
| ruff | `verified` | `C:\Users\Leo\AppData\Roaming\Python\Python314\Scripts\ruff.exe` | `python -m ruff --version` -> `ruff 0.15.14` | Style checks referenced by README, AGENTS, and `pyproject.toml`. | Installed in the Python 3.14 user environment with `pip --user`. |
| pre-commit | `verified` | `C:\Users\Leo\AppData\Roaming\Python\Python314\Scripts\pre-commit.exe` | `python -m pre_commit --version` -> `pre-commit 4.6.0` | Optional local hook runner matching `pyproject.toml` dev dependencies. | Installed in the Python 3.14 user environment with `pip --user`. |
| Python scientific stack | `verified` | Current Python environment | `python -c "import sympy, numpy, scipy, networkx"` | Exact/symbolic and small linear-algebra experiments. | Use exact arithmetic whenever possible. |
| IPython / Jupyter | `verified` | `C:\Users\Leo\AppData\Roaming\Python\Python314\Scripts\ipython.exe`; `...\jupyter.exe` | `python -m IPython --version` -> `9.13.0`; `python -m jupyter --version` -> Jupyter core packages present | Exploratory notebooks under `notebooks/`. | Reusable code must still move to `src/jordan_qh/`; `qtconsole` is not installed. |
| MATLAB | `verified` | `D:\matlab\bin\matlab.exe` | `matlab -batch "disp(version)"` -> `26.1.0.3203278 (R2026a)` | Numerical checks, visualization, and MATLAB-specific experiments. | Startup is heavy; prefer batch mode, not GUI. |
| Maple CLI | `verified` | `D:\maple\bin.X86_64_WINDOWS\cmaple.exe` | `"kernelopts(version); quit;" \| & D:\maple\bin.X86_64_WINDOWS\cmaple.exe -q` -> `Maple 2026.0` | Symbolic algebra and exact computations. | Maple-MATLAB integration is not assumed; Maple 2026 did not automatically detect MATLAB R2026a in prior checks. |
| WolframScript / Wolfram Language | `verified` | `C:\Program Files\Wolfram Research\WolframScript\wolframscript.exe` | `wolframscript -code '$Version'` -> `14.3.0 for Microsoft Windows (64-bit)` | Symbolic checks and independent CAS comparison. | Use script mode for reproducible commands. |
| SageMath via WSL | `verified` | `C:\Users\Leo\AppData\Local\Microsoft\WindowsApps\sage.cmd` -> `wsl.exe -d Ubuntu -- sage` | `wsl.exe -d Ubuntu -- bash -lc 'sage -c "print(2+2)"'` -> `4` | Exact algebra experiments, small examples, and existing `*.sage` files. | The Windows wrapper is quote-sensitive; route through `wsl.exe ... bash -lc` for reliable one-liners. |
| GAP via Sage interface | `verified` | `wsl.exe -d Ubuntu -- sage` | `sage -c "from sage.interfaces.gap import gap; print(gap(\"2+2\"))"` -> `4` | Group, representation, and small algebra examples through Sage. | This is not a standalone `gap` CLI on PATH. |
| Singular via Sage interface | `verified` | `wsl.exe -d Ubuntu -- sage` | `sage -c "from sage.interfaces.singular import singular; print(singular(\"2+2\"))"` -> `4` | Polynomial and Groebner-basis computations through Sage. | This is not a standalone `Singular` CLI on PATH. |
| Standalone GAP CLI via WSL | `verified` | `wsl.exe -d Ubuntu -- /home/leo/miniforge3/envs/math-tools/bin/gap` | `printf "2+2;\nquit;\n" \| .../gap -q` -> `4`; `GAPInfo.Version` -> `4.15.1` | Direct GAP scripts when the Sage interface is not enough. | Installed in the WSL conda environment `math-tools`; not on the default Windows or WSL PATH. |
| Standalone Singular CLI via WSL | `verified` | `wsl.exe -d Ubuntu -- /home/leo/miniforge3/envs/math-tools/bin/Singular` | `Singular --version` -> `Singular ... version 4.4.1`; `2+2` -> `4` | Direct Singular scripts and Groebner-basis computations. | Installed in the WSL conda environment `math-tools`; not on the default Windows or WSL PATH. |
| Maxima | `verified` | `C:\maxima-5.49.0\bin\maxima.bat` | `& C:\maxima-5.49.0\bin\maxima.bat --very-quiet --batch-string='2+2;'` -> `4` | General symbolic CAS backup and independent checks. | Installed by `winget`; not on current shell PATH, so use the absolute path. |
| Julia | `verified` | `C:\Users\Leo\AppData\Local\Microsoft\WindowsApps\julia.exe` via Juliaup | `julia -e 'println(VERSION); println(2+2)'` -> `1.12.6`, `4` | Julia-native exact and numerical experiments. | Native Windows Julia works, but native Windows OSCAR does not load because Polymake reports Windows unsupported. |
| OSCAR via WSL Julia | `verified` | `wsl.exe -d Ubuntu -- $HOME/.juliaup/bin/julia` | `using Oscar; println(Oscar.VERSION); println(2+2)` -> `1.12.6`, `4` | Commutative algebra, algebraic geometry, and exact algebra computation. | Installed in WSL user Julia depot; visualization warns that `/usr/bin/wslview` is missing, but algebraic computation loads. |
| Macaulay2 via WSL wrapper | `verified` | `wsl.exe -d Ubuntu -- /home/leo/local/bin/M2-codex`; WSL login shell command `M2-codex` | `M2-codex --version` -> `1.22`; `2+2` -> `4` | Groebner bases, commutative algebra, and algebraic geometry. | User-level install from Ubuntu 24.04 packages extracted under `/home/leo/local/macaulay2-1.22-apt/root`; wrapper uses user-level `proot` to bind the extracted Singular data path. `/home/leo/.profile` adds `/home/leo/local/bin` for WSL login shells. Upstream stable is newer than this Ubuntu package. |
| R / Rscript | `verified` | `C:\Program Files\R\R-4.6.0\bin\Rscript.exe` | `Rscript -e "cat(R.version.string); cat(2+2)"` -> `R version 4.6.0`, `4` | Statistics or plotting if later needed. | Not on current shell PATH; use the absolute path until PATH is refreshed or updated. |
| Octave | `verified` | `C:\Users\Leo\AppData\Local\Programs\GNU Octave\Octave-11.1.0\mingw64\bin\octave-cli.exe` | `octave-cli --quiet --eval "disp(version); disp(2+2);"` -> `11.1.0`, `4` | MATLAB-like open-source numerical checks. | Installed locally under the user profile; use CLI mode for reproducible commands. |
| Lean | `verified` | `C:\Users\Leo\.elan\bin\lean.exe` | `lean --version` -> `Lean 4.21.0` | Future formalization under `formal/lean/`. | Formal files are not in the default verification path unless selected. |
| Lake | `verified` | `C:\Users\Leo\.elan\bin\lake.exe` | `lake --version` -> `Lake version 5.0.0-6741444` | Lean project builds under `formal/lean/`. | `lake` is available; do not list it as missing. |
| Rocq / Coq Platform | `verified` | `C:\Rocq-Platform~9.0~2025.08\bin\rocq.exe` | `rocq --version` -> `The Rocq Prover, version 9.0.1`; `rocq compile <temp>.v` checked `Check nat.` | Alternative formalization track when explicitly selected. | Installed by `winget`; prefer the new `rocq` command. Legacy `coqc`/`coqtop` exist in the same `bin` directory but did not emit useful version output in the checked shell. |
| Isabelle via WSL | `verified` | `wsl.exe -d Ubuntu -- /home/leo/local/Isabelle2025-2/bin/isabelle` | `isabelle version` -> `Isabelle2025-2` | Alternative formalization track when explicitly selected. | Installed in WSL user space from the official Linux archive; not on default PATH. |
| Agda via WSL | `verified` | `wsl.exe -d Ubuntu -- /home/leo/local/agda-2.8.0/agda` | `agda --version` -> `Agda version 2.8.0`; `Data.Nat` import from `standard-library-2.3` type-checked; `agda --compile` smoke test printed `agda-compile-ok` | Alternative formalization track and small Agda compile experiments when explicitly selected. | Standard library v2.3 is installed at `/home/leo/local/agda-stdlib-2.3` and exposed by `~/.config/agda/libraries` plus `~/.config/agda/defaults`. GHC backend uses GHCup under `/home/leo/.ghcup`; WSL `.profile` sets `LIBRARY_PATH` to the user-level conda `math-tools` GMP library so GHC can link without modifying system `/usr`. Editor integration is not configured. |
| GHC / Cabal via GHCup in WSL | `verified` | WSL login shell commands `ghc`, `cabal`; absolute paths `/home/leo/.ghcup/bin/ghc`, `/home/leo/.ghcup/bin/cabal` | `ghc --version` -> `The Glorious Glasgow Haskell Compilation System, version 9.6.7`; `cabal --version` -> `cabal-install version 3.14.2.0` | Agda GHC backend support and occasional Haskell-side compile checks. | Installed in WSL user space by GHCup. Do not use it to create Haskell project dependencies in this repo unless a task explicitly asks. |
| Aristotle CLI | `verified` | `D:\aristotle\.venv\Scripts\aristotle.exe` | `D:\aristotle\.venv\Scripts\aristotle.exe --version` -> `aristotlelib 1.0.1` | External Lean theorem-proving assistant when explicitly selected. | Requires authentication via `ARISTOTLE_API_KEY` or CLI option; never store the key in this repo. |

## Quick Usage Recipes

Run these examples from PowerShell unless a command explicitly starts with
`wsl.exe`. For WSL tools that need repository files, use the WSL path
`/mnt/d/learning/(co)homology_of_Jordan/...` and quote it because the repository
path contains parentheses.

### Leo Manual Use

Use these for interactive shells, quick checks, and hand-driven experiments.

```powershell
# Repository checks
python -m pytest
python -m ruff check .
python scripts/check_claims.py

# Python and notebooks
python
python -m IPython
python -m jupyter lab

# Windows-native CAS / numerical tools
& 'D:\matlab\bin\matlab.exe'
& 'D:\matlab\bin\matlab.exe' -batch "disp(2+2)"
'2+2; quit;' | & 'D:\maple\bin.X86_64_WINDOWS\cmaple.exe' -q
& 'C:\Program Files\Wolfram Research\WolframScript\wolframscript.exe' -code '2+2'
& 'C:\maxima-5.49.0\bin\maxima.bat' --very-quiet --batch-string='2+2;'
julia
& 'C:\Program Files\R\R-4.6.0\bin\Rscript.exe' -e "print(2+2)"
& 'C:\Users\Leo\AppData\Local\Programs\GNU Octave\Octave-11.1.0\mingw64\bin\octave-cli.exe' --quiet

# WSL algebra tools
wsl.exe -d Ubuntu -- sage
wsl.exe -d Ubuntu -- /home/leo/miniforge3/envs/math-tools/bin/gap -q
wsl.exe -d Ubuntu -- /home/leo/miniforge3/envs/math-tools/bin/Singular
wsl.exe -d Ubuntu -- /home/leo/local/bin/M2-codex
wsl.exe -d Ubuntu -- bash -lc 'M2-codex'
wsl.exe -d Ubuntu -- /home/leo/.juliaup/bin/julia

# Formal tools
& 'C:\Users\Leo\.elan\bin\lean.exe' --version
& 'C:\Users\Leo\.elan\bin\lake.exe' --version
& 'C:\Rocq-Platform~9.0~2025.08\bin\rocq.exe' --version
wsl.exe -d Ubuntu -- /home/leo/local/Isabelle2025-2/bin/isabelle jedit
wsl.exe -d Ubuntu -- /home/leo/local/Isabelle2025-2/bin/isabelle vscode
wsl.exe -d Ubuntu -- /home/leo/local/agda-2.8.0/agda --version
wsl.exe -d Ubuntu -- bash -lc 'ghc --version; cabal --version | head -n 1'
wsl.exe -d Ubuntu -- bash -lc 'cd "/mnt/d/learning/(co)homology_of_Jordan/path/to/agda-dir" && /home/leo/local/agda-2.8.0/agda File.agda'
wsl.exe -d Ubuntu -- bash -lc 'cd "/mnt/d/learning/(co)homology_of_Jordan/path/to/agda-dir" && /home/leo/local/agda-2.8.0/agda --compile Main.agda'

# Aristotle: requires ARISTOTLE_API_KEY in the user environment or --api-key
& 'D:\aristotle\.venv\Scripts\aristotle.exe' --help
```

### Codex Non-Interactive Use

Codex should prefer explicit absolute paths, one-shot commands, and batch modes.
Use WSL login-shell shortcuts only when testing or using the user-facing
shortcuts documented here. Do not rely on credentials stored in this repository.

```powershell
# Repository verification
python -m pytest
python -m ruff check .
python -m ruff format --check .
python scripts/check_claims.py

# Python exact/symbolic smoke check
python -c "import sympy as sp; print(sp.factor(sp.Symbol('x')**2 - 1))"

# Sage, GAP, Singular, and Macaulay2 through WSL
wsl.exe -d Ubuntu -- bash -lc 'sage -c "print(2+2)"'
wsl.exe -d Ubuntu -- bash -lc 'printf "2+2;\nquit;\n" | /home/leo/miniforge3/envs/math-tools/bin/gap -q'
wsl.exe -d Ubuntu -- bash -lc 'printf "2+2;\nquit;\n" | /home/leo/miniforge3/envs/math-tools/bin/Singular -q'
wsl.exe -d Ubuntu -- bash -lc 'printf "2+2\nexit 0\n" | M2-codex --no-readline --print-width 80 --stop --no-debug'

# Windows-native CAS / numerical batch checks
& 'D:\matlab\bin\matlab.exe' -batch "disp(2+2)"
'2+2; quit;' | & 'D:\maple\bin.X86_64_WINDOWS\cmaple.exe' -q
& 'C:\Program Files\Wolfram Research\WolframScript\wolframscript.exe' -code '2+2'
& 'C:\maxima-5.49.0\bin\maxima.bat' --very-quiet --batch-string='2+2;'
julia -e 'println(2+2)'
wsl.exe -d Ubuntu -- bash -lc '$HOME/.juliaup/bin/julia -e "using Oscar; println(2+2)"'
& 'C:\Program Files\R\R-4.6.0\bin\Rscript.exe' -e "print(2+2)"
& 'C:\Users\Leo\AppData\Local\Programs\GNU Octave\Octave-11.1.0\mingw64\bin\octave-cli.exe' --quiet --eval "disp(2+2);"

# Formal tool checks
& 'C:\Users\Leo\.elan\bin\lean.exe' --version
& 'C:\Users\Leo\.elan\bin\lake.exe' --version
& 'C:\Rocq-Platform~9.0~2025.08\bin\rocq.exe' --version
wsl.exe -d Ubuntu -- /home/leo/local/Isabelle2025-2/bin/isabelle version
wsl.exe -d Ubuntu -- /home/leo/local/agda-2.8.0/agda --version
wsl.exe -d Ubuntu -- bash -lc 'ghc --version; cabal --version | head -n 1'

# Formal project files, once such files exist
& 'C:\Users\Leo\.elan\bin\lean.exe' path\to\File.lean
& 'C:\Rocq-Platform~9.0~2025.08\bin\rocq.exe' compile path\to\File.v
wsl.exe -d Ubuntu -- bash -lc 'cd "/mnt/d/learning/(co)homology_of_Jordan/path/to/agda-dir" && /home/leo/local/agda-2.8.0/agda File.agda'
wsl.exe -d Ubuntu -- bash -lc 'cd "/mnt/d/learning/(co)homology_of_Jordan/path/to/agda-dir" && /home/leo/local/agda-2.8.0/agda --compile Main.agda'
wsl.exe -d Ubuntu -- bash -lc '/home/leo/local/Isabelle2025-2/bin/isabelle build -d "/mnt/d/learning/(co)homology_of_Jordan/path/to/session" -l SessionName'
```

Setup notes:

- Use `M2-codex` for Macaulay2. Do not call the extracted `M2` directly; the
  wrapper supplies the user-level library paths and temporary Singular data
  bind needed by this non-sudo install.
- Agda is ready for CLI type-checking with `standard-library-2.3`, and the GHC
  backend is usable from WSL login shells. The standard library is exposed by
  `~/.config/agda/libraries` and `~/.config/agda/defaults`. The `.profile`
  `LIBRARY_PATH` block is intentional: it points GHC at the existing user-level
  conda `libgmp.so` symlink without adding Debian `libgmp-dev` under system
  `/usr`.
- Agda editor integration is still optional follow-up setup. Use CLI checks
  until a concrete Agda project layout or editor workflow is needed.
- Isabelle is ready for CLI commands and can start `jedit` or `vscode`.
  Repository-specific Isabelle sessions still need explicit `ROOT`/session
  files before `isabelle build` can be used for project proofs.
- Aristotle commands must not echo, store, or commit API keys. Use a user-level
  `ARISTOTLE_API_KEY` environment variable or a one-off `--api-key` argument
  only when needed.
- Magma has no local account/license setup here. Use the web calculator only
  for small, non-private checks when Magma is useful and reproducibility is not
  the main requirement.

## Still Not Configured

| Tool | Status | Evidence | Possible repo use | Caveats |
| --- | --- | --- | --- | --- |
| Magma local install | `not-configured` | `magma` was not found on PATH or in checked common routes; no local account, license, or passfile was configured. Web fallback: <https://magma.maths.usyd.edu.au/calc/> currently states 120 seconds, 50000-byte input, and Magma V2.29-6. | Occasional small algebra, number theory, and algebraic geometry checks. | Web-only fallback is suitable only for small, non-private checks. It is not a local configured tool and should not be used for large or reproducibility-critical jobs. |

## Suggested Setup Priority

1. For normal repository checks, use `python -m pytest`, `python -m ruff check .`,
   and `python scripts/check_claims.py`.
2. For exact algebra experiments, prefer Python/SymPy, Sage via WSL, Maple,
   WolframScript, Maxima, or OSCAR via WSL depending on the computation.
3. For Julia algebraic geometry work, use the WSL Julia/OSCAR route. Do not
   rely on native Windows OSCAR until upstream Polymake support changes.
4. Use standalone GAP, standalone Singular, Macaulay2, Isabelle, or Agda only
   when an experiment or formalization task explicitly needs that route.
5. Use the Magma web calculator only for small, non-private checks. Add local
   Magma only with a valid account/license and a concrete computation need.

Lower-priority, need-driven options:

- Macaulay2: available through the WSL wrapper; useful if Groebner-basis or
  commutative-algebra computations become central and OSCAR/Sage are
  insufficient.
- Standalone GAP or Singular: available through the WSL `math-tools` conda
  environment; useful if direct upstream scripts become part of the project.
- Isabelle or Agda: command-line basics are available. Agda also has
  `standard-library-2.3` and GHC backend support; add editor integration and
  formalization-specific build files only when needed.
- Magma: strong but proprietary. The web calculator is available as a temporary
  small-check fallback; install locally only with a valid license and a concrete
  experiment.

## External Setup References

- GAP Windows installation: <https://www.gap-system.org/install/windows/>
- OSCAR Windows installation: <https://www.oscar-system.org/install/win/>
- Macaulay2 Windows installation: <https://macaulay2.com/Downloads/Microsoft-Windows/index.html>
- Macaulay2 GNU/Linux installation: <https://macaulay2.com/Downloads/GNU-Linux/>
- Isabelle installation: <https://isabelle.in.tum.de/installation.html>
- Agda installation: <https://agda.readthedocs.io/en/stable/getting-started/installation.html>
- Agda standard library v2.3: <https://github.com/agda/agda-stdlib/releases/tag/v2.3>
- GHCup: <https://www.haskell.org/ghcup/>
- Julia installation: <https://julialang.org/downloads/>
- Magma calculator: <https://magma.maths.usyd.edu.au/calc/>
- Magma home page: <https://magma-maths.org/>
- Rocq / Coq Platform: <https://rocq-prover.org/>
