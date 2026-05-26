# Task Traceability: Scalar CFWENO5 Readiness Review

## Task Information
- **Task ID**: cfweno5_scalar_readiness
- **Task type**: post-v1.0 readiness review
- **Based on v1.0 tag**: 42d97ee
- **Previous diagnostic**: Burgers order recovery commit 4d671c0
- **Date**: 2026-05-26
- **Status**: complete (strict formula confidence gate passes, ready for human approval)

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
**READY FOR HUMAN APPROVAL** — All 11 required formulas at high confidence.
A2 reclassified as optional derivation reference. Strict confidence gate passes.

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
1. Appendix A Eq. (A2) — reclassified as optional; derivable from verified A1

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
| docs/formula_inventories/cfweno5_scalar_formulas.yml | A2 reclassified optional; 3 formulas promoted high/verified |
| docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_confidence_report.md | Regenerated |
| docs/scheme_specs/cfweno5_scalar_subset.md | Updated readiness, formula gate, blocking status |
| docs/feasibility/cfweno5_scalar_readiness.md | Updated decision, A2 derivation policy |
| docs/tasks/cfweno5_scalar_readiness/traceability.md | This update |
| docs/roadmaps/v1_real_paper_demo.md | Updated CFWENO5 readiness status |
| docs/tasks/cfweno5_formula_verification/verification_packet.md | Verification results |
| docs/tasks/cfweno5_formula_verification/a2_derivation_policy.md | A2 derivation policy decision |
| tools/check_formula_confidence.py | Added 'derived' verification status |
| tests/test_formula_confidence.py | Updated for A2 policy, added 2 new tests |

## Code Changes
None — this is a tooling/documentation-only task. solver/schemes.py NOT modified.

## Formula Confidence Workflow Update (this commit)
- Formula inventory: `docs/formula_inventories/cfweno5_scalar_formulas.yml`
- Confidence checker: `tools/check_formula_confidence.py` (supports 'derived' status)
- Confidence report: `docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_confidence_report.md`
- 11 high / 1 medium (optional) / 0 low formulas
- 0 blocking formulas
- A2 derivation policy: `docs/tasks/cfweno5_formula_verification/a2_derivation_policy.md`
- Strict check: PASSES
- Tests: `tests/test_formula_confidence.py` (11 tests including derived + optional)

## Tests Run
- `make compile` — pass
- `make test` — TBC
- `make health` — TBC
- `make formula-confidence-cfweno5` — expected pass
- `make formula-confidence-cfweno5-strict` — passes (0 blocking formulas)
- `make formula-confidence-report-cfweno5` — expected generate report

## Approval Status
- `docs/scheme_specs/cfweno5_scalar_subset.md`: **Approved for implementation: no**
- This spec will remain unapproved until formula-confidence-cfweno5-strict passes.

## Recommended Next Action
1. Human reviews and approves the CFWENO5 spec (`docs/scheme_specs/cfweno5_scalar_subset.md`)
2. Set `Approved for implementation: yes` after human review
3. Run `tools/run_in_project_env.sh python tools/check_scheme_spec_approval.py docs/scheme_specs/cfweno5_scalar_subset.md`
4. Implement CFWENO5 scalar linear advection using approved spec

## Whether Production Solver Changed
No — solver/schemes.py was NOT modified.

## Whether v1.0 Tag Changed
No — v1.0 still points to 42d97ee.

## Commit
- **Hash**: pending (this task)
- **Previous hash**: 326f7b2 (human verification integration)
- **Branch**: master
- **Push**: pending
