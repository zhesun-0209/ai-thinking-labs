"""Notebook cell building blocks for executable code labs."""

from __future__ import annotations

Cell = tuple[str, str]


def md(text: str) -> Cell:
    return ("md", text.strip())


def code(text: str) -> Cell:
    return ("code", text.strip())


def chapter_link(title: str, intro: str | list[str] = "", objectives: list[str] | str | None = None, web_href: str = "") -> list[Cell]:
    if isinstance(intro, list) and isinstance(objectives, str) and not web_href:
        web_href = objectives
        objectives = intro
        intro = ""
    parts = [f"# {title}"]
    if intro:
        parts.append(intro)
    if web_href:
        parts.append(f"[章节网页]({web_href})")
    if objectives:
        parts.append("## 运行内容\n\n" + "\n".join(f"- {o}" for o in objectives))
    return [md("\n\n".join(parts))]


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
    return [code(_ensure_code_comment("\n".join(lines)))]


def stepcode(*lines: str) -> list[Cell]:
    """每行独立 code cell，便于逐步执行与阅读。"""
    return [code(_ensure_code_comment(line.strip())) for line in lines if line.strip()]


def _ensure_code_comment(source: str) -> str:
    stripped = source.strip()
    if not stripped or stripped.startswith("#"):
        return stripped
    first = stripped.splitlines()[0].strip()
    if first.startswith(("import ", "from ")):
        comment = "# 准备依赖、导入库和实验运行时。"
    elif first.startswith("display("):
        comment = "# 显示当前实验结果表。"
    elif first.startswith("plot_"):
        comment = "# 绘制当前实验图。"
    elif first.startswith("print("):
        comment = "# 输出当前实验结果。"
    elif "fit(" in stripped or "fit_predict(" in stripped:
        comment = "# 调用库模型训练或推断。"
    elif "=" in first:
        comment = "# 保存本步骤变量，供后续代码单元使用。"
    else:
        comment = "# 运行当前实验步骤。"
    return f"{comment}\n{stripped}"


def summary(*paragraphs: str) -> list[Cell]:
    return [md("## 小结\n\n" + "\n\n".join(paragraphs))]


def exercises(*items: str) -> list[Cell]:
    body = "\n".join(f"{i+1}. {t}" for i, t in enumerate(items))
    return [md(f"## 练习\n\n{body}")]


_COMMON_RUNTIME_FILES = [
    "labs/common/mpl_setup.py",
    "labs/common/codelens.py",
    "labs/common/viz_anim.py",
    "labs/common/notebook_helpers.py",
    "labs/common/campus_graph.json",
    "labs/common/ch6_rules.json",
    "labs/common/ch6_kg.json",
    "labs/common/luxun_bpe.json",
]

_CHAPTER_RUNTIME_FILES = {
    "ch05": ["labs/ch05/search_algorithms.py"],
    "ch06": ["labs/ch06/reasoning.py"],
    "ch07": ["labs/ch07/learning.py"],
    "ch08": ["labs/ch08/neural.py"],
    "ch09": ["labs/ch09/bpe.py", "labs/ch09/language.py"],
    "ch10": ["labs/ch10/vision.py"],
    "ch11": ["labs/ch11/rl.py"],
    "ch12": ["labs/ch12/create.py"],
}


def boot(ch: str, imports: str = "") -> str:
    runtime_files = sorted(set(_COMMON_RUNTIME_FILES + _CHAPTER_RUNTIME_FILES[ch]))
    base = f"""
# 准备运行时：若下载单个 ipynb 后本地没有 labs/，会自动拉取所需脚本和数据。
import importlib.util
import subprocess
import sys
from pathlib import Path
from urllib.request import urlretrieve

BASE_URL = "https://raw.githubusercontent.com/zhesun-0209/ai-thinking-labs/main"
RUNTIME_FILES = {runtime_files!r}

ROOT = Path.cwd()
if not (ROOT / "labs").exists() and (ROOT.parent / "labs").exists():
    ROOT = ROOT.parent
if not (ROOT / "labs").exists():
    ROOT = Path.cwd() / "_ai_thinking_labs_runtime"
    for rel in RUNTIME_FILES:
        target = ROOT / rel
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(f"{{BASE_URL}}/{{rel}}", target)

missing = []
for module, package in [
    ("numpy", "numpy>=1.24"),
    ("pandas", "pandas>=2.0"),
    ("matplotlib", "matplotlib>=3.7"),
    ("scipy", "scipy>=1.10"),
    ("sklearn", "scikit-learn>=1.3"),
]:
    if importlib.util.find_spec(module) is None:
        missing.append(package)
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "labs"))
sys.path.insert(0, str(ROOT / "labs" / "{ch}"))
import matplotlib.pyplot as plt
from common.mpl_setup import configure_matplotlib
configure_matplotlib()
from IPython.display import display, Image
print("runtime ready:", ROOT)
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
