# Scheme Specification: CFWENO3 Scalar Nonlinear Burgers Subset from Zhou-Dong-Pan 2025

## Status
Approved for implementation: no

## Scope

This spec targets a **1D scalar nonlinear Burgers equation CFWENO3 prototype**:

```
u_t + (u^2 / 2)_x = 0
```

This is the natural next step after the v1.1 scalar linear advection CFWENO3 prototype.
Only CFWENO3 (3rd-order) is in scope. This is a **scalar nonlinear** prototype, not the
full CFWENO scheme.

(Parent spec: `docs/scheme_specs/cfweno_scalar_subset.md` — approved: yes for linear only)

## Source

- paper: .local/papers/cfweno_pof_2025.pdf (NOT in git)
- paper reference: docs/papers/cfweno_pof_2025_reference.md
- extraction report: docs/paper_reviews/cfweno_pof_2025/extraction_report.md
- parent scalar spec: docs/scheme_specs/cfweno_scalar_subset.md
- dependency register: docs/papers/cfweno_dependency_register.md
- readiness review: docs/feasibility/cfweno_scalar_burgers_readiness.md

## Relation to v1.1

### What v1.1 already provides (linear advection CFWENO3)

- CFWENO3 compact stencil implementation (Eq. 30) in `solver/schemes.py`
- 4th-order centred interface reconstruction
- Periodic boundary handling via `np.roll`
- Conservative update Eq. (25)
- Constant wave speed `a = 1.0`, so `nu = cfl`
- Numerical flux `f_hat = a * ubar` (a factors cancel)
- Upwind / Lax-Wendroff / CFWENO3 baseline comparison
- 3rd-order convergence verified (3.04 -> 3.01 -> 3.00)
- CFL sweep (0.1, 0.5, 0.9) — empirically stable
- 19 CFWENO-specific tests + comprehensive traceability

### What v1.2 will add (Burgers nonlinear CFWENO3)

- Nonlinear flux `f(u) = u^2 / 2` instead of `f(u) = a * u`
- Local wave speed `a_i = f'(u_i) = u_i` (variable, not constant)
- Flux linearization (SFM decomposition): `f(u) = a * u - f*`
- Numerical flux becomes `f_hat = a * ubar_{i+1/2} - f*` (a no longer cancels)
- Optional nonlinear WENO weights (Eq. 17, Tables I-II, Eq. 19) if linear weights insufficient near shocks
- Burgers smooth pre-shock validation against known implicit analytic solution
- Optional post-shock qualitative comparison against high-resolution reference
- No claim of rigorous shock-capturing

## Required Formula Review

The following formulas must be confirmed and understood before implementation:

### 1. SFM flux linearization

The paper's SFM (Solution Formula Method) approach linearizes the flux around a local
characteristic speed:

```
f(u) = a * u - f*
```

where `a` is the local characteristic speed and `f*` is the residual flux.

### 2. Local wave speed

```
a = f'(u) = u        for Burgers: f(u) = u^2/2
```

Unlike v1.1 where `a = const = 1.0`, the wave speed now varies spatially.

### 3. Residual flux (flux correction)

```
f* = a * u^{n+1}_{i+1/2} - f(u^{n+1}_{i+1/2})
```

This is the difference between the linearized flux and the true nonlinear flux at
the predicted interface state.

### 4. Numerical flux with correction

```
f_hat_{i+1/2} = a * ubar_{i+1/2} - f*
```

The update becomes:
```
u_i^{n+1} = u_i - (tau/h) * (f_hat_{i+1/2} - f_hat_{i-1/2})
```

Note: `a` and `f*` are interface-specific, so the simple `cfl * (ubar_right - ubar_left)`
from v1.1 no longer applies directly.

### 5. CFWENO3 initial value reconstruction (inherited from v1.1)

The 4th-order centred interface reconstruction:
```
u_{i+1/2} = (-u_{i-1} + 7u_i + 7u_{i+1} - u_{i+2}) / 12
```

This remains unchanged from v1.1.

### 6. Interface state u^{n+1}_{i+1/2} (inherited from Eq. 30)

