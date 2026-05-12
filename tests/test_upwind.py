"""Correctness tests for upwind and lax_wendroff schemes."""

import numpy as np
import pytest

from solver.grid import gaussian_ic, make_grid
from solver.simulate import exact_solution, initial_condition, run_advection
from solver.schemes import step


# ---- shape preservation ---------------------------------------------------

def test_upwind_preserves_shape():
    """Upwind step must return an array with the same shape."""
    u = np.ones(100)
    result = step(u, cfl=0.5, scheme="upwind")
    assert result.shape == u.shape


def test_lax_wendroff_preserves_shape():
    """Lax-Wendroff step must return an array with the same shape."""
    u = np.ones(100)
    result = step(u, cfl=0.5, scheme="lax_wendroff")
    assert result.shape == u.shape


# ---- uniform field invariance ---------------------------------------------

def test_upwind_uniform_remains_uniform():
    """A uniform field should stay uniform (constant advection)."""
    u = np.full(50, 3.14)
    result = step(u, cfl=0.8, scheme="upwind")
    np.testing.assert_allclose(result, 3.14)


def test_lax_wendroff_uniform_remains_uniform():
    """A uniform field should stay uniform with Lax-Wendroff."""
    u = np.full(50, 3.14)
    result = step(u, cfl=0.8, scheme="lax_wendroff")
    np.testing.assert_allclose(result, 3.14)


# ---- smooth transport (existing upwind test) ------------------------------

def test_upwind_smooth_transport():
    """After one full period the Gaussian should be approximately back
    (diffused due to first-order dissipation)."""
    n = 400
    cfl = 0.8
    centers, dx = make_grid(n, length=1.0)
    u = gaussian_ic(centers, x0=0.25, sigma=0.05)

    # One period: t_final = L / a = 1.0
    n_steps = int(round(1.0 / (cfl * dx)))
    for _ in range(n_steps):
        u = step(u, cfl, scheme="upwind")

    # Peak should be near x=0.25 again, but diffused.
    peak_idx = np.argmax(u)
    assert abs(centers[peak_idx] - 0.25) < 0.05


# ---- error handling -------------------------------------------------------

def test_unknown_scheme_raises():
    """Requesting an unregistered scheme must raise ValueError."""
    with pytest.raises(ValueError, match="Unknown scheme"):
        step(np.ones(10), cfl=0.5, scheme="nonexistent")


def test_unstable_cfl_raises():
    """CFL outside [0, 1] must raise ValueError."""
    with pytest.raises(ValueError, match="CFL must satisfy"):
        step(np.ones(10), cfl=1.5, scheme="upwind")


def test_negative_cfl_raises():
    """Negative CFL must raise ValueError."""
    with pytest.raises(ValueError, match="CFL must satisfy"):
        step(np.ones(10), cfl=-0.1, scheme="upwind")


# ---- analytic solution ----------------------------------------------------

def test_exact_solution_at_t0():
    """At t=0, exact_solution must equal initial_condition."""
    x, _ = make_grid(100)
    np.testing.assert_allclose(
        exact_solution(x, t=0.0),
        initial_condition(x),
    )


# ---- run_advection consistency --------------------------------------------

def test_run_advection_shapes():
    """run_advection returns arrays of consistent shapes."""
    res = run_advection("upwind", nx=50, cfl=0.5, final_time=0.1)
    n = 50
    assert res["u_num"].shape == (n,)
    assert res["u_exact"].shape == (n,)
    assert res["u0"].shape == (n,)
    assert res["x"].shape == (n,)
