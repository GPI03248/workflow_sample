"""Tests for boundary conditions."""

import numpy as np
import pytest

from cfd.boundary.ghost_cells import apply_boundary_conditions
from cfd.variables.conversion import primitive_to_conservative


def _make_state(ny=10, nx=12, ng=2):
    """Create a simple state array with distinct interior values."""
    nxt = nx + 2 * ng
    nyt = ny + 2 * ng
    rho = np.ones((nyt, nxt)) * 2.0
    u = np.ones((nyt, nxt)) * 0.5
    v = np.ones((nyt, nxt)) * 0.3
    p = np.ones((nyt, nxt)) * 1.0
    # Make interior cells distinct.
    rng = np.random.default_rng(123)
    rho[ng:-ng, ng:-ng] = rng.uniform(0.5, 3.0, (ny, nx))
    return primitive_to_conservative(rho, u, v, p), ng


def test_periodic_bc_copies_interior():
    """Periodic BC should fill ghosts from opposite side."""
    U, ng = _make_state()
    apply_boundary_conditions(U, ng, bc_x="periodic", bc_y="periodic")
    # Check x-periodic: left ghost == right interior edge
    np.testing.assert_allclose(U[:, :, :ng], U[:, :, -2 * ng:-ng])
    np.testing.assert_allclose(U[:, :, -ng:], U[:, :, ng:2 * ng])


def test_transmissive_bc_constant():
    """Transmissive BC should copy nearest interior to ghosts."""
    U, ng = _make_state()
    apply_boundary_conditions(U, ng, bc_x="transmissive", bc_y="transmissive")
    for i in range(ng):
        np.testing.assert_allclose(U[:, :, i], U[:, :, ng])
        np.testing.assert_allclose(U[:, :, -(i + 1)], U[:, :, -(ng + 1)])


def test_reflective_bc_negates_momentum():
    """Reflective BC in x should negate x-momentum in ghost cells."""
    U, ng = _make_state()
    apply_boundary_conditions(U, ng, bc_x="reflective", bc_y="periodic")
    # Check that ghost cells have x-momentum opposite sign to their mirror interior cells.
    for i in range(ng):
        mirror_i = 2 * ng - 1 - i
        np.testing.assert_allclose(U[1, :, i], -U[1, :, mirror_i], atol=1e-14)
        mirror_j = -(2 * ng - i)
        np.testing.assert_allclose(U[1, :, -(i + 1)], -U[1, :, mirror_j], atol=1e-14)


def test_unknown_bc_raises():
    """Unknown boundary type should raise ValueError."""
    U, ng = _make_state()
    with pytest.raises(ValueError, match="Unknown"):
        apply_boundary_conditions(U, ng, bc_x="invalid", bc_y="transmissive")
