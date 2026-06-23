"""Runestone-style Chapter 7 notebooks."""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import boot, flatten

B = boot("ch07", "from learning import *")


def notebooks() -> dict[str, list]:
    return {
        "ch07_decision_tree_kmeans.ipynb": flatten(_tree()),
        "ch07_perceptron_gd.ipynb": flatten(_gd()),
    }


def _tree() -> list[list]:
    return [
        rs.chapter(
            "第 7 章 · 决策树与 K-均值",
            "Runestone 式：先读概念，再 ActiveCode 看**每一步分裂/迭代**的数据变化。",
            ["理解熵与信息增益", "观察 K-均值中心移动", "对比两种「压缩」"],
        ),
        rs.section("1", "Reading · 学习 = 压缩"),
        rs.reading("决策树把 50 道题**压缩**成 if-else；K-均值把 14 个点**压缩**成 2 个中心。"),
        rs.listing("熵", "H = -Σ p log2 p"),
        *rs.activecode(
            B,
            "display(error_distribution_df())",
            "decision_tree_demo()",
            caption="50 题分布与根熵",
        ),
        *rs.activecode("plot_error_pie()", caption="可视化分布"),
        rs.self_check("根节点为何选「含分数」分裂？", answer="该特征使左右子集更纯（计算错误集中在一侧）。"),
        rs.section("2", "K-均值 CodeLens 式迭代"),
        rs.listing("K-means", "assign → update centers → repeat"),
        *rs.activecode("kmeans_demo()", "plot_kmeans()", caption="14 点 · 初始中心与最终结果"),
        rs.summary("树的可解释性 vs 聚类的几何中心——两种压缩物。"),
    ]


def _gd() -> list[list]:
    return [
        rs.chapter("第 7 章 · 感知机与梯度下降", "内层 MSE 下降 + 外层 P/R 指标。", ["读 MSE 曲线", "读感知机边界", "理解两层优化"]),
        rs.section("1", "梯度下降逐步下降"),
        rs.listing("GD 更新", "w ← w - η ∇MSE"),
        *rs.activecode(B, "gd_demo()", "plot_gd_mse()", caption="MSE 每轮数值 + 曲线"),
        rs.section("2", "感知机边界"),
        *rs.activecode("perceptron_demo()", "plot_perceptron()", caption="b 从 -88 → -66"),
        rs.section("3", "外层指标"),
        *rs.activecode("display(metrics_table())", caption="阈值 τ 对 P/R 的影响"),
        rs.self_check("MSE↓ 是否保证 F1↑？", answer="否；内外层优化目标不同。"),
    ]
