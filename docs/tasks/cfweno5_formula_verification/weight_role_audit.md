# CFWENO5 Weight Role Audit

**Date**: 2026-05-27
**Task**: v1.3-pre.9 — Audit Table I/Table II weight role for combined reconstruction
**Paper**: Zhou-Dong-Pan (2025), Phys. Fluids 37, 106131

---

## Trigger

After v1.3-pre.8 s2 correction:
- s0/s1/s2/s3 substencil individual checks all pass (3.0, 4.0, 4.0, 6.0 respectively)
- Combined reconstruction still ~1st order
- Table I r=3 weights sum to `(4 - nu + nu^2)/6 ≠ 1` for general nu
- This strongly suggests a weight-role or reconstruction-target mismatch

---

## Source Equations (from paper)

### Eq. (15): Polynomial Decomposition

```
q(x) = sum_{k=0}^{r-1} c_rk * p_rk(x)
```

where `c_rk` are the **optimal linear weights** and `p_rk(x)` are the
r-th-order substencil polynomials. `q(x)` is the (2r-1)-th order
full-stencil polynomial.

### Eq. (16): WENO Reconstruction of Two Targets

The paper defines TWO distinct reconstruction targets:

**Target 1 — Averaged cell-interface value ubar_{i+1/2}:**
```
ubar^{2r-1}_{i+1/2} ≈ sum_{k=0}^{r-1} x_bar_rk * (1/(vh)) * ∫_{x_{i+1/2}-vh}^{x_{i+1/2}} p_rk(x) dx
```

where the integral of each substencil polynomial p_rk gives the
substencil expressions from Appendix A Eq. (A1).

**Target 2 — Next-time-level interface value u^{n+1}_{i+1/2}:**
```
u^{n+1,2r-1}_{i+1/2} ≈ sum_{k=0}^{r-1} x_rk * p_rk(x_{i+1/2} - vh)
```

where the substencil polynomials evaluated at x-vh give the
expressions from Appendix A Eq. (A2).

### Eq. (17): Nonlinear Weight Construction

```
alpha_bar_rk = c_bar_rk / (b_bar_k + eps)^2
alpha_rk     = c_rk     / (b_k + eps)^2

x_bar_rk = alpha_bar_rk / sum_{k=0}^{r-1}(alpha_bar_rk)
x_rk     = alpha_rk     / sum_{k=0}^{r-1}(alpha_rk)
```

**Critical**: `x_bar_rk` and `x_rk` are **explicitly normalized** by dividing
by the sum of alpha factors. Even when all smoothness indicators b_k
are equal (smooth solution), the denominator normalizes the weights
to sum to 1.

### Table I: Optimal Linear Weights for ubar_{i+1/2}

Provides `c_bar_rk` (the alpha-factor numerators), NOT the final weights.
For r=3 (CFWENO5):
- k=0: `nu(1+nu)/6`
- k=1: `(1+nu)(2-nu)/6`
- k=2: `(1-nu)(2-nu)/6`
- k=3: N/A (ellipsis in the table)

### Table II: Optimal Linear Weights for u^{n+1}_{i+1/2}

Provides `c_rk` for the next-time-level reconstruction target.
For r=3 (CFWENO5):
- k=0: `nu(5*nu^2+nu-2) / (6*(3*nu-1))`
- k=1: `-(30*nu^4-60*nu^3-nu^2+31*nu-8) / (6*(3*nu-1)*(3*nu-2))`
- k=2: `(nu-1)(5*nu^2-11*nu+4) / (6*(3*nu-2))`
- k=3: N/A

---

## Key Questions

### 1. Should Table I r=3 weights sum to 1 directly?

**No.** The paper defines them as `c_bar_rk` — optimal linear weights /
alpha-factor numerators. Eq. (17) explicitly normalizes them:
`x_bar_rk = alpha_bar_rk / sum(alpha_bar_rk)`.

The normalization ensures `sum(x_bar_rk) = 1`, guaranteeing that the
reconstruction is a convex combination of substencils. Raw `c_bar_rk`
need NOT sum to 1 — the normalization in Eq. (17) handles this.

### 2. If they don't sum to 1, is normalization needed?

