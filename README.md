# Multi-Agent Workflow Sample

A Python project demonstrating **multi-agent / agentic coding workflows** with
two solvers:

1. **1D scalar advection** — toy solver with analytic-solution verification
2. **2D compressible Euler** — CPU full-field CFD solver MVP

## Purpose

This project showcases a new engineering paradigm where AI agents handle
analysis, design, implementation, testing, and review in a structured workflow:

| Traditional (script) | Agentic (this project) |
|---|---|
| Human reads the request | repo-analyst agent reads the repo |
| Human designs the scheme | scheme-designer agent creates a plan |
| Human writes code | implementer agent makes minimal edits |
| Human writes tests | test-engineer agent adds and runs tests |
| Human reviews | reviewer agent checks the diff |
| Human follows a checklist | skill encodes the workflow once, runs every time |
| Human remembers rules | hooks enforce rules automatically |

---

## Part 1: 1D Scalar Advection with Analytic Verification

The toy solver solves the **1D linear advection equation** with a known analytic
solution:

- **PDE**:  u_t + a * u_x = 0,  a = 1.0
- **Domain**:  x in [0, 1), periodic boundary
- **IC**:  u(x, 0) = sin(2*pi*x) + 1
- **Analytic**:  u_exact(x, t) = sin(2*pi*(x - a*t)) + 1
- **Schemes**: upwind (1st order), Lax-Wendroff (2nd order)

```bash
bash -ic 'module-conda && pytest -q'
bash -ic 'module-conda && python examples/compare_advection_schemes.py'
```

---

## Part 2: Python CPU CFD Full-Field Solver MVP

A minimal but complete **2D compressible Euler solver** for an ideal gas
(gamma = 1.4), implemented entirely in NumPy.

### Equations

```
dU/dt + dF(U)/dx + dG(U)/dy = 0

U = [rho, rho*u, rho*v, E]
p = (gamma - 1) * (E - 0.5 * rho * (u^2 + v^2))
```

### Supported Methods

| Component | Current | Extensible to |
|-----------|---------|--------------|
| Numerical flux | Rusanov (local Lax-Friedrichs) | HLLC, Roe |
| Reconstruction | Piecewise constant (1st order) | MUSCL, WENO |
| Limiters | minmod (reserved) | van Leer, superbee |
| Time integration | Forward Euler | RK2, RK3 |
| Boundary conditions | Periodic, transmissive, reflective | Inlet, outlet, far-field |

### CFD Directory Structure

```
cfd/
  config.py              — Solver configuration (CFDConfig dataclass)
  constants.py           — Index constants, gamma
  mesh/
    structured.py        — 2D uniform Cartesian grid with ghost cells
  variables/
    conversion.py        — Primitive <-> Conservative conversion
  physics/
    eos.py               — Equation of state (ideal gas)
    fluxes.py            — Euler physical flux F(U), G(U)
    wavespeeds.py        — Wave speed estimation
  boundary/
    conditions.py        — Periodic, transmissive, reflective BCs
    ghost_cells.py       — BC dispatch
  numerics/
    reconstruction.py    — Piecewise constant (MUSCL reserved)
    limiters.py          — minmod limiter (reserved)
    riemann.py           — Rusanov numerical flux
    timestep.py          — CFL dt computation
    update.py            — Conservative update (forward Euler)
    time_integration.py  — Time loop driver
  cases/
    uniform_flow.py      — Uniform flow preservation test
    sod_shock_tube_2d.py — 2D Sod shock tube
  io/
    output.py            — CSV, NPZ, PNG, MD output
  solver.py              — Orchestration entry point
```

### Run CFD Examples

```bash
# Uniform flow preservation (should be exact to machine precision)
bash -ic 'module-conda && python examples/run_cfd_uniform_flow.py'

# 2D Sod shock tube
bash -ic 'module-conda && python examples/run_cfd_sod_2d.py'
```

### View Results

Results are saved to `results/`:

| Case | Directory | Outputs |
|------|-----------|---------|
| Uniform flow | `results/cfd_uniform_flow/` | summary.csv, final_state.npz, analysis.md, density.png, pressure.png |
| Sod 2D | `results/cfd_sod_2d/` | summary.csv, final_state.npz, analysis.md, density.png, pressure.png, centerline_density.png |

### Generate API Docs

```bash
bash -ic 'module-conda && python tools/generate_cfd_api_docs.py'
```

### How to Add New Methods

See `docs/cfd_iteration_guide.md` for detailed instructions. Quick reference:

