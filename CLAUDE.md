# Project Rules — workflow_sample

## Scope

- Keep changes **minimal** — only touch files directly related to the task.
- Do **not** modify unrelated files, tests, or documentation.
- Do **not** refactor code that is not in scope.

## Environment Rules

- Do **not** use `bash -ic 'module-conda && ...'`. It starts an interactive shell and is unreliable in automated contexts.
- Do **not** depend on user shell aliases (e.g., `module-conda`).
- Do **not** source `~/.bashrc` from tools or hooks.
- All Python / pytest / project tool commands must use:
  ```
  tools/run_in_project_env.sh <command>
  ```
- If environment discovery fails, run:
  ```
  tools/run_in_project_env.sh python tools/discover_project_env.py --json
  ```
- To manually specify conda, set environment variables:
  ```
  export WORKFLOW_SAMPLE_CONDA_SH=/path/to/conda.sh
  export WORKFLOW_SAMPLE_CONDA_ENV=base
  ```
- The wrapper auto-discovers conda via a 5-level priority chain (see `tools/discover_project_env.py`).
- Local config is stored in `.local/project_env.sh` (git-ignored).

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

## Paper-to-Code Rules (MANDATORY)

1. **When a user asks to add a method from a paper**, must use `extract-paper-scheme` skill first.
2. **Never jump from PDF directly to code.** Always go through extraction → spec → approval → implementation.
3. **Unapproved specs must not be implemented.** The spec must pass:
   ```
   tools/run_in_project_env.sh python tools/check_scheme_spec_approval.py <spec>
   ```
   If this returns non-zero, implementation is blocked.
4. **If PDF extraction is incomplete**, must report the issue and ask the user to provide the method section text.
5. **Formulas, variable mappings, and applicability** must be explicitly written into the scheme spec.
6. **After implementation**, must run `validate-paper-scheme` skill or required CFD validation.
7. **Final report for paper-derived work** must include:
   - Paper path
   - Extraction report path (`docs/paper_reviews/<id>_extraction.md`)
   - Scheme spec path (`docs/scheme_specs/<scheme>.md`)
   - Approval checker result
   - Traceability manifest path (`docs/tasks/<id>/traceability.md`)
   - Validation result path (`results/<scheme>_validation/`)
   - Unresolved assumptions
   - Tests run
   - Remaining risks

See `docs/paper_to_code_workflow.md` for the full workflow description.

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
   - `tools/run_in_project_env.sh python examples/run_cfd_entropy_wave.py`
   - `tools/run_in_project_env.sh python examples/run_cfd_entropy_wave_convergence.py`
   - `tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex.py`
   - `tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex_convergence.py`
   Errors must NOT increase significantly vs. previous method.
5. **Public interface changes**: After modifying any public CFD interface, **must**:
   - Run `tools/run_in_project_env.sh python tools/generate_cfd_api_docs.py`
   - Update `docs/cfd_module_interfaces.md`

## Benchmarking

- When adding a new 1D advection scheme, update `examples/compare_advection_schemes.py`.
- When adding a new CFD method, add a test case in `cfd/cases/` and an example script.
- Result files go in `results/`.

## Testing

- After any code change, run: `make test` or `tools/run_in_project_env.sh pytest -q`
- All existing tests must continue to pass.
- New CFD features require tests in `tests/test_cfd_*.py`.
- All verification commands must use `tools/run_in_project_env.sh <command>`.
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

## v0.1 Demo Workflow

- The HLL paper-to-code demo is the project's primary showcase.
- **Do not re-implement HLL.** To reproduce, run `make demo-hll-workflow`.
- Case study: `docs/case_studies/hll_flux_paper_to_code.md`.
- After adding new validation results, run `make validation-index` to update `docs/validation_index.md`.
- After workflow changes, run `make health` to verify repo integrity.
- All commands use `tools/run_in_project_env.sh`.

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
| `make check-spec SPEC=<path>` | Check scheme spec approval status |
| `make trace-task TASK_ID=<id>` | Create traceability manifest |
| `make discover-env` | Show environment discovery result |
| `make demo-hll-workflow` | Run HLL paper-to-code demo end-to-end |
| `make validation-index` | Generate `docs/validation_index.md` |
| `make health` | Repo health check |
