"""Reject legacy package-management commands in student-facing files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "README.md",
    ROOT / "NOTICE.md",
    ROOT / "data",
    ROOT / "lectures",
    ROOT / "exercises",
    ROOT / "schedule",
]
PATTERNS = [
    re.compile(r"(?i)\bpython\s+-m\s+pip\b"),
    re.compile(r"(?i)\bpip\s+install\b"),
    re.compile(r"(?i)\bpipenv\b"),
    re.compile(r"(?i)\bPipfile(?:\.lock)?\b"),
    re.compile(r"(?m)^\s*[!%]\s*pip\b"),
]


def iter_files() -> list[Path]:
    files: list[Path] = []
    for target in TARGETS:
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            files.extend(
                path
                for path in target.rglob("*")
                if path.suffix in {".md", ".ipynb", ".py", ".txt"}
            )
    return sorted(files)


def notebook_text(path: Path) -> str:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    chunks: list[str] = []
    for cell in notebook.get("cells", []):
        source = cell.get("source", "")
        if isinstance(source, list):
            chunks.extend(source)
        else:
            chunks.append(source)
    return "\n".join(chunks)


def read_text(path: Path) -> str:
    if path.suffix == ".ipynb":
        return notebook_text(path)
    return path.read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    for path in iter_files():
        text = read_text(path)
        rel = path.relative_to(ROOT)
        for pattern in PATTERNS:
            match = pattern.search(text)
            if match:
                failures.append(f"{rel}: found disallowed environment instruction: {match.group(0)!r}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("No disallowed package-management instructions found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
