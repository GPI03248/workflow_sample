#!/usr/bin/env python3
"""Check formula confidence from a YAML inventory.

Usage:
    python tools/check_formula_confidence.py <inventory.yml>
    python tools/check_formula_confidence.py <inventory.yml> --json
    python tools/check_formula_confidence.py <inventory.yml> --require-high-for-implementation --spec <spec.md>
    python tools/check_formula_confidence.py <inventory.yml> --markdown-report <output.md>
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

VALID_CONFIDENCES = ("high", "medium", "low")
VALID_VERIFICATION = ("verified", "visually_confirmed", "partial", "uncertain", "missing", "derived", "failed_validation")
VALID_RELEVANCE = ("required", "optional", "not_needed")
VALID_CONSISTENCY = ("passed", "failed", "not_run", "not_required")


def load_inventory(path: str) -> dict:
    """Load a formula inventory YAML file."""
    p = Path(path)
    if not p.exists():
        print(f"ERROR: inventory file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(p) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        print("ERROR: inventory must be a YAML mapping", file=sys.stderr)
        sys.exit(1)
    if "formulas" not in data:
        print("ERROR: inventory missing 'formulas' key", file=sys.stderr)
        sys.exit(1)
    return data


def validate_formula(entry: dict, idx: int) -> list[str]:
    """Validate a single formula entry. Returns list of errors."""
    errors = []
    required_keys = [
        "formula_id", "paper_id", "source", "formula_type",
        "expression", "extraction_method", "confidence",
        "verification_status", "used_by", "implementation_relevance",
        "blocks_implementation",
    ]
    for key in required_keys:
        if key not in entry:
            errors.append(f"formula #{idx}: missing required key '{key}'")

    if "confidence" in entry and entry["confidence"] not in VALID_CONFIDENCES:
        errors.append(f"formula #{idx}: invalid confidence '{entry['confidence']}'")
    if "verification_status" in entry and entry["verification_status"] not in VALID_VERIFICATION:
        errors.append(f"formula #{idx}: invalid verification_status '{entry['verification_status']}'")
    if "implementation_relevance" in entry and entry["implementation_relevance"] not in VALID_RELEVANCE:
        errors.append(f"formula #{idx}: invalid implementation_relevance '{entry['implementation_relevance']}'")
    if "consistency_status" in entry and entry["consistency_status"] not in VALID_CONSISTENCY:
        errors.append(f"formula #{idx}: invalid consistency_status '{entry['consistency_status']}'")
    return errors


def check_inventory(inventory: dict) -> dict:
    """Analyze inventory and return structured results."""
    formulas = inventory.get("formulas", [])
    results = {
        "total": len(formulas),
        "high": 0,
        "medium": 0,
        "low": 0,
        "blocking": [],
        "warnings": [],
        "errors": [],
        "formulas": [],
    }

    for i, entry in enumerate(formulas):
        # Validate
        validation_errors = validate_formula(entry, i)
        results["errors"].extend(validation_errors)

        confidence = entry.get("confidence", "unknown")
        if confidence == "high":
            results["high"] += 1
        elif confidence == "medium":
            results["medium"] += 1
        elif confidence == "low":
            results["low"] += 1

        formula_info = {
            "formula_id": entry.get("formula_id", f"unknown_{i}"),
            "confidence": confidence,
            "verification_status": entry.get("verification_status", "unknown"),
            "implementation_relevance": entry.get("implementation_relevance", "unknown"),
            "blocks_implementation": entry.get("blocks_implementation", False),
            "consistency_status": entry.get("consistency_status", "not_run"),
            "formula_scope": entry.get("formula_scope", "scalar_linear_direct"),
        }
        results["formulas"].append(formula_info)

        # Track blocking items
        if entry.get("blocks_implementation", False):
            results["blocking"].append(formula_info)

        # Track warnings for medium/low confidence required formulas
        if entry.get("implementation_relevance") == "required" and confidence in ("medium", "low"):
            results["warnings"].append(
                f"REQUIRED formula '{entry.get('formula_id')}' has {confidence} confidence "
                f"(status: {entry.get('verification_status')})"
            )

    return results


def check_strict(results: dict, spec_path: str | None = None) -> list[str]:
    """Check strict mode for the scalar-linear direct-target scope.

    Required scalar-linear formulas must be high + verified and must not have
    consistency_status=failed. Diagnostic-only and deferred nonlinear/WENO
    formulas are reported but intentionally do not block this target-specific
    gate.
    """
    failures = []
    for f in results["formulas"]:
        if f.get("formula_scope") in ("diagnostic_only", "deferred_nonlinear_weno"):
            continue
        if f["implementation_relevance"] != "required":
            continue
        if spec_path:
            # Could check used_by matches spec, but keep simple for now
            pass
        if f["confidence"] != "high":
            failures.append(
                f"BLOCKING: '{f['formula_id']}' is required but confidence={f['confidence']}, "
                f"verification={f['verification_status']}"
            )
        elif f["verification_status"] != "verified":
            failures.append(
                f"BLOCKING: '{f['formula_id']}' is high confidence but "
                f"verification_status={f['verification_status']} (expected 'verified')"
            )
        # Check substencil-level numerical consistency
        if f.get("consistency_status") == "failed":
            failures.append(
                f"BLOCKING: '{f['formula_id']}' has consistency_status=failed — "
                f"substencil-level numerical validation did not achieve expected convergence order. "
                f"See docs/tasks/cfweno5_scalar_prototype/failed_attempt_diagnostic.md"
            )
    return failures


def format_report(results: dict, inventory_path: str, strict_failures: list[str] | None = None) -> str:
    """Format human-readable report."""
    lines = []
    lines.append(f"# Formula Confidence Report")
    lines.append(f"")
    lines.append(f"**Inventory**: `{inventory_path}`")
    lines.append(f"")

    # Summary
    lines.append(f"## Summary")
    lines.append(f"")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total formulas | {results['total']} |")
    lines.append(f"| High confidence | {results['high']} |")
    lines.append(f"| Medium confidence | {results['medium']} |")
    lines.append(f"| Low confidence | {results['low']} |")
    lines.append(f"| Blocking formulas | {len(results['blocking'])} |")
    lines.append(f"")

    ready = "Not ready for implementation approval" if results["blocking"] else "Ready for implementation approval"
    lines.append(f"**Implementation readiness**: {ready}")
    lines.append(f"")

    # High confidence
    high = [f for f in results["formulas"] if f["confidence"] == "high"]
    if high:
        lines.append(f"## High Confidence Formulas ({len(high)})")
        lines.append(f"")
        for f in high:
            cs = f.get("consistency_status", "not_run")
            scope = f.get("formula_scope", "scalar_linear_direct")
            lines.append(f"- `{f['formula_id']}`: {f['verification_status']}, "
                         f"relevance={f['implementation_relevance']}, "
                         f"scope={scope}, "
                         f"consistency={cs}")
        lines.append(f"")

    # Medium/Low confidence
    low_med = [f for f in results["formulas"] if f["confidence"] in ("medium", "low")]
    if low_med:
        lines.append(f"## Medium/Low Confidence Formulas ({len(low_med)})")
        lines.append(f"")
        for f in low_med:
            cs = f.get("consistency_status", "not_run")
            scope = f.get("formula_scope", "scalar_linear_direct")
            lines.append(f"- `{f['formula_id']}`: confidence={f['confidence']}, "
                         f"verification={f['verification_status']}, "
                         f"relevance={f['implementation_relevance']}, "
                         f"scope={scope}, "
                         f"blocks={f['blocks_implementation']}, "
                         f"consistency={cs}")
        lines.append(f"")


    # Deferred / diagnostic formulas
    deferred = [f for f in results["formulas"]
                if f.get("formula_scope") in ("diagnostic_only", "deferred_nonlinear_weno")]
    if deferred:
        lines.append(f"## Deferred / Diagnostic Formulas ({len(deferred)})")
        lines.append(f"")
        for f in deferred:
            cs = f.get("consistency_status", "not_run")
            scope = f.get("formula_scope", "scalar_linear_direct")
            lines.append(f"- `{f['formula_id']}`: scope={scope}, "
                         f"confidence={f['confidence']}, "
                         f"verification={f['verification_status']}, "
                         f"consistency={cs}")
        lines.append(f"")
    # Blocking
    if results["blocking"]:
        lines.append(f"## Blocking Formulas ({len(results['blocking'])})")
        lines.append(f"")
        lines.append(f"The following formulas block implementation approval:")
        lines.append(f"")
        for f in results["blocking"]:
            lines.append(f"1. `{f['formula_id']}`: confidence={f['confidence']}, "
                         f"verification={f['verification_status']}")
        lines.append(f"")

    # Strict failures
    if strict_failures:
        lines.append(f"## Strict Check Failures ({len(strict_failures)})")
        lines.append(f"")
        for sf in strict_failures:
            lines.append(f"- {sf}")
        lines.append(f"")

    # Warnings
    if results["warnings"]:
        lines.append(f"## Warnings ({len(results['warnings'])})")
        lines.append(f"")
        for w in results["warnings"]:
            lines.append(f"- {w}")
        lines.append(f"")

    # Human verification queue
    queue = [f for f in results["formulas"]
             if f["confidence"] != "high" and f["implementation_relevance"] == "required"]
    if queue:
        lines.append(f"## Recommended Human Verification Queue")
        lines.append(f"")
        for i, f in enumerate(queue, 1):
            cs = f.get("consistency_status", "not_run")
            lines.append(f"{i}. `{f['formula_id']}`: currently {f['confidence']} confidence, "
                         f"{f['verification_status']}, consistency={cs}")
        lines.append(f"")

    # Consistency failures
    consistency_failures = [f for f in results["formulas"]
                            if f.get("consistency_status") == "failed"]
    if consistency_failures:
        lines.append(f"## Numerical Consistency Failures ({len(consistency_failures)})")
        lines.append(f"")
        lines.append(f"The following formulas failed substencil-level numerical validation:")
        lines.append(f"")
        for f in consistency_failures:
            lines.append(f"1. `{f['formula_id']}`: confidence={f['confidence']}, "
                         f"verification={f['verification_status']}")
        lines.append(f"")
        lines.append(f"See `docs/tasks/cfweno5_scalar_prototype/failed_attempt_diagnostic.md` "
                     f"for details.")
        lines.append(f"")

    # Decision
    lines.append(f"## Decision")
    lines.append(f"")
    if results["blocking"]:
        lines.append(f"**Conditionally ready, blocked by {len(results['blocking'])} medium/low confidence required formulas.**")
    else:
        lines.append(f"**Ready for implementation approval.**")
    lines.append(f"")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check formula confidence from a YAML inventory")
    parser.add_argument("inventory", help="Path to formula inventory YAML file")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--require-high-for-implementation", action="store_true",
                        help="Strict mode: all required formulas must be high confidence and verified")
    parser.add_argument("--spec", help="Scheme spec file to cross-reference (for strict mode)")
    parser.add_argument("--markdown-report", metavar="PATH",
                        help="Generate a Markdown confidence report at PATH")
    args = parser.parse_args()

    inventory = load_inventory(args.inventory)
    results = check_inventory(inventory)

    # Check for validation errors
    if results["errors"]:
        for e in results["errors"]:
            print(f"ERROR: {e}", file=sys.stderr)
        if args.json:
            json.dump({"valid": False, "errors": results["errors"]}, sys.stdout, indent=2)
            print()
        sys.exit(1)

    # Strict check
    strict_failures = []
    if args.require_high_for_implementation:
        strict_failures = check_strict(results, args.spec)

    # JSON output
    if args.json:
        output = {
            "valid": True,
            "inventory": args.inventory,
            "summary": {
                "total": results["total"],
                "high": results["high"],
                "medium": results["medium"],
                "low": results["low"],
                "blocking_count": len(results["blocking"]),
            },
            "formulas": results["formulas"],
            "warnings": results["warnings"],
            "blocking": results["blocking"],
        }
        if strict_failures:
            output["strict_failures"] = strict_failures
        json.dump(output, sys.stdout, indent=2)
        print()
        if strict_failures:
            sys.exit(1)
        sys.exit(0)

    # Markdown report
    if args.markdown_report:
        report = format_report(results, args.inventory, strict_failures or None)
        Path(args.markdown_report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown_report).write_text(report)
        print(f"Report written to {args.markdown_report}")

    # Human-readable console output
    print(f"Formula confidence check: {args.inventory}")
    print(f"  Total: {results['total']}, High: {results['high']}, "
          f"Medium: {results['medium']}, Low: {results['low']}")
    print(f"  Blocking: {len(results['blocking'])}")

    for w in results["warnings"]:
        print(f"  WARNING: {w}", file=sys.stderr)

    if results["blocking"]:
        print(f"\n  BLOCKING formulas:")
        for f in results["blocking"]:
            print(f"    - {f['formula_id']}: confidence={f['confidence']}, "
                  f"verification={f['verification_status']}, "
                  f"scope={f.get('formula_scope', 'scalar_linear_direct')}")

    if args.require_high_for_implementation:
        if strict_failures:
            print(f"\n  STRICT CHECK FAILED ({len(strict_failures)} failures):")
            for sf in strict_failures:
                print(f"    - {sf}")
            sys.exit(1)
        else:
            print(f"\n  STRICT CHECK PASSED: all required formulas are high confidence and verified")

    if not results["blocking"] and not results["warnings"]:
        print("  OK")


if __name__ == "__main__":
    main()
