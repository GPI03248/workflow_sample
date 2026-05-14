# API: cfd.cases_isentropic_vortex

2D isentropic vortex — analytic validation case for Euler solver.

Responsibilities:
    - Provide an exact solution for the 2D compressible Euler equations.
    - The vortex is a smooth, nonlinear flow that is advected at constant velocity.
    - More complex than the entropy wave: velocity and density both vary.

Does NOT:
    - Run the solver.

Analytic solution:
    dx = x - (x0 + u_inf*t),  dy = y - (y0 + v_inf*t),  r2 = dx^2 + dy^2
    du = -beta/(2*pi) * exp(0.5*(1 - r2)) * dy
    dv =  beta/(2*pi) * exp(0.5*(1 - r2)) * dx
    T = 1 - ((gamma-1)*beta^2)/(8*gamma*pi^2) * exp(1 - r2)
    rho = T^(1/(gamma-1))
    p = rho^gamma

## Classes

- **IsentropicVortexParams**
  — Parameters for the isentropic vortex.

## Functions

### `isentropic_vortex_config(params)`
Return a CFDConfig for the isentropic vortex.

### `isentropic_vortex_primitive(X, Y, t, params)`
Compute primitive variables for the isentropic vortex at time *t*.

### `isentropic_vortex_conservative(X, Y, t, params)`
Compute conservative variables. Returns U, shape (4, ...).

### `isentropic_vortex_exact_solution(mesh, t, params)`
Exact conservative solution on *mesh* at time *t*.

### `isentropic_vortex_ic(nxt, nyt, gamma, params)`
IC compatible with run_solver. Uses domain [0,10]x[0,10], ng=2.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
