# CFWENO3 Burgers Nonlinear Order Recovery — Diagnostic Study

**Status**: Post-v1.0 diagnostic (not a production change)

**Purpose**: Determine whether 3rd-order convergence can be recovered for scalar Burgers CFWENO3 by changing the nu treatment.

**Constraint**: solver/schemes.py was NOT modified.

## Hypothesis

The CFWENO3 stencil (Eq. 30) was derived for constant nu. For Burgers, per-cell `nu_i = dt * u_i / dx` varies spatially, introducing truncation error that reduces convergence to ~2nd order.

If using a constant or interface-based nu restores ~3rd order, it confirms the nu-variation hypothesis and suggests a path to recovery.

## Diagnostic Variants

| ID | Variant | nu treatment |
|----|---------|-------------|
| A | current (production) | per-cell `nu = tau * u_i / h` |
| B | constant global nu | `nu = tau * mean(u) / h` |
| C | interface-speed nu | `nu` from reconstructed `u_{i+1/2}` |
| D | predictor + interface nu | predictor-updated `nu` |

## Case: standard

- amplitude = 0.2
- final_time = 0.1
- CFL = 0.5
- nx = [40, 80]
- reference_nx = 320

### Error Table

| Variant | nx | L2 | Observed Order |
|---------|----|----|---------------|
| A_current | 40 | 5.595314e-05 | 2.07 |
| A_current | 80 | 1.335571e-05 | 2.07 |
| B_constant_nu | 40 | 5.808894e-04 | 0.98 |
| B_constant_nu | 80 | 2.954466e-04 | 0.98 |
| C_interface_nu | 40 | 1.331561e-05 | 1.69 |
| C_interface_nu | 80 | 4.113335e-06 | 1.69 |
| D_predictor_interface_nu | 40 | 5.583889e-05 | 2.07 |
| D_predictor_interface_nu | 80 | 1.334009e-05 | 2.07 |

### Convergence Orders (L2)

| Variant | Avg Order |
|---------|----------|
| A: current (per-cell nu) | **2.07** |
| B: constant global nu | **0.98** |
| C: interface-speed nu | **1.69** |
| D: predictor + interface nu | **2.07** |

## Conclusions

1. **Best observed order**: 2.07 (variant A_current)
2. **Lowest L2 error at finest grid**: variant C_interface_nu
3. No variant approaches 3rd order (best = 2.07).
   The ~2nd-order result appears to be **structural** for the current CFWENO3 stencil applied to Burgers with any simple nu treatment.
   Recovery may require the paper's nonlinear WENO weights (Eq. 17, Tables I-II) or a fundamentally different approach.

4. The production solver/schemes.py was NOT modified.
5. Any variant that shows improvement is a **diagnostic finding only**;
   it requires a formal spec update and approval before production use.
6. The reduced-amplitude and shorter-time cases help distinguish
   whether the order reduction is nonlinear-strength-dependent.

## Limitations

- Diagnostic variants are NOT approved for production
- Reference solutions are numerical (fine-grid), not analytic
- Only pre-shock smooth data tested
- No shock-capturing (Eq. 17 nonlinear WENO weights not implemented)
- These results do not constitute a complete CFWENO implementation
