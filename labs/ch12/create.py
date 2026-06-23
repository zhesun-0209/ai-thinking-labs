"""Chapter 12 creation demos — pedagogical API."""

from __future__ import annotations

import math
import random

import matplotlib.pyplot as plt
import numpy as np


def annealing_demo() -> None:
    losses = [12.4, 8.1, 3.2, 2.3]
    reprs = ["代数", "代数+退火", "几何", "几何"]
    print("| 步骤 | 表征 | loss |")
    for i, (r, l) in enumerate(zip(reprs, losses)):
        print(f"| {i} | {r} | {l} |")


def plot_annealing() -> None:
    losses = [12.4, 8.1, 3.2, 2.3]
    fig, ax = plt.subplots()
    ax.plot(range(len(losses)), losses, marker="o", color="#0d6b62", linewidth=2)
    ax.set_xlabel("搜索步骤")
    ax.set_ylabel("loss")
    ax.set_title("表征搜索 + 模拟退火：换表征跳出局部最优")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def mcts_uct(q: float, n: int, N: int, c: float = 1.4) -> float:
    if n == 0:
        return float("inf")
    return q / n + c * math.sqrt(math.log(N + 1) / n)


def mcts_demo() -> None:
    stats = {"a": (2, 5), "b": (3, 4)}
    N = sum(n for _, n in stats.values())
    print("UCT = Q/N + c·√(ln N / n):")
    for k, (q, n) in stats.items():
        print(f"  走法 {k}: Q={q}, n={n} → UCT={mcts_uct(q, n, N):.3f}")


def plot_uct() -> None:
    stats = {"a": (2, 5), "b": (3, 4), "c": (0, 0)}
    N = sum(n for _, n in stats.values())
    keys = list(stats.keys())
    scores = [mcts_uct(q, n, N) for q, n in stats.values()]
    fig, ax = plt.subplots()
    ax.bar(keys, scores, color="#0d6b62")
    ax.set_title("MCTS：未访问节点 c 的 UCT=∞，优先探索")
    plt.tight_layout()
    plt.show()


def diffusion_1d() -> None:
    random.seed(0)
    x0, steps = 1.0, 5
    xs = [x0]
    x = x0
    for _ in range(steps):
        x += random.gauss(0, 0.3)
        xs.append(x)
    print("前向加噪 x:", [round(v, 3) for v in xs])
    return xs


def plot_diffusion_1d(xs: list[float] | None = None) -> None:
    if xs is None:
        random.seed(0)
        xs = [1.0]
        x = 1.0
        for _ in range(5):
            x += random.gauss(0, 0.3)
            xs.append(x)
    fig, ax = plt.subplots()
    ax.plot(range(len(xs)), xs, marker="o", color="#3498db", label="前向加噪")
    ax.plot(range(len(xs)-1, -1, -1), xs[::-1], marker="x", color="#0d6b62", label="反向去噪(概念)")
    ax.set_title("1D 玩具扩散")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def gan_toy() -> None:
    d_fake = [0.18, 0.08, 0.74, 0.50]
    print("D(生成样本) 概率:", " → ".join(f"{v:.2f}" for v in d_fake))


def plot_gan_d() -> None:
    d_fake = [0.18, 0.08, 0.74, 0.50]
    fig, ax = plt.subplots()
    ax.plot(range(len(d_fake)), d_fake, marker="o", color="#e74c3c", linewidth=2)
    ax.axhline(0.5, color="gray", linestyle="--", label="理想 D=0.5")
    ax.set_title("GAN：判别器对假样本的输出轨迹")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def alphafold_outline() -> None:
    steps = ["输入氨基酸序列", "MSA 共变", "Evoformer", "3D 坐标 + pLDDT"]
    for i, s in enumerate(steps):
        print(f"{i+1}. {s}")
