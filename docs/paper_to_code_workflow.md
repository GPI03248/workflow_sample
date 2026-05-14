# Paper-to-Code CFD Workflow

This document describes how to go from a CFD research paper to a verified
implementation in this solver, step by step, using the project's agentic skills.

---

## Why Not Jump Straight from PDF to Code?

1. **PDF text extraction is unreliable** — formulas lose subscripts, superscripts,
   Greek letters, and fractions. Table formatting is usually destroyed.
2. **Papers assume context** — variable definitions may be scattered across sections,
   appendices, or referenced papers.
3. **Not all methods fit our solver** — the paper may assume unstructured grids,
   3D, different variable formulations, or pre-processing not available here.
4. **Formulas need verification** — a misread subscript or sign error produces a
   subtly wrong implementation that passes basic tests but gives wrong physics.
5. **Human oversight is essential** — the agent cannot judge physical correctness
   of a formula it extracted from a noisy PDF.

The workflow forces a **review gate** between extraction and implementation.

---

## Recommended Flow

```
1. Place PDF in docs/papers/
       ↓
2. Extract paper content → docs/paper_reviews/<id>_text.md
       ↓
3. Build agent context  → docs/paper_reviews/<id>_context.md
       ↓
4. Extract method info  → docs/paper_reviews/<id>_extraction.md
       ↓
5. Generate scheme spec → docs/scheme_specs/<scheme>.md
       ↓
6. HUMAN REVIEWS AND APPROVES THE SPEC
       ↓
7. Implement code       → cfd/numerics/<module>.py
       ↓
8. Run validation       → results/<scheme>_validation/
       ↓
9. Review changes       → review-cfd-change skill
       ↓
10. Commit and push
```

---

## File Naming Conventions

| File | Path | Description |
|------|------|-------------|
| PDF | `docs/papers/<author>_<year>_<topic>.pdf` | Original paper |
| Extracted text | `docs/paper_reviews/<id>_text.md` | Raw text from PDF |
| Agent context | `docs/paper_reviews/<id>_context.md` | Structured context |
| Extraction report | `docs/paper_reviews/<id>_extraction.md` | Method extraction |
| Scheme spec | `docs/scheme_specs/<scheme_name>.md` | Implementation spec |
| Validation results | `results/<scheme_name>_validation/` | Validation outputs |

Use a consistent `<id>` across all files. Example: `toro_2009_hllc`.

---

## How to Handle Common Issues

### PDF Parsing Failed

If `tools/extract_pdf_text.py` fails:
1. Check if the PDF is scanned (image-based): `pdftotext` will produce empty output.
2. Try installing OCR tools: `apt-get install tesseract-ocr poppler-utils`
3. Alternatively, manually copy the paper's method section into a `.md` file
   and place it in `docs/paper_reviews/`.
4. Re-run the extraction skill with the text file instead of the PDF.

### Formulas Are Incomplete or Garbled

This is expected for most PDFs with mathematical content. Options:
1. Manually write the key formulas in the extraction report.
2. Provide the paper's method section as text/markdown.
3. If only a few formulas are unclear, mark them `[AMBIGUOUS]` in the spec
   and ask the user to verify.

### Method Is Incompatible with Current Solver

The extraction report will flag this. Common incompatibilities:
- Requires unstructured mesh (we have Cartesian only)
- Requires 3D (we are 2D)
- Requires different variable formulation (e.g., entropy variables)
- Requires source terms we don't support (e.g., gravity, chemistry)
- Requires AMR or adaptive time stepping

Options:
1. Simplify the method for our solver (document simplifications in the spec).
2. Add the missing infrastructure first (may be a separate task).
3. Skip this paper and find a compatible method.

---

## How to Run Each Skill

### Step 1: Extract Paper Scheme

```
使用 extract-paper-scheme skill 分析 docs/papers/xxx.pdf。
只生成 extraction report，不要实现代码。
```

Or manually:
```bash
bash -ic 'module-conda && python tools/extract_pdf_text.py docs/papers/xxx.pdf --out docs/paper_reviews/xxx_text.md'
bash -ic 'module-conda && python tools/build_paper_context.py docs/paper_reviews/xxx_text.md --out docs/paper_reviews/xxx_context.md'
```

Then ask Claude to read the context and generate the extraction report.

### Step 2: Write Scheme Spec

```
使用 write-scheme-spec skill，根据 docs/paper_reviews/xxx_extraction.md 生成 scheme spec。
默认不要实现代码。
```

### Step 3: Review and Approve

Open `docs/scheme_specs/<scheme>.md`, review every section, and change:
```
Approved for implementation: no
```
to:
```
Approved for implementation: yes
```

### Step 4: Implement

```
我已经确认 docs/scheme_specs/xxx.md，并将 Approved for implementation 改为 yes。
请使用 implement-paper-scheme skill 实现它，并运行 required validation。
```

### Step 5: Validate (if not already done by implement step)

```
使用 validate-paper-scheme skill，验证 docs/scheme_specs/xxx.md 中实现的数值方法。
```

### Step 6: Review and Commit

```
使用 review-cfd-change skill，review 当前未提交的改动。确认后 commit。
```

---

## Example End-to-End Session

```bash
# 1. Place paper
cp ~/Downloads/toro_2009_hllc.pdf docs/papers/

# 2. Extract (via Claude Code prompt)
# "使用 extract-paper-scheme skill 分析 docs/papers/toro_2009_hllc.pdf"

# 3. Generate spec (via Claude Code prompt)
# "使用 write-scheme-spec skill，根据 docs/paper_reviews/toro_2009_hllc_extraction.md 生成 scheme spec"

# 4. Human reviews spec
# Edit docs/scheme_specs/hllc.md → set Approved for implementation: yes

# 5. Implement (via Claude Code prompt)
# "使用 implement-paper-scheme skill 实现 docs/scheme_specs/hllc.md"

# 6. Validate
# "使用 validate-paper-scheme skill 验证 hllc"

# 7. Commit
# git add . && git commit -m "Add HLLC Riemann solver from Toro (2009)"
```

---

## Quick Reference: Skills

| Skill | Input | Output | Code changes? |
|-------|-------|--------|---------------|
| `extract-paper-scheme` | PDF or text | extraction report | No |
| `write-scheme-spec` | extraction report | scheme spec | No |
| `implement-paper-scheme` | approved spec | code + tests + docs | Yes |
| `validate-paper-scheme` | scheme spec | validation results | No |

---

## Quick Reference: Tools

```bash
# Extract PDF text
bash -ic 'module-conda && python tools/extract_pdf_text.py docs/papers/<name>.pdf'

# Build agent context
bash -ic 'module-conda && python tools/build_paper_context.py docs/paper_reviews/<name>_text.md'

# Or use Makefile
make paper-extract PAPER=docs/papers/<name>.pdf
make paper-context PAPER_TEXT=docs/paper_reviews/<name>_text.md
```
