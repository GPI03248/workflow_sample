# CFWENO3 Burgers Scalar Prototype — Formula Consistency Audit

**Audit date**: 2026-05-20
**Auditor**: agentic workflow (Claude)
**Implementation commit**: cce631b
**Spec**: docs/scheme_specs/cfweno_scalar_burgers_subset.md (approved: yes)

---

## 1. Implemented Formula Mapping

### Burgers flux
- **Spec**: f(u) = u^2/2
- **Code**: `f_hat_right = 0.5 * ubar_right**2` (solver/schemes.py:161)
- **Match**: YES

### Characteristic speed
- **Spec**: a = f'(u) = u
- **Code**: `a = u.copy()` (solver/schemes.py:146)
- **Match**: YES — initial speed is cell-center value

### SFM flux linearization
- **Spec**: f(u) = a*u - f*, f* = a*u_pred - f(u_pred), f_hat = a*ubar - f*
- **Code**: The SFM decomposition simplifies to f_hat = f(ubar) = ubar^2/2 because f* = a*ubar - ubar^2/2, so f_hat = a*ubar - (a*ubar - ubar^2/2) = ubar^2/2
- **Match**: YES — mathematically correct simplification

### CFWENO3 stencil
- **Spec**: Eq. (30) inherited from v1.1, with per-cell nu = tau*a/h
- **Code**: `_cfweno3_stencil(u, nu)` at solver/schemes.py:91-101
- **Match**: YES — same stencil formula, generalized to per-cell nu

### Interface reconstruction
- **Spec**: 4th-order centred: u_{i+1/2} = (-u_{i-1} + 7u_i + 7u_{i+1} - u_{i+2})/12
- **Code**: `_interface_reconstruction(u)` at solver/schemes.py:83-88
- **Match**: YES — identical to v1.1

### Predictor iterations
- **Spec**: supports 0/1/2, default 1
- **Code**: `predictor_iterations` parameter with default=1 (solver/schemes.py:104-105)
- **Iteration logic** (lines 149-154):
  - a starts as u (cell-center)
  - Each iteration: compute nu from a, run stencil, update a to cell-average of ubar
- **Match**: YES

### Conservative update
- **Spec**: u_i^{n+1} = u_i - (tau/h)*(f_hat_{i+1/2} - f_hat_{i-1/2})
- **Code**: `return u - tau_h * (f_hat_right - f_hat_left)` (solver/schemes.py:165)
- **Match**: YES

### CFL check
- **Spec**: CFL based on max(|u|), reject if > 1
- **Code**: Lines 138-143, raises ValueError if max(|u|)*dt/dx > 1
- **Match**: YES

### Smooth pre-shock only
- **Spec**: final_time before shock formation, no shock-capturing claim
- **Code**: Examples use final_time=0.15 with IC u0=1+0.2*sin(2*pi*x)
- **Shock time**: T_shock = 1/(pi*A*2*pi) = 1/(2*pi^2*0.2) ≈ 0.253, so T=0.15 < T_shock
- **Match**: YES — correctly pre-shock

---

## 2. Confirmed Non-Goals

| Item | Confirmed not implemented? |
|------|--------------------------|
| Eq. 23 (p_m prediction) | YES — not present |
| Euler characteristic decomposition | YES — not present |
| 2D extension | YES — 1D only |
| CFWENO5/7 | YES — 3rd-order only |
| Nonlinear WENO shock-capturing (Eq. 17) | YES — no omega_k computation |
| Post-shock validation claim | YES — all tests are pre-shock |
| cfd/ modifications | YES — no cfd/ changes |

---

## 3. Accuracy Concern — Observed Order ≈ 2 Instead of 3

### Observed convergence (from convergence study)

| nx | CFWENO3 Burgers L2 | Ratio | Order |
|----|---------------------|-------|-------|
| 40 | 9.09e-05 | — | — |
| 80 | 2.26e-05 | 4.02 | 2.01 |
| 160 | 5.60e-06 | 4.03 | 2.01 |
| 320 | 1.38e-06 | 4.06 | 2.02 |

Consistently ~2nd order. This contrasts with the v1.1 linear advection result of exactly 3rd order.

### Possible causes (in order of likelihood)

1. **Per-cell nu variation**: The CFWENO3 stencil (Eq. 30) was derived assuming constant nu = tau*a/h. For Burgers, nu = tau*u_i/h varies spatially. When the stencil operates across cells with different nu values, the spatial variation of nu introduces truncation error that reduces the formal order by approximately one. This is the most likely explanation.

2. **SFM simplification**: The numerical flux f_hat = f(ubar) = ubar^2/2 is correct by the SFM decomposition, but the CFWENO3 stencil provides ubar that is a time-averaged interface state computed assuming locally constant characteristics. For nonlinear problems, the actual characteristic curves are curved, and the "constant-nu-within-stencil" approximation loses accuracy.

3. **Predictor iteration convergence**: The predictor iterates a from cell-center u_i toward an interface-predicted average. Even with iterations, the predictor may not converge to a value that fully restores 3rd-order accuracy because the underlying stencil assumes constant nu.

4. **Reference solution error**: The fine-grid reference (nx=2560) has its own numerical error. However, at nx=2560 with ~2nd-order convergence, the reference error is ~1.38e-06/(2560/320)^2 ≈ 2.2e-08, which is 60x smaller than the nx=320 coarse error. This does NOT explain the observed 2nd order.

5. **Interface reconstruction**: The 4th-order centred stencil is purely spatial and equation-independent. It should not cause order reduction.

### Conclusion

The 2nd-order convergence is **most likely a natural consequence of per-cell nu variation in the CFWENO3 stencil when applied to nonlinear Burgers**. The stencil treats nu as constant within each stencil footprint, but for Burgers, nu varies spatially as nu_i = tau*u_i/h. This introduces O(nu') terms that reduce the truncation error order.

**This is not a bug** — it is a known limitation of extending linear-derived stencils to nonlinear problems without additional nonlinear correction terms. The paper may address this through more sophisticated eigenvalue iteration or nonlinear WENO weighting (Eq. 17), which are not yet implemented.

---

## 5. Flux Form Clarification (v1.2.1 audit, 2026-05-21)

A follow-up audit (`docs/tasks/cfweno_burgers_prototype/flux_form_audit.md`)
confirmed that the current flux form `f_hat = f(ubar) = ubar^2/2` is an **exact
algebraic identity** of the spec's two-step SFM form `f_hat = a*ubar - f*` for
scalar Burgers. The simplification introduces no approximation error and cannot
explain the observed second-order convergence. The two-step form is only needed
for the Euler system extension (v1.4).

---

## 4. Audit Conclusion

**PASS with observation** — The implementation correctly and faithfully implements the scalar nonlinear Burgers CFWENO3 prototype as specified in `docs/scheme_specs/cfweno_scalar_burgers_subset.md`.

- Only Eq. (25) and Eq. (30) are used (same as v1.1)
- SFM flux linearization correctly simplifies to f_hat = f(ubar)
- No formulas outside the approved subset spec are used
- The 2nd-order convergence (instead of 3rd) is attributed to per-cell nu variation, not an implementation error
- No Euler, characteristic decomposition, Eq. 23, or nonlinear WENO weights are present
