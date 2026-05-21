# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0] - 2026-05-21

### Added

- CFWENO3 scalar linear advection prototype — 3rd-order convergence (order 3.02)
- CFWENO3 scalar Burgers prototype — ~2nd-order convergence (order 2.01), pre-shock
- Full CFWENO paper-to-code workflow (13 gated stages) from Zhou-Dong-Pan (2025)
- CFWENO scalar linear demo, convergence, and CFL sweep scripts
- CFWENO Burgers demo, convergence, predictor sweep, CFL sweep, reference sensitivity scripts
- Burgers flux-form audit: confirmed f_hat = f(ubar) is exact algebraic identity
- SFM state-consistency audit: confirmed state variables match spec
- CFWENO real-paper case study (`docs/case_studies/cfweno_real_paper_demo.md`)
- Unified demo target `make demo-real-paper-cfweno`
- 27 CFWENO-specific tests (19 scalar + 8 Burgers)
- Release notes for v1.0

### Changed

- Updated validation index with 8 CFWENO result directories (15 total)
- Updated roadmap with phased v1.1-v1.5 implementation plan

### Validation Results

- CFWENO3 linear: 380x more accurate than Lax-Wendroff, 11,937x more accurate than upwind
- CFWENO3 Burgers: 173x more accurate than Rusanov at nx=100
- CFL sweep: stable at CFL 0.1–0.9 (linear), 0.1–0.5 (Burgers)

## [0.1] - 2026-05-18

### Added

- 2D compressible Euler solver (NumPy) with Rusanov numerical flux
- 1D scalar advection solver with upwind and Lax-Wendroff schemes
- Analytic-solution verification for both solvers
- MUSCL reconstruction (2nd order) with minmod and van Leer limiters
- SSP RK2 time integration
- Periodic, transmissive, and reflective boundary conditions
- CFD test cases: uniform flow, Sod 2D, entropy wave, isentropic vortex
- Entropy wave and isentropic vortex convergence studies
- HLL approximate Riemann solver (Roe-averaged wave speeds)
- Paper-to-code workflow with deterministic approval gating
- Scheme spec approval checker (`tools/check_scheme_spec_approval.py`)
- Task traceability tool (`tools/create_task_traceability.py`)
- Project environment discovery and portable wrapper (`tools/run_in_project_env.sh`)
- Validation index generator (`tools/summarize_validation_results.py`)
- Repo health checker (`tools/check_repo_health.py`)
- CFD API docs generator (`tools/generate_cfd_api_docs.py`)
- PDF text extraction and agent context builder tools
- 9 agentic skills in `.claude/skills/`
- HLL paper-to-code case study (`docs/case_studies/hll_flux_paper_to_code.md`)
- Release notes, CHANGELOG, and `release-check` Makefile target
- Auto-generated validation index (`docs/validation_index.md`)
- Comprehensive test suite (200+ tests)

### Changed

- Environment wrapper migrated from interactive `bash -ic` to non-interactive discovery
- HLL validation index now correctly selects entropy_wave over uniform_flow for comparison

### Validation Results

- HLL produces 33% lower L2 error than Rusanov on entropy wave (ratio 0.6734)
- MUSCL + SSP RK2 achieves ~2nd-order convergence on isentropic vortex
- Uniform flow preserved to machine precision (all fluxes)
