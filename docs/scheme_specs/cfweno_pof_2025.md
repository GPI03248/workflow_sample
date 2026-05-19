# Scheme Specification

## Status
Approved for implementation: no

## Source
- paper: .local/papers/cfweno_pof_2025.pdf (NOT in git)
- paper reference: docs/papers/cfweno_pof_2025_reference.md
- extraction report: docs/paper_reviews/cfweno_pof_2025/extraction_report.md

## Scheme name
CFWENO (Compact Fully-discrete WENO) — single-stage fully-discrete scheme using Hamilton-Jacobi quasi-exact solutions

## Scope
- target equation: 2D compressible Euler equations, dU/dt + dF/dx + dG/dy = 0
- dimension: 1D (primary), 2D (extension via consistent cell-interface distribution)
- variable form: primitive (rho, u, v, p) for reconstruction; conservative for update
- supported mesh: structured Cartesian (existing solver mesh)
- supported boundary: all existing BCs (periodic, transmissive, reflective)
- orderings: CFWENO3 (3rd), CFWENO5 (5th), CFWENO7 (7th)

### Implementation Subsets

This scheme decomposes into three progressively larger subsets with independent blockers:

| Subset | Scope | Required equations | Blocking dependencies | Estimated LOC |
|--------|-------|-------------------|----------------------|---------------|
| **Scalar 1D** | Linear advection + Burgers | Eq. 27-30, 32, 25 | WENO weights [6,7] only | ~150-250 |
| **Euler 1D** | 1D compressible Euler with characteristic decomposition | + Eq. 21-24, Algorithm 1 | + Eigenvalue iteration, p_m verification | ~350-550 |
| **2D Euler** | Full 2D Euler with dimensional composition | + Eq. 33 | None additional | ~450-700 |

See also: `docs/scheme_specs/cfweno_scalar_subset.md` for the implementation-ready scalar subset spec.

## Mathematical definition

### Core concept (SFM — Solution Formula Method)

1. Write the conservation law as a Hamilton-Jacobi (HJ) equation:
   ```
   Phi_t + f(Phi_x)_x = 0,  Phi(x,0) = Phi_0(x)
   u = Phi_x
   ```
2. The HJ equation admits a quasi-exact integral solution over [t_n, t_n + tau]
3. Evaluate the integral numerically -> yields cell-center values AND cell-interface fluxes simultaneously
4. No multi-stage Runge-Kutta or Lax-Wendroff derivative expansion needed

### Scalar 1D Foundation

**Eq. (28-29)** — Third-order stencil Hermite interpolation:
```
Phi(x) = cubic Hermite interpolation using {Phi_i, u_i, Phi_{i+-1/2}}
u(x) = dPhi/dx
```

**Eq. (30)** — CFWENO stencil formula (cell-average from interface values):
```
u_bar_{i+1/2} = u_{i+1/2} - nu*(u_{i+1/2} - u_i)
                - nu*(1-nu)*(u_{i-1/2} - 2*u_i + u_{i+1/2})
```
where `nu = tau*a/h`, `a` = characteristic speed.

### Numerical Flux (Eq. 32)

```
f_hat_{i+1/2} = [computed from HJ integral]
```
Derived from integrating `f(Phi_x)` along the characteristic.

### Euler Equations Extension

#### Characteristic Decomposition (Eq. 21)

```
L * u_t + (A * L * u - L * f*) = 0
L * v_t + A * L * v_x - L * f* = 0
```

#### Roe-averaged quantities (Eq. 22)

```
u_bar = (sqrt(rho_L)*u_L + sqrt(rho_R)*u_R) / (sqrt(rho_L) + sqrt(rho_R))
        when u_L > u_R
u_bar = (u_L + u_R) / 2
        when u_L <= u_R
```
Similar for Roe-averaged enthalpy H_bar.

#### Characteristic variables

```
phi^k = lambda^k * L^k * u* - L^k * f*
c = sqrt((gamma-1)(H - 0.5*u^2))
Lambda = {lambda^k} = Lambda(u, c),  L = {L^k} = L(u, c)
```

### Flux Reconstruction Strategy (Algorithm 1)

**Parameters**: s1 = 2, s2 = 1.05

**Step 1** — Shock detection:
```
if max(|p_L|, |p_R|) >= s1*min(|p_L|, |p_R|) OR p_L*p_R <= 0:
    -> all waves use baseline (entropy condition) reconstruction
else:
    -> compute predicted middle pressure p_m (Eq. 23)
```

**Step 2** — Smooth flow check:
```
if max(|p_L|, |p_R|) < s2*min(|p_L|, |p_R|):   [s2=1.05]
    -> all waves use high-order flux: phi^k = L^k*(lambda^k*(u*)*u* - f(u*))
```

