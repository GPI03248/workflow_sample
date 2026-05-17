"""Spatial discretisation and conservative variable update.

Responsibilities:
    - Compute the spatial residual L(U) = -(dF/dx + dG/dy).
    - Apply forward Euler or return residual for multi-stage methods.
    - Apply the update only to interior cells.

Does NOT:
    - Compute dt (see timestep.py).
    - Handle boundary conditions (see boundary/).
    - Implement time integration loops (see time_integration.py).
"""

from __future__ import annotations
import numpy as np

from ..constants import GAMMA
from .reconstruction import reconstruct, reconstruct_y
from .riemann import rusanov_flux_x, rusanov_flux_y, hll_flux_x, hll_flux_y


def compute_residual(
    U: np.ndarray,
    dx: float,
    dy: float,
    ng: int,
    gamma: float = GAMMA,
    flux_type: str = "rusanov",
    reconstruction: str = "piecewise_constant",
    limiter: str = "minmod",
) -> np.ndarray:
    """Compute spatial residual L(U) = -(dF/dx + dG/dy) for interior cells.

    Returns
    -------
    L : np.ndarray, shape (4, ny, nx)
        Residual for interior cells only (no ghost cells in output).
    """
    # x-direction
    UL_x, UR_x = reconstruct(
        U, ng, method=reconstruction, limiter_name=limiter, gamma=gamma
    )
    if flux_type == "rusanov":
        Fnum = rusanov_flux_x(UL_x, UR_x, gamma)
    elif flux_type == "hll":
        Fnum = hll_flux_x(UL_x, UR_x, gamma)
    else:
        raise ValueError(f"Unknown flux_type: {flux_type!r}")

    # y-direction
    UL_y, UR_y = reconstruct_y(
        U, ng, method=reconstruction, limiter_name=limiter, gamma=gamma
    )
    if flux_type == "rusanov":
        Gnum = rusanov_flux_y(UL_y, UR_y, gamma)
    elif flux_type == "hll":
        Gnum = hll_flux_y(UL_y, UR_y, gamma)
    else:
        raise ValueError(f"Unknown flux_type: {flux_type!r}")

    # Flux divergence for interior cells.
    nxt = U.shape[2]
    nyt = U.shape[1]

    dFdx = (
        Fnum[:, ng:-ng, ng : nxt - ng] - Fnum[:, ng:-ng, ng - 1 : nxt - ng - 1]
    ) / dx

    dGdy = (
        Gnum[:, ng : nyt - ng, ng:-ng] - Gnum[:, ng - 1 : nyt - ng - 1, ng:-ng]
    ) / dy

    return -(dFdx + dGdy)


def apply_euler_step(
    U: np.ndarray,
    dx: float,
    dy: float,
    dt: float,
    ng: int,
    gamma: float = GAMMA,
    flux_type: str = "rusanov",
    reconstruction: str = "piecewise_constant",
    limiter: str = "minmod",
) -> np.ndarray:
    """Apply one forward-Euler update to U in-place: U += dt * L(U).

    Returns U (same array).
    """
    L = compute_residual(U, dx, dy, ng, gamma, flux_type, reconstruction, limiter)
    s = (slice(None), slice(ng, -ng), slice(ng, -ng))
    U[s] = U[s] + dt * L
    return U


# Backward-compatible alias.
euler_update = apply_euler_step
