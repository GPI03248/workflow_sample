# API: cfd.solver

CFD solver orchestration.

Responsibilities:
    - Tie together mesh, initial conditions, boundary conditions, numerics, and output.
    - This is the main entry point for running a CFD simulation.

Does NOT:
    - Implement numerical methods (see numerics/).
    - Define physics (see physics/).

## Functions

### `run_solver(config, initial_condition_func, case_name, output_dir, centerline_x)`
Run a full CFD simulation from initialisation to output.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
