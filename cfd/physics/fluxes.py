"""Euler equation physical flux functions.

Responsibilities:
    - Compute the physical flux vectors F(U) and G(U) for the 2D Euler equations.

Does NOT:
    - Compute numerical fluxes (see cfd/numerics/riemann.py).
"""

from __future__ import annotations
import numpy as np

from ..constants import GAMMA


def euler_flux_x(U: np.ndarray, gamma: float = GAMMA) -> np.ndarray:
    """Physical flux in x-direction.

    F = [rho*u, rho*u^2 + p, rho*u*v, u*(E + p)]

    Parameters
    ----------
    U : np.ndarray, shape (4, ...)
        Conservative variables [rho, rho*u, rho*v, E].
    gamma : float

    Returns
    -------
    F : np.ndarray, shape (4, ...)
    """
    rho = U[0]
    rhou = U[1]
    rhov = U[2]
    E = U[3]
    u = rhou / rho
    v = rhov / rho
    p = (gamma - 1.0) * (E - 0.5 * rho * (u**2 + v**2))
    F = np.empty_like(U)
    F[0] = rhou
    F[1] = rhou * u + p
    F[2] = rhov * u
    F[3] = u * (E + p)
    return F


def euler_flux_y(U: np.ndarray, gamma: float = GAMMA) -> np.ndarray:
    """Physical flux in y-direction.

    G = [rho*v, rho*u*v, rho*v^2 + p, v*(E + p)]

    Parameters
    ----------
    U : np.ndarray, shape (4, ...)
    gamma : float

    Returns
    -------
    G : np.ndarray, shape (4, ...)
    """
    rho = U[0]
    rhou = U[1]
    rhov = U[2]
    E = U[3]
    u = rhou / rho
    v = rhov / rho
    p = (gamma - 1.0) * (E - 0.5 * rho * (u**2 + v**2))
    G = np.empty_like(U)
    G[0] = rhov
    G[1] = rhou * v
    G[2] = rhov * v + p
    G[3] = v * (E + p)
    return G
