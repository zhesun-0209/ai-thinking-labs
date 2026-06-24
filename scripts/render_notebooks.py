#!/usr/bin/env python3
"""Execute real Jupyter notebooks and export official nbconvert HTML."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = ROOT / "notebooks"
RENDERED_DIR = NOTEBOOKS_DIR / "rendered"
READER_SCRIPT = """<script id="ai-labs-reader-script">
(() => {
  const root = document.documentElement;
  const topButton = document.getElementById("ai-labs-top");
  const updateProgress = () => {
    const scrollable = Math.max(1, root.scrollHeight - root.clientHeight);
    const progress = Math.min(1, Math.max(0, root.scrollTop / scrollable));
    root.style.setProperty("--ai-labs-read-progress", `${Math.round(progress * 100)}%`);
    if (topButton) topButton.hidden = root.scrollTop < 520;
  };
  document.addEventListener("scroll", updateProgress, { passive: true });
  topButton?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  updateProgress();
})();
</script>"""
RENDER_STYLE = """<style id="ai-labs-render-style">
:root {
  --ai-labs-accent: #2563eb;
  --ai-labs-accent-dark: #1e3a8a;
  --ai-labs-blue: #2563eb;
  --ai-labs-amber: #c2410c;
  --ai-labs-line: #e2e8f0;
  --ai-labs-surface: #ffffff;
  --ai-labs-soft: #f8fafc;
  --ai-labs-gutter: clamp(18px, 6vw, 96px);
  --ai-labs-read-progress: 0%;
}

html[lang="zh-CN"] {
  scroll-padding-top: 72px;
}

body.jp-Notebook {
  margin: 0;
  padding: 0 var(--ai-labs-gutter) 56px;
  background: #fbfcfd;
  color: #111827;
  font-family: "Noto Sans CJK SC", system-ui, -apple-system, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
}

#ai-labs-chrome {
  position: sticky;
  top: 0;
  z-index: 9999;
  margin: 0 calc(-1 * var(--ai-labs-gutter)) 22px;
  padding: 10px var(--ai-labs-gutter);
  min-height: 48px;
  box-sizing: border-box;
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  align-items: center;
  background: rgba(255, 255, 255, 0.96);
  color: #0f172a;
  border-bottom: 1px solid var(--ai-labs-line);
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.05);
  font: 700 13px/1.3 "Noto Sans CJK SC", system-ui, -apple-system, "Segoe UI", sans-serif;
}

#ai-labs-chrome::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;
  height: 3px;
  background: linear-gradient(90deg, var(--ai-labs-accent) var(--ai-labs-read-progress), transparent 0);
}

#ai-labs-chrome a {
  color: #0f172a;
  min-height: 32px;
  padding: 0 2px;
  display: inline-flex;
  align-items: center;
  text-decoration: none;
}

#ai-labs-chrome a:focus-visible {
  outline: 3px solid rgba(37, 99, 235, 0.22);
  outline-offset: 2px;
}

#ai-labs-chrome span {
  margin-left: auto;
  opacity: 0.9;
}

#ai-labs-top {
  position: fixed;
  right: 18px;
  bottom: 18px;
  z-index: 9998;
  min-width: 42px;
  min-height: 42px;
  border: 1px solid var(--ai-labs-line);
  border-radius: 8px;
  background: #fff;
  color: var(--ai-labs-accent-dark);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.16);
  font: 800 16px/1 "Noto Sans CJK SC", system-ui, -apple-system, "Segoe UI", sans-serif;
  cursor: pointer;
}

#ai-labs-top[hidden] {
  display: none;
}

.jp-Notebook .jp-Cell {
  max-width: 960px;
  margin-left: auto;
  margin-right: auto;
  margin-bottom: 10px;
}

.jp-Notebook .jp-CodeCell {
  max-width: min(1120px, 100%);
}

.jp-Notebook .jp-MarkdownCell:first-of-type {
  padding: 18px 20px;
  border: 1px solid var(--ai-labs-line);
  border-left: 5px solid var(--ai-labs-accent);
  border-radius: 8px;
  background: #ffffff;
  box-shadow: none;
}

.jp-RenderedHTMLCommon,
.jp-RenderedHTMLCommon p,
.jp-RenderedHTMLCommon li {
  line-height: 1.72;
}

.jp-RenderedHTMLCommon p,
.jp-RenderedHTMLCommon ul,
.jp-RenderedHTMLCommon ol {
  max-width: 840px;
}

.jp-RenderedHTMLCommon h1,
.jp-RenderedHTMLCommon h2,
.jp-RenderedHTMLCommon h3 {
  letter-spacing: 0;
  color: #1f2937;
}

.jp-RenderedHTMLCommon h1 {
  font-size: clamp(1.85rem, 5vw, 2.45rem);
  line-height: 1.16;
}

.jp-RenderedHTMLCommon h2 {
  margin-top: 1.35em;
  padding-top: 0.2em;
  font-size: clamp(1.35rem, 3.6vw, 1.78rem);
}

.jp-RenderedHTMLCommon h3 {
  color: #334155;
}

