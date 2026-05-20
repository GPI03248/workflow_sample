"""CFWENO3 Burgers demo — smooth pre-shock baseline comparison.

Compares CFWENO3 Burgers vs local Lax-Friedrichs (Rusanov) baseline on
u_t + (u^2/2)_x = 0 with smooth IC, before shock formation.

Reference solution: fine-grid CFWENO3 Burgers (nx=2560).

Outputs (results/cfweno_burgers_demo/):
  error_summary.csv
  line_profile.csv
  cfweno_burgers_comparison.png
  analysis.md
"""

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solver.schemes import burgers_upwind, cfweno_burgers

NX = 100
CFL = 0.5
FINAL_TIME = 0.15
IC_AMP = 0.2  # u0 = 1 + IC_AMP * sin(2*pi*x)
PREDICTOR_ITERS = 1

RESULTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "results", "cfweno_burgers_demo"
)
os.makedirs(RESULTS_DIR, exist_ok=True)


def _burgers_ic(x: np.ndarray) -> np.ndarray:
    """Smooth IC: u0 = 1 + amp * sin(2*pi*x)."""
    return 1.0 + IC_AMP * np.sin(2.0 * np.pi * x)


def _run_burgers_cfweno(nx: int, cfl: float, final_time: float,
                        predictor_iterations: int = 1) -> dict:
    """Run CFWENO3 Burgers simulation."""
    dx = 1.0 / nx
    x = np.linspace(0, 1, nx, endpoint=False)
    u = _burgers_ic(x)
    u0 = u.copy()
    t = 0.0
    n_steps = 0
    while t < final_time - 1e-12:
        max_speed = np.max(np.abs(u))
        dt = min(cfl * dx / max(max_speed, 1e-10), final_time - t)
        u = cfweno_burgers(u, dx, dt, predictor_iterations=predictor_iterations)
        t += dt
        n_steps += 1
    return {"x": x, "u0": u0, "u_num": u, "dx": dx, "n_steps": n_steps,
            "actual_final_time": t}


def _run_burgers_rusanov(nx: int, cfl: float, final_time: float) -> dict:
    """Run local Lax-Friedrichs (Rusanov) Burgers baseline."""
    dx = 1.0 / nx
    x = np.linspace(0, 1, nx, endpoint=False)
    u = _burgers_ic(x)
    t = 0.0
    n_steps = 0
    while t < final_time - 1e-12:
        max_speed = np.max(np.abs(u))
        dt = min(cfl * dx / max(max_speed, 1e-10), final_time - t)
        u = burgers_upwind(u, dx, dt)
        t += dt
        n_steps += 1
    return {"x": x, "u_num": u, "dx": dx, "n_steps": n_steps,
            "actual_final_time": t}


def _interp_to_coarse(fine_x, fine_u, coarse_x):
    """Interpolate fine-grid solution to coarse grid (periodic)."""
    dx_fine = fine_x[1] - fine_x[0]
    # Periodic interpolation
    fine_x_ext = np.concatenate([fine_x - 1.0, fine_x, fine_x + 1.0])
    fine_u_ext = np.concatenate([fine_u, fine_u, fine_u])
    return np.interp(coarse_x, fine_x_ext, fine_u_ext)


def _compute_errors(u_num, u_ref, dx):
    diff = u_num - u_ref
    l1 = np.sum(np.abs(diff)) * dx
    l2 = np.sqrt(np.sum(diff**2) * dx)
    linf = np.max(np.abs(diff))
    mass_err = abs(np.sum(u_num) - np.sum(u_ref)) * dx
    return {"l1_error": l1, "l2_error": l2, "linf_error": linf,
            "mass_error": mass_err}


