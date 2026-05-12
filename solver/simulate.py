"""High-level simulation driver."""

import numpy as np

from .grid import gaussian_ic, make_grid
from .schemes import WAVE_SPEED, step


def run(
    n: int = 200,
    cfl: float = 0.8,
    t_final: float = 1.0,
    scheme: str = "upwind",
) -> dict:
    """Run a 1D advection simulation and return snapshots.

    Returns a dict with keys: centers, u_final, u_initial, dx, n_steps.
    """
    centers, dx = make_grid(n)
    dt = cfl * dx / WAVE_SPEED
    n_steps = int(np.ceil(t_final / dt))
    # Adjust dt so we land exactly on t_final.
    dt = t_final / n_steps
    cfl_actual = WAVE_SPEED * dt / dx

    u = gaussian_ic(centers)
    u_initial = u.copy()

    for _ in range(n_steps):
        u = step(u, cfl_actual, scheme=scheme)

    return {
        "centers": centers,
        "u_initial": u_initial,
        "u_final": u,
        "dx": dx,
        "n_steps": n_steps,
    }
