# Roadmap: v1.x Real-Paper Demo (CFWENO)

## Current State — v1.0 Demo Packaging Complete

The CFWENO real-paper demo is packaged as a **v1.0 milestone**:
- **v1.1**: Scalar linear CFWENO3 — **complete** (3rd-order convergence)
- **v1.2**: Scalar Burgers CFWENO3 — **complete** (~2nd-order, documented)
- **v1.2.1**: Burgers flux-form audit — **complete** (f_hat = f(ubar) is exact identity)
- **v1.2.2**: SFM state-consistency audit — **complete** (state variables match spec)
- **v1.0 packaging**: Case study, unified demo target — **complete**

Run: `make demo-real-paper-cfweno`

Case study: `docs/case_studies/cfweno_real_paper_demo.md`

---

## Detailed History

v1.1 is **complete**. The scalar linear CFWENO3 prototype has been implemented, hardened, and validated:

- Implementation commit: `2b580ef`
- Formula audit: PASS (Eq. 30 stencil verified against spec and paper)
- Convergence: **exactly 3rd order** (3.04 -> 3.01 -> 3.00)
- CFL sweep: stable at CFL 0.1, 0.5, 0.9
- Baseline comparison: upwind (1st), Lax-Wendroff (2nd), CFWENO3 (3rd)
- Tests: 19 CFWENO-specific tests + 212 total passing
- **Not** complete CFWENO — scalar linear advection prototype only

The v1.0 intake for the CFWENO paper (Zhou-Dong-Pan 2025, Phys. Fluids 37, 106131) is **complete**. The full paper-to-code workflow has been exercised from PDF extraction through feasibility assessment, producing:

- Paper reference metadata
- Comprehensive extraction report (25 pages, 9 sections)
- Scheme specification (with approval gate set to `no`)
- Feasibility assessment (verdict: intake complete, implementation deferred)
- Traceability manifest

**Phase 2.5 correction**: The original Phase 2 assessment classified references [6,7] as CRITICAL blockers for ALL subsets. The Phase 2.5 readiness audit confirms this was incorrect — the paper self-contains Eq. (17), Tables I-II, Eq. (19) for WENO weights, and Eq. (27-30) for the CFWENO3 stencil. **Scalar CFWENO3 has ZERO external blockers and can proceed immediately.**

---

## Phased Implementation Plan

### Implementation Subsets

The CFWENO scheme decomposes into three subsets with independent blockers:

| Subset | Scope | Blocking dependencies | Target phase |
|--------|-------|----------------------|--------------|
| **Scalar Linear** | Linear advection, constant a, CFWENO3 stencil | **NONE** | v1.1 (COMPLETE) |
| **Scalar Nonlinear** | Burgers, variable a, flux linearization | **NONE** | v1.2 (spec created) |
| **Euler 1D** | Characteristic decomposition, Algorithm 1, compact flux, p_m prediction | Eigenvalue iteration, p_m verification | v1.3 |
| **2D Euler** | Consistent cell-interface distribution, dimensional composition | None additional | v1.4 |

Key insight: **Scalar subset can proceed immediately** — Phase 2.5 audit confirms ZERO external blockers. References [6,7] are NOT needed.

### v1.1 — Scalar CFWENO3 Prototype (COMPLETE)

**Status**: Implemented and hardened.

| Item | Result |
|------|--------|
| Linear advection CFWENO3 | Eq. 30 stencil, 3rd-order convergence |
| CFL sweep | Stable at CFL 0.1, 0.5, 0.9 |
| Baseline comparison | upwind / Lax-Wendroff / CFWENO3 |
| Formula audit | PASS — only Eq. 25 + Eq. 30 used |
| Spec approval | cfweno_scalar_subset.md = yes |
| Remaining | Burgers (nonlinear) requires separate approval |

**Next step for scalar nonlinear**: Separate approval needed for Burgers extension.

### v1.2 — Scalar Nonlinear Burgers CFWENO3 (COMPLETE)

**Status**: Implemented and validated.

