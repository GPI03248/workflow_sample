# API: cfd.config

Solver configuration dataclass.

Responsibilities:
    - Hold all solver parameters in one place.
    - Provide sensible defaults for 2D Euler on a uniform Cartesian grid.

Does NOT:
    - Perform any computation.

## Classes

- **CFDConfig**
  — Configuration for the 2D Euler solver.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
