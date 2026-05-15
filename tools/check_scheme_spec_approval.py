"""Deterministic approval checker for scheme specs.

Checks whether a scheme spec markdown file has
"Approved for implementation: yes".  Returns exit code 0 only when
the approval status is strictly "yes".

Usage:
    python tools/check_scheme_spec_approval.py <spec_path>
    python tools/check_scheme_spec_approval.py <spec_path> --json

Exit codes:
    0  — approved (status is "yes")
    1  — not approved (status is "no" or missing/abnormal)
    2  — file not found or read error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Pattern matches "Approved for implementation: <value>"
_APPROVAL_RE = re.compile(
    r"^Approved\s+for\s+implementation\s*:\s*(\S+)",
    re.MULTILINE | re.IGNORECASE,
)


def parse_approval_status(text: str) -> str | None:
    """Parse the approval status from spec text.

    Parameters
    ----------
    text : str
        Full text of the scheme spec markdown.

    Returns
    -------
    str or None
        The approval value in lowercase (e.g. "yes", "no"),
        or None if the line is not found.
    """
    m = _APPROVAL_RE.search(text)
    if m is None:
        return None
    return m.group(1).strip().lower()


def check_spec_approval(path: Path) -> dict:
    """Check a scheme spec file for approval status.

    Parameters
    ----------
    path : Path
        Path to the scheme spec markdown file.

    Returns
    -------
    dict
        Keys: spec_path (str), approved (bool), status (str|None),
        reason (str).
    """
    result = {
        "spec_path": str(path),
        "approved": False,
        "status": None,
        "reason": "",
        "checked_at": datetime.now().isoformat(),
    }

    if not path.exists():
        result["reason"] = f"File not found: {path}"
        return result

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        result["reason"] = f"Read error: {exc}"
        return result

    status = parse_approval_status(text)
    result["status"] = status

    if status is None:
        result["reason"] = "Approved for implementation line is missing"
    elif status == "yes":
        result["approved"] = True
        result["reason"] = "Approved for implementation is yes"
    else:
        result["reason"] = (
            f"Approved for implementation is not yes (found: {status!r})"
        )

    return result


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    parser = argparse.ArgumentParser(
        description="Check whether a scheme spec is approved for implementation.",
    )
    parser.add_argument("spec_path", type=Path, help="Path to scheme spec markdown")
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output result as JSON",
    )
    args = parser.parse_args(argv)

    result = check_spec_approval(args.spec_path)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        tag = "APPROVED" if result["approved"] else "NOT APPROVED"
        print(f"[{tag}] {args.spec_path}")
        print(f"  Status: {result['status']!r}")
        print(f"  Reason: {result['reason']}")

    return 0 if result["approved"] else 1 if result["status"] is not None else 2


if __name__ == "__main__":
    sys.exit(main())
