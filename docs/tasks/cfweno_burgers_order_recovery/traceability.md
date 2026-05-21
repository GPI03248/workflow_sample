# Task Traceability: CFWENO3 Burgers Order Recovery Diagnostic

## Task Information
- **Task ID**: cfweno_burgers_order_recovery
- **Task type**: post-v1.0 diagnostic
- **Based on v1.0 tag**: 42d97ee
- **Date**: 2026-05-21
- **Status**: complete

## Purpose
Investigate whether 3rd-order convergence can be recovered for scalar Burgers CFWENO3
by testing different nu-treatment variants. This is a diagnostic study only — no
production code was modified.

## Diagnostic Variants Tested
- A: current production (per-cell nu)
- B: constant global nu
- C: interface-speed nu
- D: predictor + interface nu
- E (case): reduced amplitude (0.05)
- F (case): shorter time (T=0.05)

## Modified Files
| File | Change |
|------|--------|
| examples/run_cfweno_burgers_order_recovery.py | NEW — diagnostic experiment script |
| tests/test_cfweno_burgers_order_recovery.py | NEW — diagnostic tests |
| Makefile | Added cfweno-burgers-order-recovery, demo-v1.1-pre-order-recovery targets |
| docs/tasks/cfweno_burgers_order_recovery/diagnostic_plan.md | NEW — diagnostic plan |
| docs/tasks/cfweno_burgers_order_recovery/traceability.md | NEW — this manifest |
| docs/roadmaps/v1_real_paper_demo.md | Updated with post-v1.0 diagnostic section |
| tools/summarize_validation_results.py | Added order_recovery directory and post-v1.0 section |

## NOT Modified
- solver/schemes.py — NOT modified
- cfd/ — NOT modified
- docs/releases/v1.0.md — NOT modified
- v0.1 tag — NOT moved
- v1.0 tag — NOT moved

## Result Paths
- results/cfweno_burgers_order_recovery/error_summary.csv
- results/cfweno_burgers_order_recovery/analysis.md

## Key Findings
- **A (current per-cell nu)**: order 2.01, stable baseline
- **B (constant global nu)**: order ~1.0 — dramatically worse, drops to first order
- **C (interface-speed nu)**: order ~1.96 — slightly lower absolute error (~4x) but same order
- **D (predictor + interface nu)**: order ~2.01 — same as current
- **Reduced amplitude (0.05)**: order 2.01 — nonlinear strength does not change the order
- **Shorter time (T=0.05)**: order 2.00 — same structural result
- **Conclusion**: No simple nu-treatment variant recovers 3rd order. The ~2nd-order result
  is structural for the CFWENO3 stencil applied to Burgers. Recovery likely requires the
  paper's nonlinear WENO weights (Eq. 17, Tables I-II).

## Limitations
- Diagnostic variants are NOT approved for production
- Reference solutions are numerical (not analytic)
- Only pre-shock smooth data tested
- No shock-capturing tested

## Whether Production Solver Changed
No — solver/schemes.py was NOT modified.

## Whether v1.0 Tag Changed
No — v1.0 still points to 42d97ee.

## Commit
- **Hash**: pending
- **Branch**: master
- **Push**: pending
