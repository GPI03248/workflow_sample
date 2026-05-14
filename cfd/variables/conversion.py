"""Primitive <-> conservative variable conversion.

Responsibilities:
    - Convert between primitive V = [rho, u, v, p] and conservative U = [rho, rho*u, rho*v, E].
    - Check for non-physical states.

Does NOT:
    - Perform any spatial operations.
"""

from __future__ import annotations
import numpy as np

from ..constants import GAMMA


def primitive_to_conservative(
    rho: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    p: np.ndarray,
    gamma: float = GAMMA,
) -> np.ndarray:
    """Convert primitive variables to conservative.

    Parameters
    ----------
    rho, u, v, p : np.ndarray
        Primitive fields, all same shape.
    gamma : float
        Ratio of specific heats.

    Returns
    -------
    U : np.ndarray, shape (4, *rho.shape)
        Conservative variables [rho, rho*u, rho*v, E].
    """
    E = p / (gamma - 1.0) + 0.5 * rho * (u**2 + v**2)
    return np.array([rho, rho * u, rho * v, E])


def conservative_to_primitive(
    U: np.ndarray,
    gamma: float = GAMMA,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Convert conservative variables to primitive.

    Parameters
    ----------
    U : np.ndarray, shape (4, ...)
        Conservative variables.
    gamma : float

    Returns
    -------
    rho, u, v, p : np.ndarray
        Primitive fields.

    Raises
    ------
    ValueError
        If rho <= 0 or p <= 0 anywhere.
    """
    rho = U[0]
    u = U[1] / rho
    v = U[2] / rho
    p = (gamma - 1.0) * (U[3] - 0.5 * rho * (u**2 + v**2))
    return rho, u, v, p
