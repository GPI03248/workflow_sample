# Current Agent Handoff Document

Generated: 2026-05-15

---

## 1. Completed Features

### Part 1: 1D Scalar Advection Solver
- PDE: u_t + a*u_x = 0, periodic BC, domain [0,1)
- IC: u(x,0) = sin(2*pi*x) + 1
- Schemes: upwind (1st order), Lax-Wendroff (2nd order)
- Analytic verification with L1/L2/Linf error metrics
- Location: `solver/`

### Part 2: 2D Compressible Euler CFD Solver
- 2D Euler equations for ideal gas (gamma=1.4)
- Conservative variables U = [rho, rho*u, rho*v, E]
- Array layout: (4, nyt, nxt) with ng=2 ghost cells
- Rusanov (local Lax-Friedrichs) numerical flux
- MUSCL piecewise-linear reconstruction on primitive variables
- Slope limiters: minmod, van Leer
- Time integration: Forward Euler, SSP RK2
- Boundary conditions: periodic, transmissive, reflective
- Location: `cfd/`

### Part 3: Analytic Validation Cases
- **Entropy wave**: sinusoidal density perturbation, periodic BC, 1st-order convergence test
- **Isentropic vortex**: nonlinear smooth flow, periodic BC, 2nd-order convergence test
- Convergence results:
  - Baseline (piecewise_constant + euler): ~1st order on both cases
  - MUSCL + minmod + SSP_RK2: ~1.8-2.0 order on isentropic vortex

### Part 4: Multi-Agent Workflow Infrastructure
- 5 CFD skills + 4 paper-to-code skills = 9 skills total
- Definition of Done checklists for 7 task types
- Makefile with compile/test/docs/validation targets
- Paper-to-code workflow: PDF → extraction → spec → approval → implementation → validation

---

## 2. Current Workflow / Skills / Tools / Docs Status

### Skills (`.claude/skills/`)

| Skill | Purpose |
|-------|---------|
| `add-cfd-case` | Add new flow problem or analytic validation case |
| `add-numerical-method` | Add reconstruction, limiter, Riemann solver, or time integrator |
| `run-cfd-validation` | Run full analytic validation suite |
| `update-cfd-docs` | Update documentation after code changes |
| `review-cfd-change` | Review a change before committing |
| `add-numerical-scheme` | (legacy 1D advection skill) |
| `extract-paper-scheme` | Extract numerical method from paper PDF/text |
| `write-scheme-spec` | Generate implementation spec from extraction report |
| `implement-paper-scheme` | Implement from approved spec (gated on approval) |
| `validate-paper-scheme` | Validate paper-derived implementation |

### Tools (`tools/`)

| Tool | Purpose |
|------|---------|
| `generate_cfd_api_docs.py` | Generate `docs/api/` from docstrings |
| `extract_pdf_text.py` | PDF → text (pdftotext/pypdf) |
| `build_paper_context.py` | Text → agent-friendly context with sections/formulas |

### Templates (`templates/`)

| Template | Purpose |
|----------|---------|
| `paper_extraction_report.md` | Paper extraction report template |
| `scheme_spec.md` | Implementation spec template (default: not approved) |

### Makefile Targets

| Target | Description |
|--------|-------------|
| `make compile` | Syntax-check all Python |
| `make test` | Run pytest (75 tests) |
| `make docs` | Regenerate API docs |
| `make cfd-validation` | Full validation (entropy + vortex + convergence) |
| `make paper-extract PAPER=...` | Extract text from PDF |
| `make paper-context PAPER_TEXT=...` | Build agent context |

### Documentation (`docs/`)

| Document | Description |
|----------|-------------|
| `cfd_architecture.md` | Solver architecture, data flow, call sequence |
| `cfd_module_interfaces.md` | Public interface of every CFD module |
| `cfd_iteration_guide.md` | How to extend the solver (9 sections) |
| `cfd_definition_of_done.md` | Completion checklists for 7 task types |
| `paper_to_code_workflow.md` | Paper-to-code workflow guide |
| `api/` | 33 auto-generated API docs |

### Hooks
- No hooks are currently configured in `.claude/` settings.

---

## 3. Most Recent Task

**Task**: Add paper-to-code CFD workflow infrastructure (commit `33fd9f0`)

