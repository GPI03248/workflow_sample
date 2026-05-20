# Feasibility Assessment: CFWENO Schemes (Zhou-Dong-Pan 2025)

**Paper**: Physics of Fluids 37, 106131 (2025), DOI: 10.1063/5.0291087
**Assessment date**: 2026-05-18
**Assessor**: agentic workflow (Claude)

---

## 1. Suitability for v1.0 Paper-to-Code Demo

### Criteria

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Paper completeness | Medium | Core algorithm extracted; WENO weights, p_m formula, eigenvalue iteration details unresolved |
| Algorithmic clarity | Medium-High | Algorithm 1 fully specified; Hermite interpolation clear; multi-dimensional extension stated |
| Code complexity | High | ~500-800 LOC new code; characteristic decomposition + WENO reconstruction + multi-branch flux |
| Existing code reuse | High | Can reuse mesh, variables, boundary, cases, physics modules |
| Validation feasibility | High | All test cases (entropy wave, vortex, Shu-Osher) are standard and well-understood |
| Risk of implementation failure | Medium | Unresolved items are non-trivial but not blocking for a partial (3rd-order scalar) implementation |

### Overall Suitability: **Conditional — suitable for phased implementation, not for a single demo**

---

## 2. Complexity Analysis

### Tier: HIGH (overall) — decomposed by subset

**Why high (overall):**
- Requires characteristic decomposition (Roe averages, eigenstructure extraction)
- Multi-branch flux reconstruction with 4+ branches per interface
- WENO reconstruction (weights from external references, not fully specified in paper)
- Hermite interpolation for Hamilton-Jacobi potential
- Eigenvalue iteration with unspecified convergence criteria

**Subset decomposition:**

| Subset | Components | Unresolved items | Dependencies | Estimated LOC | Difficulty |
|--------|-----------|-----------------|--------------|---------------|------------|
| **Scalar 1D** | HJ equation (Eq. 27), Hermite interpolation (Eq. 28-29), CFWENO stencil (Eq. 30), numerical flux (Eq. 32), update (Eq. 25), WENO weights (Eq. 17, Tables I-II, Eq. 19) | CFL stability (low priority, empirically verified) | **NONE** — all formulas self-contained in paper | ~150-250 | Medium |
| **Euler 1D** | + Characteristic decomposition (Eq. 21-22), Algorithm 1 flux reconstruction, p_m prediction (Eq. 23), compact flux (Eq. 24) | + Eigenvalue iteration, p_m verification | Eigenvalue iteration details, Eq. 23 verification | ~350-550 (total) | High |
| **2D Euler** | + Consistent cell-interface distribution (Eq. 33), dimensional composition | None additional | None additional | ~450-700 (total) | High |

### Estimated effort (new LOC, by component):

| Component | Lines | Difficulty | Subset |
|-----------|-------|------------|--------|
| Hermite interpolation | ~50-80 | Low | Scalar |
| WENO reconstruction (3rd order) | ~80-120 | Medium | Scalar |
| CFWENO stencil (Eq. 30) | ~30-50 | Low | Scalar |
| Numerical flux (Eq. 32) | ~40-60 | Medium | Scalar |
| Characteristic decomposition | ~100-150 | Medium | Euler |
| Algorithm 1 flux reconstruction | ~100-150 | High | Euler |
| Compact flux (Eq. 24) | ~60-80 | Medium | Euler |
| WENO reconstruction (5th order) | ~80-120 | Medium | Scalar (extended) |
| WENO reconstruction (7th order) | ~80-120 | Medium | Scalar (extended) |
| Multi-dimensional extension | ~40-60 | Medium | 2D |
| Tests | ~200-300 | Medium | All |
| **Total** | **~820-1230** | — | — |

---

## 3. Dependencies on Existing Code

### Can reuse (no modification needed)
- `cfd/mesh/` — grid layout, cell centres
- `cfd/variables/` — primitive <-> conservative conversion
- `cfd/boundary/` — ghost-cell filling
- `cfd/physics/` — EOS, physical fluxes, wave speeds
- `cfd/cases/` — IC + config for test problems
- `cfd/validation/` — error metrics, analytic comparison
- `cfd/io/` — output to disk

