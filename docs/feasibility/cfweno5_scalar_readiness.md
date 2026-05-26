# Feasibility Review: Scalar CFWENO5 Readiness

**Date**: 2026-05-26
**Based on**: v1.0 tag `42d97ee`, Burgers order recovery commit `4d671c0`
**Decision**: **Conditionally ready** (updated after human verification)

---

## Is Scalar CFWENO5 Ready?

**Decision: CONDITIONALLY READY — Appendix A transcription needs final character-level check**

Table I and Table II have been human-verified from rendered PDF page images.
Appendix A (Eqs. A1-A2) is visually confirmed present and readable, but the
pdftotext transcription was not independently re-transcribed by the human.
The remaining uncertainty is limited to the Appendix A substencil expressions.

See `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md` for full details.

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

4. **Eq. (19) smoothness indicators not independently verified.** The pdftotext
   extraction has medium confidence. Not part of this human verification round.
   Should be verified at implementation time.

5. ~~**Appendix A content not extracted.**~~ **RESOLVED**: Eqs. (A1)-(A2) extracted
   and visually confirmed. Transcription accuracy still medium confidence.

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
   reconstructions are provided. **Confidence: MEDIUM** — visually confirmed
   present, transcription not independently verified.

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

4. **Eq. (19) smoothness indicators b_30-b_33**: All 4 extracted with coefficients.
   b_33 has complex multi-term expression with coefficient 781/20.
   **Confidence: MEDIUM** — not independently verified.

5. **Interface reconstruction**: Confirmed same 4th-order centered as CFWENO3.
   **Confidence: HIGH**.

6. **Boundary handling**: Stencil width 5 cells, `np.roll(±2)` sufficient.
   **Confidence: HIGH**.

### What remains uncertain

1. Appendix A, Eqs. (A1)-(A2) substencil coefficients — transcription not
   independently character-verified against the rendered PDF
2. Eq. (19) smoothness indicators b_30-b_33 — not part of this verification round

### Whether blockers remain

**Partially** — Table I and Table II are fully resolved. Appendix A is visually
confirmed but transcription accuracy remains at medium confidence. Eq. (19) is
medium confidence but was not flagged for this verification round.

### Whether implementation can proceed after this verification

**Conditionally** — the two highest-risk items (Table I and Table II) are now
human-verified at high confidence. The remaining Appendix A uncertainty is
lower risk since the equations are visually confirmed present and the structure
is clear. A final character-level check at implementation time is recommended.

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

### Decision After Human Verification

**CONDITIONALLY READY — pending Appendix A final transcription check**

Table I and Table II (the highest-risk formula items) are now human-verified.
The remaining Appendix A uncertainty does not block readiness elevation to
"ready for human approval" — it can be resolved at implementation time with
a character-level comparison against the PDF. However, since the transcription
was not independently verified in this round, the conservative decision is to
remain at "conditionally ready" rather than "ready for human approval."

**The spec should be approved for implementation after:**
1. A human performs character-level transcription of Eqs. (A1)-(A2) from the
   rendered PDF, OR
2. The implementer does this check as the first implementation step, with a
   convergence test as immediate verification

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
| High | 8 | Table I (3), Table II (3), interface reconstruction (1), conservative update (1) |
| Medium | 4 | Appendix A A1, A2, Eq.19 smoothness, stencil assembly |
| Low | 0 | — |
| **Blocking** | **4** | All medium-confidence required formulas |

### Strict confidence check

```
make formula-confidence-cfweno5-strict
```

**Expected result**: FAIL — 4 required formulas have medium confidence.

### Non-strict confidence check

```
make formula-confidence-cfweno5
```

**Expected result**: PASS (reports blocking items but does not fail).

### Readiness decision after workflow integration

Remains **conditionally ready / blocked for approval**. The formula confidence
gate now enforces that `Approved=yes` cannot be set until the strict check passes.
