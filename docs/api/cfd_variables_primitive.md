# API: cfd.variables_primitive

Primitive variable container.

Responsibilities:
    - Provide a thin wrapper around a raw NumPy array for primitive variables.
    - Primitive ordering: [rho, u, v, p], shape (4, nyt, nxt).

Does NOT:
    - Perform conversions (see conversion.py).

## Classes

- **PrimitiveArray**
  — Lightweight container for primitive variables V = [rho, u, v, p].

## Functions

### `rho(self)`

### `u(self)`

### `v(self)`

### `p(self)`

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
