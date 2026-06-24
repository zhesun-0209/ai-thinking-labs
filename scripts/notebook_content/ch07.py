"""第 7 章 · 机器学习代码实验。"""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import flatten


DEPENDENCIES_CELL = """
# 导入实验库，并设置图表中文显示。
import importlib.util
import logging
import subprocess
import sys
import warnings
from pathlib import Path

required_packages = {
    "numpy": "numpy>=1.24",
    "pandas": "pandas>=2.0",
    "matplotlib": "matplotlib>=3.7",
    "sklearn": "scikit-learn>=1.3",
}
missing = [package for module, package in required_packages.items() if importlib.util.find_spec(module) is None]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from IPython.display import display
from sklearn.cluster import KMeans
from sklearn.linear_model import Perceptron, SGDRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, precision_recall_fscore_support
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree

font_paths = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
]
font_name = "DejaVu Sans"
for path in font_paths:
    if Path(path).exists():
        fm.fontManager.addfont(path)
        font_name = fm.FontProperties(fname=path).get_name()
        break

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")
plt.rcParams.update({
    "figure.dpi": 110,
    "axes.unicode_minus": False,
    "font.family": "sans-serif",
    "font.sans-serif": [font_name, "DejaVu Sans", "sans-serif"],
})
"""


TREE_DATA_CELL = """
# 准备学生练习数据：特征进入模型，标签表示是否已经掌握。
tree_df = pd.DataFrame(
    [
        {"正确率": 0.92, "复盘次数": 3, "按时提交": 1, "掌握": 1},
        {"正确率": 0.85, "复盘次数": 2, "按时提交": 1, "掌握": 1},
        {"正确率": 0.78, "复盘次数": 2, "按时提交": 1, "掌握": 1},
        {"正确率": 0.73, "复盘次数": 3, "按时提交": 0, "掌握": 1},
        {"正确率": 0.66, "复盘次数": 1, "按时提交": 1, "掌握": 0},
        {"正确率": 0.60, "复盘次数": 2, "按时提交": 0, "掌握": 0},
        {"正确率": 0.58, "复盘次数": 0, "按时提交": 1, "掌握": 0},
        {"正确率": 0.52, "复盘次数": 1, "按时提交": 0, "掌握": 0},
        {"正确率": 0.48, "复盘次数": 0, "按时提交": 0, "掌握": 0},
        {"正确率": 0.88, "复盘次数": 1, "按时提交": 1, "掌握": 1},
    ]
)

feature_names = ["正确率", "复盘次数", "按时提交"]
class_names = ["未掌握", "已掌握"]
X_tree = tree_df[feature_names]
y_tree = tree_df["掌握"]
display(tree_df)
"""


TREE_MODEL_CELL = """
# 训练 sklearn 决策树，并输出每个样本的预测。
tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=1, random_state=0)
tree.fit(X_tree, y_tree)

tree_pred = tree.predict(X_tree)
tree_result = tree_df.copy()
tree_result["预测"] = tree_pred
tree_result["预测含义"] = np.where(tree_pred == 1, "已掌握", "未掌握")
tree_result["预测正确"] = tree_result["预测"].eq(tree_result["掌握"])
display(tree_result)
print("训练集准确率:", round(accuracy_score(y_tree, tree_pred), 3))
"""


TREE_PROCESS_CELL = """
# 查看树的分裂规则和特征贡献。
importance_df = pd.DataFrame(
    {"特征": feature_names, "重要度": tree.feature_importances_}
).sort_values("重要度", ascending=False)

print(export_text(tree, feature_names=feature_names))
display(importance_df)
"""


TREE_PLOT_CELL = """
# 绘制 sklearn 训练出的树结构。
fig, ax = plt.subplots(figsize=(9.5, 5.2))
plot_tree(
    tree,
    feature_names=feature_names,
    class_names=class_names,
    filled=True,
    rounded=True,
    impurity=False,
    ax=ax,
)
ax.set_title("决策树分裂路径", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


KMEANS_DATA_CELL = """
# 准备二维学习行为点：横轴是测验分，纵轴是项目分。
kmeans_points = pd.DataFrame(
    {
        "学生": ["A", "B", "C", "D", "E", "F", "G", "H"],
        "测验分": [92, 88, 85, 79, 62, 58, 54, 49],
        "项目分": [86, 82, 90, 76, 60, 55, 49, 45],
    }
)
X_cluster = kmeans_points[["测验分", "项目分"]].to_numpy()
display(kmeans_points)
"""


KMEANS_PROCESS_CELL = """
# 用 sklearn KMeans 连续跑几个单步迭代，观察中心如何移动。
centers = np.array([[58.0, 55.0], [88.0, 84.0]])
center_rows = []
label_history = []

