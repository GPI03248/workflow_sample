# API: cfd.variables_conservative

Conservative variable container.

Responsibilities:
    - Thin wrapper for conservative variables U = [rho, rho*u, rho*v, E].
    - Shape (4, nyt, nxt).

Does NOT:
    - Perform conversions (see conversion.py).

## Classes

- **ConservativeArray**
  — Lightweight container for conservative variables U = [rho, rho*u, rho*v, E].

## Functions

### `rho(self)`

### `rho_u(self)`

### `rho_v(self)`

### `E(self)`

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
