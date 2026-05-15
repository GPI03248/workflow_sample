"""Tests for tools/create_task_traceability.py.

Covers:
- build_traceability_markdown: task id present, all sections, approval info
- create_traceability_manifest: writes file, creates parent dirs
- Approval status integration: reads real spec approval info
- CLI: basic invocation
No network, no PDF dependency.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from create_task_traceability import build_traceability_markdown, create_traceability_manifest


class TestBuildTraceabilityMarkdown:
    def test_contains_task_id(self):
        md = build_traceability_markdown(task_id="test_task")
        assert "test_task" in md

    def test_contains_all_sections(self):
        md = build_traceability_markdown(task_id="t1")
        for section in ["Task metadata", "Source material", "Approval status",
                        "Intended code changes", "Actual code changes",
                        "Tests and validation", "Review", "Git"]:
            assert section in md

    def test_includes_approval_info(self):
        md = build_traceability_markdown(
            task_id="t1",
            approval_info={"approved": False, "status": "no", "reason": "not approved"},
        )
        assert "no" in md
        assert "not approved" in md

    def test_includes_source_material(self):
        md = build_traceability_markdown(
            task_id="t1",
            source="docs/papers/test.pdf",
            extraction_report="docs/paper_reviews/test_extraction.md",
        )
        assert "docs/papers/test.pdf" in md
        assert "docs/paper_reviews/test_extraction.md" in md

    def test_includes_commit_hash(self):
        md = build_traceability_markdown(task_id="t1", commit_hash="abc1234")
        assert "abc1234" in md

    def test_includes_implementation_status(self):
        md = build_traceability_markdown(
            task_id="t1",
            implementation_status="rejected by approval gate",
        )
        assert "rejected by approval gate" in md

    def test_default_empty_strings(self):
        md = build_traceability_markdown(task_id="t1")
        # Should not crash with all defaults
        assert isinstance(md, str)
        assert len(md) > 0

    def test_approval_info_approved(self):
        md = build_traceability_markdown(
            task_id="t1",
            approval_info={"approved": True, "status": "yes", "reason": "Approved for implementation is yes"},
        )
        assert "yes" in md
        assert "Approved for implementation is yes" in md


class TestCreateTraceabilityManifest:
    def test_writes_file(self, tmp_path):
        out = tmp_path / "tasks" / "t1" / "traceability.md"
        path = create_traceability_manifest(out, task_id="t1")
        assert path.is_file()
        content = path.read_text()
        assert "t1" in content

    def test_creates_parent_dirs(self, tmp_path):
        out = tmp_path / "deep" / "nested" / "traceability.md"
        create_traceability_manifest(out, task_id="t1")
        assert out.is_file()

    def test_written_content_is_valid_markdown(self, tmp_path):
        out = tmp_path / "tasks" / "t1" / "traceability.md"
        create_traceability_manifest(out, task_id="t1")
        content = out.read_text()
        assert content.startswith("# Task Traceability Manifest")

    def test_includes_all_kwargs(self, tmp_path):
        out = tmp_path / "tasks" / "t1" / "traceability.md"
        create_traceability_manifest(
            out,
            task_id="t1",
            task_type="paper-to-code",
            source="docs/papers/test.pdf",
            commit_hash="abc1234",
            remaining_risks="none",
        )
        content = out.read_text()
        assert "paper-to-code" in content
        assert "docs/papers/test.pdf" in content
        assert "abc1234" in content
        assert "none" in content


class TestApprovalIntegration:
    def test_reads_hll_flux_spec_approval(self, tmp_path):
        """When scheme spec is hll_flux.md (not approved), manifest reflects that."""
        spec_path = Path("docs/scheme_specs/hll_flux.md")
        if not spec_path.exists():
            pytest.skip("hll_flux.md not present")

        from check_scheme_spec_approval import check_spec_approval
        approval = check_spec_approval(spec_path)
        assert approval["approved"] is False

        md = build_traceability_markdown(
            task_id="hll_flux_test",
            approval_info=approval,
        )
        assert "no" in md.lower() or "false" in md.lower()

    def test_no_spec_path_gives_none_approval(self):
        """When no spec path provided, approval_info should indicate no spec."""
        md = build_traceability_markdown(
            task_id="t1",
            approval_info={"approved": None, "status": None, "reason": "No spec provided"},
        )
        assert "No spec provided" in md


class TestTraceabilityCLI:
    def test_basic_invocation(self, tmp_path):
        out = tmp_path / "tasks" / "cli_test" / "traceability.md"
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "create_task_traceability.py"),
             "--task-id", "cli_test",
             "--out", str(out)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        assert out.is_file()
        assert "cli_test" in out.read_text()

    def test_with_scheme_spec(self, tmp_path):
        spec_path = Path("docs/scheme_specs/hll_flux.md")
        if not spec_path.exists():
            pytest.skip("hll_flux.md not present")

        out = tmp_path / "tasks" / "cli_spec_test" / "traceability.md"
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "create_task_traceability.py"),
             "--task-id", "cli_spec_test",
             "--scheme-spec", str(spec_path),
             "--out", str(out)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        assert out.is_file()
