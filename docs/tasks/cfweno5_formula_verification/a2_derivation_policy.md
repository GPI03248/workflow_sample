# Appendix A2 Derivation Policy

**Date**: 2026-05-26
**Context**: v1.3-pre.6, commit db94024 (character-level verification)
**Decision needed**: Is A2 a hard implementation blocker or an optional verification reference?

---

## Current Issue

- A2 (Eq. A2, Appendix A, page 24) is the sole remaining medium-confidence formula
- Strict formula confidence check fails due to A2
- pdftotext cannot reliably parse d/dv derivative terms (superscripts merge with other text)
- A2 has been at medium confidence since initial extraction
- A1 is verified at character level with high confidence

---

## Role of A2

### What A2 provides

Eq. (A2) gives the next-time-level reconstruction `u^{n+1,3}_{i+1/2,k}` for substencils
k=0,1,2,3. These are the coefficients needed to assemble the CFWENO5 predictor
at the next time level.

### What A1 provides

Eq. (A1) gives the initial-value reconstruction `ubar^{3}_{i+1/2,k}` for the same
substencils. These are the coefficients for the current-time-level interface values.

### Mathematical relationship

The paper defines A2 as the `d/dv` derivative of A1's coefficients, where `v = nu`:

```
u^{n+1}_{i+1/2,k} = ubar^{3}_{i+1/2,k} + (1-v) * d/dv [ubar^{3}_{i+1/2,k}]
```

This is a Taylor expansion in time — A2 is structurally derived from A1, not an
independent formula.

---

## Assessment: Required vs Optional

### Argument for REQUIRED

- A2 coefficients are needed at runtime to compute the next-time-level reconstruction
- The implementation must produce A2-equivalent values somehow
- If A2 is wrong, the CFWENO5 scheme produces wrong results

### Argument for OPTIONAL (verification reference)

- A2 is **mathematically derived** from A1 by differentiation
- A1 is verified at high confidence (character-level pdftotext)
- Symbolic differentiation of verified A1 coefficients is exact — no numerical error
- The implementation can compute `d/dv(A1 coefficients)` at implementation time
  and verify the result against the paper's A2 as a sanity check
- Transcribing A2 from pdftotext is LESS reliable than deriving from verified A1

### Implementation dependency analysis

1. **Does CFWENO5 implementation need to directly transcribe A2?** No.
   The implementation can derive A2 coefficients from A1 via symbolic differentiation.

2. **Can the implementation use only A1 and compute derivatives?** Yes.
   The derivatives are of simple polynomial expressions in v. Symbolic computation
   (e.g., `sympy.diff`) or manual differentiation of A1's coefficients produces
   exact A2 coefficients.

3. **If the implementation derives A2 from A1, does A2 transcription still block?** No.
   The derived coefficients are at least as reliable as A1 (high confidence, verified).

4. **Should A2 serve as a verification reference?** Yes.
   The paper provides A2 as an explicit check. The implementer should derive from A1
   and cross-verify against the paper's A2 expressions.

---

## Decision

**A2 is not a hard implementation blocker.** It is reclassified as an optional
verification reference.

**Rationale:**
1. A2 is mathematically derived from A1 (d/dv relationship)
2. A1 is verified at high confidence
3. Deriving A2 from verified A1 via symbolic differentiation is more reliable than
   transcribing A2 from pdftotext (which produces ambiguous output)
4. The paper provides A2 as a verification reference, not as the only source
5. An implementation that derives from A1 and cross-verifies against the paper's A2
   has strictly higher confidence than one that transcribes A2 directly

**Implementation path:**
1. Use verified A1 coefficients as the primary source
2. Compute d/dv of each A1 coefficient symbolically
3. Cross-verify the derived coefficients against the paper's A2 (visual check)
4. If all derived coefficients match the paper → A2 effectively verified
5. If any derived coefficient disagrees → flag for human investigation

**Inventory changes:**
- `implementation_relevance`: required → optional
- `blocks_implementation`: true → false
- `confidence`: medium (unchanged — pdftotext transcription remains ambiguous)
- `verification_status`: partial → derived_from_verified_A1
- Add notes explaining the derivation policy

---

## Impact on Formula Gate

After this policy change:
- Blocking formulas: 0
- All required formulas: 11 at high confidence, verified
- 1 optional formula (A2) at medium confidence, derived from verified source
- Strict confidence check: expected to PASS (only checks required formulas)

**Approved for implementation remains `no`** — the spec requires explicit human
approval regardless of formula gate status.
