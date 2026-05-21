"""CFWENO3 Burgers nonlinear order recovery — diagnostic study.

Post-v1.0 diagnostic: tests several nu-treatment variants to determine
whether 3rd-order convergence can be recovered for scalar Burgers CFWENO3.

DOES NOT modify solver/schemes.py.  All diagnostic variants are implemented
as private helpers within this script.

Outputs (results/cfweno_burgers_order_recovery/):
  error_summary.csv
  analysis.md

Usage:
  python examples/run_cfweno_burgers_order_recovery.py
  python examples/run_cfweno_burgers_order_recovery.py --quick   # fast test mode
"""

import argparse
import csv
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solver.schemes import _cfweno3_stencil, _interface_reconstruction, cfweno_burgers

RESULTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "results", "cfweno_burgers_order_recovery"
)

# --- Diagnostic variant helpers ------------------------------------------------
# These reimplement the CFWENO3 Burgers step with different nu treatments.
# They do NOT modify solver/schemes.py.


def _diag_constant_nu(u, dx, dt):
    """Variant B: constant global nu = tau * mean(u) / dx."""
    tau_h = dt / dx
    nu_scalar = tau_h * np.mean(u)
    nu = np.full_like(u, np.clip(nu_scalar, 0.0, 1.0))
    ubar_right = _cfweno3_stencil(u, nu)
    f_hat_right = 0.5 * ubar_right**2
    f_hat_left = np.roll(f_hat_right, 1)
    return u - tau_h * (f_hat_right - f_hat_left)


def _diag_interface_nu(u, dx, dt):
    """Variant C: nu computed from 4th-order reconstructed interface values."""
    tau_h = dt / dx
    u_half_right = _interface_reconstruction(u)
    u_half_left = np.roll(u_half_right, 1)
    # Average of left and right interface states at i+1/2
    a_interface = 0.5 * (u_half_right + np.roll(u, -1))
    # But simpler: use the reconstructed value directly as speed at i+1/2
    # nu per-interface (same shape as u_half_right)
    nu_interface = np.clip(tau_h * u_half_right, 0.0, 1.0)
    # Apply stencil with interface-level nu
    ubar_right = (u_half_right
                  - nu_interface * (u_half_right - u)
                  - nu_interface * (1.0 - nu_interface)
                  * (u_half_left - 2.0 * u + u_half_right))
    f_hat_right = 0.5 * ubar_right**2
    f_hat_left = np.roll(f_hat_right, 1)
    return u - tau_h * (f_hat_right - f_hat_left)


def _diag_predictor_interface_nu(u, dx, dt, predictor_iterations=1):
    """Variant D: predictor-updated interface-speed nu."""
    tau_h = dt / dx
    a = u.copy()

    for _ in range(predictor_iterations):
        u_half_right = _interface_reconstruction(u)
        a_interface = u_half_right  # use interface reconstruction as speed
        nu_interface = np.clip(tau_h * a_interface, 0.0, 1.0)
        u_half_left = np.roll(u_half_right, 1)
        ubar_right = (u_half_right
                      - nu_interface * (u_half_right - u)
                      - nu_interface * (1.0 - nu_interface)
                      * (u_half_left - 2.0 * u + u_half_right))
        ubar_left = np.roll(ubar_right, 1)
        a = 0.5 * (ubar_right + ubar_left)

    # Final step with predictor-refined a used as interface nu
    u_half_right = _interface_reconstruction(u)
    nu_final = np.clip(tau_h * a, 0.0, 1.0)
    ubar_right = _cfweno3_stencil(u, nu_final)
    f_hat_right = 0.5 * ubar_right**2
    f_hat_left = np.roll(f_hat_right, 1)
    return u - tau_h * (f_hat_right - f_hat_left)


# --- Shared utilities ----------------------------------------------------------


def _burgers_ic(x, amplitude=0.2):
    return 1.0 + amplitude * np.sin(2.0 * np.pi * x)


