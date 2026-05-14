"""2D isentropic vortex — analytic validation case for Euler solver.

Responsibilities:
    - Provide an exact solution for the 2D compressible Euler equations.
    - The vortex is a smooth, nonlinear flow that is advected at constant velocity.
    - More complex than the entropy wave: velocity and density both vary.

Does NOT:
    - Run the solver.

Analytic solution:
    dx = x - (x0 + u_inf*t),  dy = y - (y0 + v_inf*t),  r2 = dx^2 + dy^2
    du = -beta/(2*pi) * exp(0.5*(1 - r2)) * dy
    dv =  beta/(2*pi) * exp(0.5*(1 - r2)) * dx
    T = 1 - ((gamma-1)*beta^2)/(8*gamma*pi^2) * exp(1 - r2)
    rho = T^(1/(gamma-1))
    p = rho^gamma
"""

from __future__ import annotations
from dataclasses import dataclass

import numpy as np

from ..config import CFDConfig
from ..variables.conversion import primitive_to_conservative
from ..constants import GAMMA


@dataclass
class IsentropicVortexParams:
    """Parameters for the isentropic vortex."""
    rho_inf: float = 1.0
    u_inf: float = 1.0
    v_inf: float = 1.0
    p_inf: float = 1.0
    gamma: float = GAMMA
    beta: float = 5.0
    x0: float = 5.0
    y0: float = 5.0


def isentropic_vortex_config(params: IsentropicVortexParams | None = None) -> CFDConfig:
    """Return a CFDConfig for the isentropic vortex."""
    return CFDConfig(
        nx=64,
        ny=64,
        xmin=0.0,
        xmax=10.0,
        ymin=0.0,
        ymax=10.0,
        gamma=params.gamma if params else GAMMA,
        cfl=0.4,
        ng=2,
        final_time=0.5,
        bc_x="periodic",
        bc_y="periodic",
        flux_type="rusanov",
        reconstruction="piecewise_constant",
        time_integrator="euler",
    )


def isentropic_vortex_primitive(
    X: np.ndarray,
    Y: np.ndarray,
    t: float = 0.0,
    params: IsentropicVortexParams | None = None,
) -> np.ndarray:
    """Compute primitive variables for the isentropic vortex at time *t*.

    Returns
    -------
    V : np.ndarray, shape (4, ...)
        [rho, u, v, p]
    """
    p = params or IsentropicVortexParams()
    beta = p.beta
    gamma = p.gamma

    xc = p.x0 + p.u_inf * t
    yc = p.y0 + p.v_inf * t
    dx = X - xc
    dy = Y - yc
    r2 = dx**2 + dy**2

    du = -beta / (2.0 * np.pi) * np.exp(0.5 * (1.0 - r2)) * dy
    dv =  beta / (2.0 * np.pi) * np.exp(0.5 * (1.0 - r2)) * dx

    T = 1.0 - ((gamma - 1.0) * beta**2) / (8.0 * gamma * np.pi**2) * np.exp(1.0 - r2)

    rho = p.rho_inf * T ** (1.0 / (gamma - 1.0))
    u = p.u_inf + du
    v = p.v_inf + dv
    pres = p.p_inf * (rho / p.rho_inf) ** gamma

    return np.array([rho, u, v, pres])


def isentropic_vortex_conservative(
    X: np.ndarray,
    Y: np.ndarray,
    t: float = 0.0,
    params: IsentropicVortexParams | None = None,
) -> np.ndarray:
    """Compute conservative variables. Returns U, shape (4, ...)."""
    p = params or IsentropicVortexParams()
    V = isentropic_vortex_primitive(X, Y, t, p)
    return primitive_to_conservative(V[0], V[1], V[2], V[3], p.gamma)


def isentropic_vortex_exact_solution(
    mesh,
    t: float,
    params: IsentropicVortexParams | None = None,
) -> np.ndarray:
    """Exact conservative solution on *mesh* at time *t*."""
    X, Y = mesh.cell_centers_2d()
    return isentropic_vortex_conservative(X, Y, t, params)


def isentropic_vortex_ic(
    nxt: int,
    nyt: int,
    gamma: float = GAMMA,
    params: IsentropicVortexParams | None = None,
) -> np.ndarray:
    """IC compatible with run_solver. Uses domain [0,10]x[0,10], ng=2."""
    p = params or IsentropicVortexParams()
    ng = 2
    nx_int = nxt - 2 * ng
    ny_int = nyt - 2 * ng
    dx = 10.0 / nx_int
    dy = 10.0 / ny_int
    x = np.linspace(-(ng - 0.5) * dx, 10.0 + (ng - 0.5) * dx, nxt)
    y = np.linspace(-(ng - 0.5) * dy, 10.0 + (ng - 0.5) * dy, nyt)
    X, Y = np.meshgrid(x, y)
    return isentropic_vortex_conservative(X, Y, t=0.0, params=p)
