# Task Traceability Manifest: CFWENO Scalar Readiness Audit (Phase 2.5)

## Task Information
- **Task ID**: cfweno_scalar_readiness_audit
- **Task type**: readiness-audit (Phase 2.5 correction of Phase 2 dependency classification)
- **Date**: 2026-05-19
- **Status**: complete

## Parent Task
- **Task ID**: cfweno_dependency_resolution (Phase 2)
- **Traceability**: `docs/tasks/cfweno_dependency_resolution/traceability.md`
- **Root task**: cfweno_real_paper_intake (Phase 1)
- **Traceability**: `docs/tasks/cfweno_real_paper_intake/traceability.md`

## Source
- **Paper**: .local/papers/cfweno_pof_2025.pdf (NOT in git, .local/ in .gitignore)
- **Paper citation**: Physics of Fluids 37, 106131 (2025), DOI: 10.1063/5.0291087
- **Authors**: Tong Zhou, Haitao Dong, Shucheng Pan

## Goal

Audit Phase 2's dependency classification which incorrectly stated that references [6,7] were CRITICAL blockers for ALL CFWENO implementation subsets. Verify that the paper self-contains sufficient formulas for scalar linear and nonlinear CFWENO3.

## Key Finding

**Scalar linear CFWENO3 has ZERO external paper blockers.** Scalar nonlinear CFWENO3 also has ZERO external blockers. The paper self-contains:

- Eq. (17): WENO nonlinear weight formulas
- Tables I-II: Optimal linear weights with explicit numerical values
- Eq. (19): Smoothness indicators
- Table III: Discontinuity positions
- Eq. (27-30): Complete CFWENO3 stencil definition

Phase 2's classification of refs [6,7] as "CRITICAL blocking for ALL subsets" was incorrect.

## Artifacts Updated

### 1. Dependency Register
- **Path**: `docs/papers/cfweno_dependency_register.md`
- **Change**: Added per-subset classification table; reclassified refs [6,7] from CRITICAL (all subsets) to NOT blocking (scalar); corrected "What is missing without [6,7]" section; updated resolution plan to show v1.1 can proceed immediately
- **Status**: Complete

### 2. Feasibility Assessment
- **Path**: `docs/feasibility/cfweno_pof_2025_feasibility.md`
- **Change**: Added Section 9 "Phase 2.5 Readiness Audit" with per-subset formula coverage tables and readiness judgments; corrected risk table for WENO weights; updated recommended path to show scalar unblocked; updated subset decomposition table
- **Status**: Complete

### 3. Scalar Subset Spec
- **Path**: `docs/scheme_specs/cfweno_scalar_subset.md`
- **Change**: Added "Phase 1 Target: Linear Advection CFWENO3 Prototype" section; updated blocking dependencies table with per-subset classification and Phase 2.5 correction note; corrected WENO weight references from "BLOCKED" to "self-contained"; updated known limitations
- **Status**: Complete

### 4. Full Scheme Spec
- **Path**: `docs/scheme_specs/cfweno_pof_2025.md`
- **Change**: Updated implementation subsets table to show scalar has "NONE (self-contained: Eq. 17, Tables I-II, Eq. 19)" instead of "WENO weights [6,7] only"
- **Status**: Complete

### 5. Roadmap
- **Path**: `docs/roadmaps/v1_real_paper_demo.md`
- **Change**: Updated current state description with Phase 2.5 correction; updated implementation subsets table; restructured v1.1 as "Scalar CFWENO3 Prototype" (was "Gap Resolution"); moved gap resolution to v1.2; updated success metrics and comparison table
- **Status**: Complete

### 6. Phase 2 Traceability
- **Path**: `docs/tasks/cfweno_dependency_resolution/traceability.md`
- **Change**: Added Phase 2.5 update section (below)
- **Status**: Complete

### 7. Phase 1 Traceability
- **Path**: `docs/tasks/cfweno_real_paper_intake/traceability.md`
- **Change**: Added Phase 2.5 update section (below)
- **Status**: Complete

### 8. This Traceability Manifest
- **Path**: `docs/tasks/cfweno_scalar_readiness_audit/traceability.md`
- **Status**: Complete

## Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| Phase 2 WENO classification was incorrect | Paper self-contains Eq. 17, Tables I-II, Eq. 19 — PDF audit confirmed | 2026-05-19 |
| Scalar linear CFWENO3 has ZERO external blockers | Eq. 27-30 fully self-contained; flux derivable as f_hat = a * u_bar | 2026-05-19 |
| Scalar nonlinear CFWENO3 has ZERO external blockers | Eq. 17 provides WENO weights; Tables I-II provide linear weights; Eq. 19 provides smoothness indicators | 2026-05-19 |
| v1.1 target changed to scalar CFWENO3 prototype | No external blockers; simplest non-trivial implementation; ~150-250 LOC | 2026-05-19 |
| Refs [6,7] demoted to "useful for context" | All essential formulas reproduced in paper; refs provide FWENO derivation background | 2026-05-19 |
| Approved for implementation remains "no" | Phase 2.5 is documentation-only; no code changes; approval to be changed during v1.1 implementation | 2026-05-19 |

## Workflow Compliance

| Step | Requirement | Status |
|------|-------------|--------|
| PDF formula audit | Verify all formulas self-contained for scalar | Done (pages 6-11 analyzed) |
| Per-subset classification | Distinguish scalar_linear, scalar_nonlinear, Euler_1D, 2D | Done |
| Dependency register correction | Reclassify refs [6,7] | Done |
| Feasibility update | Add readiness audit section | Done |
| Spec update | Scalar subset spec reflects new findings | Done |
| Roadmap update | v1.1 = scalar prototype | Done |
| Traceability | This document + parent updates | Done |
| No code changes | Only docs/ modifications | Done |
| Approval gate unchanged | Approved: no maintained | Done |

## No Code Changes

This task produced **no modifications** to `cfd/`, `solver/`, `tests/`, or any executable code. All artifacts are documentation only.

## Outstanding Items for v1.1

| Item | Action needed | Priority |
|------|--------------|----------|
| Implement scalar linear CFWENO3 | Code implementation from Eq. 27-30 | Critical |
| Implement WENO weights from Eq. 17, Tables I-II, Eq. 19 | Code implementation for nonlinear case | High |
| Verify 3rd-order convergence | Linear advection convergence test | High |
| Empirically verify CFL <= 1 | Stability testing during implementation | Medium |
| Burgers shock test | Non-oscillatory shock capturing | Medium |

## Commit

- **Commit**: (to be created)
- **Branch**: master
