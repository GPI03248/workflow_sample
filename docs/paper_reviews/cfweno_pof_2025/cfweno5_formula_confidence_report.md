# Formula Confidence Report

**Inventory**: `docs/formula_inventories/cfweno5_scalar_formulas.yml`

## Summary

| Metric | Count |
|--------|-------|
| Total formulas | 12 |
| High confidence | 10 |
| Medium confidence | 2 |
| Low confidence | 0 |
| Blocking formulas | 0 |

**Implementation readiness**: Ready for implementation approval

## High Confidence Formulas (10)

- `table_I_r3_k0`: verified, relevance=not_needed, scope=deferred_nonlinear_weno, consistency=not_run
- `table_I_r3_k1`: verified, relevance=not_needed, scope=deferred_nonlinear_weno, consistency=not_run
- `table_I_r3_k2`: verified, relevance=not_needed, scope=deferred_nonlinear_weno, consistency=not_run
- `table_II_r3_k0`: verified, relevance=not_needed, scope=deferred_nonlinear_weno, consistency=not_run
- `table_II_r3_k1`: verified, relevance=not_needed, scope=deferred_nonlinear_weno, consistency=not_run
- `table_II_r3_k2`: verified, relevance=not_needed, scope=deferred_nonlinear_weno, consistency=not_run
- `eq19_smoothness_r3`: verified, relevance=not_needed, scope=deferred_nonlinear_weno, consistency=not_run
- `appendix_A_eq_A1`: verified, relevance=required, scope=scalar_linear_direct, consistency=passed
- `cfweno5_interface_reconstruction`: verified, relevance=required, scope=scalar_linear_direct, consistency=not_run
- `cfweno5_conservative_update`: verified, relevance=required, scope=scalar_linear_direct, consistency=not_run

## Medium/Low Confidence Formulas (2)

- `appendix_A_eq_A2`: confidence=medium, verification=derived, relevance=optional, scope=deferred_nonlinear_weno, blocks=False, consistency=not_required
- `cfweno5_stencil_expression`: confidence=medium, verification=failed_validation, relevance=not_needed, scope=deferred_nonlinear_weno, blocks=False, consistency=failed

## Deferred / Diagnostic Formulas (9)

- `table_I_r3_k0`: scope=deferred_nonlinear_weno, confidence=high, verification=verified, consistency=not_run
- `table_I_r3_k1`: scope=deferred_nonlinear_weno, confidence=high, verification=verified, consistency=not_run
- `table_I_r3_k2`: scope=deferred_nonlinear_weno, confidence=high, verification=verified, consistency=not_run
- `table_II_r3_k0`: scope=deferred_nonlinear_weno, confidence=high, verification=verified, consistency=not_run
- `table_II_r3_k1`: scope=deferred_nonlinear_weno, confidence=high, verification=verified, consistency=not_run
- `table_II_r3_k2`: scope=deferred_nonlinear_weno, confidence=high, verification=verified, consistency=not_run
- `eq19_smoothness_r3`: scope=deferred_nonlinear_weno, confidence=high, verification=verified, consistency=not_run
- `appendix_A_eq_A2`: scope=deferred_nonlinear_weno, confidence=medium, verification=derived, consistency=not_required
- `cfweno5_stencil_expression`: scope=deferred_nonlinear_weno, confidence=medium, verification=failed_validation, consistency=failed

## Numerical Consistency Failures (1)

The following formulas failed substencil-level numerical validation:

1. `cfweno5_stencil_expression`: confidence=medium, verification=failed_validation

See `docs/tasks/cfweno5_scalar_prototype/failed_attempt_diagnostic.md` for details.

## Decision

**Ready for implementation approval.**
