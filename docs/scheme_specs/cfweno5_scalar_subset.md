# Scalar CFWENO5 Subset — Scheme Spec

**Source**: Zhou-Dong-Pan (2025), Phys. Fluids 37, 106131
**Subset**: 1D scalar linear advection CFWENO5 prototype
Approved for implementation: no

**Human verification status**: Reverted 2026-05-27. After failed CFWENO5 implementation (observed ~1st order convergence, expected ~5th), Appendix A Eq. (A1) substencils and stencil assembly formulas demoted to medium/failed_validation.

**v1.3-pre.8 s2 correction (2026-05-27)**: The s2 substencil 1/2 factor was on the wrong correction term. Moved from first term `(1/2)(1-nu)(u_{i+1/2} - u_i)` to second term `(1/2)(1-nu)(-nu)(u_i - 2*u_{i+1/2} + u_{i+1})`. Corrected s2 now achieves ~4.0 individual order (was ~2.0). Combined 3-substencil scheme still fails (~1st order). See `docs/tasks/cfweno5_formula_verification/s2_retranscription.md`.

**v1.3-pre.9 weight role audit (2026-05-27)**: Comprehensive audit of Table I/Table II weight role and Eq. (17) normalization. Key findings: (1) Eq. (17) normalization IS missing from current checker — Table I provides `c_bar_rk` (alpha numerators), not final weights. (2) Normalization fixes ~1st→~3rd order but ALL weight variants (Table I normalized, Table II raw/normalized, equal weights) cap at ~3.0 — NOT 5th. (3) The ~3.0 ceiling is weight-independent: equal 1/3 weights give the same result as optimal weights. (4) This confirms Appendix A Eq. (A1) substencil polynomials have coefficient errors beyond normalization. See `docs/tasks/cfweno5_formula_verification/weight_role_audit.md`.

**Implementation readiness**: BLOCKED — strict formula confidence gate fails (2 blocking formulas with consistency_status=failed). See `docs/tasks/cfweno5_scalar_prototype/failed_attempt_diagnostic.md`.

---

## Scope

This spec covers the 5th-order scalar CFWENO prototype for 1D linear advection:

```
u_t + a * u_x = 0,  a = const > 0
```

Periodic boundary conditions on [0, 1).

**This is a readiness spec only.** Implementation is blocked pending approval
(see Approval Checklist).

---

## Relation to Existing CFWENO3

| Aspect | CFWENO3 (existing) | CFWENO5 (this spec) |
|--------|--------------------|--------------------|
| Formal order | 3 | 5 |
| Stencil width | 4 cells | ~6 cells (TBD) |
| Number of substencils | r+1 = 3 | r+1 = 4 (TBD) |
| Linear observed order | ~3.02 | Expected ~5 |
| Interface reconstruction | 4th-order centered | Higher order (TBD) |
| Status | Implemented, validated | Blocked |

CFWENO5 does **not** replace CFWENO3. It is a separate higher-order benchmark.
It does not affect Burgers, Euler, or 2D solvers.

---

## Formula Inventory

**Extraction report**: `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md`

The following formulas have been extracted from the paper. Items marked
NEEDS VERIFICATION require human reading of the PDF before implementation.

### 1. CFWENO5 Substencil Expressions — Appendix A, Eqs. (A1)-(A2)

Appendix A provides CFWENO5 (r=3) as an explicit example with 4 substencils.

**Eq. (A1)**: Character-level verified from pdftotext of page 24. All 4 substencils
match the extraction report. Minor pdftotext artifact: k=3 shows u_j instead of u_i
(subscript rendering issue, not a formula discrepancy).
**Status: VERIFIED — character-level pdftotext extraction**
**Confidence: HIGH**

**Eq. (A2)**: Structure verified (same as A1 with d/dv applied to coefficients).
pdftotext rendering of d/dv derivative terms introduces ambiguity — superscripts
on (1-v) factors get merged with other text. Can be derived from A1 by
differentiating coefficients wrt nu at implementation time.
**Status: PARTIALLY VERIFIED — derivative terms ambiguous in pdftotext**
**Confidence: MEDIUM**
**Source**: Appendix A, page 24 (PDF page number)

### 2. Optimal Linear Weights — Table I

For r=3 (CFWENO5), the weights are (3 valid entries, k=3 is ellipsis):
- k=0: `nu(1+nu) / 6`
- k=1: `(1+nu)(2-nu) / 6`
- k=2: `(1-nu)(2-nu) / 6` — **HUMAN VERIFIED**
- k=3: not applicable / ellipsis

**Status: HUMAN VERIFIED — all entries confirmed from rendered PDF page image**
**Confidence: HIGH**
**Source**: Table I, page 5

### 3. Next-Time-Level Weights — Table II

For r=3 (CFWENO5), the next-time-level weights are (3 valid entries, k=3 is ellipsis):
- k=0: `nu(5*nu^2 + nu - 2) / (6*(3*nu - 1))`
- k=1: `-(30*nu^4 - 60*nu^3 - nu^2 + 31*nu - 8) / (6*(3*nu - 1)*(3*nu - 2))`
- k=2: `(nu - 1)(5*nu^2 - 11*nu + 4) / (6*(3*nu - 2))`
- k=3: not applicable / ellipsis

