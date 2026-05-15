# Makefile for workflow_sample
# All Python commands use: tools/run_in_project_env.sh <command>
# (non-interactive, no bash -ic, no module-conda)
# Usage: make <target>

ENV = tools/run_in_project_env.sh

.PHONY: compile test docs \
        scalar-validation \
        cfd-uniform cfd-sod \
        cfd-entropy cfd-entropy-convergence \
        cfd-vortex cfd-vortex-convergence \
        cfd-validation \
        paper-extract paper-context \
        check-spec trace-task discover-env

# --- Compilation ---

compile:
	$(ENV) python -m compileall solver cfd tests examples tools

# --- Testing ---

test:
	$(ENV) pytest -q

# --- Documentation ---

docs:
	$(ENV) python tools/generate_cfd_api_docs.py

# --- 1D Scalar Advection ---

scalar-validation:
	$(ENV) python examples/compare_advection_schemes.py

# --- CFD: Uniform Flow ---

cfd-uniform:
	$(ENV) python examples/run_cfd_uniform_flow.py

# --- CFD: Sod Shock Tube ---

cfd-sod:
	$(ENV) python examples/run_cfd_sod_2d.py

# --- CFD: Entropy Wave ---

cfd-entropy:
	$(ENV) python examples/run_cfd_entropy_wave.py

cfd-entropy-convergence:
	$(ENV) python examples/run_cfd_entropy_wave_convergence.py

# --- CFD: Isentropic Vortex ---

cfd-vortex:
	$(ENV) python examples/run_cfd_isentropic_vortex.py

cfd-vortex-convergence:
	$(ENV) python examples/run_cfd_isentropic_vortex_convergence.py

# --- CFD: Full Validation Suite ---

cfd-validation: cfd-entropy cfd-entropy-convergence cfd-vortex cfd-vortex-convergence
	@echo "=== Full CFD validation complete ==="

# --- Paper-to-Code Tools ---

# Usage: make paper-extract PAPER=docs/papers/example.pdf
paper-extract:
	@if [ -z "$(PAPER)" ]; then echo "Usage: make paper-extract PAPER=docs/papers/<name>.pdf"; exit 1; fi
	$(ENV) python tools/extract_pdf_text.py $(PAPER)

# Usage: make paper-context PAPER_TEXT=docs/paper_reviews/example_text.md
paper-context:
	@if [ -z "$(PAPER_TEXT)" ]; then echo "Usage: make paper-context PAPER_TEXT=docs/paper_reviews/<name>_text.md"; exit 1; fi
	$(ENV) python tools/build_paper_context.py $(PAPER_TEXT)

# --- Approval Gate ---

# Usage: make check-spec SPEC=docs/scheme_specs/<name>.md
check-spec:
	@if [ -z "$(SPEC)" ]; then echo "Usage: make check-spec SPEC=docs/scheme_specs/<name>.md"; exit 1; fi
	$(ENV) python tools/check_scheme_spec_approval.py $(SPEC)

# --- Task Traceability ---

# Usage: make trace-task TASK_ID=<id> [other args...]
trace-task:
	@if [ -z "$(TASK_ID)" ]; then echo "Usage: make trace-task TASK_ID=<id>"; exit 1; fi
	$(ENV) python tools/create_task_traceability.py --task-id $(TASK_ID) \
		$(if $(SOURCE),--source $(SOURCE),) \
		$(if $(TASK_TYPE),--task-type $(TASK_TYPE),) \
		$(if $(SCHEME_SPEC),--scheme-spec $(SCHEME_SPEC),) \
		$(if $(EXTRACTION_REPORT),--extraction-report $(EXTRACTION_REPORT),) \
		$(if $(COMMIT_HASH),--commit-hash $(COMMIT_HASH),)

# --- Environment Discovery ---

discover-env:
	$(ENV) python tools/discover_project_env.py --json
