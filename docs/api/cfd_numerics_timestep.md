# API: cfd.numerics_timestep

CFL-based time-step computation.

Responsibilities:
    - Compute dt from CFL condition: dt = cfl * min(dx, dy) / max_wavespeed.

Does NOT:
    - Advance the solution (see update.py, time_integration.py).

## Functions

### `compute_dt(U, dx, dy, cfl, gamma)`
Compute time step from CFL condition.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
