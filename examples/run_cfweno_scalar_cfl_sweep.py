"""CFWENO3 scalar CFL sweep — stability and accuracy at different CFL numbers.

Tests CFWENO3 at CFL = 0.1, 0.5, 0.9 on smooth linear advection.

Outputs (results/cfweno_scalar_cfl_sweep/):
  error_summary.csv
  analysis.md
"""

import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solver.simulate import compute_errors, run_advection

CFL_LIST = [0.1, 0.5, 0.9]
NX = 160
FINAL_TIME = 0.25
A = 1.0

RESULTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "results", "cfweno_scalar_cfl_sweep"
)
os.makedirs(RESULTS_DIR, exist_ok=True)


def main() -> None:
    rows = []

    for cfl in CFL_LIST:
        res = run_advection("cfweno", nx=NX, cfl=cfl, final_time=FINAL_TIME, a=A)
        errs = compute_errors(res["u_num"], res["u_exact"], res["dx"])
        rows.append({
            "method": "cfweno",
            "nx": NX,
            "cfl": cfl,
            "final_time": res["actual_final_time"],
            "n_steps": res["n_steps"],
            "l1_error": errs["l1_error"],
            "l2_error": errs["l2_error"],
            "linf_error": errs["linf_error"],
            "mass_error": errs["mass_error"],
        })
        has_nan = "NaN!" if any(
            x != x for x in [errs["l1_error"], errs["l2_error"]]
        ) else "ok"
        print(f"  CFL={cfl:.1f}  L2={errs['l2_error']:.6e}  "
              f"mass={errs['mass_error']:.2e}  {has_nan}")

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
        f.write("# CFWENO3 Scalar CFL Sweep\n\n")
        f.write("## Setup\n\n")
        f.write("Equation: u_t + a*u_x = 0, a = 1.0, periodic BC\n\n")
        f.write(f"Grid: nx = {NX}\n\n")
        f.write(f"CFL values tested: {CFL_LIST}\n\n")
        f.write(f"final_time = {FINAL_TIME}\n\n")
        f.write("IC: u(x,0) = sin(2*pi*x) + 1\n\n")
        f.write("## Results\n\n")
        f.write("| CFL | Steps | L1 | L2 | Linf | Mass |\n")
        f.write("|-----|-------|----|----|------|------|\n")
        for r in rows:
            f.write(f"| {r['cfl']} | {r['n_steps']} | "
                    f"{r['l1_error']:.6e} | {r['l2_error']:.6e} | "
                    f"{r['linf_error']:.6e} | {r['mass_error']:.2e} |\n")
        f.write("\n## Notes\n\n")
        f.write("- CFL=0.9 is an **empirical verification** on this smooth case.\n")
        f.write("- This is **not** a rigorous stability proof.\n")
        f.write("- Results are valid only for this specific smooth linear advection case.\n")
        f.write("- All runs used the same grid resolution (nx=160).\n")
        f.write("- Mass conservation should hold to near machine precision.\n")
        f.write("- If any CFL value produces NaN or divergent results,\n")
        f.write("  that constitutes a failure and should be reported honestly.\n")
    print(f"Analysis saved to {md_path}")


if __name__ == "__main__":
    main()
