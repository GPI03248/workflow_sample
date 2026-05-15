# Scheme Specification

## Status
Approved for implementation: no

## Source
- paper: docs/papers/hll_flux_test_note.md (workflow test document)
- extraction report: docs/paper_reviews/hll_flux_test_note_extraction.md

## Scheme name
HLL (Harten-Lax-van Leer) approximate Riemann solver

## Scope
- target equation: 2D compressible Euler equations, dU/dt + dF/dx + dG/dy = 0
- dimension: 2D
- variable form: conservative U = [rho, rho*u, rho*v, E]
- supported mesh: structured Cartesian (existing solver mesh)
- supported boundary: all existing BCs (periodic, transmissive, reflective)

## Mathematical definition

### Physical fluxes (existing, from `cfd/physics/fluxes.py`)

x-direction:
```
F(U) = [rho*u, rho*u^2 + p, rho*u*v, u*(E + p)]
```

y-direction:
```
G(U) = [rho*v, rho*u*v, rho*v^2 + p, v*(E + p)]
```

### Primitive extraction from conservative states

```
rho = U[0]
u   = U[1] / rho
v   = U[2] / rho
E   = U[3]
p   = (gamma - 1) * (E - 0.5 * rho * (u^2 + v^2))
c   = sqrt(gamma * p / rho)
H   = (E + p) / rho
```

### Roe-averaged quantities (x-direction)

```
rho_hat = sqrt(rhoL * rhoR)
u_hat   = (sqrt(rhoL) * uL + sqrt(rhoR) * uR) / (sqrt(rhoL) + sqrt(rhoR))
H_hat   = (sqrt(rhoL) * HL + sqrt(rhoR) * HR) / (sqrt(rhoL) + sqrt(rhoR))
c_hat   = sqrt((gamma - 1) * (H_hat - 0.5 * u_hat^2))
```

where `HL = (EL + pL) / rhoL` and `HR = (ER + pR) / rhoR`.

### Wave speed estimates (x-direction)

```
S_L = min(uL - cL, u_hat - c_hat)
S_R = max(uR + cR, u_hat + c_hat)
```

### HLL numerical flux (x-direction)

```
if S_L >= 0:
    F_HLL = F(UL)
elif S_R <= 0:
    F_HLL = F(UR)
else:
    F_HLL = (S_R * F(UL) - S_L * F(UR) + S_L * S_R * (UR - UL)) / (S_R - S_L)
```

### Roe-averaged quantities (y-direction)

Replace u with v throughout:

```
v_hat = (sqrt(rhoB) * vB + sqrt(rhoT) * vT) / (sqrt(rhoB) + sqrt(rhoT))
H_hat = (sqrt(rhoB) * HB + sqrt(rhoT) * HT) / (sqrt(rhoB) + sqrt(rhoT))
c_hat = sqrt((gamma - 1) * (H_hat - 0.5 * v_hat^2))
```

### Wave speed estimates (y-direction)

```
S_B = min(vB - cB, v_hat - c_hat)
S_T = max(vT + cT, v_hat + c_hat)
```

### HLL numerical flux (y-direction)

```
if S_B >= 0:
    G_HLL = G(UB)
elif S_T <= 0:
    G_HLL = G(UT)
else:
    G_HLL = (S_T * G(UB) - S_B * G(UT) + S_B * S_T * (UT - UB)) / (S_T - S_B)
```

### Stability condition

Same CFL constraint as Rusanov: CFL <= 0.5 for forward Euler,
CFL <= 0.5 for SSP RK2. No additional restriction.

### Degenerate case

When `S_R == S_L` (both states identical or zero velocity), the denominator
`(S_R - S_L)` is zero. Guard with epsilon:

```
dS = S_R - S_L
if |dS| < eps:
    F_HLL = 0.5 * (F(UL) + F(UR))   # fallback to simple average
```

where `eps = 1e-14`.

