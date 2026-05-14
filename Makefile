# Makefile for workflow_sample
# All Python commands use: bash -ic 'module-conda && <command>'
# Usage: make <target>

.PHONY: compile test docs \
        scalar-validation \
        cfd-uniform cfd-sod \
        cfd-entropy cfd-entropy-convergence \
        cfd-vortex cfd-vortex-convergence \
        cfd-validation

# --- Compilation ---

compile:
	bash -ic 'module-conda && python -m compileall solver cfd tests examples tools'

# --- Testing ---

test:
	bash -ic 'module-conda && pytest -q'

# --- Documentation ---

docs:
	bash -ic 'module-conda && python tools/generate_cfd_api_docs.py'

# --- 1D Scalar Advection ---

scalar-validation:
	bash -ic 'module-conda && python examples/compare_advection_schemes.py'

# --- CFD: Uniform Flow ---

cfd-uniform:
	bash -ic 'module-conda && python examples/run_cfd_uniform_flow.py'

# --- CFD: Sod Shock Tube ---

cfd-sod:
	bash -ic 'module-conda && python examples/run_cfd_sod_2d.py'

# --- CFD: Entropy Wave ---

cfd-entropy:
	bash -ic 'module-conda && python examples/run_cfd_entropy_wave.py'

cfd-entropy-convergence:
	bash -ic 'module-conda && python examples/run_cfd_entropy_wave_convergence.py'

# --- CFD: Isentropic Vortex ---

cfd-vortex:
	bash -ic 'module-conda && python examples/run_cfd_isentropic_vortex.py'

cfd-vortex-convergence:
	bash -ic 'module-conda && python examples/run_cfd_isentropic_vortex_convergence.py'

# --- CFD: Full Validation Suite ---

cfd-validation: cfd-entropy cfd-entropy-convergence cfd-vortex cfd-vortex-convergence
	@echo "=== Full CFD validation complete ==="
