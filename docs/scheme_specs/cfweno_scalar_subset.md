# Scheme Specification: CFWENO Scalar 1D Subset

## Status
Approved for implementation: no

## Phase 1 Target: Linear Advection CFWENO3 Prototype
This spec's Phase 1 target is a **1D scalar linear advection CFWENO3 prototype** — the simplest non-trivial implementation with **ZERO external blockers**. All required formulas (Eq. 27-30) are self-contained in the paper.

Phase 2 target extends to nonlinear scalar (Burgers) with WENO weighting (Eq. 17, Tables I-II, Eq. 19) — also **ZERO external blockers**.

(Parent spec: `docs/scheme_specs/cfweno_pof_2025.md` — also set to `no`)

## Source
- paper: .local/papers/cfweno_pof_2025.pdf (NOT in git)
- paper reference: docs/papers/cfweno_pof_2025_reference.md
- extraction report: docs/paper_reviews/cfweno_pof_2025/extraction_report.md
- parent spec: docs/scheme_specs/cfweno_pof_2025.md
- dependency register: docs/papers/cfweno_dependency_register.md

## Subset definition

This spec covers **only** the scalar 1D subset of CFWENO:
- Linear advection: u_t + a*u_x = 0 (constant speed)
- Burgers equation: u_t + u*u_x = 0 (nonlinear)
- CFWENO3 order only (3rd order)

It does NOT include Euler equations, characteristic decomposition, Algorithm 1, p_m prediction, or multi-dimensional extension. Those belong to the Euler and 2D subsets.

## Scope
- target equation: 1D scalar conservation law u_t + f(u)_x = 0
- dimension: 1D only
- variable form: scalar u (no vector of conservative variables)
- supported mesh: structured Cartesian (existing solver mesh)
- supported boundary: periodic
- orderings: CFWENO3 (3rd order) only

## Blocking dependencies

| Dependency | Subset affected | Status | Resolution plan |
|-----------|----------------|--------|-----------------|
| WENO nonlinear weight formulas [6,7] | ~~scalar_linear~~ | NOT needed — Eq. 17, Tables I-II, Eq. 19 are self-contained | References [6,7] provide FWENO context only |
| CFL stability limit | All scalar | Stated as <= 1, not proven | Empirically verify during testing (non-blocking) |

**Phase 2.5 correction**: References [6,7] were previously classified as CRITICAL blockers for ALL subsets. Phase 2.5 audit confirms the paper self-contains all needed formulas. Scalar linear and scalar nonlinear CFWENO3 have ZERO external blockers.

## Mathematical definition

### Scalar 1D Foundation

**Eq. (27)** — HJ equation connection:
```
Phi_t + f(Phi_x)_x = 0,  Phi(x,0) = Phi_0(x)
u = Phi_x
```

**Eq. (28-29)** — Third-order stencil Hermite interpolation:
```
Phi(x) = cubic Hermite interpolation using {Phi_i, u_i, Phi_{i+/-1/2}}
u(x) = dPhi/dx
```
Input: cell-center values Phi_i, u_i = (Phi_x)_i, interface values Phi_{i+/-1/2}
Output: reconstructed Phi(x) and u(x) within each cell

