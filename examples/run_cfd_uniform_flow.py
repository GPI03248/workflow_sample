"""Run uniform flow preservation test.

Verifies the CFD solver preserves a constant free-stream.
Results are saved to results/cfd_uniform_flow/.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np

from cfd.cases.uniform_flow import uniform_flow_config, uniform_flow_ic
from cfd.solver import run_solver


def main() -> None:
    config = uniform_flow_config()
    result_dir = os.path.join(os.path.dirname(__file__), "..", "results", "cfd_uniform_flow")

    print("=== Uniform Flow Preservation Test ===")
    print(f"Grid: {config.nx} x {config.ny}, ng={config.ng}")
    print(f"Final time: {config.final_time}")

    result = run_solver(
        config=config,
        initial_condition_func=uniform_flow_ic,
        case_name="uniform_flow",
        output_dir=result_dir,
    )

    ng = config.ng
    U = result["U"]
    U_int = U[:, ng:-ng, ng:-ng]
    rho_err = np.max(np.abs(U_int[0] - 1.0))
    rhou_err = np.max(np.abs(U_int[1] - 1.0))
    rhov_err = np.max(np.abs(U_int[2] - 0.5))

    print(f"\nSteps: {result['n_steps']}")
    print(f"Actual final time: {result['actual_final_time']:.6f}")
    print(f"max |rho - 1|   = {rho_err:.6e}")
    print(f"max |rho*u - 1| = {rhou_err:.6e}")
    print(f"max |rho*v - 0.5| = {rhov_err:.6e}")

    if rho_err < 1e-10:
        print("\nPASS: Uniform flow preserved to machine precision.")
    else:
        print(f"\nWARNING: rho error = {rho_err:.6e}")

    paths = result.get("output_paths", {})
    for key, p in paths.items():
        if isinstance(p, dict):
            for k2, p2 in p.items():
                print(f"  {key}/{k2}: {p2}")
        else:
            print(f"  {key}: {p}")


if __name__ == "__main__":
    main()
