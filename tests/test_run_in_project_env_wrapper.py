"""Tests for tools/run_in_project_env.sh wrapper script.

Verifies the wrapper script exists, is executable, does not contain
bash -ic or module-conda, and can execute simple commands.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

WRAPPER = Path("tools/run_in_project_env.sh")


class TestWrapperScript:
    def test_exists(self):
        assert WRAPPER.is_file(), "run_in_project_env.sh not found"

    def test_is_executable(self):
        assert WRAPPER.exists()
        assert os.access(WRAPPER, os.X_OK), "run_in_project_env.sh is not executable"

    def test_no_bash_ic_in_code(self):
        """Only code lines (not comments) should not contain bash -ic."""
        content = WRAPPER.read_text()
        code_lines = [l for l in content.splitlines()
                      if l.strip() and not l.strip().startswith("#")]
        for line in code_lines:
            assert "bash -i" not in line, f"Found bash -i in code: {line}"

    def test_no_module_conda_in_code(self):
        """Only code lines (not comments) should not contain module-conda."""
        content = WRAPPER.read_text()
        code_lines = [l for l in content.splitlines()
                      if l.strip() and not l.strip().startswith("#")]
        for line in code_lines:
            assert "module-conda" not in line, f"Found module-conda in code: {line}"

    def test_can_execute_python(self):
        r = subprocess.run(
            [str(WRAPPER), sys.executable, "--version"],
            capture_output=True, text=True,
            timeout=30,
        )
        assert r.returncode == 0
        assert "Python" in r.stdout or "Python" in r.stderr

    def test_can_execute_simple_command(self):
        r = subprocess.run(
            [str(WRAPPER), "echo", "hello"],
            capture_output=True, text=True,
            timeout=30,
        )
        assert r.returncode == 0
        assert "hello" in r.stdout

    def test_fallback_without_conda(self):
        """Wrapper should still work even if conda.sh is empty/missing."""
        env = os.environ.copy()
        env["WORKFLOW_SAMPLE_CONDA_SH"] = "/nonexistent/conda.sh"
        r = subprocess.run(
            [str(WRAPPER), "echo", "works"],
            capture_output=True, text=True,
            timeout=30,
            env=env,
        )
        assert r.returncode == 0
        assert "works" in r.stdout
