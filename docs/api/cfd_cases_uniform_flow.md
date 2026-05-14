# API: cfd.cases_uniform_flow

Uniform flow preservation case.

Responsibilities:
    - Provide config and initial condition for a uniform free-stream.
    - This case verifies that the solver preserves a constant state.

Does NOT:
    - Run the solver (see cfd.solver).

## Functions

### `uniform_flow_config()`
Return a CFDConfig for the uniform-flow preservation test.

### `uniform_flow_ic(nxt, nyt, rho0, u0, v0, p0, gamma)`
Uniform initial condition.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
