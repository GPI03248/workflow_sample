"""Mass conservation tests — the integral of u should stay constant."""

import numpy as np

from solver.grid import gaussian_ic, make_grid
from solver.simulate import initial_condition
from solver.schemes import step


def test_upwind_mass_conservation_single_step():
    """One upwind step should conserve total mass (sum of u * dx)."""
    n = 200
    centers, dx = make_grid(n)
    u = gaussian_ic(centers)
    mass_before = u.sum() * dx

    u_new = step(u, cfl=0.8, scheme="upwind")
    mass_after = u_new.sum() * dx

    np.testing.assert_allclose(mass_after, mass_before, rtol=1e-12)


def test_upwind_mass_conservation_many_steps():
    """After many steps, total mass should still be conserved."""
    n = 200
    cfl = 0.8
    centers, dx = make_grid(n)
    u = gaussian_ic(centers)
    mass_initial = u.sum() * dx

    for _ in range(500):
        u = step(u, cfl, scheme="upwind")

    mass_final = u.sum() * dx
    np.testing.assert_allclose(mass_final, mass_initial, rtol=1e-10)


def test_lax_wendroff_mass_conservation_single_step():
    """One Lax-Wendroff step should conserve total mass."""
    n = 200
    centers, dx = make_grid(n)
    u = initial_condition(centers)
    mass_before = u.sum() * dx

    u_new = step(u, cfl=0.5, scheme="lax_wendroff")
    mass_after = u_new.sum() * dx

    np.testing.assert_allclose(mass_after, mass_before, rtol=1e-12)


def test_lax_wendroff_mass_conservation_many_steps():
    """After many steps, Lax-Wendroff mass should still be conserved."""
    n = 200
    cfl = 0.5
    centers, dx = make_grid(n)
    u = initial_condition(centers)
    mass_initial = u.sum() * dx

    for _ in range(500):
        u = step(u, cfl, scheme="lax_wendroff")

    mass_final = u.sum() * dx
    np.testing.assert_allclose(mass_final, mass_initial, rtol=1e-10)
