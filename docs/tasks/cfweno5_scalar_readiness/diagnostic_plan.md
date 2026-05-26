# Diagnostic Plan: Scalar CFWENO5 Readiness Review

**Task ID**: cfweno5_scalar_readiness
**Task type**: post-v1.0 readiness review (not implementation)
**Based on**: v1.0 tag `42d97ee`, Burgers order recovery commit `4d671c0`
**Date**: 2026-05-26

---

## Motivation

After the Burgers nonlinear order recovery diagnostic (commit `4d671c0`), the
project faces a decision point:

1. **Burgers CFWENO3 is structurally ~2nd-order** — no nu-treatment variant
   recovers 3rd order. The order reduction is inherent to the CFWENO3 stencil
   applied to nonlinear problems.
2. **Continuing to tune CFWENO3 parameters has diminishing returns.** The
   diagnostic tested 4 variants across 3 case configurations (12 combinations)
   and none approached 3rd order.
3. **The next highest-value scalar target is CFWENO5.** A 5th-order stencil
   would provide a stronger smooth-problem benchmark and might show whether the
   paper's higher-order formulation is reproducible at all.
4. **CFWENO5 is safer than Euler.** It stays within 1D scalar, periodic BC,
   and uses existing infrastructure. No characteristic decomposition, no 2D,
   no shock-capturing.

---

## Current Baseline

| Capability | Status | Observed Order |
|-----------|--------|---------------|
| Scalar linear CFWENO3 | Complete (v1.1) | ~3.02 |
| Scalar Burgers CFWENO3 | Complete (v1.2) | ~2.01 |
| Burgers order recovery | Complete (v1.1-pre diagnostic) | No variant > 2.01 |
| CFWENO5 | Not started | — |
| Euler CFWENO | Not started | — |
| 2D CFWENO | Not started | — |

---

## CFWENO5 Readiness Questions

### 1. Does the paper provide CFWENO5 stencil formulas?

**Critical gap.** The extraction report only transcribed Eq. (30), the CFWENO3
(3rd-order) stencil. The paper must contain a generalization for 5th order
(or a different equation number), but it was **never extracted**. The extraction
report has no Appendix A content and no CFWENO5-specific stencil formula.

### 2. Are optimal weights available for r=3 (CFWENO5)?

**Missing.** The dependency register states that Tables I-II provide weights
for r=2,3,4 (CFWENO3, 5, 7), but only r=2 values were transcribed. The r=3
weight values needed for CFWENO5 implementation are not in the repo.

The general formula pattern is known:
- `gamma_bar_0^3 = (1+nu)^2/6`
- `gamma_bar_1^3 = (1+nu)(2-nu)/6`
- `gamma_bar_2^3 = (1-nu)(2-nu)/6`

But the full weight set for the 5th-order substencil structure (r+1 = 4 substencils)
has not been verified against the paper.

### 3. Are smoothness indicators defined for CFWENO5?

**Partially.** Eq. (19) gives the general smoothness indicator formula, and the
WENO weight machinery (Eq. 17) is order-independent. But the explicit polynomial
expressions for the r=3 substencil case have not been written out or verified.

### 4. Does the paper's Appendix A provide what's needed?

**Unknown.** No Appendix A content exists anywhere in the repo. The extraction
report did not cover appendices. This is a significant gap — the appendix likely
contains the expanded stencil formulas and coefficient tables.

### 5. Periodic boundary handling — does it need extension?

CFWENO5 uses a wider stencil than CFWENO3. The current `np.roll` approach
extends naturally, but the stencil width increases from 4 cells (CFWENO3) to
approximately 6 cells (CFWENO5). This is a minor implementation concern, not
a blocker.

### 6. Is solver/schemes.py suitable for CFWENO5?

The current structure is clean and extensible. A CFWENO5 implementation would
need:
- A new stencil function (replacing `_cfweno3_stencil`)
- Possibly a higher-order interface reconstruction
- New top-level functions `cfweno5()` and potentially `cfweno5_burgers()`

The `_SCHEMES` registry can easily add `"cfweno5"`. The blocker is missing
formulas, not architecture.

### 7. Should scalar CFWENO helpers be refactored first?

CFWENO3 currently uses three functions in `solver/schemes.py`:
`_interface_reconstruction()`, `_cfweno3_stencil()`, `cfweno_burgers()`.
Adding CFWENO5 would add 2-3 more functions. The file (232 lines) is still
manageable but approaching a point where a `solver/cfweno.py` module might
be cleaner. This is a style decision, not a blocker.

### 8. New reference / convergence benchmarks needed?

The existing convergence framework (nx=40/80/160/320, reference nx=2560+) can
be reused directly. Expected observed order for CFWENO5 should be ~5 if the
formulas are correct.

### 9. Should implementation still target smooth linear advection only?

Yes. First implementation should be smooth linear advection with periodic BC.
This is the simplest possible test case and the same one used for CFWENO3.
Burgers CFWENO5 can follow after linear convergence is confirmed.

---

## Summary of Readiness Status

| Item | Status | Blocking? |
|------|--------|-----------|
| CFWENO5 stencil formula | **NOT EXTRACTED** | **YES** |
| Optimal weights (Tables I-II, r=3) | **NOT TRANSCRIBED** | **YES** |
| Smoothness indicators (Eq. 19, r=3) | **NOT EXPANDED** | **YES** |
| Interface reconstruction order | Needs verification | Minor |
| Solver architecture | Extensible | No |
| Convergence framework | Reusable | No |
| Periodic boundary handling | Extensible | No |

**Verdict**: CFWENO5 is **blocked** until the paper's CFWENO5 stencil formula,
weight tables, and smoothness indicators are extracted and verified.
The blocker is formula extraction, not code architecture.