### Must extend
- `cfd/numerics/riemann.py` — add CFWENO flux functions
- `cfd/numerics/update.py` — add dispatch for `flux_type="cfweno"`
- `cfd/numerics/time_integration.py` — single-stage CFWENO update
- `cfd/config.py` — add `cfweno_order` parameter

### New modules needed
- `cfd/numerics/characteristic.py` — Roe averages, eigenvector matrices, eigenvalues
- `cfd/numerics/hermite.py` — Hermite interpolation for Phi and u
- `cfd/numerics/weno.py` — WENO reconstruction (3rd/5th/7th order weights)

---

## 4. Risk Assessment

### Subset-Specific Risk Summary

| Risk | Affects | Severity | Blocking? |
|------|---------|----------|-----------|
| WENO weight formulas not in paper | ~~Scalar, Euler, 2D~~ Euler, 2D only | ~~High~~ Medium | ~~YES — all subsets~~ NO — paper self-contains Eq. 17, Tables I-II, Eq. 19 |
| Eigenvalue iteration details missing | Euler, 2D | High | YES — Euler and 2D only |
| p_m formula (Eq. 23) uncertainty | Euler, 2D | Medium | YES — Euler and 2D only |
| CFL stability limit unproven | All subsets | Low | No — empirically verifiable |
| Multi-dimensional extension correctness | 2D only | Medium | No — testable |

**Key insight (updated Phase 2.5)**: The scalar subset has **ZERO external blocking dependencies**. The paper self-contains all formulas needed for scalar linear CFWENO3 (Eq. 27-30) and scalar nonlinear CFWENO3 (Eq. 17, Tables I-II, Eq. 19). The original classification of WENO weights [6,7] as blocking for all subsets was incorrect.

### High Risks

1. **~~WENO weight formulas not in paper~~** — CORRECTED by Phase 2.5 audit: The paper self-contains Eq. (17) for nonlinear weights ω̄_k^r, ω_k^r; Tables I-II for optimal linear weights γ̄_k^r, γ_k^r; Eq. (19) for smoothness indicators β_k^r; and Table III for discontinuity positions δ_r^k. References [6,7] provide FWENO derivation context but are NOT needed for implementation. This risk is demoted to "informational" for scalar subsets.

2. **Eigenvalue iteration details missing** — The paper states that iterative improvement of characteristic speed `a` increases accuracy but does not specify:
   - Starting guess for `a`
   - Number of iterations
   - Convergence tolerance
   - Fallback if iteration fails

3. **p_m formula (Eq. 23) transcription uncertainty** — The middle pressure prediction is critical for Algorithm 1 branching. Complex formula in image-based PDF; transcription may have errors.

### Medium Risks

4. **CFL stability limit unproven** — Paper claims CFL <= 1 sufficient but provides no rigorous proof. Actual stability limit may be more restrictive for certain flow configurations.

5. **Multi-dimensional extension correctness** — The consistent cell-interface distribution (Eq. 33) is stated to maintain formal order, but verification requires 2D convergence tests that may reveal subtle issues.

6. **Characteristic decomposition robustness** — Roe averages can be ill-conditioned near vacuum states or strong shocks. No vacuum handling discussed in paper.

### Low Risks

7. **Performance** — Single-stage nature should be faster than WENO-RK, but memory access patterns for compact stencils may be less cache-friendly.

8. **Boundary treatment** — Compact stencils require wider ghost-cell regions. Existing BC modules may need extension.

---

## 5. Comparison with HLL (v0.1 Demo)

