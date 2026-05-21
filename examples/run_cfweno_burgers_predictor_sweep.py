"""CFWENO3 Burgers predictor sensitivity study.

Tests predictor_iterations = 0, 1, 2 on smooth pre-shock Burgers at
multiple grid sizes to quantify the effect of the predictor on accuracy
and convergence order.

Outputs (results/cfweno_burgers_predictor_sweep/):
  error_summary.csv
  analysis.md
"""

import csv
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solver.schemes import cfweno_burgers

PREDICTOR_LIST = [0, 1, 2]
NX_LIST = [80, 160, 320]
CFL = 0.5
FINAL_TIME = 0.1
IC_AMP = 0.2
NX_REF = 2560

RESULTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "results", "cfweno_burgers_predictor_sweep"
)
os.makedirs(RESULTS_DIR, exist_ok=True)


def _burgers_ic(x):
    return 1.0 + IC_AMP * np.sin(2.0 * np.pi * x)


def _run(nx, cfl, final_time, predictor_iterations):
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


def _interp_to_coarse(fine_x, fine_u, coarse_x):
    fine_x_ext = np.concatenate([fine_x - 1.0, fine_x, fine_x + 1.0])
    fine_u_ext = np.concatenate([fine_u, fine_u, fine_u])
    return np.interp(coarse_x, fine_x_ext, fine_u_ext)


def _compute_errors(u_num, u_ref, dx):
    diff = u_num - u_ref
    l1 = np.sum(np.abs(diff)) * dx
    l2 = np.sqrt(np.sum(diff**2) * dx)
    linf = np.max(np.abs(diff))
    return {"l1_error": l1, "l2_error": l2, "linf_error": linf}


def _convergence_order(errors, dxs):
    orders = []
    for i in range(1, len(errors)):
        if errors[i] > 0 and errors[i - 1] > 0:
            orders.append(math.log(errors[i - 1] / errors[i])
                          / math.log(dxs[i - 1] / dxs[i]))
    return orders


