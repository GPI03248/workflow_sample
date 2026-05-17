# CFD Module Interfaces

This document lists the public interface of every CFD module.

## cfd.config

### `CFDConfig` (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| nx, ny | int | 100, 50 | Interior cell counts |
| xmin, xmax, ymin, ymax | float | 0/1/0/0.5 | Domain extents |
| gamma | float | 1.4 | Ratio of specific heats |
| cfl | float | 0.5 | CFL number |
| ng | int | 2 | Ghost-cell layers |
| final_time | float | 0.1 | Simulation end time |
| bc_x, bc_y | str | "transmissive" | Boundary type |
| flux_type | str | "rusanov" | Numerical flux: "rusanov" or "hll" |
| reconstruction | str | "piecewise_constant" | Reconstruction: "piecewise_constant" or "muscl" |
| limiter | str | "minmod" | Slope limiter: "minmod" or "vanleer" |
| time_integrator | str | "euler" | Time integration: "euler" or "ssp_rk2" |

---

## cfd.mesh.structured

### `StructuredMesh2D`

**Constructor**: `StructuredMesh2D(nx, ny, xmin, xmax, ymin, ymax, ng=2)`

**Key attributes**: `dx`, `dy`, `x`, `y`, `nxt`, `nyt`, `interior_slice`

**Methods**:
- `cell_centers_2d() -> (X, Y)` — shape `(nyt, nxt)` each

---

## cfd.variables.conversion

### `primitive_to_conservative(rho, u, v, p, gamma=1.4) -> U`

- Input: 4 arrays of same shape
- Output: `U` shape `(4, *rho.shape)`

### `conservative_to_primitive(U, gamma=1.4) -> (rho, u, v, p)`

- Input: `U` shape `(4, ...)`
- Output: 4 arrays of shape `U.shape[1:]`
- Raises: ValueError if rho <= 0 or p <= 0

---

## cfd.physics

### `eos.pressure(rho, u, v, E, gamma=1.4) -> p`
- Shape: broadcast-compatible

### `eos.sound_speed(rho, p, gamma=1.4) -> c`
- Raises: ValueError if rho <= 0 or p <= 0

### `eos.total_energy(rho, u, v, p, gamma=1.4) -> E`

### `fluxes.euler_flux_x(U, gamma=1.4) -> F`
- Input/Output: shape `(4, ...)`

### `fluxes.euler_flux_y(U, gamma=1.4) -> G`
- Input/Output: shape `(4, ...)`

### `wavespeeds.max_wavespeed(U, gamma=1.4) -> (max_sx, max_sy)`

---

## cfd.boundary

### `ghost_cells.apply_boundary_conditions(U, ng, bc_x, bc_y)`
- Modifies `U` in-place
- `bc_x`, `bc_y`: one of "periodic", "transmissive", "reflective"

### Individual BC functions: `periodic_x`, `periodic_y`, `transmissive_x`, `transmissive_y`, `reflective_x`, `reflective_y`

---

## cfd.numerics

### `reconstruction.reconstruct(U, ng, method="piecewise_constant", limiter_name="minmod") -> (UL, UR)`
- `method`: "piecewise_constant" or "muscl"
- Returns left/right states at x-interfaces, shape `(4, nyt, nxt-1)`

### `reconstruction.reconstruct_y(U, ng, method="piecewise_constant", limiter_name="minmod") -> (UB, UT)`
- Returns bottom/top states at y-interfaces, shape `(4, nyt-1, nxt)`

### `limiters.minmod(a, b) -> slope`
- Vectorized minmod limiter

### `limiters.van_leer(a, b) -> slope`
- Vectorized van Leer limiter

### `limiters.get_limiter(name) -> callable`
- Returns limiter function by name; raises ValueError for unknown

### `riemann.rusanov_flux_x(UL, UR, gamma=1.4) -> Fnum`
- Input: `(4, nyt, nxt-1)`
- Output: `(4, nyt, nxt-1)`

### `riemann.rusanov_flux_y(UL, UR, gamma=1.4) -> Gnum`
- Input: `(4, nyt-1, nxt)`
- Output: `(4, nyt-1, nxt)`

