"""Integration test: solver runs uniform flow to completion."""

import numpy as np
import os
import tempfile
import pytest

from cfd.cases.uniform_flow import uniform_flow_config, uniform_flow_ic
from cfd.solver import run_solver


def test_solver_uniform_flow():
    """Uniform flow should be preserved (errors near machine epsilon)."""
    config = uniform_flow_config()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_solver(
            config=config,
            initial_condition_func=uniform_flow_ic,
            case_name="test_uniform",
            output_dir=tmpdir,
        )
    ng = config.ng
    U_int = result["U"][:, ng:-ng, ng:-ng]
    rho_err = np.max(np.abs(U_int[0] - 1.0))
    assert rho_err < 1e-10, f"Uniform flow rho error: {rho_err}"
    assert result["n_steps"] > 0
    assert result["actual_final_time"] > 0


def test_solver_output_files():
    """Solver should produce output files."""
    config = uniform_flow_config()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_solver(
            config=config,
            initial_condition_func=uniform_flow_ic,
            case_name="test_output",
            output_dir=tmpdir,
        )
        paths = result["output_paths"]
        assert os.path.exists(paths["csv"])
        assert os.path.exists(paths["npz"])
        assert os.path.exists(paths["md"])