**Eq. (30)** — CFWENO stencil (cell-average at interface from interface values):
```
u_bar_{i+1/2} = u_{i+1/2} - nu*(u_{i+1/2} - u_i) - nu*(1-nu)*(u_{i-1/2} - 2*u_i + u_{i+1/2})
```
where `nu = tau*a/h`, `a` = characteristic speed (= f'(u) for scalar).

**Eq. (32)** — Numerical flux from HJ integral:
```
f_hat_{i+1/2} = [computed from HJ integral]
```
Derived from integrating f(Phi_x) along the characteristic.

### Update formula

**Eq. (25)** — Conservative update:
```
u_i^{n+1} = u_i^n - (tau/h)*(f_hat_{i+1/2} - f_hat_{i-1/2})
```

### Truncation error
- Initial value reconstruction: O(Dx^2)
- Flux reconstruction: O(tau)*O(h)^2 ~ O(Dx^(2+1)) = 3rd order
- Single-stage: no Runge-Kutta needed

## Variable mapping (scalar subset only)

| Paper symbol | Meaning | Code variable / module |
|---|---|---|
| Phi | HJ potential (u = Phi_x) | New local variable |
| u | Scalar solution | Existing `cfd/variables/` (adapted for scalar) |
| u_{i+1/2} | Cell-interface value | New — from Hermite interpolation |
| u_bar_{i+1/2} | Cell-average at interface | New — Eq. (30) |
| nu | tau*a/h (normalized wave speed) | New local variable |
| a | Characteristic speed = f'(u) | New — f'(u) for scalar |
| f_hat_{i+1/2} | Numerical flux at interface | New — replaces `rusanov_flux_x` etc. |
| tau | Time step | Existing `cfd/numerics/dt.py` |
| h | Grid spacing | Existing `cfd/mesh/` |

## Algorithm steps (scalar 1D)

1. Given: cell-center values u_i^n, grid spacing h, time step tau
2. Compute characteristic speed a_i = f'(u_i) at each cell center
3. Compute interface values u_{i+1/2} from cell-center values via Hermite interpolation (Eq. 28-29)
4. Compute cell-averages at interfaces u_bar_{i+1/2} via CFWENO stencil (Eq. 30)
5. Compute numerical flux f_hat_{i+1/2} from HJ integral (Eq. 32)
6. Update: u_i^{n+1} = u_i^n - (tau/h)*(f_hat_{i+1/2} - f_hat_{i-1/2})

**Note**: Steps 3-5 are fully self-contained in the paper for the linear case. For nonlinear (Burgers), WENO weights come from Eq. (17), Tables I-II, and Eq. (19) — also self-contained. References [6,7] provide FWENO derivation context but are NOT required for implementation.

## Required code changes

| Module | Required change |
|---|---|
| `cfd/numerics/` (new module) | Hermite interpolation for Phi and u at interfaces |
| `cfd/numerics/` (new module) | WENO reconstruction (3rd order weight computation) — self-contained via Eq. 17, Tables I-II, Eq. 19 |
| `cfd/numerics/` (new module) | CFWENO stencil formula (Eq. 30) |
| `cfd/numerics/riemann.py` | Add `cfweno_scalar_flux()` |
| `cfd/numerics/update.py` | Add dispatch for scalar CFWENO |
| `cfd/cases/` | New scalar test cases (linear advection, Burgers) |
| `tests/test_cfd_cfweno.py` | New test module |

## Public API changes

- New functions:
  - `cfd.numerics.riemann.cfweno_scalar_flux(u, a, tau, h) -> Fnum`
  - `cfd.numerics.hermite.hermite_interp_1d(phi, u, h) -> phi_half, u_half`
  - `cfd.numerics.weno.weno3_weights(u, ...) -> w` — self-contained via Eq. 17, Tables I-II, Eq. 19
- No breaking changes; fully backward-compatible.

## Tests required

1. **Hermite interpolation**: Verify Phi(x) matches cubic Hermite for known data
2. **CFWENO stencil**: Eq. 30 produces correct u_bar for manufactured u_{i+/-1/2}
3. **Flux shape test**: `cfweno_scalar_flux` returns shape `(nxt-1,)` or `(nxt,)`
4. **Uniform state**: u = const -> exact flux (zero residual)
5. **Linear advection convergence**: Verify 3rd-order convergence on u_t + u_x = 0
6. **Burgers shock**: Non-oscillatory shock capturing
7. **Comparison**: Compare with existing upwind/LW/Rusanov schemes

## Validation required

1. Linear advection u_0 = sin(pi*x): L2 error at different resolutions
2. Linear advection convergence: verify order ~ 3 for CFWENO3
3. Burgers equation: shock formation without oscillations
4. Uniform flow: preserved to machine precision

## Expected behavior

- Single-stage scheme — no Runge-Kutta stages
- Compact stencil — fewer cells than non-compact WENO
- 3rd-order accuracy on smooth flows
- Non-oscillatory near discontinuities (depends on WENO weights from [6,7])
- CFL <= 1 for stability

## Known limitations

1. **WENO weights** — Previously classified as unresolved; Phase 2.5 audit confirmed paper self-contains Eq. (17), Tables I-II, Eq. (19)
2. **CFL limit unproven** — Stated as CFL <= 1 sufficient but not rigorously proven; will verify empirically
3. **Scalar only** — This subset does not cover Euler equations or multi-dimensional problems
4. **No characteristic decomposition** — Not needed for scalar equations
5. **No Algorithm 1** — The pressure-based wave selection is Euler-specific

## Human confirmation checklist
- [ ] Hermite interpolation (Eq. 28-29) verified against paper Sec. II.A
- [ ] CFWENO stencil (Eq. 30) verified against paper Sec. II.B
- [ ] Numerical flux (Eq. 32) formula fully transcribed
- [ ] WENO weight source references [6,7] identified and accessible (context only, not blocking)
- [ ] CFL <= 1 stability claim verified for linear advection and Burgers
- [ ] 3rd-order convergence target accepted
- [ ] Approved for implementation changed to yes
