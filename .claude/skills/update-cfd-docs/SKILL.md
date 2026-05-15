---
name: update-cfd-docs
description: Update CFD documentation after code changes
---

# Update CFD Docs

## When to Use

- After modifying any public CFD interface
- After adding new functions, classes, or parameters
- After changing data flow or module responsibilities
- As the final step of any CFD task (before commit)

## Required Inputs

- None — this skill inspects the current state of the code and docs
- The agent should know what was changed in the current task

## Required Workflow

1. **Identify what changed**: Determine which modules had public interface changes.

2. **Regenerate API docs**:
   ```bash
   tools/run_in_project_env.sh python tools/generate_cfd_api_docs.py
   ```

3. **Update `docs/cfd_module_interfaces.md`** if any of:
   - New public function added
   - Function signature changed (new parameters, return type)
   - New config field added
   - New module created
   - Follow the existing format exactly (tables, headers, code blocks)

4. **Update `docs/cfd_architecture.md`** if any of:
   - Data flow changed (new step in time loop)
   - Module responsibilities changed
   - New module added to the system
   - Array layout conventions changed

5. **Update `docs/cfd_iteration_guide.md`** if any of:
   - New extension point added (new method type)
   - Existing instructions became inaccurate
   - New validation steps required

6. **Update `README.md`** if any of:
   - New methods added (update Supported Methods table)
   - New cases added (update cases table, run instructions)
   - New result directories
   - Convergence results changed

7. **Update `CLAUDE.md`** if any of:
   - New project rules needed (e.g., new parameter threading)
   - Module responsibilities changed
   - New validation requirements

8. **Verify consistency**: Ensure doc changes match actual code.

## Files to Inspect

- `cfd/` — all modified Python files, to extract current interfaces
- `docs/cfd_module_interfaces.md` — current interface docs
- `docs/cfd_architecture.md` — current architecture docs
- `docs/cfd_iteration_guide.md` — current iteration guide
- `README.md` — current README
- `CLAUDE.md` — current project rules

## Files That May Be Modified

- `docs/api/*.md` — regenerated automatically
- `docs/cfd_module_interfaces.md` — manual update
- `docs/cfd_architecture.md` — manual update
- `docs/cfd_iteration_guide.md` — manual update
- `README.md` — manual update
- `CLAUDE.md` — manual update

## Tests to Run

```bash
# Verify no syntax errors introduced
tools/run_in_project_env.sh python -m compileall cfd tests examples tools
tools/run_in_project_env.sh pytest -q
```

## Result Files to Generate

- Updated `docs/api/` directory (33+ files)
- Updated `docs/cfd_module_interfaces.md`
- Updated `docs/cfd_architecture.md` (if applicable)
- Updated `docs/cfd_iteration_guide.md` (if applicable)
- Updated `README.md` (if applicable)
- Updated `CLAUDE.md` (if applicable)

## Final Response Format

```
## Documentation Update Report

### API Docs
- Regenerated: X files in docs/api/

### Interface Docs
- Updated: docs/cfd_module_interfaces.md
  - Added: [list new/changed sections]

### Architecture Docs
- Updated: docs/cfd_architecture.md
  - Changed: [what changed]

### README
- Updated sections: [list]

### CLAUDE.md
- Updated rules: [list]
```

## Failure Handling Rules

- If `generate_cfd_api_docs.py` fails → fix the script, do NOT skip
- If docs don't match code → update docs, not code (code is source of truth)
- If unsure whether to update → err on the side of updating (false positive is better than stale docs)
- Do NOT modify code behavior while updating docs — this skill is doc-only
