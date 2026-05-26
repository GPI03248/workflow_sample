# Feasibility Review: Scalar CFWENO5 Readiness

**Date**: 2026-05-26
**Based on**: v1.0 tag `42d97ee`, Burgers order recovery commit `4d671c0`
**Decision**: **Conditionally ready** (updated after formula extraction)

---

## Is Scalar CFWENO5 Ready?

**Decision: CONDITIONALLY READY — human verification of 3 items required**

All CFWENO5 formulas have been located and extracted from the paper. The primary
blocker (formulas not extracted) is resolved. However, pdftotext mangled critical
multi-column table entries and multi-line piecewise formulas, so human reading
of specific PDF pages is required before implementation.

See `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md` for full details.
formulas to be transcribed and approved before implementation begins.

---

## Available Assets

| Asset | Location | Status |
|-------|----------|--------|
| CFWENO3 scalar infrastructure | `solver/schemes.py` | Working, extensible |
| CFWENO3 convergence framework | `examples/run_cfweno_scalar_convergence.py` | Reusable |
| CFWENO3 linear advection spec | `docs/scheme_specs/cfweno_scalar_subset.md` | Approved, pattern to follow |
| Paper extraction report | `docs/paper_reviews/cfweno_pof_2025/extraction_report.md` | CFWENO3 only |
| Dependency register | `docs/papers/cfweno_dependency_register.md` | Lists r=3 weights as existing |
| Approval gate tool | `tools/check_scheme_spec_approval.py` | Ready |
| Validation index generator | `tools/summarize_validation_results.py` | Ready |
| Linear advection analytic solution | Exact: `u(x,t) = sin(2*pi*(x-a*t)) + 1` | Available |
| WENO weight machinery (Eq. 17) | General, order-independent | Available |
| Cost/performance data | Tables V, VII, VIII in extraction report | Available |

---

## Missing or Risky Parts

### Critical Blockers

1. **CFWENO5 stencil formula not extracted.** The extraction report only covers
   Eq. (30), the 3rd-order stencil. The paper must contain a 5th-order stencil
   generalization, but it was never transcribed. Without this formula, no
   implementation is possible.

2. **Table I optimal weights for r=3 not transcribed.** The dependency register
   confirms Tables I-II provide weights for r=2,3,4, but only r=2 values are in
   the repo. The CFWENO5 implementation needs the exact r=3 coefficient values.

3. **Table II next-time-level weights for r=3 not transcribed.** Same situation.

4. **Eq. (19) smoothness indicators not expanded for r=3.** The general formula
   is known, but the specific polynomial expressions for the 5th-order substencil
   case have not been written out.

5. **Appendix A content not extracted.** No Appendix A content exists anywhere
   in the repo. The appendix likely contains the expanded stencil formulas and
   complete coefficient tables. This is a significant extraction gap.

### Risky (Not Blockers)

6. **Appendix A formula transcription risk.** Even if Appendix A is extracted,
   higher-order stencils involve more coefficients and wider polynomial
   expressions, increasing the chance of transcription errors. Verification
   against the paper's numerical results will be essential.

7. **Interface reconstruction order.** CFWENO3 uses 4th-order centered
   interpolation. CFWENO5 may require 6th-order reconstruction. Whether the
   paper provides this or it must be derived separately is unknown.

8. **solver/schemes.py extensibility.** The current 232-line file can
   accommodate CFWENO5 but would grow significantly. A refactor to
   `solver/cfweno_scalar.py` might be warranted before adding CFWENO5.
   This is a style decision, not a blocker.

9. **Risk of conflating CFWENO5 scalar with full paper reproduction.** CFWENO5
   scalar linear advection is a narrow subset. The paper's CFWENO5 includes
   Euler system, 2D, and shock-capturing capabilities that are NOT in scope.
   Clear scoping is essential to avoid scope creep.

10. **Long polynomial coefficients.** CFWENO5 stencil coefficients will be
    longer and more complex than CFWENO3. Hard-coding them is feasible but
    error-prone. Testing against published numerical results is the only
    reliable verification.

---

## Refactor Recommendation

### Option A: Continue adding to `solver/schemes.py`

- Pros: Simple, follows existing pattern, no file restructuring
- Cons: File grows to ~350+ lines, CFWENO3/5/7 helpers mixed with upwind/LW

### Option B: Create dedicated `solver/cfweno_scalar.py`

- Pros: Clean separation, CFWENO-specific helpers grouped together,
  easier to test and review stencil coefficients
