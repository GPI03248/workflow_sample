# Formula Confidence Report

**Inventory**: `docs/formula_inventories/cfweno5_scalar_formulas.yml`

## Summary

| Metric | Count |
|--------|-------|
| Total formulas | 12 |
| High confidence | 8 |
| Medium confidence | 4 |
| Low confidence | 0 |
| Blocking formulas | 4 |

**Implementation readiness**: Not ready for implementation approval

## High Confidence Formulas (8)

- `table_I_r3_k0`: verified, relevance=required
- `table_I_r3_k1`: verified, relevance=required
- `table_I_r3_k2`: verified, relevance=required
- `table_II_r3_k0`: verified, relevance=required
- `table_II_r3_k1`: verified, relevance=required
- `table_II_r3_k2`: verified, relevance=required
- `cfweno5_interface_reconstruction`: verified, relevance=required
- `cfweno5_conservative_update`: verified, relevance=required

## Medium/Low Confidence Formulas (4)

- `eq19_smoothness_r3`: confidence=medium, verification=uncertain, relevance=required, blocks=True
- `appendix_A_eq_A1`: confidence=medium, verification=visually_confirmed, relevance=required, blocks=True
- `appendix_A_eq_A2`: confidence=medium, verification=visually_confirmed, relevance=required, blocks=True
- `cfweno5_stencil_expression`: confidence=medium, verification=partial, relevance=required, blocks=True

## Blocking Formulas (4)

The following formulas block implementation approval:

1. `eq19_smoothness_r3`: confidence=medium, verification=uncertain
1. `appendix_A_eq_A1`: confidence=medium, verification=visually_confirmed
1. `appendix_A_eq_A2`: confidence=medium, verification=visually_confirmed
1. `cfweno5_stencil_expression`: confidence=medium, verification=partial

## Warnings (4)

- REQUIRED formula 'eq19_smoothness_r3' has medium confidence (status: uncertain)
- REQUIRED formula 'appendix_A_eq_A1' has medium confidence (status: visually_confirmed)
- REQUIRED formula 'appendix_A_eq_A2' has medium confidence (status: visually_confirmed)
- REQUIRED formula 'cfweno5_stencil_expression' has medium confidence (status: partial)

## Recommended Human Verification Queue

1. `eq19_smoothness_r3`: currently medium confidence, uncertain
2. `appendix_A_eq_A1`: currently medium confidence, visually_confirmed
3. `appendix_A_eq_A2`: currently medium confidence, visually_confirmed
4. `cfweno5_stencil_expression`: currently medium confidence, partial

## Decision

**Conditionally ready, blocked by 4 medium/low confidence required formulas.**
