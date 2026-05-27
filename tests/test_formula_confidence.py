"""Tests for tools/check_formula_confidence.py."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

TOOL = Path("tools/check_formula_confidence.py")
CFWENO5_INVENTORY = Path("docs/formula_inventories/cfweno5_scalar_formulas.yml")


def _run_tool(*args, expect_fail=False):
    """Run the checker tool and return CompletedProcess."""
    cmd = [sys.executable, str(TOOL)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not expect_fail and result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise AssertionError(f"Tool failed with return code {result.returncode}")
    return result


def _write_inventory(formulas, metadata=None):
    """Write a temp inventory file and return its path."""
    data = {
        "metadata": metadata or {"paper_id": "test"},
        "formulas": formulas,
    }
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False)
    yaml.dump(data, f)
    f.close()
    return f.name


# --- Test: read CFWENO5 inventory ---

def test_read_cfweno5_inventory():
    """Checker can read the real CFWENO5 inventory."""
    result = _run_tool(str(CFWENO5_INVENTORY))
    assert "Total:" in result.stdout
    assert "High:" in result.stdout


# --- Test: JSON output ---

def test_json_output():
    """JSON output is parseable."""
    inv = _write_inventory([
        {
            "formula_id": "test_weight",
            "paper_id": "test",
            "source": {"section": "Table I", "page": 5},
            "formula_type": "weight",
            "expression": "nu/2",
            "extraction_method": "human",
            "confidence": "high",
            "verification_status": "verified",
            "used_by": ["spec.md"],
            "implementation_relevance": "required",
            "blocks_implementation": False,
            "notes": "test",
        }
    ])
    result = _run_tool(inv, "--json")
    data = json.loads(result.stdout)
    assert data["valid"] is True
    assert data["summary"]["total"] == 1
    assert data["summary"]["high"] == 1


# --- Test: strict mode fails on medium confidence required formula ---

def test_strict_fails_on_medium_confidence():
    """Strict mode returns non-zero when a required formula is medium confidence."""
    inv = _write_inventory([
        {
            "formula_id": "blocked_formula",
            "paper_id": "test",
            "source": {"section": "A", "page": 1},
            "formula_type": "stencil",
            "expression": None,
            "extraction_method": "pdftotext",
            "confidence": "medium",
            "verification_status": "partial",
            "used_by": ["spec.md"],
            "implementation_relevance": "required",
            "blocks_implementation": True,
            "notes": "test",
        }
    ])
    result = _run_tool(inv, "--require-high-for-implementation", expect_fail=True)
    assert result.returncode != 0
    assert "STRICT CHECK FAILED" in result.stdout


# --- Test: high confidence non-blocking passes ---

def test_high_confidence_passes():
    """High confidence, verified, required formula passes strict mode."""
    inv = _write_inventory([
        {
            "formula_id": "good_formula",
            "paper_id": "test",
            "source": {"section": "Table I", "page": 5},
            "formula_type": "weight",
            "expression": "nu/2",
            "extraction_method": "human",
            "confidence": "high",
            "verification_status": "verified",
            "used_by": ["spec.md"],
            "implementation_relevance": "required",
            "blocks_implementation": False,
            "notes": "test",
        }
    ])
    result = _run_tool(inv, "--require-high-for-implementation")
    assert "STRICT CHECK PASSED" in result.stdout


# --- Test: missing required field fails ---

def test_missing_field_fails():
    """Inventory with missing required field returns non-zero."""
    inv = _write_inventory([
        {
            "formula_id": "incomplete",
            # missing many required keys
            "confidence": "high",
        }
    ])
    result = _run_tool(inv, expect_fail=True)
    assert result.returncode != 0


# --- Test: markdown report generation ---

def test_markdown_report():
    """Markdown report can be generated."""
    inv = _write_inventory([
        {
            "formula_id": "test_formula",
            "paper_id": "test",
            "source": {"section": "Eq 1", "page": 1},
            "formula_type": "weight",
            "expression": "nu",
            "extraction_method": "human",
            "confidence": "high",
            "verification_status": "verified",
            "used_by": ["spec.md"],
            "implementation_relevance": "optional",
            "blocks_implementation": False,
            "notes": "test",
        }
    ])
    with tempfile.TemporaryDirectory() as td:
        report_path = str(Path(td) / "report.md")
        result = _run_tool(inv, f"--markdown-report={report_path}")
        report = Path(report_path).read_text()
        assert "# Formula Confidence Report" in report
        assert "High Confidence" in report


# --- Test: CFWENO5 inventory has 2 blocking items (after Appendix A demotion) ---

def test_cfweno5_has_blocking_items():
    """After Appendix A demotion, the CFWENO5 inventory has 2 blocking formulas."""
    result = _run_tool(str(CFWENO5_INVENTORY), expect_fail=True)
    assert "Blocking:" in result.stdout
    for line in result.stdout.split("\n"):
        if line.strip().startswith("Blocking:"):
            count_str = line.split("Blocking:")[-1].strip()
            assert int(count_str) == 2, f"Expected 2 blocking, got {count_str}"


# --- Test: checker does not modify inventory ---

def test_checker_does_not_modify_inventory():
    """Reading inventory does not modify the file."""
    original = CFWENO5_INVENTORY.read_text()
    _run_tool(str(CFWENO5_INVENTORY))
    after = CFWENO5_INVENTORY.read_text()
    assert original == after


# --- Test: CFWENO5 strict mode fails (after Appendix A demotion) ---

def test_cfweno5_strict_fails():
    """CFWENO5 strict check FAILS after Appendix A formulas demoted."""
    result = _run_tool(
        str(CFWENO5_INVENTORY),
        "--require-high-for-implementation",
        expect_fail=True,
    )
    assert result.returncode != 0
    assert "STRICT CHECK FAILED" in result.stdout
    # Should mention consistency_status failures
    assert "consistency_status=failed" in result.stdout


# --- Test: derived verification status is valid ---

def test_derived_verification_status():
    """The 'derived' verification status is accepted by the checker."""
    inv = _write_inventory([
        {
            "formula_id": "derived_formula",
            "paper_id": "test",
            "source": {"section": "Appendix A", "page": 24},
            "formula_type": "stencil",
            "expression": None,
            "extraction_method": "derived from verified source",
            "confidence": "medium",
            "verification_status": "derived",
            "used_by": ["spec.md"],
            "implementation_relevance": "optional",
            "blocks_implementation": False,
            "notes": "Derived from verified formula",
        }
    ])
    result = _run_tool(inv, "--json")
    data = json.loads(result.stdout)
    assert data["valid"] is True


# --- Test: optional formula does not block strict check ---

def test_optional_formula_does_not_block_strict():
    """An optional formula with medium confidence does not fail strict check."""
    inv = _write_inventory([
        {
            "formula_id": "required_good",
            "paper_id": "test",
            "source": {"section": "Table I", "page": 5},
            "formula_type": "weight",
            "expression": "nu/2",
            "extraction_method": "human",
            "confidence": "high",
            "verification_status": "verified",
            "used_by": ["spec.md"],
            "implementation_relevance": "required",
            "blocks_implementation": False,
            "consistency_status": "not_run",
            "notes": "test",
        },
        {
            "formula_id": "optional_medium",
            "paper_id": "test",
            "source": {"section": "Appendix A", "page": 24},
            "formula_type": "stencil",
            "expression": None,
            "extraction_method": "derived",
            "confidence": "medium",
            "verification_status": "derived",
            "used_by": ["spec.md"],
            "implementation_relevance": "optional",
            "blocks_implementation": False,
            "consistency_status": "not_required",
            "notes": "Optional, derived from verified formula",
        }
    ])
    result = _run_tool(inv, "--require-high-for-implementation")
    assert "STRICT CHECK PASSED" in result.stdout


# --- Test: consistency_status=failed blocks strict check ---

def test_consistency_failed_blocks_strict():
    """A required formula with consistency_status=failed blocks strict check."""
    inv = _write_inventory([
        {
            "formula_id": "high_but_failed",
            "paper_id": "test",
            "source": {"section": "A", "page": 1},
            "formula_type": "stencil",
            "expression": "inline",
            "extraction_method": "pdftotext",
            "confidence": "high",
            "verification_status": "verified",
            "used_by": ["spec.md"],
            "implementation_relevance": "required",
            "blocks_implementation": True,
            "consistency_status": "failed",
            "notes": "High confidence but failed numerical consistency",
        }
    ])
    result = _run_tool(inv, "--require-high-for-implementation", expect_fail=True)
    assert result.returncode != 0
    assert "STRICT CHECK FAILED" in result.stdout
    assert "consistency_status=failed" in result.stdout


# --- Test: failed_validation verification status is valid ---

def test_failed_validation_status_accepted():
    """The 'failed_validation' verification status is accepted by the checker."""
    inv = _write_inventory([
        {
            "formula_id": "failed_formula",
            "paper_id": "test",
            "source": {"section": "Appendix A", "page": 24},
            "formula_type": "stencil",
            "expression": None,
            "extraction_method": "pdftotext",
            "confidence": "medium",
            "verification_status": "failed_validation",
            "used_by": ["spec.md"],
            "implementation_relevance": "required",
            "blocks_implementation": True,
            "consistency_status": "failed",
            "notes": "Failed numerical validation",
        }
    ])
    result = _run_tool(inv, "--json")
    data = json.loads(result.stdout)
    assert data["valid"] is True
    assert data["summary"]["blocking_count"] == 1


# --- Test: consistency_status=not_run does not block ---

def test_consistency_not_run_does_not_block():
    """consistency_status=not_run does NOT block (only 'failed' blocks)."""
    inv = _write_inventory([
        {
            "formula_id": "not_run_formula",
            "paper_id": "test",
            "source": {"section": "Table I", "page": 5},
            "formula_type": "weight",
            "expression": "nu/2",
            "extraction_method": "human",
            "confidence": "high",
            "verification_status": "verified",
            "used_by": ["spec.md"],
            "implementation_relevance": "required",
            "blocks_implementation": False,
            "consistency_status": "not_run",
            "notes": "Not yet checked",
        }
    ])
    result = _run_tool(inv, "--require-high-for-implementation")
    assert "STRICT CHECK PASSED" in result.stdout


# --- Test: consistency_status=passed does not block ---

def test_consistency_passed_does_not_block():
    """consistency_status=passed does NOT block strict check."""
    inv = _write_inventory([
        {
            "formula_id": "passed_formula",
            "paper_id": "test",
            "source": {"section": "A", "page": 1},
            "formula_type": "stencil",
            "expression": "inline",
            "extraction_method": "human",
            "confidence": "high",
            "verification_status": "verified",
            "used_by": ["spec.md"],
            "implementation_relevance": "required",
            "blocks_implementation": False,
            "consistency_status": "passed",
            "notes": "All good",
        }
    ])
    result = _run_tool(inv, "--require-high-for-implementation")
    assert "STRICT CHECK PASSED" in result.stdout
