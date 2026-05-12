# Multi-Agent Workflow Sample

A minimal Python project demonstrating how to use **multi-agent / agentic coding workflows** to add numerical schemes to a 1D scalar advection solver.

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

## Project Structure

```
workflow_sample/
  README.md                          # This file
  CLAUDE.md                          # Project rules for Claude Code
  pyproject.toml                     # Dependencies & pytest config
  solver/
    __init__.py
    grid.py                          # 1D grid utilities
    schemes.py                       # Numerical schemes (currently: upwind)
    simulate.py                      # High-level simulation driver
  tests/
    test_upwind.py                   # Upwind correctness tests
    test_mass_conservation.py        # Mass conservation tests
  docs/
    feature_request_lax_wendroff.md  # Task: add Lax-Wendroff scheme
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
# Clone
git clone git@gitee.com:gpiii/workflow_sample.git
cd workflow_sample

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install numpy pytest
```

## Run Tests

```bash
pytest -q
```

## Use the Skill with Claude Code

The `add-numerical-scheme` skill orchestrates the full multi-agent workflow:

1. **repo-analyst** — analyses the repository
2. **scheme-designer** — translates requirements into an implementation plan
3. **implementer** — makes minimal code changes
4. **test-engineer** — adds tests and runs pytest
5. **reviewer** — reviews the final diff

### Recommended Demo Prompt

Open this repo in Claude Code and paste:

```
使用 add-numerical-scheme skill，根据 docs/feature_request_lax_wendroff.md 完成需求。
要求先分析仓库，再设计方案，再实现，再补测试，再审查。
不要修改无关文件。
完成后运行 pytest -q，并给出最终报告。
```

## How This Maps to Real CFD Projects

| This toy project | Real CFD project |
|---|---|
| 1D scalar advection | 3D RANS / LES / DNS |
| Upwind scheme | HLLC, WENO, DG schemes |
| `schemes.py` (one file) | Multi-file flux / limiter libraries |
| Gaussian IC | Complex geometry + mesh |
| `np.roll` periodic BC | MPI halo exchange |
| `pytest` | Regression suites + verification cases |
| 5 agents | 10-20 agents (mesh, BC, I/O, performance, etc.) |

The workflow pattern (analyse -> design -> implement -> test -> review) scales
directly. The skill, agents, and hooks in this repo are a minimal but faithful
template for what a production CFD multi-agent workflow would look like.
