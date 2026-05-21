# SFM State Consistency Audit: Burgers CFWENO3

**Audit date**: 2026-05-21
**Auditor**: agentic workflow (Claude)
**Implementation commit**: c609728
**Scope**: Verify that the v1.2.1 equivalence proof uses the same state variable as the approved spec

---

## Exact Spec Quotes

### f* definition (spec section 3, lines 78–85):

```
### 3. Residual flux (flux correction)

f* = a * u^{n+1}_{i+1/2} - f(u^{n+1}_{i+1/2})

This is the difference between the linearized flux and the true nonlinear flux at
the predicted interface state.
```

### ubar definition (spec section 6, lines 110–118):

```
### 6. Interface state u^{n+1}_{i+1/2} (inherited from Eq. 30)

The CFWENO3 stencil:
ubar_{i+1/2} = u_{i+1/2} - nu*(u_{i+1/2} - u_i) - nu*(1-nu)*(u_{i-1/2} - 2u_i + u_{i+1/2})
```

Note the section heading explicitly equates `u^{n+1}_{i+1/2}` with `ubar_{i+1/2}`:
**"Interface state u^{n+1}_{i+1/2}"** defines `ubar_{i+1/2}`.

### f_hat definition (spec section 4, lines 87–91):

```
### 4. Numerical flux with correction

f_hat_{i+1/2} = a * ubar_{i+1/2} - f*
```

### Variable mapping table (spec lines 209–210):

```
| f*    | Residual flux | 0 (linear case) | a * u - u^2/2 (nonzero) |
| f_hat | Numerical flux | a * ubar        | a * ubar - f*           |
```

---

## Exact Code Formula

File: `solver/schemes.py`, lines 156–165:

```python
nu = np.clip(tau_h * a, 0.0, 1.0)
ubar_right = _cfweno3_stencil(u, nu)

f_hat_right = 0.5 * ubar_right**2    # f(ubar)
f_hat_left = np.roll(f_hat_right, 1)

return u - tau_h * (f_hat_right - f_hat_left)
```

The code computes `f_hat = f(ubar) = ubar^2/2` using `ubar` from `_cfweno3_stencil`,
which is the Eq. (30) output — the same `ubar_{i+1/2}` defined in spec section 6.

---

## State Variable Analysis

### Does the spec use the same state for f* and f_hat?

**YES.** The spec defines:

1. `u^{n+1}_{i+1/2}` = `ubar_{i+1/2}` (spec section 6 heading + formula)
2. `f* = a * u^{n+1}_{i+1/2} - f(u^{n+1}_{i+1/2})` (spec section 3)
3. `f_hat = a * ubar_{i+1/2} - f*` (spec section 4)

Substituting (1) into (2):
```
f* = a * ubar_{i+1/2} - f(ubar_{i+1/2})
```

Substituting into (3):
```
f_hat = a * ubar_{i+1/2} - (a * ubar_{i+1/2} - f(ubar_{i+1/2}))
      = f(ubar_{i+1/2})
```

The spec's `u^{n+1}_{i+1/2}` and `ubar_{i+1/2}` are the **same quantity** —
the Eq. (30) CFWENO3 stencil output. There is no separate `u_interface` distinct
from `ubar`.

### This is Case A

The spec defines `f* = a * ubar - f(ubar)`, using the same reconstructed state
`ubar_{i+1/2}` as appears in the `f_hat` formula. The code's `f_hat = f(ubar)`
is an exact algebraic simplification of the spec's two-step form, with no state
variable mismatch.

---

## Is the v1.2.1 Equivalence Proof Valid?

**YES.** The v1.2.1 flux form audit (`flux_form_audit.md`) performed the
substitution:

```
f*_{i+1/2} = a_{i+1/2} * ubar_{i+1/2} - f(ubar_{i+1/2})
```

This correctly uses `ubar_{i+1/2}` as the state in `f*`, which matches the spec's
definition where `u^{n+1}_{i+1/2}` = `ubar_{i+1/2}`. The proof is valid under
the approved spec.

The proof does NOT use a different state variable (e.g., spatial `u_{i+1/2}`
before time integration). The substitution is state-consistent.

---

## Decision

**Case A: The current implementation matches the spec exactly.**

The spec defines `f*` at `u^{n+1}_{i+1/2}`, which it equates to `ubar_{i+1/2}`
(the Eq. (30) stencil output). The code computes `f_hat = f(ubar)` using this
same `ubar`. The v1.2.1 equivalence proof correctly identifies this as an exact
algebraic identity.

No follow-up implementation is needed. No state variable inconsistency exists.

---

## Summary

| Question | Answer |
|----------|--------|
| Spec state for f* | `u^{n+1}_{i+1/2}` = `ubar_{i+1/2}` (Eq. 30 output) |
| Code state for f_hat | `ubar` from `_cfweno3_stencil` (Eq. 30 output) |
| Same state variable? | YES |
| v1.2.1 proof valid? | YES |
| Matches spec exactly? | YES |
| Follow-up needed? | NO |
