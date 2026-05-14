# API: cfd.validation_errors

Error metrics for CFD solution validation.

Responsibilities:
    - Compute L1, L2, Linf errors per conservative variable.
    - Compute mass error for density.
    - Return results as a structured dict.

Does NOT:
    - Run the solver.
    - Perform any I/O.

## Functions

### `compute_field_errors(U_num, U_exact, dx, dy, variable_names)`
Compute per-variable error metrics between numerical and exact solutions.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
