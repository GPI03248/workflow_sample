# Paper Reference: CFWENO Schemes

## Citation

- **Title**: High-order compact fully discrete schemes for inviscid compressible flows simulations
- **Authors**: Tong Zhou (周通), Haitao Dong (董海涛), Shucheng Pan (潘书诚)
- **Journal**: Physics of Fluids 37, 106131 (2025)
- **DOI**: 10.1063/5.0291087
- **Publisher**: AIP Publishing
- **License**: Exclusive license to AIP Publishing

## Local Copy

- **Path**: `.local/papers/cfweno_pof_2025.pdf` (NOT in git)
- **Size**: ~10 MB, 25 pages

## Method Designation

- **Short name**: CFWENO (Compact Fully-discrete WENO)
- **Full name**: Compact single-stage fully discrete WENO scheme
- **Key innovation**: Uses Hamilton-Jacobi equation quasi-exact solutions instead of Lax-Wendroff temporal derivative expansion

## Scope in Paper

| Section | Content |
|---------|---------|
| II.A | Scalar 1D: SFM derivation, Hermite interpolation connection |
| II.B | WENO reconstruction: 3rd/5th/7th order stencils |
| II.C | Flux reconstruction strategy (Algorithm 1) |
| II.D | Extension to 1D Euler equations |
| II.E | Multi-dimensional extension via consistent cell-interface distribution |
| III | Numerical validation: scalar + Euler 1D + 2D cases |

## Orderings Available

- CFWENO3 (3rd order)
- CFWENO5 (5th order)
- CFWENO7 (7th order)

## Key Distinguishing Features vs. Existing Methods

| Feature | CFWENO | FWENO | WENO-RK |
|---------|--------|-------|---------|
| Time stepping | Single-stage | Single-stage | Multi-stage RK |
| Stencil type | Compact | Non-compact | Non-compact |
| Temporal discretization | HJ quasi-exact solution | HJ quasi-exact solution | Runge-Kutta |
| Cost per step | ~1.2-1.4x FWENO | Baseline | ~3-4x FWENO |
| Total cost (scalar) | ~0.25x WENO-RK3 | ~0.2x WENO-RK3 | Baseline |
| CFL restriction | ≤ 1 | ≤ 1 | ≤ 1 |

## Intake Date

- 2026-05-18

## Intake Purpose

- Feasibility assessment for v1.0 paper-to-code demo in workflow_sample
