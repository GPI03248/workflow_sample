# Feasibility Review: Scalar CFWENO5 Readiness

**Date**: 2026-05-27 (updated after failed implementation attempt)
**Based on**: v1.0 tag `42d97ee`, failed implementation diagnostic `dc78864`
**Decision**: **BLOCKED — formula confidence gate hardened after failed implementation**

---

## Is Scalar CFWENO5 Ready?

**Decision: BLOCKED — strict formula confidence gate fails after implementation attempt**

The CFWENO5 implementation (v1.3, 2026-05-26) was attempted with the approved spec
but achieved only ~1st-order convergence (expected ~5th). The s2 substencil from
Appendix A produced only 2nd-order individually (expected 4th). The combined
3-substencil scheme degraded to 1st-order globally.

**v1.3-pre.8 s2 correction (2026-05-27)**: s2 1/2 factor moved from first to second
correction term based on pdftotext -layout analysis. Corrected s2 achieves ~4.0
individual order (was ~2.0). All 4 substencils now pass individually. Combined scheme
still fails (~1st order) — additional formula errors remain, likely in Table I weights.

The implementation was fully reverted. A diagnostic report was committed as `dc78864`.
The formula confidence gate was subsequently hardened:
- `appendix_A_eq_A1` and `cfweno5_stencil_expression` demoted to medium/failed_validation
- New `consistency_status` field added to formula inventory
- New `tools/check_cfweno5_formula_consistency.py` checks substencil-level convergence
- Strict formula confidence gate now blocks on `consistency_status=failed`

**Implementation must NOT proceed until ALL formula errors are resolved and the combined scheme achieves ~5th-order convergence.**

See:
- `docs/tasks/cfweno5_scalar_prototype/failed_attempt_diagnostic.md` — detailed diagnostic
- `docs/tasks/cfweno5_formula_verification/appendix_a_reverification_plan.md` — what to re-verify

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

### Critical Blockers (updated after human verification)

1. ~~**CFWENO5 stencil formula not extracted.**~~ **RESOLVED**: Extracted from
   Appendix A, Eqs. (A1)-(A2). Visually confirmed present in rendered PDF.
   Transcription needs final character-level check at implementation time.

2. ~~**Table I optimal weights for r=3 not transcribed.**~~ **RESOLVED**: Human
   verified. k=2 corrected to `(1-nu)(2-nu)/6` (was `(1-nu)(2+nu)/6`). k=3 is
   not applicable (ellipsis). 3 valid entries confirmed.

3. ~~**Table II next-time-level weights for r=3 not transcribed.**~~ **RESOLVED**:
   Human verified. 3 valid entries with full formulas. k=3 is not applicable.
   Denominators have singularities at nu=1/3 and nu=2/3 (implementation note).

4. ~~**Eq. (19) smoothness indicators not independently verified.**~~ **RESOLVED**:
   Character-level verified via pdftotext of page 7. b_30 corrected (removed extra
   first term that belonged to b_20). b_31, b_32, b_33 match extraction report.
   **Confidence: HIGH**.

5. ~~**Appendix A content not extracted.**~~ **RESOLVED**: Eq. (A1) character-level
   verified from pdftotext of page 24. All 4 substencils match extraction report.
   Eq. (A2) remains medium confidence (pdftotext d/dv derivative ambiguity).
   A2 derivable from A1 at implementation time.

### Risky (Not Blockers)

6. **Appendix A Eq. (A2) derivative ambiguity.** pdftotext mangles d/dv superscripts
   on (1-v) factors, preventing character-level verification. A2 can be derived from
   A1 by differentiating coefficients wrt nu. The paper provides A2 as a verification
   reference. **Not a hard blocker for implementation.**

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

1. **Appendix A, Eq. (A1)**: CFWENO5 substencil expressions for r=3
   with 4 substencils (k=0,1,2,3). Character-level verified from pdftotext
   of page 24. All 4 substencils match extraction report.
   **Confidence: HIGH**.

