"""High-level simulation driver with analytic-solution benchmarking."""

import numpy as np

from .grid import make_grid
from .schemes import WAVE_SPEED, step


# ---- analytic solution for u_t + a*u_x = 0 on [0,1) periodic ------------

def initial_condition(x: np.ndarray) -> np.ndarray:
    """u(x, 0) = sin(2*pi*x) + 1"""
    return np.sin(2.0 * np.pi * x) + 1.0


def exact_solution(x: np.ndarray, t: float, a: float = 1.0) -> np.ndarray:
    """u_exact(x, t) = sin(2*pi*(x - a*t)) + 1"""
    return np.sin(2.0 * np.pi * (x - a * t)) + 1.0


# ---- error metrics --------------------------------------------------------

def compute_errors(u_num: np.ndarray, u_exact: np.ndarray, dx: float) -> dict:
    """Return L1, L2, Linf, and mass errors.

    L2 = sqrt( sum((u_num - u_exact)^2) * dx )
    mass_error = abs( sum(u_num) - sum(u_exact) ) * dx
    """
    diff = u_num - u_exact
    l1 = np.sum(np.abs(diff)) * dx
    l2 = np.sqrt(np.sum(diff**2) * dx)
    linf = np.max(np.abs(diff))
    mass_err = abs(np.sum(u_num) - np.sum(u_exact)) * dx
    return {
        "l1_error": l1,
        "l2_error": l2,
        "linf_error": linf,
        "mass_error": mass_err,
    }


# ---- simulation driver ----------------------------------------------------

def run_advection(
    scheme: str,
    nx: int = 100,
    cfl: float = 0.5,
    final_time: float = 0.25,
    a: float = 1.0,
) -> dict:
    """Run one advection simulation and return results + exact solution.

    Uses fixed dt = cfl * dx / a for every step, so actual_final_time may
    differ slightly from *final_time*.  The exact solution is evaluated at
    actual_final_time so the comparison is always consistent.

    Returns dict with keys:
        x, u0, u_num, u_exact, dx, dt, n_steps, actual_final_time
    """
    x, dx = make_grid(nx)
    dt = cfl * dx / a
    n_steps = int(round(final_time / dt))
    actual_final_time = n_steps * dt

    u = initial_condition(x)
    u0 = u.copy()

    for _ in range(n_steps):
        u = step(u, cfl, scheme=scheme)

    u_ex = exact_solution(x, actual_final_time, a=a)

    return {
        "x": x,
        "u0": u0,
        "u_num": u,
        "u_exact": u_ex,
        "dx": dx,
        "dt": dt,
        "n_steps": n_steps,
        "actual_final_time": actual_final_time,
    }