| To add... | Modify... |
|-----------|-----------|
| New flux | `cfd/numerics/riemann.py`, `cfd/numerics/update.py` |
| New reconstruction | `cfd/numerics/reconstruction.py` |
| New limiter | `cfd/numerics/limiters.py` |
| New time integrator | `cfd/numerics/time_integration.py` |
| New boundary condition | `cfd/boundary/conditions.py`, `cfd/boundary/ghost_cells.py` |
| New test case | `cfd/cases/`, `examples/` |

### Current Limitations

- **First-order accurate only** (piecewise constant reconstruction)
- **No turbulence modelling** (Euler equations only)
- **No adaptive mesh refinement**
- **No parallelisation** (single CPU thread)
- **No moving meshes or complex geometries**
- Forward Euler time integration limits effective CFL
- Rusanov flux is very diffusive — better fluxes needed for sharp shocks

---

## Analytic CFD Validation: 2D Advected Entropy Wave

The entropy wave is an exact solution of the 2D compressible Euler equations
with periodic boundary conditions, used to verify solver correctness and measure
convergence order.

### Equations and Analytic Solution

```
rho(x,y,t) = rho0 + eps * sin(2*pi*(kx*(x - u0*t) + ky*(y - v0*t)))
u(x,y,t) = u0
v(x,y,t) = v0
p(x,y,t) = p0
E = p0/(gamma-1) + 0.5*rho*(u0^2 + v0^2)
```

Default parameters: rho0=1, eps=0.1, u0=1, v0=0.5, p0=1, kx=1, ky=1, gamma=1.4.

This case is ideal for validation because:
- The exact solution is known at all times
- Periodic BCs are exact (no boundary artifacts)
- It tests the full Euler solver (conservative/primitive conversion, fluxes, CFL, update)
- Grid convergence can be measured against the analytic solution

### Run Validation

```bash
bash -ic 'module-conda && python examples/run_cfd_entropy_wave.py'
```

### Run Convergence Study

```bash
bash -ic 'module-conda && python examples/run_cfd_entropy_wave_convergence.py'
```

### View Results

```bash
cat results/cfd_entropy_wave/error_summary.csv
cat results/cfd_entropy_wave/analysis.md
cat results/cfd_entropy_wave_convergence/convergence_summary.csv
cat results/cfd_entropy_wave_convergence/convergence_analysis.md
```

Plots (if matplotlib is available):
- `results/cfd_entropy_wave/density_initial.png` — initial density field
- `results/cfd_entropy_wave/density_numerical.png` — numerical solution
- `results/cfd_entropy_wave/density_exact.png` — analytic solution
- `results/cfd_entropy_wave/density_error.png` — error field
- `results/cfd_entropy_wave/density_centerline_comparison.png` — overlay
- `results/cfd_entropy_wave_convergence/density_l2_convergence.png` — convergence plot

### Current Convergence Results

With Rusanov + piecewise constant + forward Euler:

| nx=ny | rho L2 error | Observed order |
|-------|-------------|----------------|
| 32 | 1.37e-02 | — |
| 64 | 7.19e-03 | 0.93 |
| 128 | 3.69e-03 | 0.96 |

Close to first-order, as expected for a first-order scheme.

---

## Installation

```bash
git clone git@gitee.com:gpiii/workflow_sample.git
cd workflow_sample
pip install numpy pytest matplotlib
```

> matplotlib is optional — scripts degrade gracefully without it.

## Run All Tests

```bash
bash -ic 'module-conda && pytest -q'
```

## Multi-Agent Workflow Demo

```
使用 add-numerical-scheme skill，根据 docs/feature_request_lax_wendroff.md 完成需求。
要求先分析仓库，再设计方案，再实现，再补测试，再审查。
不要修改无关文件。完成后运行 pytest -q，并给出最终报告。
```

## Documentation

| Document | Description |
|----------|-------------|
| `CLAUDE.md` | Project rules |
| `docs/cfd_architecture.md` | CFD solver architecture overview |
| `docs/cfd_module_interfaces.md` | Public interface reference |
| `docs/cfd_iteration_guide.md` | How to extend the solver |
| `docs/api/` | Auto-generated API docs |

## How This Maps to Real CFD Projects

| This project | Real CFD project |
|---|---|
| 2D Euler (NumPy) | 3D RANS/LES/DNS (C++/Fortran) |
| Rusanov flux | HLLC, WENO, DG schemes |
| 50x50 uniform grid | 10M+ cells, AMR |
| Forward Euler | RK3, IMEX, dual time stepping |
| np.roll / ghost cells | MPI halo exchange |
| pytest | Regression suites + verification cases |
| 5 agents | 10-20 agents (mesh, BC, I/O, performance, etc.) |
