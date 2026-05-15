#!/usr/bin/env bash
# run_in_project_env.sh — non-interactive project environment wrapper
#
# Finds and activates conda without bash -ic, module-conda, or sourcing .bashrc.
# Falls back to current environment if conda is not found.
#
# Usage:
#   tools/run_in_project_env.sh python --version
#   tools/run_in_project_env.sh pytest -q
#   tools/run_in_project_env.sh python -m compileall solver cfd tests examples tools
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOCAL_CONFIG="$PROJECT_ROOT/.local/project_env.sh"

# --- Ensure local config exists ---
if [ ! -f "$LOCAL_CONFIG" ]; then
    echo "[run_in_project_env] Generating .local/project_env.sh ..." >&2
    python3 "$SCRIPT_DIR/discover_project_env.py" --write-local-config >&2 || true
fi

# --- Source local config ---
if [ -f "$LOCAL_CONFIG" ]; then
    # shellcheck source=/dev/null
    source "$LOCAL_CONFIG"
fi

# --- Activate conda if available ---
if [ -n "${PROJECT_CONDA_SH:-}" ] && [ -f "$PROJECT_CONDA_SH" ]; then
    # shellcheck source=/dev/null
    source "$PROJECT_CONDA_SH"
    conda activate "${PROJECT_CONDA_ENV:-base}" 2>/dev/null || true
    echo "[run_in_project_env] conda activated: ${PROJECT_CONDA_ENV:-base} ($PROJECT_CONDA_SH)" >&2
else
    echo "[run_in_project_env] WARNING: conda.sh not found, using current environment" >&2
fi

# --- Ensure project root is on PYTHONPATH ---
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"

# --- Diagnostics ---
echo "[run_in_project_env] python: $(command -v python3 2>/dev/null || echo 'not found')" >&2
echo "[run_in_project_env] version: $(python3 --version 2>/dev/null || echo 'unknown')" >&2

# --- Execute ---
exec "$@"
