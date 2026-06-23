#!/usr/bin/env python3
"""Execute real Jupyter notebooks and export official nbconvert HTML."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = ROOT / "notebooks"
RENDERED_DIR = NOTEBOOKS_DIR / "rendered"
CHROME = """<div id="ai-labs-chrome" style="position:sticky;top:0;z-index:9999;background:#0d6b62;color:#fff;font:600 13px system-ui,sans-serif;padding:8px 16px;display:flex;gap:16px;flex-wrap:wrap;align-items:center;border-bottom:1px solid #0a5a52"><a href="../index.html" style="color:#fff;text-decoration:none">Notebook 索引</a><a href="../../hub.html" style="color:#fff;text-decoration:none">章节目录</a><span style="opacity:.85;margin-left:auto">Jupyter 预渲染 · 国内可访问</span></div>"""


def list_notebooks(pattern: list[str] | None = None) -> list[Path]:
    if pattern:
        return [NOTEBOOKS_DIR / p for p in pattern if (NOTEBOOKS_DIR / p).exists()]
    return sorted(NOTEBOOKS_DIR.glob("ch*.ipynb"))


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(ROOT), check=True)


def execute_inplace(path: Path) -> None:
    run(
        [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.timeout=120",
            str(path.relative_to(ROOT)),
        ]
    )


def export_html(path: Path) -> Path:
    RENDERED_DIR.mkdir(parents=True, exist_ok=True)
    stem = path.stem
    run(
        [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "html",
            "--template",
            "lab",
            "--embed-images",
            f"--output={stem}",
            f"--output-dir={RENDERED_DIR.relative_to(ROOT)}",
            str(path.relative_to(ROOT)),
        ]
    )
    out = RENDERED_DIR / f"{stem}.html"
    inject_chrome(out)
    return out


def inject_chrome(html_path: Path) -> None:
    text = html_path.read_text(encoding="utf-8")

    old = re.compile(
        r'<div id="ai-labs-chrome"[^>]*>.*?</div>',
        re.DOTALL,
    )
    if old.search(text):
        text = old.sub(CHROME, text, count=1)
    elif "<body" in text:
        text = text.replace("<body", f"{CHROME}<body", 1)
    else:
        text = CHROME + text
    html_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebooks", nargs="*", help="ipynb names under notebooks/")
    parser.add_argument("--skip-execute", action="store_true")
    args = parser.parse_args()

    paths = list_notebooks(args.notebooks or None)
    if not paths:
        raise SystemExit("no notebooks found")

    for path in paths:
        if not args.skip_execute:
            execute_inplace(path)
        out = export_html(path)
        print(f"ok {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
