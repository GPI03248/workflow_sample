"""Tests for tools/check_cfweno5_formula_consistency.py.

NOTE: The tool currently returns exit code 1 because s2 and cfweno5_combined
fail consistency (known issue from failed CFWENO5 implementation). Most tests
use expect_fail=True to account for this. When the Appendix A formulas are
re-verified and corrected, these tests should be updated to use expect_fail=False.
"""

import json
import subprocess
import sys
from pathlib import Path

TOOL = Path("tools/check_cfweno5_formula_consistency.py")


def _run_tool(*args, expect_fail=False):
    """Run the consistency checker tool and return CompletedProcess.

    Parameters
    ----------
    *args : str
        Arguments to pass to the tool.
    expect_fail : bool
        If True, non-zero exit code is expected and does not raise.
    """
    cmd = [sys.executable, str(TOOL)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if not expect_fail and result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise AssertionError(
            f"Tool failed with return code {result.returncode}"
        )
    return result


# --- Tool can be invoked ---

def test_tool_help():
    """Tool can be invoked."""
    result = _run_tool("--help")
    assert "usage" in result.stdout.lower() or "CFWENO5" in result.stdout


# --- JSON output ---

def test_json_output():
    """JSON output is parseable and contains expected keys."""
    result = _run_tool("--quick", "--json", expect_fail=True)
    data = json.loads(result.stdout)
    assert "substencils" in data
    assert "combined" in data
    assert "all_passed" in data
    assert "failures" in data
    assert "summary" in data
    # Quick mode should have 3 resolutions
    assert len(data["resolutions"]) == 3


# --- Quick mode ---

def test_quick_mode():
    """Quick mode returns results faster with fewer resolutions."""
    result = _run_tool("--quick", expect_fail=True)
    assert "CFWENO5 Substencil Consistency Check" in result.stdout
    assert "Result:" in result.stdout


# --- All substencils are reported ---

def test_all_substencils_reported():
    """All four substencils (s0, s1, s2, s3) appear in output."""
    result = _run_tool("--quick", expect_fail=True)
    for name in ["s0", "s1", "s2", "s3"]:
        assert name in result.stdout, f"{name} not found in output"


# --- Combined scheme is reported ---

def test_combined_scheme_reported():
    """Combined CFWENO5 scheme appears in output."""
    result = _run_tool("--quick", expect_fail=True)
    assert "comb" in result.stdout


# --- s2 fails (known issue from failed implementation) ---

def test_s2_fails_consistency():
    """s2 substencil FAILS consistency check (known issue)."""
    result = _run_tool("--quick", "--json", expect_fail=True)
    data = json.loads(result.stdout)
    s2 = [r for r in data["substencils"] if r["name"] == "s2"][0]
    assert s2["passed"] is False, (
        f"s2 should FAIL consistency check but passed. "
        f"observed_order={s2['observed_order']}, expected ~4.0"
    )
    assert "s2" in data["failures"]


# --- Combined scheme fails (known issue from failed implementation) ---

def test_combined_fails_consistency():
    """Combined CFWENO5 FAILS consistency check (known issue)."""
    result = _run_tool("--quick", "--json", expect_fail=True)
    data = json.loads(result.stdout)
    assert data["combined"]["passed"] is False, (
        f"Combined scheme should FAIL but passed. "
        f"observed_order={data['combined']['observed_order']}, expected ~5.0"
    )


# --- s0 and s1 pass (they were individually correct) ---

def test_s0_passes():
    """s0 substencil passes individual consistency check."""
    result = _run_tool("--quick", "--json", expect_fail=True)
    data = json.loads(result.stdout)
    s0 = [r for r in data["substencils"] if r["name"] == "s0"][0]
    assert s0["passed"] is True, (
        f"s0 should PASS. observed_order={s0['observed_order']}"
    )


def test_s1_passes():
    """s1 substencil passes individual consistency check."""
    result = _run_tool("--quick", "--json", expect_fail=True)
    data = json.loads(result.stdout)
    s1 = [r for r in data["substencils"] if r["name"] == "s1"][0]
    assert s1["passed"] is True, (
        f"s1 should PASS. observed_order={s1['observed_order']}"
    )


# --- Exit code reflects failures ---

def test_exit_code_nonzero_on_failure():
    """Tool returns non-zero exit code when consistency checks fail."""
    result = _run_tool("--quick", expect_fail=True)
    assert result.returncode == 1, (
        f"Expected exit code 1, got {result.returncode}"
    )


# --- CFL parameter is respected ---

def test_cfl_parameter():
    """Custom CFL parameter is used."""
    result = _run_tool("--quick", "--cfl", "0.3", "--json", expect_fail=True)
    data = json.loads(result.stdout)
    assert data["cfl"] == 0.3


# --- Edge case: all observed orders are finite numbers ---

def test_observed_orders_are_finite():
    """All observed orders are finite numbers (not None, not NaN)."""
    result = _run_tool("--quick", "--json", expect_fail=True)
    data = json.loads(result.stdout)
    for r in data["substencils"]:
        assert r["observed_order"] is not None, (
            f"{r['name']}: observed_order is None"
        )
        assert isinstance(r["observed_order"], (int, float)), (
            f"{r['name']}: observed_order is not numeric"
        )
    assert data["combined"]["observed_order"] is not None
    assert isinstance(data["combined"]["observed_order"], (int, float))
