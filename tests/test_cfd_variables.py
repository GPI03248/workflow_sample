"""Tests for primitive / conservative variable conversion."""

import numpy as np
import pytest

from cfd.constants import GAMMA
from cfd.variables.conversion import primitive_to_conservative, conservative_to_primitive


def test_roundtrip_uniform():
    """Primitive -> Conservative -> Primitive should be identity."""
    ny, nx = 10, 12
    rho = np.full((ny, nx), 1.2)
    u = np.full((ny, nx), 0.8)
    v = np.full((ny, nx), -0.3)
    p = np.full((ny, nx), 1.5)

    U = primitive_to_conservative(rho, u, v, p, GAMMA)
    rho2, u2, v2, p2 = conservative_to_primitive(U, GAMMA)

    np.testing.assert_allclose(rho2, rho, atol=1e-14)
    np.testing.assert_allclose(u2, u, atol=1e-14)
    np.testing.assert_allclose(v2, v, atol=1e-14)
    np.testing.assert_allclose(p2, p, atol=1e-14)


def test_roundtrip_random():
    """Round-trip with random positive values."""
    rng = np.random.default_rng(42)
    ny, nx = 20, 25
    rho = rng.uniform(0.5, 2.0, (ny, nx))
    u = rng.uniform(-1, 1, (ny, nx))
    v = rng.uniform(-1, 1, (ny, nx))
    p = rng.uniform(0.5, 3.0, (ny, nx))

    U = primitive_to_conservative(rho, u, v, p, GAMMA)
    rho2, u2, v2, p2 = conservative_to_primitive(U, GAMMA)

    np.testing.assert_allclose(rho2, rho, rtol=1e-12)
    np.testing.assert_allclose(u2, u, rtol=1e-12)
    np.testing.assert_allclose(v2, v, rtol=1e-12)
    np.testing.assert_allclose(p2, p, rtol=1e-12)


def test_conservative_shape():
    """Conservative array should have shape (4, ny, nx)."""
    ny, nx = 5, 8
    rho = np.ones((ny, nx))
    u = np.zeros((ny, nx))
    v = np.zeros((ny, nx))
    p = np.ones((ny, nx))
    U = primitive_to_conservative(rho, u, v, p)
    assert U.shape == (4, ny, nx)
