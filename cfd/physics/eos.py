"""Equation of state for ideal gas.

Responsibilities:
    - Compute pressure, sound speed, total energy from primitive or conservative variables.

Does NOT:
    - Perform any spatial operations.
"""

from __future__ import annotations
import numpy as np

from ..constants import GAMMA


def pressure(rho: np.ndarray, u: np.ndarray, v: np.ndarray, E: np.ndarray,
             gamma: float = GAMMA) -> np.ndarray:
    """Compute pressure from conservative variables.

    p = (gamma - 1) * (E - 0.5 * rho * (u^2 + v^2))
    """
    return (gamma - 1.0) * (E - 0.5 * rho * (u**2 + v**2))


def sound_speed(rho: np.ndarray, p: np.ndarray, gamma: float = GAMMA) -> np.ndarray:
    """Compute sound speed c = sqrt(gamma * p / rho).

    Raises
    ------
    ValueError
        If rho or p contain non-positive values.
    """
    if np.any(rho <= 0):
        raise ValueError("Non-physical density detected (rho <= 0).")
    if np.any(p <= 0):
        raise ValueError("Non-physical pressure detected (p <= 0).")
    return np.sqrt(gamma * p / rho)


def total_energy(rho: np.ndarray, u: np.ndarray, v: np.ndarray, p: np.ndarray,
                 gamma: float = GAMMA) -> np.ndarray:
    """Compute total energy E from primitive variables.

    E = p / (gamma - 1) + 0.5 * rho * (u^2 + v^2)
    """
    return p / (gamma - 1.0) + 0.5 * rho * (u**2 + v**2)
