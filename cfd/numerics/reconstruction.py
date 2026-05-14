"""Variable reconstruction at cell interfaces.

Responsibilities:
    - Reconstruct left/right states at cell interfaces.
    - Implements piecewise-constant (1st order) and MUSCL (2nd order).
    - MUSCL reconstructs in primitive variables for stability.

Does NOT:
    - Apply limiters directly (limiter is passed in).
"""

from __future__ import annotations
import numpy as np

from ..variables.conversion import conservative_to_primitive, primitive_to_conservative
from ..constants import GAMMA


def reconstruct(
    U: np.ndarray,
    ng: int,
    method: str = "piecewise_constant",
    limiter_name: str = "minmod",
    gamma: float = GAMMA,
) -> tuple[np.ndarray, np.ndarray]:
    """Reconstruct left and right states at x-interfaces.

    Parameters
    ----------
    U : np.ndarray, shape (4, nyt, nxt)
    ng : int
    method : str
        "piecewise_constant" or "muscl".
    limiter_name : str
        Limiter for MUSCL: "minmod" or "vanleer".
    gamma : float

    Returns
    -------
    UL, UR : np.ndarray, shape (4, nyt, nxt-1)
    """
    if method == "piecewise_constant":
        return U[:, :, :-1].copy(), U[:, :, 1:].copy()
    elif method == "muscl":
        return _muscl_x(U, ng, limiter_name, gamma)
    else:
        raise ValueError(f"Unknown reconstruction method: {method}")


def reconstruct_y(
    U: np.ndarray,
    ng: int,
    method: str = "piecewise_constant",
    limiter_name: str = "minmod",
    gamma: float = GAMMA,
) -> tuple[np.ndarray, np.ndarray]:
    """Reconstruct bottom/top states at y-interfaces.

    Returns
    -------
    UB, UT : np.ndarray, shape (4, nyt-1, nxt)
    """
    if method == "piecewise_constant":
        return U[:, :-1, :].copy(), U[:, 1:, :].copy()
    elif method == "muscl":
        return _muscl_y(U, ng, limiter_name, gamma)
    else:
        raise ValueError(f"Unknown reconstruction method: {method}")


def _muscl_x(
    U: np.ndarray,
    ng: int,
    limiter_name: str,
    gamma: float,
) -> tuple[np.ndarray, np.ndarray]:
    """MUSCL reconstruction in x-direction (on primitive variables)."""
    from .limiters import get_limiter
    limiter = get_limiter(limiter_name)

    rho, u, v, p = conservative_to_primitive(U, gamma)

    UL_list, UR_list = [], []
    for W in [rho, u, v, p]:
        # W shape: (nyt, nxt)
        dW_fwd = W[:, 1:] - W[:, :-1]  # shape (nyt, nxt-1)
        # slope at cell k = limiter(dW_fwd[k-1], dW_fwd[k])
        slope = limiter(dW_fwd[:, :-1], dW_fwd[:, 1:])  # shape (nyt, nxt-2)
        slope = np.pad(slope, ((0, 0), (1, 1)), mode='constant', constant_values=0.0)

        UL_w = W[:, :-1] + 0.5 * slope[:, :-1]  # (nyt, nxt-1)
        UR_w = W[:, 1:] - 0.5 * slope[:, 1:]    # (nyt, nxt-1)
        UL_list.append(UL_w)
        UR_list.append(UR_w)

    rhoL, uL, vL, pL = UL_list
    rhoR, uR, vR, pR = UR_list

    # Safety: ensure rho > 0 and p > 0, fallback to piecewise constant where violated.
    safeL = (rhoL > 1e-10) & (pL > 1e-10)
    safeR = (rhoR > 1e-10) & (pR > 1e-10)
    if not np.all(safeL) or not np.all(safeR):
        rhoL = np.where(safeL, rhoL, rho[:, :-1])
        uL = np.where(safeL, uL, u[:, :-1])
        vL = np.where(safeL, vL, v[:, :-1])
        pL = np.where(safeL, pL, p[:, :-1])
        rhoR = np.where(safeR, rhoR, rho[:, 1:])
        uR = np.where(safeR, uR, u[:, 1:])
        vR = np.where(safeR, vR, v[:, 1:])
        pR = np.where(safeR, pR, p[:, 1:])

    UL = primitive_to_conservative(rhoL, uL, vL, pL, gamma)
    UR = primitive_to_conservative(rhoR, uR, vR, pR, gamma)
    return UL, UR


def _muscl_y(
    U: np.ndarray,
    ng: int,
    limiter_name: str,
    gamma: float,
) -> tuple[np.ndarray, np.ndarray]:
    """MUSCL reconstruction in y-direction (on primitive variables)."""
    from .limiters import get_limiter
    limiter = get_limiter(limiter_name)

    rho, u, v, p = conservative_to_primitive(U, gamma)

    UB_list, UT_list = [], []
    for W in [rho, u, v, p]:
        dW_fwd = W[1:, :] - W[:-1, :]  # (nyt-1, nxt)
        slope = limiter(dW_fwd[:-1, :], dW_fwd[1:, :])  # (nyt-2, nxt)
        slope = np.pad(slope, ((1, 1), (0, 0)), mode='constant', constant_values=0.0)

        UB_w = W[:-1, :] + 0.5 * slope[:-1, :]
        UT_w = W[1:, :] - 0.5 * slope[1:, :]
        UB_list.append(UB_w)
        UT_list.append(UT_w)

    rhoB, uB, vB, pB = UB_list
    rhoT, uT, vT, pT = UT_list

    safeB = (rhoB > 1e-10) & (pB > 1e-10)
    safeT = (rhoT > 1e-10) & (pT > 1e-10)
    if not np.all(safeB) or not np.all(safeT):
        rhoB = np.where(safeB, rhoB, rho[:-1, :])
        uB = np.where(safeB, uB, u[:-1, :])
        vB = np.where(safeB, vB, v[:-1, :])
        pB = np.where(safeB, pB, p[:-1, :])
        rhoT = np.where(safeT, rhoT, rho[1:, :])
        uT = np.where(safeT, uT, u[1:, :])
        vT = np.where(safeT, vT, v[1:, :])
        pT = np.where(safeT, pT, p[1:, :])

    UB = primitive_to_conservative(rhoB, uB, vB, pB, gamma)
    UT = primitive_to_conservative(rhoT, uT, vT, pT, gamma)
    return UB, UT
