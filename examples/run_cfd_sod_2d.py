"""Run 2D Sod shock tube.

Demonstrates full-field shock capturing on a 2D grid.
Results are saved to results/cfd_sod_2d/.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np

from cfd.cases.sod_shock_tube_2d import sod_2d_config, sod_2d_ic
from cfd.solver import run_solver


def main() -> None:
    config = sod_2d_config()
    result_dir = os.path.join(os.path.dirname(__file__), "..", "results", "cfd_sod_2d")

    print("=== 2D Sod Shock Tube ===")
    print(f"Grid: {config.nx} x {config.ny}, ng={config.ng}")
    print(f"Final time: {config.final_time}")

    result = run_solver(
        config=config,
        initial_condition_func=sod_2d_ic,
        case_name="sod_2d",
        output_dir=result_dir,
        centerline_x=True,
    )

    ng = config.ng
    U = result["U"]
    U_int = U[:, ng:-ng, ng:-ng]
    rho = U_int[0]
    u = U_int[1] / rho
    v = U_int[2] / rho
    gamma = config.gamma
    p = (gamma - 1.0) * (U_int[3] - 0.5 * rho * (u**2 + v**2))

    print(f"\nSteps: {result['n_steps']}")
    print(f"Actual final time: {result['actual_final_time']:.6f}")
    print(f"rho: min={np.min(rho):.6e}  max={np.max(rho):.6e}")
    print(f"p:   min={np.min(p):.6e}  max={np.max(p):.6e}")
    print(f"u:   min={np.min(u):.6e}  max={np.max(u):.6e}")

    paths = result.get("output_paths", {})
    for key, p in paths.items():
        if isinstance(p, dict):
            for k2, p2 in p.items():
                print(f"  {key}/{k2}: {p2}")
        else:
            print(f"  {key}: {p}")


if __name__ == "__main__":
    main()
