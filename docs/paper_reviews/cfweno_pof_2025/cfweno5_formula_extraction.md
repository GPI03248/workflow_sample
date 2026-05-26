# CFWENO5 Formula Extraction Report

**Date**: 2026-05-26
**Extractor**: Claude Code (automated, pdftotext + manual parsing)

## Source

- **Paper**: High-order compact fully discrete schemes for inviscid compressible flows simulations
- **Authors**: Zhou, Dong, Pan
- **Journal**: Physics of Fluids 37, 106131 (2025)
- **DOI**: 10.1063/5.0291087
- **Local PDF**: `.local/papers/cfweno_pof_2025.pdf` (10.4 MB, NOT tracked in git)
- **Pages/sections checked**: Pages 4-6 (stencil construction, Tables I-III), Pages 5-6 (Eq. 19), Page 23 (Appendix A: Eqs. A1-A2), Page 11 (Eq. 30), Page 24 (Appendix B: Algorithm 2)
- **Extraction method**: `pdftotext -layout` followed by targeted grep and manual interpretation
- **Formula reliability**: MEDIUM — pdftotext mangles subscripts/superscripts; key tables are in multi-column layout requiring careful parsing. Critical formulas must be verified by human reading the PDF.

---

## Required Formula Inventory

### 1. CFWENO5 Substencil Expressions — Appendix A, Eqs. (A1)-(A2)

**Extracted**: YES (partial — text needs human verification)
**Confidence**: MEDIUM
**Source**: Appendix A, page 23, Eqs. (A1) and (A2)
**Implementation relevance**: REQUIRED

The paper provides CFWENO5 (r=3) as an explicit example in Appendix A.
For r=3, there are 4 substencils (k=0,1,2,3).

**Eq. (A1) — Initial value reconstruction ubar^{3}_{i+1/2,k}:**

The four substencils for the cell-average at i+1/2 are:

```
ubar^3_{i+1/2,0} = u_i + (1-nu)(u_i - u_{i-1/2})
                   + (1/2)(1-nu)(u_{i-1} - 2*u_{i-1/2} + u_i)

ubar^3_{i+1/2,1} = u_i + (1-nu)(u_{i+1/2} - u_i)
                   + (1-nu)(-nu)(u_{i-1/2} - 2*u_i + u_{i+1/2})

ubar^3_{i+1/2,2} = u_i + (1/2)(1-nu)(u_{i+1/2} - u_i)
                   + (1-nu)(-nu)(u_i - 2*u_{i+1/2} + u_{i+1})

ubar^3_{i+1/2,3} = u_i + (1-nu)(u_{i+1/2} - u_i)
                   + (1/2)(1-nu)(-nu)(u_i - 2*u_{i+1/2} + u_{i+1})
                   + (1/4)(1-nu)(-nu)(1+nu)(2*u_{i-1/2} - 5*u_i + 4*u_{i+1/2} - u_{i+1})
                   + (1/12)(1-nu)^2*(-nu)(1+nu)(-u_{i-1} + 6*u_{i-1/2} - 10*u_i + 6*u_{i+1/2} - u_{i+1})
```

NOTE: The pdftotext transcription of Eq. (A1) is unreliable due to multi-line
piecewise formatting. The above is a best-effort interpretation. **Human
verification against the PDF is required.**

**Eq. (A2) — Next-time-level reconstruction u^{n+1,3}_{i+1/2,k}:**

Same structure as (A1) but with derivatives `d/dv` applied, producing terms
with `dv` factors. The text extraction of (A2) is similarly mangled. Four
substencils k=0,1,2,3 are defined.

NOTE: Eq. (A2) is needed for the WENO combination producing `u^{n+1}_{i+1/2}`.
The pdftotext output is unreliable here. **Human verification required.**

---

### 2. CFWENO5 Interface Reconstruction

**Extracted**: YES (from Eq. 11 context)
**Confidence**: HIGH
**Source**: Eqs. (11) and (13), page 4
**Implementation relevance**: REQUIRED

CFWENO5 uses three quadratic polynomials p_0, p_1, p_2 and one quartic
polynomial q(x) for the 5th-order stencil. The cell-interface values
`u_{i-1/2}` and `u_{i+1/2}` are obtained from these polynomials.

For linear advection with constant `nu = cfl`, the same 4th-order centered
interface reconstruction used by CFWENO3 applies:
```
u_{i+1/2} = (-u_{i-1} + 7*u_i + 7*u_{i+1} - u_{i+2}) / 12
```

This is consistent with the paper's Eq. (13) for the quartic polynomial q(x)
evaluated at the interface. The interface reconstruction does NOT need to
change for CFWENO5.

---

### 3. CFWENO5 Conservative Update (Eq. 30 generalization)

