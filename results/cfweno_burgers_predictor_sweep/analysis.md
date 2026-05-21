# CFWENO3 Burgers Predictor Sensitivity Study

## Setup

Equation: u_t + (u^2/2)_x = 0, periodic BC

Predictor iterations: [0, 1, 2]

Grid sizes: [80, 160, 320]

Reference: CFWENO3 Burgers nx=2560, predictor=1

CFL = 0.5, final_time = 0.1

IC: u(x,0) = 1 + 0.2*sin(2*pi*x)

## Error Table

| Predictor | nx | L1 | L2 | Linf |
|-----------|----|----|----|------|
| 0 | 80 | 8.157827e-06 | 9.315127e-06 | 1.646960e-05 |
| 0 | 160 | 2.022117e-06 | 2.307546e-06 | 4.076516e-06 |
| 0 | 320 | 4.959500e-07 | 5.654055e-07 | 9.980606e-07 |
| 1 | 80 | 1.248134e-05 | 1.423088e-05 | 2.530918e-05 |
| 1 | 160 | 3.104787e-06 | 3.540194e-06 | 6.297048e-06 |
| 1 | 320 | 7.680890e-07 | 8.752875e-07 | 1.554982e-06 |
| 2 | 80 | 1.248401e-05 | 1.423766e-05 | 2.534372e-05 |
| 2 | 160 | 3.105115e-06 | 3.541044e-06 | 6.301653e-06 |
| 2 | 320 | 7.681306e-07 | 8.753945e-07 | 1.555566e-06 |

## Convergence Orders (L2)

| Predictor | Order (80->160) | Order (160->320) | Average |
|-----------|----------------|------------------|----------|
| 0 | 2.0132 | 2.0290 | 2.0211 |
| 1 | 2.0071 | 2.0160 | 2.0116 |
| 2 | 2.0075 | 2.0162 | 2.0118 |

## Analysis

### Which predictor has smallest error?

- nx=80: predictor=0 (L2=9.315127e-06)
- nx=160: predictor=0 (L2=2.307546e-06)
- nx=320: predictor=0 (L2=5.654055e-07)

### Does predictor improve convergence order?

All predictors yield approximately the same convergence order (range: 2.01–2.02). The predictor does **not** significantly change the convergence rate.

### Is default predictor_iterations=1 still reasonable?

Predictor=0 is slightly better at nx=320 (L2 ratio: 1.55x). The improvement is notable (1.55x). Consider changing the default to 0.

### Does the predictor need redesign?

No urgent redesign needed. All predictors yield ~2nd-order convergence, consistent with the per-cell nu variation limitation documented in the audit. A more fundamental change (e.g., nonlinear WENO weights or higher-order interface reconstruction) would be needed to improve convergence order.

### Scope limitation

This study only covers smooth pre-shock Burgers (T=0.1, T_shock≈0.253). Post-shock behavior is not tested and would require nonlinear WENO weights (Eq. 17) not yet implemented.