**Note**: Denominators have singularities at nu = 1/3 and nu = 2/3.
Implementation must handle these limits.

**Status: HUMAN VERIFIED — all entries confirmed from rendered PDF page image**
**Confidence: HIGH**
**Source**: Table II, page 6

### 4. Smoothness Indicators — Eq. (19)

b_30 through b_33 for r=3 substencils, character-level verified from pdftotext
of page 7. b_30 corrected: original extraction had 3 terms (first term belonged
to b_20, not b_30); correct b_30 has 2 terms. b_31, b_32, b_33 match exactly.

| Sub-indicator | Terms | Coefficients |
|--------------|-------|-------------|
| b_30 | 2 terms | (1/4), (39/4) |
| b_31 | 2 terms | (1), (39) |
| b_32 | 2 terms | (1/4), (39/4) |
| b_33 | 3 terms | (1), (39), (781/20) |

**Status: VERIFIED — character-level pdftotext extraction, b_30 corrected**
**Confidence: HIGH**
**Source**: Eq. (19), page 7

### 5. WENO Nonlinear Weights — Eq. (17)

Order-independent, already available from CFWENO3 work.

**Status: AVAILABLE**

### 6. Interface Reconstruction

Confirmed: same 4th-order centered interpolation as CFWENO3.
`u_{i+1/2} = (-u_{i-1} + 7*u_i + 7*u_{i+1} - u_{i+2}) / 12`

**Status: CONFIRMED — no change needed**

### 7. Conservative Update

Same as CFWENO3: `u_i^{n+1} = u_i - cfl * (ubar_{i+1/2} - ubar_{i-1/2})`

**Status: AVAILABLE**

### 8. Periodic Boundary Handling

Stencil width is 5 cells (u_{i-2} through u_{i+2}), requiring `np.roll(u, ±2)`.
Manageable with current `np.roll` approach.

**Status: CONFIRMED — extends naturally**

---

## Intended Implementation Subset

### Phase 1 (this spec)

- 1D scalar linear advection only
- CFWENO5 stencil (when formulas become available)
- Periodic boundary conditions
- Convergence test against analytic solution
- Comparison with upwind, Lax-Wendroff, and CFWENO3
- No nonlinear Burgers
- No shock
- No Euler

### Phase 2 (future, not this spec)

- Burgers CFWENO5 (if linear convergence confirmed)
- Possible scalar CFWENO7

---

## Non-Goals

This spec explicitly does **NOT** cover:

- Burgers CFWENO5
- Euler CFWENO (1D or 2D)
- 2D CFWENO
- CFWENO7 (7th order)
- Post-shock validation
- WENO shock-capturing claims
- Production solver claims
- GPU/MPI/HPC
- Replacing CFWENO3

---

## Required Modules (If Later Approved)

If this spec is approved for implementation, the following would be needed:

1. **Possible refactor**: Extract scalar CFWENO helpers into `solver/cfweno.py`
   or `solver/cfweno_scalar.py` (recommended but not required)
2. **New functions**: `cfweno5()` in solver, `_cfweno5_stencil()`,
   possibly `_interface_reconstruction_6th()`
3. **Example scripts**: `examples/run_cfweno5_scalar_demo.py`,
   `examples/run_cfweno5_scalar_convergence.py`
4. **Tests**: `tests/test_cfweno5_scalar.py`
5. **Results directories**: `results/cfweno5_scalar_demo/`,
   `results/cfweno5_scalar_convergence/`
6. **Task traceability**: `docs/tasks/cfweno5_scalar_prototype/traceability.md`
7. **Validation index update**: add CFWENO5 results

---

## Validation Plan

When implemented, validation must include:

1. Smooth sine wave: `u_0 = sin(2*pi*x) + 1`, `a = 1.0`
2. Grid sizes: nx = 40, 80, 160, 320
3. Expected observed order: ~5.0 (if stencil formula is correct)
4. Reference: CFWENO5 fine-grid (nx=2560+) or analytic solution
5. Comparison methods: upwind (1st), Lax-Wendroff (2nd), CFWENO3 (~3rd)
6. Output: error_summary.csv, line_profile.csv, analysis.md
7. **If 5th order is not observed, STOP and audit** — do not proceed to Burgers

---

## Approval Checklist

- [x] CFWENO5 stencil formula extracted from paper (Appendix A, Eq. A1 character-level verified)
- [x] Table I optimal weights for r=3 transcribed and human-verified (3 entries, k=3 = N/A)
- [x] Table II weights for r=3 transcribed and human-verified (3 entries, k=3 = N/A)
- [x] Eq. (19) smoothness indicators expanded for r=3 substencils (b_30-b_33, character-level verified)
- [x] Interface reconstruction order requirement confirmed (4th-order centered, same as CFWENO3)
- [x] Periodic boundary stencil width verified (5 cells, np.roll +/-2)
- [ ] Helper refactor decision made
- [x] Validation plan accepted
- [x] Appendix A Eq. (A1) substencil transcription independently verified (character-level)
- [ ] Appendix A Eq. (A2) derivative terms verified (derivable from A1, medium confidence)
- [ ] Approved for implementation changed to yes