def main() -> None:
    print(f"Predictor sweep: iters={PREDICTOR_LIST}, nx={NX_LIST}, CFL={CFL}, T={FINAL_TIME}")
    print(f"IC: u0 = 1 + {IC_AMP}*sin(2*pi*x)")

    # Reference — use predictor_iterations=1 (default)
    print("Computing reference (nx=2560, predictor=1) ...")
    ref = _run(NX_REF, CFL, FINAL_TIME, 1)

    rows = []
    pred_errors = {p: {"l2": [], "dx": []} for p in PREDICTOR_LIST}

    for p in PREDICTOR_LIST:
        for nx in NX_LIST:
            res = _run(nx, CFL, FINAL_TIME, p)
            u_ref = _interp_to_coarse(ref["x"], ref["u_num"], res["x"])
            errs = _compute_errors(res["u_num"], u_ref, res["dx"])
            rows.append({
                "predictor_iterations": p,
                "nx": nx,
                "dx": res["dx"],
                "l1_error": errs["l1_error"],
                "l2_error": errs["l2_error"],
                "linf_error": errs["linf_error"],
            })
            pred_errors[p]["l2"].append(errs["l2_error"])
            pred_errors[p]["dx"].append(res["dx"])
            print(f"  predictor={p}  nx={nx:4d}  L2={errs['l2_error']:.6e}")

    # error_summary.csv
    csv_path = os.path.join(RESULTS_DIR, "error_summary.csv")
    fieldnames = list(rows[0].keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nCSV saved to {csv_path}")

    # Compute convergence orders
    order_info = {}
    for p in PREDICTOR_LIST:
        orders = _convergence_order(pred_errors[p]["l2"], pred_errors[p]["dx"])
        avg = sum(orders) / len(orders) if orders else float("nan")
        order_info[p] = {"orders": orders, "avg": avg}

    # analysis.md
    md_path = os.path.join(RESULTS_DIR, "analysis.md")
    with open(md_path, "w") as f:
        f.write("# CFWENO3 Burgers Predictor Sensitivity Study\n\n")
        f.write("## Setup\n\n")
        f.write("Equation: u_t + (u^2/2)_x = 0, periodic BC\n\n")
        f.write(f"Predictor iterations: {PREDICTOR_LIST}\n\n")
        f.write(f"Grid sizes: {NX_LIST}\n\n")
        f.write(f"Reference: CFWENO3 Burgers nx={NX_REF}, predictor=1\n\n")
        f.write(f"CFL = {CFL}, final_time = {FINAL_TIME}\n\n")
        f.write(f"IC: u(x,0) = 1 + {IC_AMP}*sin(2*pi*x)\n\n")

        f.write("## Error Table\n\n")
        f.write("| Predictor | nx | L1 | L2 | Linf |\n")
        f.write("|-----------|----|----|----|------|\n")
        for r in rows:
            f.write(f"| {r['predictor_iterations']} | {r['nx']} | "
                    f"{r['l1_error']:.6e} | {r['l2_error']:.6e} | "
                    f"{r['linf_error']:.6e} |\n")

        f.write("\n## Convergence Orders (L2)\n\n")
        f.write("| Predictor | Order (80->160) | Order (160->320) | Average |\n")
        f.write("|-----------|----------------|------------------|----------|\n")
        for p in PREDICTOR_LIST:
            oi = order_info[p]
            o = oi["orders"]
            if len(o) >= 2:
                f.write(f"| {p} | {o[0]:.4f} | {o[1]:.4f} | {oi['avg']:.4f} |\n")
            elif len(o) == 1:
                f.write(f"| {p} | {o[0]:.4f} | — | {oi['avg']:.4f} |\n")
            else:
                f.write(f"| {p} | — | — | — |\n")

        f.write("\n## Analysis\n\n")

        # Which predictor is best?
        best_at_320 = min(PREDICTOR_LIST,
                          key=lambda p: next(r["l2_error"] for r in rows
                                             if r["predictor_iterations"] == p and r["nx"] == 320))
        f.write(f"### Which predictor has smallest error?\n\n")
        for nx in NX_LIST:
            best = min(PREDICTOR_LIST,
                       key=lambda p: next(r["l2_error"] for r in rows
                                          if r["predictor_iterations"] == p and r["nx"] == nx))
            l2_best = next(r["l2_error"] for r in rows
                           if r["predictor_iterations"] == best and r["nx"] == nx)
            f.write(f"- nx={nx}: predictor={best} (L2={l2_best:.6e})\n")

        f.write(f"\n### Does predictor improve convergence order?\n\n")
        all_orders = [order_info[p]["avg"] for p in PREDICTOR_LIST]
        max_order = max(all_orders)
        min_order = min(all_orders)
        if max_order - min_order < 0.3:
            f.write(f"All predictors yield approximately the same convergence order "
                    f"(range: {min_order:.2f}–{max_order:.2f}). "
                    f"The predictor does **not** significantly change the convergence rate.\n\n")
        else:
            best_pred = max(PREDICTOR_LIST, key=lambda p: order_info[p]["avg"])
            f.write(f"Predictor={best_pred} has the highest convergence order "
                    f"({order_info[best_pred]['avg']:.2f}). "
                    f"Order range: {min_order:.2f}–{max_order:.2f}.\n\n")

        f.write(f"### Is default predictor_iterations=1 still reasonable?\n\n")
        default_l2_320 = next(r["l2_error"] for r in rows
                              if r["predictor_iterations"] == 1 and r["nx"] == 320)
        best_l2_320 = next(r["l2_error"] for r in rows
                           if r["predictor_iterations"] == best_at_320 and r["nx"] == 320)
        if best_at_320 == 1:
            f.write("Yes — predictor_iterations=1 is the best or tied for best at the finest "
                    "resolution. The default is appropriate.\n\n")
        else:
            ratio = default_l2_320 / best_l2_320 if best_l2_320 > 0 else float("inf")
            f.write(f"Predictor={best_at_320} is slightly better at nx=320 "
                    f"(L2 ratio: {ratio:.2f}x). ")
            if ratio < 1.5:
                f.write("However, the improvement is small (< 1.5x), so "
                        "predictor_iterations=1 remains a reasonable default.\n\n")
            else:
                f.write(f"The improvement is notable ({ratio:.2f}x). "
                        f"Consider changing the default to {best_at_320}.\n\n")

        f.write("### Does the predictor need redesign?\n\n")
        if max_order - min_order < 0.3 and max(all_orders) < 2.5:
            f.write("No urgent redesign needed. All predictors yield ~2nd-order convergence, "
                    "consistent with the per-cell nu variation limitation documented in the "
                    "audit. A more fundamental change (e.g., nonlinear WENO weights or "
                    "higher-order interface reconstruction) would be needed to improve "
                    "convergence order.\n\n")
        else:
            f.write(f"Predictor={max(PREDICTOR_LIST, key=lambda p: order_info[p]['avg'])} "
                    f"shows improved convergence. Further investigation may be warranted.\n\n")

        f.write("### Scope limitation\n\n")
        f.write("This study only covers smooth pre-shock Burgers (T=0.1, T_shock≈0.253). "
                "Post-shock behavior is not tested and would require nonlinear WENO weights "
                "(Eq. 17) not yet implemented.\n")

    print(f"Analysis saved to {md_path}")


if __name__ == "__main__":
    main()
