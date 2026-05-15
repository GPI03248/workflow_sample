# HLL Approximate Riemann Solver for Compressible Euler Equations

> **NOTE**: This is a workflow test document, not a formal paper. It describes the
> HLL (Harten-Lax-van Leer) approximate Riemann solver for the purpose of testing
> the paper-to-code extraction, spec generation, and approval gate workflow.

---

## 1. Method Name

**HLL (Harten-Lax-van Leer) approximate Riemann solver**

Reference: Harten, A., Lax, P.D., and van Leer, B. (1983). "On Upstream Differencing
and Godunov-Type Schemes for Hyperbolic Conservation Laws." SIAM Review, 25(1), 35-61.

---

## 2. Target Equation

2D compressible Euler equations for an ideal gas (gamma = 1.4):

```
dU/dt + dF(U)/dx + dG(U)/dy = 0

U = [rho, rho*u, rho*v, E]
E = p / (gamma - 1) + 0.5 * rho * (u^2 + v^2)
```

The HLL solver computes a numerical flux at each cell interface given left and right
conservative states.

---

## 3. Left and Right Conservative States

At each x-direction interface:

```
UL = [rhoL, rhoL*uL, rhoL*vL, EL]
UR = [rhoR, rhoR*uR, rhoR*vR, ER]
```

At each y-direction interface:

```
UB = [rhoB, rhoB*uB, rhoB*vB, EB]
UT = [rhoT, rhoT*uT, rhoT*vT, ET]
```

These are obtained from the reconstruction step (piecewise constant or MUSCL).

---

## 4. Physical Fluxes

x-direction physical flux:

```
F(U) = [rho*u, rho*u^2 + p, rho*u*v, u*(E + p)]
```

y-direction physical flux:

```
G(U) = [rho*v, rho*u*v, rho*v^2 + p, v*(E + p)]
```

---

## 5. Wave Speed Estimates S_L and S_R

For the x-direction Riemann problem between UL and UR:

```
rho_hat = sqrt(rhoL * rhoR)
u_hat   = (sqrt(rhoL)*uL + sqrt(rhoR)*uR) / (sqrt(rhoL) + sqrt(rhoR))
H_hat   = (sqrt(rhoL)*HL + sqrt(rhoR)*HR) / (sqrt(rhoL) + sqrt(rhoR))
c_hat   = sqrt((gamma - 1) * (H_hat - 0.5 * u_hat^2))

S_L = min(uL - cL, u_hat - c_hat)
S_R = max(uR + cR, u_hat + c_hat)
```

where H = (E + p) / rho is the specific total enthalpy, and c = sqrt(gamma * p / rho)
is the sound speed.

For the y-direction, replace u with v and compute analogously:

```
S_B = min(vB - cB, v_hat - c_hat)
S_T = max(vT + cT, v_hat + c_hat)
```

---

## 6. HLL Flux Formula

### x-direction:

```
if S_L >= 0:
    F_HLL = F(UL)
elif S_R <= 0:
    F_HLL = F(UR)
else:
    F_HLL = (S_R * F(UL) - S_L * F(UR) + S_L * S_R * (UR - UL)) / (S_R - S_L)
```

### y-direction:

```
if S_B >= 0:
    G_HLL = G(UB)
elif S_T <= 0:
    G_HLL = G(UT)
else:
    G_HLL = (S_T * G(UB) - S_B * G(UT) + S_B * S_T * (UT - UB)) / (S_T - S_B)
```

---

## 7. Relation to Current Rusanov Flux

The current solver uses the Rusanov (local Lax-Friedrichs) flux:

```
F_Rusanov = 0.5 * (F(UL) + F(UR)) - 0.5 * S_max * (UR - UL)
```

where `S_max = max(|uL| + cL, |uR| + cR)`.

**Key differences:**
- Rusanov uses a single maximum wave speed; HLL uses two separate wave speeds S_L and S_R.
- HLL is less diffusive than Rusanov because it accounts for the asymmetry of wave
  speeds, especially when one wave is much faster than the other.
- Both are two-wave approximate solvers; HLL is a strict improvement over Rusanov
  in terms of accuracy while maintaining similar robustness.
- When S_L = -S_max and S_R = S_max, HLL reduces to Rusanov.

---

## 8. Expected Tests

1. **Flux shape test**: `hll_flux_x(UL, UR, gamma)` returns shape `(4, nyt, nxt-1)`.
2. **Flux shape test**: `hll_flux_y(UB, UT, gamma)` returns shape `(4, nyt-1, nxt)`.
3. **Consistency test**: When UL = UR, HLL flux equals the physical flux F(UL).
4. **Comparison test**: HLL flux should be less diffusive than Rusanov on smooth problems.
5. **Robustness test**: No NaN for moderate Mach number states.
6. **Integration test**: Full solver runs to completion with HLL flux on entropy wave and isentropic vortex cases.

---

## 9. Validation Suggestion

1. Run entropy wave validation with HLL + piecewise_constant + euler — expect ~1st order
   convergence, lower L2 error than Rusanov.
2. Run entropy wave convergence with HLL + MUSCL + SSP_RK2 — expect ~2nd order.
3. Run isentropic vortex with HLL + MUSCL + SSP_RK2 — expect ~2nd order convergence,
   lower L2 error than Rusanov at same resolution.
4. Run isentropic vortex convergence — verify observed order >= 1.8.
5. Compare L2 errors side-by-side with Rusanov at 32x32, 64x64, 128x128.

---

## 10. Limitations

1. HLL is a two-wave solver — it cannot resolve contact discontinuities or shear waves.
    For that, HLLC (a three-wave solver) is needed.
2. Wave speed estimates depend on Roe averages — if both states have the same density
    but opposite velocities, the Roe average velocity may be poorly conditioned.
3. No entropy fix is needed for HLL (it is inherently entropy-satisfying).
4. HLL assumes the Riemann solution consists of two waves enclosing a single
    intermediate state — this is exact for two-wave systems but approximate for the
    Euler equations (which have three wave families).
5. The implementation requires both x and y direction versions, following the same
    pattern as the existing `rusanov_flux_x` and `rusanov_flux_y` in `cfd/numerics/riemann.py`.
