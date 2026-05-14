"""Error metrics for CFD solution validation.

Responsibilities:
    - Compute L1, L2, Linf errors per conservative variable.
    - Compute mass error for density.
    - Return results as a structured dict.

Does NOT:
    - Run the solver.
    - Perform any I/O.
"""

from __future__ import annotations
import numpy as np


def compute_field_errors(
    U_num: np.ndarray,
    U_exact: np.ndarray,
    dx: float,
    dy: float,
    variable_names: tuple | None = None,
) -> dict:
    """Compute per-variable error metrics between numerical and exact solutions.

    Parameters
    ----------
    U_num : np.ndarray, shape (4, ny, nx)
        Numerical conservative variables (interior only, no ghost cells).
    U_exact : np.ndarray, shape (4, ny, nx)
        Exact conservative variables on the same grid.
    dx, dy : float
        Cell sizes.
    variable_names : tuple of str or None
        Names for the 4 conservative variables. Default:
        ("rho", "rho_u", "rho_v", "E").

    Returns
    -------
    errors : dict
        Keys:
        - "rho_l1_error", "rho_l2_error", "rho_linf_error", "rho_mass_error"
        - "<name>_l1", "<name>_l2", "<name>_linf" for each variable
    """
    if variable_names is None:
        variable_names = ("rho", "rho_u", "rho_v", "E")

    cell_area = dx * dy
    n_cells = U_num.shape[1] * U_num.shape[2]

    errors: dict = {}

    for i, name in enumerate(variable_names):
        diff = U_num[i] - U_exact[i]
        l1 = np.sum(np.abs(diff)) * cell_area
        l2 = np.sqrt(np.sum(diff**2) * cell_area)
        linf = float(np.max(np.abs(diff)))
        errors[f"{name}_l1"] = l1
        errors[f"{name}_l2"] = l2
        errors[f"{name}_linf"] = linf

    # Density-specific errors with convenient names.
    errors["rho_l1_error"] = errors["rho_l1"]
    errors["rho_l2_error"] = errors["rho_l2"]
    errors["rho_linf_error"] = errors["rho_linf"]
    errors["rho_mass_error"] = float(np.abs(np.sum(U_num[0] - U_exact[0]) * cell_area))

    return errors
