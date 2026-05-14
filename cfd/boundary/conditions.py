"""Individual boundary condition implementations.

Each function operates on the full conservative array U with shape (4, nyt, nxt).

Responsibilities:
    - Fill ghost cells according to the specified boundary type.

Does NOT:
    - Decide which boundary to apply (see ghost_cells.py).
"""

from __future__ import annotations
import numpy as np


def periodic_x(U: np.ndarray, ng: int) -> None:
    """Periodic boundary in x: wrap around."""
    U[:, :, :ng] = U[:, :, -2 * ng:-ng]
    U[:, :, -ng:] = U[:, :, ng:2 * ng]


def periodic_y(U: np.ndarray, ng: int) -> None:
    """Periodic boundary in y: wrap around."""
    U[:, :ng, :] = U[:, -2 * ng:-ng, :]
    U[:, -ng:, :] = U[:, ng:2 * ng, :]


def transmissive_x(U: np.ndarray, ng: int) -> None:
    """Transmissive (outflow / zero-gradient) in x."""
    for i in range(ng):
        U[:, :, i] = U[:, :, ng]
        U[:, :, -(i + 1)] = U[:, :, -(ng + 1)]


def transmissive_y(U: np.ndarray, ng: int) -> None:
    """Transmissive (outflow / zero-gradient) in y."""
    for i in range(ng):
        U[:, i, :] = U[:, ng, :]
        U[:, -(i + 1), :] = U[:, -(ng + 1), :]


def reflective_x(U: np.ndarray, ng: int) -> None:
    """Reflective wall in x: normal velocity (u) is negated."""
    for i in range(ng):
        U[:, :, i] = U[:, :, 2 * ng - 1 - i]
        U[:, :, -(i + 1)] = U[:, :, -(2 * ng - i)]
        # Negate x-momentum in ghost cells.
        U[1, :, i] = -U[1, :, i]
        U[1, :, -(i + 1)] = -U[1, :, -(i + 1)]


def reflective_y(U: np.ndarray, ng: int) -> None:
    """Reflective wall in y: normal velocity (v) is negated."""
    for i in range(ng):
        U[:, i, :] = U[:, 2 * ng - 1 - i, :]
        U[:, -(i + 1), :] = U[:, -(2 * ng - i), :]
        # Negate y-momentum in ghost cells.
        U[2, i, :] = -U[2, i, :]
        U[2, -(i + 1), :] = -U[2, -(i + 1), :]
