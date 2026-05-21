# CFWENO Real-Paper Demo: From Published PDF to Scalar Prototype

**Date**: 2026-05-21
**Status**: Complete (v1.0 demo packaging)
**Commit**: cbfecb0

---

## Purpose

This demo showcases how `workflow_sample` takes a real published paper through the
full paper-to-code workflow: PDF intake, extraction, feasibility review, dependency
classification, spec approval, implementation, validation, accuracy audit, and
traceability — producing runnable, validated numerical prototypes.

---

## Source Paper

- **Title**: High-order compact fully discrete schemes for inviscid compressible flows simulations
- **Authors**: Zhou, Dong, Pan
- **Journal**: Physics of Fluids 37, 106131 (2025)
- **DOI**: [10.1063/5.0291087](https://doi.org/10.1063/5.0291087)
- **Method**: CFWENO (Compact Fully-discrete WENO)
- **Note**: Original PDF is not redistributed (publisher license). Local copy at `.local/papers/cfweno_pof_2025.pdf`.

---

## Workflow Path

The full paper-to-code workflow was exercised across 13 gated stages:

| Stage | Artifact |
|-------|----------|
| 1. PDF intake | `docs/paper_reviews/cfweno_pof_2025/` |
| 2. Extraction report | `docs/paper_reviews/cfweno_pof_2025/extraction_report.md` |
| 3. Feasibility review | `docs/feasibility/cfweno_pof_2025_feasibility.md` |
| 4. Dependency classification | `docs/papers/cfweno_dependency_register.md` |
| 5. Scalar readiness audit | `docs/feasibility/cfweno_scalar_burgers_readiness.md` |
| 6. Approved scalar linear spec | `docs/scheme_specs/cfweno_scalar_subset.md` |
| 7. Scalar linear implementation | `solver/schemes.py` — `cfweno()` |
| 8. Scalar linear hardening | CFL sweep, convergence, audit |
| 9. Approved Burgers subset spec | `docs/scheme_specs/cfweno_scalar_burgers_subset.md` |
| 10. Burgers implementation | `solver/schemes.py` — `cfweno_burgers()` |
| 11. Burgers accuracy audit | Predictor/CFL/reference sweeps |
| 12. Burgers flux-form audit | `docs/tasks/cfweno_burgers_prototype/flux_form_audit.md` |
| 13. SFM state-consistency audit | `docs/tasks/cfweno_burgers_prototype/sfm_state_consistency_audit.md` |

---

## Implemented Subsets

| Subset | Equation | Scope | Status |
|--------|----------|-------|--------|
| Scalar linear advection CFWENO3 | `u_t + a*u_x = 0`, `a = const` | Full prototype, 3rd-order | Complete |
| Scalar nonlinear Burgers CFWENO3 | `u_t + (u^2/2)_x = 0` | Pre-shock only, ~2nd-order | Complete |
| Euler CFWENO | 2D compressible Euler | Characteristic decomposition | Not implemented |
| 2D CFWENO | Multi-dimensional | Dimensional composition | Not implemented |
| CFWENO5/7 | Higher orders | 5th/7th order weights | Not implemented |
| Post-shock shock-capturing | Burgers/Euler | Nonlinear WENO weights (Eq. 17) | Not implemented |

---

## Validation Summary

### Linear Advection (v1.1)

**Setup**: `u_t + a*u_x = 0`, `a = 1`, `u_0 = sin(2*pi*x) + 1`, periodic BC

| Method | L2 (nx=100) | Observed order |
|--------|------------|----------------|
| Upwind | 1.724e-02 | ~1 |
| Lax-Wendroff | 5.480e-04 | ~2 |
| **CFWENO3** | **1.444e-06** | **~3.02** |

- CFWENO3 is **380x** more accurate than Lax-Wendroff, **11,937x** more accurate than upwind
- CFL sweep: stable at CFL 0.1, 0.5, 0.9

**Outputs**: `results/cfweno_scalar_demo/`, `results/cfweno_scalar_convergence/`, `results/cfweno_scalar_cfl_sweep/`

### Burgers Pre-Shock (v1.2)

**Setup**: `u_t + (u^2/2)_x = 0`, `u_0 = 1 + 0.2*sin(2*pi*x)`, CFL=0.5, T=0.15 (pre-shock)

| Method | L2 (nx=100) | Observed order |
|--------|------------|----------------|
| Rusanov baseline | 2.496e-03 | ~1.0 |
| **CFWENO3 Burgers** | **1.444e-05** | **~2.0** |

- CFWENO3 is **173x** more accurate than Rusanov at nx=100

**Predictor sweep** (0/1/2 iterations): all yield ~2.0 order; predictor=0 marginally lower error; iterations do not improve convergence rate.

**CFL sweep** (0.1/0.3/0.5): all stable; CFL=0.5 is ~2x worse than CFL=0.1 but uses far fewer steps.

**Reference sensitivity** (nx_ref=1280/2560/5120): convergence order insensitive to reference (spread 0.04); nx=2560 sufficient.

**Outputs**: `results/cfweno_burgers_demo/`, `results/cfweno_burgers_convergence/`, `results/cfweno_burgers_predictor_sweep/`, `results/cfweno_burgers_cfl_sweep/`, `results/cfweno_burgers_reference_sensitivity/`

---

## Why Burgers Is Second Order

The Burgers prototype achieves ~2nd-order convergence instead of the 3rd order
observed for linear advection. This has been investigated through three audits:

1. **Accuracy audit** (predictor/CFL/reference sweeps): All configurations yield ~2.0 order.
   The per-cell variation of `nu = dt * u_i / dx` in the CFWENO3 stencil (derived for
   constant `nu`) introduces truncation error that reduces the formal order.

2. **Flux-form audit** (v1.2.1): The numerical flux `f_hat = f(ubar) = ubar^2/2` is an
   exact algebraic identity of the SFM two-step form `f_hat = a*ubar - f*` for scalar
   Burgers. This is NOT the cause of the order reduction.

3. **SFM state-consistency audit** (v1.2.2): The spec defines `f*` at `u^{n+1}_{i+1/2}`,
   which equals `ubar_{i+1/2}` — the same state used in the code. No state variable mismatch.

**Conclusion**: The ~2nd-order result is a documented and accepted prototype limitation,
caused by per-cell `nu` variation in a stencil derived for constant `nu`. This should NOT
be presented as a full nonlinear high-order CFWENO implementation.

---

## Traceability

| Task | Manifest |
|------|----------|
| Real-paper intake | `docs/tasks/cfweno_real_paper_intake/traceability.md` |
| Dependency resolution | `docs/tasks/cfweno_dependency_resolution/traceability.md` |
| Scalar readiness audit | `docs/tasks/cfweno_scalar_readiness_audit/traceability.md` |
| Scalar linear prototype (v1.1) | `docs/tasks/cfweno_scalar_prototype/traceability.md` |
| Burgers readiness | `docs/tasks/cfweno_burgers_readiness/traceability.md` |
| Burgers prototype (v1.2) | `docs/tasks/cfweno_burgers_prototype/traceability.md` |
| Demo packaging (v1.0) | `docs/tasks/cfweno_real_paper_demo_packaging/traceability.md` |

---

## Reproduce

```bash
# Linear advection + convergence + CFL sweep
make demo-real-paper-scalar

# Burgers + convergence + predictor/CFL/reference sweeps
make demo-real-paper-burgers

# Full CFWENO real-paper demo (both + validation index + health)
make demo-real-paper-cfweno

# Validation index and repo health
make validation-index
make health
```

---

## Current Limitations

- **No full CFWENO** — scalar prototypes only (linear advection + Burgers pre-shock)
- **No Euler CFWENO** — characteristic decomposition not implemented
- **No 2D CFWENO** — dimensional extension not implemented
- **No CFWENO5/7** — 3rd-order only
- **No post-shock validation** — requires nonlinear WENO weights (Eq. 17)
- **Burgers convergence is ~2nd order** — not the theoretical 3rd order; caused by per-cell `nu` variation
- **Original PDF not redistributed** — publisher license restriction
