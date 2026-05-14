"""2D uniform Cartesian structured mesh (cell-centered).

Responsibilities:
    - Define cell centres, cell sizes, ghost-cell layout.
    - Provide index helpers for interior vs ghost regions.

Does NOT:
    - Store solution data (that lives in the solver).
"""

from __future__ import annotations
from dataclasses import dataclass

import numpy as np


@dataclass
class StructuredMesh2D:
    """Uniform Cartesian mesh with ghost cells.

    Parameters
    ----------
    nx, ny : int
        Interior cell counts.
    xmin, xmax, ymin, ymax : float
        Domain extents.
    ng : int
        Number of ghost-cell layers on each side.

    Attributes
    ----------
    dx, dy : float
        Cell sizes.
    x, y : np.ndarray
        1-D arrays of cell-centre coordinates (including ghosts), shape
        (nx + 2*ng,) and (ny + 2*ng,).
    nxt, nyt : int
        Total cell counts including ghosts.
    """

    nx: int
    ny: int
    xmin: float = 0.0
    xmax: float = 1.0
    ymin: float = 0.0
    ymax: float = 1.0
    ng: int = 2

    def __post_init__(self) -> None:
        self.nxt = self.nx + 2 * self.ng
        self.nyt = self.ny + 2 * self.ng
        self.dx = (self.xmax - self.xmin) / self.nx
        self.dy = (self.ymax - self.ymin) / self.ny
        # Cell-centre coordinates including ghost cells.
        self.x = np.linspace(
            self.xmin - (self.ng - 0.5) * self.dx,
            self.xmax + (self.ng - 0.5) * self.dx,
            self.nxt,
        )
        self.y = np.linspace(
            self.ymin - (self.ng - 0.5) * self.dy,
            self.ymax + (self.ng - 0.5) * self.dy,
            self.nyt,
        )

    @property
    def interior_slice(self) -> tuple[slice, slice]:
        """Slice for interior cells: (ng:-ng, ng:-ng)."""
        ng = self.ng
        return (slice(ng, -ng), slice(ng, -ng))

    def cell_centers_2d(self) -> tuple[np.ndarray, np.ndarray]:
        """Return 2-D arrays (X, Y) of cell centres, shape (nyt, nxt)."""
        return np.meshgrid(self.x, self.y)
