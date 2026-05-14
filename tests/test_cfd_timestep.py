"""Tests for CFL time-step computation."""

import numpy as np
import pytest

from cfd.numerics.timestep import compute_dt
from cfd.variables.conversion import primitive_to_conservative


def test_dt_positive():
    """CFL dt should be positive for a valid state."""
    rho = np.ones((10, 12))
    u = np.full((10, 12), 1.0)
    v = np.full((10, 12), 0.5)
    p = np.ones((10, 12))
    U = primitive_to_conservative(rho, u, v, p)
    dt = compute_dt(U, dx=0.01, dy=0.01, cfl=0.5)
    assert dt > 0


def test_dt_scales_with_cfl():
    """dt should scale linearly with CFL number."""
    rho = np.ones((10, 12))
    u = np.full((10, 12), 1.0)
    v = np.zeros((10, 12))
    p = np.ones((10, 12))
    U = primitive_to_conservative(rho, u, v, p)
    dt1 = compute_dt(U, dx=0.01, dy=0.01, cfl=0.3)
    dt2 = compute_dt(U, dx=0.01, dy=0.01, cfl=0.6)
    np.testing.assert_allclose(dt2 / dt1, 2.0, rtol=1e-10)
