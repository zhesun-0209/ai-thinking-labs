"""Chapter 9 language demos beyond BPE."""

from __future__ import annotations

import numpy as np

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
        grad = (1 - sim_before) * v_p  # toy
        emb[idx[center]] += lr * grad * 0.01
        emb[idx[pos]] += lr * grad * 0.01
    sim_after = float(emb[idx[center]] @ emb[idx[pos]])
    print(f"Skip-gram 鲁迅→写 相似度 {sim_before:.2f} → {sim_after:.2f} (网页 0.42→0.68)")


def self_attention_matrix() -> None:
    tokens = ["鲁迅", "写", "了", "狂人", "日记"]
    q_idx = 1
    scores = np.array([1.2, 0.3, 0.1, 0.4, 0.2])
    w = np.exp(scores) / np.exp(scores).sum()
    print("Q(写) 对全句 softmax 权重:")
    for t, a in zip(tokens, w):
        print(f"  {t}: α={a:.2f}")
    print(f"最高: 鲁迅 score=1.2 (网页 α(鲁迅)=0.35)")


def char_lm_demo() -> None:
    text = "鲁迅写了狂人日记"
    print("字符 bigram 计数（下一字符预测）:")
    for i in range(len(text) - 1):
        print(f"  P({text[i+1]}|{text[i]})")
