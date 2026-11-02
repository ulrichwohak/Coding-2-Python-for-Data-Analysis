"""Execute every module notebook from a fresh kernel without modifying sources."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "modules"


def execute(path: Path, output_dir: Path | None) -> None:
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=300,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.execute()
    if output_dir is not None:
        relative = path.relative_to(MODULES)
        destination = output_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(notebook, destination)
    print(f"executed {path.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    arguments = parser.parse_args()
    # Preserve figures in the executed copy, just as JupyterLab does for students.
    os.environ.setdefault("MPLBACKEND", "module://matplotlib_inline.backend_inline")

    for path in sorted(MODULES.rglob("*.ipynb")):
        execute(path, arguments.output_dir)


if __name__ == "__main__":
    main()
