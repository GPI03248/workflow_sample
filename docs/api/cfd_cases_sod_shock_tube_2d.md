# API: cfd.cases_sod_shock_tube_2d

2D Sod-like shock tube case.

Responsibilities:
    - Provide config and initial condition for a 2D Sod shock tube.
    - x-direction: Sod Riemann problem; y-direction: uniform / transmissive.

Does NOT:
    - Run the solver.

## Functions

### `sod_2d_config()`
Return a CFDConfig for the 2D Sod shock tube.

### `sod_2d_ic(nxt, nyt, x_center, gamma)`
Sod shock tube initial condition on a 2D grid.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