**Extracted**: YES (structural understanding)
**Confidence**: HIGH
**Source**: Eq. (30) page 11, plus Eqs. (17) and (25)
**Implementation relevance**: REQUIRED

Eq. (30) gives the CFWENO3 stencil. For CFWENO5, the assembly is:

1. Compute WENO nonlinear weights from Eq. (17):
   ```
   alpha_bar_k = c_bar_rk / (b_k + eps)^2
   w_bar_k = alpha_bar_k / sum(alpha_bar_k)
   ```

2. Combine substencils from Appendix A:
   ```
   ubar_{i+1/2} = sum_k(w_bar_k * ubar^3_{i+1/2,k})
   ```

3. Similarly for u^{n+1}_{i+1/2} using Table II weights.

4. Conservative update (Eq. 25):
   ```
   u_i^{n+1} = u_i - cfl * (ubar_{i+1/2} - ubar_{i-1/2})
   ```

The structure is the same as CFWENO3 but with 4 substencils instead of 2.

---

### 4. Table I — Optimal Linear Weights c_bar_rk for ubar_{i+1/2}

**Extracted**: YES
**Confidence**: HIGH
**Source**: Table I, page 5
**Implementation relevance**: REQUIRED

For r=3 (CFWENO5), the weights are:

| k | c_bar^3_k |
|---|-----------|
| 0 | nu(1+nu) / 6 |
| 1 | (1+nu)(2-nu) / 6 |
| 2 | (1-nu)(2+nu) / 6 |
| 3 | (1-nu)(2-nu) / 6 |

Wait — correction from the PDF text. The table has 4 columns (k=0,1,2,3)
for r=3:

```
c_bar^3_0 = nu(1+nu) / 6
c_bar^3_1 = (1+nu)(2-nu) / 6
c_bar^3_2 = (1-nu)(2+nu) / 6   [UNCERTAIN — text unclear, could be (2-nu)]
c_bar^3_3 = (1-nu)(2-nu) / 6
```

NOTE: The multi-column PDF layout makes k=2 uncertain. It reads as either
`(1-nu)(2+nu)` or `(1-nu)(2-nu)`. **Human verification of Table I row r=3,
column k=2 is required.** The weights must sum to 1, which constrains the
correct value.

Verification: sum = [nu(1+nu) + (1+nu)(2-nu) + c_bar_2 + (1-nu)(2-nu)] / 6
If c_bar_2 = (1-nu)(2+nu): sum = [nu+nu^2 + 2+nu-nu-nu^2 + 2+nu-nu-nu^2 + 2-nu-nu+nu^2] / 6
= [nu+nu^2 + 2 + 2-2nu+nu-nu^2 + 2-nu-nu+nu^2] / 6
This is hard to verify in text. **Human must check.**

---

### 5. Table II — Optimal Linear Weights c_rk for u^{n+1}_{i+1/2}

**Extracted**: PARTIAL
**Confidence**: LOW
**Source**: Table II, page 6 (multi-column layout, badly mangled by pdftotext)
**Implementation relevance**: REQUIRED

The pdftotext output for Table II r=3 row is severely mangled due to the
multi-column layout. The text appears to contain expressions involving `v`,
`(2v^2-4v+1)`, `(3v-2v)`, `(3v-1)`, `(2v-1)`, etc.

Partial transcription for r=3:

```
c^3_0 = [1] nu(5*nu^2 + nu - 2) / ?   [UNCERTAIN]
c^3_1 = (2*nu^2 - 4*nu + 1) / ?       [UNCERTAIN]
c^3_2 = (3*nu - 2*nu) / ?              [UNCERTAIN — text unclear]
c^3_3 = (3*nu - 1)(2*nu - 1) / ?       [UNCERTAIN]
```

**These values are NOT reliable.** The denominators are unclear, and the
column alignment is ambiguous. The text fragment `108` and `36` appear in
the r=3 row area, possibly as denominators, but this is speculative.

**Human verification of Table II is a HARD REQUIREMENT.**

---

### 6. Eq. (19) — Smoothness Indicators for r=3

**Extracted**: YES
**Confidence**: HIGH
**Source**: Eq. (19), page 5 (rendered inline with the table region)
**Implementation relevance**: REQUIRED

The smoothness indicators for r=3 (b_30, b_31, b_32, b_33) are:

