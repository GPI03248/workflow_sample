# CFWENO5 Combined Reconstruction Target Audit

**Date**: 2026-05-29
**Task**: v1.3-pre.10 - Re-verify Appendix A combined reconstruction target
**Status**: Outcome B - still blocked

## Question

The milestone investigated why the CFWENO5 combined reconstruction still fails
a 5th-order diagnostic after the v1.3-pre.8 s2 correction and v1.3-pre.9
weight-role audit.

The candidate blockers were:

1. residual Appendix A substencil transcription error;
2. wrong combined reconstruction target;
3. Table I / Table II role confusion;
4. missing or incorrect Eq. (17) normalization;
5. checker testing a quantity different from the paper definition.

## Paper Evidence

Eq. (16) defines two WENO reconstruction targets:

- `ubar_{i+1/2}`: averaged cell-interface value, using Table I `c_bar_rk`
  and Appendix A Eq. (A1) substencil integrals.
- `u^{n+1}_{i+1/2}`: next-time-level interface value, using Table II `c_rk`
  and Appendix A Eq. (A2) point-evaluation expressions.

Appendix A Eq. (A1) prints three indexed CFWENO5 substencil expressions,
`k=0,1,2`, followed by a fourth expression without a `,k` subscript. That
fourth expression is the direct full-polynomial averaged target for
`ubar_{i+1/2}`, not a fourth Table I substencil.

This matches Table I, where the r=3 row has three valid entries and the k=3
column is not applicable.

## Checker Evidence

`tools/check_cfweno5_formula_consistency.py` now separates two diagnostics:

- `appendix_A_full_target`: the direct full-stencil target printed as the
  fourth Eq. (A1) expression.
- `cfweno5_table_I_combined`: the Eq. (16) / Table I WENO-combination path,
  using Eq. (17) normalized Table I alpha numerators.

Quick diagnostic result at CFL=0.5:

| Quantity | Observed order | Result |
|---|---:|---|
| s0 | ~3.00 | pass |
| s1 | ~4.01 | pass |
| s2 | ~4.01 | pass |
| Appendix A direct full target | ~6.00 | pass |
| Eq. (16) / Table I combined diagnostic | ~3.00 | fail |

Weight diagnosis also includes `appendix_A_full_target`. The direct full target
passes, while normalized Table I, Table II, and equal-weight variants remain
near third order.

## Interpretation

The strongest supported blocker is **combined reconstruction target mismatch / checker target mismatch**.

The existing checker was using a WENO-combination diagnostic as the only
"combined" CFWENO5 check. That made it look as if Appendix A Eq. (A1) itself
was globally inconsistent. The direct full-stencil target printed in Appendix A
is numerically high order, so a residual coefficient error in that full target is
not currently supported by the diagnostic evidence.

However, CFWENO5 remains blocked because the paper/spec interpretation of the
Eq. (16) Table I WENO combination is not yet reconciled with the direct Appendix
A target. The normalized Table I combination still caps near third order, so the
checker cannot yet prove that the WENO-combination path recovers the printed
full target.

## Outcome

Outcome B - still blocked.

- CFWENO5 implementation remains forbidden.
- `Approved for implementation` remains `no`.
- Formula-confidence strict gate is expected to fail because
  `cfweno5_stencil_expression` still has failed consistency.
- The next single verification step is to reconcile Eq. (16), Table I, and the
  fourth Eq. (A1) full-target expression algebraically: determine whether the
  published Table I weights, after Eq. (17), are intended to reproduce the
  printed full target, or whether the direct full target is the correct scalar
  diagnostic target for this milestone.
