# API: cfd.numerics_limiters

Slope limiters for high-order reconstruction.

Responsibilities:
    - Provide limiter functions for MUSCL-type reconstruction.
    - All limiters take two slope arrays (a, b) and return limited slopes.

Does NOT:
    - Perform reconstruction itself (see reconstruction.py).

## Functions

### `minmod(a, b)`
Minmod limiter: returns the smaller slope in magnitude if signs agree, else 0.

### `van_leer(a, b)`
van Leer limiter: (a*b)(a+b) / (a^2 + b^2) when a*b > 0, else 0.

### `get_limiter(name)`
Return limiter function by name.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
