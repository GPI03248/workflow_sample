# API: cfd.physics_fluxes

Euler equation physical flux functions.

Responsibilities:
    - Compute the physical flux vectors F(U) and G(U) for the 2D Euler equations.

Does NOT:
    - Compute numerical fluxes (see cfd/numerics/riemann.py).

## Functions

### `euler_flux_x(U, gamma)`
Physical flux in x-direction.

### `euler_flux_y(U, gamma)`
Physical flux in y-direction.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
