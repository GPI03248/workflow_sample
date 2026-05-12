#!/usr/bin/env bash
# quick-check.sh
# Hook: PostToolUse — quick syntax and test check after file edits.

set -euo pipefail

project_dir="$(cd "$(dirname "$0")/../.." && pwd)"

echo "[quick-check] Running compile check on solver/ and tests/..."
cd "$project_dir"
python -m compileall solver tests -q 2>&1 || {
    echo "[quick-check] FAIL: compile error detected."
    exit 0  # Don't block — just report.
}

# Run pytest if available.
if command -v pytest &>/dev/null; then
    echo "[quick-check] Running pytest -q ..."
    pytest -q 2>&1 || {
        echo "[quick-check] FAIL: some tests failed."
        exit 0  # Don't block — just report.
    }
else
    echo "[quick-check] pytest not found — skipping tests."
fi

echo "[quick-check] OK."
exit 0
