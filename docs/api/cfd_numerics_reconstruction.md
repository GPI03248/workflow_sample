# API: cfd.numerics_reconstruction

Variable reconstruction at cell interfaces.

Responsibilities:
    - Reconstruct left/right states at cell interfaces.
    - Implements piecewise-constant (1st order) and MUSCL (2nd order).
    - MUSCL reconstructs in primitive variables for stability.

Does NOT:
    - Apply limiters directly (limiter is passed in).

## Functions

### `reconstruct(U, ng, method, limiter_name, gamma)`
Reconstruct left and right states at x-interfaces.

### `reconstruct_y(U, ng, method, limiter_name, gamma)`
Reconstruct bottom/top states at y-interfaces.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
