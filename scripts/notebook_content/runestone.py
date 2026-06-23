"""Runestone-style notebook building blocks (PythonDS 交互教材结构).

映射关系（静态 Jupyter 预渲染）：
- Reading      → 长文 Markdown 小节
- Listing      → 伪代码 / 代码清单（Markdown）
- ActiveCode   → 可运行、尽量短小的 code cell
- CodeLens     → 分步 code cell + 每步打印全部变量状态
- Self-Check   → 预测题 + <details> 隐藏答案
"""

from __future__ import annotations

Cell = tuple[str, str]


def md(text: str) -> Cell:
    return ("md", text.strip())


def code(text: str) -> Cell:
    return ("code", text.strip())


def chapter(title: str, subtitle: str, objectives: list[str]) -> list[Cell]:
    objs = "\n".join(f"- {o}" for o in objectives)
    return [
        md(
            f"""# {title}

{subtitle}

> 本 notebook 采用 [Runestone Academy · PythonDS](https://runestone.academy/ns/books/published/pythonds/index.html) 式结构：
> **Reading（阅读）→ Listing（清单/伪代码）→ ActiveCode（运行）→ CodeLens（分步状态）→ Self-Check（自测）**。
> 配套交互网页见各章 `chN.html`。

## 学习目标

{objs}"""
        )
    ]


def section(num: str, title: str, body: str = "") -> list[Cell]:
    parts = [f"## {num}. {title}"]
    if body:
        parts.append(body)
    return [md("\n\n".join(parts))]


def subsection(num: str, title: str, body: str = "") -> list[Cell]:
    parts = [f"### {num} {title}"]
    if body:
        parts.append(body)
    return [md("\n\n".join(parts))]


def reading(*paragraphs: str) -> list[Cell]:
    return [md("\n\n".join(paragraphs))]


def listing(caption: str, source: str, lang: str = "text") -> list[Cell]:
    return [md(f"**Listing · {caption}**\n\n```{lang}\n{source.strip()}\n```")]


def activecode(*lines: str, caption: str = "") -> list[Cell]:
    cap = f"# ActiveCode · {caption}\n" if caption else ""
    return [code(cap + "\n".join(lines))]


def codelens(caption: str, *lines: str) -> list[Cell]:
    cap = f"# CodeLens · {caption}\n" if caption else ""
    return [code(cap + "\n".join(lines))]


def self_check(question: str, hint: str = "", answer: str = "") -> list[Cell]:
    hint_block = f"\n\n*{hint}*" if hint else ""
    ans_block = ""
    if answer:
        ans_block = f"\n\n<details><summary>点击展开答案</summary>\n\n{answer}\n\n</details>"
    return [md(f"**Self-Check** · {question}{hint_block}{ans_block}")]


def summary(*paragraphs: str) -> list[Cell]:
    return [md("## 本章小结\n\n" + "\n\n".join(paragraphs))]


def exercises(*items: str) -> list[Cell]:
    body = "\n".join(f"{i+1}. {t}" for i, t in enumerate(items))
    return [md(f"## 练习题\n\n{body}")]


def boot(ch: str, imports: str = "") -> str:
    base = f"""
import sys
from pathlib import Path
ROOT = Path.cwd()
if not (ROOT / "labs").exists() and (ROOT.parent / "labs").exists():
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "labs"))
sys.path.insert(0, str(ROOT / "labs" / "{ch}"))
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
from IPython.display import display, Markdown
""".strip()
    return base + ("\n" + imports.strip() if imports.strip() else "")


def flatten(groups: list) -> list[Cell]:
    out: list[Cell] = []
    for g in groups:
        if isinstance(g, tuple) and len(g) == 2 and g[0] in ("md", "code"):
            out.append(g)
        elif isinstance(g, list):
            out.extend(flatten(g))
        else:
            raise TypeError(f"unexpected cell group: {type(g)!r}")
    return out