## Variable mapping
| Paper symbol | Meaning | Code variable / module |
|---|---|---|
| UL | Left conservative state at x-interface | `UL` from `reconstruct()`, shape (4, nyt, nxt-1) |
| UR | Right conservative state at x-interface | `UR` from `reconstruct()`, shape (4, nyt, nxt-1) |
| UB | Bottom conservative state at y-interface | `UL` from `reconstruct_y()`, shape (4, nyt-1, nxt) |
| UT | Top conservative state at y-interface | `UR` from `reconstruct_y()`, shape (4, nyt-1, nxt) |
| rhoL, rhoR | Left/right density | `UL[0]`, `UR[0]` |
| uL, uR | Left/right x-velocity | `UL[1] / UL[0]`, `UR[1] / UR[0]` |
| vL, vR | Left/right y-velocity | `UL[2] / UL[0]`, `UR[2] / UR[0]` |
| pL, pR | Left/right pressure | `(gamma-1)*(UL[3] - 0.5*rhoL*(uL^2+vL^2))` etc. |
| cL, cR | Left/right sound speed | `sqrt(gamma * pL / rhoL)` etc. |
| HL, HR | Left/right total enthalpy | `(UL[3] + pL) / rhoL`, `(UR[3] + pR) / rhoR` |
| rho_hat | Roe-averaged density | `sqrt(rhoL * rhoR)` — new local variable |
| u_hat | Roe-averaged x-velocity | Roe formula — new local variable |
| H_hat | Roe-averaged enthalpy | Roe formula — new local variable |
| c_hat | Roe-averaged sound speed | From H_hat — new local variable |
| S_L, S_R | Wave speed bounds (x) | New local variables |
| S_B, S_T | Wave speed bounds (y) | New local variables |
| F(UL), F(UR) | Physical x-flux | `euler_flux_x(UL, gamma)`, `euler_flux_x(UR, gamma)` |
| G(UB), G(UT) | Physical y-flux | `euler_flux_y(UB, gamma)`, `euler_flux_y(UT, gamma)` |
| F_HLL | HLL numerical flux (x) | Return value of new `hll_flux_x()` |
| G_HLL | HLL numerical flux (y) | Return value of new `hll_flux_y()` |
| gamma | Ratio of specific heats | Function parameter, default from `cfd/constants.py` |

## Algorithm steps

### `hll_flux_x(UL, UR, gamma)` — x-direction HLL flux

1. Extract primitive quantities from `UL`:
   - `rhoL = UL[0]`
   - `uL = UL[1] / rhoL`
   - `vL = UL[2] / rhoL`
   - `pL = (gamma - 1) * (UL[3] - 0.5 * rhoL * (uL^2 + vL^2))`
   - `cL = sqrt(gamma * abs(pL) / rhoL)`
   - `HL = (UL[3] + pL) / rhoL`

2. Extract primitive quantities from `UR` (analogously):
   - `rhoR, uR, vR, pR, cR, HR`

3. Compute Roe averages:
   - `sqrtL = sqrt(rhoL)`, `sqrtR = sqrt(rhoR)`
   - `rho_hat = sqrt(rhoL * rhoR)`
   - `u_hat = (sqrtL * uL + sqrtR * uR) / (sqrtL + sqrtR)`
   - `H_hat = (sqrtL * HL + sqrtR * HR) / (sqrtL + sqrtR)`
   - `c_hat = sqrt(abs((gamma - 1) * (H_hat - 0.5 * u_hat^2)))`

4. Compute wave speeds:
   - `S_L = min(uL - cL, u_hat - c_hat)`
   - `S_R = max(uR + cR, u_hat + c_hat)`

5. Compute physical fluxes:
   - `FL = euler_flux_x(UL, gamma)`
   - `FR = euler_flux_x(UR, gamma)`

6. Compute HLL flux with vectorized conditionals:
   - `dS = S_R - S_L`
   - Where `S_L >= 0`: `F_HLL = FL`
   - Where `S_R <= 0`: `F_HLL = FR`
   - Otherwise (with epsilon guard on `dS`):
     `F_HLL = (S_R * FL - S_L * FR + S_L * S_R * (UR - UL)) / dS`

7. Return `F_HLL`, shape `(4, nyt, nxt-1)`.

### `hll_flux_y(UB, UT, gamma)` — y-direction HLL flux

Same algorithm with v replacing u, S_B/S_T replacing S_L/S_R,
`euler_flux_y` replacing `euler_flux_x`.

Return shape: `(4, nyt-1, nxt)`.

## Required code changes
| Module | Required change |
|---|---|
| `cfd/numerics/riemann.py` | Add `hll_flux_x(UL, UR, gamma)` and `hll_flux_y(UL, UR, gamma)`. Add helper `_roe_averages_x()` and `_roe_averages_y()` for wave speed computation. |
| `cfd/numerics/update.py` | Import `hll_flux_x`, `hll_flux_y`. In `compute_residual()`, add `if/elif` dispatch on `flux_type == "hll"` to call HLL fluxes instead of Rusanov. |
| `cfd/numerics/__init__.py` | Add `hll_flux_x`, `hll_flux_y` to exports. |
| `cfd/config.py` | Update `flux_type` docstring to list `"rusanov"` and `"hll"`. |
| `tests/test_cfd_fluxes.py` | Add tests for HLL flux: shape, consistency (UL==UR => physical flux), no NaN, comparison with Rusanov. |
| `docs/cfd_module_interfaces.md` | Add `hll_flux_x` and `hll_flux_y` signatures under `cfd.numerics`. |
| `docs/api/` | Regenerate with `python tools/generate_cfd_api_docs.py`. |

