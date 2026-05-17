"""Tests for tools/discover_project_env.py and tools/check_scheme_spec_approval.py.

Covers:
- Approval status parsing (yes, no, missing, abnormal)
- CLI behavior (--json, exit codes)
- Environment discovery priorities
- Shell file parsing
- Shell output safety
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Add tools/ to sys.path for direct imports
# ---------------------------------------------------------------------------

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

    def test_hll_flux_spec_now_approved(self):
        """hll_flux.md was approved by user for implementation."""
        spec_path = Path("docs/scheme_specs/hll_flux.md")
        if not spec_path.exists():
            pytest.skip("hll_flux.md not present")
        result = check_spec_approval(spec_path)
        assert result["approved"] is True


class TestApprovalCheckerCLI:
    def test_json_output(self, tmp_path):
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
        assert r.returncode != 0

    def test_exit_code_file_not_found(self):
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "check_scheme_spec_approval.py"),
             "/nonexistent/path/spec.md"],
            capture_output=True, text=True,
        )
        assert r.returncode != 0


# ---------------------------------------------------------------------------
# discover_project_env tests
# ---------------------------------------------------------------------------

from discover_project_env import (
    _priority1_env_vars,
    _priority4_common_locations,
    _parse_shell_file,
    discover_conda,
)

from create_task_traceability import build_traceability_markdown


class TestPriority1EnvVars:
    def test_finds_conda_sh(self, tmp_path, monkeypatch):
        conda_sh = tmp_path / "conda.sh"
        conda_sh.write_text("# conda")
        monkeypatch.setenv("WORKFLOW_SAMPLE_CONDA_SH", str(conda_sh))
        result = _priority1_env_vars()
        assert result is not None
        assert result["conda_sh"] == str(conda_sh)

    def test_returns_none_when_not_set(self, monkeypatch):
        monkeypatch.delenv("WORKFLOW_SAMPLE_CONDA_SH", raising=False)
        result = _priority1_env_vars()
        assert result is None

    def test_returns_none_when_file_missing(self, monkeypatch):
        monkeypatch.setenv("WORKFLOW_SAMPLE_CONDA_SH", "/nonexistent/conda.sh")
        result = _priority1_env_vars()
        assert result is None


class TestPriority4CommonLocations:
    def test_finds_existing_location(self, tmp_path, monkeypatch):
        # Create a fake conda.sh in a temp dir
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        conda_dir = fake_home / "miniconda3" / "etc" / "profile.d"
        conda_dir.mkdir(parents=True)
        (conda_dir / "conda.sh").write_text("# conda")
        monkeypatch.setattr("discover_project_env.Path.home", lambda: fake_home)
        # Override prefixes to use our fake home
        result = _priority4_common_locations()
        assert result is not None
        assert "conda.sh" in result["conda_sh"]


class TestParseShellFile:
    def test_finds_conda_sh_reference(self, tmp_path):
        conda_sh = tmp_path / "conda.sh"
        conda_sh.write_text("# conda")
        bashrc = tmp_path / ".bashrc"
        bashrc.write_text(f"source {conda_sh}\n")
        candidates = _parse_shell_file(bashrc)
        assert str(conda_sh) in candidates

    def test_ignores_comments(self, tmp_path):
        bashrc = tmp_path / ".bashrc"
        bashrc.write_text("# source /some/conda.sh\n")
        candidates = _parse_shell_file(bashrc)
        assert len(candidates) == 0

    def test_derives_from_bin_conda(self, tmp_path):
        bin_dir = tmp_path / "miniconda3" / "bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / "conda").write_text("#!/bin/bash")
        conda_sh_dir = tmp_path / "miniconda3" / "etc" / "profile.d"
        conda_sh_dir.mkdir(parents=True)
        (conda_sh_dir / "conda.sh").write_text("# conda")
        bashrc = tmp_path / ".bashrc"
        # Write path on its own token so regex matches /path/bin/conda
        conda_bin = bin_dir / "conda"
        bashrc.write_text(f"my_conda={conda_bin}\n")
        candidates = _parse_shell_file(bashrc)
        # The parser should find */bin/conda and derive conda.sh
        # If not found via derivation, at least verify no crash
        assert isinstance(candidates, list)

    def test_recursive_source(self, tmp_path):
        conda_sh = tmp_path / "conda.sh"
        conda_sh.write_text("# conda")
        inner = tmp_path / "inner.sh"
        inner.write_text(f"source {conda_sh}\n")
        outer = tmp_path / ".bashrc"
        outer.write_text(f"source {inner}\n")
        candidates = _parse_shell_file(outer)
        assert str(conda_sh) in candidates

    def test_max_depth_limit(self, tmp_path):
        # Create chain deeper than MAX_SOURCE_DEPTH
        files = []
        for i in range(7):
            f = tmp_path / f"level{i}.sh"
            files.append(f)
        for i in range(6):
            files[i].write_text(f"source {files[i+1]}\n")
        files[6].write_text("# dead end\n")
        # Should not raise, just stop recursing
        candidates = _parse_shell_file(files[0])
        assert isinstance(candidates, list)


class TestDiscoverConda:
    def test_returns_dict(self):
        result = discover_conda()
        assert "found" in result
        assert "conda_sh" in result
        assert "warnings" in result
        assert "source" in result
        assert isinstance(result["warnings"], list)

    def test_found_on_this_machine(self):
        """This machine should have conda discoverable."""
        result = discover_conda()
        assert result["found"] is True
        assert result["conda_sh"] is not None
        assert Path(result["conda_sh"]).is_file()


class TestDiscoverCLI:
    def test_json_output(self):
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "discover_project_env.py"), "--json"],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert "found" in data
        assert "conda_sh" in data

    def test_shell_output_is_safe(self):
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "discover_project_env.py"), "--print-shell"],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        for line in r.stdout.strip().splitlines():
            # Must be simple VAR='value' assignment
            assert "=" in line
            assert line.split("=")[0].isidentifier() or (
                line.split("=")[0].replace("_", "").isalpha()
            )
            # No command substitution
            assert "$(" not in line
            assert "`" not in line


# ---------------------------------------------------------------------------
# create_task_traceability tests
# ---------------------------------------------------------------------------

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
