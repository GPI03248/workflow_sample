# Multi-Agent Workflow Sample

A minimal Python project demonstrating how to use **multi-agent / agentic coding workflows** to add numerical schemes to a 1D scalar advection solver, with **analytic-solution verification**.

## Purpose

This project is **not** about building a production CFD solver. It is a toy
example that showcases a new engineering paradigm:

| Traditional (script) | Agentic (this project) |
|---|---|
| Human reads the request | repo-analyst agent reads the repo |
| Human designs the scheme | scheme-designer agent creates a plan |
| Human writes code | implementer agent makes minimal edits |
| Human writes tests | test-engineer agent adds and runs tests |
| Human reviews | reviewer agent checks the diff |
| Human follows a checklist | skill encodes the workflow once, runs every time |
| Human remembers rules | hooks enforce rules automatically |

## Verification Mechanism

The solver solves the **1D linear advection equation** with a known analytic
solution, enabling systematic verification of numerical schemes:

- **PDE**:  u_t + a * u_x = 0,  a = 1.0
- **Domain**:  x in [0, 1), periodic boundary
- **Initial condition**:  u(x, 0) = sin(2*pi*x) + 1
- **Analytic solution**:  u_exact(x, t) = sin(2*pi*(x - a*t)) + 1

Each numerical scheme is compared against the analytic solution using L1, L2,
Linf, and mass-conservation error metrics.

## Project Structure

```
workflow_sample/
  README.md                          # This file
  CLAUDE.md                          # Project rules for Claude Code
  pyproject.toml                     # Dependencies & pytest config
  solver/
    __init__.py
    grid.py                          # 1D grid utilities
    schemes.py                       # Numerical schemes (upwind, lax_wendroff)
    simulate.py                      # Simulation driver + analytic solution + errors
  tests/
    test_upwind.py                   # Scheme correctness tests
    test_mass_conservation.py        # Mass conservation tests
  examples/
    compare_advection_schemes.py     # Benchmark: compare schemes vs analytic
  results/                           # Generated benchmark outputs
    advection_error_summary.csv
    advection_solution_comparison.png
    advection_analysis.md
  docs/
    feature_request_lax_wendroff.md  # Task: add Lax-Wendroff scheme (completed)
  .claude/
    agents/                          # Sub-agent definitions
      repo-analyst.md
      scheme-designer.md
      implementer.md
      test-engineer.md
      reviewer.md
    skills/
      add-numerical-scheme/
        SKILL.md                     # Orchestrating skill
    hooks/
      block-dangerous-bash.sh        # Blocks rm -rf, git push --force, etc.
      quick-check.sh                 # Runs compile check + pytest after edits
    settings.json                    # Hook configuration
```

## Installation

```bash
git clone git@gitee.com:gpiii/workflow_sample.git
cd workflow_sample
pip install numpy pytest matplotlib
```

> Note: matplotlib is optional — the comparison script will still produce CSV
> and markdown reports without it.

## Run Tests

```bash
bash -ic 'module-conda && pytest -q'
```

## Generate Benchmark Results

```bash
bash -ic 'module-conda && python examples/compare_advection_schemes.py'
```

This produces:
- `results/advection_error_summary.csv` — error metrics per scheme
- `results/advection_solution_comparison.png` — overlay plot (if matplotlib is available)
- `results/advection_analysis.md` — qualitative analysis report

## How to Add a New Numerical Scheme

1. Implement the scheme function in `solver/schemes.py`.
2. Register it in the `_SCHEMES` dict.
3. Add tests (shape, uniform field, mass conservation).
4. Update `examples/compare_advection_schemes.py` to include the new scheme in `SCHEMES`.
5. Re-run tests and the comparison script to verify.

Or use the multi-agent workflow:

```
使用 add-numerical-scheme skill，根据 docs/feature_request_lax_wendroff.md 完成需求。
要求先分析仓库，再设计方案，再实现，再补测试，再审查。
不要修改无关文件。完成后运行 pytest -q，并给出最终报告。
```

## How This Maps to Real CFD Projects

| This toy project | Real CFD project |
|---|---|
| 1D scalar advection | 3D RANS / LES / DNS |
| Upwind / Lax-Wendroff | HLLC, WENO, DG schemes |
| `schemes.py` (one file) | Multi-file flux / limiter libraries |
| sin(2*pi*x) + 1 IC | Complex geometry + mesh |
| `np.roll` periodic BC | MPI halo exchange |
| Analytic L2 error | Manufactured solutions / convergence studies |
| `pytest` | Regression suites + verification cases |
| 5 agents | 10-20 agents (mesh, BC, I/O, performance, etc.) |

The workflow pattern (analyse -> design -> implement -> test -> review -> verify
against analytic solution) scales directly to production CFD.