**Yes.** Eq. (17) explicitly requires normalization. The WENO nonlinear
weights `x_bar_rk` are defined as `alpha_bar_rk / sum(alpha_bar_rk)`.
For smooth solutions where all b_k ≈ equal, `x_bar_rk ≈ c_bar_rk / sum(c_bar_rk)`.

The current checker uses raw `c_bar_rk` directly without normalization,
producing a reconstruction that is NOT a convex combination. This
violates consistency and explains the ~1st-order convergence.

### 3. Table I provides pre-normalization alpha factors?

**Yes.** Table I gives `c_bar_rk`, which are the numerators in Eq. (17)'s
alpha formula. They are not the final combination weights.

### 4. Table I only for ubar_{i+1/2}, not u^{n+1}_{i+1/2}?

**Yes.** The paper is explicit:
- Table I → `c_bar_rk` → `x_bar_rk` → `ubar_{i+1/2}` (averaged reconstruction)
- Table II → `c_rk` → `x_rk` → `u^{n+1}_{i+1/2}` (next-time-level reconstruction)

These are two DIFFERENT targets with DIFFERENT weights.

### 5. What target does the current combined checker test?

The current checker computes `ubar_right = scheme_fn(u0, nu, ...)` then applies
the conservative update `u1 = u0 - cfl*(ubar_right - ubar_left)`. This tests
the **averaged reconstruction** target `ubar_{i+1/2}`, which corresponds to
Table I weights (c_bar_rk). This is the CORRECT target for the single-step
consistency check.

### 6. Does the checker incorrectly mix Table I / Table II?

**No** — the checker correctly uses Table I weights for the ubar_{i+1/2} target.
However, it uses them **without the Eq. (17) normalization**.

### 7. Does the checker mix ubar_{i+1/2} and u^{n+1}_{i+1/2}?

**No** — the checker consistently tests the single-step conservative update
using ubar_{i+1/2} only. The bug is normalization, not target confusion.

---

## Decision

**Conclusion B**: Table I transcription is likely CORRECT, but the checker uses
the weights incorrectly — missing the Eq. (17) normalization step.

**Supporting evidence**:
1. Eq. (17) **explicitly** defines `x_bar_rk = alpha_bar_rk / sum(alpha_bar_rk)`
2. Table I provides `c_bar_rk` which are the numerators in alpha_bar_rk
3. The current checker uses raw `c_bar_rk` without normalization
4. Raw weights sum to (4-nu+nu^2)/6 ≠ 1 at nu=0.5, violating convex combination
5. All 4 individual substencils now pass (after s2 correction) → substencil formulas are likely correct
6. If normalization is the only missing step, `table_I_normalized` should achieve ~5th order

**Caveat**: This analysis assumes the smoothness indicators b_k are equal for
the smooth sinusoidal test case. For linear advection with equal b_k, the
nonlinear weights reduce to normalized linear weights. This is the correct
behavior and is what Eq. (17) specifies.

**Alternative possibility (less likely)**: If normalized Table I weights still
don't produce 5th order, additional errors exist — possibly in the Appendix A
substencil expressions (beyond s2), or the need for Table II weights in a
different part of the full CFWENO algorithm.

---

## Diagnostic Plan

Test the following variants:

| Variant | Weight source | Normalized | Target | Rationale |
|---------|--------------|-----------|--------|-----------|
| current_table_I_raw | Table I c_bar_rk | No | ubar_{i+1/2} | Current checker (known broken) |
| table_I_normalized | Table I c_bar_rk | Yes (sum=1) | ubar_{i+1/2} | Eq. (17) correct usage |
| table_II_raw | Table II c_rk | No | u^{n+1}_{i+1/2} | Wrong target, diagnostic only |
| table_II_normalized | Table II c_rk | Yes (sum=1) | u^{n+1}_{i+1/2} | Wrong target, diagnostic only |
| equal_weights_debug | Equal (1/3 each) | Yes | ubar_{i+1/2} | Diagnostic baseline |
| cfweno3_known_good | CFWENO3 (r=2) | No | ubar_{i+1/2} | Infrastructure sanity check |

**Prediction**: `table_I_normalized` should achieve ~5th order if the paper's
formulas are correct and normalization is the only issue.

