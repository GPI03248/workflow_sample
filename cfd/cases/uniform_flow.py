"""Uniform flow preservation case.

Responsibilities:
    - Provide config and initial condition for a uniform free-stream.
    - This case verifies that the solver preserves a constant state.

Does NOT:
    - Run the solver (see cfd.solver).
"""

from __future__ import annotations
import numpy as np

from ..config import CFDConfig
from ..variables.conversion import primitive_to_conservative


def uniform_flow_config() -> CFDConfig:
    """Return a CFDConfig for the uniform-flow preservation test."""
    return CFDConfig(
        nx=50,
        ny=50,
        xmin=0.0,
        xmax=1.0,
        ymin=0.0,
        ymax=1.0,
        gamma=1.4,
        cfl=0.5,
        ng=2,
        final_time=0.1,
        bc_x="periodic",
        bc_y="periodic",
        flux_type="rusanov",
        reconstruction="piecewise_constant",
        time_integrator="euler",
    )


def uniform_flow_ic(
    nxt: int,
    nyt: int,
    rho0: float = 1.0,
    u0: float = 1.0,
    v0: float = 0.5,
    p0: float = 1.0,
    gamma: float = 1.4,
) -> np.ndarray:
    """Uniform initial condition.

    Returns
    -------
    U : np.ndarray, shape (4, nyt, nxt)
    """
    rho = np.full((nyt, nxt), rho0)
    u = np.full((nyt, nxt), u0)
    v = np.full((nyt, nxt), v0)
    p = np.full((nyt, nxt), p0)
    return primitive_to_conservative(rho, u, v, p, gamma)
