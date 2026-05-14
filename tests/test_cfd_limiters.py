"""Tests for slope limiters."""

import numpy as np
import pytest

from cfd.numerics.limiters import minmod, van_leer, get_limiter


def test_minmod_same_sign_returns_smaller():
    a = np.array([1.0, 2.0, -3.0, -1.0])
    b = np.array([2.0, 1.0, -1.0, -3.0])
    result = minmod(a, b)
    np.testing.assert_allclose(result, [1.0, 1.0, -1.0, -1.0])


def test_minmod_opposite_sign_returns_zero():
    a = np.array([1.0, -1.0, 2.0])
    b = np.array([-1.0, 1.0, -3.0])
    result = minmod(a, b)
    np.testing.assert_allclose(result, [0.0, 0.0, 0.0])


def test_van_leer_no_nan():
    a = np.array([1.0, 0.0, -1.0, 1e-20])
    b = np.array([1.0, 1.0, 1.0, 1e-20])
    result = van_leer(a, b)
    assert not np.any(np.isnan(result))


def test_van_leer_opposite_sign_zero():
    a = np.array([1.0, -1.0])
    b = np.array([-1.0, 1.0])
    result = van_leer(a, b)
    np.testing.assert_allclose(result, [0.0, 0.0])


def test_get_limiter_unknown_raises():
    with pytest.raises(ValueError, match="Unknown limiter"):
        get_limiter("nonexistent")


def test_limiters_support_arrays():
    a = np.ones((4, 10, 12))
    b = np.ones((4, 10, 12)) * 2.0
    for name in ["minmod", "vanleer"]:
        limiter = get_limiter(name)
        result = limiter(a, b)
        assert result.shape == a.shape
