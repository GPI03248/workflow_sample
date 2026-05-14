"""High-level ghost-cell application.

Responsibilities:
    - Dispatch to the correct boundary condition functions based on config.

Does NOT:
    - Implement individual BC logic (see conditions.py).
"""

from __future__ import annotations
import numpy as np

from .conditions import periodic_x, periodic_y, transmissive_x, transmissive_y, reflective_x, reflective_y

_BC_DISPATCH = {
    "periodic": (periodic_x, periodic_y),
    "transmissive": (transmissive_x, transmissive_y),
    "reflective": (reflective_x, reflective_y),
}


def apply_boundary_conditions(
    U: np.ndarray,
    ng: int,
    bc_x: str = "transmissive",
    bc_y: str = "transmissive",
) -> None:
    """Apply boundary conditions to ghost cells (in-place).

    Parameters
    ----------
    U : np.ndarray, shape (4, nyt, nxt)
        Conservative variables (modified in-place).
    ng : int
        Number of ghost-cell layers.
    bc_x, bc_y : str
        One of "periodic", "transmissive", "reflective".
    """
    bc_x_lower = bc_x.lower()
    bc_y_lower = bc_y.lower()

    if bc_x_lower not in _BC_DISPATCH:
        raise ValueError(f"Unknown x boundary type: {bc_x}")
    if bc_y_lower not in _BC_DISPATCH:
        raise ValueError(f"Unknown y boundary type: {bc_y}")

    _BC_DISPATCH[bc_x_lower][0](U, ng)
    _BC_DISPATCH[bc_y_lower][1](U, ng)
