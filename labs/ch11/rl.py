"""Chapter 11 RL demos — aligned with ch11.js."""

from __future__ import annotations

import math
import random

GAMMA = 0.9
STATES = ["待搜索", "已比价", "已下单", "已确认"]
REWARDS = [0, 1, 2, 10]


def mdp_demo() -> None:
    g = 0
    total = 0
    for i, r in enumerate(REWARDS):
        total += (GAMMA ** i) * r
    print("订机票 MDP 状态链:", " → ".join(STATES))
    print("奖励:", REWARDS, f"折扣回报 G≈{total:.1f} (网页 ≈9.8)")


def value_iteration() -> None:
    v = [0.0] * len(STATES)
    for _ in range(10):
        v = [r + GAMMA * (v[i + 1] if i + 1 < len(v) else 0) for i, r in enumerate(REWARDS)]
    print("价值迭代 V:", [round(x, 2) for x in v])


def td_demo() -> None:
    v_old, r, v_next, alpha = 2.0, 1.0, 4.0, 0.2
    target = r + GAMMA * v_next
    v_new = v_old + alpha * (target - v_old)
    print(f"V(s)={v_old} → target={target:.2f} → V新={v_new:.2f} (网页 2.52)")


def epsilon_greedy(eps: float, q: list[float], trials: int = 1000) -> tuple[int, int]:
    random.seed(0)
    explore = exploit = 0
    for _ in range(trials):
        if random.random() < eps:
            explore += 1
            arm = random.randint(0, len(q) - 1)
        else:
            exploit += 1
            arm = max(range(len(q)), key=lambda i: q[i])
    return explore, exploit


def bandit_demo() -> None:
    q = [0.9, 0.7, 0.6]
    for eps in [0.4, 0.15, 0.02]:
        ex, _ = epsilon_greedy(eps, q)
        print(f"ε={eps:.2f} → 探索约 {ex/10:.0f}% (1000 次模拟)")
