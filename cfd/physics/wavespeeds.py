"""Wave-speed estimation for CFL calculation.

Responsibilities:
    - Compute maximum wave speed |u| + c or |v| + c for the entire domain.

Does NOT:
    - Compute the actual dt (see numerics/timestep.py).
"""

from __future__ import annotations
import numpy as np

from ..constants import GAMMA


def max_wavespeed(
    U: np.ndarray,
    gamma: float = GAMMA,
) -> tuple[float, float]:
    """Return (max_sx, max_sy) where sx = |u| + c, sy = |v| + c.

    Parameters
    ----------
    U : np.ndarray, shape (4, nyt, nxt)
        Conservative variables.
    gamma : float

    Returns
    -------
    max_sx, max_sy : float
    """
    rho = U[0]
    u = U[1] / rho
    v = U[2] / rho
    p = (gamma - 1.0) * (U[3] - 0.5 * rho * (u**2 + v**2))
    c = np.sqrt(gamma * np.abs(p) / rho)
    max_sx = float(np.max(np.abs(u) + c))
    max_sy = float(np.max(np.abs(v) + c))
    return max_sx, max_sy
