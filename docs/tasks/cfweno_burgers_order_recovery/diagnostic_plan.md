# Diagnostic Plan: Burgers CFWENO3 Nonlinear Order Recovery

**Task ID**: cfweno_burgers_order_recovery
**Task type**: post-v1.0 diagnostic (not a production change)
**Based on**: v1.0 tag `42d97ee`
**Date**: 2026-05-21

---

## Current Issue

| Property | Linear (v1.1) | Burgers (v1.2) |
|----------|--------------|----------------|
| Observed order | ~3.02 | ~2.01 |
| nu treatment | constant scalar | per-cell array |
| Flux form | `a * ubar` | `f(ubar) = ubar^2/2` |

The CFWENO3 stencil (Eq. 30 from Zhou-Dong-Pan 2025) was derived under the
assumption of constant `nu = tau * a / h`. For linear advection, `a` is a global
constant and `nu` is scalar — the derivation assumptions hold exactly. For
Burgers, `a = u` varies spatially, making `nu_i = tau * u_i / h` per-cell.

Three audits (formula consistency, flux-form identity, SFM state consistency)
confirm the v1.2 implementation is mathematically correct against the spec.
The 2nd-order result is a consequence of the underlying stencil derivation
assumptions, not a bug.

## Main Hypotheses

1. **Per-cell nu variation** (primary): When the stencil operates across cells
   with different `nu` values, the spatial gradient of `nu` introduces truncation
   error proportional to `nu'`, reducing formal order by approximately one.
   A constant or interface-based `nu` might partially restore 3rd-order.

2. **Interface-speed nu**: Using reconstructed interface values to define `nu`
   at the interface level (rather than cell centres) may better match the
   stencil derivation's constant-nu assumption within each stencil application.

3. **Predictor-updated interface nu**: Running the predictor to refine interface
   states and then computing `nu` from those refined states may reduce the
   nu-variation-induced error.

4. **SFM treatment fidelity**: The current implementation uses the direct flux
   form `f_hat = f(ubar)`, which is algebraically exact for scalar Burgers but
   may not exercise the full SFM machinery that the paper's nonlinear extension
   relies upon. This is a secondary hypothesis.

5. **Reference solution contamination**: Previously ruled out — convergence order
   is insensitive to reference resolution (nx=1280/2560/5120).

6. **Nonlinear strength**: Reduced amplitude or shorter simulation time may
   reduce the per-cell nu variation and push observed order closer to 3. This
   would confirm the nu-variation hypothesis but does not constitute a fix.

## Diagnostic Variants

| ID | Variant | nu treatment | Notes |
|----|---------|-------------|-------|
| A | **current** | per-cell `nu = tau * u_i / h` | Baseline (matches v1.0 production) |
| B | **constant-nu** | global `nu = tau * mean(u) / h` | Tests if removing spatial nu variation restores order |
| C | **interface-nu** | `nu` from reconstructed interface `u_half` | Tests if interface-level nu better matches derivation |
| D | **predictor-interface-nu** | predictor-updated interface `nu` | Combines predictor + interface nu |
| E | **reduced-amplitude** | `u0 = 1 + 0.05 sin(2pi x)` | Tests nonlinear strength effect |
| F | **shorter-time** | `T = 0.05` | Reduces time for nu variation to accumulate |

These are **diagnostic variants only** — not approved production schemes.

## Success Criteria

- If any variant achieves observed order >= 2.8: candidate for follow-up spec
- If all variants remain <= 2.3: the 2nd-order result is structural, requiring
  nonlinear WENO weights (Eq. 17) or more fundamental changes
- Conservative language throughout: "candidate", "suggests", "does not prove"

## Constraints

- `solver/schemes.py` is NOT modified
- All variants live in the experiment script only
- No new schemes registered in `_SCHEMES`
- v1.0 demo must remain unaffected
- No post-shock testing
- No Euler, 2D, or CFWENO5/7 work
