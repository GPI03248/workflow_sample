"""Basic correctness tests for the upwind scheme."""

import numpy as np
import pytest

from solver.grid import gaussian_ic, make_grid
from solver.schemes import step


def test_upwind_preserves_shape():
    """Upwind step must return an array with the same shape."""
    u = np.ones(100)
    result = step(u, cfl=0.5, scheme="upwind")
    assert result.shape == u.shape


def test_upwind_uniform_remains_uniform():
    """A uniform field should stay uniform (constant advection)."""
    u = np.full(50, 3.14)
    result = step(u, cfl=0.8, scheme="upwind")
    np.testing.assert_allclose(result, 3.14)


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


def test_unknown_scheme_raises():
    """Requesting an unregistered scheme must raise ValueError."""
    with pytest.raises(ValueError, match="Unknown scheme"):
        step(np.ones(10), cfl=0.5, scheme="nonexistent")
