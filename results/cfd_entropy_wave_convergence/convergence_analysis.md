# Entropy Wave Convergence Study

## Setup

- 2D compressible Euler, ideal gas (gamma=1.4)
- Advected entropy wave, periodic BC
- CFL = 0.4, final_time = 0.1
- Rusanov flux + piecewise-constant reconstruction + forward Euler

## Results

| nx=ny | dx | rho L1 | rho L2 | rho Linf | order(L1) | order(L2) | order(Linf) |
|-------|-----|--------|--------|----------|-----------|-----------|-------------|
| 32 | 0.031250 | 1.233273e-02 | 1.368688e-02 | 1.970132e-02 | nan | nan | nan |
| 64 | 0.015625 | 6.472427e-03 | 7.189797e-03 | 1.042433e-02 | 0.93 | 0.93 | 0.92 |
| 128 | 0.007812 | 3.319017e-03 | 3.687488e-03 | 5.373958e-03 | 0.96 | 0.96 | 0.96 |

## Notes

- Piecewise-constant reconstruction + Rusanov flux + forward Euler
  is expected to give **first-order** convergence.
- Higher-order reconstruction (MUSCL) or time integration (RK2/RK3)
  would be needed to achieve second-order or higher.
