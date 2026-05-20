# CFWENO3 Scalar Prototype — Demo Results

## Source

This CFWENO3 prototype is derived from a real paper:

- **Paper**: Zhou-Dong-Pan (2025), *Physics of Fluids* 37, 106131
- **Equation**: u_t + a*u_x = 0 (1D scalar linear advection)
- **Stencil**: Eq. (30) — Compact Fully-discrete WENO, 3rd order
- **Spec**: `docs/scheme_specs/cfweno_scalar_subset.md`

## What This Is

- A **1D scalar linear advection prototype** of CFWENO3
- Single-stage, compact stencil scheme
- Uses paper Eq. (30) for the CFWENO3 compact reconstruction
- **Not** the full CFWENO scheme (no Euler, no 2D, no CFWENO5/7)
- **Not** a shock-capturing scheme (linear prototype only)
- **Not** an entropy-satisfying Euler solver

## Parameters

- nx = 100
- CFL = 0.5
- final_time = 0.250000
- IC: u(x,0) = sin(2*pi*x) + 1
- BC: periodic

## Error Summary

| Method | L1 | L2 | Linf | Mass |
|--------|----|----|------|------|
| upwind | 1.552083e-02 | 1.723647e-02 | 2.436403e-02 | 0.000000e+00 |
| lax_wendroff | 4.933090e-04 | 5.479955e-04 | 7.749610e-04 | 1.421085e-16 |
| cfweno | 1.300211e-06 | 1.443934e-06 | 2.041023e-06 | 1.421085e-16 |

## Observations

- CFWENO3 L2 error is **11937.2x smaller** than upwind
- CFWENO3 L2 error is **379.5x smaller** than Lax-Wendroff
- These results are for **smooth linear advection only** — discontinuous or nonlinear problems may show different behaviour
- CFWENO3 achieves ~3rd order convergence on smooth data
- Mass conservation: mass error should be near machine precision
