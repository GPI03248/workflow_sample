"""Compare upwind vs Lax-Wendroff against the analytic advection solution.

Outputs:
  results/advection_error_summary.csv
  results/advection_solution_comparison.png   (if matplotlib is available)
  results/advection_analysis.md
"""

import csv
import os
import sys

# Ensure project root is on sys.path so `solver` is importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solver.simulate import compute_errors, run_advection

# ---- parameters -----------------------------------------------------------
NX = 100
CFL = 0.5
FINAL_TIME = 0.25
A = 1.0
SCHEMES = ["upwind", "lax_wendroff"]

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def main() -> None:
    rows = []
    plot_data = {}

    for scheme_name in SCHEMES:
        print(f"Running {scheme_name} ...")
        res = run_advection(scheme_name, nx=NX, cfl=CFL, final_time=FINAL_TIME, a=A)
        errs = compute_errors(res["u_num"], res["u_exact"], res["dx"])

        rows.append({
            "scheme": scheme_name,
            "nx": NX,
            "cfl": CFL,
            "final_time": FINAL_TIME,
            "actual_final_time": res["actual_final_time"],
            **errs,
        })
        plot_data[scheme_name] = res
        print(f"  L1={errs['l1_error']:.6e}  L2={errs['l2_error']:.6e}  "
              f"Linf={errs['linf_error']:.6e}  mass={errs['mass_error']:.6e}")

    # ---- CSV ---------------------------------------------------------------
    csv_path = os.path.join(RESULTS_DIR, "advection_error_summary.csv")
    fieldnames = list(rows[0].keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nCSV saved to {csv_path}")

    # ---- plot (optional) ---------------------------------------------------
    png_path = os.path.join(RESULTS_DIR, "advection_solution_comparison.png")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        ref = plot_data[SCHEMES[0]]
        x = ref["x"]
        u_exact = ref["u_exact"]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(x, u_exact, "k-", linewidth=2, label="Analytic")
        for scheme_name in SCHEMES:
            ax.plot(x, plot_data[scheme_name]["u_num"], "--",
                    linewidth=1.5, label=scheme_name)
        ax.set_xlabel("x")
        ax.set_ylabel("u")
        ax.set_title(
            f"1D Advection: u_t + u_x = 0   "
            f"nx={NX}, CFL={CFL}, t={ref['actual_final_time']:.4f}"
        )
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(png_path, dpi=150)
        plt.close(fig)
        print(f"Plot saved to {png_path}")
    except ImportError:
        print("matplotlib not available — skipping plot.")

    # ---- analysis markdown -------------------------------------------------
    md_path = os.path.join(RESULTS_DIR, "advection_analysis.md")
    with open(md_path, "w") as f:
        f.write("# Advection Benchmark Analysis\n\n")
        f.write("## PDE Problem Setup\n\n")
        f.write("Equation:  u_t + a * u_x = 0,  a = 1.0\n\n")
        f.write("Domain:  x in [0, 1), periodic boundary\n\n")
        f.write(f"Initial condition:  u(x, 0) = sin(2*pi*x) + 1\n\n")
        f.write("## Analytic Solution\n\n")
        f.write("u_exact(x, t) = sin(2*pi*(x - a*t)) + 1\n\n")
        f.write("## Numerical Parameters\n\n")
        f.write(f"- nx = {NX}\n")
        f.write(f"- CFL = {CFL}\n")
        f.write(f"- requested final_time = {FINAL_TIME}\n")
        f.write(f"- actual final_time = {rows[0]['actual_final_time']:.6f}\n\n")
        f.write("## Error Summary\n\n")
        f.write("| Scheme | L1 | L2 | Linf | Mass |\n")
        f.write("|--------|----|----|------|------|\n")
        for r in rows:
            f.write(f"| {r['scheme']} | {r['l1_error']:.6e} | "
                    f"{r['l2_error']:.6e} | {r['linf_error']:.6e} | "
                    f"{r['mass_error']:.6e} |\n")
        f.write("\n## Qualitative Observations\n\n")
        f.write("- **Upwind** is a first-order scheme. It introduces significant "
                "numerical dissipation, which smooths the solution and reduces "
                "the peak amplitude. For smooth periodic problems this "
                "dissipation is the dominant error source.\n\n")
        f.write("- **Lax-Wendroff** is a second-order scheme. It has lower "
                "dissipation than upwind on smooth solutions, typically yielding "
                "smaller L2 errors. However, it introduces dispersive oscillations "
                "that can become pronounced near discontinuities or sharp "
                "gradients.\n\n")
        f.write("- The current benchmark uses a **smooth, periodic** initial "
                "condition (sinusoidal). Results here do **not** generalise to "
                "all CFD problems — discontinuous or multi-dimensional cases "
                "may show very different behaviour.\n\n")
        f.write("- The purpose of this sample is to demonstrate a **repeatable "
                "verification mechanism** using an analytic solution, not to "
                "claim that one scheme is universally better than another.\n")
    print(f"Analysis saved to {md_path}")


if __name__ == "__main__":
    main()
