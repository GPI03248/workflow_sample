"""Primitive variable container.

Responsibilities:
    - Provide a thin wrapper around a raw NumPy array for primitive variables.
    - Primitive ordering: [rho, u, v, p], shape (4, nyt, nxt).

Does NOT:
    - Perform conversions (see conversion.py).
"""

from __future__ import annotations
import numpy as np


class PrimitiveArray:
    """Lightweight container for primitive variables V = [rho, u, v, p].

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
    def u(self) -> np.ndarray:
        return self.data[1]

    @property
    def v(self) -> np.ndarray:
        return self.data[2]

    @property
    def p(self) -> np.ndarray:
        return self.data[3]
