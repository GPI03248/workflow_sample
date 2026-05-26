# Task Traceability: Scalar CFWENO5 Readiness Review

## Task Information
- **Task ID**: cfweno5_scalar_readiness
- **Task type**: post-v1.0 readiness review
- **Based on v1.0 tag**: 42d97ee
- **Previous diagnostic**: Burgers order recovery commit 4d671c0
- **Date**: 2026-05-26
- **Status**: complete (human verification integrated, implementation still blocked)

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
**CONDITIONALLY READY** — Table I and Table II human-verified; Appendix A visually
confirmed but transcription not independently verified.

Extraction report: `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md`

### What changed (formula extraction, commit cb6b64a)
- All CFWENO5 formulas located and extracted from the paper
- Appendix A (Eqs. A1-A2): substencil expressions extracted (medium confidence)
- Table I r=3 weights: extracted (high confidence, k=2 uncertain)
- Table II r=3 weights: extracted (low confidence, needs full verification)
- Eq. (19) smoothness indicators b_30-b_33: extracted (medium confidence)
- Interface reconstruction: confirmed same as CFWENO3

### What changed (human verification, this commit)
- Table I k=2 **corrected** to `(1-nu)(2-nu)/6` (was `(1-nu)(2+nu)/6`)
- Table I k=3 confirmed as not applicable (ellipsis) — 3 valid entries only
- Table II fully human-verified — 3 valid entries with correct formulas
- Table II k=3 confirmed as not applicable (ellipsis)
- Appendix A visually confirmed present and readable — transcription NOT independently verified
- Smoothness indicators (Eq. 19) not part of this verification round

### Remaining uncertainties
1. Appendix A, Eqs. (A1)-(A2) substencil transcription — character-level check needed
2. Eq. (19) smoothness indicators b_30-b_33 — not independently verified

## Human Verification Record
- **Date**: 2026-05-26
- **Verifier**: Human (rendered PDF page images)
- **Items verified**:
  1. Table I, r=3, k=2 — corrected, confidence HIGH
  2. Table I, r=3 structure — 3 entries, k=3 = N/A, confidence HIGH
  3. Table II, r=3, all entries — verified, confidence HIGH
  4. Table II, r=3 structure — 3 entries, k=3 = N/A, confidence HIGH
  5. Appendix A presence — visually confirmed, confidence MEDIUM

## Updated Files (this task)
| File | Change |
|------|--------|
| docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md | Added human verification section |
| docs/scheme_specs/cfweno5_scalar_subset.md | Corrected Table I/II, updated readiness status |
| docs/feasibility/cfweno5_scalar_readiness.md | Added human verification update, updated decision |
| docs/tasks/cfweno5_scalar_readiness/traceability.md | This update |
| docs/roadmaps/v1_real_paper_demo.md | Updated CFWENO5 readiness status |

## Code Changes
None — this is a documentation-only readiness review.

## Tests Run
- `make compile` — pass (no code changed)
- `make test` — 254 passed (no new tests, no regressions)
- `make health` — 5 OK

## Approval Status
- `docs/scheme_specs/cfweno5_scalar_subset.md`: **Approved for implementation: no**
- This spec will remain unapproved until Appendix A transcription is verified.

## Recommended Next Action
1. Character-level transcription of Appendix A Eqs. (A1)-(A2) from rendered PDF
2. If transcription matches existing extraction: change approval to yes
3. If transcription differs: update extraction report and spec, then re-evaluate
4. Alternatively: approve spec with implementation-time verification as first step

## Whether Production Solver Changed
No — solver/schemes.py was NOT modified.

## Whether v1.0 Tag Changed
No — v1.0 still points to 42d97ee.

## Commit
- **Hash**: pending (this task)
- **Previous hash**: cb6b64a (formula extraction)
- **Branch**: master
- **Push**: pending
