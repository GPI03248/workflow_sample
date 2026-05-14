"""Pre-built CFD test cases."""

from .uniform_flow import uniform_flow_config, uniform_flow_ic
from .sod_shock_tube_2d import sod_2d_config, sod_2d_ic

__all__ = [
    "uniform_flow_config",
    "uniform_flow_ic",
    "sod_2d_config",
    "sod_2d_ic",
]
