# CFWENO3 Burgers Convergence Study

## Setup

Equation: u_t + (u^2/2)_x = 0, periodic BC

Grid sizes: [40, 80, 160, 320]

Reference: CFWENO3 Burgers nx=2560

CFL = 0.5, final_time = 0.15

IC: u(x,0) = 1 + 0.2*sin(2*pi*x)

predictor_iterations = 1

## Error Table

| Method | nx | dx | L1 | L2 | Linf | Mass |
|--------|----|----|----|----|------|------|
| rusanov | 40 | 2.5000e-02 | 5.628828e-03 | 6.287622e-03 | 9.508400e-03 | 0.000000e+00 |
| cfweno_burgers | 40 | 2.5000e-02 | 7.680143e-05 | 9.086200e-05 | 1.758218e-04 | 0.000000e+00 |
| rusanov | 80 | 1.2500e-02 | 2.798562e-03 | 3.130601e-03 | 4.754797e-03 | 0.000000e+00 |
| cfweno_burgers | 80 | 1.2500e-02 | 1.921964e-05 | 2.260623e-05 | 4.364543e-05 | 0.000000e+00 |
| rusanov | 160 | 6.2500e-03 | 1.397127e-03 | 1.564621e-03 | 2.381929e-03 | 0.000000e+00 |
| cfweno_burgers | 160 | 6.2500e-03 | 4.769106e-06 | 5.604267e-06 | 1.081224e-05 | 0.000000e+00 |
| rusanov | 320 | 3.1250e-03 | 6.970551e-04 | 7.808909e-04 | 1.190050e-03 | 0.000000e+00 |
| cfweno_burgers | 320 | 3.1250e-03 | 1.177121e-06 | 1.382391e-06 | 2.666439e-06 | 0.000000e+00 |

## Convergence Orders (L2)

| Method | Order estimate | Expected |
|--------|---------------|----------|
| rusanov | 1.00 (from [1.0060746309389113, 1.0006265755260284, 1.0026202792870664]) | ~1 |
| cfweno_burgers | 2.01 (from [2.006956861417415, 2.012122683705807, 2.019359442972163]) | ~3 |

## Notes

- CFWENO3 Burgers uses per-cell nu = dt * a_i / dx with predictor iterations
- Default predictor_iterations = 1
- Reference is **numerical** (fine-grid CFWENO3), not exact analytic
- Pre-shock smooth case only
- Convergence orders are approximate due to numerical reference
