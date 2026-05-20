"""Tests for the CFWENO3 scalar advection prototype.

Covers: import, shape, constant state, mass conservation, sine wave,
CFL validation, and approval checker integration.
"""

import subprocess
import sys

import numpy as np
import pytest

# ---- import test -----------------------------------------------------------

def test_cfweno_import():
    """CFWENO scheme is importable and registered."""
    from solver.schemes import _SCHEMES, cfweno
    assert "cfweno" in _SCHEMES
    assert _SCHEMES["cfweno"] is cfweno


def test_step_dispatches_cfweno():
    """step() dispatches to cfweno when scheme='cfweno'."""
    from solver.schemes import step
    u = np.sin(2 * np.pi * np.linspace(0, 1, 50, endpoint=False)) + 1.0
    result = step(u, 0.5, scheme="cfweno")
    assert result.shape == u.shape


# ---- shape and basic properties --------------------------------------------

def test_cfweno_shape_preserved():
    """Output shape matches input shape."""
    from solver.schemes import cfweno
    for nx in [20, 50, 100]:
        u = np.ones(nx)
        assert cfweno(u, 0.5).shape == (nx,)


def test_cfweno_constant_state():
    """Constant state is preserved exactly."""
    from solver.schemes import cfweno
    u = np.full(100, 3.14)
    result = cfweno(u, 0.5)
    np.testing.assert_allclose(result, u, atol=1e-14)


def test_cfweno_mass_conservation():
    """Mass (sum of u) is conserved to machine precision for one step."""
    from solver.schemes import cfweno
    nx = 100
    x = np.linspace(0, 1, nx, endpoint=False)
    u = np.sin(2 * np.pi * x) + 1.0
    result = cfweno(u, 0.5)
    mass_before = np.sum(u)
    mass_after = np.sum(result)
    assert abs(mass_after - mass_before) < 1e-12


# ---- sine wave short-time run ---------------------------------------------

def test_cfweno_sine_wave_no_nan():
    """Sine wave runs 10 steps without NaN."""
    from solver.schemes import step
    nx = 80
    x = np.linspace(0, 1, nx, endpoint=False)
    u = np.sin(2 * np.pi * x) + 1.0
    for _ in range(10):
        u = step(u, 0.5, scheme="cfweno")
    assert not np.any(np.isnan(u))
    assert not np.any(np.isinf(u))


def test_cfweno_sine_wave_error_bounded():
    """After 5 steps, L2 error is reasonable for CFWENO3."""
    from solver.simulate import compute_errors
    from solver.schemes import step
    nx = 80
    dx = 1.0 / nx
    cfl = 0.5
    x = np.linspace(0, 1, nx, endpoint=False)
    u = np.sin(2 * np.pi * x) + 1.0
    t = 0.0
    dt = cfl * dx  # a=1
    n_steps = 5
    for _ in range(n_steps):
        u = step(u, cfl, scheme="cfweno")
        t += dt
    u_exact = np.sin(2 * np.pi * (x - t)) + 1.0
    errs = compute_errors(u, u_exact, dx)
    assert errs["l2_error"] < 0.1, f"L2 error too large: {errs['l2_error']}"


# ---- CFL validation --------------------------------------------------------

def test_cfweno_cfl_gt_1_raises():
    """CFL > 1 raises ValueError via step()."""
    from solver.schemes import step
    u = np.ones(50)
    with pytest.raises(ValueError, match="CFL"):
        step(u, 1.5, scheme="cfweno")


def test_cfweno_cfl_negative_raises():
    """Negative CFL raises ValueError via step()."""
    from solver.schemes import step
    u = np.ones(50)
    with pytest.raises(ValueError, match="CFL"):
        step(u, -0.1, scheme="cfweno")


def test_cfweno_cfl_zero():
    """CFL = 0 means no update (identity)."""
    from solver.schemes import cfweno
    u = np.sin(2 * np.pi * np.linspace(0, 1, 50, endpoint=False)) + 1.0
    result = cfweno(u, 0.0)
    np.testing.assert_allclose(result, u, atol=1e-14)


# ---- run_advection integration ---------------------------------------------

def test_cfweno_run_advection():
    """run_advection works with scheme='cfweno'."""
    from solver.simulate import run_advection, compute_errors
    res = run_advection("cfweno", nx=80, cfl=0.5, final_time=0.1)
    errs = compute_errors(res["u_num"], res["u_exact"], res["dx"])
    assert errs["l2_error"] < 0.05
    assert res["u_num"].shape == (80,)


# ---- approval checker integration ------------------------------------------

def test_scalar_subset_spec_approved():
    """cfweno_scalar_subset.md is approved for implementation."""
    from pathlib import Path
    import tools.check_scheme_spec_approval as checker
    result = checker.check_spec_approval(Path("docs/scheme_specs/cfweno_scalar_subset.md"))
    assert result["approved"] is True


def test_full_cfweno_spec_not_approved():
    """cfweno_pof_2025.md is NOT approved."""
    from pathlib import Path
    import tools.check_scheme_spec_approval as checker
    result = checker.check_spec_approval(Path("docs/scheme_specs/cfweno_pof_2025.md"))
    assert result["approved"] is False
