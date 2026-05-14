# API: cfd.numerics_riemann

Riemann solvers / numerical flux functions.

Responsibilities:
    - Compute numerical flux at cell interfaces.
    - Currently implements Rusanov (local Lax-Friedrichs).

Does NOT:
    - Perform reconstruction (see reconstruction.py).

## Functions

### `rusanov_flux_x(UL, UR, gamma)`
Rusanov (local Lax-Friedrichs) numerical flux in x.

### `rusanov_flux_y(UL, UR, gamma)`
Rusanov (local Lax-Friedrichs) numerical flux in y.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
