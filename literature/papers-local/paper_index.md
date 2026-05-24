# Local Paper Index

Generated for the local files in this directory on 2026-05-24.

This index records file-management and extraction metadata only. It is not a
substitute for `literature/bib/references.bib`, and it does not certify any
mathematical claim.

## Conformance Check

- Menu coverage: items `01` through `57` from `paper_menu.md` are represented
  by local PDF files. Items with multiple source texts are split into suffixes
  such as `06a`, `06b`, `26a`-`26f`, and `29a`-`29d`.
- Storage rule: all original PDF files are under `literature/papers-local/`.
- Git rule: `.gitignore` ignores `literature/papers-local/*.pdf`, so the raw
  PDF files stay out of git history.
- Metadata rule: `paper_menu.md`, this index, and `README.md` are lightweight
  Markdown metadata files and are not covered by the PDF ignore rule.
- Caveat: some filenames contain accents, apostrophes, or spaces because they
  mirror downloaded source names. Keep future new filenames English and stable;
  do not rename existing raw files unless references are updated together.
- Extra local file: `on_homology_of_jordan_algebras(1).pdf` is not part of
  `paper_menu.md`; treat it as `extra; provenance-check` and do not cite it as
  literature until its source is verified.
- Content check: all numbered PDFs parse with `pdfinfo`; sampled title-page
  text matches the represented menu item. The local file and BibTeX for item
  `51` use the PDF title `Operadic Cobar Constructions...`.

## Tag Legend

- `text-layer`: `pdftotext` extracts useful text from sampled pages. Good for
  search and rough reading; formulas and theorem statements still need PDF
  verification before claim or paper use.
- `text-layer-frontmatter-sparse`: front matter has little extractable text,
  but later sampled pages extract usable text.
- `scan-only`: sampled pages have no useful text layer. Use MinerU/OCR only
  for task-relevant pages, and verify formulas against the rendered PDF.
- Topic tags are routing hints only, not claims about the paper's contents.

## Indexed Files

