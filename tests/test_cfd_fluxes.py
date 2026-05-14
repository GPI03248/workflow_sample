"""Tests for Euler physical fluxes and numerical fluxes."""

import numpy as np
import pytest

from cfd.constants import GAMMA
from cfd.variables.conversion import primitive_to_conservative
from cfd.physics.fluxes import euler_flux_x, euler_flux_y
from cfd.physics.eos import pressure, sound_speed
from cfd.numerics.riemann import rusanov_flux_x, rusanov_flux_y


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
