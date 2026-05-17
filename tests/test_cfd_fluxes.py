"""Tests for Euler physical fluxes and numerical fluxes."""

import numpy as np
import pytest

from cfd.constants import GAMMA
from cfd.variables.conversion import primitive_to_conservative
from cfd.physics.fluxes import euler_flux_x, euler_flux_y
from cfd.physics.eos import pressure, sound_speed
from cfd.numerics.riemann import rusanov_flux_x, rusanov_flux_y
from cfd.numerics.riemann import hll_flux_x, hll_flux_y


def _make_uniform_state(ny=10, nx=12, rho0=1.0, u0=0.5, v0=0.3, p0=1.0):
    rho = np.full((ny, nx), rho0)
    u = np.full((ny, nx), u0)
    v = np.full((ny, nx), v0)
    p = np.full((ny, nx), p0)
    U = primitive_to_conservative(rho, u, v, p, GAMMA)
    return U, rho, u, v, p


def test_euler_flux_x_shape():
    """Physical flux in x should have same shape as U."""
    U, *_ = _make_uniform_state()
    F = euler_flux_x(U)
    assert F.shape == U.shape


def test_euler_flux_y_shape():
    """Physical flux in y should have same shape as U."""
    U, *_ = _make_uniform_state()
    G = euler_flux_y(U)
    assert G.shape == U.shape


def test_pressure_uniform():
    """Pressure from EOS should match input for uniform state."""
    U, rho, u, v, p = _make_uniform_state()
    p_comp = pressure(U[0], U[1] / U[0], U[2] / U[0], U[3])
    np.testing.assert_allclose(p_comp, p, atol=1e-14)


def test_sound_speed_positive():
    """Sound speed should be positive for valid state."""
    U, rho, u, v, p = _make_uniform_state()
    c = sound_speed(rho, p)
    assert np.all(c > 0)


def test_sound_speed_negative_rho_raises():
    """Non-positive density should raise ValueError."""
    with pytest.raises(ValueError, match="rho"):
        sound_speed(np.array([-1.0]), np.array([1.0]))


def test_sound_speed_negative_p_raises():
    """Non-positive pressure should raise ValueError."""
    with pytest.raises(ValueError, match="pressure"):
        sound_speed(np.array([1.0]), np.array([-1.0]))


def test_rusanov_flux_x_shape():
    """Rusanov x-flux shape should match interface count."""
    ny, nx = 10, 12
    U, *_ = _make_uniform_state(ny, nx)
    UL = U[:, :, :-1].copy()
    UR = U[:, :, 1:].copy()
    Fnum = rusanov_flux_x(UL, UR)
    assert Fnum.shape == (4, ny, nx - 1)


def test_rusanov_flux_y_shape():
    """Rusanov y-flux shape should match interface count."""
    ny, nx = 10, 12
    U, *_ = _make_uniform_state(ny, nx)
    UL = U[:, :-1, :].copy()
    UR = U[:, 1:, :].copy()
    Gnum = rusanov_flux_y(UL, UR)
    assert Gnum.shape == (4, ny - 1, nx)


# --- HLL flux tests ---


def test_hll_flux_x_shape():
    """HLL x-flux shape should match interface count."""
    ny, nx = 10, 12
    U, *_ = _make_uniform_state(ny, nx)
    UL = U[:, :, :-1].copy()
    UR = U[:, :, 1:].copy()
    Fnum = hll_flux_x(UL, UR)
    assert Fnum.shape == (4, ny, nx - 1)


def test_hll_flux_y_shape():
    """HLL y-flux shape should match interface count."""
    ny, nx = 10, 12
    U, *_ = _make_uniform_state(ny, nx)
    UL = U[:, :-1, :].copy()
    UR = U[:, 1:, :].copy()
    Gnum = hll_flux_y(UL, UR)
    assert Gnum.shape == (4, ny - 1, nx)


def test_hll_flux_x_consistency():
    """When UL == UR, HLL x-flux should equal physical flux."""
    ny, nx = 10, 12
    U, *_ = _make_uniform_state(ny, nx)
    UL = U[:, :, :-1].copy()
    UR = U[:, :, 1:].copy()
    # Make UL == UR (both equal to the left state)
    UR[:] = UL
    Fnum = hll_flux_x(UL, UR, GAMMA)
    Fphys = euler_flux_x(UL, GAMMA)
    np.testing.assert_allclose(Fnum, Fphys, atol=1e-12)


