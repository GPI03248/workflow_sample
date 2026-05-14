# API: cfd.numerics_reconstruction

Variable reconstruction at cell interfaces.

Responsibilities:
    - Reconstruct left/right states at cell interfaces from cell-centred values.
    - Currently implements piecewise-constant (1st order).
    - MUSCL interface is reserved for future extension.

Does NOT:
    - Apply limiters (see limiters.py).

## Functions

### `reconstruct(U, ng, method)`
Reconstruct left and right states at x-interfaces.

## Extension Notes

See docs/cfd_iteration_guide.md for how to extend this module.
