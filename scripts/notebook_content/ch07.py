"""第 7 章 notebook — 与 ch5 同等逐步密度。"""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import boot, flatten

B = boot(
    "ch07",
    "from learning import *",
)


def notebooks() -> dict[str, list]:
    return {
        "ch07_decision_tree_kmeans.ipynb": flatten(_tree()),
        "ch07_perceptron_gd.ipynb": flatten(_gd()),
    }


def _tree() -> list:
    return [
        rs.chapter_link(
            "第 7 章 · 决策树与 K-均值",
            "50 道错题与 14 个成绩点：逐步看熵、分裂与簇中心更新。",
            ["计算熵与信息增益", "理解决策树分裂", "K-均值 assign/update 循环", "对照 ch7 网页"],
            "../ch7.html",
        ),
        rs.section("1", "错题分布"),
        rs.reading("50 道题按错误类型统计：计算错误、概念混淆、粗心。根节点熵衡量不确定性。"),
        rs.listing("熵", "H = -sum p_i log2 p_i"),
        *rs.stepcode(
            B,
            "display(error_distribution_df())",
            "display(tree_split_table())",
        ),
        *rs.stepcode("plot_error_pie()"),
        rs.self_check("哪类错误最多？", answer="计算错误 20 题。"),
        rs.section("2", "决策树分裂"),
        rs.subsection("2.1", "根分裂", "问「是否含分数」——左子树纯为计算错误，右子树仍混合。"),
        rs.reading("纯叶节点无需再分；混合子树继续按特征分裂。"),
        rs.self_check("右子树为何还要分？", answer="概念混淆与粗心仍混合，需继续分裂。"),
        rs.section("3", "K-均值聚类"),
        rs.subsection("3.1", "迭代循环", "① 每点分配到最近中心 ② 更新中心为簇内均值 ③ 直到稳定。"),
        rs.listing("K-means", "repeat:\n  labels = argmin ||x - mu_k||\n  mu_k = mean(x in cluster k)"),
        *rs.stepcode(
            "km_frames = codelens_kmeans()",
            "animate_kmeans()",
            "display(kmeans_iteration_table())",
        ),
        *rs.stepcode(
            "kmeans_demo()",
            "plot_kmeans()",
        ),
        rs.self_check("14 点最终簇大小？", answer="约 6+8，与网页演示一致。"),
        rs.section("4", "两种压缩方式对比"),
        rs.reading("**决策树** → 可读 if-then 规则；**K-均值** → 连续空间的簇中心。"),
        rs.summary(
            "熵驱动树分裂；K-均值用几何距离压缩数据。",
            "对照 [ch7.html](../ch7.html) 查看分裂与簇动画。",
        ),
        rs.exercises(
            "若三类错题数量相等，根熵是多少？",
            "K=3 时 14 点会如何分配？",
        ),
    ]


def _gd() -> list:
    return [
        rs.chapter_link(
            "第 7 章 · 感知机与梯度下降",
            "房价 MSE 逐轮下降、感知机边界 b 更新、分类阈值与 P/R。",
            ["梯度下降逐步 trace", "感知机决策边界", "阈值与 P/R 权衡"],
            "../ch7.html",
        ),
        rs.section("1", "梯度下降"),
        rs.reading("最小化 MSE：沿负梯度方向更新权重 w，学习率控制步长。"),
        rs.listing("GD", "w <- w - lr * d(MSE)/dw"),
        *rs.stepcode(
            B,
            "gd_frames = codelens_gd()",
            "display(gd_iteration_table())",
            "plot_gd_mse()",
        ),
        rs.self_check("MSE 从 8420 降到多少？", answer="约 920，单调下降。"),
        rs.section("2", "感知机边界"),
        rs.subsection("2.1", "权重更新", "错分样本推动法向量旋转，边界逐步分开两类。"),
        rs.listing("Perceptron", "if misclassified: w += lr * y * x"),
        *rs.stepcode(
            "perceptron_demo()",
            "plot_perceptron()",
        ),
        rs.self_check("边界 b 最终约多少？", answer="-66，见 plot 图例。"),
        rs.section("3", "阈值与 P/R"),
        rs.reading("分类阈值 τ 影响 TP/FP/FN/TN；提高 τ 通常提高 P、降低 R。"),
        *rs.stepcode(
            "display(metrics_table())",
        ),
        rs.self_check("τ=0.65 时 P 与 R 如何？", answer="P 高 R 低，更保守。"),
        rs.section("4", "两层优化"),
        rs.reading("内层 loss（MSE/hinge）驱动训练；外层 F1/P/R 评泛化，目标不一定同向。"),
        rs.summary(
            "GD 逐步降 loss；感知机找线性可分边界；阈值调 P/R。",
            "对照 [ch7.html](../ch7.html) 查看边界与 MSE 曲线。",
        ),
        rs.exercises(
            "学习率过大时 MSE 曲线会怎样？",
            "感知机对 XOR 数据能收敛吗？",
        ),
    ]