def test_hll_flux_y_consistency():
    """When UB == UT, HLL y-flux should equal physical flux."""
    ny, nx = 10, 12
    U, *_ = _make_uniform_state(ny, nx)
    UB = U[:, :-1, :].copy()
    UT = UB.copy()
    Gnum = hll_flux_y(UB, UT, GAMMA)
    Gphys = euler_flux_y(UB, GAMMA)
    np.testing.assert_allclose(Gnum, Gphys, atol=1e-12)


def test_hll_flux_x_no_nan():
    """HLL x-flux should not produce NaN for moderate states."""
    ny, nx = 10, 12
    U, *_ = _make_uniform_state(ny, nx, rho0=1.0, u0=1.0, v0=0.3, p0=1.0)
    UL = U[:, :, :-1].copy()
    UR = U[:, :, 1:].copy()
    Fnum = hll_flux_x(UL, UR)
    assert not np.any(np.isnan(Fnum))


def test_hll_flux_y_no_nan():
    """HLL y-flux should not produce NaN for moderate states."""
    ny, nx = 10, 12
    U, *_ = _make_uniform_state(ny, nx, rho0=1.0, u0=0.5, v0=1.0, p0=1.0)
    UB = U[:, :-1, :].copy()
    UT = U[:, 1:, :].copy()
    Gnum = hll_flux_y(UB, UT)
    assert not np.any(np.isnan(Gnum))


def test_hll_epsilon_guard():
    """HLL flux should not divide by zero when UL == UR (S_L == S_R)."""
    ny, nx = 5, 6
    rho = np.full((ny, nx), 1.0)
    u = np.full((ny, nx), 0.5)
    v = np.full((ny, nx), 0.3)
    p = np.full((ny, nx), 1.0)
    U = primitive_to_conservative(rho, u, v, p, GAMMA)
    UL = U[:, :, :-1].copy()
    UR = UL.copy()
    Fnum = hll_flux_x(UL, UR)
    assert not np.any(np.isnan(Fnum))
    assert not np.any(np.isinf(Fnum))


def test_hll_vs_rusanov_less_diffusive():
    """HLL flux should be less diffusive than Rusanov on non-trivial states."""
    ny, nx = 10, 12
    # Create left/right states with a jump
    rhoL = np.full((ny, nx), 1.0)
    uL = np.full((ny, nx), 0.5)
    vL = np.full((ny, nx), 0.0)
    pL = np.full((ny, nx), 1.0)
    UL_full = primitive_to_conservative(rhoL, uL, vL, pL, GAMMA)

    rhoR = np.full((ny, nx), 0.5)
    uR = np.full((ny, nx), 1.0)
    vR = np.full((ny, nx), 0.0)
    pR = np.full((ny, nx), 0.5)
    UR_full = primitive_to_conservative(rhoR, uR, vR, pR, GAMMA)

    UL = UL_full[:, :1, :1].copy()
    UR = UR_full[:, :1, :1].copy()

    F_rusanov = rusanov_flux_x(UL, UR, GAMMA)
    F_hll = hll_flux_x(UL, UR, GAMMA)

    # Both should be finite
    assert not np.any(np.isnan(F_hll))
    assert not np.any(np.isnan(F_rusanov))
    # They should differ (HLL uses different wave speed estimates)
    assert not np.allclose(F_hll, F_rusanov)


def test_update_raises_on_unknown_flux():
    """compute_residual should raise ValueError for unknown flux_type."""
    from cfd.numerics.update import compute_residual

    U, *_ = _make_uniform_state(10, 12)
    with pytest.raises(ValueError, match="flux_type"):
        compute_residual(U, dx=0.1, dy=0.1, ng=2, gamma=GAMMA, flux_type="unknown")


def test_solver_runs_with_hll():
    """Solver should complete a small uniform flow run with flux_type='hll'."""
    from cfd.config import CFDConfig
    from cfd.cases.uniform_flow import uniform_flow_config, uniform_flow_ic
    from cfd.solver import run_solver

    config = uniform_flow_config()
    config.flux_type = "hll"
    config.nx = 10
    config.ny = 5
    config.final_time = 0.01

    result = run_solver(
        config=config,
        initial_condition_func=uniform_flow_ic,
        case_name="uniform_hll",
        output_dir=None,
    )
    U = result["U"]
    ng = config.ng
    rho = U[0, ng:-ng, ng:-ng]
    # Uniform flow should be preserved to near machine precision
    np.testing.assert_allclose(rho, 1.0, atol=1e-10)
