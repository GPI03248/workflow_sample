# Formula Inventories

This directory stores structured formula inventories extracted from papers.
Each inventory tracks the confidence and verification status of formulas
needed for implementation.

## Purpose

- Record which formulas have been extracted from a paper
- Track confidence level and verification status of each formula
- Identify which formulas block implementation approval
- Surface low-confidence formulas as a human verification queue

## Rules

1. Formula inventories are NOT paper full-text transcriptions
2. Only record formulas needed for implementation
3. Do NOT commit original PDFs
4. Do NOT copy large blocks of paper text
5. Only `high` confidence formulas can enter an implementation-ready spec
6. `medium` / `low` confidence formulas block or limit implementation
7. Required formulas must pass the confidence gate before `Approved=yes`

## File Format

Inventories use YAML (`.yml`) format. Each entry has:

| Field | Description |
|-------|-------------|
| `formula_id` | Unique identifier within the inventory |
| `paper_id` | Paper identifier (e.g., `cfweno_pof_2025`) |
| `source` | Section, page, table, equation reference |
| `formula_type` | Category (weight, stencil, indicator, reconstruction, update) |
| `expression` | Implementation-friendly string, or `null` if not verified |
| `extraction_method` | How the formula was obtained (pdftotext, human, etc.) |
| `confidence` | `high`, `medium`, or `low` |
| `verification_status` | `verified`, `visually_confirmed`, `partial`, `uncertain`, `missing` |
| `used_by` | List of spec files that depend on this formula |
| `implementation_relevance` | `required`, `optional`, or `not_needed` |
| `blocks_implementation` | `true` if low confidence blocks approval |
| `notes` | Free text |

## Tools

- **Checker**: `tools/check_formula_confidence.py <inventory.yml>`
- **Strict mode**: `--require-high-for-implementation --spec <spec.md>`
- **Markdown report**: `--markdown-report <output.md>`
- **JSON output**: `--json`

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make formula-confidence-cfweno5` | Check CFWENO5 formula confidence |
| `make formula-confidence-cfweno5-strict` | Strict check (expected to fail until all required formulas are high) |
| `make formula-confidence-report-cfweno5` | Generate CFWENO5 confidence report |
