# CFWENO Dependency Paper Register

**Paper**: CFWENO (Zhou-Dong-Pan 2025, Phys. Fluids 37, 106131)
**Register date**: 2026-05-19
**Purpose**: Catalog all referenced papers needed for CFWENO implementation, with extraction status

---

## Critical Dependencies (Blocking Implementation)

These references contain formulas or algorithms NOT fully specified in the CFWENO paper itself.

| Ref # | Short ID | Authors / Title | Year | Journal / Source | Relevance | Status | Blocking? |
|-------|----------|-----------------|------|------------------|-----------|--------|-----------|
| [6] | FWENO-1 | FWENO scheme (first reference) — exact WENO nonlinear weight formulas | — | — | WENO weight computation for 3rd/5th/7th order reconstruction | Not obtained | **YES** |
| [7] | FWENO-2 | FWENO scheme (second reference) — exact WENO nonlinear weight formulas | — | — | WENO weight computation (alternative or extended) | Not obtained | **YES** |

### What is missing without [6,7]
- Exact nonlinear weight formulas (alpha_k, beta_k, d_k for each WENO order)
- These are fundamental — the CFWENO stencil structure is known (Eq. 30) but the WENO reconstruction weights that determine accuracy and non-oscillatory properties are from these references
- The paper states: "we use the WENO reconstruction from [6,7]" without reproducing the weight formulas

---

## Algorithmic Dependencies (Partial Information in Paper)

These references are cited for specific algorithmic components. The paper provides some detail but the references may contain more.

| Ref # | Short ID | Cited for | Paper coverage | Status |
|-------|----------|-----------|----------------|--------|
| — | Eigenvalue iteration | Iterative improvement of characteristic speed `a` | Mentioned but convergence criteria, starting guess, iteration count not specified | Unresolved — may be in FWENO refs [6,7] or earlier SFM papers |
| — | CFL stability | CFL <= 1 claim | Stated without rigorous proof | Needs empirical verification during implementation |

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
| WENO family | Reconstruction framework | Weight formulas from [6,7] are critical (see above) |
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
| 1 | Obtain FWENO refs [6,7] — extract WENO weight formulas | v1.1 (gap resolution) |
| 2 | Extract full bibliography from PDF pages | v1.1 |
| 3 | Resolve eigenvalue iteration details (may be in [6,7]) | v1.1 |
| 4 | Verify Eq. 23 p_m formula against paper | v1.1 |
| 5 | Empirically verify CFL stability limit | v1.2 (after scalar implementation) |

---

## Summary

- **Total references cited**: ~54+ (exact count pending bibliography extraction)
- **Critical blocking dependencies**: 2 (refs [6,7] — WENO weight formulas)
- **Partially specified components**: 2 (eigenvalue iteration, CFL limit)
- **Test case references**: 5+ (non-blocking)
- **Self-contained components**: Characteristic decomposition (Eq. 21-22), Hermite interpolation (Eq. 28-29), CFWENO stencil (Eq. 30), Algorithm 1 flux reconstruction, update formula (Eq. 25), multi-dimensional extension (Eq. 33)