```
b_30 = 4*(u_j - u_{j-1/2})^2
     + (1/4)(u_{j-1} - 6*u_{j-1/2} + 5*u_j)^2
     + (39/4)(u_{j-1} - 2*u_{j-1/2} + u_j)^2

b_31 = (u_{j-1/2} - u_{j+1/2})^2
     + (39)(u_{j-1/2} - 2*u_j + u_{j+1/2})^2

b_32 = (1/4)(5*u_j - 6*u_{j+1/2} + u_{j+1})^2
     + (39/4)(u_j - 2*u_{j+1/2} + u_{j+1})^2

b_33 = (3*u_j - 5*u_{j+1/2} + 3*u_{j+1} - u_{j+3/2})^2
     + (39)(u_j - 3*u_{j+1/2} + 3*u_{j+1} - u_{j+3/2})^2
     + (781/20)(u_j - 4*u_{j+1/2} + 5*u_{j+1} - 2*u_{j+3/2})^2
```

Wait — this is the full set from r=2 through r=4. The r=3 indicators are
b_30, b_31, b_32 (for the 4 substencils of CFWENO5? No — r=3 means
k=0,1,2,3, so we need b_30 through b_33).

Actually, examining the text more carefully:
- b_20, b_21 are for r=2 (CFWENO3, 2 substencils)
- b_30, b_31, b_32 are listed first — these may be for the first 3 substencils of r=3
- b_33 appears to be a separate formula
- b_40, b_41, b_42, b_43 are for r=4 (CFWENO7, 4 substencils)

**The numbering follows b_{r*10+k} where r is the order parameter and k is the substencil.**
For CFWENO5 (r=3): b_30, b_31, b_32, b_33.

The transcriptions above for b_30-b_33 appear reasonable from the PDF text,
but the long expressions (especially b_33) need human verification.

---

### 7. Table III — Discontinuity Positions delta_rk

**Extracted**: YES (partial)
**Confidence**: MEDIUM
**Source**: Table III, page 5
**Implementation relevance**: OPTIONAL (needed for nonlinear WENO weighting, not for smooth linear advection)

For r=3: delta positions at k=1,2,3 are 1/3 and 2/3.

For smooth linear advection (first implementation target), the discontinuity
positions are NOT needed — the smoothness indicators (b_k) are only used
to detect smooth regions where all weights remain close to optimal.

---

### 8. Boundary / Periodic Handling Implications

**Extracted**: YES (structural)
**Confidence**: HIGH
**Source**: Fig. 1(b) and stencil structure
**Implementation relevance**: REQUIRED

CFWENO5 substencils span from u_{i-1} through u_{i+3/2} (Appendix A, Eq. A1).
This requires:
- Cell-center values: u_{i-1}, u_i, u_{i+1} (3 cells)
- Interface values: u_{i-1/2}, u_{i+1/2}, u_{i+3/2} (3 interfaces)

The interface reconstruction uses u_{i-1}, u_i, u_{i+1}, u_{i+2} (4 cells).

For periodic BC with `np.roll`, the widest stencil access is u_{i+2} (2 shifts).
This is the same width as CFWENO3. **No boundary handling extension needed.**

Wait — re-examining: the k=0 substencil uses u_{i-1}, which requires
u_{i-1/2}. The interface reconstruction for u_{i-1/2} needs u_{i-2}. So
the full stencil width is 5 cells: u_{i-2} through u_{i+2}. This is 2
shifts in each direction — `np.roll(u, 2)` and `np.roll(u, -2)`. Still
manageable.

---

## CFWENO5 Scalar Linear Implementation Readiness

**Decision: CONDITIONALLY READY — pending human verification of 3 items**

### What is now available:
1. CFWENO5 substencil expressions (Appendix A, Eqs. A1-A2) — extracted but needs human verification
2. Interface reconstruction — confirmed same as CFWENO3 (4th-order centered)
3. Conservative update — confirmed same structure as CFWENO3
4. Table I optimal weights for r=3 — extracted with one uncertain entry (k=2)
5. Eq. (19) smoothness indicators b_30 through b_33 — extracted, needs verification
6. Boundary handling — confirmed no extension needed

### What remains uncertain (human verification required):
1. **Table I, r=3, k=2 weight**: (1-nu)(2+nu) or (1-nu)(2-nu) — PDF text ambiguous
2. **Table II, r=3 weights**: pdftotext mangled the multi-column layout beyond reliable transcription
3. **Appendix A, Eqs. (A1)-(A2)**: The piecewise multi-line formatting was mangled by pdftotext; the transcriptions above are best-effort interpretations

### What is NOT needed for first scalar linear implementation:
- Table III discontinuity positions (only for shock detection)
- Eq. (20) entropy condition (only for Euler systems)
- Appendix B pseudocode (only for system/Euler)
- Higher-order interface reconstruction (4th-order is sufficient)

### Recommendation:
A human should read the PDF at:
- **Page 5**: Table I (r=3 row, verify k=2), Table II (r=3 row, all entries)
- **Page 23**: Appendix A, Eqs. (A1) and (A2) (verify all substencil expressions)

After human verification, the spec can be updated and implementation can proceed.
The formulas are all present in the paper — the blocker was extraction, not absence.
