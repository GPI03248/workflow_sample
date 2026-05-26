# Task Traceability: Scalar CFWENO5 Readiness Review

## Task Information
- **Task ID**: cfweno5_scalar_readiness
- **Task type**: post-v1.0 readiness review
- **Based on v1.0 tag**: 42d97ee
- **Previous diagnostic**: Burgers order recovery commit 4d671c0
- **Date**: 2026-05-26
- **Status**: complete (readiness review only, implementation blocked)

## Purpose
Determine whether scalar CFWENO5 linear advection is a viable next implementation
target after the Burgers order recovery diagnostic concluded that CFWENO3 Burgers
~2nd order is structural.

## Created Files
| File | Purpose |
|------|---------|
| docs/tasks/cfweno5_scalar_readiness/diagnostic_plan.md | Readiness questions and status |
| docs/scheme_specs/cfweno5_scalar_subset.md | CFWENO5 subset spec (NOT approved) |
| docs/feasibility/cfweno5_scalar_readiness.md | Feasibility review — decision: BLOCKED |
| docs/tasks/cfweno5_scalar_readiness/traceability.md | This manifest |
| docs/roadmaps/v1_real_paper_demo.md | Updated with CFWENO5 readiness section |

## Readiness Decision
**CONDITIONALLY READY** — formulas extracted, pending human verification of 3 items.

Extraction report: `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md`

### What changed
- All CFWENO5 formulas located and extracted from the paper
- Appendix A (Eqs. A1-A2): substencil expressions extracted (medium confidence)
- Table I r=3 weights: extracted (high confidence, k=2 uncertain)
- Table II r=3 weights: extracted (low confidence, needs full verification)
- Eq. (19) smoothness indicators b_30-b_33: extracted (medium confidence)
- Interface reconstruction: confirmed same as CFWENO3

### Remaining human verification items
1. Table I, r=3, k=2 weight value (page 5)
2. Table II, r=3, all 4 weight values (page 6)
3. Appendix A, Eqs. (A1)-(A2) substencil coefficients (page 23)

## Code Changes
None — this is a documentation-only readiness review.

## Tests Run
- `make compile` — pass (no code changed)
- `make test` — 254 passed (no new tests, no regressions)
- `make health` — 5 OK

## Approval Status
- `docs/scheme_specs/cfweno5_scalar_subset.md`: **Approved for implementation: no**
- This spec will remain unapproved until all formula blockers are resolved.

## Recommended Next Action
1. Re-read the paper at pages containing CFWENO5 stencil, Tables I-II (r=3), Appendix A
2. Use `extract-paper-scheme` skill to update the extraction report
3. Update the CFWENO5 spec with transcribed formulas
4. Run `make check-spec SPEC=docs/scheme_specs/cfweno5_scalar_subset.md`
5. If formulas verify: change approval to yes and proceed to implementation

## Whether Production Solver Changed
No — solver/schemes.py was NOT modified.

## Whether v1.0 Tag Changed
No — v1.0 still points to 42d97ee.

## Commit
- **Hash**: pending
- **Branch**: master
- **Push**: pending
