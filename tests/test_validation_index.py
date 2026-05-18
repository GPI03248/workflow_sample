"""Tests for tools/summarize_validation_results.py."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from summarize_validation_results import (
    _find_csv,
    _read_csv_rows,
    _has_analysis,
    _detect_methods,
    _extract_hll_comparison,
    scan_results,
    build_markdown,
)


class TestFindCsv:
    def test_finds_error_summary(self, tmp_path):
        (tmp_path / "error_summary.csv").write_text("a,b\n1,2\n")
        assert _find_csv(tmp_path) == "error_summary.csv"

    def test_finds_convergence_summary(self, tmp_path):
        (tmp_path / "convergence_summary.csv").write_text("a,b\n1,2\n")
        assert _find_csv(tmp_path) == "convergence_summary.csv"

    def test_returns_none_on_empty(self, tmp_path):
        assert _find_csv(tmp_path) is None


class TestReadCsvRows:
    def test_reads_valid_csv(self, tmp_path):
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("case,riemann\nentropy,rusanov\n")
        rows = _read_csv_rows(csv_path)
        assert len(rows) == 1
        assert rows[0]["case"] == "entropy"

    def test_returns_empty_for_missing(self, tmp_path):
        rows = _read_csv_rows(tmp_path / "nonexistent.csv")
        assert rows == []


class TestHasAnalysis:
    def test_has_analysis_md(self, tmp_path):
        (tmp_path / "analysis.md").write_text("# Analysis")
        assert _has_analysis(tmp_path) is True

    def test_has_convergence_analysis(self, tmp_path):
        (tmp_path / "convergence_analysis.md").write_text("# Analysis")
        assert _has_analysis(tmp_path) is True

    def test_missing_analysis(self, tmp_path):
        assert _has_analysis(tmp_path) is False


class TestDetectMethods:
    def test_detects_riemann(self):
        rows = [{"riemann": "hll"}, {"riemann": "rusanov"}]
        assert "hll" in _detect_methods(rows)
        assert "rusanov" in _detect_methods(rows)

    def test_empty_rows(self):
        assert _detect_methods([]) == "N/A"


class TestExtractHllComparison:
    """Tests for _extract_hll_comparison: case-aware row selection."""

    def _rows(self):
        """Rows matching actual results/cfd_hll_validation/error_summary.csv."""
        return [
            {"case": "entropy_wave", "riemann": "rusanov", "rho_l2_error": "1.5928720708e-02"},
            {"case": "uniform_flow", "riemann": "rusanov", "rho_l2_error": "0.0000000000e+00"},
            {"case": "entropy_wave", "riemann": "hll", "rho_l2_error": "1.0726734638e-02"},
            {"case": "uniform_flow", "riemann": "hll", "rho_l2_error": "0.0000000000e+00"},
        ]

    def test_prefers_entropy_wave_over_uniform_flow(self):
        warnings = []
        result = _extract_hll_comparison(self._rows(), warnings)
        assert result["hll_comparison_case"] == "entropy_wave"
        assert result["hll_l2"] == "1.0726734638e-02"
        assert result["rusanov_l2"] == "1.5928720708e-02"

    def test_computes_ratio(self):
        warnings = []
        result = _extract_hll_comparison(self._rows(), warnings)
        assert result["hll_rusanov_ratio"] == "0.6734"

    def test_no_uniform_flow_note_when_entropy_wave(self):
        warnings = []
        result = _extract_hll_comparison(self._rows(), warnings)
        assert "hll_comparison_note" not in result

    def test_falls_back_to_uniform_flow_with_note(self):
        rows = [
            {"case": "uniform_flow", "riemann": "rusanov", "rho_l2_error": "0.0"},
            {"case": "uniform_flow", "riemann": "hll", "rho_l2_error": "0.0"},
        ]
        warnings = []
        result = _extract_hll_comparison(rows, warnings)
        assert result["hll_comparison_case"] == "uniform_flow"
        assert "hll_comparison_note" in result

    def test_warns_when_no_matching_pair(self):
        rows = [
            {"case": "entropy_wave", "riemann": "rusanov", "rho_l2_error": "1e-3"},
        ]
        warnings = []
        result = _extract_hll_comparison(rows, warnings)
        assert "hll_comparison_case" not in result
        assert len(warnings) == 1

    def test_prefers_nonzero_error_case(self):
        rows = [
            {"case": "zero_case", "riemann": "rusanov", "rho_l2_error": "0.0"},
            {"case": "zero_case", "riemann": "hll", "rho_l2_error": "0.0"},
            {"case": "nonzero_case", "riemann": "rusanov", "rho_l2_error": "2e-3"},
            {"case": "nonzero_case", "riemann": "hll", "rho_l2_error": "1e-3"},
        ]
        warnings = []
        result = _extract_hll_comparison(rows, warnings)
        assert result["hll_comparison_case"] == "nonzero_case"
        assert result["hll_rusanov_ratio"] == "0.5000"

    def test_scan_results_includes_hll_comparison(self, tmp_path, monkeypatch):
        import summarize_validation_results as mod
        hll_dir = tmp_path / "cfd_hll_validation"
        hll_dir.mkdir()
        (hll_dir / "error_summary.csv").write_text(
            "case,riemann,rho_l2_error\n"
            "entropy_wave,rusanov,1.59e-02\n"
            "uniform_flow,rusanov,0.0\n"
            "entropy_wave,hll,1.07e-02\n"
            "uniform_flow,hll,0.0\n"
        )
        (hll_dir / "analysis.md").write_text("# HLL")
        monkeypatch.setattr(mod, "RESULTS_DIR", tmp_path)
        scan = scan_results()
        hll = [r for r in scan["results"] if "hll" in r["directory"]]
        assert len(hll) == 1
        assert hll[0]["hll_comparison_case"] == "entropy_wave"
        assert hll[0]["hll_l2"] == "1.07e-02"


class TestBuildMarkdown:
    def test_generates_markdown(self):
        scan = {"results": [
            {
                "directory": "results/cfd_hll_validation/",
                "result_type": "hll validation",
                "primary_csv": "error_summary.csv",
                "analysis_file": "yes",
                "methods": "hll, rusanov",
                "rows": 4,
                "status": "ok",
                "hll_comparison_case": "entropy_wave",
                "hll_l2": "1.073e-02",
                "rusanov_l2": "1.593e-02",
                "hll_rusanov_ratio": "0.6734",
            }
        ], "warnings": []}
        md = build_markdown(scan)
        assert "# Validation Index" in md
        assert "cfd_hll_validation" in md
        assert "0.6734" in md
        assert "entropy_wave" in md
        assert "Comparison case" in md

    def test_includes_warnings(self):
        scan = {"results": [], "warnings": ["Missing directory: foo"]}
        md = build_markdown(scan)
        assert "Missing" in md


class TestScanWithTempResults:
    def test_scans_temp_dir(self, tmp_path, monkeypatch):
        """Create a fake results dir and verify scan picks it up."""
        import summarize_validation_results as mod
        hll_dir = tmp_path / "cfd_hll_validation"
        hll_dir.mkdir()
        (hll_dir / "error_summary.csv").write_text(
            "case,riemann,rho_l2_error\nentropy,hll,1e-3\n"
        )
        (hll_dir / "analysis.md").write_text("# HLL")

        monkeypatch.setattr(mod, "RESULTS_DIR", tmp_path)
        scan = scan_results()
        assert len(scan["results"]) >= 1
        hll = [r for r in scan["results"] if "hll" in r["directory"]]
        assert len(hll) == 1
        assert hll[0]["status"] == "ok"

    def test_missing_dir_produces_warning(self, tmp_path, monkeypatch):
        import summarize_validation_results as mod
        monkeypatch.setattr(mod, "RESULTS_DIR", tmp_path)
        monkeypatch.setattr(mod, "KNOWN_DIRS", ["cfd_nonexistent"])
        scan = scan_results()
        assert any("Missing" in w for w in scan["warnings"])


class TestCLI:
    def test_json_output(self):
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "summarize_validation_results.py"), "--json"],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert "results" in data
        assert "warnings" in data

    def test_writes_file(self, tmp_path):
        out = tmp_path / "index.md"
        r = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "summarize_validation_results.py"),
             "--out", str(out)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        assert out.exists()
        assert "Validation Index" in out.read_text()