def _run_variant(variant_fn, nx, cfl, final_time, amplitude=0.2, **kwargs):
    """Run a diagnostic variant stepping function."""
    dx = 1.0 / nx
    x = np.linspace(0, 1, nx, endpoint=False)
    u = _burgers_ic(x, amplitude)
    t = 0.0
    n_steps = 0
    while t < final_time - 1e-12:
        max_speed = np.max(np.abs(u))
        dt = min(cfl * dx / max(max_speed, 1e-10), final_time - t)
        u = variant_fn(u, dx, dt, **kwargs)
        t += dt
        n_steps += 1
    return {"x": x, "u_num": u, "dx": dx, "n_steps": n_steps}


def _run_production_cfweno(nx, cfl, final_time, amplitude=0.2, predictor_iterations=1):
    """Run production cfweno_burgers from solver/schemes.py."""
    dx = 1.0 / nx
    x = np.linspace(0, 1, nx, endpoint=False)
    u = _burgers_ic(x, amplitude)
    t = 0.0
    n_steps = 0
    while t < final_time - 1e-12:
        max_speed = np.max(np.abs(u))
        dt = min(cfl * dx / max(max_speed, 1e-10), final_time - t)
        u = cfweno_burgers(u, dx, dt, predictor_iterations=predictor_iterations)
        t += dt
        n_steps += 1
    return {"x": x, "u_num": u, "dx": dx, "n_steps": n_steps}


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
            orders.append(
                math.log(errors[i - 1] / errors[i]) / math.log(dxs[i - 1] / dxs[i])
            )
    return orders


# --- Variant definitions -------------------------------------------------------

VARIANTS = {
    "A_current": {
        "label": "A: current (per-cell nu)",
        "runner": lambda nx, cfl, ft, amp, nx_ref=None: _run_production_cfweno(
            nx, cfl, ft, amplitude=amp, predictor_iterations=1
        ),
    },
    "B_constant_nu": {
        "label": "B: constant global nu",
        "runner": lambda nx, cfl, ft, amp, nx_ref=None: _run_variant(
            _diag_constant_nu, nx, cfl, ft, amplitude=amp
        ),
    },
    "C_interface_nu": {
        "label": "C: interface-speed nu",
        "runner": lambda nx, cfl, ft, amp, nx_ref=None: _run_variant(
            _diag_interface_nu, nx, cfl, ft, amplitude=amp
        ),
    },
    "D_predictor_interface_nu": {
        "label": "D: predictor + interface nu",
        "runner": lambda nx, cfl, ft, amp, nx_ref=None: _run_variant(
            _diag_predictor_interface_nu, nx, cfl, ft, amplitude=amp,
            predictor_iterations=1
        ),
    },
}