The CFWENO3 stencil:
```
ubar_{i+1/2} = u_{i+1/2} - nu*(u_{i+1/2} - u_i) - nu*(1-nu)*(u_{i-1/2} - 2u_i + u_{i+1/2})
```

where now `nu = tau * a / h` and `a = u_i` (local, not constant). This is a key
generalization from v1.1.

### 7. Predictor iteration for a

**Open question**: Whether one predictor iteration is needed for `a`. Options:
- **Zero iterations (frozen)**: Use `a = u_i^n` directly. Simplest; accuracy depends on
  whether the CFWENO3 stencil already provides sufficient implicit time accuracy.
- **One iteration**: Compute a first estimate `u^{(1)}_{i+1/2}` using `a = u_i^n`, then
  recompute with `a = u^{(1)}_{i+1/2}`. The paper mentions iterative improvement of `a`
  increases accuracy by one order per iteration (Sec. II.C truncation analysis).
- **Recommendation**: Start with zero iterations for the smooth pre-shock case; add one
  iteration if convergence order is below 3.

### 8. Entropy / shock treatment for post-shock cases

**Not in Phase 1 scope**. For post-shock Burgers:
- The paper's entropy condition (Algorithm 1, Eq. 23) is Euler-specific and NOT applicable
- For scalar Burgers, simple entropy fixes or WENO nonlinear weights may suffice
- Phase 2 (optional post-shock validation) will address this experimentally
- No claim of rigorous shock-capturing until verified

## Intended Phase 1 Implementation

Phase 1 is restricted to **smooth pre-shock Burgers** only:

