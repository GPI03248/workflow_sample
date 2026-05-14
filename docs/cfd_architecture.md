# CFD Solver Architecture

## Overview

The CFD solver is a Python/NumPy implementation of a 2D compressible Euler
equation solver for an ideal gas.  It is designed as a **minimum viable product**
that is correct, testable, and extensible.

## Equations

2D compressible Euler equations, ideal gas (gamma = 1.4):

```
dU/dt + dF(U)/dx + dG(U)/dy = 0

U   = [rho, rho*u, rho*v, E]

F(U) = [rho*u, rho*u^2 + p, rho*u*v, u*(E + p)]
G(U) = [rho*v, rho*u*v, rho*v^2 + p, v*(E + p)]

p = (gamma - 1) * (E - 0.5 * rho * (u^2 + v^2))
```

## Data Flow

```
Case config (cfd.config.CFDConfig)
  |
  v
Mesh generation (cfd.mesh.structured.StructuredMesh2D)
  |
  v
Initial condition (cfd.cases.*.py -> U array)
  |
  v
+------------------- Time loop -------------------+
|                                                  |
|  1. Apply boundary conditions (cfd.boundary)     |
|  2. Compute CFL dt (cfd.numerics.timestep)       |
|  3. Reconstruct at interfaces (cfd.numerics.reconstruction)
|  4. Compute Riemann flux (cfd.numerics.riemann)  |
|  5. Conservative update (cfd.numerics.update)    |
|                                                  |
+--------------------------------------------------+
  |
  v
Output (cfd.io.output -> CSV, NPZ, PNG, MD)
  |
  v
Validation (cfd.validation -> compare against analytic solution)
```

## Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `cfd.config` | Holds all solver parameters |
| `cfd.constants` | Physical indices, gamma, NVAR |
| `cfd.mesh` | Grid generation, cell centres, ghost layout |
| `cfd.variables` | Primitive <-> Conservative conversion |
| `cfd.physics` | EOS, physical fluxes, wave speeds |
| `cfd.boundary` | Ghost-cell boundary conditions |
| `cfd.numerics.reconstruction` | Piecewise constant + MUSCL reconstruction |
| `cfd.numerics.limiters` | Slope limiters (minmod, van Leer) |
| `cfd.numerics.riemann` | Numerical flux (Rusanov) |
| `cfd.numerics.timestep` | CFL dt computation |
| `cfd.numerics.update` | Spatial residual + Euler update |
| `cfd.numerics.time_integration` | Time loop (Euler, SSP RK2) |
| `cfd.cases` | Pre-built initial conditions |
| `cfd.validation` | Error metrics, analytic comparison |
| `cfd.io` | Result output |
| `cfd.solver` | Orchestration (ties everything together) |

## Array Layout

- Conservative array `U`: shape `(4, nyt, nxt)` where `nxt = nx + 2*ng`, `nyt = ny + 2*ng`
- `U[0]` = rho, `U[1]` = rho*u, `U[2]` = rho*v, `U[3]` = E
- Interior cells: `U[:, ng:-ng, ng:-ng]`
- Ghost cells: outer layers

## One Time Step (Call Sequence)

```python
# Forward Euler
apply_boundary_conditions(U, ng, bc_x, bc_y)
dt = compute_dt(U, dx, dy, cfl, gamma)
U = apply_euler_step(U, dx, dy, dt, ng, gamma, flux_type, reconstruction, limiter)

# SSP RK2
U1 = U + dt * compute_residual(U, dx, dy, ng, gamma, flux_type, reconstruction, limiter)
U = 0.5*U + 0.5*(U1 + dt * compute_residual(U1, dx, dy, ng, gamma, flux_type, reconstruction, limiter))
```

## How to Add Extensions

See `docs/cfd_iteration_guide.md` for detailed instructions on adding new
numerical methods, boundary conditions, and test cases.