for iteration in range(1, 5):
    km_step = KMeans(n_clusters=2, init=centers, n_init=1, max_iter=1, random_state=0)
    labels = km_step.fit_predict(X_cluster)
    centers = km_step.cluster_centers_
    label_history.append(labels)
    for cluster_id, (cx, cy) in enumerate(centers):
        center_rows.append({
            "迭代": iteration,
            "簇": cluster_id,
            "中心_测验分": round(cx, 2),
            "中心_项目分": round(cy, 2),
            "簇内样本数": int((labels == cluster_id).sum()),
        })

kmeans = KMeans(n_clusters=2, init=centers, n_init=1, max_iter=50, random_state=0)
final_labels = kmeans.fit_predict(X_cluster)
kmeans_points["簇"] = final_labels

centers_df = pd.DataFrame(center_rows)
display(centers_df)
display(kmeans_points)
"""


KMEANS_PLOT_CELL = """
# 绘制最终聚类结果和中心移动轨迹。
fig, ax = plt.subplots(figsize=(7.8, 5.6))
palette = np.array(["#2563eb", "#f97316"])
ax.scatter(
    kmeans_points["测验分"],
    kmeans_points["项目分"],
    c=palette[final_labels],
    s=130,
    edgecolors="white",
    linewidth=1.6,
)
for _, row in kmeans_points.iterrows():
    ax.text(row["测验分"] + 0.9, row["项目分"] + 0.9, row["学生"], fontsize=9, color="#334155")

for cluster_id in sorted(centers_df["簇"].unique()):
    path = centers_df[centers_df["簇"] == cluster_id]
    ax.plot(path["中心_测验分"], path["中心_项目分"], "--", color=palette[cluster_id], linewidth=1.8)
    ax.scatter(
        [kmeans.cluster_centers_[cluster_id, 0]],
        [kmeans.cluster_centers_[cluster_id, 1]],
        marker="X",
        s=230,
        color=palette[cluster_id],
        edgecolors="#0f172a",
        linewidth=1.0,
    )

ax.set_title("KMeans 聚类与中心移动", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xlabel("测验分")
ax.set_ylabel("项目分")
ax.grid(True, color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
"""


GD_DATA_CELL = """
# 准备线性回归数据：学习时长预测测验分。
gd_df = pd.DataFrame(
    {
        "学习时长": [1, 2, 3, 4, 5, 6, 7, 8],
        "测验分": [52, 55, 61, 66, 70, 76, 82, 86],
    }
)
X_gd = gd_df[["学习时长"]].to_numpy()
y_gd = gd_df["测验分"].to_numpy()
display(gd_df)
"""


GD_PROCESS_CELL = """
# 用 sklearn SGDRegressor 逐轮更新，记录损失下降过程。
regressor = SGDRegressor(
    loss="squared_error",
    penalty=None,
    learning_rate="constant",
    eta0=0.002,
    random_state=0,
)

gd_rows = []
for epoch in range(1, 31):
    regressor.partial_fit(X_gd, y_gd)
    pred = regressor.predict(X_gd)
    gd_rows.append({
        "轮次": epoch,
        "斜率": round(regressor.coef_[0], 4),
        "截距": round(regressor.intercept_[0], 4),
        "MSE": round(mean_squared_error(y_gd, pred), 3),
    })

gd_trace = pd.DataFrame(gd_rows)
display(gd_trace.tail(8))
"""


GD_PLOT_CELL = """
# 绘制拟合直线和 MSE 曲线。
fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.5))

x_line = np.linspace(X_gd.min(), X_gd.max(), 100).reshape(-1, 1)
axes[0].scatter(X_gd[:, 0], y_gd, s=110, color="#2563eb", edgecolor="white", linewidth=1.4)
axes[0].plot(x_line[:, 0], regressor.predict(x_line), color="#f97316", linewidth=2.4)
axes[0].set_title("SGDRegressor 拟合结果", loc="left", fontweight="bold")
axes[0].set_xlabel("学习时长")
axes[0].set_ylabel("测验分")
axes[0].grid(True, color="#e2e8f0", linewidth=0.8)

axes[1].plot(gd_trace["轮次"], gd_trace["MSE"], color="#2563eb", linewidth=2.4)
axes[1].set_title("损失下降", loc="left", fontweight="bold")
axes[1].set_xlabel("轮次")
axes[1].set_ylabel("MSE")
axes[1].grid(True, color="#e2e8f0", linewidth=0.8)

