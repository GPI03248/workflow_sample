# CFWENO5 Scalar Prototype — Failed Implementation Diagnostic

**Date**: 2026-05-26
**Task**: v1.3 — scalar CFWENO5 implementation attempt
**Status**: **NOT ACCEPTED** — implementation failed validation

---

## Task Summary

Attempted to implement a 1D scalar linear advection CFWENO5 prototype from
the approved subset spec `docs/scheme_specs/cfweno5_scalar_subset.md`.

The paper source is Zhou-Dong-Pan (2025), *Physics of Fluids* 37, 106131.
Appendix A provides CFWENO5 (r=3) substencil expressions, and Table I
provides optimal linear weights.

Implementation used the Appendix A Eq. (A1) substencils (k=0,1,2,3)
combined with Table I optimal weights, following the substencil-decomposition
pattern validated for CFWENO3.

---

## Expected Result

- **CFWENO5 convergence order**: ~5.0 (or at minimum > 4.0 for acceptance)
- **CFWENO5 error**: lower than CFWENO3 at nx >= 80
- **CFWENO3 convergence order**: ~3.0 (regression check — unchanged)

---

## Observed Result

### Multi-step convergence (CFL=0.5, T=0.25, u_t + u_x = 0, sin(2πx)+1)

| Scheme | nx=40 | nx=80 | nx=160 | nx=320 | Observed Order |
|--------|-------|-------|--------|--------|----------------|
| CFWENO3 | 2.329e-05 | 2.830e-06 | 3.512e-07 | 4.382e-08 | **~3.0** |
| CFWENO5 | 2.690e-03 | 1.358e-03 | 6.807e-04 | 3.406e-04 | **~1.0** |

- **CFWENO5 observed order**: ~1.0 (not 5.0, not even 2.0)
- **CFWENO5 error at nx=40**: 2.690e-03 — **115x worse** than CFWENO3 (2.329e-05)
- **CFWENO3 regression**: unchanged at ~3.0 order

### Single-step diagnostics (one time-step, same IC)

Individual substencil convergence order (CFL=0.5):

| Substencil | CFWENO3 (r=2) | CFWENO5 (r=3, as-extracted) |
|------------|---------------|------------------------------|
| s0 (left)  | ~3.0 | ~3.0 |
| s1 (center) | ~4.0 | ~4.0 |
| s2 (right) | ~3.0 | **~2.0** |
| s3 (full)  | N/A | ~4.0 (unverified) |

The CFWENO5 s2 substencil achieves only 2nd order, while CFWENO3 s2 achieves
3rd order. The combined scheme degrades to 1st order globally.

---

## Suspected Root Cause

**Appendix A Eq. (A1) substencil formula transcription error.**

The pdftotext-based extraction of the s2 substencil appears to contain a
misplaced coefficient. The extracted s2 is:

```
ubar^3_{i+1/2,2} = u_i + (1/2)(1-nu)(u_{i+1/2} - u_i)
                   + (1-nu)(-nu)(u_i - 2*u_{i+1/2} + u_{i+1})
```

The factor `(1/2)` on the first correction term (1-nu)(u_hr - u) is
suspicious. In the CFWENO3 (r=2) counterpart, this factor is 1, not 1/2.
The left-biased substencil s0 has the full factor (not 1/2) on its first
correction term. This asymmetry is likely a pdftotext transcription artifact.

Moving the 1/2 factor to the second correction term (producing a reflected
version of s0's structure) improves s2 to 4th order individually, but the
full 4-substencil combination still only achieves 3rd order — same as
CFWENO3. This strongly suggests additional errors exist in the extraction.

### Why 3rd order at best? (even with corrected s2)

The 4-substencil combination with corrected s2 converges at exactly 3rd
order regardless of interface reconstruction order (tested both 4th and
6th order). This indicates the substencil formulas as a whole are
incomplete or incorrect for achieving 5th-order accuracy. The WENO
combination of substencils cannot cancel error terms that are not
represented in any substencil.

---

## Modified Files During Attempt

### Created (to be removed):
| File | Purpose |
|------|---------|
| `solver/cfweno_scalar.py` | CFWENO5 scheme module (failing) |
| `examples/run_cfweno5_scalar_demo.py` | CFWENO5 demo (failing) |
| `examples/run_cfweno5_scalar_convergence.py` | CFWENO5 convergence study (failing) |
| `tests/test_cfweno5_scalar.py` | CFWENO5 tests (many fail) |
| `docs/tasks/cfweno5_scalar_prototype/traceability.md` | Task traceability (pre-emptive) |

### Modified (to be reverted):
| File | Change |
|------|--------|
| `solver/schemes.py` | Added `from solver.cfweno_scalar import cfweno5` and `"cfweno5": cfweno5` in `_SCHEMES` |
| `Makefile` | Added `cfweno5-scalar-demo`, `cfweno5-scalar-convergence`, `demo-cfweno5-scalar` targets |
| `tools/summarize_validation_results.py` | Added cfweno5 result directories |

### NOT modified:
- `cfd/` — no changes
- `v1.0` tag — unchanged at `42d97ee`

---

## Key Diagnostic Commands

```bash
# Multi-step convergence
tools/run_in_project_env.sh python examples/run_cfweno5_scalar_convergence.py

# Single-step order check
python -c "
from solver.simulate import run_advection, compute_errors
import math
for nx in [40,80,160,320]:
    res = run_advection('cfweno5', nx=nx, cfl=0.5, final_time=0.25)
    print(f'nx={nx} L2={compute_errors(...)}')"
```

---

## Recommendation

**Return to formula verification before any new implementation attempt.**

1. Re-read the paper's Appendix A directly from the PDF (not pdftotext)
2. Verify all substencil coefficients character-by-character against the
   printed PDF
3. Pay special attention to s2: where does the 1/2 factor belong?
4. Verify Table I weights against the paper (not pdftotext)
5. Verify k=3 weight: is `(2-nu)(1+nu)/6` the correct derived value?
6. Consider whether CFWENO5 requires a higher-order interface reconstruction
   or different substencil structure than what was extracted
7. Update the extraction report at
   `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md`
8. Re-run formula confidence checks after correction

---

## Conclusion

**CFWENO5 implementation is NOT accepted.** The numerical evidence shows
approximately 1st-order convergence, not the expected 5th order.
The failing code must be reverted. A new implementation attempt should
only begin after the Appendix A substencil formulas are re-verified
against the paper PDF at full resolution.

## Related Documents

- Spec: `docs/scheme_specs/cfweno5_scalar_subset.md` (approved, but formulas are wrong)
- Extraction: `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md`
- Formula inventory: `docs/formula_inventories/cfweno5_scalar_formulas.yml`
- Feasibility: `docs/feasibility/cfweno5_scalar_readiness.md`
- Roadmap: `docs/roadmaps/v1_real_paper_demo.md`
