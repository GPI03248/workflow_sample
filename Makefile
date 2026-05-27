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
        cfweno-scalar-demo cfweno-scalar-convergence cfweno-scalar-cfl-sweep demo-real-paper-scalar \
        cfweno-burgers-demo cfweno-burgers-convergence \
        cfweno-burgers-predictor-sweep cfweno-burgers-cfl-sweep \
        cfweno-burgers-reference-sensitivity demo-real-paper-burgers \
        demo-real-paper-cfweno demo-v1-real-paper \
        cfweno-burgers-order-recovery demo-v1.1-pre-order-recovery \
        paper-extract paper-context \
        check-spec trace-task discover-env \
        demo-hll-workflow validation-index health \
        formula-confidence-cfweno5 formula-confidence-cfweno5-strict formula-confidence-report-cfweno5 \
        cfweno5-formula-consistency cfweno5-formula-consistency-quick \
        release-check

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

# --- CFWENO Scalar Prototype ---

cfweno-scalar-demo:
	$(ENV) python examples/run_cfweno_scalar_demo.py

cfweno-scalar-convergence:
	$(ENV) python examples/run_cfweno_scalar_convergence.py

cfweno-scalar-cfl-sweep:
	$(ENV) python examples/run_cfweno_scalar_cfl_sweep.py

demo-real-paper-scalar: cfweno-scalar-demo cfweno-scalar-convergence cfweno-scalar-cfl-sweep validation-index
	@echo "=== CFWENO scalar demo complete ==="

# --- CFWENO Burgers Prototype ---

cfweno-burgers-demo:
	$(ENV) python examples/run_cfweno_burgers_demo.py

cfweno-burgers-convergence:
	$(ENV) python examples/run_cfweno_burgers_convergence.py

cfweno-burgers-predictor-sweep:
	$(ENV) python examples/run_cfweno_burgers_predictor_sweep.py

cfweno-burgers-cfl-sweep:
	$(ENV) python examples/run_cfweno_burgers_cfl_sweep.py

cfweno-burgers-reference-sensitivity:
	$(ENV) python examples/run_cfweno_burgers_reference_sensitivity.py

demo-real-paper-burgers: cfweno-burgers-demo cfweno-burgers-convergence \
                         cfweno-burgers-predictor-sweep cfweno-burgers-cfl-sweep \
                         cfweno-burgers-reference-sensitivity validation-index
	@echo "=== CFWENO Burgers demo complete ==="

# --- CFWENO Real-Paper Unified Demo (v1.0) ---

demo-real-paper-cfweno: demo-real-paper-scalar demo-real-paper-burgers validation-index health
	@echo "=== CFWENO real-paper demo complete (v1.0) ==="

demo-v1-real-paper: demo-real-paper-cfweno

# --- Post-v1.0 Diagnostic ---

cfweno-burgers-order-recovery:
	$(ENV) python examples/run_cfweno_burgers_order_recovery.py

demo-v1.1-pre-order-recovery: cfweno-burgers-order-recovery

cfd-validation: cfd-entropy cfd-entropy-convergence cfd-vortex cfd-vortex-convergence
	@echo "=== Full CFD validation complete ==="

# --- Formula Confidence ---

formula-confidence-cfweno5:
	$(ENV) python tools/check_formula_confidence.py docs/formula_inventories/cfweno5_scalar_formulas.yml

formula-confidence-cfweno5-strict:
	$(ENV) python tools/check_formula_confidence.py docs/formula_inventories/cfweno5_scalar_formulas.yml --require-high-for-implementation --spec docs/scheme_specs/cfweno5_scalar_subset.md

formula-confidence-report-cfweno5:
	$(ENV) python tools/check_formula_confidence.py docs/formula_inventories/cfweno5_scalar_formulas.yml --markdown-report docs/paper_reviews/cfweno_pof_2025/cfweno5_formula_confidence_report.md

# --- CFWENO5 Formula Consistency ---

cfweno5-formula-consistency:
	$(ENV) python tools/check_cfweno5_formula_consistency.py

cfweno5-formula-consistency-quick:
	$(ENV) python tools/check_cfweno5_formula_consistency.py --quick

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

# --- v0.1 Demo ---

demo-hll-workflow:
	@echo "=== HLL Paper-to-Code Demo ==="
	@echo "Step 1: Approval check"
	$(ENV) python tools/check_scheme_spec_approval.py docs/scheme_specs/hll_flux.md
	@echo "Step 2: Compile check"
	$(ENV) python -m compileall solver cfd tests examples tools -q
	@echo "Step 3: Tests"
	$(ENV) pytest -q
	@echo "Step 4: HLL validation"
	$(ENV) python examples/run_cfd_hll_validation.py
	@echo "Step 5: Validation index"
	$(ENV) python tools/summarize_validation_results.py
	@echo "=== Demo complete ==="

validation-index:
	$(ENV) python tools/summarize_validation_results.py

health:
	$(ENV) python tools/check_repo_health.py

# --- Release Check ---

release-check: compile test health validation-index
	@echo "=== Release checks complete ==="
