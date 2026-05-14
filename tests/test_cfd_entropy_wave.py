"""Tests for the entropy wave analytic validation case."""

import numpy as np
import pytest

from cfd.cases.entropy_wave import (
    EntropyWaveParams,
    entropy_wave_conservative,
    entropy_wave_exact_solution,
    entropy_wave_ic,
    entropy_wave_primitive,
)
from cfd.mesh.structured import StructuredMesh2D


def _make_mesh(nx=10, ny=10):
    return StructuredMesh2D(nx=nx, ny=ny, xmin=0.0, xmax=1.0, ymin=0.0, ymax=1.0, ng=2)


def test_entropy_wave_primitive_shape():
    """Primitive solution shape should be (4, nyt, nxt)."""
    mesh = _make_mesh(10, 10)
    X, Y = mesh.cell_centers_2d()
    V = entropy_wave_primitive(X, Y, t=0.0)
    assert V.shape == (4, mesh.nyt, mesh.nxt)


def test_entropy_wave_conservative_shape():
    """Conservative solution shape should be (4, nyt, nxt)."""
    mesh = _make_mesh(10, 10)
    X, Y = mesh.cell_centers_2d()
    U = entropy_wave_conservative(X, Y, t=0.0)
    assert U.shape == (4, mesh.nyt, mesh.nxt)


def test_entropy_wave_exact_at_t0():
    """Exact solution at t=0 should match initial condition."""
    mesh = _make_mesh(10, 10)
    U_exact = entropy_wave_exact_solution(mesh, t=0.0)
    U_ic = entropy_wave_ic(mesh.nxt, mesh.nyt)
    np.testing.assert_allclose(U_exact, U_ic, atol=1e-14)


def test_entropy_wave_rho_positive():
    """Density should always be positive (rho0 - eps > 0)."""
    mesh = _make_mesh(20, 20)
    X, Y = mesh.cell_centers_2d()
    params = EntropyWaveParams()
    V = entropy_wave_primitive(X, Y, t=0.0, params=params)
    assert np.all(V[0] > 0)
    # Also check at a later time.
    V2 = entropy_wave_primitive(X, Y, t=0.5, params=params)
    assert np.all(V2[0] > 0)


def test_entropy_wave_p_positive():
    """Pressure should always be positive (constant p0 > 0)."""
    mesh = _make_mesh(20, 20)
    V = entropy_wave_primitive(*mesh.cell_centers_2d(), t=0.0)
    assert np.all(V[3] > 0)


def test_entropy_wave_periodic_consistency():
    """After one full period, the solution should return to the initial state."""
    mesh = _make_mesh(20, 20)
    X, Y = mesh.cell_centers_2d()
    params = EntropyWaveParams()
    V0 = entropy_wave_primitive(X, Y, t=0.0, params=params)
    # One period in x: T = 1/u0 = 1.0; but also needs y period T = 1/v0 = 2.0.
    # Use LCM: at t=1.0, x has done 1 period, y has done 0.5 period.
    # At t=2.0 both have completed integer periods.
    V_period = entropy_wave_primitive(X, Y, t=2.0, params=params)
    np.testing.assert_allclose(V0[0], V_period[0], atol=1e-14)


def test_entropy_wave_ic_compatible_with_solver():
    """IC function should produce valid array matching solver expectations."""
    mesh = _make_mesh(10, 10)
    U = entropy_wave_ic(mesh.nxt, mesh.nyt)
    assert U.shape == (4, mesh.nyt, mesh.nxt)
    # Density should be positive.
    assert np.all(U[0] > 0)


def test_run_entropy_wave_small_grid():
    """Run entropy wave solver on a small grid to final_time."""
    from cfd.config import CFDConfig
    from cfd.numerics.time_integration import advance

    params = EntropyWaveParams()
    config = CFDConfig(
        nx=8, ny=8, xmin=0.0, xmax=1.0, ymin=0.0, ymax=1.0,
        gamma=1.4, cfl=0.4, ng=2, final_time=0.05,
        bc_x="periodic", bc_y="periodic",
        flux_type="rusanov", reconstruction="piecewise_constant",
        time_integrator="euler",
    )
    mesh = StructuredMesh2D(
        nx=config.nx, ny=config.ny,
        xmin=0.0, xmax=1.0, ymin=0.0, ymax=1.0,
        ng=config.ng,
    )
    U = entropy_wave_ic(mesh.nxt, mesh.nyt, config.gamma, params)
    sim = advance(
        U, dx=mesh.dx, dy=mesh.dy, ng=config.ng, cfl=config.cfl,
        final_time=config.final_time,
        bc_x="periodic", bc_y="periodic",
        gamma=config.gamma, flux_type="rusanov",
        reconstruction="piecewise_constant", time_integrator="euler",
    )
    assert sim["n_steps"] > 0
    # Numerical and exact should have same shape.
    ng = config.ng
    U_num = sim["U"][:, ng:-ng, ng:-ng]
    U_ex = entropy_wave_exact_solution(mesh, sim["actual_final_time"], params)
    U_ex_int = U_ex[:, ng:-ng, ng:-ng]
    assert U_num.shape == U_ex_int.shape
