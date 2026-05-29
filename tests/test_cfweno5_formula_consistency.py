"""Tests for tools/check_cfweno5_formula_consistency.py.

NOTE: The default tool exit code is based on required scalar-linear targets:
the three Appendix A substencils plus Appendix A's direct full-stencil target.
The Eq. (16) / Table I WENO-combination path remains diagnostic-only and is
reported separately because it still fails to reach 5th order.
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
    result = _run_tool("--quick", "--json")
    data = json.loads(result.stdout)
    assert "substencils" in data
    assert "full_target" in data
    assert "combined" in data
    assert "all_passed" in data
    assert "policy_decision" in data
    assert "diagnostic_failures" in data
    assert "failures" in data
    assert "summary" in data
    # Quick mode should have 3 resolutions
    assert len(data["resolutions"]) == 3


# --- Quick mode ---

def test_quick_mode():
    """Quick mode returns results faster with fewer resolutions."""
    result = _run_tool("--quick")
    assert "CFWENO5 Substencil Consistency Check" in result.stdout
    assert "Required result:" in result.stdout


# --- All substencils are reported ---

def test_all_substencils_reported():
    """All three Table I substencils (s0, s1, s2) appear in output."""
    result = _run_tool("--quick")
    for name in ["s0", "s1", "s2"]:
        assert name in result.stdout, f"{name} not found in output"


def test_appendix_a_full_target_reported_and_passes():
    """Appendix A's direct full-stencil target is reported separately."""
    result = _run_tool("--quick", "--json")
    data = json.loads(result.stdout)
    full = data["full_target"]
    assert full["name"] == "appendix_A_full_target"
    assert full["passed"] is True
    assert full["observed_order"] >= 5.0


# --- Combined scheme is reported ---

def test_combined_scheme_reported():
    """Eq. (16) / Table I WENO-combination diagnostic appears in output."""
    result = _run_tool("--quick")
    assert "comb" in result.stdout
    assert "diagnostic-only Eq. (16) Table I" in result.stdout


# --- s2 passes (corrected in v1.3-pre.8 — 1/2 factor moved to second term) ---

def test_s2_passes_consistency():
    """s2 substencil PASSES consistency check after v1.3-pre.8 correction."""
    result = _run_tool("--quick", "--json")
    data = json.loads(result.stdout)
    s2 = [r for r in data["substencils"] if r["name"] == "s2"][0]
    assert s2["passed"] is True, (
        f"s2 should PASS after correction. "
        f"observed_order={s2['observed_order']}, expected ~4.0"
    )
    assert "s2" not in data["failures"]


# --- Combined scheme fails (known issue from failed implementation) ---

def test_combined_fails_consistency():
    """Eq. (16) / Table I WENO combination still FAILS consistency."""
    result = _run_tool("--quick", "--json")
    data = json.loads(result.stdout)
    assert data["combined"]["passed"] is False, (
        f"Table I combined diagnostic should FAIL but passed. "
        f"observed_order={data['combined']['observed_order']}, expected ~5.0"
    )


# --- s0 and s1 pass (they were individually correct) ---

def test_s0_passes():
    """s0 substencil passes individual consistency check."""
    result = _run_tool("--quick", "--json")
    data = json.loads(result.stdout)
    s0 = [r for r in data["substencils"] if r["name"] == "s0"][0]
    assert s0["passed"] is True, (
        f"s0 should PASS. observed_order={s0['observed_order']}"
    )


def test_s1_passes():
    """s1 substencil passes individual consistency check."""
    result = _run_tool("--quick", "--json")
    data = json.loads(result.stdout)
    s1 = [r for r in data["substencils"] if r["name"] == "s1"][0]
    assert s1["passed"] is True, (
        f"s1 should PASS. observed_order={s1['observed_order']}"
    )


# --- Exit code reflects failures ---

def test_exit_code_zero_when_required_targets_pass():
    """Tool returns zero when required scalar-linear targets pass."""
    result = _run_tool("--quick")
    assert result.returncode == 0, (
        f"Expected exit code 0, got {result.returncode}"
    )


# --- CFL parameter is respected ---

def test_cfl_parameter():
    """Custom CFL parameter is used."""
    result = _run_tool("--quick", "--cfl", "0.3", "--json")
    data = json.loads(result.stdout)
    assert data["cfl"] == 0.3


# --- Edge case: all observed orders are finite numbers ---

def test_observed_orders_are_finite():
    """All observed orders are finite numbers (not None, not NaN)."""
    result = _run_tool("--quick", "--json")
    data = json.loads(result.stdout)
    for r in data["substencils"]:
        assert r["observed_order"] is not None, (
            f"{r['name']}: observed_order is None"
        )
        assert isinstance(r["observed_order"], (int, float)), (
            f"{r['name']}: observed_order is not numeric"
        )
    assert data["full_target"]["observed_order"] is not None
    assert isinstance(data["full_target"]["observed_order"], (int, float))
    assert data["combined"]["observed_order"] is not None
    assert isinstance(data["combined"]["observed_order"], (int, float))


