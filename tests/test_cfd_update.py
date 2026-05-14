"""Tests for conservative update (euler_update)."""

import numpy as np
import pytest

from cfd.constants import GAMMA
from cfd.numerics.update import euler_update
from cfd.boundary.ghost_cells import apply_boundary_conditions
from cfd.variables.conversion import primitive_to_conservative


def test_euler_update_shape():
    """euler_update should not change array shape."""
    ng = 2
    ny, nx = 10, 12
    nxt, nyt = nx + 2 * ng, ny + 2 * ng
    rho = np.ones((nyt, nxt))
    u = np.full((nyt, nxt), 0.5)
    v = np.full((nyt, nxt), 0.3)
    p = np.ones((nyt, nxt))
    U = primitive_to_conservative(rho, u, v, p, GAMMA)
    apply_boundary_conditions(U, ng, bc_x="periodic", bc_y="periodic")
    U_new = euler_update(U, dx=0.1, dy=0.1, dt=0.01, ng=ng)
    assert U_new.shape == (4, nyt, nxt)
