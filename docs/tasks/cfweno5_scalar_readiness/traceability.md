# Task Traceability: Scalar CFWENO5 Readiness Review

## Task Information
- **Task ID**: cfweno5_scalar_readiness
- **Task type**: post-v1.0 readiness review
- **Based on v1.0 tag**: 42d97ee
- **Previous diagnostic**: Burgers order recovery commit 4d671c0
- **Date**: 2026-05-27 (updated after v1.3-pre.9 weight role audit)
- **Status**: formula gate hardened after failed implementation. 2 blocking formulas. Strict check FAILS. v1.3-pre.9 weight diagnosis: normalization fixes 1st→3rd but all weight variants cap at ~3.0 — substencil polynomials have additional errors.

### v1.3-pre.8 s2 correction (2026-05-27)

- s2 substencil 1/2 factor corrected: moved from first correction term to second
- Corrected s2 achieves ~4.0 individual order (was ~2.0)
- All 4 individual substencils now pass single-step convergence
- Combined 3-substencil scheme still fails (~1st order) — remains blocked
- Re-transcription document: `docs/tasks/cfweno5_formula_verification/s2_retranscription.md`
- Method: pdftotext -layout column-position analysis (image rendering unavailable for visual PDF reading)

### v1.3-pre.9 weight role audit (2026-05-27)

- Comprehensive audit of Table I/Table II weight role and Eq. (17) normalization
- Five weight variants tested via `--diagnose-weights` in consistency checker
- Normalization fixes ~1st→~3rd but ALL variants cap at ~3.0 (not ~5th)
- Table II weights already sum to 1.0 (normalization is no-op for them)
- Equal 1/3 weights achieve same ~3.0 as "optimal" Table I/Table II weights
- **Conclusion C**: Error is in Appendix A Eq. (A1) substencil polynomials, not weights
- Audit document: `docs/tasks/cfweno5_formula_verification/weight_role_audit.md`
- New tool flag: `--diagnose-weights` in `tools/check_cfweno5_formula_consistency.py`
- New Makefile targets: `cfweno5-diagnose-weights`, `cfweno5-diagnose-weights-quick`
- New tests: 7 weight diagnosis tests in `tests/test_cfweno5_formula_consistency.py`

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
**BLOCKED** — After failed CFWENO5 implementation (v1.3, 2026-05-26) and gate hardening
(v1.3-pre.7, 2026-05-27), 2 required formulas block implementation:
`appendix_A_eq_A1` and `cfweno5_stencil_expression` — both medium/failed_validation
with consistency_status=failed. See failed_attempt_diagnostic.md.

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
| tools/check_cfweno5_formula_consistency.py | Added --diagnose-weights mode with 5 variants |
| tests/test_cfweno5_formula_consistency.py | Added 7 weight diagnosis tests |
| Makefile | Added cfweno5-diagnose-weights targets |
| docs/tasks/cfweno5_formula_verification/weight_role_audit.md | Created — comprehensive weight role audit |
| docs/formula_inventories/cfweno5_scalar_formulas.yml | Updated notes for appendix_A_eq_A1 and cfweno5_stencil_expression |
| docs/scheme_specs/cfweno5_scalar_subset.md | Added v1.3-pre.9 weight audit section |
| docs/feasibility/cfweno5_scalar_readiness.md | Added weight diagnosis findings |
| docs/roadmaps/v1_real_paper_demo.md | Added v1.3-pre.9 section |

## Code Changes
- `tools/check_cfweno5_formula_consistency.py` — added `--diagnose-weights` mode (diagnostic only, not solver code)
- `tests/test_cfweno5_formula_consistency.py` — added 7 weight diagnosis tests
- `Makefile` — added `cfweno5-diagnose-weights` and `cfweno5-diagnose-weights-quick` targets
solver/schemes.py NOT modified. cfd/ NOT modified. examples/ NOT modified. results/ NOT modified.

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

## v1.3-pre.7 — Formula Gate Hardening (2026-05-27)

After the failed CFWENO5 implementation (commit dc78864), the formula confidence gate was hardened:

- **Formula inventory**: `appendix_A_eq_A1` and `cfweno5_stencil_expression` demoted from high/verified to medium/failed_validation with consistency_status=failed
- **New field**: `consistency_status` added to all formula entries (passed/failed/not_run/not_required)
- **Confidence checker**: `check_strict()` now blocks on `consistency_status=failed`; `failed_validation` added as valid verification status
- **New tool**: `tools/check_cfweno5_formula_consistency.py` — substencil-level numerical convergence checker
- **New tests**: `tests/test_cfweno5_formula_consistency.py` (12 tests)
- **New doc**: `docs/tasks/cfweno5_formula_verification/appendix_a_reverification_plan.md`
- **Updated tests**: `tests/test_formula_confidence.py` (15 tests, updated for new blocking state)
- **Strict gate**: Now FAILS with 4 blocking items (2 confidence + 2 consistency_status)
- **Spec**: `Approved for implementation` reverted to `no`

## Commit
- **Hash**: pending (this task)
- **Previous hash**: dc78864 (failed attempt diagnostic)
- **Branch**: master
- **Push**: pending

### v1.3-pre.10 combined target audit (2026-05-29)

- Added `docs/tasks/cfweno5_formula_verification/combined_target_audit.md`.
- Updated `tools/check_cfweno5_formula_consistency.py` to report Appendix A's direct full-stencil target separately from the Eq. (16) / Table I WENO-combination diagnostic.
- Updated `tests/test_cfweno5_formula_consistency.py` for the separate `full_target` JSON field and `appendix_A_full_target` diagnostic variant.
- Result: direct Appendix A full target reaches ~6.0 quick one-step order; normalized Table I combined diagnostic remains ~3.0.
- CFWENO5 remains blocked; `Approved for implementation` remains `no`; no solver, `cfd/`, examples, results, release docs, or tags changed.

### v1.3-pre.11 direct target policy (2026-05-29)

- Added `docs/tasks/cfweno5_formula_verification/direct_target_policy.md`.
- Accepted Appendix A Eq. (A1)'s direct full-stencil averaged target as the first scalar linear prototype target.
- Updated the checker so `cfweno5-formula-consistency-quick` gates required scalar-linear targets and reports Eq. (16) / Table I as diagnostic-only.
- Updated formula inventory so direct-target required formulas pass the strict confidence gate.
- CFWENO5 implementation remains forbidden; `Approved for implementation` remains `no`; Eq. (16) / Table I remains unresolved for later WENO-combination work.

### v1.3-pre.12 gate scope alignment (2026-05-29)

- Added `docs/tasks/cfweno5_formula_verification/gate_scope_alignment.md`.
- Updated formula inventory with `formula_scope` for scalar direct-target vs deferred nonlinear/WENO formulas.
- Updated `tools/check_formula_confidence.py` so strict mode checks scalar-linear direct-target required formulas while reporting deferred diagnostics.
- Updated `tests/test_formula_confidence.py` for direct-target strict pass, deferred formula visibility, and approval remaining `no`.
- CFWENO5 remains unimplemented; `Approved for implementation` remains `no`; Eq. (16) / Table I remains deferred.
