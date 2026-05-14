"""CFL-based time-step computation.

Responsibilities:
    - Compute dt from CFL condition: dt = cfl * min(dx, dy) / max_wavespeed.

Does NOT:
    - Advance the solution (see update.py, time_integration.py).
"""

from __future__ import annotations
import numpy as np

from ..constants import GAMMA


def compute_dt(
    U: np.ndarray,
    dx: float,
    dy: float,
    cfl: float,
    gamma: float = GAMMA,
) -> float:
    """Compute time step from CFL condition.

    dt = cfl * min(dx, dy) / max(|u|+c, |v|+c)

    Parameters
    ----------
    U : np.ndarray, shape (4, nyt, nxt)
        Conservative variables.
    dx, dy : float
        Cell sizes.
    cfl : float
        CFL number (0 < cfl <= 1).
    gamma : float

    Returns
    -------
    dt : float

    Raises
    ------
    ValueError
        If computed dt is non-positive (non-physical state).
    """
    rho = U[0]
    u = U[1] / rho
    v = U[2] / rho
    p = (gamma - 1.0) * (U[3] - 0.5 * rho * (u**2 + v**2))
    c = np.sqrt(gamma * np.abs(p) / rho)
    max_sx = float(np.max(np.abs(u) + c))
    max_sy = float(np.max(np.abs(v) + c))
    max_s = max(max_sx, max_sy)
    if max_s <= 0:
        raise ValueError("Maximum wave speed is non-positive — non-physical state.")
    dt = cfl * min(dx, dy) / max_s
    return dt
