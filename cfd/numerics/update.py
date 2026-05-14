"""Conservative variable update (forward Euler).

Responsibilities:
    - Compute the net flux divergence and update U by one time step.
    - Apply the update only to interior cells.

Does NOT:
    - Compute dt (see timestep.py).
    - Handle boundary conditions (see boundary/).
"""

from __future__ import annotations
import numpy as np

from ..constants import GAMMA
from .reconstruction import reconstruct
from .riemann import rusanov_flux_x, rusanov_flux_y


def euler_update(
    U: np.ndarray,
    dx: float,
    dy: float,
    dt: float,
    ng: int,
    gamma: float = GAMMA,
    flux_type: str = "rusanov",
    reconstruction: str = "piecewise_constant",
) -> np.ndarray:
    """Forward Euler update: U^{n+1} = U^n - dt * (dF/dx + dG/dy).

    Operates on interior cells only.  Ghost cells should already be filled.

    Parameters
    ----------
    U : np.ndarray, shape (4, nyt, nxt)
        Conservative variables (will be modified in-place and returned).
    dx, dy : float
        Cell sizes.
    dt : float
        Time step.
    ng : int
        Ghost-cell layers.
    gamma : float
    flux_type : str
        "rusanov" (only option for now).
    reconstruction : str
        "piecewise_constant" (only option for now).

    Returns
    -------
    U : np.ndarray
        Updated conservative variables (same array, modified in-place).
    """
    # --- x-direction fluxes ---
    UL_x, UR_x = reconstruct(U, ng, method=reconstruction)
    Fnum = rusanov_flux_x(UL_x, UR_x, gamma)

    # --- y-direction fluxes ---
    UL_y = U[:, :-1, :].copy()
    UR_y = U[:, 1:, :].copy()
    Gnum = rusanov_flux_y(UL_y, UR_y, gamma)

    # Flux divergence for interior cells.
    # x-flux: Fnum has shape (4, nyt, nxt-1). Interior in x is [ng:-ng].
    # For cell (j, i), dF/dx = (F[j, i] - F[j, i-1]) / dx
    # Fnum[:, j, k] is the flux at interface between cell k and cell k+1.
    # So for interior cell i (with ng offset), fluxes are Fnum[:, j, i+ng-1] and Fnum[:, j, i+ng]
    dFdx = (Fnum[:, ng:-ng, ng:U.shape[2] - ng] -
            Fnum[:, ng:-ng, ng - 1:U.shape[2] - ng - 1]) / dx

    # y-flux: Gnum has shape (4, nyt-1, nxt). Interior in y is [ng:-ng].
    dGdy = (Gnum[:, ng:U.shape[1] - ng, ng:-ng] -
            Gnum[:, ng - 1:U.shape[1] - ng - 1, ng:-ng]) / dy

    # Update interior cells only.
    s = (slice(None), slice(ng, -ng), slice(ng, -ng))
    U[s] = U[s] - dt * (dFdx + dGdy)

    return U
