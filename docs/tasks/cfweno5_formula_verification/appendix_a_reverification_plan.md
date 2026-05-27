# Appendix A Re-Verification Plan

**Date**: 2026-05-27
**Context**: v1.3-pre.7 — formula gate hardening after failed CFWENO5 implementation
**Previous verification**: Character-level pdftotext (verified, high confidence)
**After failed implementation**: DEMOTED to medium/failed_validation

---

## What Failed

The CFWENO5 scalar linear advection implementation (see `docs/tasks/cfweno5_scalar_prototype/failed_attempt_diagnostic.md`) achieved only ~1st-order convergence (expected ~5th). The diagnostic revealed:

1. **s2 substencil**: Only 2nd-order individually (should be 4th)
2. **Combined scheme**: 1st-order multi-step, 3rd-order at best with corrected s2
3. **CFWENO3 regression**: Unchanged at ~3.0 order (not affected)

## Suspected Root Cause

**The s2 substencil coefficient placement is wrong.** Extracted s2:

```
ubar^3_{i+1/2,2} = u_i + (1/2)(1-nu)(u_{i+1/2} - u_i)
                   + (1-nu)(-nu)(u_i - 2*u_{i+1/2} + u_{i+1})
```

The factor `(1/2)` on the first correction term is suspicious. In the CFWENO3 (r=2) counterpart, this factor is 1, not 1/2. The left-biased substencil s0 has the full factor (not 1/2) on its first correction term. Moving the 1/2 factor to the second correction term improved s2 to 4th order individually, but the full 4-substencil combination still only achieved 3rd order — suggesting additional errors.

## What Must Be Re-Verified

### Priority 1: s2 Substencil (highest risk)

The s2 (k=2, right-biased) substencil is the primary suspect. A human must read the PDF at **Appendix A, page 23 (journal numbering)** and verify character-by-character:

1. The **first correction term coefficient**: Is it `(1/2)(1-nu)` or `(1-nu)`?
2. The **second correction term**: Does `(1-nu)(-nu)` apply to `(u_i - 2*u_{i+1/2} + u_{i+1})` or a different combination?
3. The **overall structure**: Are there 2 or 3 correction terms? The pdftotext shows 2 terms past the base u_i. Compare with s0 (also 2 correction terms) and s3 (4 correction terms).

### Priority 2: All Substencil Coefficients (s0, s1, s2, s3)

Re-read the entire Appendix A Eq. (A1) from the rendered PDF at full resolution:

| Substencil | Expected terms | Current extraction | Suspicious aspects |
|------------|---------------|-------------------|-------------------|
| s0 (k=0) | base + 2 | u + (1-nu)(u - u_hl) + 0.5*(1-nu)*(u_im1 - 2*u_hl + u) | 0.5 factor on 2nd term — is this correct? |
| s1 (k=1) | base + 2 | u + (1-nu)(u_hr - u) + (1-nu)*(-nu)*(u_hl - 2*u + u_hr) | Looks structurally correct (CFWENO3 pattern) |
| s2 (k=2) | base + 2 | u + 0.5*(1-nu)*(u_hr - u) + (1-nu)*(-nu)*(u - 2*u_hr + u_ip1) | **0.5 on 1st term is suspicious** — should be 1.0? |
| s3 (k=3) | base + 4 | u + (1-nu)*(u_hr - u) + 0.5*(1-nu)*(-nu)*... + 0.25*(1-nu)*(-nu)*(1+nu)*... + (1/12)*(1-nu)^2*(-nu)*(1+nu)*... | Most complex; multiple coefficient errors possible |

### Priority 3: Table I Weight Assignment

The current implementation uses k=0,1,2 with k=3 omitted (N/A in Table I). Verify:

1. Does Table I list weights for **all 4 substencils** (k=0,1,2,3) or only 3?
2. If k=3 has a weight but is marked "N/A", what does N/A mean? Could it be "not applicable" because k=3 is a higher-order correction not used with linear weights?
3. Do the 3 weights sum to 1? Current check: `nu*(1+nu)/6 + (1+nu)*(2-nu)/6 + (1-nu)*(2-nu)/6` does not trivially simplify to 1 for general nu.

### Priority 4: Higher-Order Interface Reconstruction

The current 4th-order centered reconstruction may be insufficient for 5th-order CFWENO. Verify:

1. Does the paper specify a different interface reconstruction for CFWENO5 vs CFWENO3?
2. Should a 6th-order reconstruction be used? The diagnostic tested 6th-order reconstruction and it did NOT improve convergence, but this might interact with substencil errors.
3. Does Eq. (13) provide a general formula for arbitrary order, or is it fixed at 4th order?

---

## Verification Procedure

1. **Open the paper PDF** at `.local/papers/cfweno_pof_2025.pdf` page 23 (journal numbering: Appendix A)
2. **Read Eq. (A1) character by character** for all 4 substencils
3. **Write down each coefficient exactly** — no interpretation, no "it looks like"
4. **Compare against the extraction report** (`docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md`, Section 1)
5. **Mark every discrepancy** — even minor subscript differences
6. **Re-read Table I** (page 5) to confirm r=3 row, all columns, especially k=2 and k=3
7. **Check for any footnote** or text near Table I explaining k=3 or weight sum-to-1 conditions
8. **Check interface reconstruction requirements** — search for any CFWENO5-specific reconstruction formula

### Output

After re-verification, update:
- `docs/formula_inventories/cfweno5_scalar_formulas.yml` — fix coefficients, promote to high/verified if confirmed
- `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md` — add re-verification section with findings
- This re-verification plan — mark items as resolved

### Acceptance Criteria

**Formulas are considered re-verified when:**
1. All substencil coefficients are independently read from the rendered PDF
2. Any discrepancies with the current extraction are resolved
3. The corrected s2 achieves 4th-order convergence individually (single-step test)
4. All 4 individual substencils achieve at least their expected individual orders
5. The 3-substencil combination achieves ~5th-order convergence
6. `consistency_status` can be changed from `failed` to `passed`

**Until criteria 3-6 are met, `consistency_status` remains `failed` and the strict formula confidence gate blocks implementation.**

---

## Related Documents

- Failure diagnostic: `docs/tasks/cfweno5_scalar_prototype/failed_attempt_diagnostic.md`
- Formula inventory: `docs/formula_inventories/cfweno5_scalar_formulas.yml`
- Extraction report: `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md`
- Subset spec: `docs/scheme_specs/cfweno5_scalar_subset.md`
- Source PDF: `.local/papers/cfweno_pof_2025.pdf` (not in git)
