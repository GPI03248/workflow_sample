# Task Traceability Manifest: CFWENO Burgers Readiness (v1.2 prep)

## Task Information
- **Task ID**: cfweno_burgers_readiness
- **Task type**: nonlinear-scalar-readiness (spec + readiness review, no code)
- **Date**: 2026-05-20
- **Status**: complete (documentation only, implementation not started)

## Source Paper
- **Paper**: .local/papers/cfweno_pof_2025.pdf (NOT in git)
- **Citation**: Zhou-Dong-Pan (2025), Physics of Fluids 37, 106131, DOI: 10.1063/5.0291087

## Relation to v1.1
- v1.1 implemented scalar **linear** CFWENO3 prototype (commit: 2b580ef, hardening: bb18e68)
- v1.2 readiness extends to scalar **nonlinear** Burgers CFWENO3
- v1.2 reuses v1.1 CFWENO3 stencil, interface reconstruction, periodic BCs
- v1.2 adds: variable wave speed, flux linearization, residual flux correction

## Created Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Burgers subset spec | `docs/scheme_specs/cfweno_scalar_burgers_subset.md` | Created, Approved: **no** |
| Readiness review | `docs/feasibility/cfweno_scalar_burgers_readiness.md` | Created, Decision: conditionally ready |
| Burgers readiness traceability | `docs/tasks/cfweno_burgers_readiness/traceability.md` | This file |

## Updated Artifacts

| Artifact | Path | Change |
|----------|------|--------|
| Roadmap | `docs/roadmaps/v1_real_paper_demo.md` | Added v1.2 Burgers section; renumbered v1.3-v1.5 |
| Scalar prototype traceability | `docs/tasks/cfweno_scalar_prototype/traceability.md` | Added v1.2 readiness reference |

## Approval Status
- **cfweno_scalar_burgers_subset.md**: `Approved for implementation: no`
- **cfweno_scalar_subset.md** (v1.1 linear): remains `yes`
- **cfweno_pof_2025.md** (full): remains `no`

## Implementation Status
- **Not started**
- Awaiting human review of spec and readiness review
- Open decisions: predictor strategy, reference solution strategy

## Code Changes
- **None** — this task is documentation only
- `solver/schemes.py` was NOT modified
- `cfd/` was NOT modified
- No tests were added or modified

## Tests Run
- No new tests (documentation-only task)
- Existing tests remain passing (218 total, verified by health check)

## Remaining Risks
1. Variable wave speed may affect CFL stability — needs empirical verification during v1.2
2. Flux linearization accuracy for Burgers untested — first implementation will reveal
3. Convergence order may be < 3 for nonlinear Burgers — predictor iteration may be needed
4. Post-shock behaviour unknown — not in Phase 1 scope
5. No external blockers — all formulas self-contained in paper

## Recommended Next Action
1. Human reviews `docs/scheme_specs/cfweno_scalar_burgers_subset.md`
2. Human selects predictor strategy (zero or one iteration)
3. Human selects reference solution strategy (fine-grid baseline or analytic implicit)
4. Human sets `Approved for implementation: yes` in the Burgers spec
5. Implementation proceeds with `implement-paper-scheme` skill
