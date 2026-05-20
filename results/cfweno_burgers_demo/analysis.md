# CFWENO3 Burgers Scalar Prototype — Demo Results

## Source

- **Paper**: Zhou-Dong-Pan (2025), *Physics of Fluids* 37, 106131
- **Equation**: u_t + (u^2/2)_x = 0 (1D scalar nonlinear Burgers)
- **Stencil**: Eq. (30) — CFWENO3 with per-cell nu = dt * a_i / dx
- **Spec**: `docs/scheme_specs/cfweno_scalar_burgers_subset.md`

## What This Is

- A **1D scalar nonlinear Burgers CFWENO3 prototype**
- Single-stage, compact stencil scheme with SFM flux linearization
- **Pre-shock only** — final_time before shock formation
- **Not** shock-capturing — no claim of oscillation control
- **Not** the full CFWENO scheme (no Euler, no 2D, no CFWENO5/7)

## Parameters

- nx = 100
- CFL = 0.5
- final_time = 0.15
- IC: u0 = 1 + 0.2 * sin(2*pi*x)
- predictor_iterations = 1
- Reference: CFWENO3 Burgers on nx=2560 grid (numerical reference)
- BC: periodic

## Error Summary

| Method | L1 | L2 | Linf | Mass |
|--------|----|----|------|------|
| rusanov | 2.230538e-03 | 2.495961e-03 | 3.789090e-03 | 0.000000e+00 |
| cfweno_burgers | 1.228822e-05 | 1.444179e-05 | 2.792812e-05 | 1.421085e-16 |

## Notes

- Reference is a **numerical reference** (fine-grid CFWENO3), not an exact analytic solution.
- Errors are measured against the interpolated reference.
- Pre-shock smooth case only — results may differ for post-shock.
- Mass conservation should hold to near machine precision.
