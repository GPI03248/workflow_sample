"""2D Sod-like shock tube case.

Responsibilities:
    - Provide config and initial condition for a 2D Sod shock tube.
    - x-direction: Sod Riemann problem; y-direction: uniform / transmissive.

Does NOT:
    - Run the solver.
"""

from __future__ import annotations
import numpy as np

from ..config import CFDConfig
from ..variables.conversion import primitive_to_conservative


def sod_2d_config() -> CFDConfig:
    """Return a CFDConfig for the 2D Sod shock tube."""
    return CFDConfig(
        nx=200,
        ny=50,
        xmin=0.0,
        xmax=1.0,
        ymin=0.0,
        ymax=0.25,
        gamma=1.4,
        cfl=0.5,
        ng=2,
        final_time=0.2,
        bc_x="transmissive",
        bc_y="transmissive",
        flux_type="rusanov",
        reconstruction="piecewise_constant",
        time_integrator="euler",
    )


def sod_2d_ic(
    nxt: int,
    nyt: int,
    x_center: float = 0.5,
    gamma: float = 1.4,
) -> np.ndarray:
    """Sod shock tube initial condition on a 2D grid.

    Left (x < x_center): rho=1, u=0, v=0, p=1
    Right (x >= x_center): rho=0.125, u=0, v=0, p=0.1

    Parameters
    ----------
    nxt, nyt : int
        Total grid sizes including ghost cells.
    x_center : float
        Position of the diaphragm.
    gamma : float

    Returns
    -------
    U : np.ndarray, shape (4, nyt, nxt)
    """
    rho = np.where(
        np.linspace(0, 1, nxt)[np.newaxis, :] < x_center,
        1.0,
        0.125,
    )
    u = np.zeros((nyt, nxt))
    v = np.zeros((nyt, nxt))
    p = np.where(
        np.linspace(0, 1, nxt)[np.newaxis, :] < x_center,
        1.0,
        0.1,
    )
    rho = np.broadcast_to(rho, (nyt, nxt)).copy()
    p = np.broadcast_to(p, (nyt, nxt)).copy()
    return primitive_to_conservative(rho, u, v, p, gamma)
