"""Tests for MUSCL reconstruction."""

import numpy as np
import pytest

from cfd.numerics.reconstruction import reconstruct, reconstruct_y
from cfd.variables.conversion import primitive_to_conservative


def _uniform_state(ny=12, nx=14):
    """Create a uniform conservative state."""
    rho = np.full((ny, nx), 1.0)
    u = np.full((ny, nx), 0.5)
    v = np.full((ny, nx), 0.3)
    p = np.full((ny, nx), 1.0)
    return primitive_to_conservative(rho, u, v, p)


def test_muscl_constant_field_remains_constant():
    """MUSCL on a constant field should return constant left/right states."""
    U = _uniform_state()
    ng = 2
    UL, UR = reconstruct(U, ng, method="muscl", limiter_name="minmod")
    np.testing.assert_allclose(UL, U[:, :, :-1], atol=1e-14)
    np.testing.assert_allclose(UR, U[:, :, 1:], atol=1e-14)


def test_muscl_shape():
    """MUSCL x-reconstruction shape."""
    U = _uniform_state()
    UL, UR = reconstruct(U, ng=2, method="muscl", limiter_name="minmod")
    assert UL.shape == (4, 12, 13)
    assert UR.shape == (4, 12, 13)


def test_muscl_y_shape():
    """MUSCL y-reconstruction shape."""
    U = _uniform_state()
    UB, UT = reconstruct_y(U, ng=2, method="muscl", limiter_name="minmod")
    assert UB.shape == (4, 11, 14)
    assert UT.shape == (4, 11, 14)


def test_muscl_smooth_field_no_nan():
    """MUSCL on a smooth varying field should not produce NaN."""
    ny, nx = 20, 24
    rng = np.random.default_rng(42)
    rho = 1.0 + 0.1 * rng.standard_normal((ny, nx))
    rho = np.clip(rho, 0.1, 10.0)
    u = np.full((ny, nx), 1.0)
    v = np.full((ny, nx), 0.5)
    p = np.full((ny, nx), 1.0)
    U = primitive_to_conservative(rho, u, v, p)
    for limiter in ["minmod", "vanleer"]:
        UL, UR = reconstruct(U, 2, method="muscl", limiter_name=limiter)
        assert not np.any(np.isnan(UL)), f"NaN in UL with {limiter}"
        assert not np.any(np.isnan(UR)), f"NaN in UR with {limiter}"
