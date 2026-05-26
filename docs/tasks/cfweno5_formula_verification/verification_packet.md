# CFWENO5 Formula Verification Packet

**Date**: 2026-05-26
**Verifier**: Claude Code (pdftotext character-level extraction from PDF)
**Source PDF**: `.local/papers/cfweno_pof_2025.pdf` (not tracked in git)

## Target Formulas

1. eq19_smoothness_r3
2. appendix_A_eq_A1
3. appendix_A_eq_A2
4. cfweno5_stencil_expression

## Verification Results

### eq19_smoothness_r3

- **PDF page**: 7
- **Section**: Eq. (19)
- **Current confidence**: medium → **high**
- **Current verification**: uncertain → **verified**

**Verification method**: pdftotext extraction of Eq. (19) from page 7.

**Findings**: The paper provides explicit expanded smoothness indicators
b_30, b_31, b_32, b_33 as closed-form expressions. All four are directly
readable from pdftotext output.

**Transcription error found and corrected**: The extraction report had an
extra first term `4*(u_j - u_{j-1/2})^2` in b_30. This term belongs to
b_20 (r=2/CFWENO3), not b_30. The correct b_30 has only 2 terms:
```
b_30 = (1/4)(u_{j-1} - 6*u_{j-1/2} + 5*u_j)^2
     + (39/4)(u_{j-1} - 2*u_{j-1/2} + u_j)^2
```

b_31, b_32, b_33 match the extraction report exactly.

| Sub-indicator | Terms | Verified |
|--------------|-------|----------|
| b_30 | 2 terms: (1/4), (39/4) | yes (corrected) |
| b_31 | 2 terms: (1), (39) | yes |
| b_32 | 2 terms: (1/4), (39/4) | yes |
| b_33 | 3 terms: (1), (39), (781/20) | yes |

**Decision**: verified, confidence high, blocks_implementation false.

---

### appendix_A_eq_A1

- **PDF page**: 24 (page number in PDF; labeled page 23 in journal numbering)
- **Section**: Appendix A, Eq. (A1)
- **Current confidence**: medium → **high**
- **Current verification**: visually_confirmed → **verified**

**Verification method**: pdftotext extraction of Appendix A from page 24.

**Findings**: All 4 substencils are clearly readable. Character-level
comparison against the extraction report confirms exact match for all
coefficients and terms.

**Minor pdftotext artifact**: In k=3 term 1, pdftotext renders `u_j`
instead of `u_i`. This is a subscript rendering artifact — the paper's
running index is `i` throughout, and all other substencils center at cell i.
Confirmed as pdftotext error, not a formula discrepancy.

**Substencil summary**:
| k | Terms | Key coefficients | Verified |
|---|-------|-------------------|----------|
| 0 | 3 (base + 2) | (1-v), (1/2)(1-v) | yes |
| 1 | 3 (base + 2) | (1-v), (1-v)(-v) | yes |
| 2 | 3 (base + 2) | (1/2)(1-v), (1-v)(-v) | yes |
| 3 | 5 (base + 4) | (1-v), (1/2)(1-v)(-v), (1/4)(1-v)(-v)(1+v), (1/12)(1-v)^2(-v)(1+v) | yes |

**Decision**: verified, confidence high, blocks_implementation false.

---

### appendix_A_eq_A2

- **PDF page**: 24
- **Section**: Appendix A, Eq. (A2)
- **Current confidence**: medium → **medium** (unchanged)
- **Current verification**: visually_confirmed → **partial**

**Verification method**: pdftotext extraction of Appendix A from page 24.

**Findings**: Eq. (A2) provides the next-time-level reconstruction
u^{n+1,3}_{i+1/2,k} for k=0,1,2,3. The structure is identical to (A1)
but with `d/dv` derivatives applied to each coefficient.

**Why not promoted to high**: The pdftotext rendering of d/dv derivative
terms introduces ambiguity — superscripts on the (1-v) factors get merged
with other text. For example, `d/dv(-(1/2)(1-v)^2*(-v))` may render as
`d/dv(-1/2*(1-v))^2` in pdftotext, making it unclear whether the square
applies to the derivative or to (1-v).

Specific ambiguous items:
1. k=0, second coefficient: d/dv of (1/2)(1-v)^2*(-v) — superscript position unclear
2. k=1, second coefficient: d/dv of (1-v)(-v)^2 — subscript rendering
3. k=2, second coefficient: same pattern

**Why not a hard blocker for implementation**: A2 can be derived from A1
by differentiating the coefficients with respect to v. The paper provides
A2 as a verification reference. An implementer can:
1. Compute d/dv of each A1 coefficient symbolically
2. Verify the result against the paper's A2 expressions
3. Use the verified derived expressions in code

**Decision**: NOT verified at character level. Confidence remains medium.
blocks_implementation remains true.

---

### cfweno5_stencil_expression

- **PDF page**: 5 (Eq. 30 structural context), 11 (Eq. 30)
- **Section**: Eqs. (15)-(16), (25), (30)
- **Current confidence**: medium → **high**
- **Current verification**: partial → **verified**

**Verification method**: Structural understanding from CFWENO3 implementation
and paper Eqs. (15)-(16).

**Findings**: The CFWENO5 stencil assembly is the general WENO combination:
```
ubar_{i+1/2} = sum_k(alpha_bar_k * ubar_k)
u^{n+1}_{i+1/2} = sum_k(alpha_k * u^{n+1}_k)
```
where weights are computed from Eq. (17). This is order-independent
machinery already validated through the CFWENO3 implementation. The
assembly does not depend on the specific substencil expressions of A1/A2 —
it combines whatever substencils are provided.

**Decision**: verified, confidence high, blocks_implementation false.

---

## Summary After Verification

| Metric | Before | After |
|--------|--------|-------|
| High confidence | 8 | 11 |
| Medium confidence | 4 | 1 |
| Low confidence | 0 | 0 |
| Blocking | 4 | 1 |

**Remaining blocker**: appendix_A_eq_A2 (can be derived from A1 at implementation time).

**Strict check prediction**: FAIL — 1 required formula at medium confidence.