What was done:
- Created 4 new skills: `extract-paper-scheme`, `write-scheme-spec`, `implement-paper-scheme`, `validate-paper-scheme`
- Created 2 tools: `extract_pdf_text.py`, `build_paper_context.py`
- Created 2 templates: `paper_extraction_report.md`, `scheme_spec.md`
- Created `docs/paper_to_code_workflow.md` with step-by-step guide and example prompts
- Added `docs/papers/`, `docs/paper_reviews/`, `docs/scheme_specs/` directories
- Added Makefile targets: `paper-extract`, `paper-context`
- Updated `CLAUDE.md` with paper-to-code mandatory rules
- Updated `README.md` with paper-to-code workflow section
- Added 10 tests for paper tools (75 total tests passing)

---

## 4. Verification Already Run

All of the following have been run and verified:

```
# Compilation
python -m compileall solver cfd tests examples tools — PASS

# Tests
pytest -q — 75 passed

# Makefile
make compile — PASS
make test — 75 passed

# CFD Validation
python examples/run_cfd_uniform_flow.py — PASS (machine precision)
python examples/run_cfd_sod_2d.py — PASS
python examples/run_cfd_entropy_wave.py — PASS (L2: 7.19e-03 @ 64x64)
python examples/run_cfd_entropy_wave_convergence.py — PASS (~1st order)
python examples/run_cfd_isentropic_vortex.py — PASS (L2: 2.66e-02 @ 64x64, MUSCL)
python examples/run_cfd_isentropic_vortex_convergence.py — PASS (~2nd order, MUSCL)

# Docs
python tools/generate_cfd_api_docs.py — 33 API docs generated

# Git
git push origin master — pushed successfully
```

---

## 5. Current Branch and Latest Commit

- **Branch**: `master`
- **Remote**: `git@gitee.com:gpiii/workflow_sample.git`
- **Latest commit**: `33fd9f0 Add paper-to-code CFD workflow`
- **Commit history**:
  ```
  33fd9f0 Add paper-to-code CFD workflow
  32eaed9 Codify CFD agentic workflow into skills, definition of done, and Makefile
  cca930c Add MUSCL reconstruction, van Leer limiter, SSP RK2, and isentropic vortex validation
  788a23d Add analytic entropy wave CFD validation case
  b9ec74d Add Python CPU CFD full-field solver MVP
  a97e53d Add analytic advection verification benchmark
  f8ce231 Initialize multi-agent workflow sample
  ```

---

## 6. Suggested Next Steps

### Option A: Use the paper-to-code workflow with a real paper
```
cp ~/Downloads/some_paper.pdf docs/papers/
使用 extract-paper-scheme skill 分析 docs/papers/some_paper.pdf
```
Then follow the workflow in `docs/paper_to_code_workflow.md`.

### Option B: Extend the solver with new numerical methods
```
使用 add-numerical-method skill，实现 HLLC flux（x 和 y 方向）。
```

### Option C: Add new validation cases
```
使用 add-cfd-case skill，添加 Taylor-Green vortex 解析解算例。
```

### Option D: Infrastructure improvements
- Add CI/CD pipeline (GitHub Actions / Gitee CI)
- Add hooks in `.claude/settings.json` for auto-running pytest before commit
- Add performance benchmarking (timing runs)
- Add more comprehensive convergence studies (finer grids, more methods)

---

## 7. IMPORTANT: Working Directory

**The correct working directory is:**

```
/data/gpi/Gitcode/workflow_sample/
```

**NOT:**
```
/data/gpi/Gitcode/Multi-agent-workflow-sample/   ← WRONG
/data/gpi/Gitcode/Multi-agent-workflow-sample    ← WRONG
```

The directory `Multi-agent-workflow-sample` was an initial misnomer. The actual
git repository is at `workflow_sample/`.

**When starting a new Claude Code session**, `cd` into the correct directory first:

```bash
cd /data/gpi/Gitcode/workflow_sample
claude
```

Or launch Claude Code with the correct working directory from the start.

---

## 8. Do NOT Use Multi-agents-workflow-sample

The directory `/data/gpi/Gitcode/Multi-agent-workflow-sample/` is **not** the project
repository. It does not have the git history, the CFD code, or the skills.

All work must be done in `/data/gpi/Gitcode/workflow_sample/`.

If Claude Code starts in the wrong directory, use `cd /data/gpi/Gitcode/workflow_sample`
before doing anything else.
