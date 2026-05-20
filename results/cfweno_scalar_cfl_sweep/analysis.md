# CFWENO3 Scalar CFL Sweep

## Setup

Equation: u_t + a*u_x = 0, a = 1.0, periodic BC

Grid: nx = 160

CFL values tested: [0.1, 0.5, 0.9]

final_time = 0.25

IC: u(x,0) = sin(2*pi*x) + 1

## Results

| CFL | Steps | L1 | L2 | Linf | Mass |
|-----|-------|----|----|------|------|
| 0.1 | 400 | 2.133791e-07 | 2.369977e-07 | 3.351441e-07 | 0.00e+00 |
| 0.5 | 80 | 3.162023e-07 | 3.511899e-07 | 4.965618e-07 | 0.00e+00 |
| 0.9 | 44 | 2.346982e-08 | 2.606975e-08 | 3.686782e-08 | 0.00e+00 |

## Notes

- CFL=0.9 is an **empirical verification** on this smooth case.
- This is **not** a rigorous stability proof.
- Results are valid only for this specific smooth linear advection case.
- All runs used the same grid resolution (nx=160).
- Mass conservation should hold to near machine precision.
- If any CFL value produces NaN or divergent results,
  that constitutes a failure and should be reported honestly.
