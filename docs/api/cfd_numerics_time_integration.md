# API: cfd.numerics_time_integration

Time integration driver.

Responsibilities:
    - Run the main time loop: compute dt -> update -> apply BC -> repeat.
    - Handle final-step truncation to hit exact final_time.
    - Collect intermediate output snapshots.

Does NOT:
    - Implement individual update steps (see update.py).

## Functions

### `advance(U, dx, dy, ng, cfl, final_time, bc_x, bc_y, n_output, gamma, flux_type, reconstruction, time_integrator)`
Advance solution from t=0 to t=final_time.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
