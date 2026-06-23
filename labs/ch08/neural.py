"""Chapter 8 neural demos — pedagogical API."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

X = np.array([6.2, 0.8])
H = np.array([0.71, 0.45])
Y_HAT = 0.82
W1 = np.array([[0.3, 0.2], [0.1, 0.4]])
W2 = np.array([0.5, 0.3])
B1 = np.array([0.0, 0.0])
B2 = 0.0


def relu(z: np.ndarray) -> np.ndarray:
    return np.maximum(0, z)


def sigmoid(z: float) -> float:
    return 1 / (1 + np.exp(-z))


def forward_trace() -> pd.DataFrame:
    z1 = W1 @ X + B1
    h = relu(z1)
    y = sigmoid(float(W2 @ h + B2))
    return pd.DataFrame(
        [
            {"阶段": "输入 x", "值": str(X.round(2))},
            {"阶段": "z1=W1x+b1", "值": str(z1.round(2))},
            {"阶段": "h=ReLU(z1)", "值": str(h.round(2))},
            {"阶段": "ŷ=σ(W2h+b2)", "值": f"{y:.2f} (网页 {Y_HAT})"},
        ]
    )


def forward_demo() -> None:
    print(forward_trace().to_string(index=False))


def backward_demo() -> None:
    y = Y_HAT
    delta_out = y * (1 - y) * (y - 1)
    delta_h = (W2 * delta_out) * (H > 0)
    print(f"δ_out={delta_out:.3f} (网页 0.036)")
    print(f"δ_h={delta_h.round(3)} (网页 [0.018, 0.011])")


def plot_mlp_flow() -> None:
    fig, ax = plt.subplots(figsize=(8, 3))
    layers = ["x₁,x₂", "h₁,h₂", "ŷ"]
    xs = [0, 1, 2]
    ax.scatter(xs, [0, 0, 0], s=200, c=["#3498db", "#0d6b62", "#e67e22"])
    for i in range(len(xs) - 1):
        ax.annotate("", xy=(xs[i + 1], 0), xytext=(xs[i], 0), arrowprops=dict(arrowstyle="->", lw=2))
    ax.set_xticks(xs)
    ax.set_xticklabels(layers)
    ax.set_yticks([])
    ax.set_title("MLP 前向：血糖+运动 → 风险概率")
    plt.tight_layout()
    plt.show()


def transe_demo() -> None:
    d_pos, d_neg = 0.31, 2.08
    print(f"正例 (鲁迅,创作,呐喊) d+={d_pos:.2f}")
    print(f"负例尾「红楼梦」 d-={d_neg:.2f}")
    print(f"margin loss: max(0, {d_pos:.2f}+1-{d_neg:.2f})={max(0, d_pos+1-d_neg):.2f}")


def plot_transe() -> None:
    fig, ax = plt.subplots()
    h = np.array([0.0, 0.0])
    r = np.array([1.0, 0.5])
    t_pos = h + r
    t_neg = np.array([2.5, 1.8])
    ax.scatter(*h, s=120, label="鲁迅 h")
    ax.scatter(*t_pos, s=120, label="呐喊 t+")
    ax.scatter(*t_neg, s=120, label="红楼梦 t-")
    ax.arrow(h[0], h[1], r[0], r[1], head_width=0.08, color="#0d6b62", length_includes_head=True)
    ax.set_title("TransE：h + r ≈ t（向量平移）")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


def attention_demo() -> None:
    tokens = ["鲁迅", "写", "日记"]
    scores = np.array([0.4, 2.1, 0.3])
    w = softmax(scores)
    target = np.array([0.05, 0.80, 0.15])
    print("tokens:", tokens)
    for t, s, a, e in zip(tokens, scores, w, target):
        print(f"  {t}: score={s:.1f} α={a:.2f} (网页 {e:.2f})")


def plot_attention() -> None:
    tokens = ["鲁迅", "写", "日记"]
    weights = np.array([0.05, 0.80, 0.15])
    fig, ax = plt.subplots()
    ax.bar(tokens, weights, color="#0d6b62")
    ax.set_ylim(0, 1)
    ax.set_title("Cross-Attention：解码「日记」时对 Encoder 的权重")
    ax.set_ylabel("α (softmax)")
    plt.tight_layout()
    plt.show()
