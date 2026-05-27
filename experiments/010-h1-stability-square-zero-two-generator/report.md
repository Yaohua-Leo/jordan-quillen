# Experiment 010 Report

Plan: `researchplan/subplan010.md`

This report summarizes the same in-memory result object written to `results.json`. It is computational evidence only and does not claim presentation invariance.

## Conventions

- Base field: `QQ`
- Category: `nonunital Jordan algebras`
- Target algebra: `k{x,y}/(x^2, xy, y^2)`
- Matrix convention: `source_rows_target_coordinates`
- Canonical relation basis: `x^2`, `xy`, `y^2`

## Outcome Statuses

`pass_strong`, `pass_weak_dimension_only`, `expected_fail_observed`, `unexpected_fail`, `unexpected_pass`

## Diagnostics

| Case | Group | Outcome | dim H1 | Certificate |
| --- | --- | --- | ---: | --- |
| A_minimal_presentation | A_minimal_presentation_baseline | pass_strong | 3 | yes |
| C_redundant_relation_without_syzygy | C_naive_redundant_relation_control | expected_fail_observed | 4 | no |
| D_redundant_relation_with_syzygy | D_repaired_redundant_relation | pass_strong | 3 | yes |
| F_truncation_depth_diagnostic | F_truncation_depth_diagnostic | pass_strong | 3 | yes |
| B_linear_change_g1 | B_linear_change_of_generators | pass_strong | 3 | yes |
| B_linear_change_g2 | B_linear_change_of_generators | pass_strong | 3 | yes |
| B_linear_change_g3 | B_linear_change_of_generators | pass_strong | 3 | yes |
| E_multiple_redundant_relations_m1 | E_multiple_redundant_relations | pass_strong | 3 | yes |
| E_multiple_redundant_relations_m2 | E_multiple_redundant_relations | pass_strong | 3 | yes |
| E_multiple_redundant_relations_m3 | E_multiple_redundant_relations | pass_strong | 3 | yes |
| E_multiple_redundant_relations_m5 | E_multiple_redundant_relations | pass_strong | 3 | yes |

## Truncation Depth

```text
minimal_presentation: {'N=1': 3, 'N=2': 3, 'N=3': 3}
redundant_without_syzygy: {'N=1': 4, 'N=2': 4, 'N=3': 4}
redundant_with_syzygy: {'N=1': 4, 'N=2': 3, 'N=3': 3}
```

## Limitations

This is a bounded low-degree diagnostic for one square-zero example. It supports H1 stability under the listed presentation stresses but does not prove presentation invariance.

## Interpretation

Experiment 010 supports the stability of the computed H1 for the two-generator square-zero Jordan algebra under deterministic linear generator changes and controlled redundant-relation refinements. The expected-fail control reproduces the false extra H1 class that appears when a redundant relation is added without the corresponding syzygy. This supports, but does not prove, the identification of the stable H1 with Sym^2(k^2) in this bounded example.
