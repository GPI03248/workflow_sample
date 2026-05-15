---
name: validate-paper-scheme
description: Validate a numerical method implemented from a paper scheme spec
---

# Validate Paper Scheme

## When to Use

- After implementing a method using `implement-paper-scheme`
- When the user asks to "validate the new method" or "run validation"
- As a mandatory step before committing paper-derived implementations

## Required Inputs

- **Scheme spec path**: `docs/scheme_specs/<scheme_name>.md`
- The implementation must already be complete and tests passing

## Required Workflow

### Step 1: Read Spec

Read the scheme spec to determine:
- What validation is required (from the "Validation required" section)
- Whether the method has an analytic solution available
- What convergence behavior is expected

### Step 2: Run Unit Tests

```bash
tools/run_in_project_env.sh pytest -q
```

All must pass. If any fail, STOP and fix before continuing.

### Step 3: Choose Validation Path

**Path A: Analytic solution available** (preferred)

Run all applicable analytic validation cases:
```bash
tools/run_in_project_env.sh python examples/run_cfd_entropy_wave.py
tools/run_in_project_env.sh python examples/run_cfd_entropy_wave_convergence.py
tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex.py
tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex_convergence.py
```

Or use: `make cfd-validation`

Then:
1. Read `results/cfd_entropy_wave/error_summary.csv`
2. Read `results/cfd_isentropic_vortex/error_summary.csv`
3. Read convergence CSVs for convergence order
4. Compare with baseline (previous method) results
5. Verify convergence order matches theoretical expectation (within 0.2)

**Path B: No analytic solution available**

Run benchmark cases and check qualitative properties:
```bash
tools/run_in_project_env.sh python examples/run_cfd_uniform_flow.py
tools/run_in_project_env.sh python examples/run_cfd_sod_2d.py
```

Check:
1. **Conservation**: mass error should be < 1e-10
2. **Stability**: no NaN, no blow-up, simulation completes
3. **Positivity**: rho > 0, p > 0 everywhere
4. **Qualitative comparison**: compare with baseline method results

### Step 4: Generate Validation Report

Create `results/<scheme_name>_validation/` directory with:

1. `error_summary.csv` — error metrics from all validation cases
2. `analysis.md` — structured analysis report
3. Plots (if matplotlib available):
   - Comparison with baseline method
   - Convergence plot (if applicable)
   - Error field visualization

### Step 5: Assess Results

Determine:
- **PASS**: Errors decrease with grid refinement, convergence order matches theory
- **PASS WITH WARNINGS**: Results are reasonable but convergence order slightly below expected
- **FAIL**: Errors increase, NaN appears, or results are unphysical

### Step 6: Report

Present clear conclusions with evidence.

### Traceability

- After validation, update or create the traceability manifest:
  ```bash
  tools/run_in_project_env.sh python tools/create_task_traceability.py --task-id <id> --validation-result <path>
  ```
- The manifest must record the validation result path.

## What Results CAN Support

- "The method achieves N-th order convergence on smooth test cases."
- "The method preserves uniform flow to machine precision."
- "The L2 error is X times smaller than the baseline method."
- "Mass is conserved to machine precision."
- "The method is stable at CFL=Y on all tested cases."

## What Results CANNOT Support

- "The method is correct for all problems." (Only tested cases were verified.)
- "The method matches the paper's results exactly." (Different implementation, grid, etc.)
- "The method is production-ready." (This is a research prototype.)
- "The convergence rate proves the paper's claims." (Only verifies our implementation.)

## Files to Inspect

- `docs/scheme_specs/<scheme_name>.md` — validation requirements
- `results/cfd_*/error_summary.csv` — error data
- `results/cfd_*/convergence_summary.csv` — convergence data
- `results/cfd_*/analysis.md` — previous analysis for comparison

## Files That May Be Modified

- `results/<scheme_name>_validation/error_summary.csv` — **NEW**
- `results/<scheme_name>_validation/analysis.md` — **NEW**
- Plots in `results/<scheme_name>_validation/` — **NEW**

## Tests to Run

```bash
tools/run_in_project_env.sh pytest -q
# Plus all applicable validation scripts (see workflow step 3)
```

## Result Files to Generate

- `results/<scheme_name>_validation/error_summary.csv`
- `results/<scheme_name>_validation/analysis.md`

## Final Response Format

```
## Validation Report

### Scheme
- Name: <scheme_name>
- Spec: docs/scheme_specs/<scheme_name>.md
- Method type: <category>

### Unit Tests
- pytest: X passed / Y failed

### Analytic Validation (if applicable)
| Case | Grid | L2 Error | Linf Error | Order |
|------|------|----------|------------|-------|
| ... | ... | ... | ... | ... |

### Comparison with Baseline
| Case | Baseline L2 | New Method L2 | Improvement |
|------|------------|---------------|-------------|
| ... | ... | ... | ... |

### Conservation Check
- Mass error: <value>
- Positivity: rho > 0, p > 0: <yes/no>

### Conclusions
- What results support: <list>
- What results do NOT support: <list>
- Needs human review: <yes/no>

### Verdict
PASS / PASS WITH WARNINGS / FAIL

### Result Files
- <paths to all generated files>

### Recommendation
<Whether to commit, needs more work, or needs spec revision>
```

## Failure Handling Rules

- If pytest fails → do NOT proceed to validation, fix tests first
- If NaN appears → CRITICAL failure, the implementation is broken
- If convergence order is significantly below expected → report, suggest investigation
- If errors increase vs. baseline → REGRESSION, do NOT commit
- If mass conservation error > 1e-10 → WARNING, check boundary conditions
- If validation scripts crash → investigate root cause, do NOT skip
