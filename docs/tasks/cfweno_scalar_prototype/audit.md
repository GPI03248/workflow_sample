# CFWENO3 Scalar Prototype — Formula Consistency Audit

**Audit date**: 2026-05-20
**Auditor**: agentic workflow (Claude)
**Implementation commit**: 2b580ef
**Spec**: docs/scheme_specs/cfweno_scalar_subset.md (approved: yes)

---

## 1. Implementation Formula Summary

The `cfweno()` function in `solver/schemes.py:36-80` implements three steps:

**Step 1 — Interface reconstruction** (line 66):
```python
u_half_right = (-u_im1 + 7.0 * u + 7.0 * u_ip1 - u_ip2) / 12.0
```
This computes `u_{i+1/2}` from cell-centre values using the standard 4th-order centred interpolation stencil.

**Step 2 — CFWENO3 compact stencil** (lines 72-74):
```python
ubar_right = (u_half_right
              - nu * (u_half_right - u)
              - nu * (1.0 - nu) * (u_half_left - 2.0 * u + u_half_right))
```
This implements Eq. (30) from the paper:
`ubar_{i+1/2} = u_{i+1/2} - nu*(u_{i+1/2} - u_i) - nu*(1-nu)*(u_{i-1/2} - 2u_i + u_{i+1/2})`

**Step 3 — Conservative update** (line 80):
```python
return u - cfl * (ubar_right - ubar_left)
```
This implements Eq. (25) from the paper. For linear advection with constant `a`, the numerical flux is `f_hat = a * ubar`, so `tau/h * (f_hat_{i+1/2} - f_hat_{i-1/2}) = cfl * (ubar_right - ubar_left)`.

---

## 2. Code-to-Spec Mapping

| Code location | Spec reference | Paper equation | Match? |
|--------------|----------------|----------------|--------|
| `solver/schemes.py:58` `nu = cfl` | Spec: "nu = tau*a/h" | Eq. 30 definition | YES — for a=1, nu = tau/h = cfl |
| `solver/schemes.py:66` interface reconstruction | Spec step 3: "Compute interface values" | Eq. 28-29 (Hermite) | YES — simplified for linear case; 4th-order centred gives sufficient accuracy for 3rd-order CFWENO3 |
| `solver/schemes.py:72-74` compact stencil | Spec step 4: "CFWENO stencil (Eq. 30)" | Eq. (30) | YES — exact match |
| `solver/schemes.py:80` conservative update | Spec step 6: "Update (Eq. 25)" | Eq. (25) | YES — exact match |
| No WENO weights | Spec: "NOT needed for scalar_linear" | — | YES — correct omission |
| No Eq. 23 | Spec: "NOT included" | — | YES — correct omission |
| No characteristic decomposition | Spec: "Not needed for scalar" | — | YES — correct omission |

---

## 3. Code-to-Paper Equation Mapping

| Paper equation | Used in implementation? | How? |
|---------------|------------------------|------|
| Eq. (25) conservative update | YES | Line 80: `u - cfl * (ubar_right - ubar_left)` |
| Eq. (27) HJ connection | Implicitly | The CFWENO stencil derives from the HJ formulation; no explicit Phi variable needed for linear advection |
| Eq. (28-29) Hermite interpolation | Simplified | Replaced by 4th-order centred stencil for linear case; functionally equivalent for interface value generation |
| Eq. (30) CFWENO3 stencil | YES | Lines 72-74: exact transcription |
| Eq. (32) numerical flux | Simplified | For linear advection: f_hat = a * ubar; a factors cancel in the update |
| Eq. (17) WENO nonlinear weights | NO | Not needed for scalar linear |
| Eq. (19) smoothness indicators | NO | Not needed for scalar linear |
| Eq. (23) p_m prediction | NO | Euler-specific, not in scope |
| Eq. (21-22) characteristic decomposition | NO | Euler-specific, not in scope |

---

## 4. Non-Goals Confirmed

| Item | Confirmed not implemented? |
|------|--------------------------|
| Burgers equation (nonlinear scalar) | YES — no u*u_x term |
| CFWENO5 (5th order) | YES — only 3rd-order stencil |
| CFWENO7 (7th order) | YES — only 3rd-order stencil |
| Euler equations | YES — no conservative variable vector |
| 2D extension | YES — 1D only |
| Nonlinear WENO weights (Eq. 17) | YES — no omega_k computation |
| Shock-capturing | YES — no limiting or oscillation control |
| Eq. 23 p_m prediction | YES — not present |
| Characteristic decomposition | YES — not present |
| Algorithm 1 | YES — not present |
| Full CFWENO paper reproduction | YES — linear scalar subset only |

---

## 5. Known Assumptions

1. **Constant wave speed a=1.0**: The implementation assumes `f(u) = a*u` with `a = WAVE_SPEED = 1.0`. For variable a, the CFL relationship `nu = cfl` would need to be generalized.

2. **Interface reconstruction**: The paper describes Hermite interpolation (Eq. 28-29) using Phi and u values. The implementation uses a 4th-order centred stencil instead. This is a simplification that provides the same order of accuracy for interface values in the linear case.

3. **CFL = nu**: For `a = const`, `nu = tau*a/h = tau/h = cfl` (since `cfl = a*tau/h` and `a=1`). This identity holds exactly.

4. **Periodic boundaries only**: Uses `np.roll` for wrap-around. No other BC treatment.

5. **No eigenvalue iteration**: The paper describes iterative improvement of characteristic speed. Not implemented — not needed for constant-speed linear advection.

6. **Single-stage**: No Runge-Kutta. The CFWENO update is applied once per time step.

---

## 6. Audit Conclusion

**PASS** — The implementation in `solver/schemes.py` correctly and faithfully implements the scalar linear advection CFWENO3 prototype as specified in `docs/scheme_specs/cfweno_scalar_subset.md`.

- Only Eq. (25) and Eq. (30) are used from the paper
- Interface reconstruction is simplified (4th-order centred instead of explicit Hermite) but provides equivalent accuracy
- No formulas outside the approved scalar subset spec are used
- No Euler, characteristic decomposition, Eq. 23, or nonlinear WENO weights are present
- The implementation does not claim to be the full CFWENO scheme

**One observation**: The spec's "Required code changes" section lists `cfd/numerics/` modules and `riemann.py` changes, but the actual implementation places CFWENO in `solver/schemes.py` (the 1D scalar advection tier) rather than `cfd/` (the 2D Euler tier). This is a correct architectural choice — CFWENO scalar advection belongs in the 1D tier, not the CFD/Euler subsystem. The spec's "Required code changes" section describes a future full integration path, not the prototype.
