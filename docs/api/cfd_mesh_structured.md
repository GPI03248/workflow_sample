# API: cfd.mesh_structured

2D uniform Cartesian structured mesh (cell-centered).

Responsibilities:
    - Define cell centres, cell sizes, ghost-cell layout.
    - Provide index helpers for interior vs ghost regions.

Does NOT:
    - Store solution data (that lives in the solver).

## Classes

- **StructuredMesh2D**
  — Uniform Cartesian mesh with ghost cells.

## Functions

### `interior_slice(self)`
Slice for interior cells: (ng:-ng, ng:-ng).

### `cell_centers_2d(self)`
Return 2-D arrays (X, Y) of cell centres, shape (nyt, nxt).

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
