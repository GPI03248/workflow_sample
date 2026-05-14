"""Tests for the isentropic vortex analytic validation case."""

import numpy as np
import pytest

from cfd.cases.isentropic_vortex import (
    IsentropicVortexParams,
    isentropic_vortex_conservative,
    isentropic_vortex_exact_solution,
    isentropic_vortex_ic,
    isentropic_vortex_primitive,
)
from cfd.mesh.structured import StructuredMesh2D


def _mesh(nx=20, ny=20):
    return StructuredMesh2D(nx=nx, ny=ny, xmin=0, xmax=10, ymin=0, ymax=10, ng=2)


def test_vortex_primitive_shape():
    mesh = _mesh()
    X, Y = mesh.cell_centers_2d()
    V = isentropic_vortex_primitive(X, Y, t=0.0)
    assert V.shape == (4, mesh.nyt, mesh.nxt)


def test_vortex_conservative_shape():
    mesh = _mesh()
    X, Y = mesh.cell_centers_2d()
    U = isentropic_vortex_conservative(X, Y, t=0.0)
    assert U.shape == (4, mesh.nyt, mesh.nxt)


def test_vortex_rho_positive():
    mesh = _mesh(40, 40)
    X, Y = mesh.cell_centers_2d()
    for t in [0.0, 0.5, 1.0]:
        V = isentropic_vortex_primitive(X, Y, t=t)
        assert np.all(V[0] > 0), f"rho <= 0 at t={t}"


def test_vortex_p_positive():
    mesh = _mesh(40, 40)
    X, Y = mesh.cell_centers_2d()
    V = isentropic_vortex_primitive(X, Y, t=0.0)
    assert np.all(V[3] > 0)


def test_vortex_exact_at_t0():
    mesh = _mesh(10, 10)
    U_exact = isentropic_vortex_exact_solution(mesh, t=0.0)
    U_ic = isentropic_vortex_ic(mesh.nxt, mesh.nyt)
    np.testing.assert_allclose(U_exact, U_ic, atol=1e-12)


def test_vortex_ic_shape():
    mesh = _mesh(10, 10)
    U = isentropic_vortex_ic(mesh.nxt, mesh.nyt)
    assert U.shape == (4, mesh.nyt, mesh.nxt)


def test_vortex_runs_small_grid():
    """Run solver on small grid to final_time."""
    from cfd.config import CFDConfig
    from cfd.numerics.time_integration import advance
    params = IsentropicVortexParams()
    config = CFDConfig(
        nx=8, ny=8, xmin=0, xmax=10, ymin=0, ymax=10,
        gamma=1.4, cfl=0.4, ng=2, final_time=0.1,
        bc_x="periodic", bc_y="periodic",
        flux_type="rusanov", reconstruction="piecewise_constant",
        limiter="minmod", time_integrator="euler",
    )
    mesh = StructuredMesh2D(nx=8, ny=8, xmin=0, xmax=10, ymin=0, ymax=10, ng=2)
    U = isentropic_vortex_ic(mesh.nxt, mesh.nyt, 1.4, params)
    sim = advance(U, dx=mesh.dx, dy=mesh.dy, ng=2, cfl=0.4,
                  final_time=0.1, bc_x="periodic", bc_y="periodic",
                  gamma=1.4, flux_type="rusanov",
                  reconstruction="piecewise_constant", limiter="minmod",
                  time_integrator="euler")
    assert sim["n_steps"] > 0
