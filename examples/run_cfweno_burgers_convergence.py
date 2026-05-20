"""CFWENO3 Burgers convergence study — grid refinement.

Runs CFWENO3 Burgers and Rusanov baseline on u_t + (u^2/2)_x = 0
at multiple grid sizes, measures error vs fine-grid reference.

Outputs (results/cfweno_burgers_convergence/):
  error_summary.csv
  analysis.md
"""

import csv
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solver.schemes import burgers_upwind, cfweno_burgers

NX_LIST = [40, 80, 160, 320]
CFL = 0.5
FINAL_TIME = 0.15
IC_AMP = 0.2
PREDICTOR_ITERS = 1
NX_REF = 2560

RESULTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "results", "cfweno_burgers_convergence"
)
os.makedirs(RESULTS_DIR, exist_ok=True)


def _burgers_ic(x):
    return 1.0 + IC_AMP * np.sin(2.0 * np.pi * x)


def _run_cfweno_burgers(nx, cfl, final_time, predictor_iterations=1):
    dx = 1.0 / nx
    x = np.linspace(0, 1, nx, endpoint=False)
    u = _burgers_ic(x)
    t = 0.0
    n_steps = 0
    while t < final_time - 1e-12:
        max_speed = np.max(np.abs(u))
        dt = min(cfl * dx / max(max_speed, 1e-10), final_time - t)
        u = cfweno_burgers(u, dx, dt, predictor_iterations=predictor_iterations)
        t += dt
        n_steps += 1
    return {"x": x, "u_num": u, "dx": dx, "n_steps": n_steps, "actual_final_time": t}


def _run_rusanov_burgers(nx, cfl, final_time):
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
    return {"x": x, "u_num": u, "dx": dx, "n_steps": n_steps, "actual_final_time": t}


def _interp_to_coarse(fine_x, fine_u, coarse_x):
    fine_x_ext = np.concatenate([fine_x - 1.0, fine_x, fine_x + 1.0])
    fine_u_ext = np.concatenate([fine_u, fine_u, fine_u])
    return np.interp(coarse_x, fine_x_ext, fine_u_ext)


def _compute_errors(u_num, u_ref, dx):
    diff = u_num - u_ref
    l1 = np.sum(np.abs(diff)) * dx
    l2 = np.sqrt(np.sum(diff**2) * dx)
    linf = np.max(np.abs(diff))
    mass_err = abs(np.sum(u_num) - np.sum(u_ref)) * dx
    return {"l1_error": l1, "l2_error": l2, "linf_error": linf, "mass_error": mass_err}


def _convergence_order(errors, dxs):
    orders = []
    for i in range(1, len(errors)):
        if errors[i] > 0 and errors[i - 1] > 0:
            orders.append(math.log(errors[i - 1] / errors[i])
                          / math.log(dxs[i - 1] / dxs[i]))
    return orders


def main() -> None:
    print(f"Burgers convergence: nx={NX_LIST}, CFL={CFL}, T={FINAL_TIME}")
    print(f"IC: u0 = 1 + {IC_AMP}*sin(2*pi*x), predictor_iterations={PREDICTOR_ITERS}")

    # Reference
    print("Computing reference (nx=2560) ...")
    ref = _run_cfweno_burgers(NX_REF, CFL, FINAL_TIME, PREDICTOR_ITERS)

    rows = []
    dx_list = []
    scheme_errors = {"rusanov": {"l2": []}, "cfweno_burgers": {"l2": []}}

    for nx in NX_LIST:
        for name, runner in [("rusanov", lambda n=nx: _run_rusanov_burgers(n, CFL, FINAL_TIME)),
                             ("cfweno_burgers", lambda n=nx: _run_cfweno_burgers(
                                 n, CFL, FINAL_TIME, PREDICTOR_ITERS))]:
            res = runner()
            u_ref = _interp_to_coarse(ref["x"], ref["u_num"], res["x"])
            errs = _compute_errors(res["u_num"], u_ref, res["dx"])
            rows.append({
                "method": name,
                "nx": nx,
                "dx": res["dx"],
                "cfl": CFL,
                "final_time": res["actual_final_time"],
                "n_steps": res["n_steps"],
                "predictor_iterations": PREDICTOR_ITERS if "cfweno" in name else 0,
                "reference": f"cfweno_burgers_nx{NX_REF}",
                "l1_error": errs["l1_error"],
                "l2_error": errs["l2_error"],
                "linf_error": errs["linf_error"],
                "mass_error": errs["mass_error"],
            })
            scheme_errors[name]["l2"].append(errs["l2_error"])
            if name == "rusanov":
                dx_list.append(res["dx"])
            print(f"  {name:>20s}  nx={nx:4d}  L2={errs['l2_error']:.6e}")

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
        f.write("# CFWENO3 Burgers Convergence Study\n\n")
        f.write("## Setup\n\n")
        f.write("Equation: u_t + (u^2/2)_x = 0, periodic BC\n\n")
        f.write(f"Grid sizes: {NX_LIST}\n\n")
        f.write(f"Reference: CFWENO3 Burgers nx={NX_REF}\n\n")
        f.write(f"CFL = {CFL}, final_time = {FINAL_TIME}\n\n")
        f.write(f"IC: u(x,0) = 1 + {IC_AMP}*sin(2*pi*x)\n\n")
        f.write(f"predictor_iterations = {PREDICTOR_ITERS}\n\n")
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
        for name in ["rusanov", "cfweno_burgers"]:
            orders = _convergence_order(scheme_errors[name]["l2"], dx_list)
            if orders:
                avg = sum(orders) / len(orders)
                expected = 3.0 if "cfweno" in name else 1.0
                f.write(f"| {name} | {avg:.2f} (from {orders}) | ~{expected:.0f} |\n")
        f.write("\n## Notes\n\n")
        f.write("- CFWENO3 Burgers uses per-cell nu = dt * a_i / dx with predictor iterations\n")
        f.write(f"- Default predictor_iterations = {PREDICTOR_ITERS}\n")
        f.write("- Reference is **numerical** (fine-grid CFWENO3), not exact analytic\n")
        f.write("- Pre-shock smooth case only\n")
        f.write("- Convergence orders are approximate due to numerical reference\n")
    print(f"Analysis saved to {md_path}")


if __name__ == "__main__":
    main()
