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


def cfweno(u: np.ndarray, cfl: float) -> np.ndarray:
    """CFWENO3 — Compact Fully-discrete WENO, 3rd-order (a > 0).

    Implements the scalar 1D linear advection prototype from
    Zhou-Dong-Pan (2025), Eq. (30).  Single-stage, compact stencil.

    Algorithm per interface i+1/2:
      1. Reconstruct interface values u_{i+1/2} from cell-centre values
         using the 4th-order centred stencil:
             u_{i+1/2} = (-u_{i-1} + 7u_i + 7u_{i+1} - u_{i+2}) / 12
      2. Compute cell-average at interface (Eq. 30):
             ubar_{i+1/2} = u_{i+1/2}
                 - nu*(u_{i+1/2} - u_i)
                 - nu*(1 - nu)*(u_{i-1/2} - 2*u_i + u_{i+1/2})
         where nu = cfl = tau*a/h.
      3. Numerical flux (linear advection, a = const):
             fhat_{i+1/2} = a * ubar_{i+1/2}
      4. Conservative update (Eq. 25):
             u_i^{n+1} = u_i - cfl*(ubar_{i+1/2} - ubar_{i-1/2})

    Uses periodic boundaries via np.roll.
    """
    nu = cfl  # nu = tau*a/h = cfl

    # Step 1: interface values from 4th-order centred interpolation.
    # u_{i+1/2} = (-u_{i-1} + 7u_i + 7u_{i+1} - u_{i+2}) / 12
    u_im1 = np.roll(u, 1)    # u_{i-1}
    u_ip1 = np.roll(u, -1)   # u_{i+1}
    u_ip2 = np.roll(u, -2)   # u_{i+2}

    u_half_right = (-u_im1 + 7.0 * u + 7.0 * u_ip1 - u_ip2) / 12.0

    # u_{i-1/2}: shift u_half_right one cell to the right
    u_half_left = np.roll(u_half_right, 1)

    # Step 2: CFWENO3 compact stencil (Eq. 30)
    ubar_right = (u_half_right
                  - nu * (u_half_right - u)
                  - nu * (1.0 - nu) * (u_half_left - 2.0 * u + u_half_right))

    # ubar_{i-1/2}: shift ubar_right one cell to the right
    ubar_left = np.roll(ubar_right, 1)

    # Step 3-4: conservative update  (a factors cancel: a*tau/h = cfl)
    return u - cfl * (ubar_right - ubar_left)


# ---- registry of known schemes -------------------------------------------
_SCHEMES: dict[str, callable] = {
    "upwind": upwind,
    "lax_wendroff": lax_wendroff,
    "cfweno": cfweno,
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
        Supported: "upwind", "lax_wendroff", "cfweno".

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
