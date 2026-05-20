# Roadmap: v1.x Real-Paper Demo (CFWENO)

## Current State (v1.1 Scalar CFWENO3 Prototype — Complete)

v1.1 is **complete**. The scalar linear CFWENO3 prototype has been implemented, hardened, and validated:

- Implementation commit: `2b580ef`
- Formula audit: PASS (Eq. 30 stencil verified against spec and paper)
- Convergence: **exactly 3rd order** (3.04 -> 3.01 -> 3.00)
- CFL sweep: stable at CFL 0.1, 0.5, 0.9
- Baseline comparison: upwind (1st), Lax-Wendroff (2nd), CFWENO3 (3rd)
- Tests: 19 CFWENO-specific tests + 212 total passing
- **Not** complete CFWENO — scalar linear advection prototype only

The v1.0 intake for the CFWENO paper (Zhou-Dong-Pan 2025, Phys. Fluids 37, 106131) is **complete**. The full paper-to-code workflow has been exercised from PDF extraction through feasibility assessment, producing:

- Paper reference metadata
- Comprehensive extraction report (25 pages, 9 sections)
- Scheme specification (with approval gate set to `no`)
- Feasibility assessment (verdict: intake complete, implementation deferred)
- Traceability manifest

**Phase 2.5 correction**: The original Phase 2 assessment classified references [6,7] as CRITICAL blockers for ALL subsets. The Phase 2.5 readiness audit confirms this was incorrect — the paper self-contains Eq. (17), Tables I-II, Eq. (19) for WENO weights, and Eq. (27-30) for the CFWENO3 stencil. **Scalar CFWENO3 has ZERO external blockers and can proceed immediately.**

---

## Phased Implementation Plan

### Implementation Subsets

The CFWENO scheme decomposes into three subsets with independent blockers:

| Subset | Scope | Blocking dependencies | Target phase |
|--------|-------|----------------------|--------------|
| **Scalar Linear** | Linear advection, constant a, CFWENO3 stencil | **NONE** | v1.1 (COMPLETE) |
| **Scalar Nonlinear** | Burgers, variable a, flux linearization | **NONE** | v1.2 (spec created) |
| **Euler 1D** | Characteristic decomposition, Algorithm 1, compact flux, p_m prediction | Eigenvalue iteration, p_m verification | v1.3 |
| **2D Euler** | Consistent cell-interface distribution, dimensional composition | None additional | v1.4 |

Key insight: **Scalar subset can proceed immediately** — Phase 2.5 audit confirms ZERO external blockers. References [6,7] are NOT needed.

### v1.1 — Scalar CFWENO3 Prototype (COMPLETE)

**Status**: Implemented and hardened.

| Item | Result |
|------|--------|
| Linear advection CFWENO3 | Eq. 30 stencil, 3rd-order convergence |
| CFL sweep | Stable at CFL 0.1, 0.5, 0.9 |
| Baseline comparison | upwind / Lax-Wendroff / CFWENO3 |
| Formula audit | PASS — only Eq. 25 + Eq. 30 used |
| Spec approval | cfweno_scalar_subset.md = yes |
| Remaining | Burgers (nonlinear) requires separate approval |

**Next step for scalar nonlinear**: Separate approval needed for Burgers extension.

### v1.2 — Scalar Nonlinear Burgers CFWENO3 (Spec Created, Implementation Pending)

**Goal**: Extend scalar CFWENO3 from linear advection to nonlinear Burgers equation.

**Status**:
- Spec created: `docs/scheme_specs/cfweno_scalar_burgers_subset.md`
- Readiness review: `docs/feasibility/cfweno_scalar_burgers_readiness.md`
- Readiness decision: **Conditionally ready** (human approval required)
- Approval: **no** (not yet approved for implementation)
- Implementation: **not started**

**What changes from v1.1**:

| Component | v1.1 (linear) | v1.2 (Burgers) |
|-----------|--------------|----------------|
| Flux | `f(u) = a*u` | `f(u) = u^2/2` |
| Wave speed | `a = 1.0` (constant) | `a = u` (variable) |
| Numerical flux | `a * ubar` (cancels) | `a * ubar - f*` (non-trivial) |
| CFL | `cfl = a*dt/dx` (fixed) | `dt = CFL*dx/max(|u|)` (adaptive) |

