"""Physical and numerical constants.

Responsibilities:
    - Centralise magic numbers used across the CFD solver.

Does NOT:
    - Perform any computation.
"""

GAMMA: float = 1.4  # ratio of specific heats for ideal diatomic gas

# Conservative variable indices
IRHO: int = 0   # rho
IRHOU: int = 1  # rho * u
IRHOV: int = 2  # rho * v
IE: int = 3     # total energy E

# Primitive variable indices
IRHO_P: int = 0  # rho
IU: int = 1      # u
IV: int = 2      # v
IP: int = 3      # p

NVAR: int = 4    # number of variables
