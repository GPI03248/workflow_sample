"""Generate API documentation from cfd/ Python modules.

Scans cfd/ for Python files, extracts module docstrings, public functions,
classes, and signatures using the ast module, and writes docs/api/*.md.

Usage:
    python tools/generate_cfd_api_docs.py
"""

from __future__ import annotations
import ast
import os
import sys

CFD_ROOT = os.path.join(os.path.dirname(__file__), "..", "cfd")
DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "api")


def _parse_file(filepath: str) -> dict:
    """Parse a Python file and extract docstring, functions, classes."""
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)

    module_doc = ast.get_docstring(tree) or ""

    functions = []
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip private functions.
            if node.name.startswith("_"):
                continue
            # Skip methods (they are inside classes).
            doc = ast.get_docstring(node) or ""
            sig = f"{node.name}({', '.join(a.arg for a in node.args.args)})"
            functions.append({"name": node.name, "signature": sig, "doc": doc.split(chr(10))[0] if doc else ""})
        elif isinstance(node, ast.ClassDef):
            if node.name.startswith("_"):
                continue
            doc = ast.get_docstring(node) or ""
            classes.append({"name": node.name, "doc": doc.split(chr(10))[0] if doc else ""})

    return {"module_doc": module_doc, "functions": functions, "classes": classes}


def _write_md(module_name: str, info: dict) -> str:
    """Write a markdown API doc for one module."""
    lines = [f"# API: cfd.{module_name}", ""]
    if info["module_doc"]:
        lines.append(info["module_doc"])
        lines.append("")

    if info["classes"]:
        lines.append("## Classes")
        lines.append("")
        for cls in info["classes"]:
            lines.append(f"- **{cls['name']}**")
            if cls["doc"]:
                lines.append(f"  — {cls['doc']}")
        lines.append("")

    if info["functions"]:
        lines.append("## Functions")
        lines.append("")
        for fn in info["functions"]:
            lines.append(f"### `{fn['signature']}`")
            if fn["doc"]:
                lines.append(f"{fn['doc']}")
            lines.append("")

    lines.append("## Extension Notes")
    lines.append("")
    lines.append("See docs/cfd_iteration_guide.md for how to extend this module.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    os.makedirs(DOCS_DIR, exist_ok=True)

    # Map from module name to file path.
    modules = {}

    # Top-level files.
    for fname in os.listdir(CFD_ROOT):
        fpath = os.path.join(CFD_ROOT, fname)
        if os.path.isfile(fpath) and fname.endswith(".py") and fname != "__init__.py":
            mod = f"{'_'.join(fname[:-3].split())}"
            modules[mod] = fpath

    # Sub-packages.
    for subpkg in os.listdir(CFD_ROOT):
        subpath = os.path.join(CFD_ROOT, subpkg)
        if os.path.isdir(subpath):
            init = os.path.join(subpath, "__init__.py")
            if os.path.exists(init):
                modules[subpkg] = init
            for fname in os.listdir(subpath):
                fpath = os.path.join(subpath, fname)
                if os.path.isfile(fpath) and fname.endswith(".py") and fname != "__init__.py":
                    mod_name = f"{subpkg}_{fname[:-3]}"
                    modules[mod_name] = fpath

    for mod_name, fpath in sorted(modules.items()):
        info = _parse_file(fpath)
        md = _write_md(mod_name, info)
        out_path = os.path.join(DOCS_DIR, f"cfd_{mod_name}.md")
        with open(out_path, "w") as f:
            f.write(md)
        print(f"  Generated {out_path}")

    print(f"\nDone. {len(modules)} API docs written to {DOCS_DIR}/")


if __name__ == "__main__":
    main()
