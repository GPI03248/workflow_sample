"""Run 2D advected entropy wave validation.

Compares numerical Euler solver output against the analytic solution.
Results are saved to results/cfd_entropy_wave/.
"""

import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np

from cfd.cases.entropy_wave import (
    EntropyWaveParams,
    entropy_wave_config,
    entropy_wave_exact_solution,
    entropy_wave_ic,
)
from cfd.solver import run_solver
from cfd.validation.errors import compute_field_errors


def main() -> None:
    params = EntropyWaveParams()
    config = entropy_wave_config(params)
    result_dir = os.path.join(
        os.path.dirname(__file__), "..", "results", "cfd_entropy_wave"
    )
    os.makedirs(result_dir, exist_ok=True)

    print("=== 2D Advected Entropy Wave Validation ===")
    print(f"Grid: {config.nx} x {config.ny}, ng={config.ng}")
    print(f"CFL={config.cfl}, final_time={config.final_time}")

    # Run solver.
    result = run_solver(
        config=config,
        initial_condition_func=lambda nxt, nyt, gamma: entropy_wave_ic(
            nxt, nyt, gamma, params
        ),
        case_name="entropy_wave",
        output_dir=None,
    )

    ng = config.ng
    mesh = result["mesh"]
    t_final = result["actual_final_time"]

    # Extract interior numerical solution.
    U_num = result["U"][:, ng:-ng, ng:-ng]

    # Compute exact solution on interior grid.
    U_exact_full = entropy_wave_exact_solution(mesh, t_final, params)
    U_exact = U_exact_full[:, ng:-ng, ng:-ng]

    # Compute errors.
    errors = compute_field_errors(U_num, U_exact, mesh.dx, mesh.dy)

    print(f"\nSteps: {result['n_steps']}")
    print(f"Actual final time: {t_final:.6f}")
    print(f"rho L2 error: {errors['rho_l2_error']:.6e}")
    print(f"rho Linf error: {errors['rho_linf_error']:.6e}")
    print(f"rho mass error: {errors['rho_mass_error']:.6e}")

    # --- Save NPZ ---
    npz_path = os.path.join(result_dir, "final_state.npz")
    X, Y = mesh.cell_centers_2d()
    X_int = X[ng:-ng, ng:-ng]
    Y_int = Y[ng:-ng, ng:-ng]
    np.savez(
        npz_path,
        U_num=U_num,
        U_exact=U_exact,
        X=X_int,
        Y=Y_int,
        rho_num=U_num[0],
        rho_exact=U_exact[0],
    )
    print(f"\nNPZ saved to {npz_path}")

    # --- Save CSV ---
    csv_path = os.path.join(result_dir, "error_summary.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "case", "nx", "ny", "cfl", "final_time", "actual_final_time",
            "reconstruction", "riemann", "time_integrator",
            "rho_l1_error", "rho_l2_error", "rho_linf_error", "rho_mass_error",
        ])
        writer.writerow([
            "entropy_wave", config.nx, config.ny, config.cfl,
            config.final_time, t_final,
            config.reconstruction, config.flux_type, config.time_integrator,
            f"{errors['rho_l1_error']:.10e}",
            f"{errors['rho_l2_error']:.10e}",
            f"{errors['rho_linf_error']:.10e}",
            f"{errors['rho_mass_error']:.10e}",
        ])
    print(f"CSV saved to {csv_path}")

    # --- Save plots (optional) ---
    matplotlib_available = False
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        matplotlib_available = True
    except ImportError:
        pass

    if matplotlib_available:
        rho_num = U_num[0]
        rho_ex = U_exact[0]
        rho_err = rho_num - rho_ex

        # density_initial
        U_init = entropy_wave_exact_solution(mesh, 0.0, params)[:, ng:-ng, ng:-ng]
        fig, ax = plt.subplots(figsize=(7, 6))
        c = ax.pcolormesh(X_int, Y_int, U_init[0], shading="auto")
        fig.colorbar(c, ax=ax, label="rho")
        ax.set_title("Entropy wave: initial density (t=0)")
        ax.set_aspect("equal")
        fig.tight_layout()
        fig.savefig(os.path.join(result_dir, "density_initial.png"), dpi=150)
        plt.close(fig)

        # density_numerical
        fig, ax = plt.subplots(figsize=(7, 6))
        c = ax.pcolormesh(X_int, Y_int, rho_num, shading="auto")
        fig.colorbar(c, ax=ax, label="rho")
        ax.set_title(f"Entropy wave: numerical density (t={t_final:.4f})")
        ax.set_aspect("equal")
        fig.tight_layout()
        fig.savefig(os.path.join(result_dir, "density_numerical.png"), dpi=150)
        plt.close(fig)

        # density_exact
        fig, ax = plt.subplots(figsize=(7, 6))
        c = ax.pcolormesh(X_int, Y_int, rho_ex, shading="auto")
        fig.colorbar(c, ax=ax, label="rho")
        ax.set_title(f"Entropy wave: exact density (t={t_final:.4f})")
        ax.set_aspect("equal")
        fig.tight_layout()
        fig.savefig(os.path.join(result_dir, "density_exact.png"), dpi=150)
        plt.close(fig)

        # density_error
        fig, ax = plt.subplots(figsize=(7, 6))
        c = ax.pcolormesh(X_int, Y_int, rho_err, shading="auto", cmap="RdBu_r")
        fig.colorbar(c, ax=ax, label="rho_num - rho_exact")
        ax.set_title(f"Entropy wave: density error (t={t_final:.4f})")
        ax.set_aspect("equal")
        fig.tight_layout()
        fig.savefig(os.path.join(result_dir, "density_error.png"), dpi=150)
        plt.close(fig)

        # centerline comparison
        mid_j = rho_num.shape[0] // 2
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(X_int[mid_j, :], rho_ex[mid_j, :], "k-", linewidth=2, label="Exact")
        ax.plot(X_int[mid_j, :], rho_num[mid_j, :], "r--", linewidth=1.5, label="Numerical")
        ax.set_xlabel("x")
        ax.set_ylabel("rho")
        ax.set_title(f"Entropy wave: density centerline (y=mid, t={t_final:.4f})")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(
            os.path.join(result_dir, "density_centerline_comparison.png"), dpi=150
        )
        plt.close(fig)

        print("Plots saved to results/cfd_entropy_wave/")
    else:
        print("matplotlib not available — skipping plots.")

    # --- Save analysis.md ---
    md_path = os.path.join(result_dir, "analysis.md")
    with open(md_path, "w") as f:
        f.write("# 2D Advected Entropy Wave Validation\n\n")
        f.write("## PDE\n\n")
        f.write("2D compressible Euler equations, ideal gas (gamma=1.4)\n\n")
        f.write("## Analytic Solution\n\n")
        f.write("```\n")
        f.write("rho(x,y,t) = rho0 + eps * sin(2*pi*(kx*(x - u0*t) + ky*(y - v0*t)))\n")
        f.write("u(x,y,t) = u0\n")
        f.write("v(x,y,t) = v0\n")
        f.write("p(x,y,t) = p0\n")
        f.write("```\n\n")
        f.write("## Parameters\n\n")
        f.write(f"- rho0={params.rho0}, eps={params.eps}, u0={params.u0}, v0={params.v0}, p0={params.p0}\n")
        f.write(f"- kx={params.kx}, ky={params.ky}\n")
        f.write(f"- nx={config.nx}, ny={config.ny}, cfl={config.cfl}\n")
        f.write(f"- final_time={config.final_time}, actual_final_time={t_final:.6f}\n")
        f.write(f"- Steps: {result['n_steps']}\n")
        f.write(f"- reconstruction={config.reconstruction}, riemann={config.flux_type}, time_integrator={config.time_integrator}\n\n")
        f.write("## Error Summary\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| rho L1 | {errors['rho_l1_error']:.6e} |\n")
        f.write(f"| rho L2 | {errors['rho_l2_error']:.6e} |\n")
        f.write(f"| rho Linf | {errors['rho_linf_error']:.6e} |\n")
        f.write(f"| rho mass | {errors['rho_mass_error']:.6e} |\n\n")
        f.write("## Notes\n\n")
        if not matplotlib_available:
            f.write("- matplotlib was not available; no plots were generated.\n")
        f.write("- This case uses periodic boundary conditions, matching the analytic solution exactly.\n")
        f.write("- The solver uses piecewise-constant reconstruction + Rusanov flux + forward Euler,\n")
        f.write("  so first-order convergence is expected.\n")
    print(f"Analysis saved to {md_path}")


if __name__ == "__main__":
    main()
