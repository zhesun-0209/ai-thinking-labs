"""Chapter 12 creation demos — numpy / stdlib only."""

from __future__ import annotations

import math
import random


def annealing_demo() -> None:
    losses = [12.4, 8.1, 3.2, 2.3]
    reprs = ["代数", "代数+退火", "几何", "几何"]
    print("| 步骤 | 表征 | loss |")
    print("|------|------|------|")
    for i, (r, l) in enumerate(zip(reprs, losses)):
        print(f"| {i} | {r} | {l} |")


def mcts_uct(q: float, n: int, N: int, c: float = 1.4) -> float:
    if n == 0:
        return float("inf")
    return q / n + c * math.sqrt(math.log(N + 1) / n)


def mcts_demo() -> None:
    stats = {"a": (2, 5), "b": (3, 4)}
    N = sum(n for _, n in stats.values())
    print("UCT 分数 (Q/N + explore):")
    for k, (q, n) in stats.items():
        print(f"  {k}: {mcts_uct(q, n, N):.3f}")
    print("选择 b → 扩展 c → rollout → 回传胜率 0.62")


def diffusion_1d() -> None:
    x0, steps = 1.0, 5
    x = x0
    print("1D 前向加噪 → 反向去噪 (玩具):")
    for t in range(steps):
        noise = random.gauss(0, 0.3)
        x = x + noise
        print(f"  t={t+1} x={x:.3f}")
    print("U-Net 预测噪声 ε 逐步减噪 (概念与 ch12 网页一致)")


def gan_toy() -> None:
    d_fake = [0.18, 0.08, 0.74, 0.50]
    print("D(x̂) 训练轨迹:", " → ".join(f"{v:.2f}" for v in d_fake))


def alphafold_outline() -> None:
    steps = ["输入氨基酸序列", "MSA 共变", "Evoformer", "3D 坐标 + pLDDT"]
    for i, s in enumerate(steps):
        print(f"{i+1}. {s}")
