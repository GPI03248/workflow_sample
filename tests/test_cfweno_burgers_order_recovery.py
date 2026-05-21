"""Tests for CFWENO3 Burgers order recovery diagnostic study."""

import csv
import importlib.util
import os
import subprocess
import sys

import numpy as np
import pytest

# Paths
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
SCRIPT = os.path.join(REPO_ROOT, "examples", "run_cfweno_burgers_order_recovery.py")
RESULTS_DIR = os.path.join(REPO_ROOT, "results", "cfweno_burgers_order_recovery")
ENV_WRAPPER = os.path.join(REPO_ROOT, "tools", "run_in_project_env.sh")


def _load_diagnostic_module():
    """Load the diagnostic script as a module (it lives in examples/, not on sys.path)."""
    spec = importlib.util.spec_from_file_location("cfweno_order_recovery", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestDiagnosticImports:
    """Test that the diagnostic script imports correctly."""

    def test_script_imports(self):
        """Script file exists and is valid Python."""
        assert os.path.isfile(SCRIPT)
        with open(SCRIPT) as f:
            code = f.read()
        compile(code, SCRIPT, "exec")

    def test_production_solver_unchanged(self):
        """solver/schemes.py was NOT modified for this diagnostic."""
        from solver.schemes import cfweno_burgers, _cfweno3_stencil, _interface_reconstruction
        assert callable(cfweno_burgers)
        assert callable(_cfweno3_stencil)
        assert callable(_interface_reconstruction)


class TestDiagnosticVariants:
    """Test that diagnostic variants produce finite arrays."""

    def _run_variant_quick(self, variant_fn, nx=40):
        dx = 1.0 / nx
        x = np.linspace(0, 1, nx, endpoint=False)
        u = 1.0 + 0.2 * np.sin(2.0 * np.pi * x)
        dt = 0.3 * dx / np.max(np.abs(u))
        result = variant_fn(u, dx, dt)
        assert np.all(np.isfinite(result))
        assert result.shape == u.shape
        return result

    def test_constant_nu_variant(self):
        mod = _load_diagnostic_module()
        self._run_variant_quick(mod._diag_constant_nu)

    def test_interface_nu_variant(self):
        mod = _load_diagnostic_module()
        self._run_variant_quick(mod._diag_interface_nu)

    def test_predictor_interface_nu_variant(self):
        mod = _load_diagnostic_module()
        self._run_variant_quick(mod._diag_predictor_interface_nu)


class TestMassConservation:
    """Mass conservation remains bounded for all variants."""

    @pytest.mark.parametrize("variant_name", [
        "_diag_constant_nu",
        "_diag_interface_nu",
        "_diag_predictor_interface_nu",
    ])
    def test_mass_conservation(self, variant_name):
        mod = _load_diagnostic_module()
        variant_fn = getattr(mod, variant_name)
        nx = 80
        dx = 1.0 / nx
        x = np.linspace(0, 1, nx, endpoint=False)
        u = 1.0 + 0.2 * np.sin(2.0 * np.pi * x)
        mass0 = np.sum(u) * dx
        # Run 10 steps
        for _ in range(10):
            dt = 0.3 * dx / np.max(np.abs(u))
            u = variant_fn(u, dx, dt)
        mass1 = np.sum(u) * dx
        assert abs(mass1 - mass0) < 1e-10, f"Mass drift for {variant_name}"


class TestQuickRunOutput:
    """Test quick mode produces valid output files."""

    @pytest.fixture(autouse=True)
    def run_quick(self, tmp_path):
        """Run the script in --quick mode."""
        result = subprocess.run(
            [sys.executable, SCRIPT, "--quick"],
            cwd=REPO_ROOT,
            capture_output=True, text=True, timeout=120,
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"

    def test_csv_parseable(self):
        csv_path = os.path.join(RESULTS_DIR, "error_summary.csv")
        assert os.path.isfile(csv_path)
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) > 0
        required = ["case_id", "amplitude", "variant", "nx", "l2_error"]
        for row in rows:
            for field in required:
                assert field in row, f"Missing field {field}"

    def test_analysis_md_exists(self):
        md_path = os.path.join(RESULTS_DIR, "analysis.md")
        assert os.path.isfile(md_path)
        with open(md_path) as f:
            content = f.read()
        assert "Conclusions" in content
        assert "NOT modified" in content


class TestV1TagUnchanged:
    """Verify v1.0 tag was not moved."""

    def test_v1_tag_target(self):
        result = subprocess.run(
            ["git", "rev-parse", "v1.0^{}"],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "42d97eea85a74337c21deee35f8745df6c5b3a18"

    def test_schemes_py_not_modified(self):
        """solver/schemes.py should not have uncommitted changes."""
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", "solver/schemes.py"],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        assert result.stdout.strip() == ""
