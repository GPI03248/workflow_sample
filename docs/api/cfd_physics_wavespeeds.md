# API: cfd.physics_wavespeeds

Wave-speed estimation for CFL calculation.

Responsibilities:
    - Compute maximum wave speed |u| + c or |v| + c for the entire domain.

Does NOT:
    - Compute the actual dt (see numerics/timestep.py).

## Functions

### `max_wavespeed(U, gamma)`
Return (max_sx, max_sy) where sx = |u| + c, sy = |v| + c.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
