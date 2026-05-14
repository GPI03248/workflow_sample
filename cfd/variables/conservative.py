"""Conservative variable container.

Responsibilities:
    - Thin wrapper for conservative variables U = [rho, rho*u, rho*v, E].
    - Shape (4, nyt, nxt).

Does NOT:
    - Perform conversions (see conversion.py).
"""

from __future__ import annotations
import numpy as np


class ConservativeArray:
    """Lightweight container for conservative variables U = [rho, rho*u, rho*v, E].

    Attributes
    ----------
    data : np.ndarray, shape (4, nyt, nxt)
    """

    def __init__(self, data: np.ndarray) -> None:
        assert data.ndim == 3 and data.shape[0] == 4
        self.data = data

    @property
    def rho(self) -> np.ndarray:
        return self.data[0]

    @property
    def rho_u(self) -> np.ndarray:
        return self.data[1]

    @property
    def rho_v(self) -> np.ndarray:
        return self.data[2]

    @property
    def E(self) -> np.ndarray:
        return self.data[3]