- Cons: Requires moving `_cfweno3_stencil`, `_interface_reconstruction`,
  `cfweno_burgers` to the new module; existing tests and examples need
  import path updates

### Recommendation: **Option B — refactor to `solver/cfweno_scalar.py`**

The refactor should be done **before** CFWENO5 implementation, as a separate
preparatory task. It keeps the growing number of CFWENO functions together
and makes coefficient verification easier. The existing `upwind`, `lax_wendroff`,
and `step()` functions remain in `solver/schemes.py`.

Suggested module structure:
```
solver/schemes.py          — upwind, lax_wendroff, step(), _SCHEMES
solver/cfweno_scalar.py    — cfweno, cfweno_burgers, cfweno5 (future)
                              _interface_reconstruction
                              _cfweno3_stencil, _cfweno5_stencil (future)
```

But: **this refactor should not be done as part of this readiness task.**
It should be a separate pre-implementation task after approval.

---

## Path Forward

1. **Re-read the paper** at pages containing:
   - The CFWENO5 stencil generalization (likely near Eq. 30 or in Appendix A)
   - Tables I and II for r=3 weight values
   - Eq. (19) expanded for r=3 substencils
   - Any higher-order interface reconstruction formulas

2. **Update the extraction report** with the new CFWENO5 formulas.

3. **Update this spec** (`docs/scheme_specs/cfweno5_scalar_subset.md`) with
   the transcribed formulas.

4. **Verify** that the extracted formulas are internally consistent.

5. **Change approval to yes** after all blockers are resolved.

6. **Refactor** solver helpers into `solver/cfweno_scalar.py` (separate task).

7. **Implement** CFWENO5 linear advection.

---

## Estimated Effort

| Step | Effort | Risk |
|------|--------|------|
| Paper re-reading and extraction | Medium | Medium (transcription accuracy) |
| Spec update with formulas | Low | Low |
| Verification | Low | Low |
| Solver refactor | Low | Low |
| CFWENO5 implementation | Medium | Medium (coefficient errors) |
| Validation | Low | Low |

The highest-risk step is formula extraction — a single transcription error in
a stencil coefficient can cause convergence failure that is hard to diagnose.

---

## Formula Extraction Update (2026-05-26)

**Extraction report**: `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md`

### What was extracted

1. **Appendix A, Eqs. (A1)-(A2)**: CFWENO5 substencil expressions for r=3
   with 4 substencils (k=0,1,2,3). Both initial-value and next-time-level
   reconstructions are provided. **Confidence: MEDIUM** — pdftotext mangled
   multi-line piecewise formatting.

2. **Table I optimal weights for r=3**: All 4 weights extracted. k=0,1,3 are
   clear; k=2 is ambiguous between `(1-nu)(2+nu)` and `(1-nu)(2-nu)`.
   **Confidence: HIGH** (except k=2).

3. **Table II weights for r=3**: The multi-column layout was severely mangled.
   Partial expressions visible but denominators unclear.
   **Confidence: LOW** — hard requirement for human verification.

4. **Eq. (19) smoothness indicators b_30-b_33**: All 4 extracted with coefficients.
   b_33 has complex multi-term expression with coefficient 781/20.
   **Confidence: MEDIUM**.

5. **Interface reconstruction**: Confirmed same 4th-order centered as CFWENO3.
   **Confidence: HIGH**.

6. **Boundary handling**: Stencil width 5 cells, `np.roll(±2)` sufficient.
   **Confidence: HIGH**.

### What remains uncertain

1. Table I, r=3, k=2 weight value
2. Table II, r=3, all 4 weight values
3. Appendix A, Eqs. (A1)-(A2) substencil coefficients

### Whether blockers remain

**Partially** — all formulas are now located in the paper and have been
extracted at medium-to-low confidence. The remaining blocker is **verification
accuracy**, not formula absence.

### Whether implementation can proceed after human review

**Yes, conditionally** — after a human verifies the 3 uncertain items by
reading pages 5, 6, and 23 of the PDF, implementation can proceed.

### Whether helper refactor is recommended before implementation

**Yes** — recommend refactoring to `solver/cfweno_scalar.py` as a separate
preparatory task before CFWENO5 implementation. This keeps CFWENO5 stencil
coefficients separate from the existing upwind/Lax-Wendroff/step infrastructure.

### Updated Readiness Decision

**CONDITIONALLY READY** — human must verify 3 items in the PDF:
1. Page 5: Table I row r=3, column k=2
2. Page 6: Table II row r=3, all columns
3. Page 23: Appendix A, Eqs. (A1) and (A2)

After verification, the spec can be approved and implementation can begin.
