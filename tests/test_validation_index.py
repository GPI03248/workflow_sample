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
                "hll_l2": "1.073e-02",
                "rusanov_l2": "1.593e-02",
                "hll_rusanov_ratio": "0.6734",
            }
        ], "warnings": []}
        md = build_markdown(scan)
        assert "# Validation Index" in md
        assert "cfd_hll_validation" in md
        assert "0.6734" in md

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
