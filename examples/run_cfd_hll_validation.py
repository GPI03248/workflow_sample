"""Run HLL Riemann solver validation with comparison against Rusanov.

Runs entropy wave and uniform flow tests using both Rusanov and HLL fluxes.
Results are saved to results/cfd_hll_validation/.
"""

import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np

from cfd.config import CFDConfig
from cfd.constants import GAMMA
from cfd.cases.entropy_wave import (
    EntropyWaveParams,
    entropy_wave_config,
    entropy_wave_exact_solution,
    entropy_wave_ic,
)
from cfd.cases.uniform_flow import uniform_flow_config, uniform_flow_ic
from cfd.solver import run_solver
from cfd.validation.errors import compute_field_errors


def _run_entropy_wave(flux_type: str) -> dict:
    """Run entropy wave validation with given flux type."""
    params = EntropyWaveParams()
    config = entropy_wave_config(params)
    config.flux_type = flux_type
    config.nx = 40
    config.ny = 20

    result = run_solver(
        config=config,
        initial_condition_func=lambda nxt, nyt, gamma: entropy_wave_ic(
            nxt, nyt, gamma, params
        ),
        case_name=f"entropy_wave_{flux_type}",
        output_dir=None,
    )

    ng = config.ng
    mesh = result["mesh"]
    t_final = result["actual_final_time"]
    U_num = result["U"][:, ng:-ng, ng:-ng]
    U_exact = entropy_wave_exact_solution(mesh, t_final, params)[:, ng:-ng, ng:-ng]
    errors = compute_field_errors(U_num, U_exact, mesh.dx, mesh.dy)

    return {
        "case": "entropy_wave",
        "riemann": flux_type,
        "reconstruction": config.reconstruction,
        "time_integrator": config.time_integrator,
        "nx": config.nx,
        "ny": config.ny,
        "final_time": config.final_time,
        "actual_final_time": t_final,
        "n_steps": result["n_steps"],
        **errors,
    }


def _run_uniform_flow(flux_type: str) -> dict:
    """Run uniform flow preservation test with given flux type."""
    config = uniform_flow_config()
    config.flux_type = flux_type
    config.nx = 20
    config.ny = 10
    config.final_time = 0.1

    result = run_solver(
        config=config,
        initial_condition_func=uniform_flow_ic,
        case_name=f"uniform_{flux_type}",
        output_dir=None,
    )

    ng = config.ng
    U = result["U"]
    rho = U[0, ng:-ng, ng:-ng]
    rho_mass_error = np.abs(np.sum(rho) - rho.size)

    return {
        "case": "uniform_flow",
        "riemann": flux_type,
        "reconstruction": config.reconstruction,
        "time_integrator": config.time_integrator,
        "nx": config.nx,
        "ny": config.ny,
        "final_time": config.final_time,
        "actual_final_time": result["actual_final_time"],
        "n_steps": result["n_steps"],
        "rho_l1_error": float(np.sum(np.abs(rho - 1.0))),
        "rho_l2_error": float(np.sqrt(np.mean((rho - 1.0) ** 2))),
        "rho_linf_error": float(np.max(np.abs(rho - 1.0))),
        "rho_mass_error": float(rho_mass_error),
    }


def main() -> None:
    result_dir = os.path.join(
        os.path.dirname(__file__), "..", "results", "cfd_hll_validation"
    )
    os.makedirs(result_dir, exist_ok=True)

    print("=== HLL Riemann Solver Validation ===\n")

    results = []
    for flux in ["rusanov", "hll"]:
        print(f"--- Entropy wave ({flux}) ---")
        r = _run_entropy_wave(flux)
        results.append(r)
        print(f"  Steps: {r['n_steps']}, rho L2: {r['rho_l2_error']:.6e}")

        print(f"--- Uniform flow ({flux}) ---")
        r = _run_uniform_flow(flux)
        results.append(r)
        print(f"  Steps: {r['n_steps']}, rho mass error: {r['rho_mass_error']:.6e}")

    # Save CSV
    csv_path = os.path.join(result_dir, "error_summary.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "case",
                "riemann",
                "reconstruction",
                "time_integrator",
                "nx",
                "ny",
                "final_time",
                "rho_l1_error",
                "rho_l2_error",
                "rho_linf_error",
                "rho_mass_error",
            ]
        )
        for r in results:
            writer.writerow(
                [
                    r["case"],
                    r["riemann"],
                    r["reconstruction"],
                    r["time_integrator"],
                    r["nx"],
                    r["ny"],
                    f"{r['final_time']:.4f}",
                    f"{r['rho_l1_error']:.10e}",
                    f"{r['rho_l2_error']:.10e}",
                    f"{r['rho_linf_error']:.10e}",
                    f"{r['rho_mass_error']:.10e}",
                ]
            )
    print(f"\nCSV saved to {csv_path}")

    # Save analysis.md
    md_path = os.path.join(result_dir, "analysis.md")
    with open(md_path, "w") as f:
        f.write("# HLL Riemann Solver Validation\n\n")
        f.write("## Method\n\n")
        f.write("HLL (Harten-Lax-van Leer) approximate Riemann solver.\n")
        f.write("Uses Roe-averaged wave speed estimates for S_L and S_R.\n\n")
        f.write("## Results\n\n")
        f.write("| Case | Riemann | rho L2 | rho Linf | rho mass |\n")
        f.write("|------|---------|--------|----------|----------|\n")
        for r in results:
            f.write(
                f"| {r['case']} | {r['riemann']} | "
                f"{r['rho_l2_error']:.6e} | {r['rho_linf_error']:.6e} | "
                f"{r['rho_mass_error']:.6e} |\n"
            )
        f.write("\n## Notes\n\n")
        f.write("- HLL is an approximate Riemann solver (two-wave model).\n")
        f.write(
            "- This validation only demonstrates behavior on the tested benchmarks.\n"
        )
        f.write("- HLL may not outperform Rusanov on all problems.\n")
        f.write("- HLLC (three-wave solver) is not yet implemented.\n")

        # Compare entropy wave errors
        ew_hll = [
            r for r in results if r["case"] == "entropy_wave" and r["riemann"] == "hll"
        ]
        ew_rus = [
            r
            for r in results
            if r["case"] == "entropy_wave" and r["riemann"] == "rusanov"
        ]
        if ew_hll and ew_rus:
            ratio = ew_hll[0]["rho_l2_error"] / ew_rus[0]["rho_l2_error"]
            f.write(f"- HLL/Rusanov L2 ratio (entropy wave): {ratio:.4f}\n")
            if ratio < 1.0:
                f.write(
                    "  HLL produces lower errors than Rusanov on this case, as expected.\n"
                )
            else:
                f.write(
                    "  HLL errors are similar to or higher than Rusanov on this grid.\n"
                )

    print(f"Analysis saved to {md_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()
