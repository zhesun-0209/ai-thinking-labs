"""Rich notebook cells for chapter 8."""

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
sys.path.insert(0, str(ROOT / "labs" / "ch08"))
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "Arial Unicode MS", "DejaVu Sans"]
from IPython.display import display
from neural import *
""".strip()


def notebooks() -> dict[str, list]:
    b = _boot()
    return {
        "ch08_mlp_backprop.ipynb": [
            md("# 第 8 章 · MLP 前向与反向传播\n\n> 配套 [ch8.html](../ch8.html) · 案例：血糖+运动 → 风险"),
            section("1. 前向传播：计算图流水线", "数据沿层流动；ReLU 截断负值；Sigmoid 输出概率。"),
            code(f"{b}\ndisplay(forward_trace())\nplot_mlp_flow()"),
            callout("误区", "前向不只推理时用——训练每个 batch 都要重算并**保存激活 a** 供反向用。"),
            section("2. 反向传播：误差分责任", "链式法则从 δ_out 回传到各层权重。"),
            code("backward_demo()"),
            callout("自测", "若隐藏层 ReLU 输出全为 0，该层还能收到梯度吗？（ReLU′=0 则截断）"),
        ],
        "ch08_transe_attention.ipynb": [
            md("# 第 8 章 · TransE 与 Cross-Attention\n\n> 配套 [ch8.html](../ch8.html)"),
            section("1. TransE：关系 = 向量平移", "h + r ≈ t；负采样推远错误尾实体。"),
            code(f"{b}\ntranse_demo()\nplot_transe()"),
            section("2. Attention：软查询对齐", "Q 来自 Decoder，K/V 来自 Encoder；Softmax 权重和为 1。"),
            code("attention_demo()\nplot_attention()"),
            callout("小结", "连接智能 = 可微流水线 + 嵌入几何 + 软对齐三种心智模型。"),
        ],
    }
