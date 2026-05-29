# CFWENO5 Direct Target Policy

**Date**: 2026-05-29
**Task**: v1.3-pre.11 - Resolve direct Appendix A target policy
**Decision**: A - direct Appendix A full-stencil target accepted as the scalar linear prototype target

## Policy Decision

For the first scalar linear CFWENO5 prototype, the implementation/validation
target is the direct Appendix A Eq. (A1) full-stencil averaged target for
`ubar_{i+1/2}`.

The Eq. (16) / normalized Table I WENO-combination path remains a diagnostic
and future nonlinear/WENO-combination reconciliation item. It is not required
for the first scalar linear direct-target prototype.

`Approved for implementation` remains `no`; human approval is still required in
a separate step before implementation.

## 1. What Appendix A Direct Full-Stencil Target Represents

Appendix A Eq. (A1) prints three indexed CFWENO5 expressions for `k=0,1,2`,
followed by a fourth expression with no `,k` subscript. The fourth expression is
the direct full-polynomial averaged target for `ubar_{i+1/2}`. It corresponds to
integrating the full quartic polynomial `q(x)` in Eq. (13), not to a fourth
Table I substencil.

This interpretation is supported by Table I: for `r=3`, the table has three
valid weights and the `k=3` column is not applicable.

## 2. What Eq. (16) / Table I Normalized Combination Represents

Eq. (16) describes a WENO reconstruction of the averaged target using nonlinear
weights `x_bar_rk`. Table I provides the corresponding `c_bar_rk` alpha
numerators, and Eq. (17) normalizes them before use.

In the current diagnostic checker, the Eq. (16) / Table I path means combining
only the three Appendix A indexed substencil expressions `s0`, `s1`, and `s2`
with normalized Table I weights.

## 3. Are The Two Targets Expected To Be Equivalent?

They are expected to represent the same averaged physical quantity in the full
paper method, but the current transcription/spec does not yet prove that the
three-substencil Eq. (16) diagnostic algebraically reproduces the direct Appendix
A full target.

Numerically, they are not equivalent in the current checker:

| Target | Quick observed order at CFL=0.5 | Status |
|---|---:|---|
| Appendix A direct full target | ~6.00 | pass |
| Eq. (16) / normalized Table I combination | ~3.00 | diagnostic fail |

The direct target is therefore the only currently verified 5th-order-or-better
scalar linear target.

## 4. Appropriate Target For The First Scalar Linear Prototype

Use the direct Appendix A full-stencil averaged target.

Reasoning:

- It is paper-derived from Appendix A Eq. (A1) and Eq. (13).
- It reaches near 5th order or better in the existing one-step diagnostic.
- The scalar linear first prototype is a smooth-problem benchmark, not a claim
  of complete nonlinear WENO shock-capturing behavior.
- Requiring the unresolved Eq. (16) / Table I WENO-combination path would block a
  narrower direct-target scalar prototype even though the paper provides an
  explicit high-order full-stencil target.

## 5. Does The Checker Test The Correct Target?

Yes for the scalar linear direct-target policy. The default consistency checker
now treats these as required:

- `s0`, `s1`, `s2` individual substencil diagnostics;
- `appendix_A_full_target` as the required scalar linear target.

The checker still reports `cfweno5_table_I_combined`, but it is marked as a
diagnostic-only unresolved target and does not fail the direct-target gate.

## 6. Formula Consistency Gate Policy

For the first scalar linear direct-target prototype, the formula consistency gate
requires:

1. the indexed Appendix A substencils to remain internally sane;
2. the direct Appendix A full-stencil target to reach at least near 5th order;
3. formula-confidence strict gate to pass for required direct-target formulas.

The Eq. (16) / Table I WENO-combination diagnostic is retained but does not block
this first scalar linear target. It should become blocking only for a later
milestone that claims WENO-combination, nonlinear, or shock-capturing behavior.

## 7. Remaining Blockers Before Implementation

The remaining blockers are procedural and scope-related, not formula-confidence
blockers for the direct target:

- `Approved for implementation` is still `no` and must only be changed by a
  later human-approved milestone.
- The future implementation must be explicitly scoped as scalar linear
  direct-target CFWENO5, not full CFWENO5 and not nonlinear WENO behavior.
- The implementation milestone must decide where the code lives without touching
  forbidden files unless approved.
- Eq. (16) / Table I WENO-combination remains unresolved and must not be claimed
  as validated.

## 8. If Eq. (16) / Table I Later Becomes Required

If a later milestone requires the Eq. (16) / Table I combination, the exact
remaining ambiguity is:

How the three normalized Table I substencil expressions in Eq. (16) reproduce
(or intentionally differ from) Appendix A's direct full-stencil averaged target.

That later milestone should perform an algebraic derivation from Eq. (11), Eq.
(13), Eq. (15), Eq. (16), Table I, and Appendix A Eq. (A1), rather than tuning
coefficients numerically.
