---
name: add-numerical-scheme
description: Orchestrates the full multi-agent workflow to add a new numerical scheme to the 1D advection solver — from analysis through design, implementation, testing, and review.
---

# Skill: add-numerical-scheme

This skill orchestrates the complete multi-agent workflow for adding a new
numerical scheme to the `workflow_sample` solver.

## Trigger

User asks to add a new numerical scheme (e.g. Lax-Wendroff, Lax-Friedrichs,
Beam-Warming, etc.) or references a feature request document in `docs/`.

## Workflow

### Step 1 — Analyse the Repository

Call the **repo-analyst** agent to:

- Map the current file structure.
- Locate `solver/schemes.py`, the `_SCHEMES` dict, and existing test files.
- Identify extension points and risks.

### Step 2 — Design the Scheme

Call the **scheme-designer** agent to:

- Read the feature request or the user's description of the new scheme.
- Translate the mathematical formula into a numpy implementation plan.
- Specify function signature, boundary conditions, invariants, and test points.

### Step 3 — Implement

Call the **implementer** agent to:

- Add the scheme function to `solver/schemes.py`.
- Register it in `_SCHEMES`.
- Run `python -m compileall solver tests` to verify syntax.
- Make **no other changes**.

### Step 4 — Test

Call the **test-engineer** agent to:

- Add tests in `tests/` for the new scheme.
- Run `pytest -q`.
- Report results; fix test issues if needed.

### Step 5 — Review

Call the **reviewer** agent to:

- Inspect the full diff.
- Check numerical correctness, boundary conditions, test coverage.
- Give an ACCEPT or REJECT verdict.

### Step 6 — Final Report

The coordinator produces a final summary:

```
## Final Report

### Changed Files
- (list of modified/created files)

### Tests Run
- (pytest command and output)

### Numerical Assumptions
- (CFL range, stability notes)

### Remaining Risks
- (known limitations)

### Next Recommended Step
- (suggested follow-up)
```

## Rules

- Each agent is called in sequence; no parallel execution of agents that
  depend on each other's output.
- If any agent reports a blocking issue, halt and report to the user.
- Keep changes minimal — no unrelated refactoring.
- Do not modify files outside the solver/tests/docs scope.