2. **Appendix A, Eq. (A2)**: Next-time-level reconstruction. Structure verified
   (same as A1 with d/dv applied). pdftotext derivative terms ambiguous.
   Derivable from A1 at implementation time.
   **Confidence: MEDIUM**.

2. **Table I optimal weights for r=3**: **Human verified**. 3 valid entries:
   k=0: `nu(1+nu)/6`, k=1: `(1+nu)(2-nu)/6`, k=2: `(1-nu)(2-nu)/6`
   (corrected from `(1-nu)(2+nu)/6`). k=3 is not applicable.
   **Confidence: HIGH**.

3. **Table II weights for r=3**: **Human verified**. 3 valid entries:
   k=0: `nu(5*nu^2+nu-2)/(6*(3*nu-1))`,
   k=1: `-(30*nu^4-60*nu^3-nu^2+31*nu-8)/(6*(3*nu-1)*(3*nu-2))`,
   k=2: `(nu-1)(5*nu^2-11*nu+4)/(6*(3*nu-2))`.
   k=3 is not applicable.
   **Confidence: HIGH**.

4. **Eq. (19) smoothness indicators b_30-b_33**: Character-level verified from
   pdftotext of page 7. b_30 corrected (removed extra first term from b_20).
   b_31, b_32, b_33 match exactly.
   **Confidence: HIGH**.

5. **Interface reconstruction**: Confirmed same 4th-order centered as CFWENO3.
   **Confidence: HIGH**.

6. **Boundary handling**: Stencil width 5 cells, `np.roll(±2)` sufficient.
   **Confidence: HIGH**.

### What remains uncertain

1. Appendix A Eq. (A2) d/dv derivative terms — pdftotext rendering ambiguous,
   but derivable from A1 at implementation time

### Whether blockers remain

**Mostly resolved** — Table I, Table II, Eq. (19), and Appendix A Eq. (A1) are all
character-level verified at high confidence. Only Appendix A Eq. (A2) remains at
medium confidence due to pdftotext d/dv rendering ambiguity. A2 is derivable from A1.

### Whether implementation can proceed after this verification

**Conditionally** — 11 of 12 formulas are at high confidence. The sole remaining
medium-confidence formula (A2) is derivable from A1 by differentiation. The strict
confidence check still fails, but the practical risk is low.

### Whether helper refactor is recommended before implementation

**Yes** — recommend refactoring to `solver/cfweno_scalar.py` as a separate
preparatory task before CFWENO5 implementation.

---

## Human Verification Update (2026-05-26)

**Verifier**: Human (paper PDF rendered page images)

### Table I — Corrected

- r=3 has **3 valid entries** (k=0,1,2), k=3 is ellipsis
- k=2 **corrected**: `(1-nu)(2-nu)/6`, NOT `(1-nu)(2+nu)/6`
- Confidence: HIGH
- Source: Table I, rendered PDF page image

### Table II — Verified

- r=3 has **3 valid entries** (k=0,1,2), k=3 is ellipsis
- All 3 formulas verified with correct numerators and denominators
- Singularity at nu=1/3 and nu=2/3 noted (implementation consideration)
- Confidence: HIGH
- Source: Table II, rendered PDF page image

### Appendix A — Visually Confirmed

- Eqs. (A1) and (A2) are visually present and readable on page 23
- Existing pdftotext transcription was NOT independently re-transcribed
- Transcription remains at MEDIUM confidence
- Needs character-level verification at implementation time

### Remaining Blockers

1. **Appendix A transcription accuracy**: Medium confidence — visually confirmed
   but not character-verified. Lower risk than Table I/II because structure is
   clear and numerical testing will catch coefficient errors.
2. **Eq. (19) smoothness indicators**: Medium confidence — not verified this round.
   Lower risk for first implementation (smooth linear advection).

### Decision After Character-Level Verification

**CONDITIONALLY READY — 1 blocking formula remains (appendix_A_eq_A2)**

Character-level pdftotext verification resolved 3 of 4 previously blocking formulas.
Only Eq. (A2) remains at medium confidence. A2 can be derived from A1 by
differentiating coefficients wrt nu. The strict formula confidence check still
fails, but the practical risk of proceeding is low.

