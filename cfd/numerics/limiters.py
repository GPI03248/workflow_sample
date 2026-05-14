"""Slope limiters for high-order reconstruction.

Responsibilities:
    - Provide limiter functions for MUSCL-type reconstruction.
    - All limiters take two slope arrays (a, b) and return limited slopes.

Does NOT:
    - Perform reconstruction itself (see reconstruction.py).
"""

from __future__ import annotations
import numpy as np


def minmod(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Minmod limiter: returns the smaller slope in magnitude if signs agree, else 0."""
    return np.where(
        a * b > 0,
        np.where(np.abs(a) < np.abs(b), a, b),
        0.0,
    )


def van_leer(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """van Leer limiter: (a*b)(a+b) / (a^2 + b^2) when a*b > 0, else 0.

    Avoids division by zero by adding a small epsilon to denominator.
    """
    product = a * b
    denom = a**2 + b**2 + 1e-30
    return np.where(product > 0, 2.0 * product / denom * (a + b) / (np.abs(a) + np.abs(b) + 1e-30), 0.0)


# Limiter registry
LIMITERS = {
    "minmod": minmod,
    "vanleer": van_leer,
}


def get_limiter(name: str):
    """Return limiter function by name."""
    if name not in LIMITERS:
        raise ValueError(f"Unknown limiter '{name}'. Available: {sorted(LIMITERS)}")
    return LIMITERS[name]
