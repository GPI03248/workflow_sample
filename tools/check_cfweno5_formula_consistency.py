#!/usr/bin/env python3
"""Check CFWENO5 substencil-level numerical consistency.

Runs single-step convergence analysis of each substencil and the combined
scheme to verify expected convergence orders before implementation.

Usage:
    python tools/check_cfweno5_formula_consistency.py
    python tools/check_cfweno5_formula_consistency.py --quick
    python tools/check_cfweno5_formula_consistency.py --json

Exit codes:
    0 — all consistency checks pass
    1 — one or more substencils fail expected order
    2 — runtime error (e.g., import failure)

Design note: This tool defines CFWENO5 substencil formulas INLINE for testing
purposes. It does NOT import from solver/cfweno_scalar.py (which was deleted
after the failed implementation). The formulas tested here match the extraction
report and formula inventory. If the formulas are re-verified and corrected,
this tool must be updated to test the new formulas.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Callable

import numpy as np

# --- inline CFWENO5 substencil formulas (from extraction report) ---
# These match the formulas in docs/formula_inventories/cfweno5_scalar_formulas.yml
# and docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_extraction.md Section 1.
# These are the formulas that failed numerical validation — they are defined
# here for consistency testing, NOT for production use.


def _interface_reconstruction(u: np.ndarray) -> np.ndarray:
    """4th-order centred interface reconstruction: u_{i+1/2}."""
    u_im1 = np.roll(u, 1)
    u_ip1 = np.roll(u, -1)
    u_ip2 = np.roll(u, -2)
    return (-u_im1 + 7.0 * u + 7.0 * u_ip1 - u_ip2) / 12.0


def _substencil_s0(u: np.ndarray, nu: float,
                   u_half_right: np.ndarray,
                   u_half_left: np.ndarray) -> np.ndarray:
    """Appendix A Eq. (A1), k=0: left-biased substencil."""
    u_im1 = np.roll(u, 1)
    omnu = 1.0 - nu
    return u + omnu * (u - u_half_left) + 0.5 * omnu * (u_im1 - 2.0 * u_half_left + u)


def _substencil_s1(u: np.ndarray, nu: float,
                   u_half_right: np.ndarray,
                   u_half_left: np.ndarray) -> np.ndarray:
    """Appendix A Eq. (A1), k=1: centre-biased substencil."""
    omnu = 1.0 - nu
    return (u
            + omnu * (u_half_right - u)
            + omnu * (-nu) * (u_half_left - 2.0 * u + u_half_right))


def _substencil_s2(u: np.ndarray, nu: float,
                   u_half_right: np.ndarray,
                   u_half_left: np.ndarray) -> np.ndarray:
    """Appendix A Eq. (A1), k=2: right-biased substencil (CORRECTED 2026-05-27).

    Correction: 0.5 factor moved from first to second correction term,
    based on pdftotext -layout column-position analysis.
    See docs/tasks/cfweno5_formula_verification/s2_retranscription.md.
    """
    u_ip1 = np.roll(u, -1)
    omnu = 1.0 - nu
    return (u
            + omnu * (u_half_right - u)
            + 0.5 * omnu * (-nu) * (u - 2.0 * u_half_right + u_ip1))


def _substencil_s3(u: np.ndarray, nu: float,
                   u_half_right: np.ndarray,
                   u_half_left: np.ndarray) -> np.ndarray:
    """Appendix A Eq. (A1), k=3: full-stencil substencil."""
    u_im1 = np.roll(u, 1)
    u_ip1 = np.roll(u, -1)
    omnu = 1.0 - nu
    return (u
            + omnu * (u_half_right - u)
            + 0.5 * omnu * (-nu) * (u - 2.0 * u_half_right + u_ip1)
            + 0.25 * omnu * (-nu) * (1.0 + nu) * (2.0 * u_half_left - 5.0 * u + 4.0 * u_half_right - u_ip1)
            + (1.0 / 12.0) * omnu**2 * (-nu) * (1.0 + nu) * (-u_im1 + 6.0 * u_half_left - 10.0 * u + 6.0 * u_half_right - u_ip1))


def _cfweno5_combined(u: np.ndarray, nu: float,
                      u_half_right: np.ndarray,
                      u_half_left: np.ndarray) -> np.ndarray:
    """Combined CFWENO5 using Table I optimal weights for k=0,1,2."""
    s0 = _substencil_s0(u, nu, u_half_right, u_half_left)
    s1 = _substencil_s1(u, nu, u_half_right, u_half_left)
    s2 = _substencil_s2(u, nu, u_half_right, u_half_left)

    # Table I optimal weights (r=3, k=0,1,2; k=3 is N/A)
    w0 = nu * (1.0 + nu) / 6.0
    w1 = (1.0 + nu) * (2.0 - nu) / 6.0
    w2 = (1.0 - nu) * (2.0 - nu) / 6.0

    return w0 * s0 + w1 * s1 + w2 * s2


# --- Variant scheme functions for weight diagnosis ---

def _make_weight_variant(name, s0_fn, s1_fn, s2_fn, weight_fn, target):
    """Create a named variant scheme function.

    Parameters
    ----------
    name : str
        Variant name for reporting.
    s0_fn, s1_fn, s2_fn : callable
        Sub-stencil functions (may be None to use defaults).
    weight_fn : callable
        Function (nu) -> (w0, w1, w2, weight_sum).
    target : str
        Reconstruction target description.
    """
    _s0 = s0_fn or _substencil_s0
    _s1 = s1_fn or _substencil_s1
    _s2 = s2_fn or _substencil_s2

    def scheme_fn(u, nu, u_half_right, u_half_left):
        s0 = _s0(u, nu, u_half_right, u_half_left)
        s1 = _s1(u, nu, u_half_right, u_half_left)
        s2 = _s2(u, nu, u_half_right, u_half_left)
        w0, w1, w2, _ws = weight_fn(nu)
        return w0 * s0 + w1 * s1 + w2 * s2

    scheme_fn._variant_name = name
    scheme_fn._target = target
    scheme_fn._weight_fn = weight_fn
    return scheme_fn


def _weights_table_I_raw(nu):
    """Table I optimal weights without normalization."""
    w0 = nu * (1.0 + nu) / 6.0
    w1 = (1.0 + nu) * (2.0 - nu) / 6.0
    w2 = (1.0 - nu) * (2.0 - nu) / 6.0
    weight_sum = w0 + w1 + w2
    return w0, w1, w2, weight_sum


def _weights_table_I_normalized(nu):
    """Table I optimal weights with Eq. (17) normalization."""
    w0, w1, w2, raw_sum = _weights_table_I_raw(nu)
    if abs(raw_sum) > 1e-15:
        return w0 / raw_sum, w1 / raw_sum, w2 / raw_sum, 1.0
    return 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0, 1.0


def _weights_table_II_raw(nu):
    """Table II optimal weights without normalization."""
    w0 = nu * (5.0 * nu ** 2 + nu - 2.0) / (6.0 * (3.0 * nu - 1.0))
    w1 = -(30.0 * nu ** 4 - 60.0 * nu ** 3 - nu ** 2 + 31.0 * nu - 8.0) / (
        6.0 * (3.0 * nu - 1.0) * (3.0 * nu - 2.0))
    w2 = (nu - 1.0) * (5.0 * nu ** 2 - 11.0 * nu + 4.0) / (6.0 * (3.0 * nu - 2.0))
    weight_sum = w0 + w1 + w2
    return w0, w1, w2, weight_sum


def _weights_table_II_normalized(nu):
    """Table II optimal weights with Eq. (17) normalization."""
    w0, w1, w2, raw_sum = _weights_table_II_raw(nu)
    if abs(raw_sum) > 1e-15:
        return w0 / raw_sum, w1 / raw_sum, w2 / raw_sum, 1.0
    return 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0, 1.0


def _weights_equal(nu):
    """Equal 1/3 weights — debug baseline."""
    return 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0, 1.0


# CFWENO3 baseline: uses r=2 substencils (k=0,1) with standard WENO-JS weights
def _cfweno3_baseline_scheme(u, nu, u_half_right, u_half_left):
    """CFWENO3 (r=2) — known-good baseline using 2-substencil WENO combination.

    CFWENO3 uses 2 substencils (k=0,1) + Table I r=2 weights: k=0: nu, k=1: 1-nu.
    The interface reconstruction uses 4-point stencil as in the CFWENO5 checker.
    """
    u_im1 = np.roll(u, 1)
    u_ip1 = np.roll(u, -1)
    omnu = 1.0 - nu
    # CFWENO3 substencil s0 (left-biased): Eq. (A1) r=2 analogue
    s0 = u + omnu * (u - u_half_left)
    # CFWENO3 substencil s1 (right-biased): Eq. (A1) r=2 analogue
    s1 = u + omnu * (u_half_right - u)
    # Table I r=2 weights: k=0=nu, k=1=1-nu (these sum to 1)
    return nu * s0 + (1.0 - nu) * s1


VARIANTS = [
    ("current_table_I_raw",
     _make_weight_variant("current_table_I_raw", None, None, None,
                          _weights_table_I_raw, "ubar_{i+1/2}"),
     "Table I raw c_bar_rk, no normalization — current (broken)"),
    ("table_I_normalized",
     _make_weight_variant("table_I_normalized", None, None, None,
                          _weights_table_I_normalized, "ubar_{i+1/2}"),
     "Table I c_bar_rk normalized per Eq. (17)"),
    ("table_II_raw",
     _make_weight_variant("table_II_raw", None, None, None,
                          _weights_table_II_raw, "u^{n+1}_{i+1/2} (wrong target)"),
     "Table II raw c_rk, no normalization — wrong target for checker"),
    ("table_II_normalized",
     _make_weight_variant("table_II_normalized", None, None, None,
                          _weights_table_II_normalized, "u^{n+1}_{i+1/2} (wrong target)"),
     "Table II c_rk normalized per Eq. (17) — wrong target for checker"),
    ("equal_weights_debug",
     _make_weight_variant("equal_weights_debug", None, None, None,
                          _weights_equal, "ubar_{i+1/2}"),
     "Equal 1/3 weights — diagnostic baseline only"),
]


def run_weight_diagnosis(cfl: float = 0.5, quick: bool = False) -> dict:
    """Test weight-role variants for combined reconstruction.

    Parameters
    ----------
    cfl : float
        CFL number.
    quick : bool
        If True, use fewer resolutions.

    Returns
    -------
    dict with variants list, cfweno3_baseline, and summary.
    """
    resolutions = (40, 80, 160) if quick else (40, 80, 160, 320)

    # Run CFWENO3 baseline
    cfweno3_result = _check_scheme("cfweno3_baseline", _cfweno3_baseline_scheme,
                                    3.0, cfl, resolutions)

    # Run each weight variant
    variant_results = []
    for vname, vfn, vdesc in VARIANTS:
        result = _check_scheme(vname, vfn, 5.0, cfl, resolutions)
        # Compute weight sum at this CFL
        _, _, _, wsum = vfn._weight_fn(cfl)
        result["weight_source"] = vfn._target
        result["weight_sum"] = round(wsum, 6)
        result["description"] = vdesc
        variant_results.append(result)

    return {
        "cfweno3_baseline": cfweno3_result,
        "variants": variant_results,
        "cfl": cfl,
        "resolutions": list(resolutions),
    }


SUBSTENCILS = {
    "s0": (_substencil_s0, 3.0),     # expected individual order ~3
    "s1": (_substencil_s1, 4.0),     # expected individual order ~4
    "s2": (_substencil_s2, 4.0),     # expected individual order ~4 (CURRENTLY FAILS)
    "s3": (_substencil_s3, 4.0),     # expected individual order ~4
}

COMBINED_SCHEME = (_cfweno5_combined, 5.0)  # expected combined order ~5


# --- single-step analysis ---

def _make_initial_condition(x: np.ndarray) -> np.ndarray:
    """Same IC as the convergence test: sin(2*pi*x) + 1."""
    return np.sin(2.0 * np.pi * x) + 1.0


def _exact_solution(x: np.ndarray, t: float, a: float = 1.0) -> np.ndarray:
    """Exact solution for linear advection."""
    return np.sin(2.0 * np.pi * (x - a * t)) + 1.0


def _compute_l2_error(u_num: np.ndarray, u_exact: np.ndarray, dx: float) -> float:
    """Compute L2 error."""
    diff = u_num - u_exact
    return float(np.sqrt(np.sum(diff**2) * dx))


def _single_step(scheme_fn: Callable, nx: int, cfl: float) -> float:
    """Run ONE time step with the given scheme function and return L2 error.

    The scheme_fn receives (u, nu, u_half_right, u_half_left) and returns
    ubar_{i+1/2}. The conservative update u_new = u - cfl*(ubar_right - ubar_left)
    is applied here.
    """
    dx = 1.0 / nx
    dt = cfl * dx  # a = 1.0
    nu = cfl

    x = np.linspace(dx / 2.0, 1.0 - dx / 2.0, nx)
    u0 = _make_initial_condition(x)

    # Interface reconstruction
    u_half_right = _interface_reconstruction(u0)
    u_half_left = np.roll(u_half_right, 1)

    # Compute ubar at i+1/2
    ubar_right = scheme_fn(u0, nu, u_half_right, u_half_left)
    ubar_left = np.roll(ubar_right, 1)

    # Conservative update for one step
    u1 = u0 - cfl * (ubar_right - ubar_left)

    # Exact solution at t = dt
    u_ex = _exact_solution(x, dt)
    return _compute_l2_error(u1, u_ex, dx)


def _compute_order(errors: dict[int, float]) -> float:
    """Estimate convergence order from errors at successive resolutions.

    Uses the finest two grids for the estimate.
    """
    nxs = sorted(errors.keys())
    if len(nxs) < 2:
        return float("nan")
    # Use the two finest grids
    n1, n2 = nxs[-2], nxs[-1]
    e1, e2 = errors[n1], errors[n2]
    if e1 <= 0.0 or e2 <= 0.0:
        return float("nan")
    return math.log(e1 / e2) / math.log(n2 / n1)


def _check_scheme(name: str, scheme_fn: Callable, expected_order: float,
                  cfl: float = 0.5,
                  resolutions: tuple = (40, 80, 160, 320)) -> dict:
    """Run single-step convergence check for one scheme.

    Returns dict with errors, observed order, and pass/fail.
    """
    errors = {}
    for nx in resolutions:
        errors[nx] = _single_step(scheme_fn, nx, cfl)

    observed_order = _compute_order(errors)

    # Allow tolerance: expected_order - 1.0 for individual substencils,
    # expected_order - 1.5 for combined scheme
    if expected_order >= 5.0:
        tolerance = 1.5
    else:
        tolerance = 1.0

    passed = observed_order >= (expected_order - tolerance) if not math.isnan(observed_order) else False

    return {
        "name": name,
        "expected_order": expected_order,
        "observed_order": round(observed_order, 2) if not math.isnan(observed_order) else None,
        "errors": {str(nx): f"{e:.6e}" for nx, e in errors.items()},
        "passed": passed,
    }


def run_consistency_checks(cfl: float = 0.5, quick: bool = False) -> dict:
    """Run all substencil consistency checks.

    Parameters
    ----------
    cfl : float
        CFL number for the test.
    quick : bool
        If True, use fewer resolutions (faster but less accurate).

    Returns
    -------
    dict with keys: substencils, combined, all_passed, summary
    """
    resolutions = (40, 80, 160) if quick else (40, 80, 160, 320)

    # Check individual substencils
    substencil_results = []
    for name, (fn, expected_order) in SUBSTENCILS.items():
        result = _check_scheme(name, fn, expected_order, cfl, resolutions)
        substencil_results.append(result)

    # Check combined scheme
    combined_fn, combined_expected = COMBINED_SCHEME
    combined_result = _check_scheme("cfweno5_combined", combined_fn, combined_expected, cfl, resolutions)

    all_passed = all(r["passed"] for r in substencil_results) and combined_result["passed"]

    # Build summary
    failures = [r["name"] for r in substencil_results if not r["passed"]]
    if not combined_result["passed"]:
        failures.append("cfweno5_combined")

    return {
        "substencils": substencil_results,
        "combined": combined_result,
        "all_passed": all_passed,
        "failures": failures,
        "summary": (
            "ALL PASSED" if all_passed
            else f"FAILED: {', '.join(failures)}"
        ),
        "cfl": cfl,
        "resolutions": list(resolutions),
    }


def _print_weight_diagnosis(results: dict, quick: bool = False) -> None:
    """Print weight diagnosis results in readable format."""
    print("CFWENO5 Weight Role Diagnosis")
    print(f"  CFL: {results['cfl']}")
    print(f"  Resolutions: {results['resolutions']}")
    print()

    # CFWENO3 baseline
    cfweno3 = results["cfweno3_baseline"]
    bfs = "PASS" if cfweno3["passed"] else "FAIL"
    bfo = f"{cfweno3['observed_order']:.2f}" if cfweno3["observed_order"] is not None else "N/A"
    print(f"  {'cfweno3':30s}  {bfs}  observed_order={bfo}  (expected ~3.0)  [infrastructure sanity]")

    print()
    print("  Variants:")
    for v in results["variants"]:
        name = v["name"]
        v_status = "PASS" if v["passed"] else "FAIL"
        v_obs = f"{v['observed_order']:.2f}" if v["observed_order"] is not None else "N/A"
        v_exp = v["expected_order"]
        wsum = v["weight_sum"]
        target = v["weight_source"]
        desc = v["description"]
        print(f"  {name:30s}  {v_status}  observed_order={v_obs}  "
              f"(expected ~{v_exp})  weight_sum={wsum}  target={target}")
        if not quick:
            for nx_str, err in v["errors"].items():
                print(f"          nx={nx_str:>4s}  L2={err}")
        print(f"          {desc}")
    print()

    # Identify best variant
    variants = results["variants"]
    if variants:
        best = max(variants, key=lambda v: v["observed_order"] if v["observed_order"] is not None else -1)
        print(f"  Best variant: {best['name']} (order={best['observed_order']:.2f})")

    print()
    print("  Diagnostic complete. Exit code 0 (diagnosis never fails).")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check CFWENO5 substencil numerical consistency"
    )
    parser.add_argument("--quick", action="store_true",
                        help="Use fewer resolutions (faster)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON")
    parser.add_argument("--cfl", type=float, default=0.5,
                        help="CFL number (default: 0.5)")
    parser.add_argument("--diagnose-weights", action="store_true",
                        help="Run weight-variant diagnosis mode "
                             "(tests Table I/II raw vs normalized vs equal weights)")
    args = parser.parse_args(argv)

    try:
        if args.diagnose_weights:
            results = run_weight_diagnosis(cfl=args.cfl, quick=args.quick)
        else:
            results = run_consistency_checks(cfl=args.cfl, quick=args.quick)
    except Exception as e:
        if args.json:
            json.dump({"error": str(e)}, sys.stdout, indent=2)
            print()
        else:
            print(f"ERROR: {e}")
        return 2

    if args.json:
        json.dump(results, sys.stdout, indent=2)
        print()
    elif args.diagnose_weights:
        _print_weight_diagnosis(results, quick=args.quick)
    else:
        print("CFWENO5 Substencil Consistency Check")
        print(f"  CFL: {args.cfl}")
        print(f"  Resolutions: {results['resolutions']}")
        print()
        for r in results["substencils"]:
            status = "PASS" if r["passed"] else "FAIL"
            obs = f"{r['observed_order']:.2f}" if r["observed_order"] is not None else "N/A"
            exp_str = f"(expected ~{r['expected_order']})"
            print(f"  {r['name']:6s}  {status}  observed_order={obs}  {exp_str}")
            if not args.quick:
                for nx_str, err in r["errors"].items():
                    print(f"          nx={nx_str:>4s}  L2={err}")
        print()
        combined = results["combined"]
        c_status = "PASS" if combined["passed"] else "FAIL"
        c_obs = f"{combined['observed_order']:.2f}" if combined["observed_order"] is not None else "N/A"
        c_exp_str = f"(expected ~{combined['expected_order']})"
        print(f"  {'comb':6s}  {c_status}  observed_order={c_obs}  {c_exp_str}")
        if not args.quick:
            for nx_str, err in combined["errors"].items():
                print(f"          nx={nx_str:>4s}  L2={err}")
        print()
        print(f"  Result: {results['summary']}")

    # Weight diagnosis always exits 0 (it's diagnostic, not pass/fail)
    if args.diagnose_weights:
        return 0
    return 0 if results["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
