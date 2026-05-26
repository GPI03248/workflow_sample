# Formula Confidence Report

**Inventory**: `docs/formula_inventories/cfweno5_scalar_formulas.yml`

## Summary

| Metric | Count |
|--------|-------|
| Total formulas | 12 |
| High confidence | 11 |
| Medium confidence | 1 |
| Low confidence | 0 |
| Blocking formulas | 1 |

**Implementation readiness**: Not ready for implementation approval

## High Confidence Formulas (11)

- `table_I_r3_k0`: verified, relevance=required
- `table_I_r3_k1`: verified, relevance=required
- `table_I_r3_k2`: verified, relevance=required
- `table_II_r3_k0`: verified, relevance=required
- `table_II_r3_k1`: verified, relevance=required
- `table_II_r3_k2`: verified, relevance=required
- `eq19_smoothness_r3`: verified, relevance=required
- `appendix_A_eq_A1`: verified, relevance=required
- `cfweno5_stencil_expression`: verified, relevance=required
- `cfweno5_interface_reconstruction`: verified, relevance=required
- `cfweno5_conservative_update`: verified, relevance=required

## Medium/Low Confidence Formulas (1)

- `appendix_A_eq_A2`: confidence=medium, verification=partial, relevance=required, blocks=True

## Blocking Formulas (1)

The following formulas block implementation approval:

1. `appendix_A_eq_A2`: confidence=medium, verification=partial

## Warnings (1)

- REQUIRED formula 'appendix_A_eq_A2' has medium confidence (status: partial)

## Recommended Human Verification Queue

1. `appendix_A_eq_A2`: currently medium confidence, partial

## Decision

**Conditionally ready, blocked by 1 medium/low confidence required formulas.**
