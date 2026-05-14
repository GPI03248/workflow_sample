"""2D compressible Euler equation solver (CPU, NumPy).

This package provides a minimal but complete full-field CFD solver MVP for the
2D compressible Euler equations with an ideal gas.  It is designed to be
extendable — new fluxes, reconstruction methods, limiters, and time integrators
can be added with minimal changes to the existing code.

Public sub-packages:
    mesh        — structured Cartesian mesh
    variables   — primitive / conservative conversion
    physics     — EOS, physical fluxes, wave speeds
    boundary    — ghost-cell boundary conditions
    numerics    — reconstruction, Riemann solvers, time stepping, update
    cases       — pre-built test cases
    io          — result output
"""

__all__ = [
    "mesh",
    "variables",
    "physics",
    "boundary",
    "numerics",
    "cases",
    "io",
]
