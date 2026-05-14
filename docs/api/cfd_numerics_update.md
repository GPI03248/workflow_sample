# API: cfd.numerics_update

Conservative variable update (forward Euler).

Responsibilities:
    - Compute the net flux divergence and update U by one time step.
    - Apply the update only to interior cells.

Does NOT:
    - Compute dt (see timestep.py).
    - Handle boundary conditions (see boundary/).

## Functions

### `euler_update(U, dx, dy, dt, ng, gamma, flux_type, reconstruction)`
Forward Euler update: U^{n+1} = U^n - dt * (dF/dx + dG/dy).

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
