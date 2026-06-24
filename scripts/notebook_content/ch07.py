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
from sklearn.datasets import load_diabetes, load_iris, load_wine
from sklearn.decomposition import PCA
from sklearn.linear_model import Perceptron, SGDRegressor
from sklearn.metrics import (
    accuracy_score,
    adjusted_rand_score,
    confusion_matrix,
    mean_squared_error,
    precision_recall_fscore_support,
    silhouette_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
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
# 加载 Wine 经典分类数据集：13 个化学特征预测 3 类葡萄酒。
wine = load_wine(as_frame=True)
tree_df = wine.frame.copy()
feature_names = wine.feature_names
class_names = list(wine.target_names)
tree_df["类别名称"] = tree_df["target"].map(dict(enumerate(class_names)))

X_tree = tree_df[feature_names]
y_tree = tree_df["target"]

summary_df = pd.DataFrame(
    {
        "样本数": [len(tree_df)],
        "特征数": [len(feature_names)],
        "类别数": [len(class_names)],
    }
)
display(summary_df)
display(tree_df.head(8))
display(tree_df["类别名称"].value_counts().rename_axis("类别").reset_index(name="样本数"))
"""


TREE_MODEL_CELL = """
# 划分训练集和测试集，再训练 sklearn 决策树。
X_train, X_test, y_train, y_test = train_test_split(
    X_tree,
    y_tree,
    test_size=0.28,
    stratify=y_tree,
    random_state=7,
)

tree = DecisionTreeClassifier(max_depth=4, min_samples_leaf=3, random_state=7)
tree.fit(X_train, y_train)

train_pred = tree.predict(X_train)
test_pred = tree.predict(X_test)
score_df = pd.DataFrame(
    [
        {"数据": "训练集", "样本数": len(y_train), "accuracy": accuracy_score(y_train, train_pred)},
        {"数据": "测试集", "样本数": len(y_test), "accuracy": accuracy_score(y_test, test_pred)},
    ]
).round(3)
display(score_df)

test_result = X_test.copy()
test_result["真实类别"] = [class_names[i] for i in y_test]
test_result["预测类别"] = [class_names[i] for i in test_pred]
test_result["预测正确"] = test_result["真实类别"].eq(test_result["预测类别"])
display(test_result.head(12))
"""


TREE_PROCESS_CELL = """
# 查看分裂规则、特征重要性和混淆矩阵。
importance_df = pd.DataFrame(
    {"特征": feature_names, "重要性": tree.feature_importances_}
).sort_values("重要性", ascending=False)
importance_df["累计重要性"] = importance_df["重要性"].cumsum()

confusion_df = pd.DataFrame(
    confusion_matrix(y_test, test_pred),
    index=[f"真实_{name}" for name in class_names],
    columns=[f"预测_{name}" for name in class_names],
)

print(export_text(tree, feature_names=feature_names, max_depth=3))
display(importance_df.head(10).round(3))
display(confusion_df)
"""


TREE_PLOT_CELL = """
# 绘制树结构和特征重要性条形图。
fig, ax = plt.subplots(figsize=(12.0, 6.3))
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

top_importance = importance_df.head(8).sort_values("重要性")
fig, ax = plt.subplots(figsize=(8.4, 5.0))
ax.barh(top_importance["特征"], top_importance["重要性"], color="#2563eb")
ax.set_title("特征重要性 Top 8", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xlabel("importance")
ax.grid(True, axis="x", color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
"""


KMEANS_DATA_CELL = """
# 加载 Iris 鸢尾花数据集，用四个形态特征做聚类。
iris = load_iris(as_frame=True)
iris_df = iris.frame.copy()
iris_feature_names = iris.feature_names
iris_class_names = list(iris.target_names)
iris_df["品种"] = iris_df["target"].map(dict(enumerate(iris_class_names)))

X_iris = iris_df[iris_feature_names]
scaler = StandardScaler()
X_iris_scaled = scaler.fit_transform(X_iris)
pca = PCA(n_components=2, random_state=0)
iris_pca = pca.fit_transform(X_iris_scaled)

display(iris_df.head(8))
display(iris_df["品种"].value_counts().rename_axis("品种").reset_index(name="样本数"))
print("PCA 两个主成分解释方差:", np.round(pca.explained_variance_ratio_, 3))
"""


KMEANS_PROCESS_CELL = """
# 比较不同 k：inertia 用于肘部曲线，silhouette 辅助判断聚类分离度。
k_values = range(1, 8)
kmeans_by_k = {}
labels_by_k = {}
metric_rows = []

for k in k_values:
    model = KMeans(n_clusters=k, n_init=20, random_state=4)
    labels = model.fit_predict(X_iris_scaled)
    kmeans_by_k[k] = model
    labels_by_k[k] = labels
    metric_rows.append({
        "k": k,
        "inertia": model.inertia_,
        "silhouette": np.nan if k == 1 else silhouette_score(X_iris_scaled, labels),
        "ARI(对照真实品种)": np.nan if k == 1 else adjusted_rand_score(iris.target, labels),
    })

k_metrics = pd.DataFrame(metric_rows).round(3)
chosen_k = 3
kmeans = kmeans_by_k[chosen_k]
final_labels = labels_by_k[chosen_k]

clustered_iris = iris_df.copy()
clustered_iris["簇"] = final_labels
cluster_profile = clustered_iris.groupby("簇")[iris_feature_names].mean().round(2)
cluster_mix = pd.crosstab(clustered_iris["簇"], clustered_iris["品种"])

display(k_metrics)
display(cluster_profile)
display(cluster_mix)
"""


KMEANS_PLOT_CELL = """
# 在 PCA 平面比较不同 k 的聚类结果。
palette = np.array(["#2563eb", "#f97316", "#16a34a", "#9333ea", "#0f766e", "#be123c", "#64748b"])
fig, axes = plt.subplots(2, 2, figsize=(10.2, 8.0), sharex=True, sharey=True)
for ax, k in zip(axes.ravel(), [2, 3, 4, 5]):
    labels = labels_by_k[k]
    centers_2d = pca.transform(kmeans_by_k[k].cluster_centers_)
    ax.scatter(
        iris_pca[:, 0],
        iris_pca[:, 1],
        c=palette[labels],
        s=58,
        alpha=0.85,
        edgecolors="white",
        linewidth=0.6,
    )
    ax.scatter(
        centers_2d[:, 0],
        centers_2d[:, 1],
        marker="X",
        s=150,
        color="#0f172a",
        edgecolors="white",
        linewidth=0.8,
    )
    ax.set_title(f"k={k}", loc="left", fontweight="bold")
    ax.grid(True, color="#e2e8f0", linewidth=0.8)

fig.suptitle("Iris KMeans 不同 k 的聚类效果", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
fig.supxlabel("PCA 1")
fig.supylabel("PCA 2")
plt.tight_layout()
plt.show()

# 肘部曲线观察 inertia 下降速度，k=3 后收益明显变小。
fig, ax1 = plt.subplots(figsize=(8.6, 5.0))
ax1.plot(k_metrics["k"], k_metrics["inertia"], marker="o", linewidth=2.4, color="#2563eb", label="inertia")
ax1.axvline(chosen_k, color="#f97316", linestyle="--", linewidth=1.8)
ax1.set_title("肘部曲线与 k 选择", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax1.set_xlabel("k")
ax1.set_ylabel("inertia", color="#2563eb")
ax1.tick_params(axis="y", labelcolor="#2563eb")
ax1.grid(True, color="#e2e8f0", linewidth=0.8)

ax2 = ax1.twinx()
ax2.plot(k_metrics["k"], k_metrics["silhouette"], marker="s", linewidth=2.0, color="#16a34a", label="silhouette")
ax2.set_ylabel("silhouette", color="#16a34a")
ax2.tick_params(axis="y", labelcolor="#16a34a")
ax1.text(chosen_k + 0.08, ax1.get_ylim()[1] * 0.82, "选择 k=3", color="#c2410c", fontweight="bold")
plt.tight_layout()
plt.show()
"""


GD_DATA_CELL = """
# 加载 Diabetes 经典回归数据集，使用 BMI 预测一年后的疾病进展指标。
diabetes = load_diabetes(as_frame=True)
gd_df = diabetes.frame[["bmi", "target"]].copy()
gd_df.columns = ["BMI", "疾病进展指标"]

X_gd = gd_df[["BMI"]].to_numpy()
y_gd = gd_df["疾病进展指标"].to_numpy()

display(gd_df.head(10))
display(gd_df.describe().round(3))
"""


GD_PROCESS_CELL = """
# 用 sklearn SGDRegressor 做梯度下降，记录损失下降过程。
gd_scaler = StandardScaler()
X_gd_scaled = gd_scaler.fit_transform(X_gd)
regressor = SGDRegressor(
    loss="squared_error",
    penalty=None,
    learning_rate="invscaling",
    eta0=0.04,
    power_t=0.25,
    random_state=0,
)

gd_rows = []
for epoch in range(1, 61):
    regressor.partial_fit(X_gd_scaled, y_gd)
    pred = regressor.predict(X_gd_scaled)
    gd_rows.append({
        "轮次": epoch,
        "标准化斜率": round(regressor.coef_[0], 4),
        "截距": round(regressor.intercept_[0], 4),
        "MSE": round(mean_squared_error(y_gd, pred), 3),
    })

gd_trace = pd.DataFrame(gd_rows)
display(gd_trace.iloc[[0, 1, 2, 9, 29, 59]])
"""


GD_PLOT_CELL = """
# 绘制拟合直线和 MSE 曲线。
fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.5))

x_line = np.linspace(X_gd.min(), X_gd.max(), 100).reshape(-1, 1)
axes[0].scatter(X_gd[:, 0], y_gd, s=42, color="#2563eb", alpha=0.72, edgecolor="white", linewidth=0.4)
axes[0].plot(x_line[:, 0], regressor.predict(gd_scaler.transform(x_line)), color="#f97316", linewidth=2.4)
axes[0].set_title("Diabetes BMI 回归", loc="left", fontweight="bold")
axes[0].set_xlabel("BMI")
axes[0].set_ylabel("疾病进展指标")
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
# 加载 Iris 中的 setosa 与 versicolor，使用两个花瓣特征做感知机二分类。
iris = load_iris(as_frame=True)
perceptron_df = iris.frame.copy()
perceptron_df["品种"] = perceptron_df["target"].map(dict(enumerate(iris.target_names)))
perceptron_df = perceptron_df[perceptron_df["品种"].isin(["setosa", "versicolor"])].copy()

per_features = ["petal length (cm)", "petal width (cm)"]
X_per = perceptron_df[per_features].to_numpy()
y_per = (perceptron_df["品种"] == "versicolor").astype(int).to_numpy()
perceptron_df["二分类标签"] = y_per

display(perceptron_df)
"""


PERCEPTRON_PROCESS_CELL = """
# 用 sklearn Perceptron 的 partial_fit 逐轮学习，记录边界参数。
per_scaler = StandardScaler()
X_per_scaled = per_scaler.fit_transform(X_per)
perceptron = Perceptron(eta0=0.08, random_state=1, warm_start=True)
classes = np.array([0, 1])
per_rows = []

for epoch in range(1, 13):
    perceptron.partial_fit(X_per_scaled, y_per, classes=classes)
    pred = perceptron.predict(X_per_scaled)
    per_rows.append({
        "轮次": epoch,
        "w_petal_length": round(perceptron.coef_[0, 0], 4),
        "w_petal_width": round(perceptron.coef_[0, 1], 4),
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
scaled_x = (x_line - per_scaler.mean_[0]) / per_scaler.scale_[0]
scaled_y = -(w0 * scaled_x + bias) / w1
y_line = scaled_y * per_scaler.scale_[1] + per_scaler.mean_[1]
ax.plot(x_line, y_line, color="#0f172a", linewidth=2.2)

ax.set_title("Iris Perceptron 决策边界", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xlabel("petal length (cm)")
ax.set_ylabel("petal width (cm)")
ax.set_xlim(x_min, x_max)
ax.set_ylim(X_per[:, 1].min() - 0.08, X_per[:, 1].max() + 0.12)
ax.grid(True, color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
"""


METRICS_CELL = """
# 用 Iris 感知机的 decision_function 分数观察阈值变化。
y_true = y_per
y_score = perceptron.decision_function(X_per_scaled)
thresholds = np.quantile(y_score, [0.35, 0.50, 0.65])

metric_rows = []
for threshold in thresholds:
    y_hat = (y_score >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_hat, average="binary", zero_division=0
    )
    metric_rows.append({
        "阈值": round(float(threshold), 3),
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
            ["训练 Wine 决策树", "查看特征重要性", "比较 Iris 不同 k 与肘部曲线"],
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
            ["用 Diabetes 运行 SGD 回归", "用 Iris 运行 Perceptron", "比较不同分类阈值"],
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
