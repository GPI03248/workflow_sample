"""Tests for SSP RK2 time integration."""

import numpy as np
import pytest

from cfd.config import CFDConfig
from cfd.cases.uniform_flow import uniform_flow_ic
from cfd.cases.entropy_wave import EntropyWaveParams, entropy_wave_ic
from cfd.mesh.structured import StructuredMesh2D
from cfd.numerics.time_integration import advance


def test_ssp_rk2_uniform_flow():
    """Uniform flow should be preserved under SSP RK2."""
    config = CFDConfig(
        nx=20, ny=20, xmin=0, xmax=1, ymin=0, ymax=1,
        gamma=1.4, cfl=0.4, ng=2, final_time=0.05,
        bc_x="periodic", bc_y="periodic",
        flux_type="rusanov", reconstruction="piecewise_constant",
        limiter="minmod", time_integrator="ssp_rk2",
    )
    mesh = StructuredMesh2D(nx=20, ny=20, xmin=0, xmax=1, ymin=0, ymax=1, ng=2)
    U = uniform_flow_ic(mesh.nxt, mesh.nyt)
    sim = advance(U, dx=mesh.dx, dy=mesh.dy, ng=2, cfl=0.4,
                  final_time=0.05, bc_x="periodic", bc_y="periodic",
                  gamma=1.4, flux_type="rusanov",
                  reconstruction="piecewise_constant", limiter="minmod",
                  time_integrator="ssp_rk2")
    ng = 2
    U_int = sim["U"][:, ng:-ng, ng:-ng]
    assert np.max(np.abs(U_int[0] - 1.0)) < 1e-10


def test_ssp_rk2_entropy_wave_runs():
    """Entropy wave should run to completion with SSP RK2."""
    params = EntropyWaveParams()
    config = CFDConfig(
        nx=16, ny=16, xmin=0, xmax=1, ymin=0, ymax=1,
        gamma=1.4, cfl=0.4, ng=2, final_time=0.05,
        bc_x="periodic", bc_y="periodic",
        flux_type="rusanov", reconstruction="piecewise_constant",
        limiter="minmod", time_integrator="ssp_rk2",
    )
    mesh = StructuredMesh2D(nx=16, ny=16, xmin=0, xmax=1, ymin=0, ymax=1, ng=2)
    U = entropy_wave_ic(mesh.nxt, mesh.nyt, 1.4, params)
    sim = advance(U, dx=mesh.dx, dy=mesh.dy, ng=2, cfl=0.4,
                  final_time=0.05, bc_x="periodic", bc_y="periodic",
                  gamma=1.4, flux_type="rusanov",
                  reconstruction="piecewise_constant", limiter="minmod",
                  time_integrator="ssp_rk2")
    assert sim["n_steps"] > 0


def test_unknown_time_integrator_raises():
    mesh = StructuredMesh2D(nx=8, ny=8, xmin=0, xmax=1, ymin=0, ymax=1, ng=2)
    U = uniform_flow_ic(mesh.nxt, mesh.nyt)
    with pytest.raises(ValueError, match="Unknown time integrator"):
        advance(U, dx=mesh.dx, dy=mesh.dy, ng=2, cfl=0.4,
                final_time=0.01, bc_x="periodic", bc_y="periodic",
                gamma=1.4, time_integrator="rk5")
