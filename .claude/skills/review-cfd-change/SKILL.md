---
name: review-cfd-change
description: Review a CFD code change for correctness, consistency, and completeness
---

# Review CFD Change

## When to Use

- After implementing a CFD feature, before committing
- When the user asks to "review" or "check" a change
- As the final step in the agentic workflow (reviewer agent)

## Required Inputs

- The set of changed files (from `git diff` or task context)
- The original task description or feature request

## Required Workflow

1. **Gather context**:
   ```bash
   git diff --stat          # what files changed
   git diff                  # full diff content
   ```

2. **Check scope**:
   - Are only relevant files modified? Flag any unrelated changes.
   - Is `cfd/constants.py`, `cfd/variables/conversion.py`, or `cfd/mesh/structured.py` modified? These require extra scrutiny.

3. **Check code quality**:
   - Array shapes: does every function respect `(4, nyt, nxt)` convention?
   - No hard-coded indices that assume specific `ng` value
   - No division by zero (epsilon guards in limiters, wave speeds)
   - In-place vs copy: ghost cell filling should be in-place, reconstruction should return copies
   - Import structure: no circular imports, proper use of `__init__.py`

4. **Check correctness**:
   - New reconstruction: does it handle both x and y directions?
   - New limiter: is it vectorized? Does it handle zero inputs?
   - New time integrator: does it use `compute_residual`, not `euler_update`?
   - New flux: does it have both `_x` and `_y` variants?
   - Parameter threading: is `limiter` passed through the full call chain?

5. **Check tests**:
   - Are there new tests for the new feature?
   - Do tests cover edge cases (constant fields, opposite signs, zero inputs)?
   - Are shape assertions present?
   - Is there a "solver runs to completion" test?

6. **Check docs**:
   - Is `docs/cfd_module_interfaces.md` updated?
   - Is `README.md` updated (methods table, cases, results)?
   - Is `CLAUDE.md` updated if new rules apply?
   - Were API docs regenerated?

7. **Check Definition of Done**:
   - Read `docs/cfd_definition_of_done.md`
   - Verify every checklist item for the relevant task type

8. **Report findings**.

## Files to Inspect

- `git diff` — all changes
- `docs/cfd_definition_of_done.md` — completion checklist
- The specific files that were modified
- Test files for the changed modules

## Files That May Be Modified

- None — this skill is read-only review
- If issues are found, recommend fixes but do NOT apply them directly
  (the user or implementer agent should apply fixes)

## Tests to Run

```bash
# Verify everything still works
bash -ic 'module-conda && python -m compileall solver cfd tests examples tools'
bash -ic 'module-conda && pytest -q'
```

## Result Files to Generate

- None (review only)
- Review report in the response

## Final Response Format

```
## Review Report

### Scope Check
- [ ] Only relevant files modified
- [ ] No unrelated changes

### Code Quality
- [ ] Array shape conventions correct
- [ ] No division-by-zero risk
- [ ] In-place / copy semantics correct
- [ ] Imports clean

### Correctness
- [ ] Both x and y directions handled
- [ ] Parameter threading complete
- [ ] Edge cases covered

### Tests
- [ ] New tests present and adequate
- [ ] All tests pass

### Documentation
- [ ] Interface docs updated
- [ ] README updated
- [ ] API docs regenerated

### Definition of Done
- [ ] All checklist items for task type verified

### Issues Found
1. [CRITICAL/WARNING/INFO] description
2. ...

### Verdict
PASS / PASS WITH WARNINGS / FAIL (reason)
```

## Failure Handling Rules

- If scope violations found → FAIL, list the unrelated files
- If critical correctness issues found → FAIL, do NOT proceed to commit
- If warnings found → PASS WITH WARNINGS, list them clearly
- If tests fail → FAIL, fix before re-review
- If docs are stale → WARNING, recommend updating before commit
- Never rubber-stamp: every review must actually inspect the diff