**Step 3** — Intermediate case (pressure-based wave selection):
```
if p_L < p_m  AND p_m > p_R:    all waves baseline (left shock)
elif p_L >= p_m AND p_m <= p_R:   all waves high-order (rarefaction)
elif p_L < p_m AND p_m <= p_R:   wave1 baseline, waves 2-3 high-order (left rarefaction)
elif p_L >= p_m AND p_m > p_R:   waves 1-2 high-order, wave3 baseline (right shock)
```

### Compact Flux (Eq. 24)

```
f_hat_{i+1/2} = L^{-1} * (A * L * u_{i+1/2} - 0.5 * L * f*)
```

### Update Formula (Eq. 25)

```
u_i^{n+1} = u_i^n - (tau/h)*(f_hat_{i+1/2} - f_hat_{i-1/2})
```

### Multi-Dimensional Extension (Eq. 33)

```
u^{n+1} = T_{x,z} o T_{x,y} u^n
```
Uses consistent cell-interface distribution per coordinate direction. NOT dimensional splitting — maintains formal order of accuracy because interface values are shared between directional updates.

### Stability condition

CFL <= 1 stated as sufficient. Exact stability limit not rigorously proven in paper.

### Truncation error

- Initial value reconstruction: O(Dx^2)
- Flux reconstruction: O(tau)*O(h)^2 ~ O(Dx^(2+1)) = 3rd order
- Each eigenvalue iteration `a` improves accuracy by one order for `u`, two orders for flux

## Variable mapping
| Paper symbol | Meaning | Code variable / module |
|---|---|---|
| Phi | HJ potential (u = Phi_x) | New — not in existing code |
| u | Conservative/primitive state | Existing `cfd/variables/` |
| u_{i+1/2} | Cell-interface value | New — from Hermite interpolation |
| u_bar_{i+1/2} | Cell-average at interface | New — Eq. (30) |
| nu | tau*a/h (normalized wave speed) | New local variable |
| a | Characteristic speed | New — from eigenvalue iteration |
| f_hat_{i+1/2} | Numerical flux at interface | New — replaces `rusanov_flux_x` etc. |
| L, L^k | Left eigenvector matrices | New — characteristic decomposition |
| Lambda, lambda^k | Eigenvalues | New — characteristic decomposition |
| phi^k | Characteristic flux variable | New |
| p_m | Predicted middle pressure | New — Eq. (23) |
| s1, s2 | Shock/smooth thresholds | Constants: s1=2, s2=1.05 |
| tau | Time step | Existing `cfd/numerics/dt.py` |
| h | Grid spacing | Existing `cfd/mesh/` |

## Algorithm steps

### CFWENO scalar step (1D)

1. Compute interface values u_{i+1/2} from cell-center values via Hermite interpolation (Eq. 28-29)
2. Compute cell-averages at interfaces via CFWENO stencil (Eq. 30)
3. Compute numerical flux f_hat_{i+1/2} from HJ integral (Eq. 32)
4. Update: u_i^{n+1} = u_i^n - (tau/h)*(f_hat_{i+1/2} - f_hat_{i-1/2})

### CFWENO Euler step (1D)

1. Compute Roe-averaged quantities (Eq. 22)
2. Compute eigenvector matrices L and eigenvalues Lambda
3. Transform to characteristic variables: phi^k = lambda^k * L^k * u* - L^k * f*
4. Apply Algorithm 1 flux reconstruction per wave:
   - Shock detection (s1 threshold)
   - Smooth flow check (s2 threshold)
   - Pressure-based wave selection (p_m comparison)
5. Compute compact flux: f_hat = L^{-1} * (A * L * u_{i+1/2} - 0.5 * L * f*) (Eq. 24)
6. Update conservative variables (Eq. 25)

### CFWENO 2D step

1. Apply 1D operator in x-direction: T_{x,y}
2. Apply 1D operator in z-direction: T_{x,z}
3. Compose: u^{n+1} = T_{x,z} o T_{x,y} u^n (Eq. 33)
4. Share interface values between directional updates (maintains order)

## Required code changes
| Module | Required change |
|---|---|
| `cfd/numerics/` (new module) | Characteristic decomposition: eigenvector matrices L, eigenvalues Lambda, Roe averages |
| `cfd/numerics/` (new module) | Hermite interpolation for Phi and u at interfaces |
| `cfd/numerics/` (new module) | WENO reconstruction (3rd/5th/7th order weight computation) |
| `cfd/numerics/` (new module) | CFWENO stencil formula (Eq. 30) |
| `cfd/numerics/riemann.py` | Add `cfweno_flux_x()`, `cfweno_flux_y()` with Algorithm 1 |
| `cfd/numerics/update.py` | Add dispatch for `flux_type == "cfweno"` |
| `cfd/numerics/time_integration.py` | Single-stage CFWENO update (no RK needed) |
| `cfd/config.py` | Add `flux_type="cfweno"`, `cfweno_order=3|5|7` |
| `cfd/cases/` | New test cases for CFWENO validation |
| `tests/test_cfd_cfweno.py` | New test module |

