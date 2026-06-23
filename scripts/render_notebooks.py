#!/usr/bin/env python3
"""Execute notebooks and render lightweight static HTML for GitHub Pages.

Inspired by tutorial sites (D2L / nbconvert lab): markdown narrative,
code cells with toggle, captured stdout, no Colab required.
"""

from __future__ import annotations

import argparse
import html
import io
import json
import re
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

try:
    import markdown
except ImportError as exc:  # pragma: no cover
    raise SystemExit("pip install markdown") from exc

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = ROOT / "notebooks"
RENDERED_DIR = NOTEBOOKS_DIR / "rendered"
TEMPLATE_CSS = "../notebook-reader.css"

NOTEBOOK_META: dict[str, dict] = {
    "ch05_campus_search.ipynb": {
        "title": "第 5 章 · 校园图六种搜索",
        "chapter": 5,
        "web": "../../ch5.html",
        "minutes": 15,
    },
    "ch09_bpe.ipynb": {
        "title": "第 9 章 · BPE 字节对合并",
        "chapter": 9,
        "web": "../../ch9.html",
        "minutes": 10,
    },
}


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text.strip().lower())
    return s.strip("-") or "section"


def extract_toc(md_source: str) -> list[tuple[str, str, int]]:
    toc: list[tuple[str, str, int]] = []
    for line in md_source.splitlines():
        m = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            toc.append((slugify(title), title, level))
    return toc


def md_to_html(source: str, toc_accum: list[tuple[str, str, int]]) -> str:
    body = markdown.markdown(
        source,
        extensions=["tables", "fenced_code", "nl2br"],
    )

    def repl(match: re.Match[str]) -> str:
        level = match.group(1)
        inner = match.group(2)
        plain = re.sub(r"<[^>]+>", "", inner)
        sid = slugify(plain)
        toc_accum.append((sid, plain, int(level)))
        return f'<h{level} id="{sid}">{inner}</h{level}>'

    body = re.sub(r"<h([1-3])>(.*?)</h\1>", repl, body, flags=re.DOTALL)
    return f'<div class="nb-markdown">{body}</div>'


def run_code_cells(codes: list[str], cwd: Path) -> list[tuple[str, str, int]]:
    """Execute notebook code cells in one namespace (like Jupyter)."""
    namespace: dict = {"__name__": "__main__"}
    results: list[tuple[str, str, int]] = []
    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(cwd)
        for code in codes:
            if not code.strip():
                results.append(("", "", 0))
                continue
            out_buf = io.StringIO()
            err_buf = io.StringIO()
            rc = 0
            try:
                with redirect_stdout(out_buf), redirect_stderr(err_buf):
                    exec(compile(code, "<notebook>", "exec"), namespace)
            except Exception:
                rc = 1
                err_buf.write(traceback.format_exc())
            results.append((out_buf.getvalue(), err_buf.getvalue(), rc))
    finally:
        import os

        os.chdir(old_cwd)
    return results


def format_output(text: str, is_error: bool = False) -> str:
    if not text.strip():
        return ""
    cls = "nb-stderr" if is_error else "nb-stdout"
    return f'<pre class="{cls}">{html.escape(text.rstrip())}</pre>'


def render_cell_code(code: str, idx: int, out: str, err: str, rc: int) -> str:
    escaped = html.escape(code.rstrip())
    stdout_html = format_output(out) + format_output(err, is_error=True)
    if rc != 0 and not err and not out:
        stdout_html += format_output(f"[exit {rc}]", is_error=True)
    if not stdout_html.strip():
        stdout_html = '<p class="nb-no-output">（无输出）</p>'

    return f"""<section class="nb-cell nb-code" data-cell="{idx}">
  <div class="nb-code-header">
    <span class="nb-code-label">In [{idx + 1}]</span>
  </div>
  <div class="nb-code-input"><pre><code class="language-python">{escaped}</code></pre></div>
  <div class="nb-code-output">{stdout_html}</div>
</section>"""


