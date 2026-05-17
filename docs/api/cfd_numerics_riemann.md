# API: cfd.numerics_riemann

Riemann solvers / numerical flux functions.

Responsibilities:
    - Compute numerical flux at cell interfaces.
    - Implements Rusanov (local Lax-Friedrichs) and HLL (Harten-Lax-van Leer).

Does NOT:
    - Perform reconstruction (see reconstruction.py).

## Functions

### `rusanov_flux_x(UL, UR, gamma)`
Rusanov (local Lax-Friedrichs) numerical flux in x.

### `rusanov_flux_y(UL, UR, gamma)`
Rusanov (local Lax-Friedrichs) numerical flux in y.

### `hll_flux_x(UL, UR, gamma)`
HLL (Harten-Lax-van Leer) numerical flux in x.

### `hll_flux_y(UL, UR, gamma)`
HLL (Harten-Lax-van Leer) numerical flux in y.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
