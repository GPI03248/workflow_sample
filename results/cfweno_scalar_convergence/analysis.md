# CFWENO3 Scalar Convergence Study

## Setup

Equation: u_t + a*u_x = 0, a = 1.0, periodic BC

Grid sizes: [40, 80, 160, 320]

CFL = 0.5, final_time = 0.25

IC: u(x,0) = sin(2*pi*x) + 1

## Error Table

| Method | nx | dx | L1 | L2 | Linf | Mass |
|--------|----|----|----|----|------|------|
| upwind | 40 | 2.5000e-02 | 3.816049e-02 | 4.234208e-02 | 5.969616e-02 | 0.000000e+00 |
| cfweno | 40 | 2.5000e-02 | 2.099310e-05 | 2.329350e-05 | 3.284044e-05 | 1.776357e-16 |
| upwind | 80 | 1.2500e-02 | 1.934511e-02 | 2.148150e-02 | 3.035600e-02 | 0.000000e+00 |
| cfweno | 80 | 1.2500e-02 | 2.548567e-06 | 2.830019e-06 | 3.999165e-06 | 0.000000e+00 |
| upwind | 160 | 6.2500e-03 | 9.743413e-03 | 1.082152e-02 | 1.530098e-02 | 0.000000e+00 |
| cfweno | 160 | 6.2500e-03 | 3.162023e-07 | 3.511899e-07 | 4.965618e-07 | 0.000000e+00 |
| upwind | 320 | 3.1250e-03 | 4.890019e-03 | 5.431358e-03 | 7.680731e-03 | 0.000000e+00 |
| cfweno | 320 | 3.1250e-03 | 3.945122e-08 | 4.381858e-08 | 6.196585e-08 | 0.000000e+00 |

## Convergence Orders (L2)

| Method | Order estimate | Expected |
|--------|---------------|----------|
| upwind | 0.99 (from [0.9789976944908, 0.9891920232947704, 0.9945175868748107]) | 1.0 |
| cfweno | 3.02 (from [3.041044132043, 3.010488262536253, 3.002636813162355]) | 3.0 |

## Notes

- CFWENO3 is a 3rd-order compact fully-discrete scheme
- Target convergence order is ~3.0 for L2 error
- This is a prototype — exact convergence order may vary
- Upwind is 1st-order (baseline)
