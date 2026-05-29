# CFWENO5 Formula Gate Scope Alignment

**Date**: 2026-05-29
**Task**: v1.3-pre.12 - Align formula-confidence gate with direct target policy
**Decision**: A - gate aligned and ready for human approval consideration

## Purpose

v1.3-pre.11 accepted Appendix A's direct full-stencil averaged target as the
first scalar linear CFWENO5 prototype target. This milestone aligns the formula
inventory, confidence checker, and reports with that target scope.

## 1. Why The Direct Appendix A Full Target Is Accepted

Appendix A Eq. (A1) prints three indexed `k=0,1,2` CFWENO5 expressions followed
by a fourth expression without a `,k` subscript. That fourth expression is the
paper-derived direct full-stencil averaged target for `ubar_{i+1/2}`.

The diagnostic checker reports this target as `appendix_A_full_target`, and it
reaches about 6th observed one-step order at CFL=0.5. This is sufficient for the
narrow scalar linear direct-target prototype gate.

## 2. Why Eq.16 / Table I Is Diagnostic-Only Here

Eq. (16) / normalized Table I describes a WENO-combination path. In the current
checker that path remains near 3rd order and does not reproduce the direct
Appendix A full target. It is therefore deferred to later nonlinear/WENO scope.

This milestone does not claim the Eq.16/Table I WENO-combination path is valid,
and it does not claim shock-capturing or full CFWENO paper reproduction.

## 3. Required Scalar Linear Direct-Target Formulas

The scalar linear direct-target gate requires:

- Appendix A Eq. (A1) direct full-stencil averaged target;
- interface reconstruction for the direct target;
- conservative update.

These formulas must be high confidence, verified, and must not have failed
consistency for the direct-target scope.

## 4. Deferred Later-Scope Formulas

The following remain visible but do not block scalar linear direct-target strict
checks:

- Table I normalized WENO-combination weights;
- Table II next-time-level WENO-combination weights;
- Eq. (19) smoothness indicators;
- Appendix A Eq. (A2) derivative target;
- Eq. (16) / Table I combined stencil expression.

They are deferred to future nonlinear/WENO-combination milestones.

## 5. Strict Gate Policy

`tools/check_formula_confidence.py --require-high-for-implementation` now checks
required formulas in the scalar-linear direct-target scope. Formulas marked
`formula_scope: diagnostic_only` or `formula_scope: deferred_nonlinear_weno` are
reported but do not block this scope-specific strict gate.

The gate is not globally weakened: a required scalar-linear formula still blocks
if confidence is not high, verification is not `verified`, or
`consistency_status` is `failed`.

## 6. Outside Current Scope

Still outside scope:

- production CFWENO5 implementation;
- changing `Approved for implementation` to `yes`;
- Eq.16/Table I WENO-combination validation;
- nonlinear, shock-capturing, Euler, or full CFWENO paper reproduction.

## Outcome

Decision A: the scalar linear direct-target formula gate is aligned. The direct
target is ready for human approval consideration in a separate milestone, while
CFWENO5 remains unimplemented and unapproved.
