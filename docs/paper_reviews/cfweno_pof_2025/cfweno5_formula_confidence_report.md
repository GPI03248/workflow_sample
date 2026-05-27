# Formula Confidence Report

**Inventory**: `docs/formula_inventories/cfweno5_scalar_formulas.yml`

## Summary

| Metric | Count |
|--------|-------|
| Total formulas | 12 |
| High confidence | 9 |
| Medium confidence | 3 |
| Low confidence | 0 |
| Blocking formulas | 2 |

**Implementation readiness**: Not ready for implementation approval

## High Confidence Formulas (9)

- `table_I_r3_k0`: verified, relevance=required, consistency=not_run
- `table_I_r3_k1`: verified, relevance=required, consistency=not_run
- `table_I_r3_k2`: verified, relevance=required, consistency=not_run
- `table_II_r3_k0`: verified, relevance=required, consistency=not_run
- `table_II_r3_k1`: verified, relevance=required, consistency=not_run
- `table_II_r3_k2`: verified, relevance=required, consistency=not_run
- `eq19_smoothness_r3`: verified, relevance=required, consistency=not_run
- `cfweno5_interface_reconstruction`: verified, relevance=required, consistency=not_run
- `cfweno5_conservative_update`: verified, relevance=required, consistency=not_run

## Medium/Low Confidence Formulas (3)

- `appendix_A_eq_A1`: confidence=medium, verification=failed_validation, relevance=required, blocks=True, consistency=failed
- `appendix_A_eq_A2`: confidence=medium, verification=derived, relevance=optional, blocks=False, consistency=not_required
- `cfweno5_stencil_expression`: confidence=medium, verification=failed_validation, relevance=required, blocks=True, consistency=failed

## Blocking Formulas (2)

The following formulas block implementation approval:

1. `appendix_A_eq_A1`: confidence=medium, verification=failed_validation
1. `cfweno5_stencil_expression`: confidence=medium, verification=failed_validation

## Warnings (2)

- REQUIRED formula 'appendix_A_eq_A1' has medium confidence (status: failed_validation)
- REQUIRED formula 'cfweno5_stencil_expression' has medium confidence (status: failed_validation)

## Recommended Human Verification Queue

1. `appendix_A_eq_A1`: currently medium confidence, failed_validation, consistency=failed
2. `cfweno5_stencil_expression`: currently medium confidence, failed_validation, consistency=failed

## Numerical Consistency Failures (2)

The following formulas failed substencil-level numerical validation:

1. `appendix_A_eq_A1`: confidence=medium, verification=failed_validation
1. `cfweno5_stencil_expression`: confidence=medium, verification=failed_validation

See `docs/tasks/cfweno5_scalar_prototype/failed_attempt_diagnostic.md` for details.

## Decision

**Conditionally ready, blocked by 2 medium/low confidence required formulas.**
