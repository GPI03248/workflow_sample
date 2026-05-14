"""Tests for paper-to-code tools: extract_pdf_text and build_paper_context."""

import importlib.util
import os
import sys
import tempfile

import pytest

# Import tools by loading them directly from file paths
_tools_dir = os.path.join(os.path.dirname(__file__), "..", "tools")


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_extract = _load_module("extract_pdf_text", os.path.join(_tools_dir, "extract_pdf_text.py"))
extract_pdf_text = _extract.extract_pdf_text
_check_binary_pdf = _extract._check_binary_pdf

_context = _load_module("build_paper_context", os.path.join(_tools_dir, "build_paper_context.py"))
build_context = _context.build_context
_detect_sections = _context._detect_sections
_detect_formulas = _context._detect_formulas


# --- extract_pdf_text tests ---

def test_extract_pdf_nonexistent_file_raises():
    """extract_pdf_text should raise FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError, match="PDF file not found"):
        extract_pdf_text("/nonexistent/path/paper.pdf", "/tmp/out.md")


def test_extract_pdf_non_pdf_file_raises():
    """extract_pdf_text should raise ValueError for non-PDF files."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        f.write("This is not a PDF file.")
        f.flush()
        try:
            with pytest.raises(ValueError, match="does not appear to be a valid PDF"):
                extract_pdf_text(f.name, "/tmp/out.md")
        finally:
            os.unlink(f.name)


def test_check_binary_pdf_rejects_text():
    """_check_binary_pdf should return None for non-PDF files."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="w") as f:
        f.write("plain text content")
        f.flush()
        try:
            result = _check_binary_pdf(f.name)
            assert result is None
        finally:
            os.unlink(f.name)


def test_check_binary_pdf_accepts_valid_header():
    """_check_binary_pdf should detect %PDF- header."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4 fake content")
        f.flush()
        try:
            result = _check_binary_pdf(f.name)
            assert result is not None
            assert result.startswith("%PDF-")
        finally:
            os.unlink(f.name)


def test_extract_pdf_returns_metadata_on_failure():
    """For a minimal PDF with no text, extraction should return structured metadata."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n")
        f.flush()
        try:
            result = extract_pdf_text(f.name, "/tmp/test_extract_out.md")
            assert "source" in result
            assert "methods_tried" in result
            assert isinstance(result["success"], bool)
            assert isinstance(result["warnings"], list)
        finally:
            os.unlink(f.name)


# --- build_paper_context tests ---

def test_build_context_from_text_file():
    """build_context should process a simple text file and produce output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        text_path = os.path.join(tmpdir, "test_text.md")
        output_path = os.path.join(tmpdir, "test_context.md")

        with open(text_path, "w") as f:
            f.write(
                "# Test Paper\n\n"
                "## Introduction\n\n"
                "Some intro text.\n\n"
                "## Numerical Method\n\n"
                "We use a finite volume scheme.\n"
                "F = 0.5 * (FL + FR) - alpha * (UR - UL)\n"
                "Eq. (1): u_t + f(u)_x = 0\n"
            )

        result = build_context(text_path, output_path)

        assert result["total_words"] > 0
        assert result["total_lines"] > 0
        assert result["non_empty_lines"] > 0
        assert result["sections_found"] >= 2
        assert os.path.isfile(output_path)

        with open(output_path) as f:
            content = f.read()
        assert "# Paper Context" in content
        assert "## Section Headings" in content
        assert "## Full Extracted Text" in content


def test_build_context_nonexistent_file_raises():
    """build_context should raise FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError, match="Text file not found"):
        build_context("/nonexistent/text.md", "/tmp/out.md")


def test_build_context_output_dir_created():
    """build_context should create output directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        text_path = os.path.join(tmpdir, "input.md")
        output_path = os.path.join(tmpdir, "subdir", "deep", "context.md")

        with open(text_path, "w") as f:
            f.write("# Minimal\n\nSome text.\n")

        build_context(text_path, output_path)
        assert os.path.isfile(output_path)


def test_detect_sections_markdown():
    """_detect_sections should find markdown headings."""
    lines = [
        "# Title",
        "",
        "## Section One",
        "Some content",
        "### Subsection",
        "More content",
        "## Section Two",
    ]
    sections = _detect_sections(lines)
    titles = [s["title"] for s in sections]
    assert "Title" in titles
    assert "Section One" in titles
    assert "Section Two" in titles


def test_detect_formulas_basic():
    """_detect_formulas should find lines with arithmetic operators."""
    lines = [
        "This is plain text.",
        "F = 0.5 * (FL + FR) - alpha * (UR - UL)",
        "u_t + f(u)_x = 0",
        "rho = p / (R * T)",
        "Another plain line.",
    ]
    formulas = _detect_formulas(lines)
    assert len(formulas) >= 2
    formula_texts = [f["text"] for f in formulas]
    assert any("FL + FR" in t for t in formula_texts)
    assert any("rho" in t for t in formula_texts)
