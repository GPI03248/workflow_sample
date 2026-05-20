"""Numerical schemes for 1D scalar advection and Burgers equations."""

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


def _interface_reconstruction(u: np.ndarray) -> np.ndarray:
    """4th-order centred interface reconstruction: u_{i+1/2}."""
    u_im1 = np.roll(u, 1)
    u_ip1 = np.roll(u, -1)
    u_ip2 = np.roll(u, -2)
    return (-u_im1 + 7.0 * u + 7.0 * u_ip1 - u_ip2) / 12.0


def _cfweno3_stencil(u: np.ndarray, nu: np.ndarray) -> np.ndarray:
    """CFWENO3 compact stencil (Eq. 30) with per-cell nu.

    Returns ubar_{i+1/2} at each interface.
    """
    u_half_right = _interface_reconstruction(u)
    u_half_left = np.roll(u_half_right, 1)
    ubar_right = (u_half_right
                  - nu * (u_half_right - u)
                  - nu * (1.0 - nu) * (u_half_left - 2.0 * u + u_half_right))
    return ubar_right


def cfweno_burgers(u: np.ndarray, dx: float, dt: float,
                   predictor_iterations: int = 1) -> np.ndarray:
    """CFWENO3 Burgers — scalar nonlinear Burgers equation.

    Solves u_t + (u^2/2)_x = 0 using the CFWENO3 stencil from
    Zhou-Dong-Pan (2025) with SFM flux linearization.

    The SFM decomposition f(u) = a*u - f* yields a numerical flux
    f_hat = f(ubar) = ubar^2/2, where ubar is the CFWENO3-reconstructed
    interface state using per-cell nu = dt * a_i / dx.

    Predictor iterations refine the characteristic speed a from u_i^n
    toward the interface-predicted value, improving accuracy.

    Parameters
    ----------
    u : np.ndarray
        Current solution (cell-centre values).
    dx : float
        Grid spacing.
    dt : float
        Time step.  Must satisfy max(|u|)*dt/dx <= 1 (CFL <= 1).
    predictor_iterations : int
        Number of predictor iterations for characteristic speed a.
        0 = frozen (a = u_i^n), 1 = one correction (default), 2 = two.

    Returns
    -------
    np.ndarray
        Solution after one time-step (same shape as *u*).
    """
    tau_h = dt / dx

    # CFL check
    max_speed = np.max(np.abs(u))
    if max_speed > 0 and max_speed * tau_h > 1.0:
        raise ValueError(
            f"CFL > 1 for Burgers: max(|u|)={max_speed:.4f}, "
            f"CFL={max_speed * tau_h:.4f}. Reduce dt or increase dx."
        )

    # Initial characteristic speed: a_i = f'(u_i) = u_i
    a = u.copy()

    # Predictor iterations to refine a
    for _ in range(predictor_iterations):
        nu = np.clip(tau_h * a, 0.0, 1.0)
        ubar_right = _cfweno3_stencil(u, nu)
        ubar_left = np.roll(ubar_right, 1)
        # Update a to cell-average of interface predictions
        a = 0.5 * (ubar_right + ubar_left)

    # Final CFWENO3 stencil with refined a
    nu = np.clip(tau_h * a, 0.0, 1.0)
    ubar_right = _cfweno3_stencil(u, nu)

    # Numerical flux: f_hat = f(ubar) = ubar^2 / 2
    f_hat_right = 0.5 * ubar_right**2
    f_hat_left = np.roll(f_hat_right, 1)

    # Conservative update (Eq. 25)
    return u - tau_h * (f_hat_right - f_hat_left)


def burgers_upwind(u: np.ndarray, dx: float, dt: float) -> np.ndarray:
    """First-order local Lax-Friedrichs (Rusanov) for Burgers scalar.

    f_hat_{i+1/2} = 0.5*(f(u_L) + f(u_R)) - 0.5*alpha*(u_R - u_L)
    where alpha = max(|u_L|, |u_R|), f(u) = u^2/2.

    Used as a stable baseline for Burgers comparison only.
    Does NOT affect the Euler solver.
    """
    u_left = np.roll(u, 1)   # u_{i-1} = u_L at interface i-1/2
    u_right = np.roll(u, -1)  # u_{i+1} = u_R at interface i+1/2

    # Flux at i+1/2
    f_L = 0.5 * u**2         # f(u_i) — left state at i+1/2
    f_R = 0.5 * u_right**2   # f(u_{i+1}) — right state at i+1/2
    alpha = np.maximum(np.abs(u), np.abs(u_right))

    f_hat_right = 0.5 * (f_L + f_R) - 0.5 * alpha * (u_right - u)
    f_hat_left = np.roll(f_hat_right, 1)

    return u - (dt / dx) * (f_hat_right - f_hat_left)


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
