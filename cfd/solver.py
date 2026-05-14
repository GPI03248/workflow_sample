"""CFD solver orchestration.

Responsibilities:
    - Tie together mesh, initial conditions, boundary conditions, numerics, and output.
    - This is the main entry point for running a CFD simulation.

Does NOT:
    - Implement numerical methods (see numerics/).
    - Define physics (see physics/).
"""

from __future__ import annotations
import numpy as np

from .config import CFDConfig
from .mesh.structured import StructuredMesh2D
from .numerics.time_integration import advance
from .io.output import save_results


def run_solver(
    config: CFDConfig,
    initial_condition_func,
    case_name: str = "cfd",
    output_dir: str | None = None,
    centerline_x: bool = False,
) -> dict:
    """Run a full CFD simulation from initialisation to output.

    Parameters
    ----------
    config : CFDConfig
        Solver configuration.
    initial_condition_func : callable(nxt, nyt, gamma) -> np.ndarray
        Function returning the initial conservative array.
    case_name : str
        Label for output.
    output_dir : str or None
        If provided, save results to this directory.
    centerline_x : bool
        Save centerline density plot.

    Returns
    -------
    result : dict
        "U", "mesh", "n_steps", "actual_final_time", "output_paths"
    """
    # 1. Build mesh.
    mesh = StructuredMesh2D(
        nx=config.nx,
        ny=config.ny,
        xmin=config.xmin,
        xmax=config.xmax,
        ymin=config.ymin,
        ymax=config.ymax,
        ng=config.ng,
    )

    # 2. Initialise solution.
    U = initial_condition_func(mesh.nxt, mesh.nyt, gamma=config.gamma)

    # 3. Run time integration.
    sim = advance(
        U,
        dx=mesh.dx,
        dy=mesh.dy,
        ng=config.ng,
        cfl=config.cfl,
        final_time=config.final_time,
        bc_x=config.bc_x,
        bc_y=config.bc_y,
        gamma=config.gamma,
        flux_type=config.flux_type,
        reconstruction=config.reconstruction,
        limiter=config.limiter,
        time_integrator=config.time_integrator,
    )

    result = {
        "U": sim["U"],
        "mesh": mesh,
        "n_steps": sim["n_steps"],
        "actual_final_time": sim["actual_final_time"],
        "output_paths": {},
    }

    # 4. Save output.
    if output_dir is not None:
        paths = save_results(
            output_dir=output_dir,
            U=sim["U"],
            mesh=mesh,
            n_steps=sim["n_steps"],
            actual_final_time=sim["actual_final_time"],
            gamma=config.gamma,
            case_name=case_name,
            centerline_x=centerline_x,
        )
        result["output_paths"] = paths

    return result
