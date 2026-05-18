"""Lightweight deterministic repo health check for agentic workflows.

Usage:
    python tools/check_repo_health.py
    python tools/check_repo_health.py --json
    python tools/check_repo_health.py --warnings-ok
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Files/dirs to scan for old env commands
_ENV_SCAN_TARGETS = [
    "README.md",
    "CLAUDE.md",
    "Makefile",
    ".claude/",
    "docs/",
    "tools/",
    "tests/",
    "examples/",
]

# Patterns for old commands in executable contexts
_EXEC_CONTEXT_RE = re.compile(
    r"^\s*(tools/|python |pytest |\t)", re.MULTILINE
)

_APPROVAL_RE = re.compile(
    r"^Approved\s+for\s+implementation\s*:\s*(\S+)",
    re.MULTILINE | re.IGNORECASE,
)

# Key demo paths that must exist
_DEMO_PATHS = {
    "tools/run_in_project_env.sh": "error",
    "examples/run_cfd_hll_validation.py": "error",
    "results/cfd_hll_validation/error_summary.csv": "error",
    "results/cfd_hll_validation/analysis.md": "error",
    "docs/case_studies/hll_flux_paper_to_code.md": "error",
    "docs/validation_index.md": "warning",
}

# HLL artifacts that must exist
_HLL_ARTIFACTS = [
    "results/cfd_hll_validation/error_summary.csv",
    "results/cfd_hll_validation/analysis.md",
    "docs/tasks/hll_flux_implementation/traceability.md",
    "docs/case_studies/hll_flux_paper_to_code.md",
]


def _collect_files(base: str, targets: list[str]) -> list[Path]:
    """Collect all files from scan targets."""
    files = []
    for t in targets:
        p = Path(base) / t if base else Path(t)
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(sorted(f for f in p.rglob("*") if f.is_file()))
    return files


def check_old_env_commands(root: Path) -> tuple[list[str], list[str]]:
    """Check for bash -ic / module-conda in executable contexts."""
    errors = []
    warnings = []
    files = _collect_files(str(root), _ENV_SCAN_TARGETS)

    for fpath in files:
        try:
            text = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()

            # Skip comments and docstrings
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                # Still check if it's in a deprecated explanation
                if "bash -ic" in line or "module-conda" in line:
                    warnings.append(
                        f"{fpath}:{i}: old command in comment/doc (allowed): {stripped[:80]}"
                    )
                continue

            has_old = "bash -ic" in line or "module-conda" in line
            if not has_old:
                continue

            # Check if it's in an executable context (Makefile recipe, code line)
            is_exec = (
                fpath.name == "Makefile" and line.startswith("\t")
            ) or (
                fpath.suffix == ".py" and not stripped.startswith("#")
                and not stripped.startswith('"""') and not stripped.startswith("'''")
                and ("subprocess" in line or "os.system" in line or "run(" in line)
            ) or (
                fpath.suffix == ".sh" and not stripped.startswith("#")
            ) or (
                fpath.suffix == ".md" and (
                    "```bash" in text[max(0, text.find(line) - 100):text.find(line)]
                    or "$ " in line or "tools/" in line
                )
            )

            if is_exec:
                errors.append(
                    f"{fpath}:{i}: executable old command: {stripped[:80]}"
                )
            else:
                warnings.append(
                    f"{fpath}:{i}: old command reference (allowed): {stripped[:80]}"
                )

    return errors, warnings


def check_scheme_spec_approval(root: Path) -> tuple[list[str], list[str]]:
    """Check all scheme specs have approval lines."""
    errors = []
    warnings = []
    specs_dir = root / "docs" / "scheme_specs"

    if not specs_dir.is_dir():
        errors.append("docs/scheme_specs/ directory not found")
        return errors, warnings

    for spec in sorted(specs_dir.glob("*.md")):
        text = spec.read_text(encoding="utf-8", errors="ignore")
        m = _APPROVAL_RE.search(text)
        if m is None:
            errors.append(f"{spec}: missing 'Approved for implementation' line")
        else:
            status = m.group(1).strip().lower()
            if status not in ("yes", "no"):
                errors.append(f"{spec}: abnormal approval status: {status!r}")

    return errors, warnings