### `riemann.hll_flux_x(UL, UR, gamma=1.4) -> Fnum`
- Input: `(4, nyt, nxt-1)`
- Output: `(4, nyt, nxt-1)`
- HLL (Harten-Lax-van Leer) approximate Riemann solver with Roe-averaged wave speeds

### `riemann.hll_flux_y(UL, UR, gamma=1.4) -> Gnum`
- Input: `(4, nyt-1, nxt)`
- Output: `(4, nyt-1, nxt)`

### `timestep.compute_dt(U, dx, dy, cfl, gamma=1.4) -> dt`
- Returns positive float
- Raises: ValueError for non-physical states

### `update.compute_residual(U, dx, dy, ng, gamma, flux_type, reconstruction, limiter) -> L`
- Returns spatial residual L(U) = -(dF/dx + dG/dy) for interior cells
- `flux_type`: "rusanov" or "hll"
- Shape matches U

### `update.apply_euler_step(U, dx, dy, dt, ng, gamma, flux_type, reconstruction, limiter) -> U`
- Applies U += dt*L(U) in-place
- `euler_update` is a backward-compatible alias

### `time_integration.advance(U, dx, dy, ng, cfl, final_time, ..., time_integrator="euler", limiter="minmod") -> dict`
- Returns `{"U", "n_steps", "actual_final_time", "snapshots"}`
- `time_integrator`: "euler" or "ssp_rk2"

---

## cfd.cases

### `uniform_flow.uniform_flow_config() -> CFDConfig`
### `uniform_flow.uniform_flow_ic(nxt, nyt, gamma=1.4) -> U`

### `sod_shock_tube_2d.sod_2d_config() -> CFDConfig`
### `sod_shock_tube_2d.sod_2d_ic(nxt, nyt, x_center=0.5, gamma=1.4) -> U`

---

## cfd.solver

### `run_solver(config, initial_condition_func, case_name, output_dir, centerline_x) -> dict`
- Returns `{"U", "mesh", "n_steps", "actual_final_time", "output_paths"}`

---

## cfd.io.output

### `save_results(output_dir, U, mesh, n_steps, actual_final_time, ...) -> dict`
- Returns dict with keys "csv", "npz", "md", "png"

---

## cfd.cases.entropy_wave

### `EntropyWaveParams` (dataclass)
- rho0, eps, u0, v0, p0, kx, ky, gamma

### `entropy_wave_config(params=None) -> CFDConfig`

### `entropy_wave_primitive(X, Y, t=0.0, params=None) -> V`
- Input: 2D coordinate arrays
- Output: (4, nyt, nxt) — [rho, u, v, p]

### `entropy_wave_conservative(X, Y, t=0.0, params=None) -> U`
- Output: (4, nyt, nxt) — [rho, rho*u, rho*v, E]

### `entropy_wave_exact_solution(mesh, t, params=None) -> U`
- Full analytic solution on the mesh at time t

### `entropy_wave_ic(nxt, nyt, gamma=1.4, params=None) -> U`
- IC compatible with run_solver

---

## cfd.cases.isentropic_vortex

### `IsentropicVortexParams` (dataclass)
- rho_inf, u_inf, v_inf, p_inf, beta, x0, y0

### `isentropic_vortex_primitive(X, Y, t=0.0, params=None) -> V`
- Output: (4, ...) — [rho, u, v, p]

### `isentropic_vortex_conservative(X, Y, t=0.0, params=None) -> U`
- Output: (4, ...) — [rho, rho*u, rho*v, E]

### `isentropic_vortex_exact_solution(mesh, t, params=None) -> U`
- Full analytic solution on the mesh at time t

### `isentropic_vortex_ic(nxt, nyt, gamma=1.4, params=None) -> U`
- IC compatible with run_solver

---

## cfd.validation.errors

### `compute_field_errors(U_num, U_exact, dx, dy, variable_names=None) -> dict`
- Input: (4, ny, nx) arrays (interior only, no ghosts)
- Returns: rho_l1_error, rho_l2_error, rho_linf_error, rho_mass_error, plus per-variable metrics
