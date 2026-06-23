"""Rich notebook cells for chapter 9."""

from __future__ import annotations

from notebook_content import callout, code, md, section


def _boot() -> str:
    return """
import sys
from pathlib import Path
ROOT = Path.cwd()
if not (ROOT / "labs").exists() and (ROOT.parent / "labs").exists():
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "labs" / "ch09"))
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "Arial Unicode MS", "DejaVu Sans"]
from IPython.display import display
""".strip()


def notebooks() -> dict[str, list]:
    return {
        "ch09_bpe.ipynb": _bpe(),
        "ch09_skipgram_toy.ipynb": _skipgram(),
        "ch09_attention_lm.ipynb": _attn_lm(),
    }


def _bpe() -> list:
    b = _boot() + "\nfrom bpe import *"
    return [
        md("# 第 9 章 · BPE 字节对合并\n\n> 配套 [ch9.html](../ch9.html) · 语料：「鲁迅写了狂人日记」"),
        section("1. 语言 Pipeline 第一步", "BPE 把字符序列压缩成**子词表**——与网页步进动画同一合并顺序。"),
        callout("预测", "初始序列里，哪一对相邻 token 出现次数最多？"),
        code(f"{b}\ndemo_first_merge()"),
        code("display(steps_table())"),
        section("2. 逐步合并", "每次合并最高频 pair，直到词表够用。"),
        code("print_steps()"),
        md("**Pipeline 位置**：BPE → 向量(Skip-gram) → Self-Attn → LM。下一本 notebook 继续。"),
    ]


def _skipgram() -> list:
    b = _boot() + "\nfrom language import *"
    return [
        md("# 第 9 章 · Skip-gram 玩具词表"),
        section("1. 分布式语义", "共现的「鲁迅」与「写」在训练中向量靠近。"),
        code(f"{b}\nskipgram_demo()\nplot_skipgram_sim()"),
    ]


def _attn_lm() -> list:
    b = _boot() + "\nfrom language import *"
    return [
        md("# 第 9 章 · Self-Attention 与字符 LM"),
        code(f"{b}\ndisplay(self_attention_matrix())\nplot_attention_heatmap()"),
        code("char_lm_demo()"),
        callout("小结", "Self-Attn 并行看全句；字符 LM 用 bigram 演示链式 P(w_t|w_{t-1})。"),
    ]
