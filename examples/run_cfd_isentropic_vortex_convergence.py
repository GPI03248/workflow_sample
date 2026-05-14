"""Convergence study for 2D isentropic vortex.

Compares baseline vs MUSCL+minmod+SSP_RK2 across grid resolutions.
"""

import csv
import math
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


def run_one(n, reconstruction, limiter, time_integrator, params):
    ng = 2
    config = CFDConfig(
        nx=n, ny=n, xmin=0.0, xmax=10.0, ymin=0.0, ymax=10.0,
        gamma=1.4, cfl=0.4, ng=ng, final_time=0.5,
        bc_x="periodic", bc_y="periodic", flux_type="rusanov",
        reconstruction=reconstruction, limiter=limiter,
        time_integrator=time_integrator,
    )
    mesh = StructuredMesh2D(nx=n, ny=n, xmin=0, xmax=10, ymin=0, ymax=10, ng=ng)
    U = isentropic_vortex_ic(mesh.nxt, mesh.nyt, config.gamma, params)
    sim = advance(
        U, dx=mesh.dx, dy=mesh.dy, ng=ng, cfl=config.cfl,
        final_time=config.final_time, bc_x="periodic", bc_y="periodic",
        gamma=config.gamma, flux_type="rusanov",
        reconstruction=reconstruction, limiter=limiter,
        time_integrator=time_integrator,
    )
    U_num = sim["U"][:, ng:-ng, ng:-ng]
    U_ex = isentropic_vortex_exact_solution(mesh, sim["actual_final_time"], params)[:, ng:-ng, ng:-ng]
    errors = compute_field_errors(U_num, U_ex, mesh.dx, mesh.dy)
    return {"nx": n, "dx": mesh.dx, "n_steps": sim["n_steps"], **errors}


def main() -> None:
    params = IsentropicVortexParams()
    result_dir = os.path.join(os.path.dirname(__file__), "..", "results", "cfd_isentropic_vortex_convergence")
    os.makedirs(result_dir, exist_ok=True)

    methods = {
        "baseline": ("piecewise_constant", "minmod", "euler"),
        "muscl_minmod_rk2": ("muscl", "minmod", "ssp_rk2"),
    }
    resolutions = [32, 64, 128]

    print("=== Isentropic Vortex Convergence Study ===")

    all_rows = {}
    for mname, (recon, lim, ti) in methods.items():
        rows = []
        for n in resolutions:
            print(f"  {mname} nx={n}...")
            r = run_one(n, recon, lim, ti, params)
            r["method"] = mname
            rows.append(r)
        # Compute observed orders.
        for i in range(1, len(rows)):
            for metric in ["rho_l1_error", "rho_l2_error", "rho_linf_error"]:
                ec = rows[i-1][metric]; ef = rows[i][metric]
                order = math.log(ec/ef)/math.log(rows[i-1]["dx"]/rows[i]["dx"]) if ef > 0 and ec > 0 else float("nan")
                rows[i][f"obs_{metric}"] = order
        rows[0].setdefault("obs_rho_l1_error", float("nan"))
        rows[0].setdefault("obs_rho_l2_error", float("nan"))
        rows[0].setdefault("obs_rho_linf_error", float("nan"))
        all_rows[mname] = rows
        print(f"  {mname} L2: {[f'{r['rho_l2_error']:.3e}' for r in rows]}")

    # CSV
    csv_path = os.path.join(result_dir, "convergence_summary.csv")
    fields = ["method","nx","dx","rho_l1_error","rho_l2_error","rho_linf_error",
              "obs_rho_l1_error","obs_rho_l2_error","obs_rho_linf_error"]
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for mname, rows in all_rows.items():
            for row in rows:
                out = {}
                for k in fields:
                    v = row.get(k, "")
                    out[k] = (f"{v:.10e}" if isinstance(v, float) and not (math.isnan(v) or math.isinf(v)) else ("N/A" if isinstance(v, float) else v))
                w.writerow(out)
    print(f"\nCSV saved to {csv_path}")

    # Plot (optional)
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 5))
        for mname, rows in all_rows.items():
            dxs = [r["dx"] for r in rows]
            l2s = [r["rho_l2_error"] for r in rows]
            ax.loglog(dxs, l2s, "o-", linewidth=2, markersize=8, label=mname)
        ref = np.array([all_rows["baseline"][0]["dx"], all_rows["baseline"][-1]["dx"]])
        ax.loglog(ref, [all_rows["baseline"][0]["rho_l2_error"]]*(ref/ref[0])**1, "k--", label="O(dx^1)")
        ax.loglog(ref, [all_rows["baseline"][0]["rho_l2_error"]]*(ref/ref[0])**2, "k:", label="O(dx^2)")
        ax.set_xlabel("dx"); ax.set_ylabel("rho L2 error")
        ax.set_title("Isentropic vortex: density L2 convergence")
        ax.legend(); ax.grid(True, which="both", alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(result_dir, "density_l2_convergence.png"), dpi=150)
        plt.close(fig)
        print("Plot saved.")
    except ImportError:
        print("matplotlib not available.")

    # analysis.md
    md_path = os.path.join(result_dir, "convergence_analysis.md")
    with open(md_path, "w") as f:
        f.write("# Isentropic Vortex Convergence\n\n")
        f.write("## Setup\n\n")
        f.write("- 2D Euler, periodic BC, domain [0,10]^2\n")
        f.write("- CFL=0.4, final_time=0.5\n\n")
        for mname, rows in all_rows.items():
            f.write(f"## {mname}\n\n")
            f.write("| nx | dx | rho L2 | order(L2) |\n")
            f.write("|----|-----|--------|----------|\n")
            for r in rows:
                o = r.get("obs_rho_l2_error", float("nan"))
                f.write(f"| {r['nx']} | {r['dx']:.4f} | {r['rho_l2_error']:.6e} | {o:.2f} |\n")
            f.write("\n")
        f.write("## Notes\n\n")
        f.write("- Baseline (piecewise_constant + Euler): ~1st order expected.\n")
        f.write("- MUSCL+minmod+SSP_RK2: higher order expected on smooth flow,\n")
        f.write("  but actual order depends on limiter, flux, and implementation details.\n")
        f.write("- These results are specific to this benchmark and do not generalise.\n")
    print(f"Analysis saved to {md_path}")


if __name__ == "__main__":
    main()
