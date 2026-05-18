# HLL Flux Paper-to-Code Case Study

This document demonstrates how the `workflow_sample` project constrains an AI
agent to go from a paper-like note to a verified numerical implementation
without skipping review or approval steps.

---

## 1. Purpose

This case study shows:

- **Spec-gated paper-to-code workflow**: an AI agent cannot implement code
  until a human explicitly approves a scheme specification.
- **Deterministic approval checker**: approval is enforced by a script
  (`tools/check_scheme_spec_approval.py`), not by the agent reading markdown.
- **Full traceability**: every step from source note to committed code is
  recorded in a traceability manifest.
- **Tests and validation**: the implementation is verified by unit tests and
  compared against an analytic solution.
- **HLL approximate Riemann solver** as a controlled, reproducible example.

---

## 2. Workflow Summary

```
Source note (docs/papers/hll_flux_test_note.md)
  |
  v
Extraction report (docs/paper_reviews/hll_flux_test_note_extraction.md)
  |
  v
Scheme spec (docs/scheme_specs/hll_flux.md)  -- Approved for implementation: no
  |
  v
Gate test: agent attempts implementation  -- BLOCKED by approval checker
  |                                          (recorded in traceability)
  v
Human review: change Approved to "yes"
  |
  v
Deterministic approval checker  -- PASSES
  |
  v
Implementation (cfd/numerics/riemann.py, update.py, config.py)
  |
  v
Unit tests (tests/test_cfd_fluxes.py)
  |
  v
Validation (examples/run_cfd_hll_validation.py)
  |
  v
Traceability manifest updated (docs/tasks/hll_flux_implementation/traceability.md)
  |
  v
Commit and push
```

---

## 3. Source Material

| File | Purpose |
|------|---------|
| `docs/papers/hll_flux_test_note.md` | Source note describing the HLL solver (test document, not a real paper) |
| `docs/paper_reviews/hll_flux_test_note_extraction.md` | Extraction report with 12 formulas, notation table, compatibility assessment |
| `docs/scheme_specs/hll_flux.md` | Implementation spec: formulas, variable mapping, algorithm steps, tests required |

---

## 4. Approval Gate Behavior

### Before approval

The scheme spec initially has `Approved for implementation: no`. The
`implement-paper-scheme` skill runs the approval checker as Step 0:

```bash
tools/run_in_project_env.sh python tools/check_scheme_spec_approval.py docs/scheme_specs/hll_flux.md
```

Output:

```
[NOT APPROVED] docs/scheme_specs/hll_flux.md
  Status: 'no'
  Reason: Approved for implementation is not yes (found: 'no')
```

Exit code: 1. Implementation is **blocked**. No code changes are made.

This was verified in commit `b5d446b` (gate test) and recorded in
`docs/tasks/hll_flux_workflow_gate_test/traceability.md`.

### After human approval

The human changes the spec to `Approved for implementation: yes`. The same
command now returns:

```
[APPROVED] docs/scheme_specs/hll_flux.md
  Status: 'yes'
  Reason: Approved for implementation is yes
```

Exit code: 0. Implementation may proceed.

### Checker design

- Only the exact string `yes` (case-insensitive) results in approval.
- `no`, missing line, misspellings, and file-not-found all return non-zero.
- The checker uses standard library only, no external dependencies.
- JSON output is available via `--json`.

---

## 5. Implementation Summary

### Files modified or created

| File | Change |
|------|--------|
| `cfd/numerics/riemann.py` | Added `hll_flux_x`, `hll_flux_y`, `_roe_averages_x`, `_roe_averages_y` |
| `cfd/numerics/update.py` | Added `"hll"` dispatch in `compute_residual` |
| `cfd/numerics/__init__.py` | Exported `hll_flux_x`, `hll_flux_y` |
| `cfd/config.py` | Updated `flux_type` docstring to list `"hll"` |
| `tests/test_cfd_fluxes.py` | Added 10 HLL tests |
| `examples/run_cfd_hll_validation.py` | HLL vs Rusanov validation script |

### Key design decisions