| Item | Result |
|------|--------|
| Burgers CFWENO3 | Eq. 30 stencil with per-cell nu, SFM flux f(ubar) |
| Convergence | ~2nd order (2.01) — reduced from 3rd due to per-cell nu variation |
| Accuracy vs Rusanov | 173x more accurate at nx=100 |
| Predictor iterations | 0/1/2 supported, default 1 |
| Reference | Fine-grid CFWENO3 Burgers (nx=2560) |
| Spec approval | cfweno_scalar_burgers_subset.md = yes |
| Tests | 19 Burgers-specific tests + 236 total passing |
| Remaining | Post-shock validation (not in scope), Euler, CFWENO5/7 |

**Convergence note**: CFWENO3 Burgers achieves ~2nd-order convergence on smooth pre-shock data, not the 3rd order observed for linear advection. This is attributed to per-cell nu variation introducing truncation error in the CFWENO3 stencil.

**Flux form note**: The Burgers prototype uses `f_hat = f(ubar) = ubar^2/2`, an exact algebraic identity of the SFM two-step form `f_hat = a*ubar - f*` for scalar Burgers. This is not an approximation — it does not contribute to the observed order reduction. The explicit two-step SFM form is only needed for the Euler system extension (v1.4).

**Implemented files**:
- `solver/schemes.py` — added `cfweno_burgers()`, `burgers_upwind()`, helper functions
- `examples/run_cfweno_burgers_demo.py`
- `examples/run_cfweno_burgers_convergence.py`
- `tests/test_cfweno_burgers.py`
- Makefile targets: `cfweno-burgers-demo`, `cfweno-burgers-convergence`, `demo-real-paper-burgers`

### v1.3 — Euler Prep (Gap Resolution)

**Goal**: Resolve Euler-specific gaps and prepare for Euler 1D implementation.

| Item | Action | Dependency |
|------|--------|------------|
| Eigenvalue iteration | Identify iteration start guess, count, and convergence from FWENO literature | Access to refs [6,7] |
| p_m formula (Eq. 23) | Re-read paper page containing Eq. 23 at higher resolution or transcribe manually | Paper access |
| CFL stability | Verify CFL <= 1 claim against test cases; document empirical limit | Code from v1.1/v1.2 |
| FWENO refs [6,7] | Obtain for derivation context (not blocking for scalar) | Access to referenced papers |

**Deliverables**:
- Updated extraction report with Euler-specific items resolved
- Updated full scheme spec with complete algorithmic detail

### v1.4 — CFWENO3 Euler 1D

**Goal**: Extend to 1D Euler equations with characteristic decomposition and Algorithm 1.

| Component | Scope |
|-----------|-------|
| Characteristic decomposition | Roe averages, eigenvector matrices |
| Flux reconstruction | Full Algorithm 1 (all 4 branches) |
| Validation | Entropy wave, Shu-Osher, Titarev-Toro |

**Files**:
- New: `cfd/numerics/characteristic.py`
- Extended: `cfd/numerics/riemann.py` (CFWENO flux)
- Extended: `cfd/numerics/update.py` (dispatch)
- New: `examples/run_cfd_cfweno_euler1d.py`

**Validation criteria**:
- Entropy wave: L2 error comparable to or better than HLL
- Shu-Osher: density profile matches published results qualitatively
- Uniform flow: preserved to machine precision

### v1.5 — Higher Orders and 2D

**Goal**: Add CFWENO5/7 and multi-dimensional extension.

| Component | Scope |
|-----------|-------|
| WENO orders | 5th and 7th order weights |
| Multi-dimensional | Consistent cell-interface distribution (Eq. 33) |
| Validation | 2D Riemann problem, 2D vortex |

**Files**:
- Extended: `cfd/numerics/weno.py` (5th/7th order)
- Extended: `cfd/numerics/riemann.py` (order parameter)
- New: `cfd/numerics/cfweno_2d.py` (dimensional extension)
- New: `examples/run_cfd_cfweno_2d.py`

---

## Comparison with v0.1 HLL Demo

| Aspect | v0.1 (HLL) | v1.1-v1.4 (CFWENO) |
|--------|------------|---------------------|
| Scope | Single Riemann solver | Full scheme (reconstruction + flux + time integration) |
| New LOC | ~150 | ~150-250 (v1.1 scalar) + ~820-1230 (total across v1.1-v1.4) |
| Phases | Single implementation | 4 phased implementations |
| External refs needed | None | 0 for scalar (v1.1-v1.2); refs [6,7] useful for Euler context (v1.3+) |
| Demo value | First paper-to-code workflow | Second method, higher complexity |