---

## Formula Confidence Gate

**Formula inventory**: `docs/formula_inventories/cfweno5_scalar_formulas.yml`
**Confidence report**: `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_confidence_report.md`
**Checker tool**: `tools/check_formula_confidence.py`

All `implementation_relevance: required` formulas must be `confidence: high`
and `verification_status: verified` before `Approved for implementation` can
be changed to `yes`.

### Current blocking formulas

**2 formulas** block implementation:

| Formula ID | Confidence | Verification | Consistency | Reason |
|------------|-----------|-------------|-------------|--------|
| appendix_A_eq_A1 | medium | failed_validation | failed | s2 substencil only 2nd order (should be 4th); combined scheme ~1st order |
| cfweno5_stencil_expression | medium | failed_validation | failed | Combined substencil WENO assembly does not achieve 5th order with current A1 formulas |

See `docs/tasks/cfweno5_scalar_prototype/failed_attempt_diagnostic.md` and
`docs/tasks/cfweno5_formula_verification/appendix_a_reverification_plan.md`.

### Optional formulas (do not block approval)

| Formula ID | Confidence | Verification | Reason |
|------------|-----------|-------------|--------|
| appendix_A_eq_A2 | medium | derived | Derived from verified A1 via d/dv; pdftotext transcription ambiguous |

A2 derivation policy: `docs/tasks/cfweno5_formula_verification/a2_derivation_policy.md`

Three previously blocking formulas resolved in v1.3-pre.5:
- appendix_A_eq_A1: promoted to high/verified (character-level pdftotext verification)
- eq19_smoothness_r3: promoted to high/verified (character-level pdftotext, b_30 corrected)
- cfweno5_stencil_expression: promoted to high/verified (order-independent, CFWENO3-validated)

A2 reclassified from required/blocking to optional/non-blocking in v1.3-pre.6:
- A2 is mathematically derived from A1 (d/dv of verified coefficients)
- Implementation derives A2 from verified A1 via symbolic differentiation
- A2 serves as verification reference, not direct implementation input

### Strict confidence check

```
make formula-confidence-cfweno5-strict
```

This check now **fails** with 4 blocking items (2 confidence + 2 consistency_status).
Both `appendix_A_eq_A1` and `cfweno5_stencil_expression` block implementation
due to medium confidence/failed_validation and consistency_status=failed.

**Do not change `Approved for implementation` to `yes` until all blocking formulas are resolved.**

---

## Remaining Items Before Approval

1. **Helper refactor decision**: Decide whether to refactor into `solver/cfweno_scalar.py`
   before adding CFWENO5 code (recommended in feasibility review).
2. **Table I sum-to-1 verification**: The three Table I weights do not trivially sum to 1
   for general nu. This should be checked algebraically or against the paper's numerical
   examples at implementation time.
3. **Explicit human approval**: The formula confidence gate passes, but the spec requires
   a human to review and explicitly set `Approved for implementation: yes`.

**v1.3-pre.10 combined target audit (2026-05-29)**: The diagnostic checker now distinguishes the three Table I substencils (`s0`, `s1`, `s2`) from the fourth Appendix A Eq. (A1) expression, which has no `,k` subscript and is treated as the direct full-stencil averaged target. That direct target reaches ~6.0 one-step order, while the Eq. (16) / normalized Table I WENO-combination diagnostic remains near ~3.0 order. CFWENO5 remains BLOCKED because the Eq. (16), Table I, and Appendix A full-target interpretation is not reconciled. See `docs/tasks/cfweno5_formula_verification/combined_target_audit.md`.

**v1.3-pre.11 direct target policy (2026-05-29)**: Decision A. For the first scalar linear CFWENO5 prototype, the accepted formula/validation target is the direct Appendix A Eq. (A1) full-stencil averaged target. The Eq. (16) / normalized Table I WENO-combination path remains diagnostic-only and unresolved for future nonlinear/WENO-combination scope. The formula consistency checker now gates the scalar linear target on the Appendix A direct full target and keeps the Table I combination as nonblocking diagnostic evidence. `Approved for implementation` remains `no`. See `docs/tasks/cfweno5_formula_verification/direct_target_policy.md`.

**v1.3-pre.12 gate scope alignment (2026-05-29)**: Decision A. The formula-confidence strict gate is now scoped to the scalar linear direct Appendix A target. Required direct-target formulas must be high confidence/verified and pass consistency; Eq. (16) / Table I normalized WENO-combination formulas are visible as deferred nonlinear/WENO scope and do not block the scalar-linear direct-target gate. The scalar linear direct target is ready for human approval consideration, but `Approved for implementation` remains `no` and CFWENO5 is not implemented. See `docs/tasks/cfweno5_formula_verification/gate_scope_alignment.md`.