- **Equation**: u_t + (u^2/2)_x = 0
- **Domain**: x in [0, 1), periodic boundary conditions
- **Initial condition**: smooth, e.g., u(x,0) = 1 + 0.5*sin(2*pi*x) (positive everywhere)
- **Final time**: before shock formation (shock time = 1 / (pi * max|u_0'|) for Burgers)
- **Comparison**: against high-resolution reference solution or known analytic implicit solution
- **No shock-capturing claim**

### Why pre-shock only?

The Burgers equation with smooth IC develops a shock at finite time. Before shock
formation, the solution is smooth and a convergence study is meaningful. After shock
formation, entropy-satisfying treatment is needed and convergence rates degrade. Restricting
to pre-shock allows clean validation of the nonlinear CFWENO3 stencil.

### Expected convergence order

If the flux linearization is handled correctly, CFWENO3 should maintain approximately
3rd-order convergence on smooth pre-shock Burgers, consistent with the paper's theoretical
predictions and the v1.1 linear results.

## Intended Phase 2 Optional Validation

Post-shock qualitative test (optional, not required for spec approval):

- Run past the shock formation time
- Compare against high-resolution reference (fine-grid upwind or exact Riemann solver)
- Observe whether CFWENO3 produces oscillations near the shock
- If oscillations appear, consider adding WENO nonlinear weights (Eq. 17)
- **Do not** claim rigorous shock-capturing unless verified
- **Do not** use Euler Eq. (23) — it is not applicable to scalar Burgers
- Document any oscillations or non-physical behaviour honestly

## Non-goals

- **No Euler equations** — scalar Burgers only
- **No Eq. (23)** — p_m prediction is Euler-specific
- **No characteristic decomposition** — not needed for scalar
- **No 2D** — 1D only
- **No CFWENO5/7** — 3rd-order only
- **No full paper reproduction** — Burgers subset prototype only
- **No production shock-capturing claim** — empirical observation only
- **No WENO5/RK3 baseline** — unless separately approved
- **No cfd/ modifications** — Burgers stays in solver/ tier

## Required Modules if Later Approved

These are suggested module locations but are **NOT to be implemented** until the spec is
approved:

| Module | Purpose |
|--------|---------|
| `solver/schemes.py` (extend or refactor) | Add Burgers CFWENO3 function; may need helper for nonlinear flux |
| `examples/run_cfweno_burgers_demo.py` | Burgers smooth pre-shock demo with baseline comparison |
| `examples/run_cfweno_burgers_convergence.py` | Grid convergence study for smooth Burgers |
| `tests/test_cfweno_burgers.py` | Burgers-specific tests |
| `results/cfweno_burgers_demo/` | Demo output directory |
| `results/cfweno_burgers_convergence/` | Convergence output directory |
| `docs/tasks/cfweno_burgers_prototype/traceability.md` | Traceability manifest |

## Variable Mapping (Burgers Extension)

| Paper symbol | Meaning | v1.1 (linear) | v1.2 (Burgers) |
|---|---|---|---|
| `f(u)` | Physical flux | `a * u` (linear) | `u^2 / 2` (nonlinear) |
| `a` | Characteristic speed | `1.0` (constant) | `u_i` (local, variable) |
| `nu` | `tau * a / h` | `cfl` (constant) | `tau * u_i / h` (local) |
| `f*` | Residual flux | `0` (linear case) | `a * u - u^2/2` (nonzero) |
| `f_hat` | Numerical flux | `a * ubar` | `a * ubar - f*` |
| `ubar_{i+1/2}` | Eq. (30) stencil | Same formula, constant nu | Same formula, local nu |
| Update | Eq. (25) | `cfl * (ubar_R - ubar_L)` | `(tau/h) * (f_hat_R - f_hat_L)` |

## Validation Plan

### Required (Phase 1 — smooth pre-shock)

1. **Smooth Burgers pre-shock case**:
   - IC: u(x,0) = 1 + 0.5*sin(2*pi*x), domain [0,1), periodic
   - Final time: T < T_shock (e.g., T = 0.1 or 0.2)
   - Reference: high-resolution fine-grid solution (e.g., nx=2560 upwind) or implicit analytic
   - Compare L1, L2, Linf errors at multiple resolutions

2. **Mass conservation**: Sum(u) conserved to machine precision at each step

3. **Finite values**: No NaN or Inf over the entire run

4. **Convergence trend**: If feasible, measure convergence order on smooth pre-shock data

5. **Result CSV**: `error_summary.csv` with method, nx, errors, steps

6. **Line plot**: Numerical vs reference solution overlay

7. **analysis.md**: Include all results, limitations, and caveats

### Optional (Phase 2 — post-shock qualitative)

8. **Post-shock comparison**: Run past T_shock, compare vs high-resolution reference
9. **Oscillation assessment**: Document any Gibbs-like oscillations near shock
10. **WENO weight impact**: If Phase 2 is attempted with Eq. 17 weights, compare linear vs nonlinear weights

## Approval Checklist

- [ ] Formula review completed — SFM flux linearization confirmed
- [ ] Smooth Burgers validation case selected — IC and final_time specified
- [ ] Predictor strategy selected — zero-iteration or one-iteration for `a`
- [ ] Reference solution strategy selected — fine-grid baseline or analytic implicit
- [ ] Risks accepted — nonlinear extension may not achieve exactly 3rd order
- [ ] Approved for implementation changed to yes

## Known Limitations

1. **Variable wave speed**: Unlike v1.1 where `a = 1.0` globally, Burgers has `a = u_i`
   which varies in space and time. The CFWENO3 stencil uses `nu = tau * a / h` at each
   interface, requiring per-cell or per-interface CFL computation.

2. **Flux linearization accuracy**: The SFM decomposition `f(u) = a*u - f*` is exact for
   any `a`, but the choice of `a` affects the accuracy of the CFWENO3 stencil. Using
   `a = u_i` (cell-center) vs `a = u_{i+1/2}` (interface) may affect results.

3. **No rigorous shock-capturing**: CFWENO3 with linear weights (no WENO nonlinear weights)
   will produce oscillations near discontinuities. This is expected and documented.

4. **Pre-shock restriction**: Phase 1 validation only covers smooth solutions before shock
   formation. Convergence after shock formation is not claimed.

5. **Single-stage**: No Runge-Kutta. The CFWENO update is applied once per time step,
   same as v1.1.

## Human Confirmation Required

Before approval, the following must be verified by a human:

1. The SFM flux linearization `f(u) = a*u - f*` is correctly applied for Burgers
2. The choice of `a = u_i` (cell-center) vs `a = u_{i+1/2}` (interface) is appropriate
3. Whether the 4th-order centred interface reconstruction is sufficient for nonlinear Burgers
4. The smooth Burgers test case IC and final_time are appropriate
5. The reference solution strategy is acceptable