| Menu | Local file | Topic tags | Extraction tag | Codex use |
| --- | --- | --- | --- | --- |
| 01 | `01_quillen_homotopical_algebra.pdf` | homotopical-algebra; model-categories; Quillen | text-layer | search-ok; verify-math-before-claim |
| 02 | `02_On_the_cohomology_of_commutative_rings.pdf` | Andre-Quillen; commutative-rings; Quillen | scan-only | OCR-needed; verify-page-images |
| 03 | `03_andre_Méthode_simpliciale_en_algèbre_homologique_et_algèbre_commutative.pdf` | Andre-Quillen; simplicial-methods; commutative-algebra | text-layer-frontmatter-sparse | search-ok-after-frontmatter; verify-math-before-claim |
| 04 | `04_lichtenbaum_schlessinger_The_Cotangent_Complex_of_a_Morphism.pdf` | cotangent-complex; deformation; commutative-algebra | text-layer | search-ok; verify-math-before-claim |
| 05 | `05_Harrison_Commutative_algebras_and_cohomology.pdf` | Harrison-cohomology; commutative-algebras | text-layer | search-ok; verify-math-before-claim |
| 06a | `06a_Illusie_Complex_cotangent_et_déformations_I.pdf` | cotangent-complex; deformation; Illusie | text-layer | search-ok; verify-math-before-claim |
| 06b | `06b_Illusie_Complex_cotangent_et_déformations_II.pdf` | cotangent-complex; deformation; Illusie | text-layer | search-ok; verify-math-before-claim |
| 07 | `07_iyengar_andre_quillen_homology_commutative_algebras.pdf` | Andre-Quillen; commutative-algebras; survey | text-layer | search-ok; verify-math-before-claim |
| 08 | `08_beck_triples_algebras_cohomology.pdf` | Beck; triples; cotriple-cohomology | text-layer | search-ok; verify-math-before-claim |
| 09 | `09_barr_beck_cotriple_homology_tac_reprint.pdf` | Barr-Beck; cotriple-homology | text-layer | search-ok; verify-math-before-claim |
| 10 | `10_blanc_generalized_andre_quillen_cohomology.pdf` | generalized-AQ; homotopy-theory | text-layer | search-ok; verify-math-before-claim |
| 11 | `11_frankland_quillen_cohomology_adjunctions.pdf` | Quillen-cohomology; adjunctions | text-layer | search-ok; verify-math-before-claim |
| 12 | `12_loday_vallette_algebraic_operads_author_draft.pdf` | operads; Jordan-operad; algebraic-operads | text-layer | search-ok; verify-math-before-claim |
| 13 | `13_Stasheff_Operads_in_Algebra_Topology_and_Physics.pdf` | operads; reference | text-layer | search-ok; verify-math-before-claim |
| 14 | `14_ginzburg_kapranov_koszul_duality_operads.pdf` | operads; Koszul-duality | text-layer | search-ok; verify-math-before-claim |
| 15 | `15_hinich_homological_algebra_homotopy_algebras.pdf` | homotopy-algebras; operads; model-categories | text-layer | search-ok; verify-math-before-claim |
| 16 | `16_berger_moerdijk_derived_category_operad_algebra.pdf` | operadic-algebras; derived-categories | text-layer | search-ok; verify-math-before-claim |
| 17 | `17_pavlov_scholbach_admissibility_rectification_colored_operads.pdf` | operads; admissibility; rectification | text-layer | search-ok; verify-math-before-claim |
| 18 | `18_white_yau_smith_ideals_operadic_algebras.pdf` | operadic-algebras; model-categories | text-layer | search-ok; verify-math-before-claim |
| 19 | `19_milles_andre_quillen_cohomology_operad_algebras.pdf` | operadic-AQ; cohomology; operads | text-layer | search-ok; verify-math-before-claim |
| 20 | `20_harpaz_nuiten_prasma_tangent_categories_operads.pdf` | tangent-categories; operads; AQ | text-layer | search-ok; verify-math-before-claim |
| 21 | `21_dotsenko_khoroshkin_quillen_homology_operads_groebner_bases.pdf` | Quillen-homology; operads; Groebner-bases | text-layer | search-ok; verify-math-before-claim |
| 22 | `22_Jacobson_Structures_and_Representations_of_Jordan_Algebras.pdf` | Jordan-algebras; structure; representations | scan-only | OCR-needed; verify-page-images |
| 23 | `23_schafer_an_introduction_to_nonassociative_algebras.pdf` | nonassociative-algebras; Jordan-background | text-layer | search-ok; verify-math-before-claim |
| 24 | `24_mccrimmon_a_taste_of_jordan_algebra.pdf` | Jordan-algebras; background | text-layer-frontmatter-sparse | search-ok-after-frontmatter; verify-math-before-claim |
| 25 | `25_Loos_Jordan_pairs.pdf` | Jordan-pairs; Jordan-structure | text-layer | search-ok; verify-math-before-claim |
| 26a | `26a_Tits_Une_classe_d’algèbres_de_Lie_en_relation_avec_les_algèbres_de_Jordan.pdf` | TKK; Lie-algebras; Jordan-algebras | text-layer | search-ok; verify-math-before-claim |
| 26b | `26b_Kantor_Classification_of_irreducible_transitive_differential_groups.pdf` | TKK; Kantor; Lie-theoretic | text-layer | search-ok; verify-math-before-claim |
| 26c | `26c_Koecher_Imbedding_of_Jordan_algebras_into_Lie algebras_I.pdf` | TKK; Koecher; Lie-algebras | text-layer | search-ok; verify-math-before-claim |
| 26d | `26d_Koecher_Imbedding_of_Jordan_algebras_into_Lie algebras_II.pdf` | TKK; Koecher; Lie-algebras | text-layer | search-ok; verify-math-before-claim |
| 26e | `26e_Tits_Algèbres_alternatives_algèbres_de_Jordan_et_algèbres_de_Lie_exceptionnelles.pdf` | TKK; exceptional-Lie; Jordan-algebras | text-layer | search-ok; verify-math-before-claim |
| 26f | `26f_Kantor_Some_generalizations_of_Jordan_algebras.pdf` | TKK; Kantor; Jordan-generalizations | scan-only | OCR-needed; verify-page-images |
| 27a | `27a_caveny_smirnov_categories_jordan_structures_graded_lie_algebras.pdf` | functorial-TKK; Jordan-structures; graded-Lie | text-layer | search-ok; verify-math-before-claim |
| 27b | `27b_Allison_Benkart_Gao_free_alternative_functors.pdf` | Allison-Benkart-Gao functor; free alternative functors | text-layer | search-ok; verify-math-before-claim |
| 28 | `28_gerstenhaber_uniform_cohomology_theory_algebras.pdf` | deformation; cohomology; Gerstenhaber | text-layer | search-ok; verify-math-before-claim |
| 29a | `29a_Gerstenhaber_On_the_deformation_of_rings_and_algebras_I.pdf` | deformation; rings-and-algebras; Gerstenhaber | text-layer | search-ok; verify-math-before-claim |
| 29b | `29b_Gerstenhaber_On_the_deformation_of_rings_and_algebras_II.pdf` | deformation; rings-and-algebras; Gerstenhaber | text-layer | search-ok; verify-math-before-claim |
| 29c | `29c_Gerstenhaber_On_the_deformation_of_rings_and_algebras_III.pdf` | deformation; rings-and-algebras; Gerstenhaber | text-layer | search-ok; verify-math-before-claim |
| 29d | `29d_Gerstenhaber_On_the_deformation_of_rings_and_algebras_IV.pdf` | deformation; rings-and-algebras; Gerstenhaber | text-layer | search-ok; verify-math-before-claim |
| 30 | `30_glassman_cohomology_nonassociative_algebras.pdf` | Glassman; nonassociative-cohomology | text-layer | search-ok; verify-math-before-claim |
| 31 | `31_Glassman_Cohomology_of_Jordan_algebras.pdf` | Glassman; Jordan-cohomology | text-layer | search-ok; verify-math-before-claim |
| 32 | `32_Harris_Cohomology_of_Lie_triple_systems_and_Lie_algebras_with_involution.pdf` | Lie-triples; involution; comparison | text-layer | search-ok; verify-math-before-claim |
| 33 | `33_Jacobson_collected_papers_General_representation_theory_of_Jordan_algebras_from_page_140.pdf` | Jordan-representations; Jacobson | text-layer-frontmatter-sparse | search-ok-after-frontmatter; verify-math-before-claim |
| 34 | `34_Penico_The_Wedderburn_Principal_Theorem_for_Jordan_Algebras.pdf` | Jordan-algebras; Wedderburn-principal-theorem | text-layer | search-ok; verify-math-before-claim |
| 35 | `35_McCrimmon_Representations_of_quadratic_Jordan_algebras.pdf` | quadratic-Jordan; representations | text-layer | search-ok; verify-math-before-claim |
| 36 | `36_seibt_Cohomology_of_algebras_and_triple_systems.pdf` | cohomology; triple-systems | text-layer | search-ok; verify-math-before-claim |
| 37 | `37_chu_russo_cohomology_jordan_triples_lie_algebras.pdf` | Jordan-triples; Lie-algebras; cohomology | text-layer | search-ok; verify-math-before-claim |
| 38 | `38_coll_deformations_jordan_algebras_jordan_defect.pdf` | Jordan-deformation; Jordan-defect; preprint | text-layer | search-ok; verify-math-before-claim |
| 39 | `39_Gnedbaye_Jordan_Triples_and_Operads.pdf` | Jordan-triples; operads | text-layer | search-ok; verify-math-before-claim |
| 40 | `40_bagherzadeh_bremner_madariaga_jordan_trialgebras.pdf` | Jordan-trialgebras; post-Jordan | text-layer | search-ok; verify-math-before-claim |
| 41 | `41_kashuba_mathieu_free_jordan_algebras.pdf` | free-Jordan-algebras; Kashuba-Mathieu | text-layer | search-ok; verify-math-before-claim |
| 42 | `42_dotsenko_kashuba_three_graces_tkk_category.pdf` | TKK; Dotsenko-Kashuba; Jordan-category | text-layer | search-ok; verify-math-before-claim |
| 43 | `43_dotsenko_hentzel_kashuba_mathieu_conjecture.pdf` | free-Jordan-algebras; Kashuba-Mathieu-conjecture | text-layer | search-ok; verify-math-before-claim |
| 44 | `44_gorodski_kashuba_martin_moment_map_jordan_algebras.pdf` | Jordan-variety; moment-map | text-layer | search-ok; verify-math-before-claim |
| 45 | `45_ahmed_bekbaev_rakhimov_two_dimensional_jordan_algebras.pdf` | low-dimensional-Jordan; classification; examples | text-layer | search-ok; verify-math-before-claim |
| 46 | `46_ancochea_fresan_margalef_contractions_low_dimensional_nilpotent_jordan_algebras.pdf` | nilpotent-Jordan; low-dimensional; contractions; deformations | text-layer | search-ok; verify-math-before-claim |
| 47 | `47_hegazi_abdelwahab_construction_nilpotent_jordan_algebras.pdf` | nilpotent-Jordan; cohomology; classification | text-layer | search-ok; verify-math-before-claim |
| 48 | `48_dokas_frankland_ikonicoff_quillen_cohomology_divided_power_algebras_operad.pdf` | Quillen-cohomology; Beck-modules; divided-power-algebras; operads | text-layer | search-ok; verify-math-before-claim |
| 49 | `49_agrawalla_khlaif_miller_andre_quillen_cohomology_commutative_monoids.pdf` | Andre-Quillen; commutative-monoids; Beck-modules | text-layer | search-ok; verify-math-before-claim |
| 50 | `50_szymik_quandle_cohomology_quillen_cohomology.pdf` | Quillen-cohomology; quandle-cohomology | text-layer | search-ok; verify-math-before-claim |
| 51 | `51_fresse_operadic_cobar_constructions_cylinder_objects_homotopy_morphisms.pdf` | operadic-cobar; cofibrant-replacements; homotopy-morphisms | text-layer | search-ok; verify-math-before-claim |
| 52 | `52_harper_bar_constructions_quillen_homology_modules_operads.pdf` | bar-constructions; Quillen-homology; operads | text-layer | search-ok; verify-math-before-claim |
| 53 | `53_truong_hochschild_cotangent_complexes_operadic_algebras.pdf` | cotangent-complex; Hochschild-cohomology; operadic-algebras | text-layer | search-ok; verify-math-before-claim |
| 54 | `54_fialowski_mukherjee_naolekar_versal_deformation_quadratic_operad.pdf` | deformation; quadratic-operads; versal-deformation | text-layer | search-ok; verify-math-before-claim |
| 55 | `55_markl_intrinsic_brackets_l_infinity_deformation_bialgebras.pdf` | deformation; intrinsic-brackets; bialgebras | text-layer | search-ok; verify-math-before-claim |
| 56 | `56_Springer_Jordan_Algebras_and_Algebraic_Groups.pdf` | Jordan-algebras; algebraic-groups; structure-background | text-layer | search-ok; verify-math-before-claim |
| 57 | `57_springer_veldkamp_octonions_jordan_algebras_exceptional_groups.pdf` | octonions; Jordan-algebras; exceptional-groups | text-layer | search-ok; verify-math-before-claim |
| extra | `on_homology_of_jordan_algebras(1).pdf` | extra; provenance-check | text-layer | do-not-cite-until-verified |
