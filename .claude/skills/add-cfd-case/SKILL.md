---
name: add-cfd-case
description: Add a new CFD test case or analytic validation case to the project
---

# Add CFD Case

## When to Use

When adding a new flow problem (e.g., Kelvin-Helmholtz, Sedov blast, Taylor-Green vortex)
to the CFD solver, with or without an analytic solution.

## Required Inputs

The user must provide (or the agent must determine):
- **Case name**: short_snake_case identifier (e.g., `kelvin_helmholtz`)
- **Description**: physics of the problem
- **Domain and BCs**: domain extents, boundary condition types
- **IC function**: how to compute initial conditions
- **Analytic solution?**: yes/no — if yes, provide the exact solution formulas
- **Parameters**: any tunable constants

## Required Workflow

1. **Read Definition of Done**: Read `docs/cfd_definition_of_done.md` sections 1 and 2.
2. **Inspect existing cases**: Read `cfd/cases/entropy_wave.py` as reference pattern.
3. **Implement case module**: Create `cfd/cases/<case_name>.py` with:
   - `<CaseName>Params` dataclass
   - `<case_name>_config(params) -> CFDConfig`
   - `<case_name>_ic(nxt, nyt, gamma, params) -> U`
   - If analytic: `<case_name>_primitive()`, `<case_name>_conservative()`, `<case_name>_exact_solution()`
4. **Update exports**: Edit `cfd/cases/__init__.py`.
5. **Create example script**: `examples/run_cfd_<case_name>.py`.
   - If analytic: also create `examples/run_cfd_<case_name>_convergence.py`.
6. **Create tests**: `tests/test_cfd_<case_name>.py`.
7. **Run tests**: `bash -ic 'module-conda && pytest -q'`.
8. **Run example**: `bash -ic 'module-conda && python examples/run_cfd_<case_name>.py'`.
9. **If analytic**: Run convergence study and verify convergence order.
10. **Update docs**: Follow `update-cfd-docs` skill.

## Files to Inspect

- `cfd/cases/entropy_wave.py` — reference pattern for analytic cases
- `cfd/cases/uniform_flow.py` — reference pattern for simple cases
- `cfd/cases/__init__.py` — export pattern
- `cfd/config.py` — CFDConfig fields
- `docs/cfd_definition_of_done.md` — completion checklists

## Files That May Be Modified

- `cfd/cases/<case_name>.py` — **NEW**
- `cfd/cases/__init__.py` — add exports
- `examples/run_cfd_<case_name>.py` — **NEW**
- `examples/run_cfd_<case_name>_convergence.py` — **NEW** (if analytic)
- `tests/test_cfd_<case_name>.py` — **NEW**
- `docs/cfd_module_interfaces.md` — add case section
- `README.md` — add case to tables
- `docs/api/` — regenerated

## Tests to Run

```bash
bash -ic 'module-conda && python -m compileall cfd tests examples tools'
bash -ic 'module-conda && pytest -q'
bash -ic 'module-conda && python examples/run_cfd_<case_name>.py'
# If analytic:
bash -ic 'module-conda && python examples/run_cfd_<case_name>_convergence.py'
```

## Result Files to Generate

- `results/cfd_<case_name>/error_summary.csv`
- `results/cfd_<case_name>/analysis.md`
- `results/cfd_<case_name>/` plots (density, error, comparison)
- If analytic: `results/cfd_<case_name>_convergence/convergence_summary.csv`

## Final Response Format

```
## Final Report

### Changed Files
- list every modified/created file

### Tests Run
- exact pytest command and output

### Validation Results (if analytic)
- L2 errors at each grid resolution
- Observed convergence order
- Comparison with expected order

### Result File Paths
- paths to generated outputs

### Numerical Assumptions
- any assumptions made

### Remaining Risks
- known limitations

### Generated Docs
- list updated documentation
```

## Failure Handling Rules

- If IC produces negative rho or p → check EOS assumptions, add clipping or fallback
- If solver blows up → reduce CFL to 0.3, check wave speed computation
- If convergence order is below expected → check reconstruction, try finer grids
- If tests fail → fix code before proceeding, do NOT skip tests
- If example script fails → investigate root cause, do NOT just catch and ignore exceptions
