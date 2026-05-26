# Scalar CFWENO5 Subset — Scheme Spec

**Source**: Zhou-Dong-Pan (2025), Phys. Fluids 37, 106131
**Subset**: 1D scalar linear advection CFWENO5 prototype
Approved for implementation: no

**Implementation readiness**: conditionally ready — pending human verification of 3 items (see Formula Inventory below)

---

## Scope

This spec covers the 5th-order scalar CFWENO prototype for 1D linear advection:

```
u_t + a * u_x = 0,  a = const > 0
```

Periodic boundary conditions on [0, 1).

**This is a readiness spec only.** Implementation is blocked pending formula
extraction from the source paper.

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
The pdftotext transcription is unreliable for the multi-line piecewise formulas.

**Status: EXTRACTED — NEEDS HUMAN VERIFICATION**
**Confidence: MEDIUM**
**Source**: Appendix A, page 23

### 2. Optimal Linear Weights — Table I

For r=3 (CFWENO5), the 4 weights are:
- k=0: `nu(1+nu) / 6`
- k=1: `(1+nu)(2-nu) / 6`
- k=2: `(1-nu)(2+nu) / 6` or `(1-nu)(2-nu) / 6` — **UNCERTAIN**
- k=3: `(1-nu)(2-nu) / 6`

**Status: EXTRACTED — k=2 NEEDS HUMAN VERIFICATION**
**Confidence: HIGH (except k=2)**
**Source**: Table I, page 5

### 3. Next-Time-Level Weights — Table II

The pdftotext output for Table II r=3 row is severely mangled due to
multi-column layout. Values involve `v`, `(2v^2-4v+1)`, `(3v-2v)`, etc.

**Status: EXTRACTED — NEEDS HUMAN VERIFICATION (all entries)**
**Confidence: LOW**
**Source**: Table II, page 6

### 4. Smoothness Indicators — Eq. (19)

b_30 through b_33 for r=3 substencils are extracted. The expressions are
complex (b_33 has 3 terms with coefficients including 39 and 781/20).

**Status: EXTRACTED — NEEDS HUMAN VERIFICATION**
**Confidence: MEDIUM**
**Source**: Eq. (19), page 5

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

- [ ] CFWENO5 stencil formula extracted from paper (Eq. 30 generalization or equivalent)
- [ ] Table I optimal weights for r=3 transcribed and verified
- [ ] Table II weights for r=3 transcribed and verified
- [ ] Eq. (19) smoothness indicators expanded for r=3 substencils
- [ ] Interface reconstruction order requirement confirmed
- [ ] Periodic boundary stencil width verified (no special cases)
- [ ] Helper refactor decision made
- [ ] Validation plan accepted
- [ ] Approved for implementation changed to yes

---

## Known Blockers

1. **CFWENO5 stencil formula not extracted** — the paper's higher-order stencil
   generalization was not transcribed during the original intake
2. **Table I/II weight values for r=3 not transcribed** — only r=2 values exist
3. **Eq. (19) smoothness indicators not expanded for r=3** — general formula
   exists but specific polynomials are unknown
4. **Appendix A content not extracted** — may contain the missing formulas

These blockers require **re-reading the paper** (specifically the pages containing
the 5th-order stencil, Tables I-II, and Appendix A). No code work can proceed
until these formulas are available.
