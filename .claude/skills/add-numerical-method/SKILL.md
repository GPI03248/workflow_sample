---
name: add-numerical-method
description: Add a new CFD numerical method (reconstruction, limiter, Riemann solver, or time integrator)
---

# Add Numerical Method

## When to Use

When adding one of:
- Reconstruction method (e.g., WENO)
- Slope limiter (e.g., superbee, MC)
- Riemann solver / numerical flux (e.g., HLLC, Roe)
- Time integration method (e.g., RK3)

## Required Inputs

The user must specify:
- **Method type**: reconstruction / limiter / riemann / time_integrator
- **Method name**: identifier string (e.g., `"weno"`, `"superbee"`, `"hllc"`, `"rk3"`)
- **Algorithm description**: formulas or reference

## Required Workflow

1. **Read Definition of Done**: Read `docs/cfd_definition_of_done.md` section matching the method type (3-6).
2. **Inspect existing implementations**:
   - Reconstruction: read `cfd/numerics/reconstruction.py`
   - Limiter: read `cfd/numerics/limiters.py`
   - Riemann: read `cfd/numerics/riemann.py`
   - Time integrator: read `cfd/numerics/time_integration.py` and `cfd/numerics/update.py`
3. **Implement the method**: Follow existing patterns exactly.
4. **Update dispatch**: Add to the relevant `if/elif` dispatch in the module.
5. **Update config**: Update `CFDConfig` field docstring in `cfd/config.py`.
6. **Update exports**: `cfd/numerics/__init__.py`.
7. **Write tests**: Add to existing test file or create new one.
8. **Run unit tests**: `tools/run_in_project_env.sh pytest -q`.
9. **Run analytic validation** (MANDATORY — not optional):
   ```bash
   tools/run_in_project_env.sh python examples/run_cfd_entropy_wave.py
   tools/run_in_project_env.sh python examples/run_cfd_entropy_wave_convergence.py
   tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex.py
   tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex_convergence.py
   ```
10. **Compare errors**: New method must NOT increase errors significantly.
11. **Update docs**: Follow `update-cfd-docs` skill.

## Files to Inspect

### For reconstruction:
- `cfd/numerics/reconstruction.py` — existing `_muscl_x` pattern
- `cfd/numerics/limiters.py` — limiter interface

### For limiter:
- `cfd/numerics/limiters.py` — existing `minmod`, `van_leer` pattern
- `cfd/numerics/reconstruction.py` — how limiters are called

### For Riemann solver:
- `cfd/numerics/riemann.py` — existing `rusanov_flux_x/y` pattern
- `cfd/numerics/update.py` — how fluxes are dispatched

### For time integrator:
- `cfd/numerics/time_integration.py` — existing `_ssp_rk2_step` pattern
- `cfd/numerics/update.py` — `compute_residual()` interface

### Always inspect:
- `cfd/config.py` — CFDConfig fields
- `docs/cfd_definition_of_done.md` — relevant section

## Files That May Be Modified

- `cfd/numerics/<module>.py` — add method
- `cfd/numerics/__init__.py` — update exports
- `cfd/config.py` — update docstring
- `cfd/numerics/update.py` — if Riemann dispatch changes
- `cfd/solver.py` — if new parameters need threading
- `tests/test_cfd_<topic>.py` — add unit tests
- `docs/cfd_module_interfaces.md` — update interfaces
- `docs/api/` — regenerated

## Tests to Run

```bash
# Compile check
tools/run_in_project_env.sh python -m compileall solver cfd tests examples tools

# Unit tests (MUST pass)
tools/run_in_project_env.sh pytest -q

# Analytic validation (MUST run, errors must NOT regress)
tools/run_in_project_env.sh python examples/run_cfd_entropy_wave.py
tools/run_in_project_env.sh python examples/run_cfd_entropy_wave_convergence.py
tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex.py
tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex_convergence.py
```

## Result Files to Generate

Analytic validation outputs (for comparison):
- `results/cfd_entropy_wave/error_summary.csv`
- `results/cfd_isentropic_vortex/error_summary.csv`
- `results/cfd_entropy_wave_convergence/convergence_summary.csv`
- `results/cfd_isentropic_vortex_convergence/convergence_summary.csv`

## Final Response Format

```
## Final Report

### Changed Files
- list every modified/created file

### Tests Run
- pytest output (must show all pass)

### Validation Results
- Entropy wave: L2 error, convergence order
- Isentropic vortex: L2 error, convergence order
- Comparison table: old method vs new method

### Numerical Assumptions
- stability constraints (CFL limit, etc.)
- any theoretical vs observed order discrepancy explanation

### Result File Paths
- paths to validation outputs

### Remaining Risks
- known limitations of the new method
```

## Failure Handling Rules

- If new method causes NaN → check for division by zero, add epsilon guards
- If new method causes negative rho/p → add safety fallback (revert to piecewise constant)
- If convergence order is below expected → verify implementation, check limiter interaction
- If errors increase vs. baseline → the method is WRONG, do NOT proceed
- If tests fail → fix before proceeding, never skip
- If time integrator is unstable → reduce CFL, check SSP property
- If the method requires changes to `compute_residual` interface → update ALL callers
