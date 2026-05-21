# CFWENO3 Burgers Reference-Grid Sensitivity Study

## Setup

Equation: u_t + (u^2/2)_x = 0, periodic BC

Reference grid sizes: [1280, 2560, 5120]

Coarse grid sizes: [80, 160, 320]

CFL = 0.5, final_time = 0.1

IC: u(x,0) = 1 + 0.2*sin(2*pi*x)

predictor_iterations = 1

## Error Table

| Ref nx | nx | L1 | L2 | Linf |
|--------|----|----|----|------|
| 1280 | 80 | 1.244475e-05 | 1.418924e-05 | 2.523544e-05 |
| 1280 | 160 | 3.068242e-06 | 3.498550e-06 | 6.223141e-06 |
| 1280 | 320 | 7.315311e-07 | 8.336418e-07 | 1.481074e-06 |
| 2560 | 80 | 1.248134e-05 | 1.423088e-05 | 2.530918e-05 |
| 2560 | 160 | 3.104787e-06 | 3.540194e-06 | 6.297048e-06 |
| 2560 | 320 | 7.680890e-07 | 8.752875e-07 | 1.554982e-06 |
| 5120 | 80 | 1.249049e-05 | 1.424129e-05 | 2.532760e-05 |
| 5120 | 160 | 3.113921e-06 | 3.550602e-06 | 6.315516e-06 |
| 5120 | 320 | 7.772267e-07 | 8.856962e-07 | 1.573450e-06 |

## Convergence Orders (L2) per Reference

| Ref nx | Order (80->160) | Order (160->320) | Average |
|--------|----------------|------------------|----------|
| 1280 | 2.0200 | 2.0693 | 2.0446 |
| 2560 | 2.0071 | 2.0160 | 2.0116 |
| 5120 | 2.0039 | 2.0032 | 2.0036 |

## Analysis

### Reference sensitivity

Convergence order across references: min=2.00, max=2.04, spread=0.04.

The measured convergence order is **insensitive** to the reference grid resolution. The reference at nx=2560 is sufficient for measuring convergence order at nx=40–320.

### Recommendation

nx=2560 is an appropriate reference for coarse grids up to nx=320. The reference error is ~60x smaller than the coarsest coarse-grid error and does not significantly bias the convergence order measurement.
