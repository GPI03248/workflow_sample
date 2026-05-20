# CFWENO Dependency Paper Register

**Paper**: CFWENO (Zhou-Dong-Pan 2025, Phys. Fluids 37, 106131)
**Register date**: 2026-05-19
**Last audited**: 2026-05-19 (Phase 2.5 readiness audit)
**Purpose**: Catalog all referenced papers needed for CFWENO implementation, with extraction status

---

## Per-Subset Dependency Classification (Phase 2.5 Correction)

Phase 2 originally classified refs [6,7] as "CRITICAL blocking for ALL subsets." Phase 2.5 audit of the paper's formula coverage reveals this was incorrect: the paper self-contains Eq. (17) for WENO nonlinear weight formulas, Tables I-II for optimal linear weights, and Eq. (19) for smoothness indicators.

| Subset | Scope | External blockers | Can proceed? |
|--------|-------|-------------------|--------------|
| **scalar_linear** | 1D linear advection (constant a), CFWENO3 stencil | **NONE** — Eq. 27-30 fully self-contained; flux derivable as f_hat = a * u_bar_{i+1/2} | **YES** |
| **scalar_nonlinear** | 1D Burgers, nonlinear WENO weighting | **NONE** — Eq. 17 provides WENO weights; Tables I-II provide linear weights; Eq. 19 provides smoothness indicators | **YES** |
| **Euler_1D** | Characteristic decomposition, Algorithm 1, p_m | Eigenvalue iteration details (convergence criteria, start guess); Eq. 23 p_m verification | NO (2 unresolved) |
| **2D Euler** | Dimensional composition | Same as Euler_1D + none additional | NO (same as Euler_1D) |

### Key Correction

References [6,7] are **NOT blockers** for scalar subsets (linear or nonlinear). The paper self-contains:

| Component | Paper source | Subset applicability |
|-----------|-------------|---------------------|
| WENO nonlinear weights ω̄_k^r, ω_k^r | Eq. (17): γ̄_k^r = ᾱ_k^r/(β̄_k^r + ε)², γ_k^r = α_k^r/(β_k^r + ε)² | scalar_nonlinear, Euler_1D |
| Optimal linear weights γ̄_k^r | Table I: explicit values for r=2,3,4 and k=0,...,r | All subsets |
| Optimal linear weights γ_k^r | Table II: explicit values for next-time-level reconstruction | All subsets |
| Discontinuity positions δ_r^k | Table III | scalar_nonlinear |
| Smoothness indicators β_k^r | Eq. (19): explicit formulas | scalar_nonlinear |
| CFWENO3 stencil ū_{i+1/2} | Eq. (30): explicit formula with ν | All subsets |
| CFWENO3 stencil ū_{i+1/2}^{n+1} | Eq. (30): explicit formula for next time level | All subsets |

---

## External References (Previously Classified as Critical)

| Ref # | Short ID | Authors / Title | Year | Journal / Source | Relevance | Status | Blocking? |
|-------|----------|-----------------|------|------------------|-----------|--------|-----------|
| [6] | FWENO-1 | FWENO scheme (first reference) | — | — | FWENO reconstruction framework context | Not obtained | **NO** (not needed for scalar) |
| [7] | FWENO-2 | FWENO scheme (second reference) | — | — | FWENO reconstruction framework context | Not obtained | **NO** (not needed for scalar) |

### Role of [6,7] (Corrected)
- The paper states "we use the WENO reconstruction from [6,7]" but then **reproduces** the essential formulas in Eq. (17), Tables I-II, and Eq. (19)
- References [6,7] provide the FWENO theoretical foundation and derivation context, which is useful for understanding but not required for implementation
- For higher-order variants (CFWENO5/7), the weight formulas in Tables I-II extend naturally — refs [6,7] may provide additional implementation details for 5th/7th order
- **Remaining value of [6,7]**: Eigenvalue iteration convergence criteria (may be documented there), FWENO derivation context, validation against FWENO benchmarks

---

## Algorithmic Dependencies (Partial Information in Paper)

These references are cited for specific algorithmic components. The paper provides some detail but the references may contain more.

