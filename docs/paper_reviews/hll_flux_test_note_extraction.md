# Paper Extraction Report

## Paper metadata
- title: HLL Approximate Riemann Solver for Compressible Euler Equations (workflow test document)
- authors: Harten, A., Lax, P.D., van Leer, B. (original method); test note by project
- year: 1983 (original); 2026 (test note)
- source: SIAM Review, 25(1), 35-61 (original reference)
- local file: docs/papers/hll_flux_test_note.md

## Target problem
- governing equations: 2D compressible Euler equations, dU/dt + dF/dx + dG/dy = 0, ideal gas gamma=1.4
- dimension: 2D
- grid type: structured Cartesian (compatible with current solver)
- variable form: conservative variables U = [rho, rho*u, rho*v, E]
- assumptions: ideal gas, no source terms, existing reconstruction pipeline provides left/right states

## Numerical method summary
- method name: HLL (Harten-Lax-van Leer) approximate Riemann solver
- spatial discretization: finite volume with interface flux
- reconstruction: any (piecewise constant or MUSCL — inherited from existing pipeline)
- limiter: any (inherited from existing pipeline)
- Riemann solver / flux: HLL two-wave approximate solver
- time integration: any (inherited from existing pipeline)
- source terms: none
- boundary conditions: any (inherited from existing pipeline)
- stability / CFL condition: same as Rusanov (CFL <= 0.5 for euler, <= 0.5 for SSP RK2)

## Formula map
| Equation / formula | Meaning | Variables | Location in paper | Confidence |
|---|---|---|---|---|
| rho_hat = sqrt(rhoL * rhoR) | Roe-averaged density | rhoL, rhoR: left/right densities | Section 5 | high |
| u_hat = (sqrt(rhoL)*uL + sqrt(rhoR)*uR) / (sqrt(rhoL) + sqrt(rhoR)) | Roe-averaged velocity (x) | uL, uR: left/right x-velocities | Section 5 | high |
| H_hat = (sqrt(rhoL)*HL + sqrt(rhoR)*HR) / (sqrt(rhoL) + sqrt(rhoR)) | Roe-averaged total enthalpy | HL, HR: (E+p)/rho | Section 5 | high |
| c_hat = sqrt((gamma-1) * (H_hat - 0.5 * u_hat^2)) | Roe-averaged sound speed | gamma, H_hat, u_hat | Section 5 | high |
| S_L = min(uL - cL, u_hat - c_hat) | Left wave speed estimate | uL, cL, u_hat, c_hat | Section 5 | high |
| S_R = max(uR + cR, u_hat + c_hat) | Right wave speed estimate | uR, cR, u_hat, c_hat | Section 5 | high |
| F_HLL = (S_R*F(UL) - S_L*F(UR) + S_L*S_R*(UR - UL)) / (S_R - S_L) | HLL flux (x, star region) | UL, UR, FL, FR, S_L, S_R | Section 6 | high |
| if S_L >= 0: F_HLL = F(UL) | HLL flux (all waves right-going) | S_L, FL | Section 6 | high |
| if S_R <= 0: F_HLL = F(UR) | HLL flux (all waves left-going) | S_R, FR | Section 6 | high |
| S_B = min(vB - cB, v_hat - c_hat) | Bottom wave speed (y) | vB, cB, v_hat, c_hat | Section 5 | high |
| S_T = max(vT + cT, v_hat + c_hat) | Top wave speed (y) | vT, cT, v_hat, c_hat | Section 5 | high |
| G_HLL = (S_T*G(UB) - S_B*G(UT) + S_B*S_T*(UT - UB)) / (S_T - S_B) | HLL flux (y, star region) | UB, UT, GB, GT, S_B, S_T | Section 6 | high |

## Notation table
| Symbol | Meaning | Current solver equivalent | Notes |
|---|---|---|---|
| UL, UR | Left/right conservative states at x-interface | `UL`, `UR` output of `reconstruct()` shape (4, nyt, nxt-1) | Direct match |
| UB, UT | Bottom/top conservative states at y-interface | `UL`, `UR` output of `reconstruct_y()` shape (4, nyt-1, nxt) | Direct match |
| F(UL) | Physical x-flux of left state | `euler_flux_x(UL, gamma)` | Direct match |
| G(UB) | Physical y-flux of bottom state | `euler_flux_y(UL, gamma)` | Direct match |
| S_L, S_R | Wave speed bounds (x) | New computation needed | Not in current solver |
| S_B, S_T | Wave speed bounds (y) | New computation needed | Not in current solver |
| rho_hat | Roe-averaged density | New computation | sqrt(rhoL * rhoR) |
| u_hat | Roe-averaged velocity | New computation | Roe average formula |
| H | Specific total enthalpy | New computation | H = (E + p) / rho |
| c_hat | Roe-averaged sound speed | New computation | From H_hat and u_hat |
| gamma | Ratio of specific heats | `gamma` parameter (default 1.4) | Direct match |
| F_HLL | HLL numerical flux (x) | New function `hll_flux_x()` | Replaces `rusanov_flux_x()` |
| G_HLL | HLL numerical flux (y) | New function `hll_flux_y()` | Replaces `rusanov_flux_y()` |

## Implementation compatibility
- compatible with current solver: yes (fully compatible)
- required modules:
  - `cfd/numerics/riemann.py` — add `hll_flux_x()` and `hll_flux_y()`
  - `cfd/numerics/update.py` — add dispatch branch for `flux_type == "hll"`
  - `cfd/numerics/__init__.py` — export new functions
  - `cfd/config.py` — update `flux_type` docstring to list "hll"
- missing infrastructure: none — all prerequisites exist (reconstruction, fluxes, wave speeds)
- simplifications needed: none
- risks:
  - Division by (S_R - S_L) when both wave speeds are equal (requires epsilon guard)
  - Roe-averaged quantities need careful handling when rhoL or rhoR approaches zero
  - HLL is still two-wave; contact/shear smearing remains (known limitation, not a risk)

## Validation plan
- analytic case 1: entropy wave (`run_cfd_entropy_wave.py`) — expect lower L2 than Rusanov, ~1st order
- analytic case 2: isentropic vortex (`run_cfd_isentropic_vortex.py`) — expect lower L2 than Rusanov, ~2nd order with MUSCL+SSP_RK2
- convergence study: entropy wave + isentropic vortex convergence at 32/64/128 grids
- invariants: mass conservation (same as Rusanov), no negative density/pressure
- plots: error fields, centerline comparisons, convergence plots

## Questions for human confirmation
1. Should the wave speed estimate use Roe averages as described, or the simpler Davis estimate (S_L = min(uL-cL, uR-cR), S_R = max(uL+cL, uR+cR))? The test note specifies Roe averages.
2. Should the implementation handle the degenerate case S_R == S_L with an epsilon guard (e.g., fallback to Rusanov), or use a tolerance check?
3. Should `flux_type` default remain "rusanov" for backward compatibility, or change to "hll" after implementation?

## Decision
- ready for scheme spec: yes
