#!/usr/bin/env python3
"""Generate all chapter Jupyter notebooks from manifest."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

try:
    import nbformat
    from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
except ImportError as exc:
    raise SystemExit("pip install nbformat") from exc

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks"

SETUP = """import sys
from pathlib import Path
ROOT = Path.cwd()
if not (ROOT / "labs").exists() and (ROOT.parent / "labs").exists():
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
"""

NOTEBOOKS: dict[str, list[tuple[str, str]]] = {
    "ch05_campus_search.ipynb": [
        ("md", "# 《AI思维》第 5 章 · 校园图搜索\n\n配套 [ch5.html](../ch5.html)。运行下方单元格复现六种搜索路径。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch05'))\nfrom search_algorithms import print_comparison\nprint_comparison()"),
    ],
    "ch06_forward_backward_chain.ipynb": [
        ("md", "# 前向链与后向链\n\n配套 [ch6.html](../ch6.html) · 苏格拉底三段论规则库。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch06'))\nfrom reasoning import forward_chain\nfor line in forward_chain():\n    print(line)"),
        ("code", f"from reasoning import backward_chain\nfor line in backward_chain():\n    print(line)"),
    ],
    "ch06_graph_reasoning.ipynb": [
        ("md", "# 图谱多跳与路径排序\n\n鲁迅/莫言知识图谱，与 ch6 实验室一致。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch06'))\nfrom reasoning import graph_multihop\nfor line in graph_multihop():\n    print(line)"),
        ("code", "from reasoning import path_ranking\npath_ranking()"),
    ],
    "ch07_decision_tree_kmeans.ipynb": [
        ("md", "# 决策树与 K-均值\n\n配套 [ch7.html](../ch7.html) · 50 道错题案例。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch07'))\nfrom learning import decision_tree_demo, kmeans_demo\ndecision_tree_demo()\nprint()\nkmeans_demo()"),
    ],
    "ch07_perceptron_gd.ipynb": [
        ("md", "# 感知机与梯度下降\n\nMSE 下降曲线与感知机边界更新。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch07'))\nfrom learning import gd_demo, perceptron_demo, metrics_demo\ngd_demo()\nprint()\nperceptron_demo()\nprint()\nmetrics_demo()"),
    ],
    "ch08_mlp_backprop.ipynb": [
        ("md", "# 小 MLP 前向与反向传播\n\n配套 [ch8.html](../ch8.html) · 血糖+运动 → 风险。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch08'))\nfrom neural import forward_demo, backward_demo\nforward_demo()\nprint()\nbackward_demo()"),
    ],
    "ch08_transe_attention.ipynb": [
        ("md", "# TransE 与 Cross-Attention\n\n与 ch8 注意力步进数字对齐。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch08'))\nfrom neural import transe_demo, attention_demo\ntranse_demo()\nprint()\nattention_demo()"),
    ],
    "ch09_bpe.ipynb": [
        ("md", "# BPE 字节对合并\n\n配套 [ch9.html](../ch9.html) · 「鲁迅 写 了 狂人 日记」。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch09'))\nfrom bpe import print_steps\nprint_steps()"),
    ],
    "ch09_skipgram_toy.ipynb": [
        ("md", "# Skip-gram 玩具词表\n\n中心词「鲁迅」预测上下文「写」。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch09'))\nfrom language import skipgram_demo\nskipgram_demo()"),
    ],
    "ch09_attention_lm.ipynb": [
        ("md", "# Self-Attention 与字符 LM"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch09'))\nfrom language import self_attention_matrix, char_lm_demo\nself_attention_matrix()\nprint()\nchar_lm_demo()"),
    ],
    "ch10_conv2d_numpy.ipynb": [
        ("md", "# 4×4 卷积与 MaxPool\n\n配套 [ch10.html](../ch10.html)"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch10'))\nfrom vision import conv_demo\nconv_demo()"),
    ],
    "ch10_vit_patchify.ipynb": [
        ("md", "# ViT Patch 词元化"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch10'))\nfrom vision import vit_patchify\nvit_patchify()"),
    ],
    "ch10_mae_masking.ipynb": [
        ("md", "# MAE 75% 掩码"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch10'))\nfrom vision import mae_demo\nmae_demo()"),
    ],
    "ch10_clip_infonce.ipynb": [
        ("md", "# CLIP InfoNCE（向量版）\n\n无 torch，用 numpy 演示对比损失几何。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch10'))\nfrom vision import clip_infonce\nclip_infonce()"),
    ],
    "ch11_mdp_value_iteration.ipynb": [
        ("md", "# MDP 与价值迭代\n\n配套 [ch11.html](../ch11.html) · 订机票四状态。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch11'))\nfrom rl import mdp_demo, value_iteration\nmdp_demo()\nprint()\nvalue_iteration()"),
    ],
    "ch11_td_learning.ipynb": [
        ("md", "# TD(0) 学习"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch11'))\nfrom rl import td_demo\ntd_demo()"),
    ],
    "ch11_epsilon_greedy.ipynb": [
        ("md", "# ε-贪心多臂老虎机"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch11'))\nfrom rl import bandit_demo\nbandit_demo()"),
    ],
    "ch12_repr_search_annealing.ipynb": [
        ("md", "# 表征搜索与模拟退火\n\n配套 [ch12.html](../ch12.html)"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch12'))\nfrom create import annealing_demo\nannealing_demo()"),
    ],
    "ch12_mcts.ipynb": [
        ("md", "# MCTS 与 UCT"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch12'))\nfrom create import mcts_demo\nmcts_demo()"),
    ],
    "ch12_diffusion_1d.ipynb": [
        ("md", "# 1D 玩具扩散（numpy）"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch12'))\nfrom create import diffusion_1d\ndiffusion_1d()"),
    ],
    "ch12_gan_toy.ipynb": [
        ("md", "# GAN 判别器曲线（概念）"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch12'))\nfrom create import gan_toy\ngan_toy()"),
    ],
    "ch12_diffusion_toy.ipynb": [
        ("md", "# 扩散去噪流程（与 ch12 网页步骤对照）\n\n完整 DDPM 需本地 torch；此处复用 1D 玩具演示流程。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch12'))\nfrom create import diffusion_1d\ndiffusion_1d()"),
    ],
    "ch12_alphafold_concepts.ipynb": [
        ("md", "# AlphaFold 流程（概念）\n\n不下载权重，仅列出与 ch12 架构步进对应的阶段。"),
        ("code", f"{SETUP}sys.path.insert(0, str(ROOT / 'labs' / 'ch12'))\nfrom create import alphafold_outline\nalphafold_outline()"),
    ],
}


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
    print(f"generated {path.relative_to(ROOT)}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, cells in NOTEBOOKS.items():
        write_notebook(name, cells)


if __name__ == "__main__":
    main()
