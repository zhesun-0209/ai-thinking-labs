"""Chapter 7 learning demos — pedagogical API."""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier, export_text

ERROR_COUNTS = [20, 18, 12]
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


def error_distribution_df() -> pd.DataFrame:
    return pd.DataFrame({"类型": ERROR_LABELS, "题数": ERROR_COUNTS})


def decision_tree_dataset() -> tuple[np.ndarray, np.ndarray, list[str], list[str]]:
    """Small labeled dataset for sklearn DecisionTreeClassifier."""
    x = np.array([[1, 0]] * 20 + [[0, 1]] * 18 + [[0, 0]] * 12, dtype=int)
    y = np.array([0] * 20 + [1] * 18 + [2] * 12, dtype=int)
    feature_names = ["含分数", "抽象概念"]
    class_names = ERROR_LABELS
    return x, y, feature_names, class_names


def decision_tree_summary(model: DecisionTreeClassifier, feature_names: list[str], class_names: list[str]) -> pd.DataFrame:
    """Summarize a fitted sklearn decision tree for notebook display."""
    return pd.DataFrame(
        {
            "特征": feature_names,
            "重要度": np.round(model.feature_importances_, 3),
        }
    ).assign(类别=", ".join(class_names))


def print_decision_tree(model: DecisionTreeClassifier, feature_names: list[str]) -> None:
    """Print sklearn's own tree text export."""
    print(export_text(model, feature_names=feature_names))


def decision_tree_demo() -> None:
    print(f"50 题分布: {dict(zip(ERROR_LABELS, ERROR_COUNTS))}")
    print(f"根熵 H={entropy(ERROR_COUNTS):.3f}")
    left = [20, 0, 0]
    right = [0, 18, 12]
    print(f"分裂「含分数」→ 左叶 {left[0]} 纯计算错误; 右子树 概念/粗心 {right[1:]}")


def tree_split_table() -> pd.DataFrame:
    left = [20, 0, 0]
    right = [0, 18, 12]
    return pd.DataFrame(
        [
            {"节点": "根节点", "样本": sum(ERROR_COUNTS), "分布": dict(zip(ERROR_LABELS, ERROR_COUNTS)), "熵": round(entropy(ERROR_COUNTS), 3), "下一步": "按「含分数」分裂"},
            {"节点": "左叶", "样本": sum(left), "分布": dict(zip(ERROR_LABELS, left)), "熵": round(entropy(left), 3), "下一步": "停止"},
            {"节点": "右子树", "样本": sum(right), "分布": dict(zip(ERROR_LABELS, right)), "熵": round(entropy(right), 3), "下一步": "继续区分概念/粗心"},
        ]
    )


def plot_error_pie() -> None:
    fig, ax = plt.subplots()
    ax.pie(ERROR_COUNTS, labels=["calc", "concept", "careless"], autopct="%1.0f%%", colors=["#0d6b62", "#3498db", "#e67e22"])
    ax.set_title("Error types (50 questions)")
    plt.tight_layout()
    plt.show()


def kmeans_demo() -> None:
    km = KMeans(n_clusters=2, init=KMEANS_INIT, n_init=1, max_iter=20)
    labels = km.fit_predict(KMEANS_PTS)
    c0, c1 = (labels == 0).sum(), (labels == 1).sum()
    print(f"14 点 → 簇大小 {c0} + {c1} (网页演示最终 6+8)")
    print(f"中心: {km.cluster_centers_.round(1).tolist()}")


def kmeans_result_table(model: KMeans, labels: np.ndarray) -> pd.DataFrame:
    """Summarize a fitted sklearn KMeans model."""
    rows = []
    for k, center in enumerate(model.cluster_centers_):
        rows.append(
            {
                "簇": k,
                "中心 x": round(float(center[0]), 2),
                "中心 y": round(float(center[1]), 2),
                "样本数": int((labels == k).sum()),
            }
        )
    return pd.DataFrame(rows)


def plot_kmeans_model(model: KMeans, labels: np.ndarray) -> None:
    fig, ax = plt.subplots()
    for lab, color in [(0, "#0d6b62"), (1, "#e67e22")]:
        m = labels == lab
        ax.scatter(KMEANS_PTS[m, 0], KMEANS_PTS[m, 1], c=color, s=60, label=f"cluster {lab}")
    ax.scatter(KMEANS_INIT[:, 0], KMEANS_INIT[:, 1], c="red", marker="x", s=120, label="init centers")
    ax.scatter(model.cluster_centers_[:, 0], model.cluster_centers_[:, 1], c="black", marker="*", s=150, label="final centers")
    ax.set_title("K-means: 14 points, 2 clusters")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_kmeans() -> None:
    km = KMeans(n_clusters=2, init=KMEANS_INIT, n_init=1, max_iter=20)
    labels = km.fit_predict(KMEANS_PTS)
    plot_kmeans_model(km, labels)


