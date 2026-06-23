"""Chapter 7 executable notebooks."""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import boot, flatten

B = boot("ch07", "from learning import *")


def notebooks() -> dict[str, list]:
    return {
        "ch07_decision_tree_kmeans.ipynb": flatten(_tree()),
        "ch07_perceptron_gd.ipynb": flatten(_gd()),
    }


def _tree() -> list:
    return [
        rs.chapter_link(
            "第 7 章 · 决策树与 KMeans",
            ["调用 sklearn 决策树", "调用 sklearn KMeans", "输出模型结果和图"],
            "../ch7.html",
        ),
        rs.section("0", "环境与数据"),
        *rs.stepcode(
            B,
            "# 查看用于训练决策树的小数据集分布。\ndisplay(error_distribution_df())",
        ),
        rs.section("1", "DecisionTreeClassifier"),
        *rs.stepcode(
            "# 直接调用 sklearn 的 DecisionTreeClassifier，而不是手写分裂过程。\nX_tree, y_tree, feature_names, class_names = decision_tree_dataset()\ntree = DecisionTreeClassifier(max_depth=2, random_state=0)\ntree.fit(X_tree, y_tree)",
            "# 查看 sklearn 训练出的特征重要度和树结构。\ndisplay(decision_tree_summary(tree, feature_names, class_names))\nprint_decision_tree(tree, feature_names)",
        ),
        rs.section("2", "KMeans"),
        *rs.stepcode(
            "# 直接调用 sklearn 的 KMeans 拟合二维成绩点。\nkmeans = KMeans(n_clusters=2, init=KMEANS_INIT, n_init=1, random_state=0)\nlabels = kmeans.fit_predict(KMEANS_PTS)",
            "# 输出聚类中心、簇大小，并绘制 sklearn 模型结果。\ndisplay(kmeans_result_table(kmeans, labels))\nplot_kmeans_model(kmeans, labels)",
        ),
    ]


def _gd() -> list:
    return [
        rs.chapter_link(
            "第 7 章 · 感知机与梯度下降",
            ["运行梯度下降", "运行感知机", "输出阈值指标"],
            "../ch7.html",
        ),
        rs.section("0", "环境与数据"),
        *rs.stepcode(
            B,
            "# 输出预设的梯度下降迭代表，用于复现实验曲线。\ndisplay(gd_iteration_table())",
            "# 绘制 MSE 随迭代下降的曲线。\nplot_gd_mse()",
        ),
        rs.section("1", "感知机"),
        *rs.stepcode(
            "# 调用实验函数输出感知机边界参数更新。\nperceptron_demo()",
            "# 绘制最终线性边界。\nplot_perceptron()",
        ),
        rs.section("2", "阈值指标"),
        *rs.stepcode(
            "# 输出不同阈值下的 P/R 指标表。\ndisplay(metrics_table())",
        ),
    ]
