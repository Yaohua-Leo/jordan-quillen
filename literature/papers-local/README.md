# Local Papers

Store original PDF or scan files here for local reading only.

PDF-like source files in this directory are intentionally ignored by git. Keep
copyrighted or locally obtained source PDFs out of repository history. Write
durable summaries in `literature/notes/` and cite stable metadata in
`literature/bib/references.bib`.

## Files In This Directory

- `paper_menu.md` is the acquisition checklist used to collect the current
  source files. The current numbered local set covers menu items `01` through
  `57`.
- `paper_index.md` is the current local file index, with topic and extraction
  tags for Codex-facing routing.
- `*.pdf` files are raw local sources. They are not committed.

## Current Audit Notes

- All numbered menu items currently have at least one local PDF file.
- All numbered PDFs parse with `pdfinfo`; sampled title-page text was checked
  against the represented menu item.
- Item `51` is indexed and cited under the PDF title `Operadic Cobar
  Constructions, Cylinder Objects and Homotopy Morphisms of Algebras over
  Operads`; the acquisition checklist has been corrected to match this title.
- Item `57` is locally named with both authors:
  `57_springer_veldkamp_octonions_jordan_algebras_exceptional_groups.pdf`.
- `on_homology_of_jordan_algebras(1).pdf` is an extra local source outside the
  numbered menu and should not be cited until its provenance is checked.

## Extraction Tags

- `text-layer`: usable text can be extracted for search and rough reading.
- `text-layer-frontmatter-sparse`: front matter extracts poorly, but later
  sampled pages have usable text.
- `scan-only`: no useful text layer was detected in sampled pages; use OCR
  only for task-relevant pages.

Text extraction and OCR are not proof sources. Any definition, theorem,
formula, or claim-facing quote must be checked against the rendered PDF before
it is used in `theory/claims/`, `paper/`, or formal notes.

## Codex Workflow

1. Use `paper_index.md` to locate the file and extraction tag.
2. Prefer `literature/notes/` for durable Codex-facing reading material.
3. Use raw PDFs only for verification against page images.
4. Put temporary OCR or full-text extraction output in an ignored local
   scratch location such as `tmp/`; do not commit raw OCR dumps.
5. If an OCR result becomes important, distill it into a curated note with page
   references and uncertainty markers.
