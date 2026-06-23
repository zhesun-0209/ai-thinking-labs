"""Chapter 7 learning demos — aligned with ch7.js."""

from __future__ import annotations

import math

import numpy as np
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier

ERROR_COUNTS = [20, 18, 12]  # 计算错误, 概念混淆, 粗心
ERROR_LABELS = ["计算错误", "概念混淆", "粗心"]

GD_POINTS = np.array(
    [[38, 86], [42, 88], [55, 110], [60, 118], [72, 130], [78, 142], [85, 150], [92, 158]],
    dtype=float,
)
GD_MSE = [8420, 5200, 3100, 1800, 920]

PERCEPTRON_PTS = np.array(
    [[52, 48, 0], [58, 55, 0], [61, 52, 0], [48, 62, 0], [72, 78, 1], [78, 82, 1], [85, 88, 1], [90, 92, 1]],
    dtype=float,
)
PERCEPTRON_B = [-88, -78, -72, -66]

KMEANS_PTS = np.array(
    [
        [35, 88], [38, 84], [40, 90], [42, 86], [36, 82], [39, 91], [41, 87],
        [70, 64], [72, 68], [74, 62], [76, 66], [73, 70], [75, 63], [71, 67],
    ],
    dtype=float,
)
KMEANS_INIT = np.array([[38, 86], [74, 66]], dtype=float)


def entropy(counts: list[int]) -> float:
    total = sum(counts)
    return -sum((c / total) * math.log2(c / total) for c in counts if c)


def decision_tree_demo() -> None:
    print(f"50 题分布: {dict(zip(ERROR_LABELS, ERROR_COUNTS))}")
    print(f"根熵 H={entropy(ERROR_COUNTS):.3f}")
    left = [20, 0, 0]
    right = [0, 18, 12]
    print(f"分裂「含分数」→ 左叶 {left[0]} 纯计算错误; 右子树 概念/粗心 {right[1:]}")


def kmeans_demo() -> None:
    km = KMeans(n_clusters=2, init=KMEANS_INIT, n_init=1, max_iter=20)
    labels = km.fit_predict(KMEANS_PTS)
    c0, c1 = (labels == 0).sum(), (labels == 1).sum()
    print(f"14 点 → 簇大小 {c0} + {c1} (网页演示最终 6+8)")
    print(f"中心: {km.cluster_centers_.round(1).tolist()}")


def perceptron_demo() -> None:
    print("感知机边界 b 更新:", " → ".join(str(b) for b in PERCEPTRON_B))


def gd_demo() -> None:
    print("MSE 下降:", " → ".join(str(m) for m in GD_MSE))


def metrics_demo() -> None:
    rows = [
        (0.35, 42, 28, 8, 22),
        (0.50, 38, 12, 12, 38),
        (0.65, 30, 4, 20, 46),
    ]
    print("| τ | TP | FP | FN | TN | P | R |")
    print("|---|----|----|----|----|---|---|")
    for tau, tp, fp, fn, tn in rows:
        p = tp / (tp + fp)
        r = tp / (tp + fn)
        print(f"| {tau} | {tp} | {fp} | {fn} | {tn} | {p:.2f} | {r:.2f} |")
