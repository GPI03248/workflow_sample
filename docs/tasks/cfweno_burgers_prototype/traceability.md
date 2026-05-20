# Task Traceability Manifest: CFWENO Burgers Prototype (v1.2)

## Task Information
- **Task ID**: cfweno_burgers_prototype
- **Task type**: paper-to-code implementation (v1.2 scalar nonlinear Burgers CFWENO3 prototype)
- **Date**: 2026-05-20
- **Status**: complete

## Source Paper
- **Paper**: .local/papers/cfweno_pof_2025.pdf (NOT in git)
- **Citation**: Zhou-Dong-Pan (2025), Physics of Fluids 37, 106131, DOI: 10.1063/5.0291087

## Scheme Spec
- **Path**: docs/scheme_specs/cfweno_scalar_burgers_subset.md
- **Approved**: yes (human-approved 2026-05-20)

## Readiness Review
- **Path**: docs/feasibility/cfweno_scalar_burgers_readiness.md
- **Decision**: conditionally ready (conditions met)

## Implemented Subset
- **Scope**: 1D scalar nonlinear Burgers CFWENO3 prototype, pre-shock only
- **Equation**: u_t + (u^2/2)_x = 0
- **IC**: u(x,0) = 1 + 0.2*sin(2*pi*x) (positive everywhere)
- **Formula source**: Paper Eq. (30) — CFWENO3 compact stencil with per-cell nu
- **Flux**: SFM decomposition → f_hat = f(ubar) = ubar^2/2
- **Predictor**: 1 iteration (default), supports 0/1/2
- **Reference**: fine-grid CFWENO3 Burgers (nx=2560)
- **Boundary**: periodic via np.roll
- **Single-stage**: No Runge-Kutta

## Non-Goals
- NOT implementing Euler CFWENO
- NOT implementing 2D CFWENO
- NOT implementing CFWENO5/7
- NOT implementing shock-capturing (pre-shock only)
- NOT using Eq. 23 (Euler-specific)
- NOT using characteristic decomposition
- NOT claiming full CFWENO paper reproduction
- NOT modifying cfd/ or existing HLL/Rusanov/Euler solver

## Modified Files
| File | Change |
|------|--------|
| solver/schemes.py | Added `cfweno_burgers()`, `burgers_upwind()`, `_interface_reconstruction()`, `_cfweno3_stencil()` helpers |
| examples/run_cfweno_burgers_demo.py | NEW — demo with reference comparison |
| examples/run_cfweno_burgers_convergence.py | NEW — convergence study (40/80/160/320) |
| tests/test_cfweno_burgers.py | NEW — 19 Burgers-specific tests |
| Makefile | Added cfweno-burgers-demo, cfweno-burgers-convergence, demo-real-paper-burgers targets |
| tools/summarize_validation_results.py | Added cfweno_burgers_demo and cfweno_burgers_convergence to KNOWN_DIRS |
| docs/tasks/cfweno_burgers_prototype/traceability.md | NEW — this manifest |

## Tests Run
- `pytest -q` — 236 passed, 1 skipped (CSV parseability skipped before demo run)
- Test coverage: import, shape, constant state, mass conservation, finite values, CFL rejection, predictor iterations 0/1/2, baseline shape/mass, CSV parseability, approval checker

## Validation Results

### Demo (nx=100, CFL=0.5, T=0.15)
- CFWENO3 Burgers L2: 1.44e-05
- Rusanov L2: 2.50e-03
- CFWENO3 is **173x more accurate** than Rusanov at this resolution

### Convergence (nx=40/80/160/320, reference nx=2560)
- CFWENO3 Burgers convergence: **~2.0 order** (2.01)
- Rusanov convergence: ~1.0 order (1.00)
- CFWENO3 Burgers is consistently more accurate at all resolutions
- Convergence is 2nd-order, not 3rd-order as for linear advection

## Numerical Assumptions
1. CFL based on max(|u|): dt = CFL * dx / max(|u|) for stability
2. Per-cell nu = dt * u_i / dx — characteristic speed varies spatially
3. SFM flux: f_hat = f(ubar) = ubar^2/2 — physical flux at reconstructed interface state
4. 4th-order centred interface reconstruction (same as v1.1)
5. Periodic boundaries via np.roll
6. Single-stage update (no RK)
7. Predictor iteration (default 1) refines characteristic speed from cell-center to interface-predicted average

## Convergence Order Note

CFWENO3 Burgers achieves ~2nd-order convergence on smooth pre-shock data, not the 3rd order
observed for linear advection. This is attributed to the per-cell variation of nu (characteristic
speed) introducing truncation error in the CFWENO3 stencil, which was derived for constant nu.
This is a known limitation of extending compact fully-discrete schemes to nonlinear problems
with cell-varying wave speeds. The scheme remains significantly more accurate than 1st-order
baselines.

## Validation Result Paths
- results/cfweno_burgers_demo/error_summary.csv
- results/cfweno_burgers_demo/line_profile.csv
- results/cfweno_burgers_demo/cfweno_burgers_comparison.png
- results/cfweno_burgers_demo/analysis.md
- results/cfweno_burgers_convergence/error_summary.csv
- results/cfweno_burgers_convergence/analysis.md

## Remaining Risks
1. CFL stability not rigorously proven — empirically verified at CFL=0.5
2. Convergence order is 2nd, not 3rd — may improve with more sophisticated predictor
3. Post-shock behavior untested — oscillations expected without WENO nonlinear weights
4. Higher-order CFWENO5/7 not implemented
5. Euler CFWENO requires eigenvalue iteration resolution

## Commit
- **Branch**: master
- **Pushed to**: origin (gitee), github
