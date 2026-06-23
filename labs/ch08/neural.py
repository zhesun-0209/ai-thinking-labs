"""Chapter 8 neural demos — aligned with ch8.js."""

from __future__ import annotations

import numpy as np

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


def forward_demo() -> None:
    z1 = W1 @ X + B1
    h = relu(z1)
    y = sigmoid(float(W2 @ h + B2))
    print(f"x={X} → h≈{h.round(2)} → ŷ={y:.2f} (网页 {Y_HAT})")


def backward_demo() -> None:
    y = Y_HAT
    delta_out = y * (1 - y) * (y - 1)
    delta_h = (W2 * delta_out) * (H > 0)
    print(f"δ_out={delta_out:.3f} (网页 0.036)")
    print(f"δ_h={delta_h.round(3)} (网页 [0.018, 0.011])")


def transe_demo() -> None:
    d_pos, d_neg = 0.31, 2.08
    print(f"正例 (鲁迅,创作,呐喊) d+={d_pos:.2f}")
    print(f"负例尾「红楼梦」 d-={d_neg:.2f}")
    print(f"margin loss: max(0, {d_pos:.2f}+1-{d_neg:.2f})={max(0, d_pos+1-d_neg):.2f}")


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
