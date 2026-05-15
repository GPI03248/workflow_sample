"""Tests for tools/check_scheme_spec_approval.py.

Covers:
- parse_approval_status: yes, no, missing, case-insensitive, abnormal, embedded
- check_spec_approval: approved, not approved, missing line, file not found
- CLI: --json output, exit codes (0=approved, 1=not approved, 2=file error)
- Real spec: hll_flux.md must be detected as not approved
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from check_scheme_spec_approval import parse_approval_status, check_spec_approval


class TestParseApprovalStatus:
    def test_yes(self):
        assert parse_approval_status("Approved for implementation: yes") == "yes"

    def test_no(self):
        assert parse_approval_status("Approved for implementation: no") == "no"

    def test_missing(self):
        assert parse_approval_status("some other text") is None

    def test_case_insensitive(self):
        assert parse_approval_status("approved for Implementation: YES") == "yes"

    def test_extra_spaces(self):
        assert parse_approval_status("Approved for implementation:  yes ") == "yes"

    def test_abnormal_value(self):
        assert parse_approval_status("Approved for implementation: maybe") == "maybe"

    def test_embedded_in_larger_text(self):
        text = "# Status\nApproved for implementation: no\n## Next"
        assert parse_approval_status(text) == "no"


class TestCheckSpecApproval:
    def test_approved_yes(self, tmp_path):
        spec = tmp_path / "spec.md"
        spec.write_text("# Status\nApproved for implementation: yes\n")
        result = check_spec_approval(spec)
        assert result["approved"] is True
        assert result["status"] == "yes"

    def test_approved_no(self, tmp_path):
        spec = tmp_path / "spec.md"
        spec.write_text("# Status\nApproved for implementation: no\n")
        result = check_spec_approval(spec)
        assert result["approved"] is False
        assert result["status"] == "no"

    def test_missing_approval_line(self, tmp_path):
        spec = tmp_path / "spec.md"
        spec.write_text("# Status\nNothing here\n")
        result = check_spec_approval(spec)
        assert result["approved"] is False
        assert result["status"] is None

    def test_file_not_found(self, tmp_path):
        spec = tmp_path / "nonexistent.md"
        result = check_spec_approval(spec)
        assert result["approved"] is False
        assert "not found" in result["reason"].lower()

    def test_abnormal_status_not_approved(self, tmp_path):
        spec = tmp_path / "spec.md"
        spec.write_text("Approved for implementation: pending\n")
        result = check_spec_approval(spec)
        assert result["approved"] is False
        assert result["status"] == "pending"


class TestApprovalCheckerCLI:
    def test_json_output_not_approved(self, tmp_path):
        spec = tmp_path / "spec.md"
        spec.write_text("Approved for implementation: no\n")
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "check_scheme_spec_approval.py"),
             str(spec), "--json"],
            capture_output=True, text=True,
        )
        assert r.returncode != 0
        data = json.loads(r.stdout)
        assert data["approved"] is False
        assert data["status"] == "no"

    def test_json_output_approved(self, tmp_path):
        spec = tmp_path / "spec.md"
        spec.write_text("Approved for implementation: yes\n")
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "check_scheme_spec_approval.py"),
             str(spec), "--json"],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert data["approved"] is True

    def test_exit_code_approved(self, tmp_path):
        spec = tmp_path / "spec.md"
        spec.write_text("Approved for implementation: yes\n")
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "check_scheme_spec_approval.py"),
             str(spec)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0

    def test_exit_code_not_approved(self, tmp_path):
        spec = tmp_path / "spec.md"
        spec.write_text("Approved for implementation: no\n")
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "check_scheme_spec_approval.py"),
             str(spec)],
            capture_output=True, text=True,
        )
        assert r.returncode == 1

    def test_exit_code_file_not_found(self):
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "check_scheme_spec_approval.py"),
             "/nonexistent/path/spec.md"],
            capture_output=True, text=True,
        )
        assert r.returncode == 2

    def test_human_readable_output(self, tmp_path):
        spec = tmp_path / "spec.md"
        spec.write_text("Approved for implementation: no\n")
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "check_scheme_spec_approval.py"),
             str(spec)],
            capture_output=True, text=True,
        )
        assert "NOT APPROVED" in r.stdout


class TestRealSpecs:
    def test_hll_flux_spec_not_approved(self):
        """Current hll_flux.md must be detected as not approved."""
        spec_path = Path("docs/scheme_specs/hll_flux.md")
        if not spec_path.exists():
            pytest.skip("hll_flux.md not present")
        result = check_spec_approval(spec_path)
        assert result["approved"] is False
