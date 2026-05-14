"""Variable reconstruction at cell interfaces.

Responsibilities:
    - Reconstruct left/right states at cell interfaces from cell-centred values.
    - Currently implements piecewise-constant (1st order).
    - MUSCL interface is reserved for future extension.

Does NOT:
    - Apply limiters (see limiters.py).
"""

from __future__ import annotations
import numpy as np


def reconstruct(
    U: np.ndarray,
    ng: int,
    method: str = "piecewise_constant",
) -> tuple[np.ndarray, np.ndarray]:
    """Reconstruct left and right states at x-interfaces.

    For piecewise constant, UL[j+1/2] = U[j], UR[j+1/2] = U[j+1].

    Parameters
    ----------
    U : np.ndarray, shape (4, nyt, nxt)
        Conservative variables with ghost cells filled.
    ng : int
        Ghost-cell layers.
    method : str
        "piecewise_constant" (default) or "muscl" (reserved).

    Returns
    -------
    UL, UR : np.ndarray, shape (4, nyt, nxt-1)
        Left and right states at each x-interface.
    """
    if method == "piecewise_constant":
        # Interface j+1/2: left state = cell j, right state = cell j+1
        UL = U[:, :, :-1].copy()
        UR = U[:, :, 1:].copy()
        return UL, UR
    elif method == "muscl":
        raise NotImplementedError("MUSCL reconstruction not yet implemented. Use piecewise_constant.")
    else:
        raise ValueError(f"Unknown reconstruction method: {method}")
