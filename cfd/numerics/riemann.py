"""Riemann solvers / numerical flux functions.

Responsibilities:
    - Compute numerical flux at cell interfaces.
    - Implements Rusanov (local Lax-Friedrichs) and HLL (Harten-Lax-van Leer).

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


def _roe_averages_x(
    UL: np.ndarray, UR: np.ndarray, gamma: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Roe-averaged quantities for x-direction wave speed estimates.

    Returns (u_hat, c_hat, sqrtL, sqrtR).
    """
    rhoL = UL[0]
    uL = UL[1] / rhoL
    vL = UL[2] / rhoL
    pL = (gamma - 1.0) * (UL[3] - 0.5 * rhoL * (uL**2 + vL**2))
    HL = (UL[3] + pL) / rhoL

    rhoR = UR[0]
    uR = UR[1] / rhoR
    vR = UR[2] / rhoR
    pR = (gamma - 1.0) * (UR[3] - 0.5 * rhoR * (uR**2 + vR**2))
    HR = (UR[3] + pR) / rhoR

    sqrtL = np.sqrt(rhoL)
    sqrtR = np.sqrt(rhoR)
    denom = sqrtL + sqrtR

    u_hat = (sqrtL * uL + sqrtR * uR) / denom
    H_hat = (sqrtL * HL + sqrtR * HR) / denom
    c_hat = np.sqrt(np.abs((gamma - 1.0) * (H_hat - 0.5 * u_hat**2)))

    return u_hat, c_hat, sqrtL, sqrtR


def _roe_averages_y(
    UL: np.ndarray, UR: np.ndarray, gamma: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Roe-averaged quantities for y-direction wave speed estimates.

    Returns (v_hat, c_hat, sqrtB, sqrtT).
    """
    rhoB = UL[0]
    uB = UL[1] / rhoB
    vB = UL[2] / rhoB
    pB = (gamma - 1.0) * (UL[3] - 0.5 * rhoB * (uB**2 + vB**2))
    HB = (UL[3] + pB) / rhoB

    rhoT = UR[0]
    uT = UR[1] / rhoT
    vT = UR[2] / rhoT
    pT = (gamma - 1.0) * (UR[3] - 0.5 * rhoT * (uT**2 + vT**2))
    HT = (UR[3] + pT) / rhoT

    sqrtB = np.sqrt(rhoB)
    sqrtT = np.sqrt(rhoT)
    denom = sqrtB + sqrtT

    v_hat = (sqrtB * vB + sqrtT * vT) / denom
    H_hat = (sqrtB * HB + sqrtT * HT) / denom
    c_hat = np.sqrt(np.abs((gamma - 1.0) * (H_hat - 0.5 * v_hat**2)))

    return v_hat, c_hat, sqrtB, sqrtT


def hll_flux_x(
    UL: np.ndarray,
    UR: np.ndarray,
    gamma: float = GAMMA,
) -> np.ndarray:
    """HLL (Harten-Lax-van Leer) numerical flux in x.

    Uses Roe-averaged wave speed estimates for S_L and S_R.

    Parameters
    ----------
    UL, UR : np.ndarray, shape (4, nyt, nxt-1)
        Left and right states at x-interfaces.
    gamma : float

    Returns
    -------
    Fnum : np.ndarray, shape (4, nyt, nxt-1)
    """
    # Primitive quantities for wave speeds
    rhoL = UL[0]
    uL = UL[1] / rhoL
    vL = UL[2] / rhoL
    pL = (gamma - 1.0) * (UL[3] - 0.5 * rhoL * (uL**2 + vL**2))
    cL = np.sqrt(gamma * np.abs(pL) / rhoL)

    rhoR = UR[0]
    uR = UR[1] / rhoR
    vR = UR[2] / rhoR
    pR = (gamma - 1.0) * (UR[3] - 0.5 * rhoR * (uR**2 + vR**2))
    cR = np.sqrt(gamma * np.abs(pR) / rhoR)

    # Roe averages
    u_hat, c_hat, _, _ = _roe_averages_x(UL, UR, gamma)

    # Wave speed estimates
    S_L = np.minimum(uL - cL, u_hat - c_hat)
    S_R = np.maximum(uR + cR, u_hat + c_hat)

    # Physical fluxes
    FL = euler_flux_x(UL, gamma)
    FR = euler_flux_x(UR, gamma)

    # HLL flux with epsilon guard
    dS = S_R - S_L
    eps = 1e-14

    # Default: HLL middle state
    F_hll = (S_R[np.newaxis] * FL - S_L[np.newaxis] * FR +
             S_L[np.newaxis] * S_R[np.newaxis] * (UR - UL)) / dS[np.newaxis]

    # Fallback when dS is too small
    small = np.abs(dS) < eps
    if np.any(small):
        F_avg = 0.5 * (FL + FR)
        for k in range(4):
            F_hll[k] = np.where(small, F_avg[k], F_hll[k])

    # Upwind: S_L >= 0 => FL
    left = S_L >= 0.0
    for k in range(4):
        F_hll[k] = np.where(left, FL[k], F_hll[k])

    # Upwind: S_R <= 0 => FR
    right = S_R <= 0.0
    for k in range(4):
        F_hll[k] = np.where(right, FR[k], F_hll[k])

    return F_hll


def hll_flux_y(
    UL: np.ndarray,
    UR: np.ndarray,
    gamma: float = GAMMA,
) -> np.ndarray:
    """HLL (Harten-Lax-van Leer) numerical flux in y.

    Uses Roe-averaged wave speed estimates for S_B and S_T.

    Parameters
    ----------
    UL, UR : np.ndarray, shape (4, nyt-1, nxt)
        Bottom and top states at y-interfaces.
    gamma : float

    Returns
    -------
    Gnum : np.ndarray, shape (4, nyt-1, nxt)
    """
    # Primitive quantities
    rhoB = UL[0]
    uB = UL[1] / rhoB
    vB = UL[2] / rhoB
    pB = (gamma - 1.0) * (UL[3] - 0.5 * rhoB * (uB**2 + vB**2))
    cB = np.sqrt(gamma * np.abs(pB) / rhoB)

    rhoT = UR[0]
    uT = UR[1] / rhoT
    vT = UR[2] / rhoT
    pT = (gamma - 1.0) * (UR[3] - 0.5 * rhoT * (uT**2 + vT**2))
    cT = np.sqrt(gamma * np.abs(pT) / rhoT)

    # Roe averages
    v_hat, c_hat, _, _ = _roe_averages_y(UL, UR, gamma)

    # Wave speed estimates
    S_B = np.minimum(vB - cB, v_hat - c_hat)
    S_T = np.maximum(vT + cT, v_hat + c_hat)

    # Physical fluxes
    GB = euler_flux_y(UL, gamma)
    GT = euler_flux_y(UR, gamma)

    # HLL flux with epsilon guard
    dS = S_T - S_B
    eps = 1e-14

    G_hll = (S_T[np.newaxis] * GB - S_B[np.newaxis] * GT +
             S_B[np.newaxis] * S_T[np.newaxis] * (UR - UL)) / dS[np.newaxis]

    small = np.abs(dS) < eps
    if np.any(small):
        G_avg = 0.5 * (GB + GT)
        for k in range(4):
            G_hll[k] = np.where(small, G_avg[k], G_hll[k])

    left = S_B >= 0.0
    for k in range(4):
        G_hll[k] = np.where(left, GB[k], G_hll[k])

    right = S_T <= 0.0
    for k in range(4):
        G_hll[k] = np.where(right, GT[k], G_hll[k])

    return G_hll
