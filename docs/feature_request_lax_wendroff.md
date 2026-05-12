# Feature Request: Add Lax-Wendroff Scheme

## Goal

Add a second-order Lax-Wendroff scheme to the `solver/schemes.py` module so that
`step(u, cfl, scheme="lax_wendroff")` becomes a valid call alongside the
existing `"upwind"` option.

## Requirements

1. Implement the Lax-Wendroff update in `solver/schemes.py`.
2. Register it in the `_SCHEMES` dict under the key `"lax_wendroff"`.
3. Do **not** modify the existing `upwind` function or its behaviour.
4. Keep the function signature identical: `(u: np.ndarray, cfl: float) -> np.ndarray`.
5. Use periodic boundaries via `np.roll` — no other boundary treatment.
6. Ensure the output array has the same shape as the input.
7. `step()` must no longer raise `ValueError` for `scheme="lax_wendroff"`.

## Lax-Wendroff Formula (1D, constant wave speed a > 0)

$$
u_j^{n+1} = u_j^n - \frac{c}{2}(u_{j+1}^n - u_{j-1}^n)
            + \frac{c^2}{2}(u_{j+1}^n - 2u_j^n + u_{j-1}^n)
$$

where $c = a \Delta t / \Delta x$ is the CFL number.

In numpy with periodic boundaries:

```python
u_right = np.roll(u, -1)   # u_{j+1}
u_left  = np.roll(u,  1)   # u_{j-1}
u_new = u - 0.5 * cfl * (u_right - u_left) \
          + 0.5 * cfl**2 * (u_right - 2*u + u_left)
```

## Test Requirements

Add or update tests to verify:

1. **Shape preservation** — `lax_wendroff` returns the same shape.
2. **Uniform field invariance** — a constant field stays constant.
3. **Mass conservation** — integral of u is preserved over many steps.
4. **Second-order accuracy hint** — after one full period the Lax-Wendroff peak
   should be sharper (less diffused) than the upwind peak.
5. **Registry check** — `step(u, cfl, scheme="lax_wendroff")` works without error.

## README Update

After implementation, update `README.md` to:

- List `"lax_wendroff"` as a supported scheme in the project structure section.
- Add a brief note that Lax-Wendroff is second-order and less diffusive than
  upwind, but can produce spurious oscillations near discontinuities.
