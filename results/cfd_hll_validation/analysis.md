# HLL Riemann Solver Validation

## Method

HLL (Harten-Lax-van Leer) approximate Riemann solver.
Uses Roe-averaged wave speed estimates for S_L and S_R.

## Results

| Case | Riemann | rho L2 | rho Linf | rho mass |
|------|---------|--------|----------|----------|
| entropy_wave | rusanov | 1.592872e-02 | 2.287901e-02 | 2.053913e-17 |
| uniform_flow | rusanov | 0.000000e+00 | 0.000000e+00 | 0.000000e+00 |
| entropy_wave | hll | 1.072673e-02 | 1.563323e-02 | 3.275158e-17 |
| uniform_flow | hll | 0.000000e+00 | 0.000000e+00 | 0.000000e+00 |

## Notes

- HLL is an approximate Riemann solver (two-wave model).
- This validation only demonstrates behavior on the tested benchmarks.
- HLL may not outperform Rusanov on all problems.
- HLLC (three-wave solver) is not yet implemented.
- HLL/Rusanov L2 ratio (entropy wave): 0.6734
  HLL produces lower errors than Rusanov on this case, as expected.
