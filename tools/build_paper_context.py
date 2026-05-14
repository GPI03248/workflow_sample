"""Build an agent-friendly context file from extracted paper text.

Reads the extracted text/markdown and produces a structured context file
that is easier for AI agents to parse and reason about.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


def _detect_sections(lines: list[str]) -> list[dict]:
    """Detect section headings from text lines."""
    sections = []
    heading_patterns = [
        re.compile(r"^#+\s+(.+)$"),                     # Markdown heading
        re.compile(r"^(\d+(\.\d+)*)\s+(.+)$"),          # Numbered heading
        re.compile(r"^([A-Z][A-Za-z\s]+)$"),            # Title-case line
    ]
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        for pat in heading_patterns:
            m = pat.match(stripped)
            if m:
                title = m.group(m.lastindex).strip() if m.lastindex else stripped
                sections.append({"line": i + 1, "title": title, "text": stripped})
                break
    return sections


def _detect_formulas(lines: list[str]) -> list[dict]:
    """Detect lines that likely contain mathematical formulas."""
    formulas = []
    formula_indicators = [
        re.compile(r"[=+\-*/^]"),           # arithmetic operators
        re.compile(r"\\frac|\\sum|\\int|\\partial"),  # LaTeX
        re.compile(r"\b(eq|equation|Eq\.?)\b", re.IGNORECASE),
        re.compile(r"\d+\.\d+[eE][+-]?\d+"),  # scientific notation
    ]
    # Lines with multiple operators and short length are likely formulas
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) < 5:
            continue
        op_count = sum(1 for c in stripped if c in "=+-*/^")
        has_latex = bool(re.search(r"\\[a-zA-Z]+", stripped))
        has_eq_ref = bool(re.search(r"\(?\d+\)?\s*$", stripped))

        if (op_count >= 2 and len(stripped) < 200) or has_latex:
            confidence = "high" if has_latex or op_count >= 3 else "medium"
            formulas.append({"line": i + 1, "text": stripped, "confidence": confidence})

    return formulas


def _detect_method_sections(sections: list[dict]) -> list[dict]:
    """Identify sections likely describing numerical methods."""
    method_keywords = [
        "numerical", "method", "scheme", "discretization", "discretisation",
        "finite volume", "finite difference", "finite element", "flux",
        "reconstruction", "limiter", "riemann", "solver", "algorithm",
        "time integration", "runge-kutta", "euler", "tvd", "weno", "muscl",
        "approximate", "hll", "hllc", "roe", "rusanov", "lax",
    ]
    method_sections = []
    for sec in sections:
        title_lower = sec["title"].lower()
        if any(kw in title_lower for kw in method_keywords):
            method_sections.append(sec)
    return method_sections


def build_context(text_path: str, output_path: str) -> dict:
    """Build agent context from extracted text file.

    Returns metadata about the context generation.
    """
    if not os.path.isfile(text_path):
        raise FileNotFoundError(f"Text file not found: {text_path}")

    with open(text_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    total_chars = len(content)
    total_lines = len(lines)
    non_empty_lines = sum(1 for l in lines if l.strip())
    words = content.split()
    total_words = len(words)

    sections = _detect_sections(lines)
    formulas = _detect_formulas(lines)
    method_sections = _detect_method_sections(sections)

    # Detect extraction method from content
    extraction_method = "unknown"
    if content.startswith("--- Page"):
        extraction_method = "pypdf"
    elif "---" not in content[:200]:
        extraction_method = "pdftotext"

    # Build context file
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    ctx_lines = [
        f"# Paper Context: {Path(text_path).stem}",
        "",
        "## Source",
        f"- extracted text: {text_path}",
        f"- extraction method: {extraction_method}",
        "",
        "## Text Statistics",
        f"- total characters: {total_chars}",
        f"- total lines: {total_lines}",
        f"- non-empty lines: {non_empty_lines}",
        f"- total words: {total_words}",
        "",
        "## Section Headings",
    ]
    for sec in sections:
        ctx_lines.append(f"- L{sec['line']}: {sec['title']}")

    ctx_lines.append("")
    ctx_lines.append("## Suspected Method Sections")
    if method_sections:
        for sec in method_sections:
            ctx_lines.append(f"- L{sec['line']}: {sec['title']}")
    else:
        ctx_lines.append("- (none detected)")

    ctx_lines.append("")
    ctx_lines.append(f"## Suspected Formula Lines ({len(formulas)} detected)")
    for fm in formulas[:50]:  # cap at 50 to avoid huge files
        ctx_lines.append(f"- L{fm['line']} [{fm['confidence']}]: {fm['text'][:120]}")

    if len(formulas) > 50:
        ctx_lines.append(f"- ... and {len(formulas) - 50} more")

    ctx_lines.append("")
    ctx_lines.append("## Limitations")
    limitations = [
        "PDF text extraction may lose mathematical formulas (subscripts, superscripts, Greek letters).",
        "Table formatting is typically not preserved.",
        "Figure content is not extracted.",
        "Cross-references between equations are often broken.",
    ]
    if extraction_method == "pypdf":
        limitations.append("pypdf extraction may have incorrect column ordering for two-column papers.")
    if not method_sections:
        limitations.append("No method sections auto-detected — manual review required.")
    if len(formulas) < 5:
        limitations.append(
            "Very few formulas detected. The PDF may be scanned or formula-heavy with no text layer."
        )
    for lim in limitations:
        ctx_lines.append(f"- {lim}")

    ctx_lines.append("")
    ctx_lines.append("## Full Extracted Text")
    ctx_lines.append("")
    ctx_lines.append(content)

    Path(output_path).write_text("\n".join(ctx_lines), encoding="utf-8")

    return {
        "source": text_path,
        "output": output_path,
        "extraction_method": extraction_method,
        "total_chars": total_chars,
        "total_lines": total_lines,
        "non_empty_lines": non_empty_lines,
        "total_words": total_words,
        "sections_found": len(sections),
        "formulas_found": len(formulas),
        "method_sections_found": len(method_sections),
        "limitations": limitations,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Build agent context from extracted paper text."
    )
    parser.add_argument("text_path", help="Path to extracted text/markdown file")
    parser.add_argument(
        "--out",
        default=None,
        help="Output context file path (default: docs/paper_reviews/<stem>_context.md)",
    )
    args = parser.parse_args()

    text_path = args.text_path
    if args.out:
        output_path = args.out
    else:
        stem = Path(text_path).stem.replace("_text", "")
        output_path = f"docs/paper_reviews/{stem}_context.md"

    print(f"Building context from: {text_path}")
    print(f"Output path: {output_path}")

    result = build_context(text_path, output_path)

    print(f"Extraction method: {result['extraction_method']}")
    print(f"Total words: {result['total_words']}")
    print(f"Sections found: {result['sections_found']}")
    print(f"Formulas detected: {result['formulas_found']}")
    print(f"Method sections: {result['method_sections_found']}")
    print(f"Context written to: {output_path}")


if __name__ == "__main__":
    main()
