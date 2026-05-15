"""Discover the project's conda environment without interactive shells.

Finds conda.sh using a priority chain:
  1. Explicit env vars (WORKFLOW_SAMPLE_CONDA_SH)
  2. Local config (.local/project_env.sh)
  3. conda on PATH
  4. Common install locations
  5. Parsed shell startup files (recursive, read-only)

Never executes user shell files.  Never uses bash -ic or module-conda.

Usage:
    python tools/discover_project_env.py             # human report
    python tools/discover_project_env.py --json       # JSON output
    python tools/discover_project_env.py --print-shell # shell assignments
    python tools/discover_project_env.py --write-local-config  # write .local/
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_CONFIG = PROJECT_ROOT / ".local" / "project_env.sh"

MAX_SOURCE_DEPTH = 5

# Common conda locations to scan
_COMMON_LOCATIONS = [
    "miniconda3", "anaconda3", "mambaforge", "miniforge3",
]

_COMMON_PREFIXES = [
    "$HOME", "$HOME/Apps", "$HOME/.local", "/opt",
]


def _expand(path_str: str) -> str:
    """Expand $HOME, ~, and environment variables."""
    path_str = os.path.expanduser(path_str)
    path_str = os.path.expandvars(path_str)
    return path_str


def _priority1_env_vars() -> dict | None:
    """Priority 1: explicit environment variables."""
    conda_sh = os.environ.get("WORKFLOW_SAMPLE_CONDA_SH")
    if conda_sh:
        conda_sh = _expand(conda_sh)
        if Path(conda_sh).is_file():
            return {
                "conda_sh": conda_sh,
                "conda_env": os.environ.get("WORKFLOW_SAMPLE_CONDA_ENV", "base"),
                "source": "explicit_env_var",
            }
    return None


def _priority2_local_config() -> dict | None:
    """Priority 2: existing .local/project_env.sh."""
    if not LOCAL_CONFIG.is_file():
        return None
    conda_sh = None
    conda_env = "base"
    discovery_source = "local_config"
    for line in LOCAL_CONFIG.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^PROJECT_CONDA_SH\s*=\s*'([^']*)'", line)
        if m:
            conda_sh = m.group(1)
        m = re.match(r"^PROJECT_CONDA_ENV\s*=\s*'([^']*)'", line)
        if m:
            conda_env = m.group(1)
        m = re.match(r"^PROJECT_ENV_DISCOVERY_SOURCE\s*=\s*'([^']*)'", line)
        if m:
            discovery_source = m.group(1)
    if conda_sh and Path(conda_sh).is_file():
        return {
            "conda_sh": conda_sh,
            "conda_env": conda_env,
            "source": f"local_config({discovery_source})",
        }
    return None


def _priority3_conda_on_path() -> dict | None:
    """Priority 3: conda executable on PATH."""
    conda_exe = os.environ.get("CONDA_EXE")
    if not conda_exe:
        # Try to find conda in PATH
        import shutil
        conda_exe = shutil.which("conda")
    if not conda_exe or not Path(conda_exe).is_file():
        return None
    try:
        base = subprocess.check_output(
            [conda_exe, "info", "--base"],
            stderr=subprocess.DEVNULL,
            timeout=10,
        ).decode().strip()
        conda_sh = str(Path(base) / "etc" / "profile.d" / "conda.sh")
        if Path(conda_sh).is_file():
            return {
                "conda_sh": conda_sh,
                "conda_env": os.environ.get("CONDA_DEFAULT_ENV", "base"),
                "source": "conda_on_path",
            }
    except Exception:
        pass
    return None


def _priority4_common_locations() -> dict | None:
    """Priority 4: scan common conda install locations."""
    home = Path.home()
    prefixes = [home, home / "Apps", home / ".local", Path("/opt")]
    for prefix in prefixes:
        for dist in _COMMON_LOCATIONS:
            candidate = prefix / dist / "etc" / "profile.d" / "conda.sh"
            if candidate.is_file():
                return {
                    "conda_sh": str(candidate),
                    "conda_env": "base",
                    "source": "common_location",
                }
    return None


def _parse_shell_file(path: Path, depth: int = 0, visited: set | None = None) -> list[str]:
    """Parse a shell file to find conda.sh references.

    Recursively follows source/. statements up to MAX_SOURCE_DEPTH.
    Returns list of candidate conda.sh paths found.
    """
    if visited is None:
        visited = set()
    resolved = str(path.resolve())
    if resolved in visited or depth > MAX_SOURCE_DEPTH:
        return []
    visited.add(resolved)

    if not path.is_file():
        return []

    candidates = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    for line in text.splitlines():
        stripped = line.strip()
        # Skip comments
        if stripped.startswith("#"):
            continue

        # Look for conda.sh references
        for m in re.finditer(r"([^\s;|&'\"<>]+/conda\.sh)", stripped):
            found = _expand(m.group(1))
            if Path(found).is_file():
                candidates.append(found)

        # Look for */bin/conda and derive conda.sh
        for m in re.finditer(r"([^\s;|&'\"<>]+)/bin/conda", stripped):
            bin_conda = _expand(m.group(1))
            derived = str(Path(bin_conda).parent.parent / "etc" / "profile.d" / "conda.sh")
            if Path(derived).is_file():
                candidates.append(derived)

        # Follow source / . statements
        for m in re.finditer(r"^(?:source|\.)\s+([^\s;|&]+)", stripped, re.MULTILINE):
            target = _expand(m.group(1).strip("\"'"))
            if target:
                candidates.extend(
                    _parse_shell_file(Path(target), depth + 1, visited)
                )

    return candidates


def _priority5_shell_startup() -> dict | None:
    """Priority 5: parse shell startup files for conda.sh."""
    home = Path.home()
    startup_files = [
        home / ".bashrc",
        home / ".bash_profile",
        home / ".profile",
    ]
    for sf in startup_files:
        if not sf.is_file():
            continue
        candidates = _parse_shell_file(sf)
        if candidates:
            return {
                "conda_sh": candidates[0],
                "conda_env": "base",
                "source": "parsed_shell_config",
            }
    return None


def discover_conda() -> dict:
    """Run the full discovery priority chain.

    Returns
    -------
    dict
        Keys: found (bool), conda_sh (str|None), conda_env (str),
        source (str|None), warnings (list[str]).
    """
    warnings = []
    candidates_tried = []

    for name, finder in [
        ("explicit_env_var", _priority1_env_vars),
        ("local_config", _priority2_local_config),
        ("conda_on_path", _priority3_conda_on_path),
        ("common_location", _priority4_common_locations),
        ("parsed_shell_config", _priority5_shell_startup),
    ]:
        candidates_tried.append(name)
        result = finder()
        if result:
            return {
                "found": True,
                "conda_sh": result["conda_sh"],
                "conda_env": result["conda_env"],
                "source": result["source"],
                "warnings": warnings,
                "candidates_tried": candidates_tried,
            }

    warnings.append("No conda installation found via any discovery method")
    return {
        "found": False,
        "conda_sh": None,
        "conda_env": "base",
        "source": None,
        "warnings": warnings,
        "candidates_tried": candidates_tried,
    }


def write_local_config(result: dict) -> Path:
    """Write .local/project_env.sh from discovery result."""
    LOCAL_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    # Shell-safe: single-quote everything
    conda_sh = result.get("conda_sh") or ""
    conda_env = result.get("conda_env", "base")
    source = result.get("source", "unknown")
    lines = [
        f"PROJECT_CONDA_SH='{conda_sh}'",
        f"PROJECT_CONDA_ENV='{conda_env}'",
        f"PROJECT_ENV_DISCOVERY_SOURCE='{source}'",
    ]
    LOCAL_CONFIG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return LOCAL_CONFIG


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Discover conda environment for the project.",
    )
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output as JSON")
    parser.add_argument("--print-shell", action="store_true",
                        help="Output shell assignments (safe for eval)")
    parser.add_argument("--write-local-config", action="store_true",
                        help="Write .local/project_env.sh")
    args = parser.parse_args(argv)

    result = discover_conda()

    if args.write_local_config:
        path = write_local_config(result)
        print(f"Written: {path}", file=sys.stderr)

    if args.json_output:
        # Remove non-serializable keys
        out = {k: v for k, v in result.items() if k != "candidates_tried"}
        print(json.dumps(out, indent=2))
    elif args.print_shell:
        conda_sh = result.get("conda_sh") or ""
        conda_env = result.get("conda_env", "base")
        source = result.get("source", "unknown")
        # Single-quoted, safe for eval
        print(f"PROJECT_CONDA_SH='{conda_sh}'")
        print(f"PROJECT_CONDA_ENV='{conda_env}'")
        print(f"PROJECT_ENV_DISCOVERY_SOURCE='{source}'")
    else:
        if result["found"]:
            print(f"Conda found: {result['conda_sh']}")
            print(f"  Environment: {result['conda_env']}")
            print(f"  Discovery source: {result['source']}")
        else:
            print("Conda NOT found")
        for w in result.get("warnings", []):
            print(f"  Warning: {w}")
        print(f"  Candidates tried: {', '.join(result.get('candidates_tried', []))}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
