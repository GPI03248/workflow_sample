# CFD Definition of Done

This document defines the **completion standard** for each type of CFD task.
A task is NOT done until every item in its checklist is satisfied.

> **Rule**: pytest passing alone is NOT sufficient to claim numerical correctness.
> Analytic validation must be run and results included in the final report.

---

## 1. Add CFD Case

**Applies when**: Adding a new flow problem (e.g., Kelvin-Helmholtz, Sedov blast).

- [ ] `cfd/cases/<case_name>.py` created with:
  - `*Params` dataclass for parameters
  - `<case_name>_config(params) -> CFDConfig`
  - `<case_name>_ic(nxt, nyt, gamma, params) -> U`
- [ ] `cfd/cases/__init__.py` updated to export new symbols
- [ ] `examples/run_cfd_<case_name>.py` created and runs without error
- [ ] `tests/test_cfd_<case_name>.py` created covering:
  - IC shape correctness
  - Positivity of rho and p
  - Solver runs to completion on small grid
- [ ] `pytest -q` passes (all tests, not just new ones)
- [ ] `python tools/generate_cfd_api_docs.py` run, `docs/api/` updated
- [ ] `docs/cfd_module_interfaces.md` updated with new case section
- [ ] README.md updated (cases table, run instructions)
- [ ] Final report includes: changed files, test output, result file paths

---

## 2. Add Analytic Validation Case

**Applies when**: Adding a case with a known exact solution for convergence testing.

All items from "Add CFD Case" PLUS:

- [ ] `<case_name>_primitive(X, Y, t, params) -> V` — analytic primitive field
- [ ] `<case_name>_conservative(X, Y, t, params) -> U` — analytic conservative field
- [ ] `<case_name>_exact_solution(mesh, t, params) -> U` — full mesh solution
- [ ] `examples/run_cfd_<case_name>_convergence.py` created with grid refinement
- [ ] Convergence study produces:
  - `results/cfd_<case_name>/error_summary.csv`
  - `results/cfd_<case_name>/analysis.md`
  - `results/cfd_<case_name>_convergence/convergence_summary.csv`
  - `results/cfd_<case_name>_convergence/convergence_analysis.md`
- [ ] Tests verify:
  - Exact solution matches IC at t=0
  - Convergence order matches theoretical expectation (within 0.2)
- [ ] Final report includes L2 errors, observed convergence order, and result file paths

---

## 3. Add Reconstruction Method

**Applies when**: Adding a new spatial reconstruction (e.g., WENO, ENO).

- [ ] `cfd/numerics/reconstruction.py` updated:
  - New method added to `reconstruct()` and `reconstruct_y()` dispatch
  - Both x and y directions implemented
- [ ] `cfd/config.py` updated: `reconstruction` field docstring lists new option
- [ ] `cfd/numerics/__init__.py` updated if new exports needed
- [ ] Unit tests in `tests/test_cfd_muscl_reconstruction.py` (or new file):
  - Constant field returns constant states
  - Output shapes are correct
  - No NaN on smooth fields
  - No negative rho or p (or safety fallback works)
- [ ] `pytest -q` passes
- [ ] **Must run analytic validation**:
  - `python examples/run_cfd_entropy_wave.py`
  - `python examples/run_cfd_entropy_wave_convergence.py`
  - `python examples/run_cfd_isentropic_vortex.py`
  - `python examples/run_cfd_isentropic_vortex_convergence.py`
- [ ] Errors must NOT increase significantly vs. previous method
- [ ] `docs/cfd_module_interfaces.md` updated with new parameters
- [ ] `python tools/generate_cfd_api_docs.py` run
- [ ] Final report includes: convergence table, comparison with previous method

---

## 4. Add Limiter

**Applies when**: Adding a new slope limiter (e.g., superbee, MC).

- [ ] `cfd/numerics/limiters.py` updated:
  - New limiter function `(a, b) -> result` (vectorized, no NaN)
  - Registered in `LIMITERS` dict
- [ ] `cfd/numerics/__init__.py` updated to export
- [ ] Unit tests in `tests/test_cfd_limiters.py`:
  - Same sign returns smaller (or correct blend)
  - Opposite sign returns zero
  - No NaN at zero input
  - Array shapes preserved
  - `get_limiter(name)` returns correct function
- [ ] `pytest -q` passes
- [ ] **Must run analytic validation** with the new limiter in MUSCL mode:
  - `python examples/run_cfd_isentropic_vortex.py`
  - `python examples/run_cfd_isentropic_vortex_convergence.py`
- [ ] `python tools/generate_cfd_api_docs.py` run
- [ ] `docs/cfd_module_interfaces.md` updated
- [ ] Final report includes: limiter behavior tests, convergence comparison

---

## 5. Add Riemann Solver

**Applies when**: Adding a new numerical flux (e.g., HLLC, Roe).

- [ ] `cfd/numerics/riemann.py` updated:
  - `<solver>_flux_x(UL, UR, gamma)` and `<solver>_flux_y(UL, UR, gamma)`
- [ ] `cfd/numerics/update.py` updated: dispatch on `flux_type`
- [ ] `cfd/config.py` updated: `flux_type` docstring lists new option
- [ ] Unit tests:
  - Flux shapes correct
  - Flux consistent (same left/right gives physical flux)
  - Entropy condition (where applicable)
- [ ] `pytest -q` passes
- [ ] **Must run analytic validation**:
  - `python examples/run_cfd_entropy_wave.py`
  - `python examples/run_cfd_entropy_wave_convergence.py`
  - `python examples/run_cfd_isentropic_vortex.py`
  - `python examples/run_cfd_isentropic_vortex_convergence.py`
- [ ] `python tools/generate_cfd_api_docs.py` run
- [ ] `docs/cfd_module_interfaces.md` updated
- [ ] Final report includes: convergence table, comparison with Rusanov

---

## 6. Add Time Integrator

**Applies when**: Adding a new time-stepping method (e.g., RK3, RK4).

- [ ] `cfd/numerics/time_integration.py` updated:
  - New `_method_step()` function
  - Dispatch branch in `advance()`
- [ ] `cfd/config.py` updated: `time_integrator` docstring lists new option
- [ ] Unit tests in `tests/test_cfd_time_integration.py`:
  - Uniform flow preserved
  - Unknown integrator raises ValueError
  - Runs to completion on non-trivial case
- [ ] `pytest -q` passes
- [ ] **Must run analytic validation**:
  - `python examples/run_cfd_entropy_wave.py`
  - `python examples/run_cfd_isentropic_vortex.py`
  - `python examples/run_cfd_isentropic_vortex_convergence.py`
- [ ] `python tools/generate_cfd_api_docs.py` run
- [ ] `docs/cfd_module_interfaces.md` updated
- [ ] Final report includes: convergence table, stability observations

---

## 7. Add Output/Analysis Script

**Applies when**: Adding a new example script, plotting utility, or analysis tool.

- [ ] Script created in `examples/` (or `tools/`)
- [ ] Script runs without error: `python examples/<script>.py`
- [ ] Output files generated to `results/` directory
- [ ] Script does NOT modify source code (analysis only)
- [ ] `pytest -q` passes (no regressions)
- [ ] README.md updated if script is user-facing

---

## Universal Checklist (applies to ALL tasks)

- [ ] `python -m compileall solver cfd tests examples tools` — no syntax errors
- [ ] `pytest -q` — all tests pass
- [ ] No unrelated files modified
- [ ] Final report includes:
  1. Changed files list
  2. Test output
  3. Numerical assumptions
  4. Remaining risks
  5. Error metrics (if applicable)
  6. Result file paths
  7. Generated docs
