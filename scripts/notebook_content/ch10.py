"""Rich notebook cells for chapters 10-12."""

from __future__ import annotations

from notebook_content import callout, code, md, section


def _boot(ch: str, mod: str) -> str:
    return f"""
import sys
from pathlib import Path
ROOT = Path.cwd()
if not (ROOT / "labs").exists() and (ROOT.parent / "labs").exists():
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "labs" / "{ch}"))
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "Arial Unicode MS", "DejaVu Sans"]
from {mod} import *
""".strip()


def notebooks() -> dict[str, list]:
    return {
        "ch10_conv2d_numpy.ipynb": _conv(),
        "ch10_vit_patchify.ipynb": _vit(),
        "ch10_mae_masking.ipynb": _mae(),
        "ch10_clip_infonce.ipynb": _clip(),
        "ch11_mdp_value_iteration.ipynb": _mdp(),
        "ch11_td_learning.ipynb": _td(),
        "ch11_epsilon_greedy.ipynb": _bandit(),
        "ch12_repr_search_annealing.ipynb": _anneal(),
        "ch12_mcts.ipynb": _mcts(),
        "ch12_diffusion_1d.ipynb": _diff1d(),
        "ch12_gan_toy.ipynb": _gan(),
        "ch12_diffusion_toy.ipynb": _diff_toy(),
        "ch12_alphafold_concepts.ipynb": _af(),
    }


def _conv() -> list:
    b = _boot("ch10", "vision")
    return [
        md("# 第 10 章 · 4×4 卷积与 MaxPool\n\n> 配套 [ch10.html](../ch10.html)"),
        section("1. CNN 归纳偏置", "局部连接 + 权值共享 → 先扫局部模式再池化。"),
        code(f"{b}\nconv_demo()\nplot_conv()"),
        callout("小结", "卷积输出 2×2，MaxPool 取 11——与网页 CNN 流水线数字一致。"),
    ]


def _vit() -> list:
    b = _boot("ch10", "vision")
    return [
        md("# 第 10 章 · ViT Patch 词元化"),
        section("1. 从像素到 token", "4×4 图切成 4 个 2×2 patch，类比 NLP 的「词」。"),
        code(f"{b}\nvit_patchify()\nplot_patches()"),
    ]


def _mae() -> list:
    b = _boot("ch10", "vision")
    return [
        md("# 第 10 章 · MAE 75% 掩码"),
        code(f"{b}\nmae_demo()\nplot_mae_mask()"),
        callout("误区", "Encoder 不看被遮 patch——节省算力；Decoder 才重构全图像素。"),
    ]


def _clip() -> list:
    b = _boot("ch10", "vision")
    return [
        md("# 第 10 章 · CLIP InfoNCE"),
        code(f"{b}\nclip_infonce()\nplot_clip_cos()"),
    ]


def _mdp() -> list:
    b = _boot("ch11", "rl")
    return [
        md("# 第 11 章 · MDP 与价值迭代\n\n> 配套 [ch11.html](../ch11.html) · 订机票四状态"),
        section("1. Agent–Env 交互环", "s → a → r, s′ 循环；γ 折扣未来奖励。"),
        code(f"{b}\nmdp_demo()\nplot_mdp_chain()"),
        section("2. 价值迭代", "Bellman 备份直到 V 收敛。"),
        code("value_iteration()\nplot_value_iteration()"),
    ]


def _td() -> list:
    b = _boot("ch11", "rl")
    return [
        md("# 第 11 章 · TD(0) 学习"),
        section("1. 自举 bootstrap", "用下一步估计 V(s′) 更新 V(s)，不必等到 episode 结束。"),
        code(f"{b}\ntd_demo()"),
    ]


def _bandit() -> list:
    b = _boot("ch11", "rl")
    return [
        md("# 第 11 章 · ε-贪心多臂老虎机"),
        code(f"{b}\nbandit_demo()\nplot_epsilon_greedy()"),
        callout("小结", "ε 大→多探索；ε 小→多利用已知最优臂。"),
    ]


def _anneal() -> list:
    b = _boot("ch12", "create")
    return [
        md("# 第 12 章 · 表征搜索与模拟退火\n\n> 配套 [ch12.html](../ch12.html)"),
        code(f"{b}\nannealing_demo()\nplot_annealing()"),
    ]


def _mcts() -> list:
    b = _boot("ch12", "create")
    return [
        md("# 第 12 章 · MCTS 与 UCT"),
        code(f"{b}\nmcts_demo()\nplot_uct()"),
        callout("心智模型", "不必展开全博弈树——采样 + UCT 平衡利用与探索。"),
    ]


def _diff1d() -> list:
    b = _boot("ch12", "create")
    return [
        md("# 第 12 章 · 1D 玩具扩散"),
        code(f"{b}\nxs = diffusion_1d()\nplot_diffusion_1d(xs)"),
    ]


def _gan() -> list:
    b = _boot("ch12", "create")
    return [
        md("# 第 12 章 · GAN 判别器曲线"),
        code(f"{b}\ngan_toy()\nplot_gan_d()"),
    ]


def _diff_toy() -> list:
    b = _boot("ch12", "create")
    return [
        md("# 第 12 章 · 扩散去噪流程\n\n完整 DDPM 需 GPU；此处用 1D 玩具理解「加噪→学 ε→去噪」。"),
        code(f"{b}\nxs = diffusion_1d()\nplot_diffusion_1d(xs)"),
    ]


def _af() -> list:
    b = _boot("ch12", "create")
    return [
        md("# 第 12 章 · AlphaFold 流程（概念）"),
        code(f"{b}\nalphafold_outline()"),
        md("不下载权重；与 ch12 网页架构步进四阶段一一对应。"),
    ]
