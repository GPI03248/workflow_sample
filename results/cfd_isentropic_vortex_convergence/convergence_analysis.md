# Isentropic Vortex Convergence

## Setup

- 2D Euler, periodic BC, domain [0,10]^2
- CFL=0.4, final_time=0.5

## baseline

| nx | dx | rho L2 | order(L2) |
|----|-----|--------|----------|
| 32 | 0.3125 | 1.965467e-01 | nan |
| 64 | 0.1562 | 1.136527e-01 | 0.79 |
| 128 | 0.0781 | 6.161644e-02 | 0.88 |

## muscl_minmod_rk2

| nx | dx | rho L2 | order(L2) |
|----|-----|--------|----------|
| 32 | 0.3125 | 7.407845e-02 | nan |
| 64 | 0.1562 | 2.661321e-02 | 1.48 |
| 128 | 0.0781 | 8.307849e-03 | 1.68 |

## Notes

- Baseline (piecewise_constant + Euler): ~1st order expected.
- MUSCL+minmod+SSP_RK2: higher order expected on smooth flow,
  but actual order depends on limiter, flux, and implementation details.
- These results are specific to this benchmark and do not generalise.
