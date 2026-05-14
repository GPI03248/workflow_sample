"""Time integration driver.

Responsibilities:
    - Run the main time loop: compute dt -> update -> apply BC -> repeat.
    - Support forward Euler and SSP RK2.
    - Handle final-step truncation to hit exact final_time.

Does NOT:
    - Implement individual update steps (see update.py).
"""

from __future__ import annotations
import numpy as np

from ..boundary.ghost_cells import apply_boundary_conditions
from .timestep import compute_dt
from .update import apply_euler_step


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
    limiter: str = "minmod",
    time_integrator: str = "euler",
) -> dict:
    """Advance solution from t=0 to t=final_time.

    Parameters
    ----------
    U, dx, dy, ng, cfl, final_time, bc_x, bc_y, gamma, flux_type,
    reconstruction, time_integrator : see CFDConfig.
    limiter : str
        Slope limiter for MUSCL: "minmod" or "vanleer".
    n_output : int
        Number of intermediate snapshots (0 = final only).

    Returns
    -------
    result : dict
        "U", "n_steps", "actual_final_time", "snapshots"
    """
    t = 0.0
    step_count = 0
    snapshots = []
    output_interval = final_time / (n_output + 1) if n_output > 0 else final_time + 1
    next_output = output_interval if n_output > 0 else final_time + 1

    while t < final_time:
        apply_boundary_conditions(U, ng, bc_x=bc_x, bc_y=bc_y)
        dt = compute_dt(U, dx, dy, cfl, gamma)
        if t + dt > final_time:
            dt = final_time - t
        if dt <= 0:
            break

        if n_output > 0 and t + dt >= next_output - 1e-14:
            snapshots.append((next_output, U.copy()))
            next_output += output_interval

        if time_integrator == "euler":
            apply_boundary_conditions(U, ng, bc_x=bc_x, bc_y=bc_y)
            apply_euler_step(U, dx, dy, dt, ng, gamma, flux_type,
                             reconstruction, limiter)
        elif time_integrator == "ssp_rk2":
            _ssp_rk2_step(U, dx, dy, dt, ng, gamma, flux_type,
                          reconstruction, limiter, bc_x, bc_y)
        else:
            raise ValueError(f"Unknown time integrator: {time_integrator}")

        t += dt
        step_count += 1

    apply_boundary_conditions(U, ng, bc_x=bc_x, bc_y=bc_y)

    return {
        "U": U,
        "n_steps": step_count,
        "actual_final_time": t,
        "snapshots": snapshots,
    }


def _ssp_rk2_step(
    U: np.ndarray, dx: float, dy: float, dt: float, ng: int,
    gamma: float, flux_type: str, reconstruction: str, limiter: str,
    bc_x: str, bc_y: str,
) -> None:
    """SSP RK2: U^{n+1} = 0.5*U^n + 0.5*(U1 + dt*L(U1)).

    Modifies U in-place.
    """
    U0 = U.copy()

    # Stage 1: U1 = U^n + dt * L(U^n)
    apply_boundary_conditions(U, ng, bc_x=bc_x, bc_y=bc_y)
    apply_euler_step(U, dx, dy, dt, ng, gamma, flux_type, reconstruction, limiter)

    # Stage 2: U^{n+1} = 0.5*U^n + 0.5*(U1 + dt*L(U1))
    apply_boundary_conditions(U, ng, bc_x=bc_x, bc_y=bc_y)
    apply_euler_step(U, dx, dy, dt, ng, gamma, flux_type, reconstruction, limiter)

    s = (slice(None), slice(ng, -ng), slice(ng, -ng))
    U[s] = 0.5 * U0[s] + 0.5 * U[s]
    # Ghost cells will be re-filled at next loop iteration.
