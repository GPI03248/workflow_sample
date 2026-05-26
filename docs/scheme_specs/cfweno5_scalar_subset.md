# Scalar CFWENO5 Subset — Scheme Spec

**Source**: Zhou-Dong-Pan (2025), Phys. Fluids 37, 106131
**Subset**: 1D scalar linear advection CFWENO5 prototype
Approved for implementation: no

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

The following formulas must be extracted and verified from the paper before
implementation can proceed:

### 1. CFWENO5 Stencil (BLOCKER)

Eq. (30) is the 3rd-order stencil. The paper must contain a generalization for
5th order (r=3, order 2r-1 = 5). This formula was **not extracted** in the
original intake.

**Status: NOT EXTRACTED — BLOCKER**

### 2. Optimal Linear Weights — Table I (BLOCKER)

The paper's Table I provides optimal weights `gamma_bar_k^r` for r=2,3,4.
Only r=2 values were transcribed. The r=3 weights needed for CFWENO5:

Expected pattern (from dependency register):
- `gamma_bar_0^3 = (1+nu)^2 / 6`
- `gamma_bar_1^3 = (1+nu)(2-nu) / 6`
- `gamma_bar_2^3 = (1-nu)(2-nu) / 6`

But the full set of weights for all 4 substencils has not been verified.

**Status: NOT FULLY TRANSCRIBED — BLOCKER**

### 3. Next-Time-Level Weights — Table II (BLOCKER)

Same as Table I but for the time-level reconstruction. r=3 values not extracted.

**Status: NOT TRANSCRIBED — BLOCKER**

### 4. Smoothness Indicators — Eq. (19) (BLOCKER)

The general formula exists (Eq. 19), but the explicit polynomial expressions
for the r=3 case's substencils have not been written out.

**Status: GENERAL FORMULA KNOWN, SPECIFIC EXPANSIONS MISSING — BLOCKER**

### 5. WENO Nonlinear Weights — Eq. (17)

The weight machinery is order-independent:
```
gamma_bar_k = alpha_bar_k / (beta_bar_k + eps)^2
```

**Status: AVAILABLE — not a blocker**

### 6. Interface Reconstruction (needs verification)

The current CFWENO3 uses 4th-order centered interpolation. For CFWENO5,
a higher-order interface reconstruction may be needed (possibly 6th-order).
The paper's Eq. (28-29) describes cubic (3rd-order) Hermite interpolation.
Whether a higher-order version is needed or provided is unknown.

**Status: NEEDS VERIFICATION**

### 7. Conservative Update

The update formula `u_i^{n+1} = u_i - cfl * (ubar_{i+1/2} - ubar_{i-1/2})`
is the same for all orders. No change needed.

**Status: AVAILABLE**

### 8. Periodic Boundary Handling

`np.roll` extends naturally to wider stencils. No conceptual change.

**Status: AVAILABLE**

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