| Aspect | HLL (v0.1) | CFWENO (v1.0 candidate) |
|--------|------------|--------------------------|
| Paper completeness | Complete | 4 unresolved items |
| New LOC | ~150 | ~820-1230 |
| New modules | 0 (extended riemann.py) | 3+ (characteristic, hermite, weno) |
| Algorithmic branches | 1 (3-wave selection) | 4+ (pressure-based wave selection) |
| Time integration | Existing (no change) | New single-stage |
| Validation difficulty | Standard | Standard + Shu-Osher |
| Implementation risk | Low | Medium-High |
| Demo impact | First paper-to-code | Significant method addition |

---

## 6. Recommendation

### For v1.0 paper-to-code demo: **DEFER to v1.1+**

**Rationale:**

1. **4 unresolved items** in the extraction prevent a complete implementation. The WENO weight formulas are fundamental — without them, the scheme cannot be implemented at all.

2. **High complexity** (~820-1230 LOC) makes this unsuitable for a demo that should be reproducible and verifiable in a single session. The HLL demo (v0.1) was ~150 LOC and demonstrated the workflow cleanly.

3. **Missing reference dependencies** — The paper references earlier FWENO work for critical components. A complete implementation requires obtaining and extracting those references as well.

4. **Eigenvalue iteration** is an algorithmic component with unspecified parameters. Implementing it without clear convergence criteria risks numerical instability.

### Recommended path forward (updated Phase 2.5 — scalar unblocked)

1. **v1.0**: Keep CFWENO as intake-only (extraction report + scheme spec + feasibility = this document) — COMPLETE
2. **v1.1**: Implement scalar linear + nonlinear CFWENO3 prototype (ZERO external blockers; all formulas in paper)
3. **v1.2**: Obtain FWENO refs [6,7] (context only), resolve eigenvalue iteration + verify p_m → Euler prep
4. **v1.3**: Implement CFWENO3 Euler 1D with Algorithm 1
5. **v1.4**: Add CFWENO5/7 and 2D extension

**Scalar subset can proceed immediately** — no external references needed. This is a significant change from Phase 2 assessment which incorrectly classified refs [6,7] as blocking for all subsets.

### What v1.0 delivers

Even without implementation, the v1.0 intake demonstrates the full paper-to-code workflow:
- PDF extraction (25 pages, image-based)
- Structured extraction report with completeness assessment
- Scheme spec with approval gate (set to `no`)
- Feasibility assessment with explicit go/no-go recommendation
- Traceability manifest linking all artifacts
- This is the **intake and feasibility** phase — it is complete and correct.

---

## 7. Decision Matrix

| Question | Answer |
|----------|--------|
| Can the scheme be fully specified from this paper alone? | No — requires external references for WENO weights |
| Is the implementation complexity proportional to the demo value? | No — too complex for a demo |
| Are all stability properties understood? | No — CFL limit unproven, iteration convergence unspecified |
| Can existing validation cases be reused? | Yes — entropy wave, vortex, Shu-Osher are all applicable |
| Is the risk of implementation failure acceptable for a demo? | No — too many unknowns |
| Should implementation proceed? | Not for v1.0. Revisit after resolving extraction gaps. |

---

## 8. Conclusion

**Verdict: INTAKE COMPLETE, IMPLEMENTATION DEFERRED**

The CFWENO paper has been thoroughly extracted and assessed. The method is scientifically interesting and the paper is well-written, but it does not meet the bar for a v1.0 demo due to:

1. Incomplete extractability (4 unresolved items requiring external references)
2. High implementation complexity (~820-1230 LOC vs. ~150 for HLL)
3. Missing algorithmic parameters (WENO weights, iteration criteria)

The intake itself is a valuable v1.0 artifact — it demonstrates the full paper-to-code workflow from PDF to go/no-go decision.

---

## 9. Phase 2.5 Readiness Audit (2026-05-19)

### Purpose

Re-audit formula coverage for the scalar CFWENO3 subset after Phase 2 incorrectly classified references [6,7] as critical blockers for ALL implementation subsets.

### Formula Coverage Audit — Scalar Linear CFWENO3

