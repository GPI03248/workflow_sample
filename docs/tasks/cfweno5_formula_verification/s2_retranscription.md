# Appendix A s2 Substencil Re-Transcription

**Date**: 2026-05-27
**Task**: v1.3-pre.8 — Re-transcribe Appendix A Eq. (A1) s2 substencil
**Method**: pdftotext -layout character-level analysis (image rendering unavailable)
**Confidence of this correction**: MEDIUM-HIGH (based on layout structure analysis; NOT visual PDF reading)

---

## Source

- **PDF**: `.local/papers/cfweno_pof_2025.pdf`, page 24 (journal numbering: page 23)
- **Section**: Appendix A, Eq. (A1) — 4-substencil braced piecewise expression
- **Extraction tool**: `pdftotext -f 24 -l 25 -layout`

---

## pdftotext Evidence

### Full Eq. (A1) braced section (pdftotext -layout, lines 66-91)

The brace renders four substencils with fraction coefficients offset to the right:

```
s0 (k=0): u^3_{i+1/2,0} = ui + (1-v)(ui - ui-1/2)
                         + 1/2 (1-v)(ui-1 - 2ui-1/2 + ui)      [1/2 on 2nd term]

s1 (k=1): u^3_{i+1/2,1} = ui + (1-v)(ui+1/2 - ui)
                         + (1-v)(-v)(ui-1/2 - 2ui + ui+1/2)     [no 1/2]

s2 (k=2): u^3_{i+1/2,2} = ui + (1-v)(ui+1/2 - ui)
                         + 1/2 (1-v)(-v)(ui - 2ui+1/2 + ui+1)   [1/2 on 2nd term]

s3 (k=3): u^3_{i+1/2,3} = ui + (1-v)(ui+1/2 - ui)
                         + 1/2 (1-v)(-v)(ui - 2ui+1/2 + ui+1)   [1/2 on 2nd term]
                         + 1/4 (1-v)(-v)(1+v)(2ui-1/2 - 5ui + 4ui+1/2 - ui+1)
                         + 1/12 (1-v)^2(-v)(1+v)(-ui-1 + 6ui-1/2 - 10ui + 6ui+1/2 - ui+1)
```

### Key observation

The `1/2` fraction in pdftotext -layout appears as orphaned numerator/denominator lines
(`1` and `2` on separate lines) at the same visual column position for BOTH s0 and s2.
This column is located AFTER the first correction term and BEFORE the second —
it applies to the SECOND correction term for both substencils.

The current extraction placed the `1/2` on the FIRST correction term of s2, which
disagrees with the visual column position.

---

## Correction

### Before (current extraction)
```
ubar^3_{i+1/2,2} = u_i + (1/2)(1-nu)(u_{i+1/2} - u_i)
                         + (1-nu)(-nu)(u_i - 2*u_{i+1/2} + u_{i+1})
```

### After (corrected)
```
ubar^3_{i+1/2,2} = u_i + (1-nu)(u_{i+1/2} - u_i)
                         + (1/2)(1-nu)(-nu)(u_i - 2*u_{i+1/2} + u_{i+1})
```

### Structural support

This correction makes s2 structurally symmetric with s0 (both have 1/2 on the
second correction term) and symmetric with s1 (both have (1-nu) on the first
correction term, no fractional coefficient):

| Sub | First term coeff | Second term coeff | Pattern |
|-----|-----------------|-------------------|---------|
| s0  | (1-nu)          | 1/2 (1-nu)       | Left-biased, 1/2 on 2nd |
| s1  | (1-nu)          | (1-nu)(-nu)      | Centre-biased, no 1/2 |
| s2  | (1-nu)          | 1/2 (1-nu)(-nu)  | Right-biased, 1/2 on 2nd |
| s3  | (1-nu)          | 1/2 (1-nu)(-nu)  | Full-stencil, 1/2 on 2nd |

The correction restores consistency: s0, s2, and s3 all have 1/2 on their
second correction terms.

---

## Python equivalent

```python
def _substencil_s2(u, nu, u_half_right, u_half_left):
    """Appendix A Eq. (A1), k=2: right-biased substencil (CORRECTED 2026-05-27)."""
    u_ip1 = np.roll(u, -1)
    omnu = 1.0 - nu
    return (u
            + omnu * (u_half_right - u)
            + 0.5 * omnu * (-nu) * (u - 2.0 * u_half_right + u_ip1))
```

---

## Remaining Uncertainty

This correction is based on pdftotext -layout column-position analysis, NOT on
direct visual reading of the rendered PDF. While the structural evidence is
strong (s0, s2, s3 all follow the same 1/2-on-second-term pattern), this should
ideally be confirmed by a human reading the PDF page at full resolution.

**Acceptance criterion**: If the corrected s2 achieves ~4th-order convergence
individually (single-step test via `make cfweno5-formula-consistency`), the
correction is numerically validated.

---

## Files to Update

| File | Change |
|------|--------|
| `docs/formula_inventories/cfweno5_scalar_formulas.yml` | Update appendix_A_eq_A1 expression/notes with corrected s2 |
| `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md` | Update s2 formula in Section 1 with correction note |
| `tools/check_cfweno5_formula_consistency.py` | Fix `_substencil_s2()` — move 0.5 from first to second term |
| `docs/scheme_specs/cfweno5_scalar_subset.md` | Update s2 formula if listed |
| `docs/feasibility/cfweno5_scalar_readiness.md` | Note s2 correction |
| `docs/tasks/cfweno5_scalar_readiness/traceability.md` | Record s2 correction |
| `docs/roadmaps/v1_real_paper_demo.md` | Note s2 correction |
