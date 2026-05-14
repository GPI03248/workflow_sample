# 2D Isentropic Vortex Validation

## Analytic Solution

Advected isentropic vortex: smooth nonlinear Euler flow.

## Error Summary

| Method | rho L2 | rho Linf |
|--------|--------|----------|
| baseline | 1.136527e-01 | 9.720926e-02 |
| muscl_minmod_rk2 | 2.661321e-02 | 2.424867e-02 |

## Notes

- Baseline: piecewise_constant + forward Euler (1st order expected).
- MUSCL+minmod+SSP_RK2: higher-order spatial + temporal (2nd order expected).
