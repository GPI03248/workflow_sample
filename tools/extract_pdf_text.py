"""Extract text content from a PDF file.

Tries multiple extraction methods in order:
1. pdftotext CLI (if available)
2. pypdf Python library (if available)
3. Direct binary read (last resort, limited)

Outputs a markdown or text file suitable for agent processing.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _try_pdftotext(pdf_path: str, output_path: str) -> bool:
    """Attempt extraction using the pdftotext CLI tool."""
    if shutil.which("pdftotext") is None:
        return False
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", pdf_path, output_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0 and os.path.getsize(output_path) > 0:
            return True
    except (subprocess.TimeoutExpired, OSError):
        pass
    return False


def _try_pypdf(pdf_path: str, output_path: str) -> bool:
    """Attempt extraction using the pypdf Python library."""
    try:
        from pypdf import PdfReader  # type: ignore[import-untyped]
    except ImportError:
        return False
    try:
        reader = PdfReader(pdf_path)
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages.append(f"--- Page {i + 1} ---\n{text}")
        if not pages:
            return False
        content = "\n\n".join(pages)
        Path(output_path).write_text(content, encoding="utf-8")
        return True
    except Exception:
        return False


def _check_binary_pdf(pdf_path: str) -> str | None:
    """Check if a file looks like a PDF by reading its header."""
    try:
        with open(pdf_path, "rb") as f:
            header = f.read(5)
        if header == b"%PDF-":
            return header.decode("ascii", errors="replace")
    except OSError:
        pass
    return None


def extract_pdf_text(pdf_path: str, output_path: str) -> dict:
    """Extract text from a PDF and write to output file.

    Returns a dict with extraction metadata.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    header = _check_binary_pdf(pdf_path)
    if header is None:
        raise ValueError(
            f"File does not appear to be a valid PDF: {pdf_path}\n"
            "Expected %PDF- header. The file may be corrupted or not a PDF."
        )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Try methods in order
    methods_tried = []

    methods_tried.append("pdftotext")
    if _try_pdftotext(pdf_path, output_path):
        return {
            "source": pdf_path,
            "output": output_path,
            "method": "pdftotext",
            "methods_tried": methods_tried,
            "success": True,
            "warnings": [],
        }

    methods_tried.append("pypdf")
    if _try_pypdf(pdf_path, output_path):
        return {
            "source": pdf_path,
            "output": output_path,
            "method": "pypdf",
            "methods_tried": methods_tried,
            "success": True,
            "warnings": [],
        }

    # No method succeeded
    warnings = [
        "Could not extract text from PDF.",
        "pdftotext CLI not available or failed.",
        "pypdf library not available or failed.",
        "",
        "Possible reasons:",
        "  - The PDF is a scanned document (image-based, no text layer).",
        "  - The PDF contains mathematical formulas rendered as images.",
        "  - Required tools are not installed.",
        "",
        "Recommended actions:",
        "  1. Install pdftotext: apt-get install poppler-utils",
        "  2. Install pypdf: pip install pypdf",
        "  3. For scanned PDFs: run OCR (e.g., tesseract) and provide the text.",
        "  4. Manually copy the paper's method section and save as .md or .txt.",
        "",
        "Then re-run this tool with the text file, or provide the text directly.",
    ]

    return {
        "source": pdf_path,
        "output": None,
        "method": None,
        "methods_tried": methods_tried,
        "success": False,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract text content from a PDF file."
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument(
        "--out",
        default=None,
        help="Output file path (default: docs/paper_reviews/<stem>_text.md)",
    )
    args = parser.parse_args()

    pdf_path = args.pdf_path
    if args.out:
        output_path = args.out
    else:
        stem = Path(pdf_path).stem
        output_path = f"docs/paper_reviews/{stem}_text.md"

    print(f"Extracting text from: {pdf_path}")
    print(f"Output path: {output_path}")

    result = extract_pdf_text(pdf_path, output_path)

    if result["success"]:
        print(f"Extraction succeeded using: {result['method']}")
        print(f"Output written to: {output_path}")
    else:
        print("Extraction FAILED.")
        for line in result["warnings"]:
            print(line)
        sys.exit(1)


if __name__ == "__main__":
    main()
