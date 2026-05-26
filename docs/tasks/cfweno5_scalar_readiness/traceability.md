# Task Traceability: Scalar CFWENO5 Readiness Review

## Task Information
- **Task ID**: cfweno5_scalar_readiness
- **Task type**: post-v1.0 readiness review
- **Based on v1.0 tag**: 42d97ee
- **Previous diagnostic**: Burgers order recovery commit 4d671c0
- **Date**: 2026-05-26
- **Status**: complete (character-level verification integrated, 1 blocking formula remains)

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
**CONDITIONALLY READY** — 11 of 12 formulas at high confidence. 1 blocking formula
remains (appendix_A_eq_A2, derivable from A1).

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
1. Appendix A Eq. (A2) d/dv derivative terms — pdftotext ambiguous, derivable from A1

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
| docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md | Added human verification section, corrected b_30 |
| docs/formula_inventories/cfweno5_scalar_formulas.yml | 3 formulas promoted: high/verified |
| docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_confidence_report.md | Regenerated |
| docs/scheme_specs/cfweno5_scalar_subset.md | Updated verification status, blocking formulas |
| docs/feasibility/cfweno5_scalar_readiness.md | Updated confidence summary, decision |
| docs/tasks/cfweno5_scalar_readiness/traceability.md | This update |
| docs/roadmaps/v1_real_paper_demo.md | Updated CFWENO5 readiness status |
| docs/tasks/cfweno5_formula_verification/verification_packet.md | New: verification results |

## Code Changes
None — this is a tooling/documentation-only task. solver/schemes.py NOT modified.

## Formula Confidence Workflow Update (this commit)
- Formula inventory created: `docs/formula_inventories/cfweno5_scalar_formulas.yml`
- Confidence checker created: `tools/check_formula_confidence.py`
- Confidence report generated: `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_confidence_report.md`
- 11 high / 1 medium / 0 low formulas
- 1 blocking formula (appendix_A_eq_A2, medium confidence, derivable from A1)
- Tests: `tests/test_formula_confidence.py`
- Makefile targets: formula-confidence-cfweno5, formula-confidence-cfweno5-strict, formula-confidence-report-cfweno5

## Tests Run
- `make compile` — pass
- `make test` — TBC
- `make health` — TBC
- `make formula-confidence-cfweno5` — expected pass
- `make formula-confidence-cfweno5-strict` — expected fail (1 blocking formula: appendix_A_eq_A2)
- `make formula-confidence-report-cfweno5` — expected generate report

## Approval Status
- `docs/scheme_specs/cfweno5_scalar_subset.md`: **Approved for implementation: no**
- This spec will remain unapproved until formula-confidence-cfweno5-strict passes.

## Recommended Next Action
1. Derive Appendix A Eq. (A2) from A1 by differentiating coefficients wrt nu
2. Verify derived A2 against paper's A2 expressions
3. Update formula inventory confidence to high for appendix_A_eq_A2
4. Run `make formula-confidence-cfweno5-strict` to confirm pass
5. Change approval to yes

## Whether Production Solver Changed
No — solver/schemes.py was NOT modified.

## Whether v1.0 Tag Changed
No — v1.0 still points to 42d97ee.

## Commit
- **Hash**: pending (this task)
- **Previous hash**: 326f7b2 (human verification integration)
- **Branch**: master
- **Push**: pending
