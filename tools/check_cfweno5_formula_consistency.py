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
    """Appendix A Eq. (A1), k=2: right-biased substencil (SUSPECT — see notes)."""
    u_ip1 = np.roll(u, -1)
    omnu = 1.0 - nu
    return (u
            + 0.5 * omnu * (u_half_right - u)
            + omnu * (-nu) * (u - 2.0 * u_half_right + u_ip1))


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
    args = parser.parse_args(argv)

    try:
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

    return 0 if results["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
