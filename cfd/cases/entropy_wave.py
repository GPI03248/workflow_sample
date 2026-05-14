"""2D advected entropy wave — analytic validation case for Euler solver.

Responsibilities:
    - Provide an exact solution for the 2D compressible Euler equations.
    - The entropy wave is advected at constant velocity with periodic BCs.
    - Density has a sinusoidal perturbation; pressure and velocity are constant.

Does NOT:
    - Run the solver.

Analytic solution:
    rho(x,y,t) = rho0 + eps * sin(2*pi*(kx*(x - u0*t) + ky*(y - v0*t)))
    u(x,y,t) = u0
    v(x,y,t) = v0
    p(x,y,t) = p0
    E = p0/(gamma-1) + 0.5*rho*(u0^2 + v0^2)
"""

from __future__ import annotations
from dataclasses import dataclass

import numpy as np

from ..config import CFDConfig
from ..variables.conversion import primitive_to_conservative
from ..constants import GAMMA


@dataclass
class EntropyWaveParams:
    """Parameters for the advected entropy wave."""
    rho0: float = 1.0
    eps: float = 0.1
    u0: float = 1.0
    v0: float = 0.5
    p0: float = 1.0
    kx: int = 1
    ky: int = 1
    gamma: float = GAMMA


def entropy_wave_config(params: EntropyWaveParams | None = None) -> CFDConfig:
    """Return a CFDConfig for the entropy wave validation case."""
    return CFDConfig(
        nx=64,
        ny=64,
        xmin=0.0,
        xmax=1.0,
        ymin=0.0,
        ymax=1.0,
        gamma=params.gamma if params else GAMMA,
        cfl=0.4,
        ng=2,
        final_time=0.1,
        bc_x="periodic",
        bc_y="periodic",
        flux_type="rusanov",
        reconstruction="piecewise_constant",
        time_integrator="euler",
    )


def entropy_wave_primitive(
    X: np.ndarray,
    Y: np.ndarray,
    t: float = 0.0,
    params: EntropyWaveParams | None = None,
) -> np.ndarray:
    """Compute primitive variables for the entropy wave at time *t*.

    Parameters
    ----------
    X, Y : np.ndarray
        2-D coordinate arrays, shape (nyt, nxt).
    t : float
    params : EntropyWaveParams or None

    Returns
    -------
    V : np.ndarray, shape (4, nyt, nxt)
        Primitive variables [rho, u, v, p].
    """
    p = params or EntropyWaveParams()
    phase = 2.0 * np.pi * (p.kx * (X - p.u0 * t) + p.ky * (Y - p.v0 * t))
    rho = p.rho0 + p.eps * np.sin(phase)
    u = np.full_like(X, p.u0)
    v = np.full_like(Y, p.v0)
    pres = np.full_like(X, p.p0)
    return np.array([rho, u, v, pres])


def entropy_wave_conservative(
    X: np.ndarray,
    Y: np.ndarray,
    t: float = 0.0,
    params: EntropyWaveParams | None = None,
) -> np.ndarray:
    """Compute conservative variables for the entropy wave at time *t*.

    Returns
    -------
    U : np.ndarray, shape (4, nyt, nxt)
    """
    p = params or EntropyWaveParams()
    V = entropy_wave_primitive(X, Y, t, p)
    return primitive_to_conservative(V[0], V[1], V[2], V[3], p.gamma)


def entropy_wave_exact_solution(
    mesh,
    t: float,
    params: EntropyWaveParams | None = None,
) -> np.ndarray:
    """Compute exact conservative solution on *mesh* at time *t*.

    Parameters
    ----------
    mesh : StructuredMesh2D
    t : float
    params : EntropyWaveParams or None

    Returns
    -------
    U_exact : np.ndarray, shape (4, nyt, nxt)
    """
    X, Y = mesh.cell_centers_2d()
    return entropy_wave_conservative(X, Y, t, params)


def entropy_wave_ic(
    nxt: int,
    nyt: int,
    gamma: float = GAMMA,
    params: EntropyWaveParams | None = None,
) -> np.ndarray:
    """Initial condition compatible with run_solver's IC signature.

    Parameters
    ----------
    nxt, nyt : int
        Total grid sizes including ghost cells.
    gamma : float
    params : EntropyWaveParams or None

    Returns
    -------
    U : np.ndarray, shape (4, nyt, nxt)
    """
    p = params or EntropyWaveParams()
    # Build coordinate arrays including ghost cells.
    # We need xmin, xmax etc. We reconstruct from the convention used
    # by StructuredMesh2D: ng=2, domain [0,1) x [0,1).
    # The IC function only gets nxt, nyt — we derive dx from the assumption
    # that interior is [0,1). This matches entropy_wave_config().
    ng = 2  # matches the config
    nx_int = nxt - 2 * ng
    ny_int = nyt - 2 * ng
    dx = 1.0 / nx_int
    dy = 1.0 / ny_int
    x = np.linspace(-(ng - 0.5) * dx, 1.0 + (ng - 0.5) * dx, nxt)
    y = np.linspace(-(ng - 0.5) * dy, 1.0 + (ng - 0.5) * dy, nyt)
    X, Y = np.meshgrid(x, y)
    return entropy_wave_conservative(X, Y, t=0.0, params=p)
