"""Create or update a task traceability manifest.

Generates a markdown document that records the full provenance of a
paper-to-code / numerical-method / CFD-case task, including source
material, approval status, code changes, tests, and git info.

Usage:
    python tools/create_task_traceability.py \
        --task-id hll_flux \
        --task-type paper-to-code \
        --source docs/papers/hll_flux_test_note.md \
        --extraction-report docs/paper_reviews/hll_flux_test_note_extraction.md \
        --scheme-spec docs/scheme_specs/hll_flux.md \
        --commit-hash abc1234

    python tools/create_task_traceability.py --help

Output defaults to docs/tasks/<task_id>/traceability.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def _read_approval_status(spec_path: str | None) -> dict:
    """Read approval status from a scheme spec using check_scheme_spec_approval."""
    if not spec_path:
        return {"approved": None, "status": None, "reason": "No spec provided"}

    # Import the checker logic directly
    from check_scheme_spec_approval import check_spec_approval

    p = Path(spec_path)
    if not p.exists():
        return {"approved": None, "status": None, "reason": f"Spec not found: {spec_path}"}

    result = check_spec_approval(p)
    return {
        "approved": result["approved"],
        "status": result["status"],
        "reason": result["reason"],
    }


def build_traceability_markdown(
    task_id: str,
    task_type: str = "",
    source: str = "",
    extraction_report: str = "",
    scheme_spec: str = "",
    validation_result: str = "",
    commit_hash: str = "",
    modules_to_change: str = "",
    modules_protected: str = "",
    modified_files: str = "",
    added_files: str = "",
    tests_run: str = "",
    test_results: str = "",
    generated_result_files: str = "",
    reviewer: str = "",
    review_status: str = "",
    unresolved_questions: str = "",
    remaining_risks: str = "",
    push_status: str = "",
    implementation_status: str = "",
    approval_info: dict | None = None,
) -> str:
    """Build a traceability manifest as markdown string.

    Parameters
    ----------
    task_id : str
        Unique task identifier.
    task_type : str
        One of: paper-to-code, numerical-method, cfd-case, other.
    source : str
        Path to source material (paper, note, etc.).
    extraction_report : str
        Path to extraction report.
    scheme_spec : str
        Path to scheme spec.
    validation_result : str
        Path to validation results.
    commit_hash : str
        Git commit hash.
    approval_info : dict or None
        Pre-fetched approval status dict. If None, will be derived
        from scheme_spec path.

    Returns
    -------
    str
        Complete markdown content for the traceability manifest.
    """
    now = datetime.now().isoformat()

    if approval_info is None:
        approval_info = _read_approval_status(scheme_spec)

    approved_str = str(approval_info.get("approved"))
    status_str = str(approval_info.get("status"))
    reason_str = approval_info.get("reason", "")

    lines = [
        "# Task Traceability Manifest",
        "",
        "## Task metadata",
        f"- task id: {task_id}",
        f"- task type: {task_type}",
        f"- created at: {now}",
        f"- source: {source}",
        "",
        "## Source material",
        f"- paper / note: {source}",
        f"- extraction report: {extraction_report}",
        f"- scheme spec: {scheme_spec}",
        "",
        "## Approval status",
        f"- Approved for implementation: {status_str}",
        f"- approval checker result: {reason_str}",
        f"- implementation status: {implementation_status}",
        "",
        "## Intended code changes",
        f"- modules expected to change: {modules_to_change}",
        f"- modules protected from change: {modules_protected}",
        "",
        "## Actual code changes",
        f"- modified files: {modified_files}",
        f"- added files: {added_files}",
        "",
        "## Tests and validation",
        f"- tests run: {tests_run}",
        f"- validation results: {test_results}",
        f"- generated result files: {generated_result_files}",
        "",
        "## Review",
        f"- reviewer: {reviewer}",
        f"- review status: {review_status}",
        f"- unresolved questions: {unresolved_questions}",
        f"- remaining risks: {remaining_risks}",
        "",
        "## Git",
        f"- commit hash: {commit_hash}",
        f"- push status: {push_status}",
        "",
    ]
    return "\n".join(lines)


def create_traceability_manifest(
    out_path: Path,
    **kwargs,
) -> Path:
    """Write a traceability manifest to disk.

    Parameters
    ----------
    out_path : Path
        Output file path. Parent directories are created automatically.
    **kwargs
        Forwarded to build_traceability_markdown.

    Returns
    -------
    Path
        The path the manifest was written to.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = build_traceability_markdown(**kwargs)
    out_path.write_text(content, encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Create or update a task traceability manifest.",
    )
    parser.add_argument("--task-id", required=True, help="Unique task identifier")
    parser.add_argument("--task-type", default="", help="Task type (paper-to-code, numerical-method, cfd-case, other)")
    parser.add_argument("--source", default="", help="Path to source material")
    parser.add_argument("--extraction-report", default="", help="Path to extraction report")
    parser.add_argument("--scheme-spec", default="", help="Path to scheme spec")
    parser.add_argument("--validation-result", default="", help="Path to validation results")
    parser.add_argument("--commit-hash", default="", help="Git commit hash")
    parser.add_argument("--modules-to-change", default="", help="Modules expected to change")
    parser.add_argument("--modules-protected", default="cfd/ (numerical core), solver/, examples/, tests/", help="Protected modules")
    parser.add_argument("--modified-files", default="", help="Actually modified files")
    parser.add_argument("--added-files", default="", help="Actually added files")
    parser.add_argument("--tests-run", default="", help="Test commands run")
    parser.add_argument("--test-results", default="", help="Test results summary")
    parser.add_argument("--validation-files", default="", help="Generated result files")
    parser.add_argument("--reviewer", default="", help="Reviewer name or agent")
    parser.add_argument("--review-status", default="", help="Review status")
    parser.add_argument("--unresolved-questions", default="", help="Unresolved questions")
    parser.add_argument("--remaining-risks", default="", help="Remaining risks")
    parser.add_argument("--push-status", default="", help="Git push status")
    parser.add_argument("--implementation-status", default="", help="Implementation status")
    parser.add_argument("--out", default="", help="Output path (default: docs/tasks/<task_id>/traceability.md)")
    args = parser.parse_args(argv)

    out_path = Path(args.out) if args.out else Path(f"docs/tasks/{args.task_id}/traceability.md")

    # Auto-detect commit hash if not provided
    commit_hash = args.commit_hash
    if not commit_hash:
        try:
            import subprocess
            commit_hash = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
            ).decode().strip()
        except Exception:
            commit_hash = "unknown"

    created = create_traceability_manifest(
        out_path=out_path,
        task_id=args.task_id,
        task_type=args.task_type,
        source=args.source,
        extraction_report=args.extraction_report,
        scheme_spec=args.scheme_spec,
        validation_result=args.validation_result,
        commit_hash=commit_hash,
        modules_to_change=args.modules_to_change,
        modules_protected=args.modules_protected,
        modified_files=args.modified_files,
        added_files=args.added_files,
        tests_run=args.tests_run,
        test_results=args.test_results,
        generated_result_files=args.validation_files,
        reviewer=args.reviewer,
        review_status=args.review_status,
        unresolved_questions=args.unresolved_questions,
        remaining_risks=args.remaining_risks,
        push_status=args.push_status,
        implementation_status=args.implementation_status,
    )

    print(f"Traceability manifest written to: {created}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