- HLL is a **two-wave** approximate Riemann solver (Harten-Lax-van Leer, 1983).
- Uses Roe-averaged wave speed estimates for S_L and S_R.
- Epsilon guard (1e-14) handles the degenerate case S_R == S_L.
- Default `flux_type` remains `"rusanov"` for backward compatibility.
- Select HLL via `CFDConfig(flux_type="hll")`.

### Not implemented

- **HLLC** (three-wave solver, contact-restoring) is not implemented.
- **Roe** flux is not implemented.
- HLL **cannot resolve contact discontinuities or shear waves**.

---

## 6. Tests

Tests are in `tests/test_cfd_fluxes.py`:

| Test | What it verifies |
|------|------------------|
| `test_hll_flux_x_shape` | Output shape `(4, nyt, nxt-1)` |
| `test_hll_flux_y_shape` | Output shape `(4, nyt-1, nxt)` |
| `test_hll_flux_x_consistency` | UL == UR implies HLL flux == physical flux |
| `test_hll_flux_y_consistency` | Same for y-direction |
| `test_hll_flux_x_no_nan` | No NaN for moderate Mach states |
| `test_hll_flux_y_no_nan` | Same for y-direction |
| `test_hll_epsilon_guard` | No division by zero when S_L == S_R |
| `test_hll_vs_rusanov_less_diffusive` | HLL and Rusanov produce different fluxes |
| `test_update_raises_on_unknown_flux` | Unknown `flux_type` raises `ValueError` |
| `test_solver_runs_with_hll` | Solver completes uniform flow with `flux_type="hll"` |

All existing Rusanov tests continue to pass.

---

## 7. Validation Results

Script: `examples/run_cfd_hll_validation.py`

Output: `results/cfd_hll_validation/`

| Case | Riemann | rho L2 | rho Linf | rho mass |
|------|---------|--------|----------|----------|
| entropy_wave | rusanov | 1.593e-02 | 2.288e-02 | ~0 |
| entropy_wave | **hll** | **1.073e-02** | **1.563e-02** | ~0 |
| uniform_flow | rusanov | 0.0 | 0.0 | 0.0 |
| uniform_flow | **hll** | 0.0 | 0.0 | 0.0 |

HLL/Rusanov L2 ratio (entropy wave): **0.67**. HLL produces lower errors on
this smooth benchmark, as expected for a less diffusive solver.

**Caveats:**

- This result is specific to the entropy wave benchmark (40x20 grid,
  piecewise constant reconstruction, forward Euler).
- It does **not** prove HLL is universally better than Rusanov.
- Uniform flow is preserved exactly by both methods.

---

## 8. Traceability

| Manifest | What it records |
|----------|-----------------|
| `docs/tasks/hll_flux_workflow_gate_test/traceability.md` | Gate test: unapproved spec was correctly rejected |
| `docs/tasks/hll_flux_implementation/traceability.md` | Approved implementation: source, approval, code changes, tests, validation, risks |

---

## 9. Reproduction Commands

Run the full demo:

```bash
make demo-hll-workflow
```

Or step by step:

```bash
# 1. Check approval
tools/run_in_project_env.sh python tools/check_scheme_spec_approval.py docs/scheme_specs/hll_flux.md

# 2. Compile check
tools/run_in_project_env.sh python -m compileall solver cfd tests examples tools

# 3. Run all tests
tools/run_in_project_env.sh pytest -q

# 4. Run HLL validation
tools/run_in_project_env.sh python examples/run_cfd_hll_validation.py

# 5. Generate validation index
tools/run_in_project_env.sh python tools/summarize_validation_results.py

# 6. Check repo health
tools/run_in_project_env.sh python tools/check_repo_health.py
```

---

## 10. Known Limitations

- HLLC (contact-restoring three-wave solver) is not implemented.
- Roe flux is not implemented.
- HLL cannot resolve contact discontinuities or shear waves.
- The current benchmark suite is limited (entropy wave, uniform flow).
- No GPU or MPI parallelization (single-thread Python/NumPy).
- The paper-to-code workflow has been demonstrated on a controlled HLL test
  note, not yet on a complex real PDF with garbled formulas.
- Roe-averaged wave speeds may be poorly conditioned when both states have
  the same density but opposite velocities.
