# Advection Benchmark Analysis

## PDE Problem Setup

Equation:  u_t + a * u_x = 0,  a = 1.0

Domain:  x in [0, 1), periodic boundary

Initial condition:  u(x, 0) = sin(2*pi*x) + 1

## Analytic Solution

u_exact(x, t) = sin(2*pi*(x - a*t)) + 1

## Numerical Parameters

- nx = 100
- CFL = 0.5
- requested final_time = 0.25
- actual final_time = 0.250000

## Error Summary

| Scheme | L1 | L2 | Linf | Mass |
|--------|----|----|------|------|
| upwind | 1.552083e-02 | 1.723647e-02 | 2.436403e-02 | 0.000000e+00 |
| lax_wendroff | 4.933090e-04 | 5.479955e-04 | 7.749610e-04 | 1.421085e-16 |

## Qualitative Observations

- **Upwind** is a first-order scheme. It introduces significant numerical dissipation, which smooths the solution and reduces the peak amplitude. For smooth periodic problems this dissipation is the dominant error source.

- **Lax-Wendroff** is a second-order scheme. It has lower dissipation than upwind on smooth solutions, typically yielding smaller L2 errors. However, it introduces dispersive oscillations that can become pronounced near discontinuities or sharp gradients.

- The current benchmark uses a **smooth, periodic** initial condition (sinusoidal). Results here do **not** generalise to all CFD problems — discontinuous or multi-dimensional cases may show very different behaviour.

- The purpose of this sample is to demonstrate a **repeatable verification mechanism** using an analytic solution, not to claim that one scheme is universally better than another.
