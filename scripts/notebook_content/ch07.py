"""Rich notebook cells for chapter 7."""

from __future__ import annotations

from notebook_content import callout, code, md, section

BOOT = """
import sys
from pathlib import Path
ROOT = Path.cwd()
if not (ROOT / "labs").exists() and (ROOT.parent / "labs").exists():
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "labs" / "ch07"))
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "Arial Unicode MS", "DejaVu Sans"]
from IPython.display import display
from learning import *
""".strip()


def notebooks() -> dict[str, list]:
    return {
        "ch07_decision_tree_kmeans.ipynb": _tree_kmeans(),
        "ch07_perceptron_gd.ipynb": _perceptron(),
    }


def _tree_kmeans() -> list:
    return [
        md(
            """# 第 7 章 · 决策树与 K-均值

> 配套 [ch7.html](../ch7.html) · **18 分钟**

**带走什么**：学习 = **压缩数据**——树压缩成 if-else 规则，K-均值压缩成簇中心。"""
        ),
        section("1. 决策树：50 道错题诊断", "根节点问「是否含分数」——信息增益最大的分裂。"),
        code(
            f"""{BOOT}
display(error_distribution_df())
decision_tree_demo()"""
        ),
        code("plot_error_pie()"),
        callout("误区", "树越深不一定越好——网页演示右子树仍混有概念/粗心，继续分裂才纯化。"),
        section("2. K-均值：成绩散点聚类", "无标签时，用簇中心代表两组学生。"),
        code("kmeans_demo()"),
        code("plot_kmeans()"),
        callout("自测", "K-均值与决策树的「压缩物」分别是什么？（簇中心 vs 可读规则）"),
        md("回到 [ch7.html](../ch7.html) 看树的分裂动画与 K-均值中心移动。"),
    ]


def _perceptron() -> list:
    return [
        md("# 第 7 章 · 感知机与梯度下降\n\n> 配套 [ch7.html](../ch7.html)"),
        section("1. 梯度下降：内层优化", "内层用 MSE 拟合训练信号；曲线单调下降。"),
        code(f"{BOOT}\ngd_demo()\nplot_gd_mse()"),
        section("2. 感知机：线性分类边界", "错分样本推动边界平移——b 从 -88 逐步到 -66。"),
        code("perceptron_demo()\nplot_perceptron()"),
        section("3. 外层指标：P / R 随阈值变化", "同一模型，不同 τ 在精确率与召回率间权衡。"),
        code("display(metrics_table())"),
        callout("小结", "内层 loss ↓ 不等于外层 F1 ↑——第 7 章强调两层优化。"),
    ]
