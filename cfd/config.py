"""Solver configuration dataclass.

Responsibilities:
    - Hold all solver parameters in one place.
    - Provide sensible defaults for 2D Euler on a uniform Cartesian grid.

Does NOT:
    - Perform any computation.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CFDConfig:
    """Configuration for the 2D Euler solver.

    Attributes
    ----------
    nx, ny : int
        Number of interior cells in x and y.
    xmin, xmax : float
        Domain extents in x.
    ymin, ymax : float
        Domain extents in y.
    gamma : float
        Ratio of specific heats (default 1.4 for air).
    cfl : float
        CFL number for time-step calculation (0 < cfl <= 1).
    ng : int
        Number of ghost-cell layers (default 2 for MUSCL).
    final_time : float
        Target end time for the simulation.
    n_output : int
        Number of intermediate outputs (0 = final only).
    bc_x : str
        Boundary type in x: "periodic", "transmissive", "reflective".
    bc_y : str
        Boundary type in y.
    flux_type : str
        Numerical flux: "rusanov".
    reconstruction : str
        Reconstruction method: "piecewise_constant".
    time_integrator : str
        Time integration: "euler".
    """

    nx: int = 100
    ny: int = 50
    xmin: float = 0.0
    xmax: float = 1.0
    ymin: float = 0.0
    ymax: float = 0.5
    gamma: float = 1.4
    cfl: float = 0.5
    ng: int = 2
    final_time: float = 0.1
    n_output: int = 0
    bc_x: str = "transmissive"
    bc_y: str = "transmissive"
    flux_type: str = "rusanov"
    reconstruction: str = "piecewise_constant"
    time_integrator: str = "euler"