.jp-RenderedHTMLCommon a.anchor-link {
  margin-left: 0.35em;
  color: var(--ai-labs-accent);
  font-size: 0.72em;
  text-decoration: none;
  opacity: 0;
  transition: opacity 120ms ease;
}

.jp-RenderedHTMLCommon h1:hover a.anchor-link,
.jp-RenderedHTMLCommon h2:hover a.anchor-link,
.jp-RenderedHTMLCommon h3:hover a.anchor-link,
.jp-RenderedHTMLCommon a.anchor-link:focus-visible {
  opacity: 0.75;
}

.jp-RenderedHTMLCommon a.anchor-link:focus-visible {
  outline: 2px solid rgba(37, 99, 235, 0.24);
  outline-offset: 2px;
}

.jp-RenderedHTMLCommon a {
  color: var(--ai-labs-accent-dark);
  font-weight: 700;
}

.jp-RenderedHTMLCommon code {
  border-radius: 5px;
  padding: 0.1em 0.35em;
  background: #eef2f7;
  color: #334155;
}

.jp-RenderedHTMLCommon details {
  max-width: 840px;
  margin: 12px 0;
  padding: 12px 14px;
  border: 1px solid var(--ai-labs-line);
  border-radius: 8px;
  background: #ffffff;
}

.jp-RenderedHTMLCommon summary {
  cursor: pointer;
  color: var(--ai-labs-accent-dark);
  font-weight: 800;
}

.jp-RenderedHTMLCommon table,
.jp-RenderedHTMLCommon table.dataframe {
  width: max-content;
  min-width: min(100%, 720px);
  max-width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin: 10px 0 18px;
  overflow: hidden;
  border: 1px solid var(--ai-labs-line);
  border-radius: 8px;
  background: var(--ai-labs-surface);
  box-shadow: none;
}

.jp-RenderedHTMLCommon thead th {
  background: #f1f5f9;
  color: #0f172a;
  font-weight: 800;
  border-bottom: 1px solid var(--ai-labs-line);
}

.jp-RenderedHTMLCommon th,
.jp-RenderedHTMLCommon td {
  padding: 9px 11px;
  border-right: 1px solid #eef2f7;
  border-bottom: 1px solid #eef2f7;
  vertical-align: top;
  white-space: nowrap;
}

.jp-RenderedHTMLCommon tr:nth-child(even) td,
.jp-RenderedHTMLCommon tr:nth-child(even) th {
  background: #f8fafc;
}

.jp-RenderedHTMLCommon tr:last-child td,
.jp-RenderedHTMLCommon tr:last-child th {
  border-bottom: 0;
}

.jp-RenderedHTMLCommon tr > :last-child {
  border-right: 0;
}

