# CFD Iteration Guide

This document explains how to extend the CFD solver.  It is written for both
human developers and AI agents.

---

## 1. Adding a New Numerical Flux

**Files to modify:**
- `cfd/numerics/riemann.py` — add the new flux function (e.g. `hllc_flux_x`)
- `cfd/numerics/update.py` — dispatch to the new flux based on `flux_type`
- `cfd/numerics/__init__.py` — export the new function

**Steps:**
1. Implement `hllc_flux_x(UL, UR, gamma)` and `hllc_flux_y(UL, UR, gamma)` in `riemann.py`.
2. In `update.py`, add a branch in `euler_update` that calls the new flux when `flux_type == "hllc"`.
3. Update `CFDConfig.flux_type` docstring to list the new option.

**Tests to run:**
```bash
pytest tests/test_cfd_fluxes.py tests/test_cfd_update.py -q
```

**Docs to update:**
- `docs/cfd_module_interfaces.md` — add new function signatures
- `docs/api/cfd_numerics_riemann.md` — regenerate with `python tools/generate_cfd_api_docs.py`

---

## 2. Adding a New Reconstruction Method

**Files to modify:**
- `cfd/numerics/reconstruction.py` — add the reconstruction path
- `cfd/numerics/limiters.py` — add limiters if needed

**Current implementations:**
- `piecewise_constant` — 1st order, simply copies cell values to interfaces
- `muscl` — 2nd order, reconstructs in **primitive variables** with slope limiter

**MUSCL implementation notes:**
- `_muscl_x` handles x-direction, `_muscl_y` handles y-direction
- Both convert to primitive variables, compute limited slopes, extrapolate, then convert back
- Safety fallback: if reconstructed rho <= 0 or p <= 0, falls back to piecewise constant
- The `limiter_name` parameter selects the slope limiter from `limiters.py`

**Tests to run:**
```bash
pytest tests/test_cfd_muscl_reconstruction.py tests/test_cfd_update.py -q
```

---

## 3. Adding a New Limiter

**Files to modify:**
- `cfd/numerics/limiters.py` — add the limiter function

**Current implementations:**
- `minmod` — most diffusive, very stable
- `van_leer` — less diffusive, sharper discontinuities

**Steps:**
1. Implement the limiter as a pure function `(a, b) -> result` following the `minmod` pattern.
2. Register it in the `LIMITERS` dict in `limiters.py`.
3. Add it to `__all__` and export from `__init__.py`.

**Tests to run:**
```bash
pytest tests/test_cfd_limiters.py -q
```

---

## 4. Adding a New Time Integration Method

**Files to modify:**
- `cfd/numerics/time_integration.py` — add the time integrator stage loop

**Current implementations:**
- `euler` — Forward Euler, 1st order, CFL <= 0.5 typically
- `ssp_rk2` — Strong Stability Preserving RK2, 2nd order

**SSP RK2 implementation:**
```
U1 = U^n + dt * L(U^n)
U^{n+1} = 0.5*U^n + 0.5*(U1 + dt*L(U1))
```
where `L(U) = compute_residual(U, ...)` is the spatial operator.

**Steps:**
1. Add a new `_method_step(U, dt, ...)` function in `time_integration.py`.
2. Add dispatch branch in `advance()`.
3. Update `CFDConfig.time_integrator` docstring.

**Tests to run:**
```bash
pytest tests/test_cfd_time_integration.py -q
```

---

## 5. Adding a New Boundary Condition

**Files to modify:**
- `cfd/boundary/conditions.py` — implement the new BC function
- `cfd/boundary/ghost_cells.py` — register it in `_BC_DISPATCH`

**Steps:**
1. Write a function `def my_bc_x(U: np.ndarray, ng: int) -> None` that fills ghost cells in-place.
2. Add to `_BC_DISPATCH` and export from `__init__.py`.

**Tests to run:**
```bash
pytest tests/test_cfd_boundary.py -q
```

---

## 6. Adding a New Case

**Files to modify:**
- `cfd/cases/` — add a new module (e.g. `kelvin_helmholtz.py`)
- `cfd/cases/__init__.py` — export

**Steps:**
1. Create `my_case_config() -> CFDConfig` and `my_case_ic(nxt, nyt, gamma) -> U`.
2. Follow the pattern in `uniform_flow.py` or `sod_shock_tube_2d.py`.
3. Add an example script in `examples/`.

**Tests to run:**
```bash
pytest tests/test_cfd_solver_uniform.py -q
pytest -q   # run all tests
```

---

## 7. After Every Change

**Must run:**
```bash
tools/run_in_project_env.sh python -m compileall cfd tests examples tools
tools/run_in_project_env.sh pytest -q
```

**Must update:**
- `docs/cfd_module_interfaces.md` — if public interfaces changed
- `docs/cfd_architecture.md` — if data flow or module responsibilities changed
- `docs/api/` — regenerate with `python tools/generate_cfd_api_docs.py`

---

## 8. Validation Flow After Adding New Numerical Methods

After implementing a new reconstruction, Riemann solver, limiter, or time
integrator, follow this validation sequence:

1. **Run unit tests**: `pytest -q`
2. **Run entropy wave validation**: `python examples/run_cfd_entropy_wave.py`
3. **Run entropy wave convergence**: `python examples/run_cfd_entropy_wave_convergence.py`
4. **Run isentropic vortex validation**: `python examples/run_cfd_isentropic_vortex.py`
5. **Run isentropic vortex convergence**: `python examples/run_cfd_isentropic_vortex_convergence.py`
6. **Check error_summary.csv** — errors should not increase significantly.
7. **Check convergence_summary.csv** — observed order should improve or stay the same.
8. **Only then** run Sod shock tube or other non-analytic cases.

The entropy wave is the primary first-order benchmark. The isentropic vortex
is the primary second-order benchmark because its nonlinear smooth solution
properly exercises MUSCL reconstruction and SSP RK2 time integration.

---

## 9. Files NOT to Modify Casually

| File | Reason |
|------|--------|
| `cfd/constants.py` | Index conventions used everywhere |
| `cfd/variables/conversion.py` | Correctness of primitive/conservative conversion is foundational |
| `cfd/mesh/structured.py` | Grid layout conventions affect all numerics |
| `cfd/solver.py` | Orchestration — changes here affect all cases |