## Public API changes

- New functions:
  - `cfd.numerics.riemann.cfweno_flux_x(UL, UR, gamma, order=3) -> Fnum`
  - `cfd.numerics.riemann.cfweno_flux_y(UB, UT, gamma, order=3) -> Gnum`
  - `cfd.numerics.characteristic.roe_averages(U, gamma) -> (u_bar, H_bar, c_bar)`
  - `cfd.numerics.characteristic.eigenvectors(u, c) -> (L, Lambda)`
- `CFDConfig.flux_type` now accepts `"cfweno"`
- `CFDConfig` gains optional `cfweno_order` field (3, 5, or 7; default 3)
- No breaking changes; fully backward-compatible.

## Tests required

1. **Characteristic decomposition**: Roe averages match analytic values for known states
2. **Eigenvector matrices**: L * A = Lambda * L verified
3. **Flux shape test**: `cfweno_flux_x` returns shape `(4, nyt, nxt-1)`
4. **Flux shape test**: `cfweno_flux_y` returns shape `(4, nyt-1, nxt)`
5. **Consistency test**: Uniform flow -> exact flux (no spurious waves)
6. **Algorithm 1 branching**: All 4 branches tested with manufactured pressure states
7. **Smooth flow**: All waves use high-order when s2 threshold met
8. **Shock detection**: All waves use baseline when s1 threshold met
9. **Integration test**: Solver runs to completion with `flux_type="cfweno"` on small grid
10. **Analytic validation** (mandatory):
    - Entropy wave single run and convergence
    - Isentropic vortex single run and convergence
    - Comparison with existing Rusanov/HLL results

## Validation required

1. Entropy wave: L2 error vs. Rusanov and HLL at same resolution
2. Entropy wave convergence: verify expected order for CFWENO3/5/7
3. Isentropic vortex: L2 error comparison with Rusanov and HLL
4. Isentropic vortex convergence: verify order >= 2 for CFWENO3 with MUSCL
5. Uniform flow: preserved to machine precision (all CFWENO orders)
6. 1D Euler Shu-Osher: qualitative comparison with published results

## Expected behavior

- CFWENO is a single-stage scheme — no Runge-Kutta stages needed
- Compact stencil uses fewer cells than non-compact WENO
- Smallest error coefficients among CFWENO, FWENO, WENO-RK (Table IV)
- Per-step cost ~1.2-1.4x FWENO but total cost ~0.25x WENO-RK3 (single-stage)
- Algorithm 1 flux reconstruction adapts wave-by-wave based on local pressure

## Known limitations

1. **Unresolved: WENO weight formulas** — Paper references weights from earlier FWENO work; full weight computation details may require consulting references [6,7] in the paper
2. **Unresolved: Eigenvalue iteration** — Iterative improvement of characteristic speed `a`; exact iteration count and convergence criteria not fully specified in paper
3. **Unresolved: p_m formula (Eq. 23)** — Middle pressure prediction formula is complex; full transcription needs verification against paper
4. **Unresolved: CFL stability limit** — Stated as CFL <= 1 sufficient but not rigorously proven
5. **High complexity**: Requires characteristic decomposition, multi-branch flux reconstruction, Hermite interpolation, WENO weights — estimated ~500-800 lines of new code
6. **No contact/shear resolution**: Like HLL, the base scheme cannot resolve contact discontinuities without additional wave models
7. **Eigenvalue iteration convergence**: Not guaranteed for all flow regimes

## Human confirmation checklist
- [ ] Algorithm 1 branching logic verified against paper Sec. II.C
- [ ] Roe average formula (Eq. 22) verified — note the piecewise definition (u_L > u_R vs u_L <= u_R)
- [ ] Characteristic variable definition phi^k = lambda^k * L^k * u* - L^k * f* verified
- [ ] Compact flux formula (Eq. 24) verified — note the L^{-1} on the outside
- [ ] CFL <= 1 stability claim verified for the specific test cases
- [ ] WENO weight source references [6,7] identified and accessible
- [ ] p_m formula (Eq. 23) fully transcribed and verified
- [ ] Eigenvalue iteration convergence criteria determined
- [ ] s1=2, s2=1.05 thresholds appropriate for the intended test cases
- [ ] Multi-dimensional extension (Eq. 33) interface sharing strategy understood
- [ ] Complexity tier (High) and estimated LOC (500-800) accepted
- [ ] Approved for implementation changed to yes (after all items resolved)
