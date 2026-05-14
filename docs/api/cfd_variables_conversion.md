# API: cfd.variables_conversion

Primitive <-> conservative variable conversion.

Responsibilities:
    - Convert between primitive V = [rho, u, v, p] and conservative U = [rho, rho*u, rho*v, E].
    - Check for non-physical states.

Does NOT:
    - Perform any spatial operations.

## Functions

### `primitive_to_conservative(rho, u, v, p, gamma)`
Convert primitive variables to conservative.

### `conservative_to_primitive(U, gamma)`
Convert conservative variables to primitive.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
