#!/usr/bin/env python3
"""Generate pedagogical Jupyter notebooks from notebook_content specs."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

try:
    import nbformat
    from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
except ImportError as exc:
    raise SystemExit("pip install nbformat") from exc

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks"
sys.path.insert(0, str(ROOT / "scripts"))

from notebook_content import all_notebooks  # noqa: E402


def write_notebook(name: str, cells: list[tuple[str, str]]) -> None:
    nb = new_notebook(
        cells=[
            new_markdown_cell(src) if kind == "md" else new_code_cell(src)
            for kind, src in cells
        ],
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
    )
    for cell in nb.cells:
        cell["id"] = str(uuid.uuid4())[:8]
    path = OUT / name
    nbformat.write(nb, path)
    n_md = sum(1 for c in cells if c[0] == "md")
    n_code = len(cells) - n_md
    print(f"generated {path.relative_to(ROOT)} ({n_md} md + {n_code} code = {len(cells)} cells)")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    notebooks = all_notebooks()
    for name, cells in notebooks.items():
        write_notebook(name, cells)
    print(f"\ntotal {len(notebooks)} notebooks")


if __name__ == "__main__":
    main()
