# Task Traceability Manifest: CFWENO Real-Paper Demo Packaging (v1.0)

## Task Information
- **Task ID**: cfweno_real_paper_demo_packaging
- **Task type**: demo-packaging
- **Date**: 2026-05-21
- **Status**: complete

## Source Paper
- **Paper**: Zhou-Dong-Pan (2025), Physics of Fluids 37, 106131
- **DOI**: 10.1063/5.0291087
- **PDF**: .local/papers/cfweno_pof_2025.pdf (NOT in git)

## Implemented Subsets
- Scalar linear advection CFWENO3 — 3rd-order convergence (v1.1)
- Scalar nonlinear Burgers CFWENO3 — ~2nd-order convergence, pre-shock (v1.2)

## Demo Commands
```bash
make demo-real-paper-scalar     # linear advection
make demo-real-paper-burgers    # Burgers pre-shock
make demo-real-paper-cfweno     # unified v1.0 demo
make demo-v1-real-paper         # alias
make validation-index
make health
```

## Validation Outputs
- results/cfweno_scalar_demo/
- results/cfweno_scalar_convergence/
- results/cfweno_scalar_cfl_sweep/
- results/cfweno_burgers_demo/
- results/cfweno_burgers_convergence/
- results/cfweno_burgers_predictor_sweep/
- results/cfweno_burgers_cfl_sweep/
- results/cfweno_burgers_reference_sensitivity/

## Key Validation Results
- Linear CFWENO3: 3rd-order convergence (order 3.02), stable CFL 0.1–0.9
- Burgers CFWENO3: 2nd-order convergence (order 2.01), 173x more accurate than Rusanov
- Burgers flux form: f_hat = f(ubar) is exact algebraic identity of SFM form (v1.2.1)
- SFM state consistency: f* uses same state as ubar, matching spec (v1.2.2)

## Limitations
- No Euler CFWENO, no 2D, no CFWENO5/7, no post-shock validation
- Burgers convergence is ~2nd order, not 3rd
- Original PDF not redistributed

## Files Modified in This Task
| File | Change |
|------|--------|
| docs/case_studies/cfweno_real_paper_demo.md | NEW — case study document |
| Makefile | Added demo-real-paper-cfweno, demo-v1-real-paper targets |
| README.md | Added Real-Paper CFWENO Demo section |
| docs/roadmaps/v1_real_paper_demo.md | Updated with v1.0 packaging status and next steps |
| docs/tasks/cfweno_real_paper_demo_packaging/traceability.md | NEW — this manifest |

## Code Changes
- **solver/schemes.py**: NOT modified
- **cfd/**: NOT modified
- **tests/**: NOT modified
- **examples/**: NOT modified
- **tools/**: NOT modified

## Tests Run
- `pytest -q` — 242 passed
- `make compile` — clean
- `make health` — 5 OK

## Commit
- **Hash**: 3a720d1
- **Branch**: master
- **Push**: github (origin/gitee unreachable)
