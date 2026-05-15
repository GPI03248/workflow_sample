---
name: run-cfd-validation
description: Run full CFD analytic validation suite and report results
---

# Run CFD Validation

## When to Use

- After modifying any CFD numerical method (reconstruction, limiter, Riemann, time integrator)
- Before committing CFD changes
- When the user asks to "run validation" or "check convergence"
- Periodically to verify no regressions

## Required Inputs

- No specific inputs required — runs the full validation suite
- Optionally: specific case to run, specific grid sizes

## Required Workflow

1. **Compile check**:
   ```bash
   tools/run_in_project_env.sh python -m compileall solver cfd tests examples tools
   ```
2. **Run all unit tests**:
   ```bash
   tools/run_in_project_env.sh pytest -q
   ```
   All must pass. If any fail, STOP and fix before continuing.

3. **Run 1D scalar advection validation** (optional, if solver/ changed):
   ```bash
   tools/run_in_project_env.sh python examples/compare_advection_schemes.py
   ```

4. **Run CFD uniform flow** (must be exact to machine precision):
   ```bash
   tools/run_in_project_env.sh python examples/run_cfd_uniform_flow.py
   ```

5. **Run entropy wave validation**:
   ```bash
   tools/run_in_project_env.sh python examples/run_cfd_entropy_wave.py
   ```

6. **Run entropy wave convergence**:
   ```bash
   tools/run_in_project_env.sh python examples/run_cfd_entropy_wave_convergence.py
   ```

7. **Run isentropic vortex validation**:
   ```bash
   tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex.py
   ```

8. **Run isentropic vortex convergence**:
   ```bash
   tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex_convergence.py
   ```

9. **Collect and compare results**: Read all `error_summary.csv` and `convergence_summary.csv` files.

10. **Report**: Present all errors, convergence orders, and pass/fail status.

## Files to Inspect

- `results/cfd_uniform_flow/summary.csv` — should show machine-precision errors
- `results/cfd_entropy_wave/error_summary.csv` — L2, Linf, mass errors
- `results/cfd_entropy_wave_convergence/convergence_summary.csv` — convergence order
- `results/cfd_isentropic_vortex/error_summary.csv` — L2 error per method
- `results/cfd_isentropic_vortex_convergence/convergence_summary.csv` — convergence order

## Files That May Be Modified

- None — this skill is read-only. It runs scripts and reports results.
- Result files in `results/` will be overwritten with fresh data.

## Tests to Run

```bash
tools/run_in_project_env.sh python -m compileall solver cfd tests examples tools
tools/run_in_project_env.sh pytest -q
tools/run_in_project_env.sh python examples/run_cfd_entropy_wave.py
tools/run_in_project_env.sh python examples/run_cfd_entropy_wave_convergence.py
tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex.py
tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex_convergence.py
```

Or use Makefile:
```bash
make compile test cfd-validation
```

## Result Files Generated

- `results/cfd_entropy_wave/error_summary.csv`
- `results/cfd_entropy_wave/analysis.md`
- `results/cfd_entropy_wave_convergence/convergence_summary.csv`
- `results/cfd_entropy_wave_convergence/convergence_analysis.md`
- `results/cfd_isentropic_vortex/error_summary.csv`
- `results/cfd_isentropic_vortex/analysis.md`
- `results/cfd_isentropic_vortex_convergence/convergence_summary.csv`
- `results/cfd_isentropic_vortex_convergence/convergence_analysis.md`

## Final Response Format

```
## Validation Report

### Compilation
- PASS / FAIL

### Unit Tests
- pytest: X passed / Y failed

### Entropy Wave
| Grid | L2 Error | Linf Error | Mass Error |
|------|----------|------------|------------|
| 32   | ...      | ...        | ...        |
| 64   | ...      | ...        | ...        |
| 128  | ...      | ...        | ...        |

Convergence order: X.XX (expected: ~1.0 for 1st order, ~2.0 for 2nd order)

### Isentropic Vortex
| Method       | L2 Error |
|--------------|----------|
| baseline     | ...      |
| MUSCL+RK2   | ...      |

Convergence order: X.XX

### Regression Check
- [ ] Errors did NOT increase vs. previous run
- [ ] Convergence order matches expectation
- [ ] No NaN or negative values

### Result File Paths
- list all generated result files
```

## Failure Handling Rules

- If pytest fails → STOP, report failure, do NOT run validation scripts
- If any script crashes → report the exact error, suggest fix
- If errors increase significantly (>2x) vs. previous → flag as REGRESSION
- If convergence order drops → flag as REGRESSION
- If NaN appears in results → this is a CRITICAL failure, the solver is broken
- If mass conservation error > 1e-10 → flag, check boundary conditions
