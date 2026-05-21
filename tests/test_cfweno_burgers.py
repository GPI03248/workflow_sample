"""Tests for the CFWENO3 scalar nonlinear Burgers prototype.

Covers: import, shape, constant state, mass conservation, finite values,
CFL rejection, predictor iterations, CSV parseability, approval checker,
sweep output parseability, audit document existence.
"""

import csv
import os

import numpy as np
import pytest


# ---- import tests -----------------------------------------------------------

def test_cfweno_burgers_import():
    """CFWENO Burgers scheme is importable."""
    from solver.schemes import cfweno_burgers
    assert callable(cfweno_burgers)


def test_burgers_upwind_import():
    """Burgers Rusanov baseline is importable."""
    from solver.schemes import burgers_upwind
    assert callable(burgers_upwind)


# ---- shape preservation -----------------------------------------------------

def test_cfweno_burgers_shape():
    """Output shape matches input shape."""
    from solver.schemes import cfweno_burgers
    for nx in [20, 50, 100]:
        u = np.ones(nx) * 1.5
        dx = 1.0 / nx
        dt = 0.5 * dx / np.max(np.abs(u))
        result = cfweno_burgers(u, dx, dt)
        assert result.shape == (nx,)


# ---- constant state ---------------------------------------------------------

def test_cfweno_burgers_constant_state():
    """Constant state is preserved exactly."""
    from solver.schemes import cfweno_burgers
    u = np.full(100, 2.0)
    dx = 0.01
    dt = 0.5 * dx / np.max(np.abs(u))
    result = cfweno_burgers(u, dx, dt, predictor_iterations=0)
    np.testing.assert_allclose(result, u, atol=1e-12)


def test_cfweno_burgers_constant_with_predictor():
    """Constant state preserved with predictor iterations."""
    from solver.schemes import cfweno_burgers
    u = np.full(100, 2.0)
    dx = 0.01
    dt = 0.5 * dx / np.max(np.abs(u))
    result = cfweno_burgers(u, dx, dt, predictor_iterations=2)
    np.testing.assert_allclose(result, u, atol=1e-12)


# ---- mass conservation ------------------------------------------------------

def test_cfweno_burgers_mass_conservation():
    """Mass is conserved to machine precision for one step."""
    from solver.schemes import cfweno_burgers
    nx = 100
    x = np.linspace(0, 1, nx, endpoint=False)
    u = 1.0 + 0.2 * np.sin(2.0 * np.pi * x)
    dx = 1.0 / nx
    dt = 0.3 * dx / np.max(np.abs(u))
    result = cfweno_burgers(u, dx, dt)
    mass_before = np.sum(u) * dx
    mass_after = np.sum(result) * dx
    assert abs(mass_after - mass_before) < 1e-12


def test_cfweno_burgers_mass_conservation_multi_step():
    """Mass conserved over 50 steps."""
    from solver.schemes import cfweno_burgers
    nx = 80
    x = np.linspace(0, 1, nx, endpoint=False)
    u = 1.0 + 0.2 * np.sin(2.0 * np.pi * x)
    dx = 1.0 / nx
    mass0 = np.sum(u) * dx
    for _ in range(50):
        max_speed = np.max(np.abs(u))
        dt = 0.4 * dx / max(max_speed, 1e-10)
        u = cfweno_burgers(u, dx, dt)
    assert abs(np.sum(u) * dx - mass0) < 1e-10


# ---- finite values ----------------------------------------------------------

def test_cfweno_burgers_smooth_no_nan():
    """Smooth pre-shock Burgers runs 50 steps without NaN."""
    from solver.schemes import cfweno_burgers
    nx = 80
    x = np.linspace(0, 1, nx, endpoint=False)
    u = 1.0 + 0.2 * np.sin(2.0 * np.pi * x)
    dx = 1.0 / nx
    for _ in range(50):
        max_speed = np.max(np.abs(u))
        dt = 0.4 * dx / max(max_speed, 1e-10)
        u = cfweno_burgers(u, dx, dt)
    assert not np.any(np.isnan(u))
    assert not np.any(np.isinf(u))


def test_cfweno_burgers_finite_error():
    """Pre-shock run produces finite and reasonable error."""
    from solver.schemes import cfweno_burgers
    nx = 80
    x = np.linspace(0, 1, nx, endpoint=False)
    u0 = 1.0 + 0.2 * np.sin(2.0 * np.pi * x)
    u = u0.copy()
    dx = 1.0 / nx
    t = 0.0
    final_time = 0.1
    while t < final_time - 1e-12:
        max_speed = np.max(np.abs(u))
        dt = min(0.4 * dx / max(max_speed, 1e-10), final_time - t)
        u = cfweno_burgers(u, dx, dt)
        t += dt
    # Should be close to IC for short time
    l2 = np.sqrt(np.sum((u - u0)**2) * dx)
    assert l2 < 0.5, f"Error too large for short time: {l2}"


# ---- CFL rejection ----------------------------------------------------------

def test_cfweno_burgers_cfl_exceed_raises():
    """CFL > 1 raises ValueError."""
    from solver.schemes import cfweno_burgers
    u = np.full(50, 3.0)  # large speed
    dx = 0.02
    dt = 1.0  # dt/dx * max|u| = 50 * 3 = 150 >> 1
    with pytest.raises(ValueError, match="CFL"):
        cfweno_burgers(u, dx, dt)


# ---- predictor iterations ---------------------------------------------------

