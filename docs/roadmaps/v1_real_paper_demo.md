# Roadmap: v1.x Real-Paper Demo (CFWENO)

## Current State (v1.0 Intake)

The v1.0 intake for the CFWENO paper (Zhou-Dong-Pan 2025, Phys. Fluids 37, 106131) is **complete**. The full paper-to-code workflow has been exercised from PDF extraction through feasibility assessment, producing:

- Paper reference metadata
- Comprehensive extraction report (25 pages, 9 sections)
- Scheme specification (with approval gate set to `no`)
- Feasibility assessment (verdict: intake complete, implementation deferred)
- Traceability manifest

**Implementation is deferred** because:
1. 4 unresolved extraction items (WENO weights, eigenvalue iteration, p_m formula, CFL limit)
2. High complexity (~820-1230 LOC vs. ~150 for HLL v0.1 demo)
3. External reference dependencies (FWENO papers [6,7])

---

## Phased Implementation Plan

### Implementation Subsets

The CFWENO scheme decomposes into three subsets with independent blockers:

| Subset | Scope | Blocking dependencies | Target phase |
|--------|-------|----------------------|--------------|
| **Scalar 1D** | Linear advection, Burgers, CFWENO3 stencil, HJ flux | WENO weights from refs [6,7] | v1.2 |
| **Euler 1D** | Characteristic decomposition, Algorithm 1, compact flux, p_m prediction | + Eigenvalue iteration, p_m verification | v1.3 |
| **2D Euler** | Consistent cell-interface distribution, dimensional composition | None additional | v1.4 |

Key insight: **Scalar subset can proceed independently** once WENO weights are obtained, even if Euler-specific items remain unresolved.

### v1.1 — Gap Resolution

**Goal**: Resolve all 4 unresolved items from the extraction report.

| Item | Action | Dependency |
|------|--------|------------|
| WENO weight formulas | Obtain and extract FWENO references [6,7] from the paper bibliography | Access to referenced papers |
| Eigenvalue iteration | Identify iteration start guess, count, and convergence from FWENO literature | Same as above |
| p_m formula (Eq. 23) | Re-read paper page containing Eq. 23 at higher resolution or transcribe manually | Paper access |
| CFL stability | Verify CFL <= 1 claim against test cases; document empirical limit | Code from v1.2 |

**Deliverables**:
- Updated extraction report with all items resolved
- Updated scheme spec with complete algorithmic detail
- Scheme spec approval changed to `yes`

### v1.2 — Scalar CFWENO3 (Proof of Concept)

**Goal**: Implement the simplest non-trivial CFWENO variant.

| Component | Scope |
|-----------|-------|
| Reconstruction | 3rd-order WENO only |
| Equation | 1D scalar advection + 1D Burgers |
| Time integration | Single-stage CFWENO update |
| Validation | Linear advection convergence, Burgers shock |

**Files**:
- New: `cfd/numerics/weno.py` (3rd-order weights only)
- New: `cfd/numerics/hermite.py`
- New: `examples/run_scalar_cfweno.py`
- New: `tests/test_cfd_cfweno.py`

**Validation criteria**:
- 3rd-order convergence on linear advection
- Non-oscillatory shock capturing on Burgers
- Comparison with existing upwind/LW schemes

### v1.3 — CFWENO3 Euler 1D

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

### v1.4 — Higher Orders and 2D

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

| Aspect | v0.1 (HLL) | v1.2-v1.4 (CFWENO) |
|--------|------------|---------------------|
| Scope | Single Riemann solver | Full scheme (reconstruction + flux + time integration) |
| New LOC | ~150 | ~820-1230 (total across v1.2-v1.4) |
| Phases | Single implementation | 3 phased implementations |
| External refs needed | None | 2+ FWENO papers |
| Demo value | First paper-to-code workflow | Second method, higher complexity |

---

## Success Metrics

1. **v1.1**: All extraction gaps resolved, scheme spec approved
2. **v1.2**: 3rd-order convergence verified on scalar equations
3. **v1.3**: Algorithm 1 produces correct wave selection; Shu-Osher matches published results
4. **v1.4**: 2D extension maintains formal order; CFWENO5/7 converge at expected rates
