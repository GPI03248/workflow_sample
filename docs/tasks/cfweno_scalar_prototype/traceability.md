# Task Traceability Manifest: CFWENO Scalar Prototype (v1.1)

## Task Information
- **Task ID**: cfweno_scalar_prototype
- **Task type**: paper-to-code implementation (v1.1 scalar CFWENO3 prototype)
- **Date**: 2026-05-20
- **Status**: complete

## Source Paper
- **Paper**: .local/papers/cfweno_pof_2025.pdf (NOT in git)
- **Citation**: Zhou-Dong-Pan (2025), Physics of Fluids 37, 106131, DOI: 10.1063/5.0291087

## Scheme Spec
- **Path**: docs/scheme_specs/cfweno_scalar_subset.md
- **Approved**: yes (human-approved 2026-05-20)

## Extraction Report
- **Path**: docs/paper_reviews/cfweno_pof_2025/extraction_report.md

## Approval Checker Result
- **Command**: `python tools/check_scheme_spec_approval.py docs/scheme_specs/cfweno_scalar_subset.md`
- **Result**: APPROVED (exit code 0)
- **Parent spec**: cfweno_pof_2025.md remains NOT APPROVED

## Implemented Subset
- **Scope**: 1D scalar linear advection CFWENO3 prototype only
- **Equation**: u_t + a*u_x = 0, a = 1.0, periodic BC
- **Formula source**: Paper Eq. (30) — CFWENO3 compact stencil
- **Stencil**: ubar_{i+1/2} = u_{i+1/2} - nu*(u_{i+1/2} - u_i) - nu*(1-nu)*(u_{i-1/2} - 2u_i + u_{i+1/2})
- **Interface reconstruction**: 4th-order centred: u_{i+1/2} = (-u_{i-1} + 7u_i + 7u_{i+1} - u_{i+2})/12
- **Numerical flux**: f_hat_{i+1/2} = a * ubar_{i+1/2} (linear advection)
- **Update**: u_i^{n+1} = u_i - cfl*(ubar_{i+1/2} - ubar_{i-1/2})
- **Single-stage**: No Runge-Kutta

## Non-Goals
- NOT implementing full CFWENO paper
- NOT implementing Euler CFWENO
- NOT implementing 2D CFWENO
- NOT implementing CFWENO5/CFWENO7
- NOT implementing nonlinear WENO shock-capturing (Eq. 17)
- NOT implementing Eq. 23 (p_m prediction)
- NOT implementing characteristic decomposition
- NOT modifying existing Euler solver, HLL, Rusanov, MUSCL, SSP RK2
- NOT moving v0.1 tag

## Modified Files
| File | Change |
|------|--------|
| solver/schemes.py | Added `cfweno()` function + registered in `_SCHEMES` |
| examples/run_cfweno_scalar_demo.py | NEW — demo with baseline comparison |
| examples/run_cfweno_scalar_convergence.py | NEW — convergence study |
| tests/test_cfweno_scalar.py | NEW — unit tests |
| Makefile | Added cfweno-scalar-demo, cfweno-scalar-convergence, demo-real-paper-scalar targets |
| tools/summarize_validation_results.py | Added cfweno_scalar_demo and cfweno_scalar_convergence to KNOWN_DIRS |
| docs/tasks/cfweno_scalar_prototype/traceability.md | NEW — this manifest |

## Tests Run
- `pytest -q` — all tests including test_cfweno_scalar.py
- Test coverage: import, shape, constant state, mass conservation, sine wave, CFL validation, run_advection integration, approval checker

## Validation Result Paths
- results/cfweno_scalar_demo/error_summary.csv
- results/cfweno_scalar_demo/line_profile.csv
- results/cfweno_scalar_demo/analysis.md
- results/cfweno_scalar_demo/cfweno_comparison.png (if matplotlib available)
- results/cfweno_scalar_convergence/error_summary.csv
- results/cfweno_scalar_convergence/analysis.md

## Numerical Assumptions
1. CFL <= 1 for stability (empirically verified, not rigorously proven)
2. Constant wave speed a = 1.0 (linear advection)
3. 4th-order centred interface reconstruction provides sufficient accuracy for 3rd-order CFWENO3
4. Periodic boundary conditions via np.roll
5. Single-stage update (no multi-stage RK)

## Remaining Risks
1. Convergence order may not reach exactly 3.0 — this is a prototype
2. CFL stability near CFL=1.0 needs empirical verification
3. Nonlinear extension (Burgers) not yet implemented
4. Higher-order CFWENO5/7 not implemented
5. Euler CFWENO requires eigenvalue iteration resolution

## Commit
- **Commit**: 2b580ef
- **Branch**: master
- **Pushed to**: origin (gitee), github
