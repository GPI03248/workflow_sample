"""Run 2D isentropic vortex validation.

Compares baseline (piecewise_constant + euler) vs MUSCL+minmod+SSP RK2.
Results saved to results/cfd_isentropic_vortex/.
"""

import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np

from cfd.config import CFDConfig
from cfd.cases.isentropic_vortex import (
    IsentropicVortexParams,
    isentropic_vortex_exact_solution,
    isentropic_vortex_ic,
)
from cfd.mesh.structured import StructuredMesh2D
from cfd.numerics.time_integration import advance
from cfd.validation.errors import compute_field_errors


def _run_one(config, params):
    mesh = StructuredMesh2D(
        nx=config.nx, ny=config.ny,
        xmin=config.xmin, xmax=config.xmax,
        ymin=config.ymin, ymax=config.ymax,
        ng=config.ng,
    )
    U = isentropic_vortex_ic(mesh.nxt, mesh.nyt, config.gamma, params)
    sim = advance(
        U, dx=mesh.dx, dy=mesh.dy, ng=config.ng, cfl=config.cfl,
        final_time=config.final_time,
        bc_x=config.bc_x, bc_y=config.bc_y,
        gamma=config.gamma, flux_type=config.flux_type,
        reconstruction=config.reconstruction, limiter=config.limiter,
        time_integrator=config.time_integrator,
    )
    ng = config.ng
    U_num = sim["U"][:, ng:-ng, ng:-ng]
    U_exact = isentropic_vortex_exact_solution(mesh, sim["actual_final_time"], params)[:, ng:-ng, ng:-ng]
    errors = compute_field_errors(U_num, U_exact, mesh.dx, mesh.dy)
    return sim, mesh, U_num, U_exact, errors