---

## Diagnostic Results (2026-05-27)

The `--diagnose-weights` mode was implemented in the consistency checker
(`tools/check_cfweno5_formula_consistency.py`) and executed at CFL=0.5
with resolutions (40, 80, 160, 320).

### Results Summary

| Variant | Order | Weight Sum | Target | Result |
|---------|-------|-----------|--------|--------|
| CFWENO3 baseline | **4.00** | N/A | ubar_{i+1/2} | PASS (sanity check) |
| current_table_I_raw | **1.00** | 0.625 | ubar_{i+1/2} | FAIL — raw weights without normalization |
| table_I_normalized | **3.00** | 1.0 | ubar_{i+1/2} | FAIL — normalization fixes 1st-order but caps at 3rd |
| table_II_raw | **3.02** | 1.0 | u^{n+1}_{i+1/2} | FAIL — wrong target, weights already sum to 1 |
| table_II_normalized | **3.02** | 1.0 | u^{n+1}_{i+1/2} | FAIL — same as raw (normalization is no-op) |
| equal_weights_debug | **3.00** | 1.0 | ubar_{i+1/2} | FAIL — 1/3 each, same ceiling as optimal weights |

### Key Findings

1. **Normalization fixes the ~1st-order problem**: `table_I_normalized`
   achieves ~3.0 order (was ~1.0 for raw). The weight_role_audit diagnosis of
   "missing normalization" was CORRECT but INSUFFICIENT.

2. **ALL normalized variants cap at ~3.0**: Table I normalized, Table II raw,
   Table II normalized, and equal weights all achieve ~3.0 order. No weight
   set reaches 5th order.

3. **The ~3.0 ceiling is weight-independent**: Equal weights (1/3 each) achieve
   the same ~3.0 order as the "optimal" weights from both Table I and Table II.
   This means the weight choice is NOT the limiting factor.

4. **Substencil formulas likely have additional errors**: Since all 4 individual
   substencils pass (s0~3, s1~4, s2~4, s3~4), but ANY combination (regardless
   of weights) yields only ~3rd order, the substencil polynomials from Appendix A
   Eq. (A1) must have coefficient errors that break the error-term cancellation
   in Eq. (15)'s polynomial decomposition `q(x) = sum c_rk * p_rk(x)`.

5. **Table II weights already sum to 1.0**: The normalization for Table II
   is a no-op — raw `c_rk` already sum to 1.0 at nu=0.5. This was confirmed
   numerically.

6. **CFWENO3 baseline achieves ~4.0**: Better than ANY CFWENO5 variant. This
   confirms the checker infrastructure is working correctly and the problem
   is in the CFWENO5 formulas, not the test harness.

### Revised Conclusion

**Conclusion C**: The Table I transcription AND the Eq. (17) normalization are
BOTH correct. However, normalization is NOT sufficient to recover 5th-order
convergence. The substencil polynomials from Appendix A Eq. (A1) likely
contain additional transcription errors beyond the s2 correction (v1.3-pre.8).

**The error is in the Appendix A substencil polynomials themselves, not in
the Table I/Table II weights or the Eq. (17) normalization.**

### Recommended Next Action

Re-verify ALL Appendix A Eq. (A1) substencil polynomials (s0, s1, s2, s3)
from the original PDF. The current transcription must be compared against
the rendered PDF at high resolution. Each substencil's coefficient errors,
even small ones, will break the polynomial decomposition's error cancellation.

### Errata: Previous Prediction Was Wrong

The prediction "table_I_normalized should achieve ~5th order if the paper's
formulas are correct and normalization is the only issue" was FALSIFIED.
Normalization is NOT the only issue — the substencil polynomials have
additional errors.

---

## References

- Paper PDF: `.local/papers/cfweno_pof_2025.pdf` (not in git)
- Eq. (17): page 5, WENO nonlinear weight definition
- Table I: page 5, optimal linear weights for ubar_{i+1/2}
- Table II: page 6, optimal linear weights for u^{n+1}_{i+1/2}
- Appendix A Eq. (A1): page 24, substencil expressions for ubar_{i+1/2}
- Appendix A Eq. (A2): page 24, substencil expressions for u^{n+1}_{i+1/2}
