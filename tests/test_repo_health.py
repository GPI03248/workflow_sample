"""Tests for tools/check_repo_health.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from check_repo_health import (
    check_old_env_commands,
    check_scheme_spec_approval,
    check_approved_spec_traceability,
    check_hll_artifacts,
    check_readme_paths,
    run_all_checks,
)


class TestCheckSchemeSpecApproval:
    def test_missing_approval_line(self, tmp_path):
        spec_dir = tmp_path / "docs" / "scheme_specs"
        spec_dir.mkdir(parents=True)
        (spec_dir / "test.md").write_text("# No approval line here\n")
        errors, warnings = check_scheme_spec_approval(tmp_path)
        assert len(errors) == 1
        assert "missing" in errors[0].lower()

    def test_approved_yes(self, tmp_path):
        spec_dir = tmp_path / "docs" / "scheme_specs"
        spec_dir.mkdir(parents=True)
        (spec_dir / "test.md").write_text("Approved for implementation: yes\n")
        errors, warnings = check_scheme_spec_approval(tmp_path)
        assert len(errors) == 0

    def test_approved_no(self, tmp_path):
        spec_dir = tmp_path / "docs" / "scheme_specs"
        spec_dir.mkdir(parents=True)
        (spec_dir / "test.md").write_text("Approved for implementation: no\n")
        errors, warnings = check_scheme_spec_approval(tmp_path)
        assert len(errors) == 0

    def test_abnormal_status(self, tmp_path):
        spec_dir = tmp_path / "docs" / "scheme_specs"
        spec_dir.mkdir(parents=True)
        (spec_dir / "test.md").write_text("Approved for implementation: maybe\n")
        errors, warnings = check_scheme_spec_approval(tmp_path)
        assert len(errors) == 1
        assert "abnormal" in errors[0].lower()


class TestCheckOldEnvCommands:
    def test_comment_allowed(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text("# Do not use bash -ic\n")
        errors, warnings = check_old_env_commands(tmp_path)
        assert len(errors) == 0

    def test_makefile_recipe_error(self, tmp_path):
        mf = tmp_path / "Makefile"
        mf.write_text("test:\n\tbash -ic 'module-conda && pytest'\n")
        errors, warnings = check_old_env_commands(tmp_path)
        assert len(errors) >= 1

    def test_shell_script_error(self, tmp_path):
        script = tmp_path / "tools" / "run.sh"
        script.parent.mkdir(parents=True)
        script.write_text("#!/bin/bash\nbash -ic 'module-conda'\n")
        errors, warnings = check_old_env_commands(tmp_path)
        assert len(errors) >= 1

    def test_python_docstring_allowed(self, tmp_path):
        py = tmp_path / "tests" / "test.py"
        py.parent.mkdir(parents=True)
        py.write_text('"""Do not use bash -ic."""\nassert True\n')
        errors, warnings = check_old_env_commands(tmp_path)
        assert len(errors) == 0


class TestCheckHllArtifacts:
    def test_all_present(self, tmp_path):
        for path in [
            "results/cfd_hll_validation/error_summary.csv",
            "results/cfd_hll_validation/analysis.md",
            "docs/tasks/hll_flux_implementation/traceability.md",
            "docs/case_studies/hll_flux_paper_to_code.md",
        ]:
            p = tmp_path / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("content")
        errors, warnings = check_hll_artifacts(tmp_path)
        assert len(errors) == 0

    def test_missing_artifact(self, tmp_path):
        errors, warnings = check_hll_artifacts(tmp_path)
        assert len(errors) > 0


class TestCheckReadmePaths:
    def test_all_present(self, tmp_path):
        for path in [
            "tools/run_in_project_env.sh",
            "examples/run_cfd_hll_validation.py",
            "results/cfd_hll_validation/error_summary.csv",
            "results/cfd_hll_validation/analysis.md",
            "docs/case_studies/hll_flux_paper_to_code.md",
        ]:
            p = tmp_path / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("content")
        errors, warnings = check_readme_paths(tmp_path)
        # validation_index is a warning, not error
        assert all("validation_index" not in e for e in errors)

    def test_missing_error_paths(self, tmp_path):
        errors, warnings = check_readme_paths(tmp_path)
        assert len(errors) > 0


class TestRunAllChecks:
    def test_returns_dict(self):
        result = run_all_checks(Path("."))
        assert "ok" in result
        assert "errors" in result
        assert "warnings" in result
        assert "checks" in result
        assert isinstance(result["checks"], list)


class TestCLI:
    def test_json_output(self):
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "check_repo_health.py"), "--json"],
            capture_output=True, text=True,
        )
        data = json.loads(r.stdout)
        assert "ok" in data
        assert "checks" in data

    def test_exit_code_on_errors(self, tmp_path):
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "check_repo_health.py"), "--json"],
            capture_output=True, text=True,
            cwd=str(tmp_path),
        )
        # tmp_path has no specs, no artifacts -> should fail
        assert r.returncode != 0
