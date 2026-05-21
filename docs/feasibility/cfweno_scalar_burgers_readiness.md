# Readiness Review: CFWENO3 Scalar Nonlinear Burgers

**Date**: 2026-05-20
**Reviewer**: agentic workflow (Claude)
**Prerequisite**: v1.1 scalar linear CFWENO3 prototype (commit bb18e68)

---

## Is Burgers ready after v1.1?

**Decision: Conditionally ready**

The scalar nonlinear Burgers CFWENO3 extension is conditionally ready for implementation
after v1.1. All core formulas are self-contained in the paper. The main condition is that
Phase 1 is restricted to smooth pre-shock Burgers with no shock-capturing claims.

---

## What is already available from v1.1?

| Component | Location | Reusable? |
|-----------|----------|-----------|
| CFWENO3 compact stencil (Eq. 30) | `solver/schemes.py:36-80` | YES — same formula, generalized `nu` |
| 4th-order centred interface reconstruction | `solver/schemes.py:66` | YES — unchanged |
| Periodic boundary handling | `np.roll` in schemes.py | YES — unchanged |
| Conservative update framework | `solver/schemes.py:80` | PARTIAL — needs flux correction |
| `step()` dispatch | `solver/schemes.py:91-123` | YES — extend for new scheme name |
| `_SCHEMES` registry | `solver/schemes.py:84-88` | YES — add Burgers entry |
| `run_advection()` | `solver/simulate.py` | NO — specific to linear advection |
| `compute_errors()` | `solver/simulate.py` | YES — error metrics are equation-agnostic |
| Convergence study machinery | `examples/run_cfweno_scalar_convergence.py` | YES — adapt for Burgers |
| Demo script pattern | `examples/run_cfweno_scalar_demo.py` | YES — adapt for Burgers |
| CFL sweep pattern | `examples/run_cfweno_scalar_cfl_sweep.py` | YES — adapt for Burgers |
| Validation result generation | CSV, PNG, analysis.md pattern | YES — same output format |
| Test patterns | `tests/test_cfweno_scalar.py` | YES — adapt for Burgers |
| Approval gate | `tools/check_scheme_spec_approval.py` | YES — check new spec |
| Traceability pattern | `docs/tasks/cfweno_scalar_prototype/` | YES — replicate for Burgers |
| Formula audit pattern | `docs/tasks/cfweno_scalar_prototype/audit.md` | YES — replicate for Burgers |

---

## What is missing?

| Component | Description | Difficulty | Source |
|-----------|-------------|------------|--------|
| Nonlinear flux handling | `f(u) = u^2/2` instead of `f(u) = a*u` | Low | Trivial |
| Local wave speed | `a_i = u_i` varies spatially | Low | Paper Eq. 30 definition: `nu = tau*a/h` |
| Residual flux f* | `f* = a*u - f(u)` at interface | Low | SFM decomposition (exact simplification for scalar Burgers: `f_hat = f(ubar)`) |
| Numerical flux with correction | `f_hat = a * ubar - f*` | Low | Simplifies exactly to `f(ubar)` for scalar Burgers; two-step form needed for Euler only |
| Predictor strategy for a | Whether to iterate on `a` or freeze | Medium | Paper mentions iteration improves accuracy |
| Burgers time stepping | `dt = CFL * dx / max(|u|)` — adaptive CFL | Low | Standard Burgers CFL |
| Burgers run function | New `run_burgers()` or generalize `run_advection()` | Medium | Cannot reuse linear-specific logic |
| Reference solution strategy | Fine-grid baseline or analytic implicit | Low | Standard approaches |
| Shock handling policy | Documented decision: pre-shock only (Phase 1) | N/A | Policy decision, not code |

---

## Does Burgers require Eq. 23?

**No.** Eq. (23) is the predicted middle pressure `p_m` used in Algorithm 1 for
Euler-specific wave selection. It is not applicable to scalar Burgers:

- Algorithm 1 is designed for the Euler equations characteristic decomposition
- Scalar Burgers has a single characteristic family (no wave selection needed)
- Shock-capturing for scalar Burgers uses entropy conditions or WENO nonlinear weights,
  not pressure-based wave selection
- Eq. (23) has no role in any scalar equation

---

## Does Burgers require Euler characteristic decomposition?

**No.** Characteristic decomposition (Eq. 21-22) decomposes the Euler system into
wave families. Scalar Burgers is already a single scalar equation — no decomposition
is needed. The characteristic speed is simply `a = f'(u) = u`.

---

## Does Burgers require external papers?

**No.** All formulas needed for scalar nonlinear CFWENO3 are self-contained in the paper:

| Component | Paper source | Self-contained? |
|-----------|-------------|-----------------|
| CFWENO3 stencil (Eq. 30) | Eq. (30) | YES |
| Interface reconstruction | Eq. (28-29) or 4th-order centred | YES |
| Conservative update (Eq. 25) | Eq. (25) | YES |
| WENO nonlinear weights (if needed) | Eq. (17), Tables I-II, Eq. (19) | YES |
| SFM flux linearization | Sec. II.A | YES |
| Truncation error analysis | Sec. II.C | YES |

**Caution** (not a blocker): The paper's description of the flux linearization for
nonlinear cases is less explicit than for the linear case. Specifically:
- The exact form of `f*` computation at interfaces may need careful derivation
- The predictor iteration strategy (if needed) is described qualitatively but not
  as a step-by-step algorithm for scalar Burgers
- These are implementation details that can be resolved during development

References [6,7] (FWENO) provide derivation context but are NOT required.

---

## Recommended Decision

**Decision: Conditional GO after human approval**

**Conditions**:
1. Phase 1 restricted to smooth pre-shock Burgers only
2. No shock-capturing claims
3. Reference solution strategy must be specified before implementation
4. Predictor strategy (zero or one iteration) must be selected before implementation

**Rationale**:
- v1.1 provides a solid foundation — the CFWENO3 stencil, interface reconstruction,
  and boundary handling are all reusable
- The nonlinear extension is a natural and well-scoped increment
- All required formulas are self-contained in the paper
- The main risk (variable wave speed) is well-understood and manageable
- Pre-shock restriction provides clean validation without shock-capturing complexity
- This is an appropriate v1.2 intermediate step between linear scalar and Euler

**Risk assessment**:

| Risk | Severity | Mitigation |
|------|----------|------------|
| Variable nu affects stability | Medium | CFL based on max(|u|); empirical sweep |
| Flux linearization accuracy | Medium | Pre-shock smooth case is forgiving |
| Convergence order < 3 | Low-Medium | Predictor iteration as fallback |
| Post-shock oscillations | Expected | Not in Phase 1 scope; documented |

**Recommended next action**: Human reviews `docs/scheme_specs/cfweno_scalar_burgers_subset.md`,
selects predictor strategy and reference solution approach, sets approval to `yes`.
