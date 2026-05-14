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

## 2. Adding a New Reconstruction Method (e.g. MUSCL)

**Files to modify:**
- `cfd/numerics/reconstruction.py` — add the MUSCL reconstruction path
- `cfd/numerics/limiters.py` — connect the chosen limiter

**Steps:**
1. In `reconstruct()`, add a `"muscl"` branch that computes slopes using `minmod()` from `limiters.py`.
2. The reconstruction should return `(UL, UR)` with the same shapes as piecewise constant.
3. Update `CFDConfig.reconstruction` docstring.

**Tests to run:**
```bash
pytest tests/test_cfd_update.py tests/test_cfd_solver_uniform.py -q
```

---

## 3. Adding a New Limiter

**Files to modify:**
- `cfd/numerics/limiters.py` — add the limiter function (e.g. `van_leer`)
- `cfd/numerics/reconstruction.py` — use it in MUSCL branch

**Steps:**
1. Implement the limiter as a pure function `(a, b) -> result` following the `minmod` pattern.
2. Add it to `__all__` in `limiters.py` and `__init__.py`.

---

## 4. Adding a New Time Integration Method (e.g. RK3)

**Files to modify:**
- `cfd/numerics/time_integration.py` — add RK3 stage loop
- `cfd/numerics/update.py` — may need a single-stage function

**Steps:**
1. In `advance()`, add an `elif time_integrator == "rk3"` branch.
2. RK3 requires 3 stages: compute k1, k2, k3 using `euler_update` (or a dedicated stage function).
3. Update `CFDConfig.time_integrator` docstring.

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
bash -ic 'module-conda && python -m compileall cfd tests examples tools'
bash -ic 'module-conda && pytest -q'
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
3. **Run convergence study**: `python examples/run_cfd_entropy_wave_convergence.py`
4. **Check error_summary.csv** — errors should not increase significantly.
5. **Check convergence_summary.csv** — observed order should improve or stay the same.
6. **Check density comparison plots** — visual inspection for anomalies.
7. **Update analysis.md** if observations change.
8. **Only then** run Sod shock tube or other non-analytic cases.

The entropy wave is the primary analytic benchmark because it has an exact
solution with periodic BCs, making it suitable for convergence measurement.
Sod shock tube is useful for robustness but has no simple analytic solution
for error quantification.

---

## 9. Files NOT to Modify Casually

| File | Reason |
|------|--------|
| `cfd/constants.py` | Index conventions used everywhere |
| `cfd/variables/conversion.py` | Correctness of primitive/conservative conversion is foundational |
| `cfd/mesh/structured.py` | Grid layout conventions affect all numerics |
| `cfd/solver.py` | Orchestration — changes here affect all cases |
