# Task Traceability Manifest: CFWENO Dependency Resolution

## Task Information
- **Task ID**: cfweno_dependency_resolution
- **Task type**: dependency-analysis (Phase 2 of real-paper demo)
- **Date**: 2026-05-19
- **Status**: complete

## Parent Task
- **Task ID**: cfweno_real_paper_intake
- **Traceability**: `docs/tasks/cfweno_real_paper_intake/traceability.md`

## Source
- **Paper**: .local/papers/cfweno_pof_2025.pdf (NOT in git, .local/ in .gitignore)
- **Paper path**: Physics of Fluids 37, 106131 (2025), DOI: 10.1063/5.0291087
- **Authors**: Tong Zhou, Haitao Dong, Shucheng Pan

## Goal

Resolve CFWENO extraction gaps from the Phase 1 intake and identify which gaps can be isolated by implementation subset (scalar vs Euler vs 2D).

## Artifacts Produced

### 1. Dependency Register
- **Path**: `docs/papers/cfweno_dependency_register.md`
- **Purpose**: Catalog all referenced papers needed for implementation, with extraction status and blocking priority
- **Key finding**: 2 critical blockers (refs [6,7] for WENO weights), 2 Euler-specific blockers, 5+ test case refs
- **Status**: Complete

### 2. Scalar Subset Scheme Spec
- **Path**: `docs/scheme_specs/cfweno_scalar_subset.md`
- **Purpose**: Implementation-ready spec for the scalar 1D subset only (linear advection + Burgers)
- **Scope**: Eq. 27-30, 32, 25 only; no Euler, no characteristic decomposition, no Algorithm 1
- **Blocking dep**: WENO weights [6,7] only (1 blocker vs 4 in full spec)
- **Status**: Complete (implementation still blocked by WENO weights)

## Artifacts Updated

### 3. Extraction Report
- **Path**: `docs/paper_reviews/cfweno_pof_2025/extraction_report.md`
- **Change**: Added Sec. 3.2 with Eq. 23 p_m transcription (marked UNCERTAIN); updated unresolved items with blocking status classification
- **Status**: Complete

### 4. Feasibility Assessment
- **Path**: `docs/feasibility/cfweno_pof_2025_feasibility.md`
- **Change**: Added subset decomposition table (scalar/Euler/2D) with independent LOC estimates and blockers; updated recommendation to note scalar can proceed independently
- **Status**: Complete

### 5. Scheme Spec
- **Path**: `docs/scheme_specs/cfweno_pof_2025.md`
- **Change**: Added implementation subsets table linking to scalar subset spec
- **Status**: Complete

### 6. Roadmap
- **Path**: `docs/roadmaps/v1_real_paper_demo.md`
- **Change**: Added implementation subsets table with target phases
- **Status**: Complete

## Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| Eq. 23 transcription marked UNCERTAIN | Image-based PDF quality insufficient; parentheses placement and denominator structure may have errors | 2026-05-19 |
| Scalar subset identified as independently implementable | Only 1 blocking dep (WENO weights); ~150-250 LOC; all formulas self-contained in paper except weights | 2026-05-19 |
| Bibliography extraction deferred | PDF reference pages (pages 23-25) not successfully extracted by image analysis; full reference details not critical for gap identification | 2026-05-19 |
| Implementation remains deferred (Approved: no) | WENO weight dependency [6,7] still unresolved for all subsets | 2026-05-19 |

## Workflow Compliance

| Step | Requirement | Status |
|------|-------------|--------|
| Dependency identification | Catalog all external references | Done (2 critical, 2 Euler-specific) |
| Eq. 23 transcription | Transcribe with uncertainty marking | Done (UNCERTAIN flag) |
| Subset decomposition | Separate scalar/Euler/2D blockers | Done |
| Implementation-ready spec | Scalar subset spec with all sections | Done |
| Traceability | This document + parent update | Done |
| No code changes | Only docs/ modifications | Done |
| Approval gate unchanged | Approved: no maintained | Done |

## No Code Changes

This task produced **no modifications** to `cfd/`, `solver/`, `tests/`, or any executable code. All artifacts are documentation only.

## Outstanding Items for v1.1

| Item | Action needed | Priority |
|------|--------------|----------|
| WENO weight formulas | Obtain and extract refs [6,7] | Critical |
| Bibliography extraction | Re-attempt PDF reference pages | Medium |
| Eq. 23 verification | Human read against paper | Medium |
| Eigenvalue iteration | Check refs [6,7] for convergence criteria | Medium |