# --- Weight diagnosis mode ---

def test_diagnose_weights_json_output():
    """Weight diagnosis JSON is parseable and contains expected keys."""
    result = _run_tool("--diagnose-weights", "--quick", "--json")
    data = json.loads(result.stdout)
    assert "cfweno3_baseline" in data
    assert "variants" in data
    assert "cfl" in data
    assert "resolutions" in data
    assert len(data["variants"]) == 6


def test_diagnose_weights_all_variants_reported():
    """All weight/target diagnostic variants appear in diagnosis output."""
    result = _run_tool("--diagnose-weights", "--quick", "--json")
    data = json.loads(result.stdout)
    variant_names = {v["name"] for v in data["variants"]}
    expected = {
        "current_table_I_raw",
        "table_I_normalized",
        "table_II_raw",
        "table_II_normalized",
        "equal_weights_debug",
        "appendix_A_full_target",
    }
    assert variant_names == expected, f"Missing variants: {expected - variant_names}"


def test_diagnose_weights_cfweno3_baseline_passes():
    """CFWENO3 baseline passes in diagnosis mode (infrastructure sanity)."""
    result = _run_tool("--diagnose-weights", "--quick", "--json")
    data = json.loads(result.stdout)
    assert data["cfweno3_baseline"]["passed"] is True, (
        f"CFWENO3 baseline should PASS. "
        f"observed_order={data['cfweno3_baseline']['observed_order']}"
    )


def test_diagnose_weights_exit_zero():
    """Weight diagnosis always exits 0 (diagnostic mode, not pass/fail)."""
    result = _run_tool("--diagnose-weights", "--quick")  # no expect_fail
    assert result.returncode == 0, (
        f"Diagnosis mode should always exit 0, got {result.returncode}"
    )


def test_diagnose_weights_variants_have_required_fields():
    """Each variant has target/source, optional weight_sum, and description fields."""
    result = _run_tool("--diagnose-weights", "--quick", "--json")
    data = json.loads(result.stdout)
    for v in data["variants"]:
        assert "weight_source" in v, f"{v['name']}: missing weight_source"
        assert "weight_sum" in v, f"{v['name']}: missing weight_sum"
        assert "description" in v, f"{v['name']}: missing description"
        assert isinstance(v["observed_order"], (int, float)), (
            f"{v['name']}: observed_order is not numeric"
        )


def test_diagnose_weights_table_I_raw_weight_sum():
    """Table I raw weights sum to (4-nu+nu^2)/6 at nu=0.5 = 0.625."""
    result = _run_tool("--diagnose-weights", "--cfl", "0.5", "--quick", "--json")
    data = json.loads(result.stdout)
    raw = [v for v in data["variants"] if v["name"] == "current_table_I_raw"][0]
    # (4 - 0.5 + 0.25)/6 = 3.75/6 = 0.625
    assert raw["weight_sum"] == 0.625, (
        f"Table I raw weight sum should be 0.625 at nu=0.5, got {raw['weight_sum']}"
    )


def test_diagnose_weights_table_I_normalized_weight_sum():
    """Table I normalized weights sum to 1.0."""
    result = _run_tool("--diagnose-weights", "--cfl", "0.5", "--quick", "--json")
    data = json.loads(result.stdout)
    norm = [v for v in data["variants"] if v["name"] == "table_I_normalized"][0]
    assert norm["weight_sum"] == 1.0, (
        f"Table I normalized weight sum should be 1.0, got {norm['weight_sum']}"
    )


def test_diagnose_weights_equal_baseline():
    """Equal weights (1/3 each) is present as baseline."""
    result = _run_tool("--diagnose-weights", "--quick", "--json")
    data = json.loads(result.stdout)
    eq = [v for v in data["variants"] if v["name"] == "equal_weights_debug"][0]
    assert eq["weight_sum"] == 1.0


def test_diagnose_weights_appendix_a_full_target_passes():
    """The direct Appendix A full target passes as a diagnostic target."""
    result = _run_tool("--diagnose-weights", "--quick", "--json")
    data = json.loads(result.stdout)
    full = [v for v in data["variants"] if v["name"] == "appendix_A_full_target"][0]
    assert full["passed"] is True
    assert full["observed_order"] >= 5.0
    assert full["weight_sum"] is None


def test_policy_marks_table_I_combined_diagnostic_only():
    """The unresolved Eq. (16) / Table I path is diagnostic-only."""
    result = _run_tool("--quick", "--json")
    data = json.loads(result.stdout)
    assert data["policy_decision"] == "A_direct_appendix_a_target"
    assert "cfweno5_table_I_combined" in data["diagnostic_only_targets"]
    assert "cfweno5_table_I_combined" in data["diagnostic_failures"]
    assert data["all_passed"] is True
