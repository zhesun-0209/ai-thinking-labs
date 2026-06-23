"""Chapter 9 language demos — pedagogical API."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

VOCAB = ["鲁迅", "写", "了", "狂人", "日记", "桌子"]
PAIRS = [("鲁迅", "写"), ("写", "了"), ("了", "狂人"), ("狂人", "日记")]
NEG = ("鲁迅", "桌子")


def skipgram_demo(steps: int = 50, lr: float = 0.1) -> None:
    rng = np.random.default_rng(0)
    dim = 4
    emb = rng.normal(0, 0.1, (len(VOCAB), dim))
    idx = {w: i for i, w in enumerate(VOCAB)}
    center, pos = "鲁迅", "写"
    sim_before = float(emb[idx[center]] @ emb[idx[pos]])
    for _ in range(steps):
        v_c, v_p = emb[idx[center]], emb[idx[pos]]
        grad = (1 - sim_before) * v_p
        emb[idx[center]] += lr * grad * 0.01
        emb[idx[pos]] += lr * grad * 0.01
    sim_after = float(emb[idx[center]] @ emb[idx[pos]])
    print(f"Skip-gram 鲁迅→写 相似度 {sim_before:.2f} → {sim_after:.2f} (网页 0.42→0.68)")


def plot_skipgram_sim() -> None:
    fig, ax = plt.subplots()
    ax.plot([0, 50], [0.42, 0.68], marker="o", color="#0d6b62", linewidth=2)
    ax.set_xlabel("训练步")
    ax.set_ylabel("cos(鲁迅, 写)")
    ax.set_title("Skip-gram：共现词向量靠近")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def self_attention_matrix() -> pd.DataFrame:
    tokens = ["鲁迅", "写", "了", "狂人", "日记"]
    scores = np.array([1.2, 0.3, 0.1, 0.4, 0.2])
    w = np.exp(scores) / np.exp(scores).sum()
    return pd.DataFrame({"token": tokens, "score": scores, "α": w.round(2)})


def plot_attention_heatmap() -> None:
    tokens = ["鲁迅", "写", "了", "狂人", "日记"]
    w = self_attention_matrix()["α"].values
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.imshow(w.reshape(1, -1), cmap="Greens", aspect="auto")
    ax.set_xticks(range(len(tokens)))
    ax.set_xticklabels(tokens)
    ax.set_yticks([0])
    ax.set_yticklabels(["Q=写"])
    ax.set_title("Self-Attention：「写」对全句的权重")
    plt.tight_layout()
    plt.show()


def char_lm_demo() -> None:
    text = "鲁迅写了狂人日记"
    print("字符 bigram（下一字符预测）:")
    for i in range(len(text) - 1):
        print(f"  P({text[i+1]} | {text[i]})")
