"""Slope limiters for high-order reconstruction.

Responsibilities:
    - Provide limiter functions (minmod, etc.) for MUSCL-type reconstruction.
    - Currently NOT connected to the main solver loop — reserved for future use.

Does NOT:
    - Perform reconstruction itself (see reconstruction.py).

Extension notes:
    To use in MUSCL, compute slopes and limit them with one of these functions
    before passing to the reconstruction step.
"""

from __future__ import annotations
import numpy as np


def minmod(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Minmod limiter: returns the smaller slope in magnitude if signs agree, else 0.

    Parameters
    ----------
    a, b : np.ndarray
        Slope estimates (same shape).

    Returns
    -------
    np.ndarray
        Limited slopes.
    """
    result = np.where(
        a * b > 0,
        np.where(np.abs(a) < np.abs(b), a, b),
        0.0,
    )
    return result


def _superbee(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Superbee limiter (reserved, not yet used in solver)."""
    s1 = minmod(a, 2 * b)
    s2 = minmod(2 * a, b)
    return np.where(np.abs(s1) > np.abs(s2), s1, s2)
