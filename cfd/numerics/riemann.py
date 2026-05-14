"""Riemann solvers / numerical flux functions.

Responsibilities:
    - Compute numerical flux at cell interfaces.
    - Currently implements Rusanov (local Lax-Friedrichs).

Does NOT:
    - Perform reconstruction (see reconstruction.py).
"""

from __future__ import annotations
import numpy as np

from ..constants import GAMMA
from ..physics.fluxes import euler_flux_x, euler_flux_y
from ..physics.wavespeeds import max_wavespeed


def _local_wavespeed_x(UL: np.ndarray, UR: np.ndarray, gamma: float) -> np.ndarray:
    """Max wave speed at each x-interface: max(|u_L|+c_L, |u_R|+c_R)."""
    rhoL, uL = UL[0], UL[1] / UL[0]
    pL = (gamma - 1.0) * (UL[3] - 0.5 * rhoL * (uL**2 + (UL[2] / rhoL)**2))
    cL = np.sqrt(gamma * np.abs(pL) / rhoL)

    rhoR, uR = UR[0], UR[1] / UR[0]
    pR = (gamma - 1.0) * (UR[3] - 0.5 * rhoR * (uR**2 + (UR[2] / rhoR)**2))
    cR = np.sqrt(gamma * np.abs(pR) / rhoR)

    return np.maximum(np.abs(uL) + cL, np.abs(uR) + cR)


def _local_wavespeed_y(UL: np.ndarray, UR: np.ndarray, gamma: float) -> np.ndarray:
    """Max wave speed at each y-interface: max(|v_L|+c_L, |v_R|+c_R)."""
    rhoL, vL = UL[0], UL[2] / UL[0]
    pL = (gamma - 1.0) * (UL[3] - 0.5 * rhoL * ((UL[1] / rhoL)**2 + vL**2))
    cL = np.sqrt(gamma * np.abs(pL) / rhoL)

    rhoR, vR = UR[0], UR[2] / UR[0]
    pR = (gamma - 1.0) * (UR[3] - 0.5 * rhoR * ((UR[1] / rhoR)**2 + vR**2))
    cR = np.sqrt(gamma * np.abs(pR) / rhoR)

    return np.maximum(np.abs(vL) + cL, np.abs(vR) + cR)


def rusanov_flux_x(
    UL: np.ndarray,
    UR: np.ndarray,
    gamma: float = GAMMA,
) -> np.ndarray:
    """Rusanov (local Lax-Friedrichs) numerical flux in x.

    F_num = 0.5 * (F(UL) + F(UR)) - 0.5 * smax * (UR - UL)

    Parameters
    ----------
    UL, UR : np.ndarray, shape (4, nyt, nxt-1)
        Left and right states at x-interfaces.
    gamma : float

    Returns
    -------
    Fnum : np.ndarray, shape (4, nyt, nxt-1)
    """
    FL = euler_flux_x(UL, gamma)
    FR = euler_flux_x(UR, gamma)
    smax = _local_wavespeed_x(UL, UR, gamma)
    return 0.5 * (FL + FR) - 0.5 * smax[np.newaxis] * (UR - UL)


def rusanov_flux_y(
    UL: np.ndarray,
    UR: np.ndarray,
    gamma: float = GAMMA,
) -> np.ndarray:
    """Rusanov (local Lax-Friedrichs) numerical flux in y.

    G_num = 0.5 * (G(UL) + G(UR)) - 0.5 * smax * (UR - UL)

    Parameters
    ----------
    UL, UR : np.ndarray, shape (4, nyt-1, nxt)
        Left (bottom) and right (top) states at y-interfaces.
    gamma : float

    Returns
    -------
    Gnum : np.ndarray, shape (4, nyt-1, nxt)
    """
    GL = euler_flux_y(UL, gamma)
    GR = euler_flux_y(UR, gamma)
    smax = _local_wavespeed_y(UL, UR, gamma)
    return 0.5 * (GL + GR) - 0.5 * smax[np.newaxis] * (UR - UL)
