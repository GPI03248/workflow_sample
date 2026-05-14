# API: cfd.boundary_ghost_cells

High-level ghost-cell application.

Responsibilities:
    - Dispatch to the correct boundary condition functions based on config.

Does NOT:
    - Implement individual BC logic (see conditions.py).

## Functions

### `apply_boundary_conditions(U, ng, bc_x, bc_y)`
Apply boundary conditions to ghost cells (in-place).

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