@pytest.mark.parametrize("iters", [0, 1, 2])
def test_cfweno_burgers_predictor_iterations(iters):
    """All predictor iteration counts produce finite results."""
    from solver.schemes import cfweno_burgers
    nx = 50
    x = np.linspace(0, 1, nx, endpoint=False)
    u = 1.0 + 0.2 * np.sin(2.0 * np.pi * x)
    dx = 1.0 / nx
    dt = 0.3 * dx / np.max(np.abs(u))
    result = cfweno_burgers(u, dx, dt, predictor_iterations=iters)
    assert result.shape == u.shape
    assert not np.any(np.isnan(result))


def test_cfweno_burgers_default_predictor():
    """Default predictor_iterations = 1."""
    from solver.schemes import cfweno_burgers
    import inspect
    sig = inspect.signature(cfweno_burgers)
    assert sig.parameters["predictor_iterations"].default == 1


# ---- baseline comparison ----------------------------------------------------

def test_burgers_upwind_shape():
    """Rusanov baseline preserves shape."""
    from solver.schemes import burgers_upwind
    nx = 50
    u = 1.0 + 0.2 * np.sin(2.0 * np.pi * np.linspace(0, 1, nx, endpoint=False))
    dx = 1.0 / nx
    dt = 0.3 * dx / np.max(np.abs(u))
    result = burgers_upwind(u, dx, dt)
    assert result.shape == u.shape


def test_burgers_upwind_mass_conservation():
    """Rusanov baseline conserves mass."""
    from solver.schemes import burgers_upwind
    nx = 50
    x = np.linspace(0, 1, nx, endpoint=False)
    u = 1.0 + 0.2 * np.sin(2.0 * np.pi * x)
    dx = 1.0 / nx
    dt = 0.3 * dx / np.max(np.abs(u))
    result = burgers_upwind(u, dx, dt)
    assert abs(np.sum(result) - np.sum(u)) < 1e-12


# ---- CSV parseability -------------------------------------------------------

def test_burgers_demo_csv_parseable():
    """Generated error_summary.csv is parseable."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "results",
        "cfweno_burgers_demo", "error_summary.csv"
    )
    if not os.path.exists(csv_path):
        pytest.skip("Run make cfweno-burgers-demo first")
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 2
    assert "method" in rows[0]
    assert "l2_error" in rows[0]


# ---- approval checker -------------------------------------------------------

def test_burgers_subset_spec_approved():
    """cfweno_scalar_burgers_subset.md is approved."""
    from pathlib import Path
    import tools.check_scheme_spec_approval as checker
    result = checker.check_spec_approval(
        Path("docs/scheme_specs/cfweno_scalar_burgers_subset.md"))
    assert result["approved"] is True


def test_full_cfweno_spec_not_approved():
    """cfweno_pof_2025.md remains NOT approved."""
    from pathlib import Path
    import tools.check_scheme_spec_approval as checker
    result = checker.check_spec_approval(
        Path("docs/scheme_specs/cfweno_pof_2025.md"))
    assert result["approved"] is False


# ---- predictor sweep CSV parseability ----------------------------------------

def test_predictor_sweep_csv_parseable():
    """Predictor sweep error_summary.csv is parseable."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "results",
        "cfweno_burgers_predictor_sweep", "error_summary.csv"
    )
    if not os.path.exists(csv_path):
        pytest.skip("Run predictor sweep first")
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 3  # at least one row per predictor
    assert "predictor_iterations" in rows[0]
    assert "l2_error" in rows[0]


# ---- CFL sweep CSV parseability ----------------------------------------------

def test_cfl_sweep_csv_parseable():
    """CFL sweep error_summary.csv is parseable."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "results",
        "cfweno_burgers_cfl_sweep", "error_summary.csv"
    )
    if not os.path.exists(csv_path):
        pytest.skip("Run CFL sweep first")
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 3
    assert "cfl" in rows[0]
    assert "l2_error" in rows[0]


# ---- reference sensitivity CSV parseability -----------------------------------

def test_reference_sensitivity_csv_parseable():
    """Reference sensitivity error_summary.csv is parseable."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "results",
        "cfweno_burgers_reference_sensitivity", "error_summary.csv"
    )
    if not os.path.exists(csv_path):
        pytest.skip("Run reference sensitivity first")
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 3
    assert "reference_nx" in rows[0]
    assert "l2_error" in rows[0]


# ---- audit document exists ---------------------------------------------------

def test_audit_document_exists():
    """Formula consistency audit document exists."""
    audit_path = os.path.join(
        os.path.dirname(__file__), "..", "docs", "tasks",
        "cfweno_burgers_prototype", "audit.md"
    )
    assert os.path.exists(audit_path), "Audit document missing"


# ---- predictor convergence order ~2.0 ----------------------------------------

def test_predictor_convergence_order_approx_2():
    """All predictors achieve ~2nd-order convergence (not 3rd)."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "results",
        "cfweno_burgers_predictor_sweep", "error_summary.csv"
    )
    if not os.path.exists(csv_path):
        pytest.skip("Run predictor sweep first")
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    for p in [0, 1, 2]:
        l2_vals = [float(r["l2_error"]) for r in rows
                    if int(r["predictor_iterations"]) == p]
        if len(l2_vals) >= 2:
            order = np.log(l2_vals[-2] / l2_vals[-1]) / np.log(2.0)
            assert 1.5 < order < 2.5, (
                f"Predictor {p}: unexpected order {order:.2f}"
            )
