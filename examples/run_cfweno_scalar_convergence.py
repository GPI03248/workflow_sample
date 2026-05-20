"""CFWENO3 scalar convergence study — grid refinement.

Runs CFWENO3 and upwind on u_t + a*u_x = 0 at multiple grid sizes,
computes error norms, and estimates convergence order.

Outputs (results/cfweno_scalar_convergence/):
  error_summary.csv
  analysis.md
"""

import csv
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solver.simulate import compute_errors, run_advection

NX_LIST = [40, 80, 160, 320]
CFL = 0.5
FINAL_TIME = 0.25
A = 1.0
SCHEMES = ["upwind", "cfweno"]

RESULTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "results", "cfweno_scalar_convergence"
)
os.makedirs(RESULTS_DIR, exist_ok=True)


def _convergence_order(errors, dxs):
    """Estimate convergence order from (error, dx) pairs via log-log slope."""
    orders = []
    for i in range(1, len(errors)):
        if errors[i] > 0 and errors[i - 1] > 0:
            orders.append(math.log(errors[i - 1] / errors[i])
                          / math.log(dxs[i - 1] / dxs[i]))
    return orders


def main() -> None:
    rows = []
    dx_list = []
    scheme_errors = {s: {"l1": [], "l2": [], "linf": []} for s in SCHEMES}

    for nx in NX_LIST:
        for name in SCHEMES:
            res = run_advection(name, nx=nx, cfl=CFL, final_time=FINAL_TIME, a=A)
            errs = compute_errors(res["u_num"], res["u_exact"], res["dx"])
            rows.append({
                "method": name,
                "nx": nx,
                "dx": res["dx"],
                "cfl": CFL,
                "final_time": res["actual_final_time"],
                "n_steps": res["n_steps"],
                "l1_error": errs["l1_error"],
                "l2_error": errs["l2_error"],
                "linf_error": errs["linf_error"],
                "mass_error": errs["mass_error"],
            })
            scheme_errors[name]["l1"].append(errs["l1_error"])
            scheme_errors[name]["l2"].append(errs["l2_error"])
            scheme_errors[name]["linf"].append(errs["linf_error"])
            if name == SCHEMES[0]:
                dx_list.append(res["dx"])
            print(f"  {name:>15s}  nx={nx:4d}  L2={errs['l2_error']:.6e}")

    # error_summary.csv
    csv_path = os.path.join(RESULTS_DIR, "error_summary.csv")
    fieldnames = list(rows[0].keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nCSV saved to {csv_path}")

    # analysis.md
    md_path = os.path.join(RESULTS_DIR, "analysis.md")
    with open(md_path, "w") as f:
        f.write("# CFWENO3 Scalar Convergence Study\n\n")
        f.write("## Setup\n\n")
        f.write("Equation: u_t + a*u_x = 0, a = 1.0, periodic BC\n\n")
        f.write(f"Grid sizes: {NX_LIST}\n\n")
        f.write(f"CFL = {CFL}, final_time = {FINAL_TIME}\n\n")
        f.write("IC: u(x,0) = sin(2*pi*x) + 1\n\n")
        f.write("## Error Table\n\n")
        f.write("| Method | nx | dx | L1 | L2 | Linf | Mass |\n")
        f.write("|--------|----|----|----|----|------|------|\n")
        for r in rows:
            f.write(f"| {r['method']} | {r['nx']} | {r['dx']:.4e} | "
                    f"{r['l1_error']:.6e} | {r['l2_error']:.6e} | "
                    f"{r['linf_error']:.6e} | {r['mass_error']:.6e} |\n")
        f.write("\n## Convergence Orders (L2)\n\n")
        f.write("| Method | Order estimate | Expected |\n")
        f.write("|--------|---------------|----------|\n")
        for name in SCHEMES:
            orders = _convergence_order(scheme_errors[name]["l2"], dx_list)
            if orders:
                avg_order = sum(orders) / len(orders)
                expected = 3.0 if name == "cfweno" else 1.0
                f.write(f"| {name} | {avg_order:.2f} (from {orders}) "
                        f"| {expected:.1f} |\n")
            else:
                f.write(f"| {name} | N/A | — |\n")
        f.write("\n## Notes\n\n")
        f.write("- CFWENO3 is a 3rd-order compact fully-discrete scheme\n")
        f.write("- Target convergence order is ~3.0 for L2 error\n")
        f.write("- This is a prototype — exact convergence order may vary\n")
        f.write("- Upwind is 1st-order (baseline)\n")
    print(f"Analysis saved to {md_path}")


if __name__ == "__main__":
    main()
