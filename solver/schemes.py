"""Numerical schemes for 1D scalar advection  du/dt + a * du/dx = 0."""

import numpy as np

# Default wave speed (positive → right-travelling wave).
WAVE_SPEED: float = 1.0


def upwind(u: np.ndarray, cfl: float) -> np.ndarray:
    """First-order upwind scheme (explicit Euler, a > 0).

    u_new[j] = u[j] - cfl * (u[j] - u[j-1])

    Uses periodic boundaries via np.roll.
    """
    u_left = np.roll(u, 1)
    return u - cfl * (u - u_left)


# ---- registry of known schemes -------------------------------------------
_SCHEMES: dict[str, callable] = {
    "upwind": upwind,
}


def step(u: np.ndarray, cfl: float, scheme: str = "upwind") -> np.ndarray:
    """Advance *u* by one time-step using the named *scheme*.

    Parameters
    ----------
    u : np.ndarray
        Current solution array (1-D).
    cfl : float
        CFL number  a * dt / dx.  Must satisfy stability constraints of the
        chosen scheme (e.g. 0 < cfl <= 1 for upwind).
    scheme : str
        Name of the numerical scheme.  Currently supported: "upwind".

    Returns
    -------
    np.ndarray
        Solution after one time-step (same shape as *u*).

    Raises
    ------
    ValueError
        If *scheme* is not recognised.
    """
    if scheme not in _SCHEMES:
        raise ValueError(
            f"Unknown scheme '{scheme}'. Available: {sorted(_SCHEMES)}"
        )
    return _SCHEMES[scheme](u, cfl)
