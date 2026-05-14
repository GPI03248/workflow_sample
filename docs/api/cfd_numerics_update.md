# API: cfd.numerics_update

Spatial discretisation and conservative variable update.

Responsibilities:
    - Compute the spatial residual L(U) = -(dF/dx + dG/dy).
    - Apply forward Euler or return residual for multi-stage methods.
    - Apply the update only to interior cells.

Does NOT:
    - Compute dt (see timestep.py).
    - Handle boundary conditions (see boundary/).
    - Implement time integration loops (see time_integration.py).

## Functions

### `compute_residual(U, dx, dy, ng, gamma, flux_type, reconstruction, limiter)`
Compute spatial residual L(U) = -(dF/dx + dG/dy) for interior cells.

### `apply_euler_step(U, dx, dy, dt, ng, gamma, flux_type, reconstruction, limiter)`
Apply one forward-Euler update to U in-place: U += dt * L(U).

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
