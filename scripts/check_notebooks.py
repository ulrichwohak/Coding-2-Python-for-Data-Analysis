"""Validate course notebooks without executing them."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIRS = [ROOT / "lectures"]
BAD_CODE_PATTERNS = [
    re.compile(r"(?i)\bread_csv\(\s*[\"']https?://"),
    re.compile(r"(?i)\bread_excel\(\s*[\"']https?://"),
    re.compile(r"(?m)^\s*[!%]\s*pip\b"),
    re.compile(r"(?i)\bpip\s+install\b"),
    re.compile(r"(?i)\bpipenv\b"),
]


def notebook_paths() -> list[Path]:
    paths: list[Path] = []
    for directory in NOTEBOOK_DIRS:
        if directory.exists():
            paths.extend(directory.rglob("*.ipynb"))
    return sorted(paths)


def source_text(cell: dict[str, Any]) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(source)
    return str(source)


def check_notebook(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    failures: list[str] = []
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{rel}: invalid JSON: {exc}"]

    kernelspec = notebook.get("metadata", {}).get("kernelspec", {})
    if kernelspec.get("display_name") != "Python 3 (ipykernel)":
        failures.append(f"{rel}: kernelspec display_name must be 'Python 3 (ipykernel)'")
    if kernelspec.get("name") != "python3":
        failures.append(f"{rel}: kernelspec name must be 'python3'")

    cells = notebook.get("cells")
    if not isinstance(cells, list) or not cells:
        failures.append(f"{rel}: notebook must contain cells")
        return failures

    for index, cell in enumerate(cells, start=1):
        cell_type = cell.get("cell_type")
        text = source_text(cell)
        if cell_type == "code":
            if cell.get("execution_count") is not None:
                failures.append(f"{rel}: code cell {index} has a stored execution_count")
            if cell.get("outputs"):
                failures.append(f"{rel}: code cell {index} has stored outputs")
            for pattern in BAD_CODE_PATTERNS:
                match = pattern.search(text)
                if match:
                    failures.append(f"{rel}: code cell {index} contains disallowed code {match.group(0)!r}")
            try:
                ast.parse(text or "\n")
            except SyntaxError as exc:
                failures.append(f"{rel}: code cell {index} is not valid Python: {exc.msg}")
        elif cell_type not in {"markdown", "raw"}:
            failures.append(f"{rel}: cell {index} has unsupported cell_type {cell_type!r}")
    return failures


def main() -> int:
    paths = notebook_paths()
    if not paths:
        print("No notebooks found.", file=sys.stderr)
        return 1

    failures: list[str] = []
    for path in paths:
        failures.extend(check_notebook(path))

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Validated {len(paths)} notebooks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
