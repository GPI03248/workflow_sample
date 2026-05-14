# API: cfd.cases_entropy_wave

2D advected entropy wave — analytic validation case for Euler solver.

Responsibilities:
    - Provide an exact solution for the 2D compressible Euler equations.
    - The entropy wave is advected at constant velocity with periodic BCs.
    - Density has a sinusoidal perturbation; pressure and velocity are constant.

Does NOT:
    - Run the solver.

Analytic solution:
    rho(x,y,t) = rho0 + eps * sin(2*pi*(kx*(x - u0*t) + ky*(y - v0*t)))
    u(x,y,t) = u0
    v(x,y,t) = v0
    p(x,y,t) = p0
    E = p0/(gamma-1) + 0.5*rho*(u0^2 + v0^2)

## Classes

- **EntropyWaveParams**
  — Parameters for the advected entropy wave.

## Functions

### `entropy_wave_config(params)`
Return a CFDConfig for the entropy wave validation case.

### `entropy_wave_primitive(X, Y, t, params)`
Compute primitive variables for the entropy wave at time *t*.

### `entropy_wave_conservative(X, Y, t, params)`
Compute conservative variables for the entropy wave at time *t*.

### `entropy_wave_exact_solution(mesh, t, params)`
Compute exact conservative solution on *mesh* at time *t*.

### `entropy_wave_ic(nxt, nyt, gamma, params)`
Initial condition compatible with run_solver's IC signature.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
