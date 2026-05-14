---
name: extract-paper-scheme
description: Extract numerical method information from a CFD paper PDF or text without implementing code
---

# Extract Paper Scheme

## When to Use

- When the user provides a paper PDF, paper text, or asks to "add a numerical method from a paper"
- When the user says "根据论文添加格式" or similar
- This is ALWAYS the first step — never skip to implementation

## Required Inputs

One of:
- **PDF file path** (e.g., `docs/papers/example.pdf`)
- **Extracted text file** (e.g., `docs/paper_reviews/example_text.md`)
- **Direct text** of the paper's method section

## Required Workflow

1. **Read project rules**:
   - Read `CLAUDE.md`
   - Read `docs/cfd_definition_of_done.md`

2. **Check input exists**: Verify the provided file path exists. If not, ask the user.

3. **Process the input**:
   - If PDF:
     a. Try reading the PDF directly (Claude can read PDFs).
     b. If direct reading is unreliable or insufficient, run:
        ```bash
        bash -ic 'module-conda && python tools/extract_pdf_text.py docs/papers/<name>.pdf --out docs/paper_reviews/<name>_text.md'
        ```
     c. Then run:
        ```bash
        bash -ic 'module-conda && python tools/build_paper_context.py docs/paper_reviews/<name>_text.md --out docs/paper_reviews/<name>_context.md'
        ```
     d. Read the generated context file.
   - If text/markdown: read it directly.

4. **Extract information** into `docs/paper_reviews/<paper_id>_extraction.md` using `templates/paper_extraction_report.md` as the template:
   - Paper metadata (title, authors, year)
   - Governing equations
   - Numerical flux type
   - Reconstruction method
   - Limiter (if any)
   - Time integration scheme
   - Boundary condition assumptions
   - CFL / stability conditions
   - Variables and notation
   - Formula map with confidence levels
   - Notation table mapping to current solver

5. **Assess compatibility**:
   - Read `docs/cfd_module_interfaces.md` to understand current solver capabilities
   - Read `docs/cfd_iteration_guide.md` to understand extension points
   - Determine if the method is: fully compatible / partially compatible / incompatible
   - List required modules and missing infrastructure

6. **Propose validation plan**:
   - Identify which existing analytic cases can be used
   - Identify what new test cases might be needed
   - Specify expected convergence behavior

7. **List questions for human confirmation**:
   - Any ambiguous formulas
   - Any assumptions that need clarification
   - Any compatibility concerns

## Mandatory Rules

- **DO NOT modify any code in `cfd/`** — this skill is extraction only
- **DO NOT implement any numerical method** — even if the formula is trivial
- **DO NOT fabricate formulas** — if a formula is unclear, mark confidence as "low" and ask
- If PDF text extraction fails or is incomplete, **must** report the issue and ask the user to provide the method section text
- If the paper describes a method incompatible with the current solver architecture, **must** flag this explicitly

## Files to Inspect

- The provided PDF or text file
- `templates/paper_extraction_report.md` — output template
- `docs/cfd_module_interfaces.md` — current solver capabilities
- `docs/cfd_iteration_guide.md` — extension points
- `cfd/config.py` — available configuration options
- `cfd/numerics/` — current numerical methods

## Files That May Be Modified

- `docs/paper_reviews/<paper_id>_text.md` — **NEW** (extracted text)
- `docs/paper_reviews/<paper_id>_context.md` — **NEW** (agent context)
- `docs/paper_reviews/<paper_id>_extraction.md` — **NEW** (extraction report)

## Tests to Run

None — this skill does not modify code.

## Result Files to Generate

- `docs/paper_reviews/<paper_id>_extraction.md` — the extraction report

## Final Response Format

```
## Paper Extraction Report

### Source
- Paper: <title>
- File: <path>

### Extraction Results
- Extraction method: <pdftotext/pypdf/direct>
- Sections found: <count>
- Formulas detected: <count>
- Method sections: <list>

### Key Findings
- Method type: <reconstruction/limiter/flux/time_integrator/complete>
- Compatible: <yes/no/partial>
- [Summary of what was found]

### Confidence Assessment
- Overall confidence: <high/medium/low>
- [Per-formula confidence if needed]

### Unresolved Questions
1. <question>
2. <question>

### Decision
- Ready for scheme spec: <yes/no>
- Next step: <use write-scheme-spec skill / provide more info / incompatible>

### Generated Files
- Extraction report: <path>
```

## Failure Handling Rules

- If PDF file not found → report path, suggest correct location
- If PDF extraction produces empty or garbage text → warn about scanned PDF, ask for manual text
- If formulas are unclear (confidence low) → mark in report, ask user to verify
- If method is incompatible → explain why, suggest what infrastructure would be needed
- If the paper describes multiple methods → extract each separately or focus on the one the user wants
