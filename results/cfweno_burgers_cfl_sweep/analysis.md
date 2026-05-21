# CFWENO3 Burgers CFL Sensitivity Study

## Setup

Equation: u_t + (u^2/2)_x = 0, periodic BC

CFL values: [0.1, 0.3, 0.5]

Grid sizes: [80, 160, 320]

Reference: CFWENO3 Burgers nx=2560, CFL=0.5

final_time = 0.1

IC: u(x,0) = 1 + 0.2*sin(2*pi*x)

predictor_iterations = 1

## Error Table

| CFL | nx | Steps | L1 | L2 | Linf |
|-----|----|-------|----|----|------|
| 0.1 | 80 | 96 | 6.236449e-06 | 7.119492e-06 | 1.267816e-05 |
| 0.1 | 160 | 192 | 1.541093e-06 | 1.757230e-06 | 3.107236e-06 |
| 0.1 | 320 | 384 | 3.752847e-07 | 4.275636e-07 | 7.532651e-07 |
| 0.3 | 80 | 32 | 9.771116e-06 | 1.115742e-05 | 1.996771e-05 |
| 0.3 | 160 | 64 | 2.420225e-06 | 2.761567e-06 | 4.925792e-06 |
| 0.3 | 320 | 128 | 5.945838e-07 | 6.777765e-07 | 1.205439e-06 |
| 0.5 | 80 | 20 | 1.248134e-05 | 1.423088e-05 | 2.530918e-05 |
| 0.5 | 160 | 39 | 3.104787e-06 | 3.540194e-06 | 6.297048e-06 |
| 0.5 | 320 | 77 | 7.680890e-07 | 8.752875e-07 | 1.554982e-06 |

## Analysis

### Stability

All CFL values (0.1, 0.3, 0.5) produce stable, finite results. No NaN or Inf values observed.

### CFL impact on accuracy

- nx=80: best CFL=0.1, worst CFL=0.5, ratio=2.00x
- nx=160: best CFL=0.1, worst CFL=0.5, ratio=2.01x
- nx=320: best CFL=0.1, worst CFL=0.5, ratio=2.05x

### Recommendations

CFL=0.5 provides a good balance between accuracy and computational cost (fewer time steps). The CFWENO3 stencil is empirically stable up to CFL=0.5 for this smooth pre-shock Burgers case.