**Phase 1 scope** (smooth pre-shock only):
- Periodic domain, smooth IC, final_time before shock formation
- Compare against high-resolution reference or analytic implicit solution
- No shock-capturing claim

**Phase 2 scope** (optional post-shock qualitative):
- Run past shock formation time
- Compare against high-resolution reference
- Document oscillations honestly
- Do not claim shock-capturing

**Non-goals**: No Euler, no Eq. 23, no characteristic decomposition, no 2D, no CFWENO5/7

**Key open decisions** (for human):
- Predictor strategy: zero iterations (frozen `a = u_i^n`) or one iteration
- Reference solution: fine-grid baseline or analytic implicit

**Recommended modules** (if approved):
- Extend `solver/schemes.py` or refactor scalar CFWENO helper
- New: `examples/run_cfweno_burgers_demo.py`
- New: `examples/run_cfweno_burgers_convergence.py`
- New: `tests/test_cfweno_burgers.py`

### v1.3 — Euler Prep (Gap Resolution)

**Goal**: Resolve Euler-specific gaps and prepare for Euler 1D implementation.

| Item | Action | Dependency |
|------|--------|------------|
| Eigenvalue iteration | Identify iteration start guess, count, and convergence from FWENO literature | Access to refs [6,7] |
| p_m formula (Eq. 23) | Re-read paper page containing Eq. 23 at higher resolution or transcribe manually | Paper access |
| CFL stability | Verify CFL <= 1 claim against test cases; document empirical limit | Code from v1.1/v1.2 |
| FWENO refs [6,7] | Obtain for derivation context (not blocking for scalar) | Access to referenced papers |

**Deliverables**:
- Updated extraction report with Euler-specific items resolved
- Updated full scheme spec with complete algorithmic detail

### v1.4 — CFWENO3 Euler 1D

**Goal**: Extend to 1D Euler equations with characteristic decomposition and Algorithm 1.

| Component | Scope |
|-----------|-------|
| Characteristic decomposition | Roe averages, eigenvector matrices |
| Flux reconstruction | Full Algorithm 1 (all 4 branches) |
| Validation | Entropy wave, Shu-Osher, Titarev-Toro |

**Files**:
- New: `cfd/numerics/characteristic.py`
- Extended: `cfd/numerics/riemann.py` (CFWENO flux)
- Extended: `cfd/numerics/update.py` (dispatch)
- New: `examples/run_cfd_cfweno_euler1d.py`

**Validation criteria**:
- Entropy wave: L2 error comparable to or better than HLL
- Shu-Osher: density profile matches published results qualitatively
- Uniform flow: preserved to machine precision

### v1.5 — Higher Orders and 2D

**Goal**: Add CFWENO5/7 and multi-dimensional extension.

| Component | Scope |
|-----------|-------|
| WENO orders | 5th and 7th order weights |
| Multi-dimensional | Consistent cell-interface distribution (Eq. 33) |
| Validation | 2D Riemann problem, 2D vortex |

**Files**:
- Extended: `cfd/numerics/weno.py` (5th/7th order)
- Extended: `cfd/numerics/riemann.py` (order parameter)
- New: `cfd/numerics/cfweno_2d.py` (dimensional extension)
- New: `examples/run_cfd_cfweno_2d.py`

---

## Comparison with v0.1 HLL Demo

| Aspect | v0.1 (HLL) | v1.1-v1.4 (CFWENO) |
|--------|------------|---------------------|
| Scope | Single Riemann solver | Full scheme (reconstruction + flux + time integration) |
| New LOC | ~150 | ~150-250 (v1.1 scalar) + ~820-1230 (total across v1.1-v1.4) |
| Phases | Single implementation | 4 phased implementations |
| External refs needed | None | 0 for scalar (v1.1-v1.2); refs [6,7] useful for Euler context (v1.3+) |
| Demo value | First paper-to-code workflow | Second method, higher complexity |

---

## Success Metrics

1. **v1.1**: Scalar CFWENO3 linear advection prototype with 3rd-order convergence verified — COMPLETE
2. **v1.2**: Scalar CFWENO3 nonlinear Burgers (smooth pre-shock) with convergence trend — spec created, pending approval
3. **v1.3**: Euler-specific gaps resolved (eigenvalue iteration, p_m)
4. **v1.4**: Algorithm 1 produces correct wave selection; Shu-Osher matches published results
5. **v1.5**: 2D extension maintains formal order; CFWENO5/7 converge at expected rates
