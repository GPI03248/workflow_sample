"""Convergence study for the 2D advected entropy wave.

Runs the Euler solver on multiple grid resolutions and reports observed
convergence order.

Results are saved to results/cfd_entropy_wave_convergence/.
"""

import csv
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np

from cfd.config import CFDConfig
from cfd.cases.entropy_wave import (
    EntropyWaveParams,
    entropy_wave_exact_solution,
    entropy_wave_ic,
)
from cfd.mesh.structured import StructuredMesh2D
from cfd.numerics.time_integration import advance
from cfd.validation.errors import compute_field_errors


def run_one_resolution(
    nx: int,
    ny: int,
    params: EntropyWaveParams,
    cfl: float = 0.4,
    final_time: float = 0.1,
) -> dict:
    """Run entropy wave on a single grid and return error metrics."""
    ng = 2
    config = CFDConfig(
        nx=nx, ny=ny,
        xmin=0.0, xmax=1.0, ymin=0.0, ymax=1.0,
        gamma=params.gamma, cfl=cfl, ng=ng,
        final_time=final_time,
        bc_x="periodic", bc_y="periodic",
        flux_type="rusanov",
        reconstruction="piecewise_constant",
        time_integrator="euler",
    )
    mesh = StructuredMesh2D(
        nx=nx, ny=ny,
        xmin=0.0, xmax=1.0, ymin=0.0, ymax=1.0,
        ng=ng,
    )

    U = entropy_wave_ic(mesh.nxt, mesh.nyt, params.gamma, params)
    sim = advance(
        U,
        dx=mesh.dx, dy=mesh.dy, ng=ng, cfl=cfl,
        final_time=final_time,
        bc_x="periodic", bc_y="periodic",
        gamma=params.gamma,
        flux_type="rusanov",
        reconstruction="piecewise_constant",
        time_integrator="euler",
    )

    t_final = sim["actual_final_time"]
    U_num = sim["U"][:, ng:-ng, ng:-ng]
    U_exact_full = entropy_wave_exact_solution(mesh, t_final, params)
    U_exact = U_exact_full[:, ng:-ng, ng:-ng]

    errors = compute_field_errors(U_num, U_exact, mesh.dx, mesh.dy)
    return {
        "nx": nx, "ny": ny,
        "dx": mesh.dx,
        "n_steps": sim["n_steps"],
        "actual_final_time": t_final,
        **errors,
    }


def main() -> None:
    params = EntropyWaveParams()
    resolutions = [32, 64, 128]
    result_dir = os.path.join(
        os.path.dirname(__file__), "..", "results", "cfd_entropy_wave_convergence"
    )
    os.makedirs(result_dir, exist_ok=True)

    print("=== Entropy Wave Convergence Study ===")

    rows = []
    for n in resolutions:
        print(f"Running nx=ny={n} ...")
        result = run_one_resolution(n, n, params)
        rows.append(result)
        print(f"  rho L2 = {result['rho_l2_error']:.6e}")

    # Compute observed convergence orders.
    for i in range(1, len(rows)):
        dx_coarse = rows[i - 1]["dx"]
        dx_fine = rows[i]["dx"]
        for metric in ["rho_l1_error", "rho_l2_error", "rho_linf_error"]:
            err_c = rows[i - 1][metric]
            err_f = rows[i][metric]
            if err_f > 0 and err_c > 0:
                order = math.log(err_c / err_f) / math.log(dx_coarse / dx_fine)
            else:
                order = float("nan")
            rows[i][f"observed_order_{metric}"] = order

    # First row has no observed order.
    rows[0].setdefault("observed_order_rho_l1_error", float("nan"))
    rows[0].setdefault("observed_order_rho_l2_error", float("nan"))
    rows[0].setdefault("observed_order_rho_linf_error", float("nan"))

    # --- Save CSV ---
    csv_path = os.path.join(result_dir, "convergence_summary.csv")
    fieldnames = [
        "nx", "ny", "dx",
        "rho_l1_error", "rho_l2_error", "rho_linf_error",
        "observed_order_rho_l1_error", "observed_order_rho_l2_error",
        "observed_order_rho_linf_error",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = {}
            for k in fieldnames:
                v = row.get(k, "")
                if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    out[k] = "N/A"
                else:
                    out[k] = f"{v:.10e}" if isinstance(v, float) else v
            writer.writerow(out)
    print(f"\nCSV saved to {csv_path}")

    # --- Save convergence plot (optional) ---
    matplotlib_available = False
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        matplotlib_available = True
    except ImportError:
        pass

    if matplotlib_available:
        dxs = [r["dx"] for r in rows]
        l2s = [r["rho_l2_error"] for r in rows]

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.loglog(dxs, l2s, "bo-", linewidth=2, markersize=8, label="Rusanov + piecewise constant")
        # Reference first-order line.
        ref_x = np.array(dxs)
        ref_y = l2s[0] * (ref_x / dxs[0]) ** 1.0
        ax.loglog(ref_x, ref_y, "k--", linewidth=1, label="O(dx^1) reference")
        ax.set_xlabel("dx")
        ax.set_ylabel("rho L2 error")
        ax.set_title("Entropy wave: density L2 convergence")
        ax.legend()
        ax.grid(True, which="both", alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(result_dir, "density_l2_convergence.png"), dpi=150)
        plt.close(fig)
        print("Plot saved to results/cfd_entropy_wave_convergence/")
    else:
        print("matplotlib not available — skipping convergence plot.")

    # --- Save analysis.md ---
    md_path = os.path.join(result_dir, "convergence_analysis.md")
    with open(md_path, "w") as f:
        f.write("# Entropy Wave Convergence Study\n\n")
        f.write("## Setup\n\n")
        f.write("- 2D compressible Euler, ideal gas (gamma=1.4)\n")
        f.write("- Advected entropy wave, periodic BC\n")
        f.write(f"- CFL = 0.4, final_time = 0.1\n")
        f.write("- Rusanov flux + piecewise-constant reconstruction + forward Euler\n\n")
        f.write("## Results\n\n")
        f.write("| nx=ny | dx | rho L1 | rho L2 | rho Linf | order(L1) | order(L2) | order(Linf) |\n")
        f.write("|-------|-----|--------|--------|----------|-----------|-----------|-------------|\n")
        for row in rows:
            o1 = row.get("observed_order_rho_l1_error", float("nan"))
            o2 = row.get("observed_order_rho_l2_error", float("nan"))
            oi = row.get("observed_order_rho_linf_error", float("nan"))
            f.write(f"| {row['nx']} | {row['dx']:.6f} | {row['rho_l1_error']:.6e} | "
                    f"{row['rho_l2_error']:.6e} | {row['rho_linf_error']:.6e} | "
                    f"{o1:.2f} | {o2:.2f} | {oi:.2f} |\n")
        f.write("\n## Notes\n\n")
        f.write("- Piecewise-constant reconstruction + Rusanov flux + forward Euler\n")
        f.write("  is expected to give **first-order** convergence.\n")
        f.write("- Higher-order reconstruction (MUSCL) or time integration (RK2/RK3)\n")
        f.write("  would be needed to achieve second-order or higher.\n")
        if not matplotlib_available:
            f.write("- matplotlib was not available; no convergence plot was generated.\n")
    print(f"Analysis saved to {md_path}")


if __name__ == "__main__":
    main()