plt.tight_layout()
plt.show()
"""


PERCEPTRON_DATA_CELL = """
# 准备二分类点：两个特征对应一个掌握/未掌握标签。
perceptron_df = pd.DataFrame(
    {
        "正确率": [0.90, 0.82, 0.78, 0.70, 0.58, 0.52, 0.46, 0.40],
        "复盘次数": [3, 3, 2, 2, 1, 1, 0, 0],
        "掌握": [1, 1, 1, 1, 0, 0, 0, 0],
    }
)
X_per = perceptron_df[["正确率", "复盘次数"]].to_numpy()
y_per = perceptron_df["掌握"].to_numpy()
display(perceptron_df)
"""


PERCEPTRON_PROCESS_CELL = """
# 用 sklearn Perceptron 的 partial_fit 逐轮学习，记录边界参数。
perceptron = Perceptron(eta0=0.2, random_state=1, warm_start=True)
classes = np.array([0, 1])
per_rows = []

for epoch in range(1, 9):
    perceptron.partial_fit(X_per, y_per, classes=classes)
    pred = perceptron.predict(X_per)
    per_rows.append({
        "轮次": epoch,
        "w_正确率": round(perceptron.coef_[0, 0], 4),
        "w_复盘次数": round(perceptron.coef_[0, 1], 4),
        "bias": round(perceptron.intercept_[0], 4),
        "错误数": int((pred != y_per).sum()),
    })

per_trace = pd.DataFrame(per_rows)
display(per_trace)
"""


PERCEPTRON_PLOT_CELL = """
# 绘制感知机决策边界。
fig, ax = plt.subplots(figsize=(7.6, 5.2))
colors = np.where(y_per == 1, "#2563eb", "#f97316")
ax.scatter(X_per[:, 0], X_per[:, 1], c=colors, s=130, edgecolors="white", linewidth=1.5)

x_min, x_max = X_per[:, 0].min() - 0.05, X_per[:, 0].max() + 0.05
x_line = np.linspace(x_min, x_max, 100)
w0, w1 = perceptron.coef_[0]
bias = perceptron.intercept_[0]
y_line = -(w0 * x_line + bias) / w1
ax.plot(x_line, y_line, color="#0f172a", linewidth=2.2)

ax.set_title("Perceptron 决策边界", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xlabel("正确率")
ax.set_ylabel("复盘次数")
ax.set_xlim(x_min, x_max)
ax.set_ylim(-0.25, 3.35)
ax.grid(True, color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
"""


METRICS_CELL = """
# 同一组概率在不同阈值下会产生不同的 precision / recall。
y_true = np.array([1, 1, 1, 0, 0, 0])
y_score = np.array([0.91, 0.74, 0.62, 0.55, 0.37, 0.21])

metric_rows = []
for threshold in [0.3, 0.5, 0.7]:
    y_hat = (y_score >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_hat, average="binary", zero_division=0
    )
    metric_rows.append({
        "阈值": threshold,
        "预测为正": int(y_hat.sum()),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "F1": round(f1, 3),
    })

display(pd.DataFrame(metric_rows))
"""


def notebooks() -> dict[str, list]:
    return {
        "ch07_decision_tree_kmeans.ipynb": flatten(_tree()),
        "ch07_perceptron_gd.ipynb": flatten(_gd()),
    }


def _tree() -> list:
    return [
        rs.chapter_link(
            "第 7 章 · 决策树与 KMeans 代码实验",
            ["训练 sklearn 决策树", "观察 KMeans 中心移动", "绘制模型结果"],
            "../ch7.html",
        ),
        rs.section("0", "环境与数据"),
        rs.code(DEPENDENCIES_CELL),
        rs.code(TREE_DATA_CELL),
        rs.section("1", "DecisionTreeClassifier"),
        rs.code(TREE_MODEL_CELL),
        rs.code(TREE_PROCESS_CELL),
        rs.code(TREE_PLOT_CELL),
        rs.section("2", "KMeans"),
        rs.code(KMEANS_DATA_CELL),
        rs.code(KMEANS_PROCESS_CELL),
        rs.code(KMEANS_PLOT_CELL),
    ]


def _gd() -> list:
    return [
        rs.chapter_link(
            "第 7 章 · 梯度下降与感知机代码实验",
            ["记录 SGD 损失下降", "记录感知机参数变化", "比较不同分类阈值"],
            "../ch7.html",
        ),
        rs.section("0", "环境与数据"),
        rs.code(DEPENDENCIES_CELL),
        rs.code(GD_DATA_CELL),
        rs.section("1", "SGDRegressor"),
        rs.code(GD_PROCESS_CELL),
        rs.code(GD_PLOT_CELL),
        rs.section("2", "Perceptron"),
        rs.code(PERCEPTRON_DATA_CELL),
        rs.code(PERCEPTRON_PROCESS_CELL),
        rs.code(PERCEPTRON_PLOT_CELL),
        rs.section("3", "阈值指标"),
        rs.code(METRICS_CELL),
    ]
