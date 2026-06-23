"""Notebook cell building blocks — 只展示算法流程。"""

from __future__ import annotations

Cell = tuple[str, str]


def md(text: str) -> Cell:
    return ("md", text.strip())


def code(text: str) -> Cell:
    return ("code", text.strip())


def chapter_link(title: str, intro: str, objectives: list[str], web_href: str) -> list[Cell]:
    objs = "\n".join(f"- {o}" for o in objectives)
    return [
        md(
            f"""# {title}

{intro}

配套交互演示：[章节网页]({web_href})

## 本节目标

{objs}"""
        )
    ]


def chapter(title: str, intro: str, objectives: list[str]) -> list[Cell]:
    return chapter_link(title, intro, objectives, "../ch5.html")


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
    return [md(f"**{caption}**\n\n```{lang}\n{source.strip()}\n```")]


def activecode(*lines: str) -> list[Cell]:
    return [code("\n".join(lines))]


def stepcode(*lines: str) -> list[Cell]:
    """每行独立 code cell，便于逐步执行与阅读。"""
    return [code(line.strip()) for line in lines if line.strip()]


def self_check(question: str, hint: str = "", answer: str = "") -> list[Cell]:
    hint_block = f"\n\n*{hint}*" if hint else ""
    ans_block = ""
    if answer:
        ans_block = f"\n\n<details><summary>查看答案</summary>\n\n{answer}\n\n</details>"
    return [md(f"**思考** · {question}{hint_block}{ans_block}")]


def summary(*paragraphs: str) -> list[Cell]:
    return [md("## 小结\n\n" + "\n\n".join(paragraphs))]


def exercises(*items: str) -> list[Cell]:
    body = "\n".join(f"{i+1}. {t}" for i, t in enumerate(items))
    return [md(f"## 练习\n\n{body}")]


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
from common.mpl_setup import configure_matplotlib
configure_matplotlib()
from IPython.display import display, Image
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
