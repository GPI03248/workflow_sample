---
name: write-scheme-spec
description: Generate an implementation-ready scheme spec from a paper extraction report
---

# Write Scheme Spec

## When to Use

- After completing the `extract-paper-scheme` skill
- When an extraction report exists in `docs/paper_reviews/`
- When the user asks to "generate the scheme spec" or "create implementation plan"

## Required Inputs

- **Extraction report path**: `docs/paper_reviews/<paper_id>_extraction.md`
- The extraction report must have `ready for scheme spec: yes`

## Required Workflow

1. **Read project context**:
   - Read `CLAUDE.md`
   - Read `docs/cfd_definition_of_done.md`

2. **Read inputs**:
   - Read `templates/scheme_spec.md` — the output template
   - Read the extraction report: `docs/paper_reviews/<paper_id>_extraction.md`
   - Read `docs/cfd_module_interfaces.md` — current solver interfaces
   - Read `docs/cfd_iteration_guide.md` — extension guide

3. **Classify the method**: Determine which category:
   - `reconstruction` → affects `cfd/numerics/reconstruction.py`
   - `limiter` → affects `cfd/numerics/limiters.py`
   - `riemann` → affects `cfd/numerics/riemann.py`, `cfd/numerics/update.py`
   - `time_integrator` → affects `cfd/numerics/time_integration.py`, `cfd/numerics/update.py`
   - `source_term` → may need new module
   - `boundary_condition` → affects `cfd/boundary/`
   - `complete_case` → affects `cfd/cases/`, may need multiple method changes

4. **Fill in the scheme spec**:

   a. **Mathematical definition**: Write out every formula in plain text notation.
      - Use explicit variable names: `rho`, `u`, `v`, `p`, `E`, `gamma`
      - Show the algorithm step by step
      - Include stability conditions (CFL limits)

   b. **Variable mapping**: Map every paper symbol to a code equivalent:
      - Paper symbol → meaning → code variable or module path
      - Flag any symbols that have no current equivalent

   c. **Algorithm steps**: Numbered list of what the code must do, in order

   d. **Required code changes**: Table of module → required change
      - Be specific about which function to modify
      - List new functions needed

   e. **Public API changes**: Any new config fields, new function signatures

   f. **Tests required**: Specific test cases from `docs/cfd_definition_of_done.md`

   g. **Validation required**: Which analytic cases and convergence studies to run

5. **Check compatibility**: Verify against `docs/cfd_module_interfaces.md`:
   - Does the method fit the existing array layout `(4, nyt, nxt)`?
   - Does it need parameters not in `CFDConfig`?
   - Does it require new modules or dependencies?

6. **Write the spec**:
   - Output to `docs/scheme_specs/<scheme_name>.md`
   - **MUST** set `Approved for implementation: no`
   - Include the full human confirmation checklist

7. **Report**: Summarize the spec and remind user they must review and approve.

## Mandatory Rules

- **DO NOT implement any code** — this skill produces a document only
- **DO NOT modify `cfd/`** — no code changes
- The spec MUST have `Approved for implementation: no` — the deterministic checker must reject it until the user explicitly changes it.
- If the extraction report says `ready for scheme spec: no`, **STOP** and tell the user what's missing
- If the method is incompatible, write the spec but clearly mark it with a warning

## Files to Inspect

- `templates/scheme_spec.md` — output template
- `docs/paper_reviews/<paper_id>_extraction.md` — input extraction report
- `docs/cfd_module_interfaces.md` — current interfaces
- `docs/cfd_iteration_guide.md` — extension guide
- `cfd/config.py` — available config fields
- `cfd/numerics/` — relevant current implementations

## Files That May Be Modified

- `docs/scheme_specs/<scheme_name>.md` — **NEW** (the spec file)

## Tests to Run

None — this skill produces a document only.

## Result Files to Generate

- `docs/scheme_specs/<scheme_name>.md`

## Final Response Format

```
## Scheme Spec Generated

### Spec File
- Path: docs/scheme_specs/<scheme_name>.md
- Status: Approved for implementation: **no**

### Summary
- Method type: <category>
- Compatible: <yes/no/partial>
- Required changes: <count> modules
- New functions: <list>
- Config changes: <list>

### What You Must Do Before Implementation
1. Open the spec file: docs/scheme_specs/<scheme_name>.md
2. Review every formula in "Mathematical definition"
3. Review every entry in "Variable mapping"
4. Verify "Compatibility" assessment
5. Review "Validation required"
6. If everything is correct, change the first line to:
   Approved for implementation: yes
7. Then use the implement-paper-scheme skill to implement.
```

## Failure Handling Rules

- If extraction report not found → tell user to run `extract-paper-scheme` first
- If extraction report says `ready for scheme spec: no` → list what's missing
- If the method is incompatible → write spec anyway but add prominent warning
- If formulas are ambiguous → mark in spec with `[AMBIGUOUS]` tag and add question