---

## Success Metrics

1. **v1.1**: Scalar CFWENO3 linear advection prototype with 3rd-order convergence verified — COMPLETE
2. **v1.2**: Scalar CFWENO3 nonlinear Burgers (smooth pre-shock) with convergence trend — COMPLETE
3. **v1.3**: Euler-specific gaps resolved (eigenvalue iteration, p_m)
4. **v1.4**: Algorithm 1 produces correct wave selection; Shu-Osher matches published results
5. **v1.5**: 2D extension maintains formal order; CFWENO5/7 converge at expected rates

---

---

## Post-v1.0 Diagnostic Work

### Burgers Nonlinear Order Recovery (v1.1-pre)

**Status**: Diagnostic study complete.

Investigates whether 3rd-order convergence can be recovered for scalar Burgers CFWENO3
by testing alternative nu treatments (constant, interface-based, predictor-updated).

| Item | Status |
|------|--------|
| Diagnostic plan | `docs/tasks/cfweno_burgers_order_recovery/diagnostic_plan.md` |
| Experiment script | `examples/run_cfweno_burgers_order_recovery.py` |
| Results | `results/cfweno_burgers_order_recovery/` |
| Traceability | `docs/tasks/cfweno_burgers_order_recovery/traceability.md` |

**Follow-up actions**:
- If successful: prepare approved spec for improved Burgers CFWENO3
- If unsuccessful: keep Burgers as ~2nd-order prototype; consider CFWENO5 scalar or Euler readiness
- Euler readiness (v1.3) remains future work regardless of diagnostic outcome

**Result**: Unsuccessful — no variant recovered 3rd order. Decision: proceed to CFWENO5 scalar readiness.

### Scalar CFWENO5 Readiness Review (v1.3-pre)

**Status**: Readiness review complete — **CONDITIONALLY READY** after human verification.

After Burgers order recovery confirmed ~2nd order is structural, the next target
is CFWENO5 scalar linear advection. This is safer than Euler and provides a
higher-order smooth-problem benchmark.

| Item | Status |
|------|--------|
| Diagnostic plan | `docs/tasks/cfweno5_scalar_readiness/diagnostic_plan.md` |
| Subset spec (not approved) | `docs/scheme_specs/cfweno5_scalar_subset.md` |
| Feasibility review | `docs/feasibility/cfweno5_scalar_readiness.md` |
| Traceability | `docs/tasks/cfweno5_scalar_readiness/traceability.md` |
| Formula extraction report | `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md` |

**Formula extraction** (commit cb6b64a):
- All formulas extracted from paper via pdftotext
- Appendix A (Eqs. A1-A2): CFWENO5 substencil expressions — extracted, medium confidence
- Table I r=3 weights: extracted, k=2 uncertain
- Table II r=3 weights: extracted, low confidence (mangled layout)
- Eq. (19) smoothness indicators: extracted, medium confidence

**Human verification** (this commit):
- Table I k=2 **corrected** to `(1-nu)(2-nu)/6` (was `(1-nu)(2+nu)/6`)
- Table I r=3 has 3 valid entries (k=3 = N/A)
- Table II r=3 fully verified — 3 valid entries with correct formulas
- Table II r=3 has 3 valid entries (k=3 = N/A), singularities at nu=1/3 and nu=2/3
- Appendix A visually confirmed present — transcription not independently verified
- **Decision: CONDITIONALLY READY — Appendix A transcription needs final check**

**Remaining before approval**: Character-level verification of Appendix A Eqs. (A1)-(A2).

**Recommended path**: Verify Appendix A transcription → approve spec → refactor solver → implement.

**Decision**: Conditionally ready. Implementation pending Appendix A verification + approval.

**CFWENO5 Implementation Attempt — FAILED** (v1.3, commit dc78864):
- CFWENO5 scalar linear advection implemented per approved spec
- Observed ~1st-order convergence (expected ~5th)
- s2 substencil only 2nd-order individually (expected 4th)
- All CFWENO5 code reverted; diagnostic committed
- See `docs/tasks/cfweno5_scalar_prototype/failed_attempt_diagnostic.md`