| Ref # | Short ID | Cited for | Paper coverage | Status |
|-------|----------|-----------|----------------|--------|
| — | Eigenvalue iteration | Iterative improvement of characteristic speed `a` | Mentioned but convergence criteria, starting guess, iteration count not specified | Unresolved — Euler_1D blocker only; may be in FWENO refs [6,7] or earlier SFM papers |
| — | CFL stability | CFL <= 1 claim | Stated without rigorous proof | Needs empirical verification during implementation (non-blocking) |

---

## Test Case References

These references define validation test cases. They are useful for reproducing results but not blocking for implementation.

| Ref # | Cited as | Description | Used in paper section |
|-------|----------|-------------|----------------------|
| [34] | Ref. 34 | Density perturbation advection (efficiency test) | Sec. III.A.3, III.B.4 |
| [40] | Shu-Osher | Shock-density interaction problem | Sec. III.B.2 |
| [41] | Titarev-Toro | High-frequency test | Sec. III.B.3 |
| [53] | Liska-Wendroff 2003 | 2D implosion problem | Sec. III.C.2 |
| [54] | Ref. 54 | 2D Riemann problem (planar shock interaction) | Sec. III.C.1 |

---

## Foundational Method References

References cited for the theoretical foundation. These provide context but the paper summarizes the key ideas.

| Ref # | Category | Relevance to implementation |
|-------|----------|----------------------------|
| SFM (Solution Formula Method) | Theoretical foundation | HJ equation quasi-exact solution — fully described in Sec. II.A |
| SLM (Semi-Lagrangian Method) | Contrast with SFM | Not needed for implementation |
| WENO family | Reconstruction framework | Weight formulas ARE in paper (Eq. 17, Tables I-II, Eq. 19); refs [6,7] provide derivation context |
| Roe averages | Characteristic decomposition | Eq. 22 provides the formulas — self-contained |

---

## Bibliography Extraction Status

| Item | Status |
|------|--------|
| References section pages | NOT fully extracted from PDF |
| Total reference count | Unknown (at least [1]-[54] based on in-text citations) |
| Full author/title/journal for each ref | Not yet available |
| DOI for dependency refs [6,7] | Not yet available |

### Note
The PDF references section (likely on the final pages) was not successfully extracted by image analysis. The bibliography should be re-extracted in a future session by manually reading the PDF or using improved OCR tools. This is a non-blocking documentation gap — the critical dependency information (refs [6,7] for WENO weights) is known from in-text citations.

---

## Resolution Plan

| Priority | Action | Target version |
|----------|--------|----------------|
| 1 | Implement scalar linear CFWENO3 prototype (NO external blockers) | v1.1 |
| 2 | Implement scalar nonlinear CFWENO3 (Burgers — NO external blockers) | v1.1 |
| 3 | Obtain FWENO refs [6,7] — useful for understanding, not blocking | v1.3 (Euler prep) |
| 4 | Extract full bibliography from PDF pages | v1.3 |
| 5 | Resolve eigenvalue iteration details (may be in [6,7]) | v1.3 |
| 6 | Verify Eq. 23 p_m formula against paper | v1.3 |
| 7 | Empirically verify CFL stability limit | v1.1 (during scalar implementation) |

---

## Summary

- **Total references cited**: ~54+ (exact count pending bibliography extraction)
- **Critical blocking dependencies**: 0 for scalar_linear; 0 for scalar_nonlinear; 2 for Euler_1D (eigenvalue iteration, Eq. 23 p_m)
- **Previously misclassified**: refs [6,7] were listed as CRITICAL for ALL subsets; Phase 2.5 audit confirms paper self-contains all WENO formulas (Eq. 17, Tables I-II, Eq. 19)
- **Partially specified components**: 2 (eigenvalue iteration — Euler_1D only; CFL limit — non-blocking, empirically verified)
- **Test case references**: 5+ (non-blocking)
- **Self-contained components**: WENO weights (Eq. 17), optimal linear weights (Tables I-II), smoothness indicators (Eq. 19), CFWENO3 stencil (Eq. 30), Hermite interpolation (Eq. 28-29), characteristic decomposition (Eq. 21-22), Algorithm 1 flux reconstruction, update formula (Eq. 25), multi-dimensional extension (Eq. 33)
