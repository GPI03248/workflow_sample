"""Numerical schemes for 1D scalar advection  du/dt + a * du/dx = 0."""

import numpy as np

# Default wave speed (positive -> right-travelling wave).
WAVE_SPEED: float = 1.0


def upwind(u: np.ndarray, cfl: float) -> np.ndarray:
    """First-order upwind scheme (explicit Euler, a > 0).

    u_new[j] = u[j] - cfl * (u[j] - u[j-1])

    Uses periodic boundaries via np.roll.
    """
    u_left = np.roll(u, 1)
    return u - cfl * (u - u_left)


def lax_wendroff(u: np.ndarray, cfl: float) -> np.ndarray:
    """Second-order Lax-Wendroff scheme (a > 0).

    u_new[j] = u[j]
        - 0.5*cfl*(u[j+1] - u[j-1])
        + 0.5*cfl^2*(u[j+1] - 2*u[j] + u[j-1])

    Uses periodic boundaries via np.roll.
    """
    u_right = np.roll(u, -1)
    u_left = np.roll(u, 1)
    return (u
            - 0.5 * cfl * (u_right - u_left)
            + 0.5 * cfl**2 * (u_right - 2.0 * u + u_left))


# ---- registry of known schemes -------------------------------------------
_SCHEMES: dict[str, callable] = {
    "upwind": upwind,
    "lax_wendroff": lax_wendroff,
}


def step(u: np.ndarray, cfl: float, scheme: str = "upwind") -> np.ndarray:
    """Advance *u* by one time-step using the named *scheme*.

    Parameters
    ----------
    u : np.ndarray
        Current solution array (1-D).
    cfl : float
        CFL number  a * dt / dx.  Must satisfy 0 <= cfl <= 1.
    scheme : str
        Name of the numerical scheme.
        Supported: "upwind", "lax_wendroff".

    Returns
    -------
    np.ndarray
        Solution after one time-step (same shape as *u*).

    Raises
    ------
    ValueError
        If *scheme* is not recognised or *cfl* is outside [0, 1].
    """
    if not (0.0 <= cfl <= 1.0):
        raise ValueError(
            f"CFL must satisfy 0 <= cfl <= 1, got {cfl}. "
            "Unstable CFL leads to divergent results."
        )
    if scheme not in _SCHEMES:
        raise ValueError(
            f"Unknown scheme '{scheme}'. Available: {sorted(_SCHEMES)}"
        )
    return _SCHEMES[scheme](u, cfl)