def main() -> None:
    params = IsentropicVortexParams()
    result_dir = os.path.join(os.path.dirname(__file__), "..", "results", "cfd_isentropic_vortex")
    os.makedirs(result_dir, exist_ok=True)

    base_cfg = dict(
        nx=64, ny=64, xmin=0.0, xmax=10.0, ymin=0.0, ymax=10.0,
        gamma=1.4, cfl=0.4, ng=2, final_time=0.5,
        bc_x="periodic", bc_y="periodic", flux_type="rusanov",
    )

    configs = {
        "baseline": CFDConfig(**base_cfg, reconstruction="piecewise_constant",
                              limiter="minmod", time_integrator="euler"),
        "muscl_minmod_rk2": CFDConfig(**base_cfg, reconstruction="muscl",
                                       limiter="minmod", time_integrator="ssp_rk2"),
    }

    print("=== 2D Isentropic Vortex Validation ===")
    results = {}
    for name, config in configs.items():
        print(f"\nRunning {name} ({config.reconstruction} + {config.time_integrator})...")
        sim, mesh, U_num, U_exact, errors = _run_one(config, params)
        results[name] = {
            "sim": sim, "mesh": mesh,
            "U_num": U_num, "U_exact": U_exact, "errors": errors,
            "config": config,
        }
        print(f"  Steps: {sim['n_steps']}, rho L2: {errors['rho_l2_error']:.6e}")

    # Save NPZ
    for name, r in results.items():
        np.savez(
            os.path.join(result_dir, f"final_state_{name}.npz"),
            U_num=r["U_num"], U_exact=r["U_exact"],
        )

    # Save CSV
    csv_path = os.path.join(result_dir, "error_summary.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "method", "reconstruction", "limiter", "time_integrator",
            "nx", "cfl", "final_time", "actual_final_time",
            "rho_l1_error", "rho_l2_error", "rho_linf_error", "rho_mass_error",
        ])
        for name, r in results.items():
            c = r["config"]
            e = r["errors"]
            writer.writerow([
                name, c.reconstruction, c.limiter, c.time_integrator,
                c.nx, c.cfl, c.final_time, r["sim"]["actual_final_time"],
                f"{e['rho_l1_error']:.10e}", f"{e['rho_l2_error']:.10e}",
                f"{e['rho_linf_error']:.10e}", f"{e['rho_mass_error']:.10e}",
            ])
    print(f"\nCSV saved to {csv_path}")

    # Plots (optional)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        mesh = results["baseline"]["mesh"]
        ng = mesh.ng
        X, Y = mesh.cell_centers_2d()
        X_int = X[ng:-ng, ng:-ng]
        Y_int = Y[ng:-ng, ng:-ng]

        # density_exact
        rho_ex = results["baseline"]["U_exact"][0]
        fig, ax = plt.subplots(figsize=(7, 6))
        c = ax.pcolormesh(X_int, Y_int, rho_ex, shading="auto")
        fig.colorbar(c, ax=ax, label="rho")
        ax.set_title("Isentropic vortex: exact density")
        ax.set_aspect("equal")
        fig.tight_layout()
        fig.savefig(os.path.join(result_dir, "density_exact.png"), dpi=150)
        plt.close(fig)

        for name in ["baseline", "muscl_minmod_rk2"]:
            rho_num = results[name]["U_num"][0]
            rho_err = rho_num - rho_ex

            fig, ax = plt.subplots(figsize=(7, 6))
            c = ax.pcolormesh(X_int, Y_int, rho_num, shading="auto")
            fig.colorbar(c, ax=ax, label="rho")
            ax.set_title(f"Isentropic vortex: {name} density")
            ax.set_aspect("equal")
            fig.tight_layout()
            fig.savefig(os.path.join(result_dir, f"density_{name}.png"), dpi=150)
            plt.close(fig)

            fig, ax = plt.subplots(figsize=(7, 6))
            c = ax.pcolormesh(X_int, Y_int, rho_err, shading="auto", cmap="RdBu_r")
            fig.colorbar(c, ax=ax, label="error")
            ax.set_title(f"Isentropic vortex: {name} density error")
            ax.set_aspect("equal")
            fig.tight_layout()
            fig.savefig(os.path.join(result_dir, f"density_error_{name}.png"), dpi=150)
            plt.close(fig)

        # Centerline comparison
        mid_j = rho_ex.shape[0] // 2
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(X_int[mid_j, :], rho_ex[mid_j, :], "k-", linewidth=2, label="Exact")
        for name in ["baseline", "muscl_minmod_rk2"]:
            ax.plot(X_int[mid_j, :], results[name]["U_num"][0][mid_j, :],
                    "--", linewidth=1.5, label=name)
        ax.set_xlabel("x"); ax.set_ylabel("rho")
        ax.set_title("Isentropic vortex: density centerline (y=mid)")
        ax.legend(); ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(result_dir, "density_centerline_comparison.png"), dpi=150)
        plt.close(fig)
        print("Plots saved.")
    except ImportError:
        print("matplotlib not available — skipping plots.")

    # analysis.md
    md_path = os.path.join(result_dir, "analysis.md")
    with open(md_path, "w") as f:
        f.write("# 2D Isentropic Vortex Validation\n\n")
        f.write("## Analytic Solution\n\n")
        f.write("Advected isentropic vortex: smooth nonlinear Euler flow.\n\n")
        f.write("## Error Summary\n\n")
        f.write("| Method | rho L2 | rho Linf |\n")
        f.write("|--------|--------|----------|\n")
        for name, r in results.items():
            f.write(f"| {name} | {r['errors']['rho_l2_error']:.6e} | "
                    f"{r['errors']['rho_linf_error']:.6e} |\n")
        f.write("\n## Notes\n\n")
        f.write("- Baseline: piecewise_constant + forward Euler (1st order expected).\n")
        f.write("- MUSCL+minmod+SSP_RK2: higher-order spatial + temporal (2nd order expected).\n")
    print(f"Analysis saved to {md_path}")


if __name__ == "__main__":
    main()