## Public API changes

- New functions:
  - `cfd.numerics.riemann.hll_flux_x(UL, UR, gamma=1.4) -> Fnum`
  - `cfd.numerics.riemann.hll_flux_y(UL, UR, gamma=1.4) -> Gnum`
- `CFDConfig.flux_type` docstring updated: `"rusanov"` or `"hll"`
- `compute_residual()` parameter `flux_type` now accepts `"hll"`
- No new config fields; no breaking changes; fully backward-compatible.

## Tests required

Per `docs/cfd_definition_of_done.md` Section 5 (Add Riemann Solver):

1. **Flux shape test**: `hll_flux_x(UL, UR, gamma)` returns shape `(4, nyt, nxt-1)`.
2. **Flux shape test**: `hll_flux_y(UB, UT, gamma)` returns shape `(4, nyt-1, nxt)`.
3. **Consistency test**: When `UL == UR`, `hll_flux_x(UL, UL, gamma) == euler_flux_x(UL, gamma)`.
4. **Robustness test**: No NaN for moderate Mach number states (uniform flow, rho=1, u=1, p=1).
5. **Epsilon guard test**: When UL == UR (S_R == S_L), no division-by-zero.
6. **Integration test**: Solver runs to completion with `flux_type="hll"` on a small grid.
7. **Analytic validation** (mandatory):
   - `python examples/run_cfd_entropy_wave.py` with `flux_type="hll"`
   - `python examples/run_cfd_entropy_wave_convergence.py` with `flux_type="hll"`
   - `python examples/run_cfd_isentropic_vortex.py` with `flux_type="hll"`
   - `python examples/run_cfd_isentropic_vortex_convergence.py` with `flux_type="hll"`

## Validation required

1. Entropy wave single run: L2 error should be lower than Rusanov at same resolution.
2. Entropy wave convergence: ~1st order with piecewise_constant + euler, ~2nd order with MUSCL + SSP_RK2.
3. Isentropic vortex single run: L2 error should be lower than Rusanov at same resolution.
4. Isentropic vortex convergence: ~2nd order with MUSCL + minmod + SSP_RK2, observed order >= 1.8.
5. Side-by-side comparison table: HLL vs. Rusanov L2 errors at 32x32, 64x64, 128x128.

## Expected behavior

- HLL flux is less diffusive than Rusanov because it uses two separate wave speed
  estimates (S_L, S_R) instead of a single maximum.
- On smooth problems (entropy wave, isentropic vortex), HLL should produce lower
  L2 errors at the same grid resolution.
- Convergence order should be the same as Rusanov for a given reconstruction/time
  integration combination (the flux type affects dissipation, not order).
- When S_L = -S_max and S_R = S_max (symmetric waves), HLL reduces to Rusanov.

## Known limitations

1. HLL is a two-wave solver — it cannot resolve contact discontinuities or shear
   waves. For those, HLLC (three-wave solver) is needed.
2. Roe-averaged wave speed estimates may be poorly conditioned when both states
   have the same density but opposite velocities.
3. No entropy fix needed (HLL is inherently entropy-satisfying).
4. The implementation assumes the existing reconstruction pipeline provides valid
   (positive rho, positive p) left/right states. No additional safety checks beyond
   the epsilon guard on `S_R - S_L`.

## Human confirmation checklist
- [ ] Formula checked — verify Roe average formulas and HLL flux expression against Harten-Lax-van Leer (1983)
- [ ] Variable mapping checked — confirm all paper symbols map correctly to code variables
- [ ] Compatibility checked — confirm HLL fits existing array layout (4, nyt, nxt) and dispatch pattern
- [ ] Validation plan checked — confirm entropy wave + isentropic vortex are sufficient
- [ ] Epsilon guard strategy confirmed — is 1e-14 appropriate, or should fallback be Rusanov instead of simple average?
- [ ] Wave speed estimate confirmed — Roe averages vs. simpler Davis estimate (S_L = min(uL-cL, uR-cR), S_R = max(uL+cL, uR+cR))?
- [ ] Default `flux_type` remains "rusanov" for backward compatibility — confirmed?
- [ ] Approved for implementation changed to yes