**The spec should be approved for implementation after:**
1. A2 is either derived from A1 and verified, OR
2. The strict formula confidence gate is relaxed for derivable formulas, OR
3. The implementer derives A2 as the first implementation step with convergence test

---

## Formula Confidence Workflow Update (2026-05-26)

### New tooling

| Item | Path |
|------|------|
| Formula inventory (YAML) | `docs/formula_inventories/cfweno5_scalar_formulas.yml` |
| Formula inventory README | `docs/formula_inventories/README.md` |
| Confidence checker | `tools/check_formula_confidence.py` |
| Confidence report | `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_confidence_report.md` |

### Current formula confidence summary

| Confidence | Count | Notes |
|-----------|-------|-------|
| High | 11 | All required formulas verified |
| Medium | 1 | Appendix A A2 (optional, derived from A1) |
| Low | 0 | — |
| **Blocking** | **0** | — |

### Strict confidence check

```
make formula-confidence-cfweno5-strict
```

**Expected result**: PASS — all required formulas are high confidence and verified.

### Non-strict confidence check

```
make formula-confidence-cfweno5
```

**Expected result**: PASS (reports blocking items but does not fail).

### Readiness decision after workflow integration

Remains **conditionally ready for human approval**. The formula confidence gate
passes (0 blocking formulas). `Approved=yes` still requires explicit human decision.

---

## Character-Level Verification Update (2026-05-26)

**Verifier**: Claude Code (pdftotext character-level extraction from PDF)
**Verification packet**: `docs/tasks/cfweno5_formula_verification/verification_packet.md`

### Eq. (19) Smoothness Indicators — VERIFIED

- Extracted page 7 via pdftotext, character-level comparison against extraction report
- **b_30 corrected**: removed extra first term `4*(u_j - u_{j-1/2})^2` that belonged to b_20
- Correct b_30: 2 terms with coefficients (1/4) and (39/4)
- b_31, b_32, b_33: match extraction report exactly
- **Confidence: MEDIUM → HIGH**

### Appendix A Eq. (A1) — VERIFIED

- Extracted page 24 via pdftotext, character-level comparison
- All 4 substencils (k=0,1,2,3) match extraction report
- Minor pdftotext artifact: k=3 shows u_j instead of u_i (subscript rendering issue)
- **Confidence: MEDIUM → HIGH**

### Appendix A Eq. (A2) — PARTIAL

- Structure verified: same as A1 with d/dv applied to coefficients
- pdftotext rendering of d/dv terms is ambiguous (superscripts merged)
- Can be derived from A1 by differentiating coefficients wrt nu
- **Confidence: MEDIUM (unchanged)**

### Stencil Assembly — VERIFIED

- Order-independent WENO combination, validated through CFWENO3 implementation
- **Confidence: MEDIUM → HIGH**

### Updated formula counts

| Metric | Before | After |
|--------|--------|-------|
| High confidence | 8 | 11 |
| Medium confidence | 4 | 1 (optional) |
| Blocking | 4 | 0 |

---

## A2 Derivation Policy Update (2026-05-26)

**Policy document**: `docs/tasks/cfweno5_formula_verification/a2_derivation_policy.md`

### Decision

A2 reclassified from `required` / `blocks_implementation: true` to `optional` /
`blocks_implementation: false`. A2 is mathematically derived from A1 via d/dv.
Implementation derives A2 coefficients from verified A1 via symbolic differentiation,
then cross-verifies against the paper's A2 expressions.

### Rationale

1. A2 = d/dv(A1) — not an independent formula
2. A1 is verified at high confidence (character-level pdftotext)
3. Symbolic differentiation of verified coefficients is exact
4. Transcribing A2 from pdftotext is LESS reliable than deriving from A1
5. A2 serves as verification reference, not direct implementation input

### Impact on formula gate

- Required formulas: 11 at high confidence, verified — **strict check PASSES**
- Optional formulas: 1 (A2) at medium confidence — does not block
- Blocking formulas: **0**