def check_approved_spec_traceability(root: Path) -> tuple[list[str], list[str]]:
    """Check that approved specs have traceability manifests."""
    errors = []
    warnings = []
    specs_dir = root / "docs" / "scheme_specs"
    tasks_dir = root / "docs" / "tasks"

    if not specs_dir.is_dir() or not tasks_dir.is_dir():
        return errors, warnings

    # Find approved specs
    approved_specs = []
    for spec in sorted(specs_dir.glob("*.md")):
        text = spec.read_text(encoding="utf-8", errors="ignore")
        m = _APPROVAL_RE.search(text)
        if m and m.group(1).strip().lower() == "yes":
            approved_specs.append(str(spec))

    if not approved_specs:
        return errors, warnings

    # Check each approved spec has a traceability manifest referencing it
    manifests = list(tasks_dir.rglob("traceability.md"))
    manifest_contents = []
    for m in manifests:
        try:
            manifest_contents.append(m.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            pass

    for spec_path in approved_specs:
        spec_name = Path(spec_path).name
        found = any(spec_name in content for content in manifest_contents)
        if not found:
            warnings.append(
                f"Approved spec {spec_name} has no traceability manifest referencing it"
            )

    return errors, warnings


def check_hll_artifacts(root: Path) -> tuple[list[str], list[str]]:
    """Check HLL demo artifacts exist."""
    errors = []
    for path in _HLL_ARTIFACTS:
        if not (root / path).exists():
            errors.append(f"Missing HLL artifact: {path}")
    return errors, []


def check_readme_paths(root: Path) -> tuple[list[str], list[str]]:
    """Check that key paths referenced in README exist."""
    errors = []
    warnings = []

    for path, level in _DEMO_PATHS.items():
        if not (root / path).exists():
            msg = f"README-referenced path missing: {path}"
            if level == "error":
                errors.append(msg)
            else:
                warnings.append(msg)

    return errors, warnings


def run_all_checks(root: Path) -> dict:
    """Run all health checks and return structured result."""
    all_errors = []
    all_warnings = []
    checks = []

    check_funcs = [
        ("Environment commands", check_old_env_commands),
        ("Scheme spec approval", check_scheme_spec_approval),
        ("Approved spec traceability", check_approved_spec_traceability),
        ("HLL validation artifacts", check_hll_artifacts),
        ("README path references", check_readme_paths),
    ]

    for name, func in check_funcs:
        errors, warnings = func(root)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
        checks.append({
            "name": name,
            "errors": len(errors),
            "warnings": len(warnings),
            "ok": len(errors) == 0,
        })

    return {
        "ok": len(all_errors) == 0,
        "errors": all_errors,
        "warnings": all_warnings,
        "checks": checks,
    }


def format_output(result: dict) -> str:
    """Format human-readable output."""
    lines = []
    for check in result["checks"]:
        tag = "OK" if check["ok"] else "FAIL"
        lines.append(f"[{tag}] {check['name']} ({check['errors']} errors, {check['warnings']} warnings)")

    if result["warnings"]:
        lines.append("")
        for w in result["warnings"]:
            lines.append(f"[WARN] {w}")

    if result["errors"]:
        lines.append("")
        for e in result["errors"]:
            lines.append(f"[ERROR] {e}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lightweight deterministic repo health check."
    )
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output JSON to stdout")
    parser.add_argument("--warnings-ok", action="store_true",
                        help="Return exit code 0 even with warnings (errors still fail)")
    args = parser.parse_args(argv)

    root = Path(".")
    result = run_all_checks(root)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_output(result))

    if result["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
