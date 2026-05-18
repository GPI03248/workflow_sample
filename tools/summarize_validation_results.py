"""Scan results/ directories and generate a validation index document.

Usage:
    python tools/summarize_validation_results.py
    python tools/summarize_validation_results.py --out docs/validation_index.md
    python tools/summarize_validation_results.py --json
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

RESULTS_DIR = Path("results")
KNOWN_DIRS = [
    "cfd_entropy_wave",
    "cfd_entropy_wave_convergence",
    "cfd_isentropic_vortex",
    "cfd_isentropic_vortex_convergence",
    "cfd_hll_validation",
    "cfd_uniform_flow",
    "cfd_sod_2d",
    # 1D advection
    "",
]

# Map directory -> (csv_name, csv_cols_of_interest)
_DIR_CSV_INFO = {
    "cfd_entropy_wave": ("error_summary.csv", ["riemann", "rho_l2_error"]),
    "cfd_entropy_wave_convergence": ("convergence_summary.csv", ["observed_order"]),
    "cfd_isentropic_vortex": ("error_summary.csv", ["riemann", "rho_l2_error"]),
    "cfd_isentropic_vortex_convergence": ("convergence_summary.csv", ["observed_order"]),
    "cfd_hll_validation": ("error_summary.csv", ["riemann", "rho_l2_error", "rho_mass_error"]),
}


def _find_csv(dirpath: Path) -> str | None:
    """Find the primary CSV file in a results directory."""
    for name in ["error_summary.csv", "convergence_summary.csv", "summary.csv"]:
        if (dirpath / name).exists():
            return name
    # Fall back to any CSV
    csvs = list(dirpath.glob("*.csv"))
    return csvs[0].name if csvs else None


def _read_csv_rows(path: Path) -> list[dict]:
    """Read CSV rows as list of dicts."""
    if not path.exists():
        return []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def _has_analysis(dirpath: Path) -> bool:
    """Check if analysis.md exists."""
    return (dirpath / "analysis.md").exists() or (dirpath / "convergence_analysis.md").exists()


def _detect_methods(rows: list[dict]) -> str:
    """Detect flux types / methods from CSV rows."""
    methods = set()
    for row in rows:
        for key in ("riemann", "reconstruction", "time_integrator", "method"):
            if key in row:
                methods.add(row[key])
    return ", ".join(sorted(methods)) if methods else "N/A"


# Preferred cases for HLL/Rusanov diffusion comparison (in priority order)
_HLL_COMPARISON_PRIORITY = ["entropy_wave", "isentropic_vortex"]


def _extract_hll_comparison(rows: list[dict], warnings: list[str]) -> dict:
    """Extract HLL vs Rusanov comparison from validation CSV rows.

    Prefers analytic benchmark cases (entropy_wave) over preservation
    tests (uniform_flow) to avoid zero-error rows masking real differences.
    """
    result: dict = {}

    # Group rows by (case, riemann)
    by_key: dict[tuple, dict] = {}
    for row in rows:
        case = row.get("case", "")
        riemann = row.get("riemann", "")
        by_key[(case, riemann)] = row

    # Find a case that has both hll and rusanov rows
    comparison_case = None
    for preferred in _HLL_COMPARISON_PRIORITY:
        if (preferred, "hll") in by_key and (preferred, "rusanov") in by_key:
            comparison_case = preferred
            break

    # Fall back to any case with both flux types and non-trivial errors
    if comparison_case is None:
        for (case, riemann), row in by_key.items():
            if riemann == "hll":
                matching = by_key.get((case, "rusanov"))
                if matching:
                    l2 = row.get("rho_l2_error", "")
                    try:
                        if l2 and float(l2) > 0:
                            comparison_case = case
                            break
                    except ValueError:
                        pass

    # Last resort: any case with both
    if comparison_case is None:
        cases_with_both = set()
        for (case, riemann) in by_key:
            if riemann == "hll" and (case, "rusanov") in by_key:
                cases_with_both.add(case)
        if cases_with_both:
            comparison_case = sorted(cases_with_both)[0]

    if comparison_case is None:
        warnings.append("HLL validation: no case with both hll and rusanov rows found")
        return result

    hll_row = by_key.get((comparison_case, "hll"), {})
    rus_row = by_key.get((comparison_case, "rusanov"), {})

    hll_l2 = hll_row.get("rho_l2_error")
    rus_l2 = rus_row.get("rho_l2_error")

    result["hll_comparison_case"] = comparison_case
    result["hll_l2"] = hll_l2
    result["rusanov_l2"] = rus_l2

    if comparison_case == "uniform_flow":
        result["hll_comparison_note"] = (
            "uniform flow has zero analytic error and is not a "
            "diffusion comparison benchmark"
        )

    if hll_l2 and rus_l2:
        try:
            ratio = float(hll_l2) / float(rus_l2)
            result["hll_rusanov_ratio"] = f"{ratio:.4f}"
        except (ValueError, ZeroDivisionError):
            pass

    return result


def scan_results() -> dict:
    """Scan all results directories and return structured summary."""
    results = []
    warnings = []

    # Check known CFD directories
    for dirname in KNOWN_DIRS:
        if not dirname:
            continue
        dirpath = RESULTS_DIR / dirname
        if not dirpath.is_dir():
            warnings.append(f"Missing results directory: {dirname}")
            continue

        csv_name = _find_csv(dirpath)
        csv_path = dirpath / csv_name if csv_name else None
        rows = _read_csv_rows(csv_path) if csv_path else []
        has_analysis = _has_analysis(dirpath)
        methods = _detect_methods(rows)

        entry = {
            "directory": f"results/{dirname}/",
            "result_type": dirname.replace("cfd_", "").replace("_", " "),
            "primary_csv": csv_name or "none",
            "analysis_file": "yes" if has_analysis else "missing",
            "methods": methods,
            "rows": len(rows),
            "status": "ok" if csv_name and has_analysis else "incomplete",
        }

        # Extract key metrics for HLL
        if dirname == "cfd_hll_validation" and rows:
            entry.update(
                _extract_hll_comparison(rows, warnings)
            )

        results.append(entry)

    return {"results": results, "warnings": warnings}


def build_markdown(scan: dict) -> str:
    """Build the validation index as Markdown."""
    lines = ["# Validation Index\n"]
    lines.append("Auto-generated by `tools/summarize_validation_results.py`.\n")

    # Summary table
    lines.append("## Summary\n")
    lines.append("| Directory | CSV | Analysis | Methods | Rows | Status |")
    lines.append("|-----------|-----|----------|---------|------|--------|")
    for r in scan["results"]:
        lines.append(
            f"| {r['directory']} | {r['primary_csv']} | {r['analysis_file']} "
            f"| {r['methods']} | {r['rows']} | {r['status']} |"
        )
    lines.append("")

    # HLL section
    hll = [r for r in scan["results"] if "hll" in r["directory"]]
    if hll:
        lines.append("## HLL Validation\n")
        h = hll[0]
        lines.append(f"- CSV: `results/cfd_hll_validation/{h['primary_csv']}`")
        lines.append(f"- Analysis: `results/cfd_hll_validation/analysis.md`")
        if h.get("hll_comparison_case"):
            lines.append(f"- Comparison case: {h['hll_comparison_case']}")
        if h.get("hll_l2"):
            lines.append(f"- HLL rho_L2: {h['hll_l2']}")
        if h.get("rusanov_l2"):
            lines.append(f"- Rusanov rho_L2: {h['rusanov_l2']}")
        if h.get("hll_rusanov_ratio"):
            lines.append(f"- HLL/Rusanov L2 ratio: {h['hll_rusanov_ratio']}")
        if h.get("hll_comparison_note"):
            lines.append(f"- Note: {h['hll_comparison_note']}")
        lines.append("")

    # Warnings
    if scan["warnings"]:
        lines.append("## Missing or Incomplete Results\n")
        for w in scan["warnings"]:
            lines.append(f"- {w}")
        lines.append("")

    # Regeneration commands
    lines.append("## Regeneration Commands\n")
    lines.append("```bash")
    lines.append("tools/run_in_project_env.sh python examples/run_cfd_entropy_wave.py")
    lines.append("tools/run_in_project_env.sh python examples/run_cfd_entropy_wave_convergence.py")
    lines.append("tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex.py")
    lines.append("tools/run_in_project_env.sh python examples/run_cfd_isentropic_vortex_convergence.py")
    lines.append("tools/run_in_project_env.sh python examples/run_cfd_hll_validation.py")
    lines.append("tools/run_in_project_env.sh python examples/run_cfd_uniform_flow.py")
    lines.append("tools/run_in_project_env.sh python examples/run_cfd_sod_2d.py")
    lines.append("```\n")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan validation results and generate index."
    )
    parser.add_argument("--out", default="docs/validation_index.md",
                        help="Output path (default: docs/validation_index.md)")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output JSON to stdout instead of writing markdown")
    args = parser.parse_args(argv)

    scan = scan_results()

    if args.json_output:
        print(json.dumps(scan, indent=2))
        return 0

    md = build_markdown(scan)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"Validation index written to: {out_path}")
    if scan["warnings"]:
        for w in scan["warnings"]:
            print(f"  WARNING: {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
