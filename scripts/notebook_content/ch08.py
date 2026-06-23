"""Runestone-style Chapters 8–12 notebooks (single module)."""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import boot, flatten


def notebooks() -> dict[str, list]:
    out: dict[str, list] = {}
    out.update(_ch08())
    out.update(_ch09())
    out.update(_ch10())
    out.update(_ch11())
    out.update(_ch12())
    return out


def _ch08() -> dict[str, list]:
    B = boot("ch08", "from neural import *")
    return {
        "ch08_mlp_backprop.ipynb": flatten([
            rs.chapter("第 8 章 · MLP 前向与反向", "逐层 ActiveCode + 中间变量表。", ["跟踪 x→h→ŷ", "读 δ 回传"]),
            rs.section("1", "前向传播 CodeLens"),
            rs.listing("MLP", "z1=W1x+b1; h=ReLU(z1); ŷ=σ(W2h+b2)"),
            *rs.activecode(B, "display(forward_trace())", "plot_mlp_flow()"),
            rs.section("2", "反向传播"),
            *rs.activecode("backward_demo()"),
            rs.self_check("ReLU 全 0 时隐藏层梯度？", answer="ReLU′=0 截断，几乎无梯度。"),
        ]),
        "ch08_transe_attention.ipynb": flatten([
            rs.chapter("第 8 章 · TransE 与 Attention", "几何嵌入 + 软对齐权重。", ["TransE 平移", "Attention softmax"]),
            *rs.activecode(B, "transe_demo()", "plot_transe()"),
            *rs.activecode("attention_demo()", "plot_attention()"),
        ]),
    }


def _ch09() -> dict[str, list]:
    B = boot("ch09", "from bpe import *\nfrom common.codelens import print_frames as print_codelens")
    return {
        "ch09_bpe.ipynb": flatten([
            rs.chapter("第 9 章 · BPE", "CodeLens：每次 merge 前后 token 序列。", ["数 pair 频次", "逐步 merge"]),
            rs.section("1", "Reading · 子词划分"),
            rs.listing("BPE", "count pairs → merge max → repeat"),
            *rs.activecode(B, "demo_first_merge()"),
            rs.section("2", "CodeLens · 全部合并步"),
            *rs.activecode("frames = codelens_bpe_merges()", "print_codelens(frames)"),
            *rs.activecode("display(steps_table())", "print_steps()"),
        ]),
        "ch09_skipgram_toy.ipynb": flatten([
            rs.chapter("第 9 章 · Skip-gram", "共现拉近向量。", ["读相似度变化"]),
            *rs.activecode(boot("ch09", "from language import *"), "skipgram_demo()", "plot_skipgram_sim()"),
        ]),
        "ch09_attention_lm.ipynb": flatten([
            rs.chapter("第 9 章 · Self-Attention 与 LM", "权重矩阵 + bigram。", ["读 α 分布"]),
            *rs.activecode(boot("ch09", "from language import *"), "display(self_attention_matrix())", "plot_attention_heatmap()", "char_lm_demo()"),
        ]),
    }


def _ch10() -> dict[str, list]:
    B = boot("ch10", "from vision import *")
    return {
        "ch10_conv2d_numpy.ipynb": flatten([
            rs.chapter("第 10 章 · 卷积", "输入→卷积→池化逐步。", ["读 2×2 特征图"]),
            rs.listing("conv2d", "滑动窗口求和"),
            *rs.activecode(B, "conv_demo()", "plot_conv()"),
        ]),
        "ch10_vit_patchify.ipynb": flatten([
            rs.chapter("第 10 章 · ViT Patchify", "4×4→4 token。", ["读 patch 像素"]),
            *rs.activecode(B, "vit_patchify()", "plot_patches()"),
        ]),
        "ch10_mae_masking.ipynb": flatten([
            rs.chapter("第 10 章 · MAE", "75% 掩码。", ["Encoder 只看 25%"]),
            *rs.activecode(B, "mae_demo()", "plot_mae_mask()"),
        ]),
        "ch10_clip_infonce.ipynb": flatten([
            rs.chapter("第 10 章 · CLIP", "正负 cos。", ["InfoNCE 几何"]),
            *rs.activecode(B, "clip_infonce()", "plot_clip_cos()"),
        ]),
    }


def _ch11() -> dict[str, list]:
    B = boot("ch11", "from rl import *")
    return {
        "ch11_mdp_value_iteration.ipynb": flatten([
            rs.chapter("第 11 章 · MDP", "状态链 + 价值迭代。", ["读 V 收敛"]),
            *rs.activecode(B, "mdp_demo()", "plot_mdp_chain()", "value_iteration()", "plot_value_iteration()"),
        ]),
        "ch11_td_learning.ipynb": flatten([
            rs.chapter("第 11 章 · TD(0)", "bootstrap 更新。", ["读 target"]),
            *rs.activecode(B, "td_demo()"),
        ]),
        "ch11_epsilon_greedy.ipynb": flatten([
            rs.chapter("第 11 章 · ε-贪心", "探索/利用。", ["读 ε"]),
            *rs.activecode(B, "bandit_demo()", "plot_epsilon_greedy()"),
        ]),
    }


def _ch12() -> dict[str, list]:
    B = boot("ch12", "from create import *")
    return {
        "ch12_repr_search_annealing.ipynb": flatten([
            rs.chapter("第 12 章 · 退火", "换表征降 loss。", ["读 loss 轨迹"]),
            *rs.activecode(B, "annealing_demo()", "plot_annealing()"),
        ]),
        "ch12_mcts.ipynb": flatten([
            rs.chapter("第 12 章 · MCTS", "UCT 逐步。", ["读 explore"]),
            *rs.activecode(B, "mcts_demo()", "plot_uct()"),
        ]),
        "ch12_diffusion_1d.ipynb": flatten([
            rs.chapter("第 12 章 · 1D 扩散", "加噪序列。", ["读 x"]),
            *rs.activecode(B, "xs=diffusion_1d()", "plot_diffusion_1d(xs)"),
        ]),
        "ch12_gan_toy.ipynb": flatten([
            rs.chapter("第 12 章 · GAN", "D 轨迹。", ["读 D(x̂)"]),
            *rs.activecode(B, "gan_toy()", "plot_gan_d()"),
        ]),
        "ch12_diffusion_toy.ipynb": flatten([
            rs.chapter("第 12 章 · 扩散概念", "1D 玩具。", ["逆过程"]),
            *rs.activecode(B, "xs=diffusion_1d()", "plot_diffusion_1d(xs)"),
        ]),
        "ch12_alphafold_concepts.ipynb": flatten([
            rs.chapter("第 12 章 · AlphaFold", "四阶段。", ["对应网页"]),
            *rs.activecode(B, "alphafold_outline()"),
        ]),
    }
