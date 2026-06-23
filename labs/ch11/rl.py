"""Chapter 11 RL demos — pedagogical API."""

from __future__ import annotations

import math
import random

import matplotlib.pyplot as plt
import numpy as np

GAMMA = 0.9
STATES = ["待搜索", "已比价", "已下单", "已确认"]
STATE_IDS = ["S0", "S1", "S2", "S3"]
REWARDS = [0, 1, 2, 10]


def mdp_demo() -> None:
    total = sum((GAMMA ** i) * r for i, r in enumerate(REWARDS))
    print("订机票 MDP:", " → ".join(STATES))
    print("即时奖励:", REWARDS, f"  折扣回报 G≈{total:.1f} (网页 ≈9.8)")


def plot_mdp_chain() -> None:
    fig, ax = plt.subplots(figsize=(8, 2))
    ax.plot(range(len(STATES)), [0] * len(STATES), "o-", markersize=12, color="#0d6b62")
    for i, (sid, r) in enumerate(zip(STATE_IDS, REWARDS)):
        ax.text(i, 0.15, f"{sid}\nr={r}", ha="center", fontsize=9)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title(f"MDP chain gamma={GAMMA}")
    plt.tight_layout()
    plt.show()


def codelens_value_iteration(max_rounds: int = 6) -> list:
    from common.codelens import Frame

    v = [0.0] * len(STATES)
    frames = [Frame(0, "V=[0,...]", "初始化价值", {"V": [round(x, 2) for x in v]})]
    for rnd in range(1, max_rounds + 1):
        v = [r + GAMMA * (v[i + 1] if i + 1 < len(v) else 0) for i, r in enumerate(REWARDS)]
        frames.append(
            Frame(
                rnd,
                "V(s) <- R + gamma V(s')",
                f"第 {rnd} 轮 Bellman 备份",
                {"V": [round(x, 2) for x in v], "V(S0)": round(v[0], 2)},
            )
        )
    return frames


def animate_value_iteration() -> None:
    from common.viz_anim import animate_bar_values

    frames = codelens_value_iteration()
    snaps = []
    for f in frames:
        v = f.state.get("V", [])
        snaps.append(
            {
                "step": f.step,
                "values": {STATE_IDS[i]: v[i] for i in range(min(len(v), len(STATE_IDS)))},
                "action": f.narrative,
                "highlight": "S0" if f.step > 0 else None,
            }
        )
    animate_bar_values(snaps, title="Value iteration V(s)", ylabel="V", fps=0.9)


def value_iteration() -> list[float]:
    v = [0.0] * len(STATES)
    history = [list(v)]
    for _ in range(10):
        v = [r + GAMMA * (v[i + 1] if i + 1 < len(v) else 0) for i, r in enumerate(REWARDS)]
        history.append(list(v))
    print("收敛 V:", [round(x, 2) for x in v])
    return history[-1]


def plot_value_iteration() -> None:
    v = [0.0] * len(STATES)
    vals = []
    for _ in range(10):
        v = [r + GAMMA * (v[i + 1] if i + 1 < len(v) else 0) for i, r in enumerate(REWARDS)]
        vals.append(v[0])
    fig, ax = plt.subplots()
    ax.plot(range(1, 11), vals, marker="o", color="#0d6b62")
    ax.set_xlabel("iteration")
    ax.set_ylabel("V(S0)")
    ax.set_title("Value iteration")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def td_demo() -> None:
    v_old, r, v_next, alpha = 2.0, 1.0, 4.0, 0.2
    target = r + GAMMA * v_next
    v_new = v_old + alpha * (target - v_old)
    print(f"TD(0): V={v_old}  target={target:.2f}  V'={v_new:.2f} (网页 2.52)")


def epsilon_greedy(eps: float, q: list[float], trials: int = 1000) -> tuple[int, int]:
    random.seed(0)
    explore = exploit = 0
    for _ in range(trials):
        if random.random() < eps:
            explore += 1
        else:
            exploit += 1
    return explore, exploit


def bandit_demo() -> None:
    q = [0.9, 0.7, 0.6]
    for eps in [0.4, 0.15, 0.02]:
        ex, _ = epsilon_greedy(eps, q)
        print(f"ε={eps:.2f} → 探索约 {ex/10:.0f}% (1000 次)")


def plot_epsilon_greedy() -> None:
    q = [0.9, 0.7, 0.6]
    eps_list = [0.4, 0.15, 0.02]
    rates = [epsilon_greedy(e, q)[0] / 10 for e in eps_list]
    fig, ax = plt.subplots()
    ax.bar([str(e) for e in eps_list], rates, color="#0d6b62")
    ax.set_xlabel("ε")
    ax.set_ylabel("explore (%)")
    ax.set_title("Epsilon-greedy explore rate")
    plt.tight_layout()
    plt.show()
