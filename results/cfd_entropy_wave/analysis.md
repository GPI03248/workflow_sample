# 2D Advected Entropy Wave Validation

## PDE

2D compressible Euler equations, ideal gas (gamma=1.4)

## Analytic Solution

```
rho(x,y,t) = rho0 + eps * sin(2*pi*(kx*(x - u0*t) + ky*(y - v0*t)))
u(x,y,t) = u0
v(x,y,t) = v0
p(x,y,t) = p0
```

## Parameters

- rho0=1.0, eps=0.1, u0=1.0, v0=0.5, p0=1.0
- kx=1, ky=1
- nx=64, ny=64, cfl=0.4
- final_time=0.1, actual_final_time=0.100000
- Steps: 36
- reconstruction=piecewise_constant, riemann=rusanov, time_integrator=euler

## Error Summary

| Metric | Value |
|--------|-------|
| rho L1 | 6.472427e-03 |
| rho L2 | 7.189797e-03 |
| rho Linf | 1.042433e-02 |
| rho mass | 2.629190e-17 |

## Notes

- This case uses periodic boundary conditions, matching the analytic solution exactly.
- The solver uses piecewise-constant reconstruction + Rusanov flux + forward Euler,
  so first-order convergence is expected.