.jp-InputArea-editor,
.jp-OutputArea-output {
  max-width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.jp-InputArea-editor {
  border: 1px solid var(--ai-labs-line);
  border-radius: 8px;
  background: #f8fafc;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.jp-OutputArea-output {
  border-radius: 8px;
}

.jp-RenderedText pre {
  padding: 12px 14px;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid var(--ai-labs-line);
}

.jp-RenderedHTMLCommon img,
.jp-OutputArea-output img,
.jp-OutputArea-output svg {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid var(--ai-labs-line);
  box-shadow: none;
}

@media (max-width: 640px) {
  body.jp-Notebook {
    padding-bottom: 40px;
  }

  #ai-labs-chrome {
    min-height: 56px;
    margin-bottom: 18px;
  }

  #ai-labs-chrome span {
    flex-basis: 100%;
    margin-left: 0;
  }

  #ai-labs-top {
    right: 14px;
    bottom: 14px;
  }

  .jp-Notebook .jp-InputPrompt,
  .jp-Notebook .jp-OutputPrompt {
    display: none;
  }

  .jp-Notebook .jp-Cell-inputWrapper,
  .jp-Notebook .jp-Cell-outputWrapper {
    padding-left: 0;
  }

  .jp-Notebook .jp-MarkdownCell:first-of-type {
    padding: 14px;
  }
}
</style>"""
CHROME_RE = re.compile(r'<(?:div|nav) id="ai-labs-chrome"[^>]*>.*?</(?:div|nav)>\s*', re.DOTALL)
STYLE_RE = re.compile(r'<style id="ai-labs-render-style">.*?</style>\s*', re.DOTALL)
TOP_BUTTON_RE = re.compile(r'<button id="ai-labs-top"[^>]*>.*?</button>\s*', re.DOTALL)
READER_SCRIPT_RE = re.compile(r'<script id="ai-labs-reader-script">.*?</script>\s*', re.DOTALL)
REQUIRE_JS_RE = re.compile(
    r'<script\s+src="https://cdnjs\.cloudflare\.com/ajax/libs/require\.js/2\.1\.10/require\.min\.js"></script>\s*',
    re.IGNORECASE,
)
MATHJAX_RE = re.compile(
    r"<!-- Load mathjax -->.*?<!-- End of mathjax configuration -->",
    re.DOTALL | re.IGNORECASE,
)
MERMAID_RE = re.compile(
    r'<script type="module">\s*document\.addEventListener\("DOMContentLoaded", async \(\) => \{.*?<!-- End of mermaid configuration -->',
    re.DOTALL,
)
DEFAULT_IMAGE_ALT_RE = re.compile(r'alt="No description has been provided for this image"')


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
            "--TagRemovePreprocessor.enabled=True",
            "--TagRemovePreprocessor.remove_cell_tags=ai-labs-bootstrap",
            f"--output={stem}",
            f"--output-dir={RENDERED_DIR.relative_to(ROOT)}",
            str(path.relative_to(ROOT)),
        ]
    )
    out = RENDERED_DIR / f"{stem}.html"
    inject_chrome(out, path)
    return out


def notebook_title(notebook_path: Path) -> str:
    nb = json.loads(notebook_path.read_text(encoding="utf-8"))
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        source = "".join(cell.get("source", []))
        for line in source.splitlines():
            if line.startswith("#"):
                return line.lstrip("#").strip()
    return notebook_path.stem


def chapter_number(notebook_path: Path) -> str | None:
    match = re.match(r"ch(\d{2})_", notebook_path.stem)
    if not match:
        return None
    return str(int(match.group(1)))


def reader_chrome(notebook_path: Path) -> str:
    ch = chapter_number(notebook_path)
    chapter_link = f'<a href="../../ch{ch}.html">章节网页</a>' if ch else '<a href="../../hub.html">章节目录</a>'
    lab_link = f'<a href="../chapter.html?ch={ch}">Python 代码实验</a>' if ch else '<a href="../../hub.html">章节目录</a>'
    return (
        '<nav id="ai-labs-chrome" aria-label="Notebook 导航">'
        f"{lab_link}"
        f"{chapter_link}"
        '<a href="../../hub.html">章节目录</a>'
        f'<a href="../{notebook_path.name}" download>下载 .ipynb</a>'
        '<span>阅读进度</span>'
        "</nav>"
    )


def set_html_lang(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        if re.search(r"\blang=", tag):
            return re.sub(r'\blang=(["\']).*?\1', 'lang="zh-CN"', tag, count=1)
        return tag.replace("<html", '<html lang="zh-CN"', 1)

    return re.sub(r"<html\b[^>]*>", repl, text, count=1)


def set_head_metadata(text: str, title: str) -> str:
    escaped_title = html.escape(f"{title} · AI思维 Notebook")
    description = html.escape(f"{title}，AI思维配套 Jupyter 预渲染代码实验。")
    favicon = '<link rel="icon" href="../../favicon.svg" type="image/svg+xml"/>'

    if re.search(r"<title>.*?</title>", text, re.DOTALL):
        text = re.sub(r"<title>.*?</title>", f"<title>{escaped_title}</title>", text, count=1, flags=re.DOTALL)
    else:
        text = text.replace("</head>", f"<title>{escaped_title}</title>\n</head>", 1)

    meta = f'<meta name="description" content="{description}"/>'
    if re.search(r'<meta\s+name=["\']description["\'][^>]*>', text, re.IGNORECASE):
        text = re.sub(r'<meta\s+name=["\']description["\'][^>]*>', meta, text, count=1, flags=re.IGNORECASE)
    else:
        text = re.sub(r"</title>", f"</title>\n{meta}", text, count=1)

    if re.search(r'<link\s+rel=["\']icon["\'][^>]*>', text, re.IGNORECASE):
        text = re.sub(r'<link\s+rel=["\']icon["\'][^>]*>', favicon, text, count=1, flags=re.IGNORECASE)
    else:
        text = re.sub(
            r'(<meta\s+name=["\']description["\'][^>]*>)',
            lambda match: f"{match.group(1)}\n{favicon}",
            text,
            count=1,
            flags=re.IGNORECASE,
        )

    return text


def inject_chrome(html_path: Path, notebook_path: Path) -> None:
    text = html_path.read_text(encoding="utf-8")
    title = notebook_title(notebook_path)
    chrome = reader_chrome(notebook_path)

    text = set_html_lang(text)
    text = set_head_metadata(text, title)
    text = REQUIRE_JS_RE.sub("", text)
    text = MATHJAX_RE.sub("", text)
    text = MERMAID_RE.sub("", text)
    text = STYLE_RE.sub("", text)
    text = TOP_BUTTON_RE.sub("", text)
    text = READER_SCRIPT_RE.sub("", text)
    text = DEFAULT_IMAGE_ALT_RE.sub('alt="Notebook 输出图表，请结合前后文字说明阅读"', text)
    text = text.replace("</head>", f"{RENDER_STYLE}\n</head>", 1)
    text = CHROME_RE.sub("", text)
    text = re.sub(r'href="\.\./(ch(?:[5-9]|1[0-2])\.html)"', r'href="../../\1"', text)

    if re.search(r"<body\b[^>]*>", text):
        text = re.sub(
            r"(<body\b[^>]*>)",
            lambda match: f'{match.group(1)}\n{chrome}\n<button id="ai-labs-top" type="button" hidden aria-label="回到顶部">↑</button>',
            text,
            count=1,
        )
    else:
        text = chrome + text
    text = text.replace("</body>", f"{READER_SCRIPT}\n</body>", 1)
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