**Formula Gate Hardening** (v1.3-pre.7, this commit):
- Appendix A formulas demoted to medium/failed_validation
- New `consistency_status` field — required formulas with status=failed block strict check
- New tool: `tools/check_cfweno5_formula_consistency.py` — substencil convergence checker
- New re-verification plan: `docs/tasks/cfweno5_formula_verification/appendix_a_reverification_plan.md`
- Strict formula confidence gate now correctly BLOCKS implementation
- `Approved for implementation` reverted to `no`

### Scalar CFWENO5 s2 Re-transcription (v1.3-pre.8)

**Status**: Partial — s2 correction confirmed, combined scheme still failing.

The s2 substencil 1/2 factor was re-transcribed from pdftotext -layout
column-position analysis. The 0.5 factor was on the wrong correction term:
moved from `(1/2)(1-nu)(u_{i+1/2} - u_i)` (first term) to
`(1/2)(1-nu)(-nu)(u_i - 2*u_{i+1/2} + u_{i+1})` (second term).

**Results after correction**:
| Component | Before | After |
|-----------|--------|-------|
| s2 individual order | ~2.0 | **~4.0** |
| All 4 substencils | 3 pass / 1 fail | **4/4 pass** |
| Combined scheme | ~1.0 | ~1.0 (unchanged) |

The combined scheme failure persists, indicating additional errors beyond s2.
Initially suspected: Table I weight sum ≠ 1, or s3/N/A weight assignment issue.

Re-transcription doc: `docs/tasks/cfweno5_formula_verification/s2_retranscription.md`

### Scalar CFWENO5 Weight Role Audit (v1.3-pre.9)

**Status**: Complete — normalization is necessary but insufficient.

Comprehensive audit of Table I/Table II weight role and Eq. (17) normalization:

| Variant | Order | Weight Sum | Finding |
|---------|-------|-----------|---------|
| Table I raw (current) | 1.00 | 0.625 | Broken — no normalization |
| Table I normalized (Eq. 17) | 3.00 | 1.0 | Fixes 1st→3rd but NOT 5th |
| Table II raw | 3.02 | 1.0 | Wrong target, caps at 3rd |
| Table II normalized | 3.02 | 1.0 | Same as raw |
| Equal 1/3 weights | 3.00 | 1.0 | Same ceiling as optimal weights |

**Conclusion C**: Normalization fixes the ~1st-order problem but ALL weight variants
cap at ~3rd order. The ~3.0 ceiling is weight-independent. The substencil polynomials
from Appendix A Eq. (A1) have additional coefficient errors beyond normalization.
The polynomial decomposition error cancellation (Eq. 15) is broken.

**Next step**: Re-verify ALL Appendix A Eq. (A1) substencil polynomials (s0, s1, s2, s3)
from the rendered PDF at high resolution.

Audit doc: `docs/tasks/cfweno5_formula_verification/weight_role_audit.md`
New tool flag: `--diagnose-weights` in `tools/check_cfweno5_formula_consistency.py`

---

**Formula confidence workflow** (this commit):
- Formula inventory: `docs/formula_inventories/cfweno5_scalar_formulas.yml`
- Confidence checker: `tools/check_formula_confidence.py` (supports 'derived' verification status)
- Confidence report: `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_confidence_report.md`
- 11 high / 1 medium (optional) / 0 low formulas
- 0 blocking formulas
- Strict check (`make formula-confidence-cfweno5-strict`) **PASSES**
- A2 derivation policy: `docs/tasks/cfweno5_formula_verification/a2_derivation_policy.md`
- A2 reclassified from required/blocking to optional/non-blocking
- Key rationale: A2 = d/dv(A1), derivable from verified source
- Ready for human approval (Approved remains `no` until human decides)

---

## Next Step Candidates

1. **Accept v1.2 as demo milestone**: The ~2nd-order Burgers result is documented and audited; accept it as a valid prototype outcome
2. **Investigate nonlinear order recovery**: Explore whether modified predictor strategies or stencil corrections can restore 3rd order for nonlinear problems
3. **CFWENO5 scalar**: Implement 5th-order scalar CFWENO from paper Eq. (30) variant
4. **Euler readiness**: Resolve eigenvalue iteration and p_m (Eq. 23) gaps for v1.3
5. **Post-shock Burgers**: Only after nonlinear WENO policy (Eq. 17) is defined and approved
