"""Tests for the CFD validation error computation."""

import numpy as np

from cfd.validation.errors import compute_field_errors


def test_zero_errors_for_identical_input():
    """Identical numerical and exact solutions should give zero errors."""
    rng = np.random.default_rng(42)
    ny, nx = 10, 12
    U = rng.uniform(0.5, 2.0, (4, ny, nx))
    errors = compute_field_errors(U, U, dx=0.1, dy=0.1)
    for key in ["rho_l1_error", "rho_l2_error", "rho_linf_error", "rho_mass_error"]:
        assert errors[key] == 0.0, f"{key} should be 0"


def test_error_positive_for_different_input():
    """Errors should be positive when solutions differ."""
    rng = np.random.default_rng(42)
    ny, nx = 10, 12
    U1 = rng.uniform(0.5, 2.0, (4, ny, nx))
    U2 = U1.copy()
    U2[0, 0, 0] += 0.1
    errors = compute_field_errors(U1, U2, dx=0.1, dy=0.1)
    assert errors["rho_l1_error"] > 0
    assert errors["rho_l2_error"] > 0
    assert errors["rho_linf_error"] > 0


def test_all_variable_errors_present():
    """All four variables should have error metrics."""
    ny, nx = 5, 6
    U = np.ones((4, ny, nx))
    errors = compute_field_errors(U, U, dx=0.1, dy=0.1)
    for name in ["rho", "rho_u", "rho_v", "E"]:
        assert f"{name}_l1" in errors
        assert f"{name}_l2" in errors
        assert f"{name}_linf" in errors