# Case configurations
CASES = [
    {"case_id": "standard", "amplitude": 0.2, "final_time": 0.1, "cfl": 0.5,
     "nx_list": [80, 160, 320, 640], "reference_nx": 5120},
    {"case_id": "reduced_amp", "amplitude": 0.05, "final_time": 0.1, "cfl": 0.5,
     "nx_list": [80, 160, 320, 640], "reference_nx": 5120},
    {"case_id": "shorter_time", "amplitude": 0.2, "final_time": 0.05, "cfl": 0.5,
     "nx_list": [80, 160, 320, 640], "reference_nx": 5120},
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CFWENO3 Burgers order recovery diagnostic"
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Quick mode: fewer grids, smaller reference (for testing)"
    )
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)

    if args.quick:
        for case in CASES:
            case["nx_list"] = [40, 80]
            case["reference_nx"] = 320
        # Only run standard case in quick mode
        cases_to_run = [CASES[0]]
    else:
        cases_to_run = CASES

    all_rows = []
    variant_order_data = {}  # {case_id: {variant: {"l2": [...], "dx": [...]}}}

    for case in cases_to_run:
        case_id = case["case_id"]
        amplitude = case["amplitude"]
        final_time = case["final_time"]
        cfl = case["cfl"]
        nx_list = case["nx_list"]
        nx_ref = case["reference_nx"]

        print(f"\n=== Case: {case_id} (amp={amplitude}, T={final_time}, CFL={cfl}) ===")

        # Reference: use production CFWENO3 Burgers at high resolution
        print(f"  Computing reference (nx={nx_ref}) ...")
        ref = _run_production_cfweno(
            nx_ref, cfl, final_time, amplitude=amplitude, predictor_iterations=1
        )

        variant_order_data[case_id] = {}
        dx_list = [1.0 / nx for nx in nx_list]

        for variant_id, vdef in VARIANTS.items():
            l2_errors = []
            print(f"  {vdef['label']} ...")
            for nx in nx_list:
                res = vdef["runner"](nx, cfl, final_time, amplitude, nx_ref)
                u_ref = _interp_to_coarse(ref["x"], ref["u_num"], res["x"])
                errs = _compute_errors(res["u_num"], u_ref, res["dx"])
                row = {
                    "case_id": case_id,
                    "amplitude": amplitude,
                    "variant": variant_id,
                    "nx": nx,
                    "cfl": cfl,
                    "final_time": final_time,
                    "reference_nx": nx_ref,
                    "l1_error": errs["l1_error"],
                    "l2_error": errs["l2_error"],
                    "linf_error": errs["linf_error"],
                    "mass_error": errs["mass_error"],
                    "observed_order": "",
                    "notes": vdef["label"],
                }
                all_rows.append(row)
                l2_errors.append(errs["l2_error"])
                print(f"    nx={nx:4d}  L2={errs['l2_error']:.6e}")

            # Compute per-variant convergence orders
            orders = _convergence_order(l2_errors, dx_list)
            if orders:
                avg_order = sum(orders) / len(orders)
                # Fill observed order into the last entry per variant per case
                for row in reversed(all_rows):
                    if (row["case_id"] == case_id and row["variant"] == variant_id
                            and row["observed_order"] == ""):
                        row["observed_order"] = f"{avg_order:.2f}"
                variant_order_data[case_id][variant_id] = {
                    "l2": l2_errors, "dx": dx_list, "order": avg_order
                }

    # Write CSV
    csv_path = os.path.join(RESULTS_DIR, "error_summary.csv")
    fieldnames = [
        "case_id", "amplitude", "variant", "nx", "cfl", "final_time",
        "reference_nx", "l1_error", "l2_error", "linf_error", "mass_error",
        "observed_order", "notes",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\nCSV saved to {csv_path}")

    # Write analysis.md
    md_path = os.path.join(RESULTS_DIR, "analysis.md")
    with open(md_path, "w") as f:
        f.write("# CFWENO3 Burgers Nonlinear Order Recovery — Diagnostic Study\n\n")
        f.write("**Status**: Post-v1.0 diagnostic (not a production change)\n\n")
        f.write("**Purpose**: Determine whether 3rd-order convergence can be recovered ")
        f.write("for scalar Burgers CFWENO3 by changing the nu treatment.\n\n")
        f.write("**Constraint**: solver/schemes.py was NOT modified.\n\n")

        f.write("## Hypothesis\n\n")
        f.write("The CFWENO3 stencil (Eq. 30) was derived for constant nu. ")
        f.write("For Burgers, per-cell `nu_i = dt * u_i / dx` varies spatially, ")
        f.write("introducing truncation error that reduces convergence to ~2nd order.\n\n")
        f.write("If using a constant or interface-based nu restores ~3rd order, ")
        f.write("it confirms the nu-variation hypothesis and suggests a path to recovery.\n\n")

        f.write("## Diagnostic Variants\n\n")
        f.write("| ID | Variant | nu treatment |\n")
        f.write("|----|---------|-------------|\n")
        f.write("| A | current (production) | per-cell `nu = tau * u_i / h` |\n")
        f.write("| B | constant global nu | `nu = tau * mean(u) / h` |\n")
        f.write("| C | interface-speed nu | `nu` from reconstructed `u_{i+1/2}` |\n")
        f.write("| D | predictor + interface nu | predictor-updated `nu` |\n\n")

        for case in cases_to_run:
            case_id = case["case_id"]
            f.write(f"## Case: {case_id}\n\n")
            f.write(f"- amplitude = {case['amplitude']}\n")
            f.write(f"- final_time = {case['final_time']}\n")
            f.write(f"- CFL = {case['cfl']}\n")
            f.write(f"- nx = {case['nx_list']}\n")
            f.write(f"- reference_nx = {case['reference_nx']}\n\n")

            if case_id not in variant_order_data:
                continue

            f.write("### Error Table\n\n")
            f.write("| Variant | nx | L2 | Observed Order |\n")
            f.write("|---------|----|----|---------------|\n")
            case_rows = [r for r in all_rows if r["case_id"] == case_id]
            for r in case_rows:
                order_str = r["observed_order"] if r["observed_order"] else "—"
                f.write(f"| {r['variant']} | {r['nx']} | {r['l2_error']:.6e} "
                        f"| {order_str} |\n")

            f.write("\n### Convergence Orders (L2)\n\n")
            f.write("| Variant | Avg Order |\n")
            f.write("|---------|----------|\n")
            for vid, vdef in VARIANTS.items():
                if vid in variant_order_data.get(case_id, {}):
                    od = variant_order_data[case_id][vid]
                    f.write(f"| {vdef['label']} | **{od['order']:.2f}** |\n")
            f.write("\n")

        # Conclusions section
        f.write("## Conclusions\n\n")
        # Find best variant across standard case
        std_data = variant_order_data.get("standard", {})
        if std_data:
            best_variant = max(std_data, key=lambda k: std_data[k]["order"])
            best_order = std_data[best_variant]["order"]
            best_l2 = min(std_data.values(), key=lambda k: k["l2"][-1])
            best_l2_name = [k for k, v in std_data.items() if v["l2"][-1] == best_l2["l2"][-1]][0]

            f.write(f"1. **Best observed order**: {best_order:.2f} (variant {best_variant})\n")
            f.write(f"2. **Lowest L2 error at finest grid**: variant {best_l2_name}\n")

            if best_order >= 2.8:
                f.write(f"3. **Variant {best_variant} approaches 3rd order** — this is a ")
                f.write("**candidate** for a follow-up spec and approval.\n")
                f.write("   However, it has NOT been approved for production use.\n")
            elif best_order >= 2.5:
                f.write(f"3. Variant {best_variant} improves order to ~{best_order:.1f} ")
                f.write("but does not fully recover 3rd order.\n")
                f.write("   A more fundamental change (nonlinear WENO weights, Eq. 17) ")
                f.write("may be needed.\n")
            else:
                f.write(f"3. No variant approaches 3rd order (best = {best_order:.2f}).\n")
                f.write("   The ~2nd-order result appears to be **structural** for the ")
                f.write("current CFWENO3 stencil applied to Burgers with any simple ")
                f.write("nu treatment.\n")
                f.write("   Recovery may require the paper's nonlinear WENO weights ")
                f.write("(Eq. 17, Tables I-II) or a fundamentally different approach.\n")

        f.write("\n4. The production solver/schemes.py was NOT modified.\n")
        f.write("5. Any variant that shows improvement is a **diagnostic finding only**;\n")
        f.write("   it requires a formal spec update and approval before production use.\n")
        f.write("6. The reduced-amplitude and shorter-time cases help distinguish\n")
        f.write("   whether the order reduction is nonlinear-strength-dependent.\n\n")

        f.write("## Limitations\n\n")
        f.write("- Diagnostic variants are NOT approved for production\n")
        f.write("- Reference solutions are numerical (fine-grid), not analytic\n")
        f.write("- Only pre-shock smooth data tested\n")
        f.write("- No shock-capturing (Eq. 17 nonlinear WENO weights not implemented)\n")
        f.write("- These results do not constitute a complete CFWENO implementation\n")

    print(f"Analysis saved to {md_path}")


if __name__ == "__main__":
    main()
