---
name: implement-paper-scheme
description: Implement a numerical method from an approved scheme spec
---

# Implement Paper Scheme

## When to Use

- When a scheme spec has been reviewed and approved by the user
- When the user says "implement the spec" or "已确认 spec，请实现"

## Required Inputs

- **Scheme spec path**: `docs/scheme_specs/<scheme_name>.md`
- The spec **MUST** contain `Approved for implementation: yes`

## Required Workflow

### Step 0: Gate Check

1. Read the scheme spec file.
2. Search for `Approved for implementation: yes` (exact match).
3. If NOT found → **STOP**. Tell the user:
   ```
   The scheme spec does not have "Approved for implementation: yes".
   Implementation is blocked. Please review the spec and update it.
   ```
4. Do NOT proceed with any code changes.

### Step 1: Read Context

Read in order:
1. `CLAUDE.md` — project rules
2. `docs/cfd_definition_of_done.md` — completion checklist for the method type
3. `docs/cfd_module_interfaces.md` — current interfaces
4. `docs/cfd_iteration_guide.md` — how to extend the solver
5. The scheme spec — the approved implementation plan

### Step 2: Classify and Plan

From the spec, determine the method category:
- `reconstruction` → modify `cfd/numerics/reconstruction.py`
- `limiter` → modify `cfd/numerics/limiters.py`
- `riemann` → modify `cfd/numerics/riemann.py`, `cfd/numerics/update.py`
- `time_integrator` → modify `cfd/numerics/time_integration.py`
- `boundary_condition` → modify `cfd/boundary/`
- `complete_case` → create `cfd/cases/<case>.py`, possibly multiple methods

Use `EnterPlanMode` to create an implementation plan if the change is non-trivial.

### Step 3: Implement

Follow the spec's "Algorithm steps" and "Required code changes" exactly.

Rules:
- Follow existing code patterns (see the referenced modules)
- Use the variable names from the spec's "Variable mapping" table
- Add the method to the existing dispatch (if/elif chain)
- Thread new parameters through the call chain (`update.py` → `time_integration.py` → `solver.py`)
- Update `CFDConfig` if new parameters are needed
- Update `__init__.py` exports

### Step 4: Write Tests

Create or update test files per the spec's "Tests required" section and `docs/cfd_definition_of_done.md`:
- Unit tests for the new method
- Integration test (solver runs to completion)
- Edge cases (constant fields, NaN safety, shape correctness)

### Step 5: Update Documentation

1. Update `docs/cfd_module_interfaces.md` with new function signatures
2. Update `docs/cfd_iteration_guide.md` if extension instructions changed
3. Run `bash -ic 'module-conda && python tools/generate_cfd_api_docs.py'`
4. Update `README.md` if user-visible features changed
5. Update `CLAUDE.md` if new project rules are needed

### Step 6: Run Validation

Per the spec's "Validation required" section:
```bash
bash -ic 'module-conda && python -m compileall solver cfd tests examples tools'
bash -ic 'module-conda && pytest -q'
```

Then run the required analytic validation:
```bash
bash -ic 'module-conda && python examples/run_cfd_entropy_wave.py'
bash -ic 'module-conda && python examples/run_cfd_entropy_wave_convergence.py'
bash -ic 'module-conda && python examples/run_cfd_isentropic_vortex.py'
bash -ic 'module-conda && python examples/run_cfd_isentropic_vortex_convergence.py'
```

Or use: `make compile test cfd-validation`

### Step 7: Review

Use the `review-cfd-change` skill to review all changes before reporting.

## Mandatory Rules

- **NEVER implement without `Approved for implementation: yes`** in the spec
- **NEVER skip the validation step** — pytest alone is not sufficient
- **NEVER fabricate formulas** — use only what's in the spec
- Follow the spec exactly — if something is unclear, ask rather than guess
- If the implementation reveals the spec is wrong, **STOP** and ask the user to update the spec

## Files to Inspect

- `docs/scheme_specs/<scheme_name>.md` — the approved spec
- `docs/cfd_definition_of_done.md` — completion checklist
- `docs/cfd_module_interfaces.md` — current interfaces
- `docs/cfd_iteration_guide.md` — extension guide
- The specific modules listed in the spec's "Required code changes"

## Files That May Be Modified

Per the spec's "Required code changes" table. Typically:
- `cfd/numerics/<module>.py` — add method
- `cfd/numerics/__init__.py` — update exports
- `cfd/config.py` — add parameters
- `cfd/solver.py` — thread parameters
- `tests/test_cfd_<topic>.py` — add tests
- `docs/cfd_module_interfaces.md` — update interfaces
- `docs/api/` — regenerated
- `README.md` — if user-visible

## Tests to Run

```bash
bash -ic 'module-conda && python -m compileall solver cfd tests examples tools'
bash -ic 'module-conda && pytest -q'
bash -ic 'module-conda && python examples/run_cfd_entropy_wave.py'
bash -ic 'module-conda && python examples/run_cfd_isentropic_vortex.py'
bash -ic 'module-conda && python examples/run_cfd_isentropic_vortex_convergence.py'
```

## Result Files to Generate

- Code changes per spec
- Updated test files
- Updated documentation
- Validation results in `results/`

## Final Response Format

```
## Implementation Report

### Scheme Spec
- Path: docs/scheme_specs/<scheme_name>.md
- Approved: yes

### Changed Files
- list every modified/created file

### Tests Run
- pytest: X passed / Y failed
- Validation scripts: results summary

### Validation Results
- Entropy wave L2 error: <value>
- Isentropic vortex L2 error: <value>
- Convergence order: <value>

### Compatibility
- New config fields: <list>
- API changes: <list>
- Backward compatible: yes/no

### Remaining Risks
- known limitations

### Generated Docs
- list updated documentation files
```

## Failure Handling Rules

- If spec not approved → STOP, show the gate check message
- If implementation reveals spec error → STOP, describe the issue, ask user to update spec
- If tests fail → fix code, re-run, do NOT skip tests
- If validation errors increase significantly → report as regression, investigate
- If the method causes NaN → check epsilon guards, safety fallbacks
