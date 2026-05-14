"""Time integration driver.

Responsibilities:
    - Run the main time loop: compute dt -> update -> apply BC -> repeat.
    - Handle final-step truncation to hit exact final_time.
    - Collect intermediate output snapshots.

Does NOT:
    - Implement individual update steps (see update.py).
"""

from __future__ import annotations
import numpy as np

from ..boundary.ghost_cells import apply_boundary_conditions
from .timestep import compute_dt
from .update import euler_update


def advance(
    U: np.ndarray,
    dx: float,
    dy: float,
    ng: int,
    cfl: float,
    final_time: float,
    bc_x: str = "transmissive",
    bc_y: str = "transmissive",
    n_output: int = 0,
    gamma: float = 1.4,
    flux_type: str = "rusanov",
    reconstruction: str = "piecewise_constant",
    time_integrator: str = "euler",
) -> dict:
    """Advance solution from t=0 to t=final_time.

    Parameters
    ----------
    U : np.ndarray, shape (4, nyt, nxt)
        Initial conservative variables (modified in-place).
    dx, dy, ng, cfl, final_time, bc_x, bc_y, gamma, flux_type,
    reconstruction, time_integrator : see CFDConfig.
    n_output : int
        Number of intermediate snapshots (0 = final only).

    Returns
    -------
    result : dict
        "U" — final conservative array.
        "n_steps" — total number of time steps.
        "actual_final_time" — actual simulation end time.
        "snapshots" — list of (t, U.copy()) if n_output > 0.
    """
    t = 0.0
    step_count = 0
    snapshots = []
    output_interval = final_time / (n_output + 1) if n_output > 0 else final_time + 1
    next_output = output_interval if n_output > 0 else final_time + 1

    while t < final_time:
        # Apply boundary conditions.
        apply_boundary_conditions(U, ng, bc_x=bc_x, bc_y=bc_y)

        # Compute time step.
        dt = compute_dt(U, dx, dy, cfl, gamma)
        # Truncate last step.
        if t + dt > final_time:
            dt = final_time - t
        if dt <= 0:
            break

        # Snapshot check.
        if n_output > 0 and t + dt >= next_output - 1e-14:
            snapshots.append((next_output, U.copy()))
            next_output += output_interval

        # Update.
        if time_integrator == "euler":
            apply_boundary_conditions(U, ng, bc_x=bc_x, bc_y=bc_y)
            euler_update(U, dx, dy, dt, ng, gamma, flux_type, reconstruction)
        else:
            raise ValueError(f"Unknown time integrator: {time_integrator}")

        t += dt
        step_count += 1

    # Final BC application.
    apply_boundary_conditions(U, ng, bc_x=bc_x, bc_y=bc_y)

    return {
        "U": U,
        "n_steps": step_count,
        "actual_final_time": t,
        "snapshots": snapshots,
    }
