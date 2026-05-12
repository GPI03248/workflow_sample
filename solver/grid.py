"""Uniform 1D grid utilities."""

import numpy as np


def make_grid(n: int, length: float = 1.0) -> tuple[np.ndarray, float]:
    """Return (cell_centers, dx) for a uniform 1D grid with *n* cells."""
    dx = length / n
    centers = np.linspace(dx / 2, length - dx / 2, n)
    return centers, dx


def gaussian_ic(centers: np.ndarray, x0: float = 0.25, sigma: float = 0.05) -> np.ndarray:
    """Gaussian initial condition centred at *x0*."""
    return np.exp(-0.5 * ((centers - x0) / sigma) ** 2)
