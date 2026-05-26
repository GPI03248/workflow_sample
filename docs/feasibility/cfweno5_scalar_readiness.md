# Feasibility Review: Scalar CFWENO5 Readiness

**Date**: 2026-05-26
**Based on**: v1.0 tag `42d97ee`, Burgers order recovery commit `4d671c0`
**Decision**: **Blocked**

---

## Is Scalar CFWENO5 Ready?

**Decision: BLOCKED — formula extraction required before implementation**

The CFWENO5 scalar linear advection prototype cannot proceed until the paper's
5th-order stencil formula, weight tables, and smoothness indicator polynomials
are extracted and verified. The project's paper-to-code workflow requires all
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
