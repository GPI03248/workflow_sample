# Project Rules — workflow_sample

## Scope

- Keep changes **minimal** — only touch files directly related to the task.
- Do **not** modify unrelated files, tests, or documentation.
- Do **not** refactor code that is not in scope.

## Numerical Correctness (1D Advection)

- All numerical schemes must preserve the **array shape** of the input.
- Periodic boundary conditions use `np.roll` by default — no other BC treatment.
- New schemes must be registered in `_SCHEMES` inside `solver/schemes.py`.
- The `step()` function must raise `ValueError` for unknown scheme names.
- The `step()` function must raise `ValueError` for CFL outside [0, 1].
- Every new scheme must be compared against the **analytic solution** using
  `compute_errors()` in `solver/simulate.py`.

## CFD Subsystem Rules

- The CFD solver lives in `cfd/` and must **not** pollute `solver/`.
- Each sub-package must have a clear `__init__.py` with `__all__`.
- Internal helpers use underscore prefix.
- `cfd/solver.py` is orchestration only — no numerical detail.
- Conservative array shape: `(4, nyt, nxt)` where `nyt = ny + 2*ng`.
- Ghost cells are always included in the array.
- MUSCL reconstruction operates on **primitive variables** (rho, u, v, p), not conservative.
- `reconstruct_y` handles y-direction interfaces; `reconstruct` handles x-direction.
- Slope limiters (minmod, van Leer) are vectorized NumPy functions: `limiter(a, b) -> slope`.
- SSP RK2 uses `compute_residual` for the spatial operator, NOT `euler_update`.
- `limiter` parameter must be threaded through `update.py` -> `time_integration.py` -> `solver.py`.

### cfd/ Directory Responsibilities

| Directory | Owns | Does NOT own |
|-----------|------|-------------|
| `mesh/` | Grid layout, cell centres | Solution data |
| `variables/` | Primitive <-> Conservative | Spatial operations |
| `physics/` | EOS, physical fluxes, wave speeds | Numerical fluxes |
| `boundary/` | Ghost-cell filling | Numerical methods |
| `numerics/` | Reconstruction, limiters, Riemann, dt, update, time loop | Physics |
| `cases/` | IC + config for a specific problem | Solver loop |
| `validation/` | Error metrics, analytic comparison | Solver logic |
| `io/` | Output to disk | Computation |
| `solver.py` | Orchestration | Numerical details |

## CFD Task Workflow (MANDATORY)

1. **Read Definition of Done first**: Before starting ANY CFD task, read
   `docs/cfd_definition_of_done.md` and identify which checklist applies.
2. **Use skills**: Prioritize skills in `.claude/skills/`:
   - `add-cfd-case` — for new flow problems or analytic validation cases
   - `add-numerical-method` — for new reconstruction, limiter, Riemann solver, or time integrator
   - `run-cfd-validation` — to run the full analytic validation suite
   - `update-cfd-docs` — to update documentation after code changes
   - `review-cfd-change` — to review a change before committing
3. **No pytest-only claims**: Passing `pytest -q` alone is **NOT sufficient** to claim
   numerical correctness. Analytic validation must be run and results reported.
4. **New numerical methods**: After adding any new CFD numerical method, **must** run:
   - `python examples/run_cfd_entropy_wave.py`
   - `python examples/run_cfd_entropy_wave_convergence.py`
   - `python examples/run_cfd_isentropic_vortex.py`
   - `python examples/run_cfd_isentropic_vortex_convergence.py`
   Errors must NOT increase significantly vs. previous method.
5. **Public interface changes**: After modifying any public CFD interface, **must**:
   - Run `python tools/generate_cfd_api_docs.py`
   - Update `docs/cfd_module_interfaces.md`

## Benchmarking

- When adding a new 1D advection scheme, update `examples/compare_advection_schemes.py`.
- When adding a new CFD method, add a test case in `cfd/cases/` and an example script.
- Result files go in `results/`.

## Testing

- After any code change, run: `make test` or `bash -ic 'module-conda && pytest -q'`
- All existing tests must continue to pass.
- New CFD features require tests in `tests/test_cfd_*.py`.
- All verification commands must use `bash -ic 'module-conda && <command>'`.
- Use `make compile` for syntax checking.

## Documentation

- When modifying CFD numerical methods, update `docs/cfd_module_interfaces.md`.
- When modifying solver data flow, update `docs/cfd_architecture.md`.
- After adding new public functions, regenerate API docs: `make docs`
- After any CFD task, follow the `update-cfd-docs` skill checklist.

## Safety

- Do **not** use the network (no web requests, no pip install at runtime).
- Do **not** run dangerous shell commands (`rm -rf`, `git push --force`, etc.).
- Do **not** store or commit API keys, secrets, or credentials.

## Final Report

When a task is complete, the final response must include:

1. **Changed files** — list every file that was modified or created.
2. **Tests run** — the exact pytest command and its output.
3. **Numerical assumptions** — any assumptions about CFL limits, stability, etc.
4. **Remaining risks** — known limitations, edge cases, or follow-up items.
5. **Error results** — relevant error metrics (L1, L2, Linf, mass).
6. **Result file paths** — paths to generated outputs.
7. **Generated docs** — any documentation created or updated.

## Makefile Quick Reference

| Target | Command |
|--------|---------|
| `make compile` | Syntax check all Python |
| `make test` | Run pytest |
| `make docs` | Regenerate API docs |
| `make cfd-validation` | Run full CFD validation suite |
| `make cfd-entropy` | Entropy wave single run |
| `make cfd-vortex` | Isentropic vortex single run |
| `make cfd-entropy-convergence` | Entropy wave convergence |
| `make cfd-vortex-convergence` | Isentropic vortex convergence |