| Formula | Paper source | Self-contained? | Notes |
|---------|-------------|-----------------|-------|
| HJ equation connection | Eq. (27): Φ_t + f(Φ_x)_x = 0, u = Φ_x | YES | Directly stated |
| Hermite interpolation for Φ(x) | Eq. (28): cubic Hermite using {Φ_i, u_i, Φ_{i±1/2}} | YES | Explicit stencil description |
| Derivative u(x) = dΦ/dx | Eq. (29) | YES | Direct derivative of Eq. 28 |
| CFWENO3 stencil (current time) | Eq. (30): ū_{i+1/2} = u_{i+1/2} - ν(u_{i+1/2} - u_i) - ν(1-ν)(u_{i-1/2} - 2u_i + u_{i+1/2}) | YES | Explicit formula with ν = τa/h |
| CFWENO3 stencil (next time) | Eq. (30): ū_{i+1/2}^{n+1} = u_{i+1/2} + 2(-ν)(u_{i+1/2} - u_i) + (-ν)(2-3ν)(u_{i-1/2} - 2u_i + u_{i+1/2}) | YES | Explicit formula for next time level |
| Numerical flux (linear) | Derivable: f_hat = a * ū_{i+1/2} for f(u) = a*u | YES | For constant-speed linear advection |
| Conservative update | Eq. (25): u_i^{n+1} = u_i^n - (τ/h)*(f̂_{i+1/2} - f̂_{i-1/2}) | YES | Standard conservative form |

**Readiness judgment — scalar linear**: **READY** (7/7 formulas self-contained, 0 external blockers)

### Formula Coverage Audit — Scalar Nonlinear CFWENO3 (Burgers)

| Formula | Paper source | Self-contained? | Notes |
|---------|-------------|-----------------|-------|
| All scalar linear formulas | See above | YES | All applicable |
| WENO nonlinear weights | Eq. (17): ω̄_k^r = γ̄_k^r / Σγ̄_l^r, γ̄_k^r = ᾱ_k^r/(β̄_k^r + ε)² | YES | Full weight formula present |
| Optimal linear weights γ̄_k^r | Table I: explicit values for r=2,3,4 (e.g., r=3: γ̄₀³=(1+ν)²/6, γ̄₁³=(1+ν)(2-ν)/6, γ̄₂³=(1-ν)(2-ν)/6) | YES | Numerical values given |
| Optimal linear weights γ_k^r | Table II: explicit values for next-time-level reconstruction | YES | Numerical values given |
| Smoothness indicators β_k^r | Eq. (19): explicit formulas | YES | Full indicator formulas present |
| Discontinuity positions δ_r^k | Table III | YES | Numerical values given |
| Error coefficients | Table IV: CFWENO vs FWENO vs WENO | YES | Confirms CFWENO smallest errors |

**Readiness judgment — scalar nonlinear**: **READY** (13/13 formulas self-contained, 0 external blockers)

### Overall Readiness Verdict

| Subset | Formula coverage | External blockers | Readiness |
|--------|-----------------|-------------------|-----------|
| scalar_linear | 7/7 (100%) | 0 | **READY — can implement immediately** |
| scalar_nonlinear | 13/13 (100%) | 0 | **READY — can implement immediately** |
| Euler_1D | ~85% | 2 (eigenvalue iteration, p_m) | NOT READY |
| 2D Euler | ~85% | 2 (same as Euler_1D) | NOT READY |

### Phase 2 Classification Error

Phase 2 (commit 2272a61) stated: "2 critical blockers (refs [6,7] for WENO weights)" affecting all subsets. This was incorrect because:

1. Eq. (17) provides the full WENO nonlinear weight formula: ω̄_k^r = γ̄_k^r / Σγ̄_l^r where γ̄_k^r = ᾱ_k^r/(β̄_k^r + ε)²
2. Tables I-II provide explicit numerical values for optimal linear weights for all orders (r=2,3,4)
3. Eq. (19) provides explicit smoothness indicator formulas
4. Table III provides discontinuity positions

The paper does cite refs [6,7] for the FWENO reconstruction framework, but reproduces all essential formulas needed for implementation. References [6,7] provide derivation context and FWENO historical background, not missing implementation formulas.