def perceptron_demo() -> None:
    print("感知机边界 b 更新:", " → ".join(str(b) for b in PERCEPTRON_B))


def plot_perceptron() -> None:
    fig, ax = plt.subplots()
    c0 = PERCEPTRON_PTS[PERCEPTRON_PTS[:, 2] == 0]
    c1 = PERCEPTRON_PTS[PERCEPTRON_PTS[:, 2] == 1]
    ax.scatter(c0[:, 0], c0[:, 1], c="#3498db", label="fail")
    ax.scatter(c1[:, 0], c1[:, 1], c="#0d6b62", label="pass")
    x = np.linspace(45, 95, 50)
    ax.plot(x, -(1.0 * x + PERCEPTRON_B[-1]) / 1.2, "r--", label=f"boundary b={PERCEPTRON_B[-1]}")
    ax.set_title("Perceptron decision boundary")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def gd_demo() -> None:
    print("MSE 下降:", " → ".join(str(m) for m in GD_MSE))


def plot_gd_mse() -> None:
    fig, ax = plt.subplots()
    ax.plot(range(1, len(GD_MSE) + 1), GD_MSE, marker="o", color="#0d6b62", linewidth=2)
    ax.set_xlabel("iteration")
    ax.set_ylabel("MSE")
    ax.set_title("GD: MSE vs iteration")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def metrics_table() -> pd.DataFrame:
    rows = []
    for tau, tp, fp, fn, tn in [
        (0.35, 42, 28, 8, 22),
        (0.50, 38, 12, 12, 38),
        (0.65, 30, 4, 20, 46),
    ]:
        p = tp / (tp + fp)
        r = tp / (tp + fn)
        rows.append({"阈值τ": tau, "TP": tp, "FP": fp, "FN": fn, "TN": tn, "P": round(p, 2), "R": round(r, 2)})
    return pd.DataFrame(rows)


def metrics_demo() -> None:
    print(metrics_table().to_string(index=False))


def codelens_gd() -> list:
    from common.codelens import Frame

    w = 0.0
    frames = [Frame(0, "w=0", "初始权重", {"w": w, "MSE": GD_MSE[0]})]
    mse_vals = [8420, 5200, 3100, 1800, 920]
    for i, mse in enumerate(mse_vals[1:], start=1):
        w += 0.15
        frames.append(Frame(i, f"w -= lr*grad  # iter {i}", f"第 {i} 轮梯度下降", {"w": round(w, 2), "MSE": mse}))
    return frames


def gd_iteration_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"轮次": f.step, "w": f.state["w"], "MSE": f.state["MSE"], "动作": f.narrative}
            for f in codelens_gd()
        ]
    )


def codelens_kmeans(max_iter: int = 3) -> list:
    from common.codelens import Frame

    centers = KMEANS_INIT.copy()
    frames = [Frame(0, "init centers", "初始簇中心", {"centers": centers.round(1).tolist()})]
    for it in range(1, max_iter + 1):
        dists = np.linalg.norm(KMEANS_PTS[:, None, :] - centers[None, :, :], axis=2)
        labels = dists.argmin(axis=1)
        for k in range(2):
            mask = labels == k
            if mask.any():
                centers[k] = KMEANS_PTS[mask].mean(axis=0)
        frames.append(
            Frame(
                it,
                "assign + update mu",
                f"第 {it} 轮：分配点后更新中心",
                {
                    "labels": labels.tolist(),
                    "centers": centers.round(1).tolist(),
                    "cluster_sizes": [(labels == 0).sum(), (labels == 1).sum()],
                },
            )
        )
    return frames


def kmeans_iteration_table() -> pd.DataFrame:
    rows = []
    for f in codelens_kmeans():
        centers = f.state["centers"]
        sizes = f.state.get("cluster_sizes", ["—", "—"])
        rows.append(
            {
                "轮次": f.step,
                "C0 中心": centers[0],
                "C1 中心": centers[1],
                "簇大小": sizes,
                "动作": f.narrative,
            }
        )
    return pd.DataFrame(rows)


def animate_kmeans() -> None:
    from common.viz_anim import animate_bar_values

    frames = codelens_kmeans()
    snaps = []
    for f in frames:
        centers = f.state.get("centers", [[0, 0], [0, 0]])
        snaps.append(
            {
                "step": f.step,
                "values": {"C0_x": centers[0][0], "C0_y": centers[0][1], "C1_x": centers[1][0], "C1_y": centers[1][1]},
                "action": f.narrative,
                "extra": str(f.state.get("cluster_sizes", "")),
            }
        )
    animate_bar_values(snaps, title="K-means cluster centers", ylabel="coord", fps=0.8)
