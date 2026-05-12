# Project Rules — workflow_sample

## Scope

- Keep changes **minimal** — only touch files directly related to the task.
- Do **not** modify unrelated files, tests, or documentation.
- Do **not** refactor code that is not in scope.

## Numerical Correctness

- All numerical schemes must preserve the **array shape** of the input.
- Periodic boundary conditions use `np.roll` by default — no other BC treatment.
- New schemes must be registered in `_SCHEMES` inside `solver/schemes.py`.
- The `step()` function must raise `ValueError` for unknown scheme names.
- The `step()` function must raise `ValueError` for CFL outside [0, 1].
- Every new scheme must be compared against the **analytic solution** using
  `compute_errors()` in `solver/simulate.py`.

## Benchmarking

- When adding a new numerical scheme, update `examples/compare_advection_schemes.py`
  to include it in the `SCHEMES` list.
- Re-run the comparison script and include error results in the final report.
- Result files go in `results/`.

## Testing

- After any code change, run the relevant tests: `pytest -q`
- All existing tests must continue to pass.
- New schemes require at least: shape test, uniform-field test, mass-conservation test.
- All verification commands must use `bash -ic 'module-conda && <command>'`.

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
5. **Error results** — L1, L2, Linf, mass errors for each scheme against analytic solution.
6. **Result file paths** — paths to generated CSV, plot, and analysis report.