def main() -> None:
    print(f"Burgers CFWENO3 demo: nx={NX}, CFL={CFL}, T={FINAL_TIME}")
    print(f"IC: u0 = 1 + {IC_AMP}*sin(2*pi*x), predictor_iterations={PREDICTOR_ITERS}")

    # Reference solution (fine grid)
    print("Computing reference solution (nx=2560) ...")
    ref = _run_burgers_cfweno(2560, CFL, FINAL_TIME,
                              predictor_iterations=PREDICTOR_ITERS)

    # Coarse-grid runs
    runs = {}
    for label, runner in [("rusanov", lambda: _run_burgers_rusanov(NX, CFL, FINAL_TIME)),
                          ("cfweno_burgers", lambda: _run_burgers_cfweno(
                              NX, CFL, FINAL_TIME, PREDICTOR_ITERS))]:
        print(f"Running {label} ...")
        runs[label] = runner()

    x = runs["cfweno_burgers"]["x"]
    dx = runs["cfweno_burgers"]["dx"]

    # Interpolate reference to coarse grid
    u_ref = _interp_to_coarse(ref["x"], ref["u_num"], x)

    rows = []
    for label, res in runs.items():
        errs = _compute_errors(res["u_num"], u_ref, dx)
        rows.append({
            "method": label,
            "nx": NX,
            "cfl": CFL,
            "final_time": res["actual_final_time"],
            "predictor_iterations": PREDICTOR_ITERS if "cfweno" in label else 0,
            "reference": "cfweno_burgers_nx2560",
            "l1_error": errs["l1_error"],
            "l2_error": errs["l2_error"],
            "linf_error": errs["linf_error"],
            "mass_error": errs["mass_error"],
        })
        print(f"  {label:>20s}  L2={errs['l2_error']:.6e}  "
              f"Linf={errs['linf_error']:.6e}  mass={errs['mass_error']:.2e}")

    # error_summary.csv
    csv_path = os.path.join(RESULTS_DIR, "error_summary.csv")
    fieldnames = list(rows[0].keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nCSV saved to {csv_path}")

    # line_profile.csv
    profile_path = os.path.join(RESULTS_DIR, "line_profile.csv")
    with open(profile_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "reference", "rusanov", "cfweno_burgers"])
        for i in range(len(x)):
            writer.writerow([
                f"{x[i]:.10f}",
                f"{u_ref[i]:.10f}",
                f"{runs['rusanov']['u_num'][i]:.10f}",
                f"{runs['cfweno_burgers']['u_num'][i]:.10f}",
            ])
    print(f"Profile saved to {profile_path}")

    # plot (optional)
    png_path = os.path.join(RESULTS_DIR, "cfweno_burgers_comparison.png")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        ax = axes[0]
        ax.plot(x, u_ref, "k-", linewidth=2, label="Reference (nx=2560)")
        for label in ["rusanov", "cfweno_burgers"]:
            ax.plot(x, runs[label]["u_num"], "--", linewidth=1.5, label=label)
        ax.set_xlabel("x")
        ax.set_ylabel("u")
        ax.set_title(f"Burgers CFWENO3 vs baseline  nx={NX} CFL={CFL}")
        ax.legend()
        ax.grid(True, alpha=0.3)

        ax = axes[1]
        for label in ["rusanov", "cfweno_burgers"]:
            ax.semilogy(x, np.abs(runs[label]["u_num"] - u_ref),
                        linewidth=1.5, label=f"{label} |error|")
        ax.set_xlabel("x")
        ax.set_ylabel("|u_num - u_ref|")
        ax.set_title("Pointwise error vs reference")
        ax.legend()
        ax.grid(True, alpha=0.3)

        fig.tight_layout()
        fig.savefig(png_path, dpi=150)
        plt.close(fig)
        print(f"Plot saved to {png_path}")
    except ImportError:
        print("matplotlib not available — skipping plot.")

    # analysis.md
    md_path = os.path.join(RESULTS_DIR, "analysis.md")
    with open(md_path, "w") as f:
        f.write("# CFWENO3 Burgers Scalar Prototype — Demo Results\n\n")
        f.write("## Source\n\n")
        f.write("- **Paper**: Zhou-Dong-Pan (2025), *Physics of Fluids* 37, 106131\n")
        f.write("- **Equation**: u_t + (u^2/2)_x = 0 (1D scalar nonlinear Burgers)\n")
        f.write("- **Stencil**: Eq. (30) — CFWENO3 with per-cell nu = dt * a_i / dx\n")
        f.write("- **Spec**: `docs/scheme_specs/cfweno_scalar_burgers_subset.md`\n\n")
        f.write("## What This Is\n\n")
        f.write("- A **1D scalar nonlinear Burgers CFWENO3 prototype**\n")
        f.write("- Single-stage, compact stencil scheme with SFM flux linearization\n")
        f.write("- **Pre-shock only** — final_time before shock formation\n")
        f.write("- **Not** shock-capturing — no claim of oscillation control\n")
        f.write("- **Not** the full CFWENO scheme (no Euler, no 2D, no CFWENO5/7)\n\n")
        f.write("## Parameters\n\n")
        f.write(f"- nx = {NX}\n")
        f.write(f"- CFL = {CFL}\n")
        f.write(f"- final_time = {FINAL_TIME}\n")
        f.write(f"- IC: u0 = 1 + {IC_AMP} * sin(2*pi*x)\n")
        f.write(f"- predictor_iterations = {PREDICTOR_ITERS}\n")
        f.write(f"- Reference: CFWENO3 Burgers on nx=2560 grid (numerical reference)\n")
        f.write("- BC: periodic\n\n")
        f.write("## Error Summary\n\n")
        f.write("| Method | L1 | L2 | Linf | Mass |\n")
        f.write("|--------|----|----|------|------|\n")
        for r in rows:
            f.write(f"| {r['method']} | {r['l1_error']:.6e} | "
                    f"{r['l2_error']:.6e} | {r['linf_error']:.6e} | "
                    f"{r['mass_error']:.6e} |\n")
        f.write("\n## Notes\n\n")
        f.write("- Reference is a **numerical reference** (fine-grid CFWENO3), not an exact analytic solution.\n")
        f.write("- Errors are measured against the interpolated reference.\n")
        f.write("- Pre-shock smooth case only — results may differ for post-shock.\n")
        f.write("- Mass conservation should hold to near machine precision.\n")
    print(f"Analysis saved to {md_path}")


if __name__ == "__main__":
    main()
