# API: cfd.numerics_limiters

Slope limiters for high-order reconstruction.

Responsibilities:
    - Provide limiter functions (minmod, etc.) for MUSCL-type reconstruction.
    - Currently NOT connected to the main solver loop — reserved for future use.

Does NOT:
    - Perform reconstruction itself (see reconstruction.py).

Extension notes:
    To use in MUSCL, compute slopes and limit them with one of these functions
    before passing to the reconstruction step.

## Functions

### `minmod(a, b)`
Minmod limiter: returns the smaller slope in magnitude if signs agree, else 0.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