def build_toc_html(toc: list[tuple[str, str, int]]) -> str:
    if not toc:
        return ""
    items = []
    for sid, title, level in toc:
        indent = " nb-toc-l2" if level == 2 else " nb-toc-l3" if level >= 3 else ""
        items.append(f'<li class="{indent.strip()}"><a href="#{sid}">{html.escape(title)}</a></li>')
    return f'<nav class="nb-toc" aria-label="本页目录"><p class="nb-toc-title">目录</p><ul>{"".join(items)}</ul></nav>'


def wrap_page(title: str, chapter: int, web: str, minutes: int, body: str, toc: list, ipynb_file: str) -> str:
    toc_html = build_toc_html(toc)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <meta name="description" content="{html.escape(title)} — 《AI思维》配套 Python 实验（预渲染）"/>
  <title>{html.escape(title)}</title>
  <link rel="icon" href="../../favicon.svg" type="image/svg+xml"/>
  <link rel="stylesheet" href="{TEMPLATE_CSS}?v=1"/>
</head>
<body class="nb-reader" data-chapter="{chapter}">
  <header class="nb-reader-header">
    <div class="nb-reader-header-inner">
      <a class="nb-reader-back" href="{web}">← 第 {chapter} 章网页</a>
      <a class="nb-reader-index" href="../index.html">Notebook 索引</a>
      <span class="nb-reader-meta">约 {minutes} 分钟 · 预渲染 · 无需 Colab</span>
    </div>
    <div class="nb-reader-toolbar">
      <h1>{html.escape(title)}</h1>
      <div class="nb-reader-actions">
        <button type="button" class="nb-toggle-code" id="toggleCode" aria-pressed="false">隐藏代码</button>
        <a class="nb-dl" id="downloadLink" href="../{ipynb_file}" download>下载 .ipynb</a>
      </div>
    </div>
  </header>
  <div class="nb-reader-layout">
    {toc_html}
    <article class="nb-reader-body" id="nbContent">
      {body}
    </article>
  </div>
  <footer class="nb-reader-footer">
    <p>输出在发布时已执行保存；修改案例数据请下载 Notebook 在本地运行。</p>
  </footer>
  <script src="../reader.js?v=1"></script>
</body>
</html>"""


def render_notebook(path: Path, execute: bool = True) -> Path:
    meta = NOTEBOOK_META.get(path.name, {})
    title = meta.get("title", path.stem)
    chapter = meta.get("chapter", 0)
    web = meta.get("web", "../hub.html")
    minutes = meta.get("minutes", 15)

    nb = json.loads(path.read_text(encoding="utf-8"))
    toc: list[tuple[str, str, int]] = []
    parts: list[str] = []

    code_cells = [
        "".join(c.get("source", []))
        for c in nb.get("cells", [])
        if c.get("cell_type") == "code"
    ]
    exec_results = run_code_cells(code_cells, ROOT) if execute else [("", "", 0)] * len(code_cells)
    code_idx = 0

    for cell in nb.get("cells", []):
        src = "".join(cell.get("source", []))
        if cell.get("cell_type") == "markdown":
            parts.append(md_to_html(src, toc))
        elif cell.get("cell_type") == "code":
            out, err, rc = exec_results[code_idx]
            parts.append(render_cell_code(src, code_idx, out, err, rc))
            code_idx += 1

    body = "\n".join(parts)
    body = body.replace('href="../ch', 'href="../../ch')
    page = wrap_page(title, chapter, web, minutes, body, toc, path.name)
    RENDERED_DIR.mkdir(parents=True, exist_ok=True)
    out = RENDERED_DIR / f"{path.stem}.html"
    out.write_text(page, encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebooks", nargs="*", help="ipynb files (default: all in NOTEBOOK_META)")
    parser.add_argument("--no-execute", action="store_true")
    args = parser.parse_args()

    names = args.notebooks or list(NOTEBOOK_META.keys())
    for name in names:
        path = NOTEBOOKS_DIR / name if not Path(name).is_absolute() else Path(name)
        if not path.exists():
            print(f"skip missing {path}", file=sys.stderr)
            continue
        out = render_notebook(path, execute=not args.no_execute)
        print(f"rendered {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
