# API: cfd.boundary_conditions

Individual boundary condition implementations.

Each function operates on the full conservative array U with shape (4, nyt, nxt).

Responsibilities:
    - Fill ghost cells according to the specified boundary type.

Does NOT:
    - Decide which boundary to apply (see ghost_cells.py).

## Functions

### `periodic_x(U, ng)`
Periodic boundary in x: wrap around.

### `periodic_y(U, ng)`
Periodic boundary in y: wrap around.

### `transmissive_x(U, ng)`
Transmissive (outflow / zero-gradient) in x.

### `transmissive_y(U, ng)`
Transmissive (outflow / zero-gradient) in y.

### `reflective_x(U, ng)`
Reflective wall in x: normal velocity (u) is negated.

### `reflective_y(U, ng)`
Reflective wall in y: normal velocity (v) is negated.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
