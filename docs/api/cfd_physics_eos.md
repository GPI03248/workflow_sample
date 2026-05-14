# API: cfd.physics_eos

Equation of state for ideal gas.

Responsibilities:
    - Compute pressure, sound speed, total energy from primitive or conservative variables.

Does NOT:
    - Perform any spatial operations.

## Functions

### `pressure(rho, u, v, E, gamma)`
Compute pressure from conservative variables.

### `sound_speed(rho, p, gamma)`
Compute sound speed c = sqrt(gamma * p / rho).

### `total_energy(rho, u, v, p, gamma)`
Compute total energy E from primitive variables.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
