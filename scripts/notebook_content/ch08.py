"""第 8-12 章 · 代码实验。"""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import flatten


DEPENDENCIES_CELL = """
# 载入本页会用到的数据集、模型和绘图工具。
import importlib.util
import logging
import math
import subprocess
import sys
import warnings
from collections import Counter, defaultdict
from pathlib import Path

required_packages = {
    "numpy": "numpy>=1.24",
    "pandas": "pandas>=2.0",
    "matplotlib": "matplotlib>=3.7",
    "scipy": "scipy>=1.10",
    "sklearn": "scikit-learn>=1.3",
}
missing = [package for module, package in required_packages.items() if importlib.util.find_spec(module) is None]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from PIL import Image
from IPython.display import display
from scipy.signal import correlate2d
from sklearn.datasets import load_breast_cancer, load_iris, load_sample_image, make_moons
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import accuracy_score, confusion_matrix, log_loss, mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.svm import SVC

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


MLP_DATA_CELL = """
# 加载 Wisconsin 乳腺癌数据：这是二分类模型的经典公开案例。
cancer = load_breast_cancer(as_frame=True)
cancer_label_names = np.array(["恶性", "良性"])
X_mlp = cancer.data
y_mlp = cancer.target

X_train_mlp, X_test_mlp, y_train_mlp, y_test_mlp = train_test_split(
    X_mlp,
    y_mlp,
    test_size=0.25,
    stratify=y_mlp,
    random_state=8,
)

feature_preview = X_mlp[[
    "mean radius",
    "mean texture",
    "mean perimeter",
    "mean area",
    "mean smoothness",
]].head(8)

cancer_summary = pd.DataFrame(
    {
        "样本数": [len(X_mlp)],
        "输入维度": [X_mlp.shape[1]],
        "类别数": [len(np.unique(y_mlp))],
        "训练样本": [len(X_train_mlp)],
        "测试样本": [len(X_test_mlp)],
        "类别名称": [", ".join(cancer.target_names)],
    }
)
display(cancer_summary)
display(feature_preview.round(3))
"""


MLP_TRAIN_CELL = """
# 训练小型 MLP，并读取每轮损失。
mlp = make_pipeline(
    StandardScaler(),
    MLPClassifier(
        hidden_layer_sizes=(32,),
        activation="relu",
        solver="adam",
        learning_rate_init=0.01,
        max_iter=80,
        random_state=8,
    ),
)

mlp.fit(X_train_mlp, y_train_mlp)
classifier = mlp.named_steps["mlpclassifier"]
mlp_trace = pd.DataFrame(
    {
        "轮次": np.arange(1, len(classifier.loss_curve_) + 1),
        "损失": classifier.loss_curve_,
    }
).round(4)

display(mlp_trace.iloc[[0, 1, 2, 9, 19, len(mlp_trace) - 1]])
"""


MLP_RESULT_CELL = """
# 查看测试集预测、准确率和混淆矩阵。
test_pred_mlp = mlp.predict(X_test_mlp)
test_prob_mlp = mlp.predict_proba(X_test_mlp)

score_df = pd.DataFrame(
    [{"数据": "乳腺癌测试集", "准确率": accuracy_score(y_test_mlp, test_pred_mlp)}]
).round(3)
confusion_df = pd.DataFrame(
    confusion_matrix(y_test_mlp, test_pred_mlp),
    index=[f"真实_{name}" for name in cancer_label_names],
    columns=[f"预测_{name}" for name in cancer_label_names],
)
sample_result = pd.DataFrame(
    {
        "样本编号": X_test_mlp.index[:12],
        "真实": y_test_mlp.to_numpy()[:12],
        "预测": test_pred_mlp[:12],
        "预测置信度": np.max(test_prob_mlp[:12], axis=1),
    }
).round(3)

display(score_df)
display(sample_result)
display(confusion_df)
"""


MLP_PLOT_CELL = """
# 绘制损失曲线、混淆矩阵和预测置信度。
fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.4), gridspec_kw={"width_ratios": [1.05, 1.0, 1.15]})

axes[0].plot(mlp_trace["轮次"], mlp_trace["损失"], color="#2563eb", linewidth=2.4)
axes[0].set_title("MLP 训练损失", loc="left", fontweight="bold")
axes[0].set_xlabel("轮次")
axes[0].set_ylabel("损失")
axes[0].grid(True, color="#e2e8f0", linewidth=0.8)

im = axes[1].imshow(confusion_df.to_numpy(), cmap="YlGnBu")
axes[1].set_title("测试集混淆矩阵", loc="left", fontweight="bold")
axes[1].set_xticks([0, 1], cancer_label_names, rotation=20, ha="right")
axes[1].set_yticks([0, 1], cancer_label_names)
for i in range(2):
    for j in range(2):
        axes[1].text(j, i, int(confusion_df.iloc[i, j]), ha="center", va="center", color="#0f172a", fontweight="bold")

preview_df = sample_result.copy()
preview_df["标签"] = [cancer_label_names[int(v)] for v in preview_df["真实"]]
preview_df["预测标签"] = [cancer_label_names[int(v)] for v in preview_df["预测"]]
bar_colors = np.where(preview_df["真实"].to_numpy() == preview_df["预测"].to_numpy(), "#16a34a", "#dc2626")
axes[2].barh(np.arange(len(preview_df)), preview_df["预测置信度"], color=bar_colors)
axes[2].set_yticks(np.arange(len(preview_df)), [f"{a}->{b}" for a, b in zip(preview_df["标签"], preview_df["预测标签"])])
axes[2].invert_yaxis()
axes[2].set_xlim(0, 1)
axes[2].set_title("样本预测置信度", loc="left", fontweight="bold")
axes[2].grid(True, axis="x", color="#e2e8f0", linewidth=0.8)

plt.tight_layout()
plt.show()
"""


TRANSE_CELL = """
# TransE：用国家-首都关系比较正确三元组和替换实体后的距离。
entity_vec = {
    "France": np.array([0.10, 0.82]),
    "Paris": np.array([0.72, 0.60]),
    "Germany": np.array([0.05, 0.22]),
    "Berlin": np.array([0.68, 0.01]),
    "Italy": np.array([0.18, 0.48]),
    "Rome": np.array([0.80, 0.28]),
}
relation_vec = {"capital_of": np.array([0.62, -0.22])}

triples = [
    ("France", "capital_of", "Paris", "正例"),
    ("Germany", "capital_of", "Berlin", "正例"),
    ("Italy", "capital_of", "Rome", "正例"),
    ("France", "capital_of", "Berlin", "替换尾实体"),
    ("Germany", "capital_of", "Paris", "替换尾实体"),
]

rows = []
for head, relation, tail, kind in triples:
    score_vec = entity_vec[head] + relation_vec[relation] - entity_vec[tail]
    rows.append({
        "样本": kind,
        "三元组": f"({head}, {relation}, {tail})",
        "距离": round(float(np.linalg.norm(score_vec)), 3),
    })

transe_df = pd.DataFrame(rows).sort_values("距离")
display(transe_df)
"""


TRANSE_PLOT_CELL = """
# 绘制 h + r 与候选 t 的几何距离。
fig, ax = plt.subplots(figsize=(7.2, 5.0))
h = entity_vec["France"]
r = relation_vec["capital_of"]
target_point = h + r

for name, vec in entity_vec.items():
    ax.scatter(vec[0], vec[1], s=170, color="#ffffff", edgecolor="#2563eb", linewidth=1.7)
    ax.text(vec[0] + 0.02, vec[1] + 0.02, name, color="#0f172a")

ax.arrow(h[0], h[1], r[0], r[1], width=0.006, head_width=0.035, color="#f97316", length_includes_head=True)
ax.scatter(target_point[0], target_point[1], s=210, marker="X", color="#f97316", edgecolor="#0f172a", linewidth=1.0)
ax.text(target_point[0] + 0.02, target_point[1] - 0.05, "France + capital_of", color="#c2410c")
ax.set_title("TransE 距离示意", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xlabel("维度1")
ax.set_ylabel("维度2")
ax.grid(True, color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
"""


ATTENTION_CELL = """
# 用一组可解释的查询/键特征，让同一句话的注意力更容易读。
labels = ["这", "只", "猫", "坐", "在", "垫子"]
features = ["subject_noun", "verb", "prep", "place_noun", "det"]

K = pd.DataFrame([
    [0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1],
    [0, 0, 0, 1, 0],
], index=labels, columns=features)

Q = pd.DataFrame([
    [8.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 8.0, 0.0, 0.0, 0.0],
    [6.5, 0.0, 0.0, 6.5, 0.0],
    [0.0, 0.0, 0.0, 8.0, 0.0],
    [0.0, 0.0, 0.0, 8.0, 0.0],
    [0.0, 0.0, 8.0, 0.0, 0.0],
], index=labels, columns=features)

V = np.array([
    [0.20, 0.10],
    [0.85, 0.20],
    [0.45, 0.80],
    [0.20, 0.65],
    [0.20, 0.10],
    [0.70, 0.55],
])

scores = Q.to_numpy() @ K.to_numpy().T / math.sqrt(len(features))
weights = np.exp(scores - scores.max(axis=1, keepdims=True))
weights = weights / weights.sum(axis=1, keepdims=True)
attn_output = weights @ V

weight_df = pd.DataFrame(np.round(weights, 3), index=labels, columns=labels)
focus_rows = []
for i, label in enumerate(labels):
    kept = [j for j in range(len(labels)) if weights[i, j] >= 0.20]
    focus_rows.append({
        "当前词": label,
        "主要关注": ", ".join(labels[j] for j in kept),
        "权重": ", ".join(f"{weights[i, j]:.2f}" for j in kept),
    })

display(pd.DataFrame(focus_rows))
display(weight_df)
display(pd.DataFrame(np.round(attn_output, 3), index=labels, columns=["输出1", "输出2"]))
"""


ATTENTION_PLOT_CELL = """
# 画出权重热力图，并把每一行的最高权重直接标出来。
fig, (ax, link_ax) = plt.subplots(
    1,
    2,
    figsize=(10.8, 5.2),
    gridspec_kw={"width_ratios": [1.25, 0.9]},
)
im = ax.imshow(weights, cmap="YlOrRd", vmin=0, vmax=1)
ax.set_xticks(range(len(labels)), labels, rotation=30, ha="right")
ax.set_yticks(range(len(labels)), labels)
ax.set_xlabel("被关注的词（键）")
ax.set_ylabel("正在读的词（查询）")

for i in range(len(labels)):
    max_weight = weights[i].max()
    for j in range(len(labels)):
        value = weights[i, j]
        color = "#ffffff" if value > 0.45 else "#0f172a"
        weight = "bold" if value == max_weight else "normal"
        ax.text(j, i, f"{value:.2f}", ha="center", va="center", color=color, fontweight=weight)
        if value == max_weight:
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="#0f172a", linewidth=2.4))

ax.set_title("注意力权重热力图", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

link_ax.set_xlim(0, 1)
link_ax.set_ylim(-0.7, len(labels) - 0.25)
link_ax.axis("off")
link_ax.text(0.02, len(labels) - 0.15, "每行最高关注", fontsize=13, fontweight="bold", color="#0f172a")
link_ax.text(0.08, len(labels) - 0.65, "当前词", color="#64748b", fontweight="bold")
link_ax.text(0.68, len(labels) - 0.65, "被关注词", color="#64748b", fontweight="bold")

for i in range(len(labels)):
    y = len(labels) - 1 - i
    max_weight = weights[i].max()
    top_indices = [j for j in range(len(labels)) if np.isclose(weights[i, j], max_weight)]
    target_text = " / ".join(labels[j] for j in top_indices)
    value_text = " / ".join(f"{weights[i, j]:.2f}" for j in top_indices)
    link_ax.text(0.08, y, labels[i], ha="left", va="center", color="#0f172a")
    link_ax.text(0.68, y, target_text, ha="left", va="center", color="#0f172a", fontweight="bold")
    link_ax.annotate(
        "",
        xy=(0.65, y),
        xytext=(0.35, y),
        arrowprops={"arrowstyle": "->", "lw": 1.2 + 4.0 * max_weight, "color": "#ea580c", "alpha": 0.95},
    )
    link_ax.text(0.50, y + 0.16, value_text, ha="center", va="center", color="#c2410c", fontsize=9)

plt.tight_layout()
plt.show()
"""


BPE_DATA_CELL = """
# 准备带频次的 BPE 语料，把每个词拆成字符序列。
word_freq = {
    "low": 5,
    "lower": 2,
    "newest": 6,
    "widest": 3,
    "newer": 4,
}
vocab = Counter({tuple(word) + ("</w>",): freq for word, freq in word_freq.items()})

def pair_counts(vocab):
    counts = Counter()
    for symbols, freq in vocab.items():
        for i in range(len(symbols) - 1):
            counts[(symbols[i], symbols[i + 1])] += freq
    return counts


def merge_pair(vocab, pair):
    merged = {}
    bigram = " ".join(pair)
    replacement = "".join(pair)
    for symbols, freq in vocab.items():
        text = " ".join(symbols)
        new_symbols = tuple(text.replace(bigram, replacement).split())
        merged[new_symbols] = freq
    return Counter(merged)


def weighted_token_count(vocab):
    return sum(len(symbols) * freq for symbols, freq in vocab.items())


display(pd.DataFrame({
    "单词": list(word_freq.keys()),
    "频次": list(word_freq.values()),
    "初始词元序列": [" ".join(tuple(word) + ("</w>",)) for word in word_freq],
}))
print("初始加权词元数:", weighted_token_count(vocab))
"""


BPE_RUN_CELL = """
# 连续执行若干次合并，记录每轮最高频符号对和词元数变化。
bpe_rows = []
history = []
current_vocab = vocab.copy()
token_totals = [weighted_token_count(current_vocab)]

for step in range(1, 7):
    counts = pair_counts(current_vocab)
    best_pair, best_count = counts.most_common(1)[0]
    before_total = weighted_token_count(current_vocab)
    current_vocab = merge_pair(current_vocab, best_pair)
    after_total = weighted_token_count(current_vocab)
    token_totals.append(after_total)
    state = [" ".join(symbols) for symbols in current_vocab.keys()]
    bpe_rows.append({
        "轮次": step,
        "合并符号对": " + ".join(best_pair),
        "频次": best_count,
        "词元数": f"{before_total} → {after_total}",
        "减少": before_total - after_total,
        "当前词元序列": " | ".join(state),
    })
    history.append((best_pair, best_count, counts, before_total, after_total))

bpe_trace = pd.DataFrame(bpe_rows)
display(bpe_trace)
"""


BPE_PLOT_CELL = """
# 展示第一轮选择依据和连续合并后的压缩过程。
first_pair, _, first_counts, _, _ = history[0]
top_pairs = first_counts.most_common(10)
pair_labels = ["+".join(pair) for pair, _ in top_pairs]
pair_values = [count for _, count in top_pairs]
pair_colors = ["#f97316" if pair == first_pair else "#2563eb" for pair, _ in top_pairs]

fig = plt.figure(figsize=(11.0, 7.0))
gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.15], width_ratios=[1.2, 1.0], hspace=0.42, wspace=0.32)

ax1 = fig.add_subplot(gs[0, 0])
y = np.arange(len(pair_labels))
ax1.barh(y, pair_values, color=pair_colors)
ax1.set_yticks(y, pair_labels)
ax1.invert_yaxis()
ax1.set_xlabel("加权频次")
ax1.set_title("第一轮符号对频次", loc="left", fontsize=13, fontweight="bold", color="#0f172a")
for idx, value in enumerate(pair_values):
    ax1.text(value + 0.25, idx, str(value), va="center", color="#0f172a", fontweight="bold" if idx == 0 else "normal")
ax1.grid(True, axis="x", color="#e2e8f0", linewidth=0.8)

ax2 = fig.add_subplot(gs[0, 1])
steps = np.arange(len(token_totals))
ax2.plot(steps, token_totals, marker="o", linewidth=2.4, color="#2563eb")
for x, value in zip(steps, token_totals):
    ax2.text(x, value + 2.0, str(value), ha="center", color="#0f172a")
ax2.set_xticks(steps, ["初始"] + [str(i) for i in range(1, len(token_totals))])
ax2.set_xlabel("合并轮次")
ax2.set_ylabel("加权词元数")
ax2.set_title("词元数逐轮下降", loc="left", fontsize=13, fontweight="bold", color="#0f172a")
ax2.grid(True, color="#e2e8f0", linewidth=0.8)

ax3 = fig.add_subplot(gs[1, :])
ax3.set_xlim(0, 1)
ax3.set_ylim(0, len(bpe_trace) + 0.8)
ax3.axis("off")
ax3.text(0.02, len(bpe_trace) + 0.35, "合并过程", fontsize=13, fontweight="bold", color="#0f172a")
ax3.text(0.05, len(bpe_trace) - 0.05, "轮次", color="#64748b", fontweight="bold")
ax3.text(0.18, len(bpe_trace) - 0.05, "选中符号对", color="#64748b", fontweight="bold")
ax3.text(0.43, len(bpe_trace) - 0.05, "频次", color="#64748b", fontweight="bold")
ax3.text(0.56, len(bpe_trace) - 0.05, "词元数", color="#64748b", fontweight="bold")
ax3.text(0.76, len(bpe_trace) - 0.05, "减少", color="#64748b", fontweight="bold")

for idx, row in bpe_trace.iterrows():
    y = len(bpe_trace) - idx - 0.65
    ax3.add_patch(plt.Rectangle((0.02, y - 0.22), 0.92, 0.38, color="#eff6ff" if idx % 2 == 0 else "#ffffff", ec="#dbeafe", lw=0.8))
    ax3.text(0.07, y, str(row["轮次"]), ha="center", va="center", color="#0f172a", fontweight="bold")
    ax3.text(0.18, y, row["合并符号对"], ha="left", va="center", color="#c2410c", fontweight="bold")
    ax3.text(0.45, y, str(row["频次"]), ha="center", va="center", color="#0f172a")
    ax3.text(0.57, y, row["词元数"], ha="left", va="center", color="#0f172a")
    ax3.text(0.78, y, f"-{row['减少']}", ha="center", va="center", color="#16a34a", fontweight="bold")

fig.suptitle("BPE：高频相邻符号被合并，序列随轮次变短", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


SKIPGRAM_DATA_CELL = """
# Word2Vec 经典类比：king - man + woman 应接近 queen。
analogy_words = ["king", "queen", "man", "woman", "prince", "princess", "apple", "orange"]
word_vectors = pd.DataFrame(
    {
        "royalty": [0.92, 0.90, 0.10, 0.10, 0.82, 0.80, 0.05, 0.04],
        "gender": [0.88, -0.88, 0.85, -0.85, 0.72, -0.72, 0.02, -0.02],
        "fruit": [0.02, 0.02, 0.00, 0.00, 0.02, 0.02, 0.92, 0.90],
    },
    index=analogy_words,
)
display(word_vectors)
"""


SKIPGRAM_EMBED_CELL = """
# 计算最近邻和类比向量。
emb = normalize(word_vectors.to_numpy())
vocab_words = word_vectors.index.to_list()
word_to_id = {word: i for i, word in enumerate(vocab_words)}
sim = cosine_similarity(emb)

analogy_vec = (
    word_vectors.loc["king"].to_numpy()
    - word_vectors.loc["man"].to_numpy()
    + word_vectors.loc["woman"].to_numpy()
)
analogy_vec = normalize(analogy_vec.reshape(1, -1))
analogy_scores = cosine_similarity(analogy_vec, emb)[0]

nearest = pd.DataFrame(
    [
        {"词": word, "最近邻": vocab_words[np.argsort(sim[i])[-2]], "相似度": round(np.sort(sim[i])[-2], 3)}
        for word, i in word_to_id.items()
    ]
)
analogy_df = pd.DataFrame(
    {"候选词": vocab_words, "king - man + woman 相似度": np.round(analogy_scores, 3)}
).sort_values("king - man + woman 相似度", ascending=False)

display(nearest)
display(analogy_df)
"""


SKIPGRAM_PLOT_CELL = """
# 绘制词向量位置。
fig, ax = plt.subplots(figsize=(7.4, 5.2))
emb_2d = word_vectors[["royalty", "gender"]].to_numpy()
ax.scatter(emb_2d[:, 0], emb_2d[:, 1], s=130, color="#eff6ff", edgecolor="#2563eb", linewidth=1.6)
for word, i in word_to_id.items():
    ax.text(emb_2d[i, 0] + 0.02, emb_2d[i, 1] + 0.02, word, color="#0f172a")
ax.annotate("", xy=emb_2d[word_to_id["queen"]], xytext=emb_2d[word_to_id["king"]], arrowprops={"arrowstyle": "->", "color": "#f97316", "lw": 2})
ax.annotate("", xy=emb_2d[word_to_id["woman"]], xytext=emb_2d[word_to_id["man"]], arrowprops={"arrowstyle": "->", "color": "#f97316", "lw": 2})
ax.axhline(0, color="#e2e8f0", linewidth=1)
ax.axvline(0, color="#e2e8f0", linewidth=1)
ax.set_title("Word2Vec 类比空间", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xlabel("王室方向")
ax.set_ylabel("性别方向")
plt.tight_layout()
plt.show()
"""


SELF_ATTENTION_CELL = """
# 加入因果遮罩后，每个位置只能看见自己和左侧词元。
lm_tokens = "to be or not to be".split()
X_lm = np.array([
    [0.7, 0.1, 0.1],
    [0.2, 0.8, 0.2],
    [0.4, 0.3, 0.6],
    [0.3, 0.7, 0.3],
    [0.7, 0.1, 0.1],
    [0.2, 0.8, 0.2],
])
scores_lm = X_lm @ X_lm.T / math.sqrt(X_lm.shape[1])
mask = np.triu(np.ones_like(scores_lm), k=1).astype(bool)
scores_lm = np.where(mask, -1e9, scores_lm)
weights_lm = np.exp(scores_lm - scores_lm.max(axis=1, keepdims=True))
weights_lm = weights_lm / weights_lm.sum(axis=1, keepdims=True)

display(pd.DataFrame(np.round(weights_lm, 3), index=lm_tokens, columns=lm_tokens))
"""


CHAR_LM_CELL = """
# 词二元统计：根据当前词统计下一个词分布。
text = "to be or not to be that is the question to be".split()
bigram = defaultdict(Counter)
for a, b in zip(text, text[1:]):
    bigram[a][b] += 1

lm_rows = []
for token, counts in bigram.items():
    total = sum(counts.values())
    best_next, best_count = counts.most_common(1)[0]
    lm_rows.append({
        "当前词": token,
        "最可能下一个词": best_next,
        "概率": round(best_count / total, 3),
        "候选分布": dict(counts),
    })

display(pd.DataFrame(lm_rows))
"""


SELF_ATTENTION_PLOT_CELL = """
# 绘制因果注意力热力图。
fig, ax = plt.subplots(figsize=(5.8, 4.8))
im = ax.imshow(weights_lm, cmap="Blues", vmin=0, vmax=weights_lm.max())
ax.set_xticks(range(len(lm_tokens)), lm_tokens)
ax.set_yticks(range(len(lm_tokens)), lm_tokens)
for i in range(len(lm_tokens)):
    for j in range(len(lm_tokens)):
        ax.text(j, i, f"{weights_lm[i, j]:.2f}", ha="center", va="center", color="#0f172a")
ax.set_title("因果自注意力", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
plt.tight_layout()
plt.show()
"""


CONV_DATA_CELL = """
# 使用真实花朵照片，配合 Sobel 核做边缘检测。
raw_conv_photo = load_sample_image("flower.jpg")
conv_photo = np.asarray(Image.fromarray(raw_conv_photo).resize((96, 96))) / 255.0
image = np.dot(conv_photo[..., :3], [0.299, 0.587, 0.114])
kernel = np.array([
    [-1, 0, 1],
    [-1, 0, 1],
    [-1, 0, 1],
], dtype=float)

feature = correlate2d(image, kernel, mode="valid")
display(pd.DataFrame({
    "图像": ["flower.jpg"],
    "尺寸": [f"{image.shape[0]}x{image.shape[1]}"],
    "灰度最小值": [float(image.min())],
    "灰度最大值": [float(image.max())],
}).round(3))
display(pd.DataFrame(kernel.astype(int)))
"""


CONV_PROCESS_CELL = """
# 展开中心区域的几个窗口，观察卷积值如何来自局部像素。
rows = []
for i in range(40, 46):
    for j in range(40, 46):
        window = image[i:i + 3, j:j + 3]
        rows.append({
            "位置": f"({i},{j})",
            "窗口均值": window.mean(),
            "左列均值": window[:, 0].mean(),
            "右列均值": window[:, 2].mean(),
            "卷积值": round(float((window * kernel).sum()), 3),
        })

conv_df = pd.DataFrame(rows)
display(conv_df.head(10).round(3))
display(pd.DataFrame({
    "特征图尺寸": [f"{feature.shape[0]}x{feature.shape[1]}"],
    "最小响应": [float(feature.min())],
    "最大响应": [float(feature.max())],
    "平均绝对响应": [float(np.abs(feature).mean())],
}).round(3))
"""


CONV_PLOT_CELL = """
# 绘制输入、边缘响应和 2x2 max pooling。
positive_feature = np.maximum(feature, 0)
pool = np.array([
    [positive_feature[i:i + 2, j:j + 2].max() for j in range(0, positive_feature.shape[1] - 1, 2)]
    for i in range(0, positive_feature.shape[0] - 1, 2)
])

fig, axes = plt.subplots(2, 2, figsize=(8.4, 7.0))
for ax, data, title, cmap in zip(
    axes.ravel(),
    [conv_photo, image, feature, pool],
    ["真实照片", "灰度输入", "Sobel 边缘响应", "MaxPool 后特征"],
    [None, "gray", "RdBu_r", "YlGnBu"],
):
    im = ax.imshow(data, cmap=cmap)
    ax.set_title(title, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
fig.suptitle("真实照片 Sobel 卷积：局部边缘被提取为特征图", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


PATCHIFY_CELL = """
# 使用真实建筑照片，按 ViT 常见设置切成 16x16 图块。
raw_photo = load_sample_image("china.jpg")
vit_image = np.asarray(Image.fromarray(raw_photo).resize((224, 224))) / 255.0
patch_size = 16
patch_grid = vit_image.shape[0] // patch_size
patches = vit_image.reshape(patch_grid, patch_size, patch_grid, patch_size, 3).swapaxes(1, 2)
patch_tokens = patches.reshape(-1, patch_size * patch_size * 3)

patch_summary = []
for patch_id, patch in enumerate(patches.reshape(-1, patch_size, patch_size, 3)):
    row, col = divmod(patch_id, patch_grid)
    patch_summary.append({
        "图块编号": patch_id,
        "行": row,
        "列": col,
        "向量维度": patch_tokens.shape[1],
        "R均值": patch[:, :, 0].mean(),
        "G均值": patch[:, :, 1].mean(),
        "B均值": patch[:, :, 2].mean(),
        "亮度标准差": patch.mean(axis=2).std(),
    })

patch_df = pd.DataFrame(patch_summary)
display(patch_df.head(12).round(3))
"""


PATCHIFY_PLOT_CELL = """
# 绘制真实图片图块网格和若干具体图块。
selected_patches = [18, 43, 87, 112, 145, 181]
fig = plt.figure(figsize=(10.8, 6.6))
gs = fig.add_gridspec(2, 6, height_ratios=[3.4, 1.5], hspace=0.22, wspace=0.08)
ax_img = fig.add_subplot(gs[0, :])
ax_img.imshow(vit_image)
ax_img.set_title("真实图片切成 14x14 个图块", loc="left", fontweight="bold")
ax_img.set_xticks(np.arange(0, 225, patch_size))
ax_img.set_yticks(np.arange(0, 225, patch_size))
ax_img.grid(color="#ffffff", linewidth=0.8)
ax_img.tick_params(labelbottom=False, labelleft=False, length=0)

for slot, patch_id in enumerate(selected_patches):
    row, col = divmod(patch_id, patch_grid)
    ax = fig.add_subplot(gs[1, slot])
    ax.imshow(patches[row, col])
    ax.set_title(f"图块 {patch_id}\\n({row},{col})", fontsize=9, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])

fig.suptitle("ViT 图块切分：真实照片转成图块向量序列", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


MAE_CELL = """
# MAE 遮挡：在同一张真实图片上随机遮住 75% 图块，只保留可见图块。
rng = np.random.default_rng(4)
num_patches = len(patch_tokens)
mask_ratio = 0.75
visible_ids = np.sort(rng.choice(num_patches, size=int(num_patches * (1 - mask_ratio)), replace=False))
masked_ids = np.array([idx for idx in range(num_patches) if idx not in set(visible_ids)])

mae_df = pd.DataFrame({
    "指标": ["总图块数", "可见图块数", "遮挡图块数", "遮挡比例"],
    "值": [num_patches, len(visible_ids), len(masked_ids), mask_ratio],
})
display(mae_df)
"""


MAE_PLOT_CELL = """
# 绘制遮挡图像和一个简单的均值重建基线。
masked_image = vit_image.astype(float).copy()
recon_image = vit_image.astype(float).copy()
mask_map = np.zeros((patch_grid, patch_grid))
visible_patch_mean = patches.reshape(-1, patch_size, patch_size, 3)[visible_ids].mean(axis=0)

for patch_id in masked_ids:
    row, col = divmod(patch_id, patch_grid)
    mask_map[row, col] = 1
    r0, r1 = row * patch_size, (row + 1) * patch_size
    c0, c1 = col * patch_size, (col + 1) * patch_size
    masked_image[r0:r1, c0:c1] = 0.72
    recon_image[r0:r1, c0:c1] = visible_patch_mean

fig, axes = plt.subplots(2, 2, figsize=(8.4, 7.0))
for ax, data, title in zip(
    axes.ravel(),
    [vit_image, mask_map, masked_image, recon_image],
    ["原图", "遮挡图", "可见图块", "均值重建基线"],
):
    cmap = "Greys" if title == "遮挡图" else None
    ax.imshow(data, cmap=cmap, vmin=0, vmax=1)
    ax.set_title(title, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
fig.suptitle("MAE 遮挡：同一张真实图片的图块遮挡", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


CLIP_SETUP_CELL = """
# 安装并导入 CLIP 需要的公开库。
clip_packages = {
    "torch": "torch>=2.2",
    "transformers": "transformers>=4.40",
    "socksio": "socksio>=1.0",
}
missing = [package for module, package in clip_packages.items() if importlib.util.find_spec(module) is None]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

import torch
import torch.nn.functional as F
from transformers import CLIPModel, CLIPProcessor
from transformers.utils import logging as hf_logging

hf_logging.set_verbosity_error()
"""


CLIP_CELL = """
# 真实图片与文本提示：计算每张图片更匹配哪一句描述。
model_id = "openai/clip-vit-base-patch32"
processor = CLIPProcessor.from_pretrained(model_id, use_fast=True)
clip_model = CLIPModel.from_pretrained(model_id)
clip_model.eval()

clip_images = [
    Image.fromarray(load_sample_image("china.jpg")),
    Image.fromarray(load_sample_image("flower.jpg")),
]
image_names = ["china.jpg", "flower.jpg"]
image_labels = ["湖边寺庙图", "红色花朵图"]
text_prompts = [
    "a photo of a Chinese temple by a lake",
    "a close-up photo of a red flower",
    "a photo of a taxi cab",
    "a photo of a city street at night",
]
prompt_labels = ["湖边寺庙", "红色花朵", "出租车", "夜晚街道"]

inputs = processor(text=text_prompts, images=clip_images, return_tensors="pt", padding=True)
with torch.no_grad():
    outputs = clip_model(**inputs)

logits = outputs.logits_per_image
probs = logits.softmax(dim=1)
targets = torch.tensor([0, 1])
clip_loss = F.cross_entropy(logits[:, :2], targets).item()

clip_prob_df = pd.DataFrame(probs.numpy(), index=image_labels, columns=prompt_labels)
display(clip_prob_df.round(3))
print("图文对比损失:", round(float(clip_loss), 4))
"""


CLIP_PLOT_CELL = """
# 绘制真实图片和图文匹配概率矩阵。
sim_matrix = probs.numpy()
fig = plt.figure(figsize=(11.0, 5.4))
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 2.2], wspace=0.35)

for idx, image in enumerate(clip_images):
    ax_img = fig.add_subplot(gs[0, idx])
    ax_img.imshow(image)
    ax_img.set_title(image_labels[idx], fontweight="bold")
    ax_img.set_xticks([])
    ax_img.set_yticks([])

ax = fig.add_subplot(gs[0, 2])
im = ax.imshow(sim_matrix, cmap="YlGnBu", vmin=0, vmax=1)
ax.set_xticks(range(len(text_prompts)), prompt_labels, rotation=30, ha="right")
ax.set_yticks(range(len(image_names)), image_labels)
for i in range(len(image_names)):
    best = int(np.argmax(sim_matrix[i]))
    for j in range(len(text_prompts)):
        value = sim_matrix[i, j]
        ax.text(j, i, f"{value:.2f}", ha="center", va="center", color="#0f172a", fontweight="bold" if j == best else "normal")
        if j == best:
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="#0f172a", linewidth=2.2))
ax.set_title("图文匹配概率", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
plt.tight_layout()
plt.show()
"""


GYM_SETUP_CELL = """
# 载入强化学习经典环境。
if importlib.util.find_spec("gymnasium") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gymnasium>=0.29"])

import gymnasium as gym
"""


MDP_CELL = """
# 冰湖导航：读取环境自带的 MDP 转移表 P。
frozen_env = gym.make("FrozenLake-v1", map_name="4x4", is_slippery=True)
n_states = frozen_env.observation_space.n
n_actions = frozen_env.action_space.n
action_names = {0: "左", 1: "下", 2: "右", 3: "上"}
action_arrows = {0: "←", 1: "↓", 2: "→", 3: "↑"}
lake_map = np.array([
    [cell.decode("utf-8") if isinstance(cell, bytes) else str(cell) for cell in row]
    for row in frozen_env.unwrapped.desc
])

transition_rows = []
for state in range(n_states):
    row, col = divmod(state, 4)
    tile = lake_map[row, col]
    for action, outcomes in frozen_env.unwrapped.P[state].items():
        for prob, next_state, reward, terminated in outcomes:
            transition_rows.append({
                "状态": state,
                "格子": tile,
                "动作": action_names[action],
                "概率": prob,
                "下一状态": next_state,
                "奖励": reward,
                "是否结束": terminated,
            })

display(pd.DataFrame(transition_rows).head(16))
display(pd.DataFrame(lake_map))
"""


MDP_START_CELL = """
# 从起点看一次决策：动作不是直接到达目标，而是先改变下一步状态分布。
start_state = 0
start_row, start_col = divmod(start_state, 4)
start_options = []
for action, outcomes in frozen_env.unwrapped.P[start_state].items():
    for prob, next_state, reward, terminated in outcomes:
        next_row, next_col = divmod(next_state, 4)
        start_options.append({
            "当前格": f"S({start_row},{start_col})",
            "选择动作": action_names[action],
            "可能到达": f"{lake_map[next_row, next_col]}({next_row},{next_col})",
            "概率": prob,
            "奖励": reward,
            "是否结束": terminated,
        })

fig, ax = plt.subplots(figsize=(4.8, 4.4))
tile_color = {"S": "#dbeafe", "F": "#ecfeff", "H": "#fee2e2", "G": "#dcfce7"}
for r in range(4):
    for c in range(4):
        tile = lake_map[r, c]
        ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, color=tile_color[tile], ec="#94a3b8"))
        ax.text(c, r, tile, ha="center", va="center", fontsize=15, fontweight="bold", color="#0f172a")
ax.scatter([start_col], [start_row], s=220, facecolors="none", edgecolors="#2563eb", linewidths=2.4)
ax.set_title("冰湖初始状态", loc="left", fontweight="bold")
ax.set_xlim(-0.5, 3.5)
ax.set_ylim(3.5, -0.5)
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.grid(True, color="#cbd5e1", linewidth=0.8)
plt.tight_layout()
plt.show()

display(pd.DataFrame(start_options).round(3))
"""


VALUE_ONE_STEP_CELL = """
# 看一次 Bellman 更新：靠近终点的状态，会把“可能到达 G 的奖励”传给动作价值。
focus_state = 14
focus_row, focus_col = divmod(focus_state, 4)
old_V = np.zeros(n_states)
one_step_rows = []
for action, outcomes in frozen_env.unwrapped.P[focus_state].items():
    q_value = 0.0
    destinations = []
    for prob, next_state, reward, terminated in outcomes:
        next_row, next_col = divmod(next_state, 4)
        contribution = prob * (reward + 0.99 * old_V[next_state] * (not terminated))
        q_value += contribution
        destinations.append(f"{prob:.2f}→{lake_map[next_row, next_col]}({next_row},{next_col})")
    one_step_rows.append({
        "状态": f"{lake_map[focus_row, focus_col]}({focus_row},{focus_col})",
        "动作": action_names[action],
        "可能转移": " / ".join(destinations),
        "本轮 Q(s,a)": q_value,
    })

display(pd.DataFrame(one_step_rows).round(4))
"""


VALUE_ITERATION_CELL = """
# 价值迭代：直接对 FrozenLake 的 P 表应用 Bellman 最优方程。
def frozenlake_value_iteration(env, gamma=0.99, theta=1e-9, max_iters=1000):
    V = np.zeros(env.observation_space.n)
    deltas = []

    for iteration in range(1, max_iters + 1):
        old_V = V.copy()
        for state in range(env.observation_space.n):
            action_values = []
            for action in range(env.action_space.n):
                q = 0.0
                for prob, next_state, reward, terminated in env.unwrapped.P[state][action]:
                    q += prob * (reward + gamma * old_V[next_state] * (not terminated))
                action_values.append(q)
            V[state] = max(action_values)
        delta = float(np.max(np.abs(V - old_V)))
        deltas.append({"iteration": iteration, "delta": delta})
        if delta < theta:
            break

    Q = np.zeros((env.observation_space.n, env.action_space.n))
    for state in range(env.observation_space.n):
        for action in range(env.action_space.n):
            Q[state, action] = sum(
                prob * (reward + gamma * V[next_state] * (not terminated))
                for prob, next_state, reward, terminated in env.unwrapped.P[state][action]
            )
    policy = Q.argmax(axis=1)
    return V, Q, policy, pd.DataFrame(deltas)


V_frozen, Q_frozen, policy_frozen, delta_trace = frozenlake_value_iteration(frozen_env)
policy_df = pd.DataFrame({
    "状态": np.arange(n_states),
    "格子": lake_map.reshape(-1),
    "推荐动作": [action_names[a] for a in policy_frozen],
    "V": V_frozen,
    "Q_左": Q_frozen[:, 0],
    "Q_下": Q_frozen[:, 1],
    "Q_右": Q_frozen[:, 2],
    "Q_上": Q_frozen[:, 3],
}).round(4)

display(delta_trace.head(8).rename(columns={"iteration": "迭代轮次", "delta": "最大价值变化"}))
display(delta_trace.tail(5).rename(columns={"iteration": "迭代轮次", "delta": "最大价值变化"}))
display(policy_df)
"""


VALUE_PLOT_CELL = """
# 绘制 FrozenLake 的价值、洞、终点和最优动作。
value_grid = V_frozen.reshape(4, 4)
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8))
im = axes[0].imshow(value_grid, cmap="YlGnBu", vmin=0, vmax=value_grid.max())
for state in range(n_states):
    r, c = divmod(state, 4)
    tile = lake_map[r, c]
    arrow = "" if tile in {"H", "G"} else action_arrows[int(policy_frozen[state])]
    axes[0].text(c, r, f"{tile}\\n{value_grid[r, c]:.2f}\\n{arrow}", ha="center", va="center", color="#0f172a", fontweight="bold")
axes[0].set_title("冰湖最优价值与策略", loc="left", fontweight="bold")
axes[0].set_xticks(range(4))
axes[0].set_yticks(range(4))
fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)

axes[1].plot(delta_trace["iteration"], delta_trace["delta"], color="#2563eb", linewidth=2.2)
axes[1].set_yscale("log")
axes[1].set_title("Bellman 误差收敛", loc="left", fontweight="bold")
axes[1].set_xlabel("迭代轮次")
axes[1].set_ylabel("最大价值变化")
axes[1].grid(True, color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
"""


TD_CELL = """
# 出租车调度：先看一个初始状态和六个可选动作。
taxi_env = gym.make("Taxi-v3", render_mode="ansi")
action_labels = ["向南", "向北", "向东", "向西", "接乘客", "放下乘客"]
location_names = ["红色站点", "绿色站点", "黄色站点", "蓝色站点"]
preview_state, _ = taxi_env.reset(seed=42)
taxi_row, taxi_col, passenger_idx, dest_idx = taxi_env.unwrapped.decode(preview_state)

print(taxi_env.render())
display(pd.DataFrame([{
    "状态编号": preview_state,
    "出租车位置": f"第 {taxi_row} 行，第 {taxi_col} 列",
    "乘客": "在车上" if passenger_idx == 4 else location_names[passenger_idx],
    "目的地": location_names[dest_idx],
}]))
display(pd.DataFrame({
    "动作编号": range(len(action_labels)),
    "动作": action_labels,
    "含义": ["向南移动", "向北移动", "向东移动", "向西移动", "接乘客", "放下乘客"],
}))

# Q-learning：每一步用奖励和下一状态更新 Q(s,a)。
n_states_taxi = taxi_env.observation_space.n
n_actions_taxi = taxi_env.action_space.n
Q_taxi = np.zeros((n_states_taxi, n_actions_taxi))
alpha = 0.15
gamma = 0.95
epsilon_start = 1.0
epsilon_end = 0.05
episodes = 1600
rng = np.random.default_rng(11)
training_rows = []
td_samples = []

for episode in range(1, episodes + 1):
    state, _ = taxi_env.reset(seed=episode)
    total_reward = 0
    steps = 0
    epsilon = max(epsilon_end, epsilon_start * (0.995 ** episode))
    terminated = truncated = False

    while not (terminated or truncated) and steps < 200:
        if rng.random() < epsilon:
            action = taxi_env.action_space.sample()
        else:
            action = int(np.argmax(Q_taxi[state]))
        next_state, reward, terminated, truncated, _ = taxi_env.step(action)
        before_q = Q_taxi[state, action]
        td_target = reward + gamma * np.max(Q_taxi[next_state]) * (not (terminated or truncated))
        td_error = td_target - Q_taxi[state, action]
        Q_taxi[state, action] += alpha * td_error
        if len(td_samples) < 12:
            td_samples.append({
                "回合": episode,
                "状态": state,
                "动作": action_labels[action],
                "奖励": reward,
                "下一状态": next_state,
                "TD 目标": td_target,
                "TD 误差": td_error,
                "更新前 Q": before_q,
                "更新后 Q": Q_taxi[state, action],
            })
        state = next_state
        total_reward += reward
        steps += 1

    if episode % 100 == 0:
        training_rows.append({"episode": episode, "reward": total_reward, "steps": steps, "epsilon": epsilon})

taxi_trace = pd.DataFrame(training_rows)
td_trace = pd.DataFrame(td_samples).round(3)
display(td_trace)
display(taxi_trace.tail(8).rename(columns={
    "episode": "回合",
    "reward": "回合奖励",
    "steps": "步数",
    "epsilon": "探索率",
}).round(3))
"""


TD_PLOT_CELL = """
# 绘制训练曲线和一个起始状态的动作价值。
start_state, _ = taxi_env.reset(seed=42)
fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.4))
axes[0].plot(taxi_trace["episode"], taxi_trace["reward"], marker="o", color="#2563eb", linewidth=2.0)
axes[0].set_title("出租车调度 Q-learning 回报", loc="left", fontweight="bold")
axes[0].set_xlabel("训练回合")
axes[0].set_ylabel("回合奖励")
axes[0].grid(True, color="#e2e8f0", linewidth=0.8)

axes[1].bar(action_labels, Q_taxi[start_state], color="#f97316")
axes[1].set_title(f"状态 {start_state} 的 Q(s,a)", loc="left", fontweight="bold")
axes[1].tick_params(axis="x", rotation=30)
axes[1].grid(True, axis="y", color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
print(taxi_env.render())
print("当前渲染状态的贪心动作:", action_labels[int(np.argmax(Q_taxi[start_state]))])
taxi_env.close()
"""


CLIFF_INTRO_CELL = """
# 悬崖行走：起点在左下角，终点在右下角，中间一排是悬崖。
cliff_action_labels = ["向上", "向右", "向下", "向左"]
cliff_action_arrows = {0: "↑", 1: "→", 2: "↓", 3: "←"}

cliff_layout = np.full((4, 12), "safe", dtype=object)
cliff_layout[3, 0] = "start"
cliff_layout[3, 11] = "goal"
cliff_layout[3, 1:11] = "cliff"

fig, ax = plt.subplots(figsize=(8.6, 5.0))
color_map = {"safe": "#ecfeff", "start": "#dbeafe", "goal": "#dcfce7", "cliff": "#fee2e2"}
label_map = {"safe": "", "start": "S", "goal": "G", "cliff": "C"}
for r in range(4):
    for c in range(12):
        cell = cliff_layout[r, c]
        ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, color=color_map[cell], ec="#cbd5e1"))
        ax.text(c, r, label_map[cell], ha="center", va="center", fontweight="bold", color="#0f172a")
ax.set_title("悬崖行走初始地图", loc="left", fontweight="bold")
ax.set_xlim(-0.5, 11.5)
ax.set_ylim(3.5, -0.5)
ax.set_xticks(range(12))
ax.set_yticks(range(4))
ax.grid(True, color="#e2e8f0", linewidth=0.7)
plt.tight_layout()
plt.show()

display(pd.DataFrame({
    "策略": ["选择当前 Q 最大动作", "以探索率随机尝试"],
    "读法": ["走已经学到的最好方向", "故意试试看其他方向"],
    "风险": ["可能过早固定路线", "可能踩到悬崖，但也可能发现更短路线"],
}))
"""


BANDIT_CELL = """
# 悬崖行走：在经典网格任务里比较不同探索率的 SARSA。
def train_cliff_sarsa(epsilon, episodes=700, alpha=0.45, gamma=0.99, seed=0):
    env = gym.make("CliffWalking")
    env.action_space.seed(seed)
    rng = np.random.default_rng(seed)
    Q = np.zeros((env.observation_space.n, env.action_space.n))
    rows = []

    def choose_action(state):
        if rng.random() < epsilon:
            return env.action_space.sample()
        return int(np.argmax(Q[state]))

    for episode in range(1, episodes + 1):
        state, _ = env.reset(seed=seed + episode)
        action = choose_action(state)
        total_reward = 0
        steps = 0
        terminated = truncated = False
        while not (terminated or truncated) and steps < 200:
            next_state, reward, terminated, truncated, _ = env.step(action)
            next_action = choose_action(next_state)
            target = reward + gamma * Q[next_state, next_action] * (not (terminated or truncated))
            Q[state, action] += alpha * (target - Q[state, action])
            state, action = next_state, next_action
            total_reward += reward
            steps += 1
        if episode % 50 == 0:
            rows.append({"epsilon": epsilon, "episode": episode, "reward": total_reward, "steps": steps})
    env.close()
    return pd.DataFrame(rows), Q


cliff_runs = []
cliff_tables = {}
for eps in [0.05, 0.10, 0.30]:
    trace, Q = train_cliff_sarsa(eps, seed=21)
    cliff_runs.append(trace)
    cliff_tables[eps] = Q

cliff_trace = pd.concat(cliff_runs, ignore_index=True)
display(cliff_trace.tail(12).rename(columns={
    "epsilon": "探索率",
    "episode": "回合",
    "reward": "回合奖励",
    "steps": "步数",
}))
"""


CLIFF_PATH_CELL = """
# 用训练后的 Q 表走一条贪心路线，查看智能体会如何从 S 走向 G。
def run_cliff_greedy_path(Q, max_steps=40):
    env = gym.make("CliffWalking")
    state, _ = env.reset(seed=5)
    rows = []
    path_coords = [divmod(state, 12)]
    total_reward = 0
    for step in range(1, max_steps + 1):
        action = int(np.argmax(Q[state]))
        next_state, reward, terminated, truncated, _ = env.step(action)
        row, col = divmod(state, 12)
        next_row, next_col = divmod(next_state, 12)
        rows.append({
            "步数": step,
            "当前位置": f"({row},{col})",
            "动作": cliff_action_labels[action],
            "下一位置": f"({next_row},{next_col})",
            "奖励": reward,
        })
        path_coords.append((next_row, next_col))
        total_reward += reward
        state = next_state
        if terminated or truncated:
            break
    env.close()
    return pd.DataFrame(rows), path_coords, total_reward


cliff_path_df, cliff_path_coords, cliff_path_reward = run_cliff_greedy_path(cliff_tables[0.10])
display(cliff_path_df.head(18))
print("总奖励:", cliff_path_reward)

fig, ax = plt.subplots(figsize=(8.6, 5.0))
for r in range(4):
    for c in range(12):
        cell = cliff_layout[r, c]
        ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, color=color_map[cell], ec="#cbd5e1"))
        ax.text(c, r, label_map[cell], ha="center", va="center", fontweight="bold", color="#0f172a")
ys = [r for r, _ in cliff_path_coords]
xs = [c for _, c in cliff_path_coords]
ax.plot(xs, ys, color="#2563eb", linewidth=2.4, marker="o")
ax.set_title("探索率 0.10 训练后的一条贪心路线", loc="left", fontweight="bold")
ax.set_xlim(-0.5, 11.5)
ax.set_ylim(3.5, -0.5)
ax.set_xticks(range(12))
ax.set_yticks(range(4))
ax.grid(True, color="#e2e8f0", linewidth=0.7)
plt.tight_layout()
plt.show()
"""


BANDIT_PLOT_CELL = """
# 绘制探索率对悬崖行走学习表现的影响。
fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.6))
for epsilon, part in cliff_trace.groupby("epsilon"):
    axes[0].plot(part["episode"], part["reward"], marker="o", linewidth=2.0, label=f"探索率={epsilon}")
axes[0].set_title("悬崖行走 SARSA 回报", loc="left", fontweight="bold")
axes[0].set_xlabel("训练回合")
axes[0].set_ylabel("回合奖励")
axes[0].grid(True, color="#e2e8f0", linewidth=0.8)
axes[0].legend()

best_eps = 0.10
policy = np.argmax(cliff_tables[best_eps], axis=1).reshape(4, 12)
arrow = {0: "↑", 1: "→", 2: "↓", 3: "←"}
grid = np.zeros((4, 12))
axes[1].imshow(grid, cmap="Greys", vmin=0, vmax=1)
for r in range(4):
    for c in range(12):
        if r == 3 and 1 <= c <= 10:
            text = "C"
            color = "#dc2626"
        elif (r, c) == (3, 0):
            text = "S"
            color = "#0f172a"
        elif (r, c) == (3, 11):
            text = "G"
            color = "#16a34a"
        else:
            text = arrow[int(policy[r, c])]
            color = "#0f172a"
        axes[1].text(c, r, text, ha="center", va="center", color=color, fontweight="bold")
axes[1].set_title("探索率 0.10 学到的策略", loc="left", fontweight="bold")
axes[1].set_xticks([])
axes[1].set_yticks([])
plt.tight_layout()
plt.show()
"""


ANNEALING_CELL = """
# 参数搜索：在鸢尾花分类任务中比较多组候选参数。
iris = load_iris(as_frame=True)
X_iris = iris.data
y_iris = iris.target
search_rows = []

candidate_params = [
    {"C": float(C), "gamma": float(gamma)}
    for C in np.logspace(-1, 2, 7)
    for gamma in np.logspace(-3, 0, 7)
]
rng = np.random.default_rng(12)
rng.shuffle(candidate_params)

for trial, params in enumerate(candidate_params[:36], start=1):
    model = make_pipeline(
        StandardScaler(),
        SVC(C=params["C"], gamma=params["gamma"], kernel="rbf"),
    )
    scores = cross_val_score(model, X_iris, y_iris, cv=5)
    accuracy = float(scores.mean())
    search_rows.append({
        "trial": trial,
        "log10_C": np.log10(params["C"]),
        "log10_gamma": np.log10(params["gamma"]),
        "C": params["C"],
        "gamma": params["gamma"],
        "cv_accuracy": accuracy,
        "error": 1 - accuracy,
    })

search_df = pd.DataFrame(search_rows)
search_df["best_accuracy"] = search_df["cv_accuracy"].cummax()
best_row = search_df.loc[search_df["cv_accuracy"].idxmax()]
best_params = pd.DataFrame([{
    "最佳 C": best_row["C"],
    "最佳 gamma": best_row["gamma"],
    "验证准确率": best_row["cv_accuracy"],
    "尝试次数": len(search_df),
}])

display(pd.DataFrame({
    "样本数": [len(X_iris)],
    "特征数": [X_iris.shape[1]],
    "类别": [", ".join(iris.target_names)],
}))
display(best_params.round(4))
display(search_df.tail(10).rename(columns={
    "trial": "尝试",
    "log10_C": "log10(C)",
    "log10_gamma": "log10(gamma)",
    "cv_accuracy": "验证准确率",
    "error": "错误率",
}).round(4))
"""


ANNEALING_PLOT_CELL = """
# 绘制超参数搜索轨迹和搜索空间中的高分区域。
fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.7))
axes[0].plot(search_df["trial"], search_df["cv_accuracy"], color="#94a3b8", linewidth=1.4, label="本次尝试")
axes[0].plot(search_df["trial"], search_df["best_accuracy"], color="#2563eb", linewidth=2.5, label="当前最好")
axes[0].set_title("参数搜索过程", loc="left", fontweight="bold")
axes[0].set_xlabel("尝试次数")
axes[0].set_ylabel("验证准确率")
axes[0].grid(True, color="#e2e8f0", linewidth=0.8)
axes[0].legend()

sc = axes[1].scatter(
    search_df["log10_C"],
    search_df["log10_gamma"],
    c=search_df["cv_accuracy"],
    cmap="YlGnBu",
    s=42,
    edgecolors="white",
    linewidth=0.45,
)
axes[1].scatter(best_row["log10_C"], best_row["log10_gamma"], s=180, marker="*", color="#f97316", edgecolor="#0f172a", linewidth=0.7)
axes[1].set_title("鸢尾花参数空间", loc="left", fontweight="bold")
axes[1].set_xlabel("log10(C)")
axes[1].set_ylabel("log10(gamma)")
axes[1].grid(True, color="#e2e8f0", linewidth=0.8)
fig.colorbar(sc, ax=axes[1], fraction=0.046, pad=0.04)
plt.tight_layout()
plt.show()
"""


MCTS_INTRO_CELL = """
# MCTS 先从起点看候选动作，再用模拟逐步判断哪个动作更值得走。
mcts_map = np.array([
    list("SFFF"),
    list("FHFF"),
    list("FFFH"),
    list("HFFG"),
])
n_rows, n_cols = mcts_map.shape
mcts_actions = {0: "左", 1: "下", 2: "右", 3: "上"}
mcts_arrows = {0: "←", 1: "↓", 2: "→", 3: "↑"}
action_delta = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}
side_actions = {0: (3, 1), 1: (0, 2), 2: (1, 3), 3: (2, 0)}
root_state = 0
goal_state = int(np.flatnonzero(mcts_map.reshape(-1) == "G")[0])

def state_to_rc(state):
    return divmod(int(state), n_cols)


def rc_to_state(row, col):
    return int(row * n_cols + col)


def state_name(state):
    row, col = state_to_rc(state)
    return f"{mcts_map[row, col]}({row},{col})"


def goal_distance(state):
    row, col = state_to_rc(state)
    goal_row, goal_col = state_to_rc(goal_state)
    return abs(row - goal_row) + abs(col - goal_col)


def move_state(state, action):
    row, col = state_to_rc(state)
    dr, dc = action_delta[action]
    next_row = min(max(row + dr, 0), n_rows - 1)
    next_col = min(max(col + dc, 0), n_cols - 1)
    return rc_to_state(next_row, next_col)


def mcts_step_model(state, action):
    tile = mcts_map[state_to_rc(state)]
    if tile in {"H", "G"}:
        return [(1.0, state, 0.0, True, "已结束")]

    candidates = [(action, 0.76, "按计划")] + [(a, 0.12, "滑向侧边") for a in side_actions[action]]
    outcomes = []
    old_dist = goal_distance(state)
    for actual_action, prob, cause in candidates:
        next_state = move_state(state, actual_action)
        next_tile = mcts_map[state_to_rc(next_state)]
        progress = 0.10 * (old_dist - goal_distance(next_state))
        reward = -0.02 + progress
        done = next_tile in {"H", "G"}
        if next_tile == "G":
            reward += 1.2
        elif next_tile == "H":
            reward -= 0.35
        outcomes.append((prob, next_state, reward, done, cause))
    return outcomes


def action_candidate_table(state):
    rows = []
    for action in mcts_actions:
        outcomes = mcts_step_model(state, action)
        expected_reward = sum(prob * reward for prob, _, reward, _, _ in outcomes)
        hole_risk = sum(prob for prob, next_state, _, _, _ in outcomes if mcts_map[state_to_rc(next_state)] == "H")
        goal_chance = sum(prob for prob, next_state, _, _, _ in outcomes if mcts_map[state_to_rc(next_state)] == "G")
        rows.append({
            "当前状态": state_name(state),
            "候选动作": mcts_actions[action],
            "一步期望得分": expected_reward,
            "掉洞概率": hole_risk,
            "到达概率": goal_chance,
            "可能到达": " / ".join(f"{prob:.2f}→{state_name(next_state)}" for prob, next_state, _, _, _ in outcomes),
        })
    return pd.DataFrame(rows)


def transition_detail_table(state):
    rows = []
    for action in mcts_actions:
        for prob, next_state, reward, done, cause in mcts_step_model(state, action):
            rows.append({
                "当前状态": state_name(state),
                "候选动作": mcts_actions[action],
                "实际结果": cause,
                "可能到达": state_name(next_state),
                "概率": prob,
                "即时得分": reward,
                "是否结束": done,
            })
    return pd.DataFrame(rows)


def draw_mcts_lake(ax, title, highlight_state=None, path_states=None):
    tile_color = {"S": "#dbeafe", "F": "#ecfeff", "H": "#fee2e2", "G": "#dcfce7"}
    path_states = set(path_states or [])
    for row in range(n_rows):
        for col in range(n_cols):
            state = rc_to_state(row, col)
            tile = mcts_map[row, col]
            ax.add_patch(plt.Rectangle((col - 0.5, row - 0.5), 1, 1, color=tile_color[tile], ec="#94a3b8"))
            ax.text(col, row, tile, ha="center", va="center", fontsize=15, fontweight="bold", color="#0f172a")
            if state in path_states:
                ax.add_patch(plt.Rectangle((col - 0.42, row - 0.42), 0.84, 0.84, fill=False, ec="#f97316", lw=2.4))
    if highlight_state is not None:
        row, col = state_to_rc(highlight_state)
        ax.scatter([col], [row], s=260, facecolors="none", edgecolors="#2563eb", linewidths=2.6)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xlim(-0.5, n_cols - 0.5)
    ax.set_ylim(n_rows - 0.5, -0.5)
    ax.set_xticks(range(n_cols))
    ax.set_yticks(range(n_rows))
    ax.grid(True, color="#cbd5e1", linewidth=0.8)

fig, ax = plt.subplots(figsize=(4.8, 4.4))
draw_mcts_lake(ax, "冰湖规划起点", highlight_state=root_state)
plt.tight_layout()
plt.show()

display(action_candidate_table(root_state).round(3))
display(transition_detail_table(root_state).round(3))
"""


MCTS_CELL = """
# 运行 UCT：平均回报代表动作已有表现，探索项代表还值得继续试探。
rng = np.random.default_rng(12)
N_state = defaultdict(int)
N_action = defaultdict(int)
W_action = defaultdict(float)

def sample_model_step(state, action):
    outcomes = mcts_step_model(state, action)
    probs = np.array([item[0] for item in outcomes], dtype=float)
    probs = probs / probs.sum()
    idx = rng.choice(len(outcomes), p=probs)
    prob, next_state, reward, done, _ = outcomes[idx]
    return next_state, reward, done


def uct_action(state, c=1.4):
    for action in mcts_actions:
        if N_action[(state, action)] == 0:
            return action
    scores = []
    for action in mcts_actions:
        mean_value = W_action[(state, action)] / N_action[(state, action)]
        explore = c * np.sqrt(np.log(N_state[state] + 1) / N_action[(state, action)])
        scores.append(mean_value + explore)
    return int(np.argmax(scores))


def rollout_action(state):
    scores = []
    for action in mcts_actions:
        outcomes = mcts_step_model(state, action)
        scores.append(sum(prob * reward for prob, _, reward, _, _ in outcomes))
    scores = np.array(scores)
    weights = np.exp((scores - scores.max()) * 5.0)
    weights = weights / weights.sum()
    return int(rng.choice(list(mcts_actions.keys()), p=weights))


def rollout(state, depth_limit=18, gamma=0.99):
    total = 0.0
    discount = 1.0
    for _ in range(depth_limit):
        action = rollout_action(state)
        state, reward, done = sample_model_step(state, action)
        total += discount * reward
        discount *= gamma
        if done:
            break
    return total


simulation_rows = []
early_simulation_rows = []
for simulation in range(1, 1001):
    state = root_state
    path = []
    path_states = [root_state]
    path_actions = []
    total_reward = 0.0
    discount = 1.0
    done = False
    for depth in range(18):
        action = uct_action(state)
        path.append((state, action))
        path_actions.append(mcts_actions[action])
        next_state, reward, done = sample_model_step(state, action)
        total_reward += discount * reward
        discount *= 0.99
        state = next_state
        path_states.append(state)
        if done:
            break
    if not done:
        total_reward += discount * rollout(state)

    if simulation <= 8:
        early_simulation_rows.append({
            "模拟轮次": simulation,
            "动作序列": " → ".join(path_actions[:8]),
            "状态序列": " → ".join(state_name(s) for s in path_states[:9]),
            "累计回报": total_reward,
        })

    for state, action in path:
        N_state[state] += 1
        N_action[(state, action)] += 1
        W_action[(state, action)] += total_reward
    if simulation % 200 == 0:
        simulation_rows.append({"simulation": simulation, "root_visits": N_state[root_state]})

root_rows = []
for action in mcts_actions:
    visits = N_action[(root_state, action)]
    mean_value = W_action[(root_state, action)] / visits if visits else 0
    explore = 1.4 * np.sqrt(np.log(N_state[root_state] + 1) / visits) if visits else 0
    root_rows.append({
        "action_id": action,
        "action": mcts_actions[action],
        "visits": visits,
        "mean_value": mean_value,
        "explore": explore,
        "UCT": mean_value + explore,
    })

mcts_root_df = pd.DataFrame(root_rows).sort_values("UCT", ascending=False).reset_index(drop=True)
mcts_sim_df = pd.DataFrame(simulation_rows)
display(pd.DataFrame(early_simulation_rows).round(4))
display(mcts_root_df.rename(columns={
    "action_id": "动作编号",
    "action": "动作",
    "visits": "访问次数",
    "mean_value": "平均回报",
    "explore": "探索项",
}).round(4))
print("起点推荐动作:", mcts_root_df.loc[0, "action"])
"""


MCTS_NEXT_CELL = """
# 沿着根节点推荐动作走一步，再查看新状态的候选动作。
best_root_action = int(mcts_root_df.loc[0, "action_id"])
best_outcomes = mcts_step_model(root_state, best_root_action)
safe_outcomes = [item for item in best_outcomes if mcts_map[state_to_rc(item[1])] != "H"]
next_prob, next_state, next_reward, next_done, _ = max(safe_outcomes, key=lambda item: (item[0], item[2]))
next_candidates = action_candidate_table(next_state).sort_values("一步期望得分", ascending=False).reset_index(drop=True)

display(pd.DataFrame([{
    "起点动作": mcts_actions[best_root_action],
    "最可能下一状态": state_name(next_state),
    "该步概率": next_prob,
    "即时得分": next_reward,
    "是否结束": next_done,
}]).round(3))
display(next_candidates.round(3))
display(transition_detail_table(next_state).round(3))

fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))
draw_mcts_lake(axes[0], "从起点推进一步", highlight_state=next_state, path_states=[root_state, next_state])
root_r, root_c = state_to_rc(root_state)
next_r, next_c = state_to_rc(next_state)
axes[0].annotate("", xy=(next_c, next_r), xytext=(root_c, root_r), arrowprops={"arrowstyle": "->", "lw": 2.4, "color": "#2563eb"})

axes[1].bar(next_candidates["候选动作"], next_candidates["一步期望得分"], color="#2563eb")
axes[1].axhline(0, color="#94a3b8", linewidth=0.9)
axes[1].set_title(f"{state_name(next_state)} 的下一轮候选", loc="left", fontweight="bold")
axes[1].set_ylabel("一步期望得分")
axes[1].grid(True, axis="y", color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
"""


MCTS_PLOT_CELL = """
# 绘制根节点动作统计和 MCTS 访问到的状态价值。
fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.7))
x = np.arange(len(mcts_root_df))
axes[0].bar(x - 0.18, mcts_root_df["mean_value"], width=0.36, color="#2563eb", label="平均回报")
axes[0].bar(x + 0.18, mcts_root_df["UCT"], width=0.36, color="#f97316", label="UCT 总分")
axes[0].set_xticks(x, mcts_root_df["action"])
axes[0].set_title("起点动作评分组成", loc="left", fontweight="bold")
axes[0].set_ylabel("评分")
axes[0].axhline(0, color="#94a3b8", linewidth=0.9)
axes[0].grid(True, axis="y", color="#e2e8f0", linewidth=0.8)
axes[0].legend()

state_count = n_rows * n_cols
value_grid = np.zeros(state_count)
policy_grid = np.full(state_count, -1)
for state in range(state_count):
    values = []
    for action in mcts_actions:
        visits = N_action[(state, action)]
        values.append(W_action[(state, action)] / visits if visits else np.nan)
    if not np.all(np.isnan(values)):
        policy_grid[state] = int(np.nanargmax(values))
        value_grid[state] = float(np.nanmax(values))
value_grid = value_grid.reshape(n_rows, n_cols)
policy_grid = policy_grid.reshape(n_rows, n_cols)

im = axes[1].imshow(value_grid, cmap="RdYlGn", vmin=min(-1.0, value_grid.min()), vmax=max(1.0, value_grid.max()))
for state in range(state_count):
    r, c = state_to_rc(state)
    tile = mcts_map[r, c]
    arrow = "" if tile in {"H", "G"} or policy_grid[r, c] < 0 else mcts_arrows[int(policy_grid[r, c])]
    axes[1].text(c, r, f"{tile}\\n{value_grid[r, c]:.2f}\\n{arrow}", ha="center", va="center", color="#0f172a", fontweight="bold")
axes[1].set_title("MCTS 估计状态价值", loc="left", fontweight="bold")
axes[1].set_xticks(range(n_cols))
axes[1].set_yticks(range(n_rows))
fig.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)
plt.tight_layout()
plt.show()
"""


DIFFUSION_SETUP_CELL = """
# 安装并导入扩散调度器需要的公开库。
diffusion_packages = {
    "torch": "torch>=2.2",
    "diffusers": "diffusers>=0.30",
}
missing = [package for module, package in diffusion_packages.items() if importlib.util.find_spec(module) is None]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

import torch
from diffusers import DDPMScheduler
"""


DIFFUSION_1D_CELL = """
# 真实图片扩散：按时间步逐渐加入噪声。
ddpm_photo = Image.fromarray(load_sample_image("flower.jpg")).resize((128, 128))
ddpm_image = np.asarray(ddpm_photo).astype("float32") / 255.0
sample = torch.tensor(ddpm_image).permute(2, 0, 1).unsqueeze(0) * 2 - 1
torch.manual_seed(12)
noise = torch.randn(sample.shape)
scheduler = DDPMScheduler(num_train_timesteps=1000)
timesteps = [0, 100, 300, 600, 900]
ddpm_images = []
diff_rows = []

for t in timesteps:
    timestep = torch.tensor([t], dtype=torch.long)
    noisy = scheduler.add_noise(sample, noise, timestep)
    image = ((noisy[0].permute(1, 2, 0).numpy() + 1) / 2).clip(0, 1)
    ddpm_images.append(image)
    alpha_bar = float(scheduler.alphas_cumprod[t])
    diff_rows.append({
        "时间步": t,
        "累计保留系数": alpha_bar,
        "原图权重": np.sqrt(alpha_bar),
        "噪声权重": np.sqrt(1 - alpha_bar),
        "像素标准差": float(image.std()),
    })

diff_1d_df = pd.DataFrame(diff_rows)
display(diff_1d_df.round(4))
"""


DIFFUSION_1D_PLOT_CELL = """
# 绘制真实图片在不同时间步下的前向扩散效果。
fig, axes = plt.subplots(2, 3, figsize=(9.0, 6.0))
for ax, image, timestep in zip(axes.ravel(), ddpm_images, timesteps):
    ax.imshow(image)
    ax.set_title(f"时间步 {timestep}", fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
for ax in axes.ravel()[len(ddpm_images):]:
    ax.axis("off")
fig.suptitle("真实图片前向加噪", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


PHOTO_DENOISE_DATA_CELL = """
# 真实图片去噪：把一张花朵照片切成图块，作为训练样本。
photo_clean = np.asarray(Image.fromarray(load_sample_image("flower.jpg")).resize((96, 96))).astype("float32") / 255.0
patch_size = 12
stride = 6

clean_patches = []
patch_positions = []
for row in range(0, photo_clean.shape[0] - patch_size + 1, stride):
    for col in range(0, photo_clean.shape[1] - patch_size + 1, stride):
        clean_patches.append(photo_clean[row:row + patch_size, col:col + patch_size].reshape(-1))
        patch_positions.append((row, col))
clean_patches = np.array(clean_patches)

display(pd.DataFrame({
    "图片": ["flower.jpg"],
    "图片尺寸": [f"{photo_clean.shape[0]}x{photo_clean.shape[1]}"],
    "图块尺寸": [f"{patch_size}x{patch_size}"],
    "训练图块数": [len(clean_patches)],
}))
"""


PHOTO_FORWARD_CELL = """
# 前向加噪：同一张真实图片在不同噪声强度下逐渐丢失结构。
rng = np.random.default_rng(11)
noise = rng.normal(size=photo_clean.shape)
noise_levels = [0.00, 0.20, 0.45, 0.70]
photo_forward = []
for level in noise_levels:
    noisy = np.sqrt(1 - level) * photo_clean + np.sqrt(level) * noise
    photo_forward.append(np.clip(noisy, 0, 1))

photo_forward_df = pd.DataFrame({
    "噪声强度": noise_levels,
    "相对原图 MSE": [mean_squared_error(photo_clean.reshape(-1), img.reshape(-1)) for img in photo_forward],
    "像素标准差": [float(img.std()) for img in photo_forward],
})
display(photo_forward_df.round(4))
"""


PHOTO_REVERSE_CELL = """
# 用图块去噪器学习从噪声图块还原干净图块。
train_rng = np.random.default_rng(12)
noisy_train = np.clip(clean_patches + train_rng.normal(0, 0.28, clean_patches.shape), 0, 1)
photo_denoiser = MLPRegressor(hidden_layer_sizes=(128,), max_iter=140, random_state=12)
photo_denoiser.fit(noisy_train, clean_patches)

noisy_photo = photo_forward[-1]
noisy_patches = []
for row, col in patch_positions:
    noisy_patches.append(noisy_photo[row:row + patch_size, col:col + patch_size].reshape(-1))
noisy_patches = np.array(noisy_patches)
predicted_patches = np.clip(photo_denoiser.predict(noisy_patches), 0, 1)

denoised_photo = np.zeros_like(photo_clean)
weight = np.zeros(photo_clean.shape[:2] + (1,), dtype=float)
for (row, col), patch in zip(patch_positions, predicted_patches):
    denoised_photo[row:row + patch_size, col:col + patch_size] += patch.reshape(patch_size, patch_size, 3)
    weight[row:row + patch_size, col:col + patch_size] += 1
denoised_photo = denoised_photo / np.maximum(weight, 1)

photo_denoise_summary = pd.DataFrame(
    [
        {"图像": "噪声输入", "相对原图均方误差": mean_squared_error(photo_clean.reshape(-1), noisy_photo.reshape(-1))},
        {"图像": "去噪输出", "相对原图均方误差": mean_squared_error(photo_clean.reshape(-1), denoised_photo.reshape(-1))},
    ]
)
display(photo_denoise_summary.round(4))
"""


PHOTO_DENOISE_PLOT_CELL = """
# 绘制真实图片的前向加噪与图块去噪结果。
fig = plt.figure(figsize=(11.2, 6.2))
gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 1.05], hspace=0.24, wspace=0.08)

for idx, (img, level) in enumerate(zip(photo_forward, noise_levels)):
    ax = fig.add_subplot(gs[0, idx])
    ax.imshow(img)
    ax.set_title(f"噪声强度 {level:.2f}", fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])

for idx, (img, title) in enumerate([
    (photo_clean, "原图"),
    (noisy_photo, "高噪声输入"),
    (denoised_photo, "图块去噪输出"),
    (np.abs(photo_clean - denoised_photo) * 3, "误差 x3"),
]):
    ax = fig.add_subplot(gs[1, idx])
    ax.imshow(np.clip(img, 0, 1))
    ax.set_title(title, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])

fig.suptitle("真实图片扩散直觉：加噪破坏结构，去噪学习局部修复", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


GAN_SETUP_CELL = """
# 安装并导入 GAN 需要的公开库。
gan_packages = {"torch": "torch>=2.2"}
missing = [package for module, package in gan_packages.items() if importlib.util.find_spec(module) is None]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

import torch
from torch import nn
"""


GAN_CELL = """
# 真实图片图块 GAN：用花朵照片中的图块训练生成器和判别器。
torch.manual_seed(7)
gan_photo = np.asarray(Image.fromarray(load_sample_image("flower.jpg")).resize((128, 128))).astype("float32") / 255.0
gan_patch_size = 16
gan_stride = 8
real_patch_list = []
for row in range(0, gan_photo.shape[0] - gan_patch_size + 1, gan_stride):
    for col in range(0, gan_photo.shape[1] - gan_patch_size + 1, gan_stride):
        real_patch_list.append(gan_photo[row:row + gan_patch_size, col:col + gan_patch_size])
real_patches_np = np.array(real_patch_list)
real_patches = torch.tensor(real_patches_np.reshape(len(real_patches_np), -1) * 2 - 1, dtype=torch.float32)

latent_dim = 24
patch_dim = real_patches.shape[1]
batch_size = 96

generator = nn.Sequential(
    nn.Linear(latent_dim, 128),
    nn.ReLU(),
    nn.Linear(128, 256),
    nn.ReLU(),
    nn.Linear(256, patch_dim),
    nn.Tanh(),
)
discriminator = nn.Sequential(
    nn.Linear(patch_dim, 256),
    nn.LeakyReLU(0.2),
    nn.Linear(256, 128),
    nn.LeakyReLU(0.2),
    nn.Linear(128, 1),
)
loss_fn = nn.BCEWithLogitsLoss()
opt_g = torch.optim.Adam(generator.parameters(), lr=0.0015, betas=(0.5, 0.999))
opt_d = torch.optim.Adam(discriminator.parameters(), lr=0.0015, betas=(0.5, 0.999))
gan_rows = []

for step in range(1, 401):
    idx = torch.randint(0, len(real_patches), (batch_size,))
    real_batch = real_patches[idx]
    z = torch.randn(batch_size, latent_dim)
    fake_batch = generator(z).detach()

    real_logits = discriminator(real_batch)
    fake_logits = discriminator(fake_batch)
    d_loss = loss_fn(real_logits, torch.ones_like(real_logits)) + loss_fn(fake_logits, torch.zeros_like(fake_logits))
    opt_d.zero_grad()
    d_loss.backward()
    opt_d.step()

    z = torch.randn(batch_size, latent_dim)
    generated = generator(z)
    g_logits = discriminator(generated)
    g_loss = loss_fn(g_logits, torch.ones_like(g_logits))
    opt_g.zero_grad()
    g_loss.backward()
    opt_g.step()

    if step % 50 == 0:
        with torch.no_grad():
            gan_rows.append({
                "训练步": step,
                "判别器损失": float(d_loss),
                "生成器损失": float(g_loss),
                "真实样本评分": float(torch.sigmoid(discriminator(real_batch)).mean()),
                "生成样本评分": float(torch.sigmoid(discriminator(generator(torch.randn(batch_size, latent_dim)))).mean()),
            })

with torch.no_grad():
    gan_samples = generator(torch.randn(16, latent_dim)).reshape(16, gan_patch_size, gan_patch_size, 3).numpy()
gan_trace = pd.DataFrame(gan_rows)
display(pd.DataFrame({
    "真实图片": ["flower.jpg"],
    "图块数": [len(real_patches)],
    "图块尺寸": [f"{gan_patch_size}x{gan_patch_size}"],
    "生成向量维度": [patch_dim],
}))
display(gan_trace.round(3))
"""


GAN_PLOT_CELL = """
# 绘制训练曲线、真实图块和生成图块。
fig = plt.figure(figsize=(10.8, 7.2))
gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 1.6], hspace=0.38, wspace=0.18)
ax_loss = fig.add_subplot(gs[0, :2])
ax_score = fig.add_subplot(gs[0, 2:])
ax_loss.plot(gan_trace["训练步"], gan_trace["判别器损失"], color="#2563eb", linewidth=2.0, label="判别器损失")
ax_loss.plot(gan_trace["训练步"], gan_trace["生成器损失"], color="#f97316", linewidth=2.0, label="生成器损失")
ax_loss.set_title("训练损失", loc="left", fontweight="bold")
ax_loss.grid(True, color="#e2e8f0", linewidth=0.8)
ax_loss.legend()

ax_score.plot(gan_trace["训练步"], gan_trace["真实样本评分"], color="#16a34a", linewidth=2.0, label="真实样本评分")
ax_score.plot(gan_trace["训练步"], gan_trace["生成样本评分"], color="#dc2626", linewidth=2.0, label="生成样本评分")
ax_score.set_title("判别器输出", loc="left", fontweight="bold")
ax_score.grid(True, color="#e2e8f0", linewidth=0.8)
ax_score.legend()

def patch_tile(images, grid=4):
    rows = [
        np.concatenate([images[i * grid + j] for j in range(grid)], axis=1)
        for i in range(grid)
    ]
    return np.concatenate(rows, axis=0)


real_tile = patch_tile(real_patches_np[:16])
fake_tile = patch_tile(((gan_samples[:16] + 1) / 2).clip(0, 1))
ax_real = fig.add_subplot(gs[1, :2])
ax_fake = fig.add_subplot(gs[1, 2:])
ax_real.imshow(real_tile)
ax_real.set_title("真实图片图块", loc="left", fontweight="bold")
ax_fake.imshow(fake_tile)
ax_fake.set_title("生成图块", loc="left", fontweight="bold")
for ax in (ax_real, ax_fake):
    ax.set_xticks([])
    ax.set_yticks([])
fig.suptitle("真实图片图块 GAN：从花朵局部纹理中学习生成分布", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


IMAGE_DENOISING_CELL = """
# 真实建筑照片去噪：用同一张图片的局部图块训练复原模型。
denoise_clean = np.asarray(Image.fromarray(load_sample_image("china.jpg")).resize((96, 96))).astype("float32") / 255.0
denoise_patch_size = 12
denoise_stride = 6
patches_clean = []
patch_coords = []
for row in range(0, denoise_clean.shape[0] - denoise_patch_size + 1, denoise_stride):
    for col in range(0, denoise_clean.shape[1] - denoise_patch_size + 1, denoise_stride):
        patches_clean.append(denoise_clean[row:row + denoise_patch_size, col:col + denoise_patch_size].reshape(-1))
        patch_coords.append((row, col))
patches_clean = np.array(patches_clean)

rng = np.random.default_rng(19)
noise_sigma = 0.24
patches_noisy = np.clip(patches_clean + rng.normal(0, noise_sigma, patches_clean.shape), 0, 1)
patch_denoiser = MLPRegressor(hidden_layer_sizes=(128,), max_iter=140, random_state=19)
patch_denoiser.fit(patches_noisy, patches_clean)

noisy_image = np.clip(denoise_clean + rng.normal(0, noise_sigma, denoise_clean.shape), 0, 1)
noisy_image_patches = np.array([
    noisy_image[row:row + denoise_patch_size, col:col + denoise_patch_size].reshape(-1)
    for row, col in patch_coords
])
predicted = np.clip(patch_denoiser.predict(noisy_image_patches), 0, 1)

denoised_image = np.zeros_like(denoise_clean)
denoise_weight = np.zeros(denoise_clean.shape[:2] + (1,), dtype=float)
for (row, col), patch in zip(patch_coords, predicted):
    denoised_image[row:row + denoise_patch_size, col:col + denoise_patch_size] += patch.reshape(denoise_patch_size, denoise_patch_size, 3)
    denoise_weight[row:row + denoise_patch_size, col:col + denoise_patch_size] += 1
denoised_image = denoised_image / np.maximum(denoise_weight, 1)

denoise_summary = pd.DataFrame(
    [
        {"图像": "带噪输入", "均方误差": mean_squared_error(denoise_clean.reshape(-1), noisy_image.reshape(-1))},
        {"图像": "去噪输出", "均方误差": mean_squared_error(denoise_clean.reshape(-1), denoised_image.reshape(-1))},
    ]
)
display(pd.DataFrame({
    "图片": ["china.jpg"],
    "图块数": [len(patches_clean)],
    "噪声标准差": [noise_sigma],
}))
display(denoise_summary.round(4))
"""


IMAGE_DENOISING_PLOT_CELL = """
# 绘制真实图片、噪声输入和模型去噪输出。
fig, axes = plt.subplots(2, 2, figsize=(8.4, 7.0))
for ax, image, title in zip(
    axes.ravel(),
    [denoise_clean, noisy_image, denoised_image, np.abs(denoise_clean - denoised_image) * 3],
    ["原图", "带噪输入", "去噪输出", "误差 x3"],
):
    ax.imshow(np.clip(image, 0, 1))
    ax.set_title(title, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
fig.suptitle("真实图片去噪重建：从噪声输入恢复建筑纹理", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


ALPHAFOLD_CELL = """
# AlphaFold 概念实验：先看多序列对齐，再把位置关系写成位置对表征。
sequence = "GIVEQCCTSICSLYQLENYCN"
msa = [
    "GIVEQCCTSICSLYQLENYCN",
    "GIVEQCCASVCSLYQLENYCN",
    "GIVEQCCTSVCSLYQLENFCN",
    "GLIEQCCTSICSLYQLDNYCN",
    "GIVEQACASVCSLYQLENFCN",
    "GVVEQCCTTICSLYQVENYCN",
    "GIVEQCCTSVCALYQLENHCN",
    "ALVEQCCASVCSLYQLENYCN",
]
msa_arr = np.array([list(row) for row in msa])
msa_df = pd.DataFrame(
    msa_arr,
    index=[f"序列{i + 1}" for i in range(len(msa))],
    columns=[f"{i + 1}" for i in range(len(sequence))],
)
conservation = []
for col in msa_arr.T:
    counts = Counter(col)
    conservation.append(counts.most_common(1)[0][1] / len(col))
conservation = np.array(conservation)
positions = np.arange(len(sequence))
sequence_gap = np.abs(positions[:, None] - positions[None, :])
locality_prior = np.exp(-sequence_gap / 7.0)
pair_repr = 0.70 * np.outer(conservation, conservation) + 0.30 * locality_prior

pair_rows = []
for i in range(len(sequence)):
    for j in range(i + 3, len(sequence)):
        pair_rows.append({
            "位置对": f"{i + 1}-{j + 1}",
            "氨基酸对": f"{sequence[i]}-{sequence[j]}",
            "序列间隔": j - i,
            "保守性乘积": conservation[i] * conservation[j],
            "位置对值": pair_repr[i, j],
        })
pair_examples = pd.DataFrame(pair_rows).sort_values("位置对值", ascending=False).head(8).reset_index(drop=True)

pipeline_df = pd.DataFrame(
    [
        {"阶段": "MSA", "输出": f"{len(msa)} 条同源序列"},
        {"阶段": "保守性", "输出": "每个位置的最大频率"},
        {"阶段": "候选位置对", "输出": "保守性与序列间隔共同形成候选分数"},
        {"阶段": "位置对表征", "输出": f"{pair_repr.shape[0]}x{pair_repr.shape[1]} 矩阵"},
    ]
)
display(pipeline_df)
display(msa_df)
display(pd.DataFrame({"位置": range(1, len(sequence) + 1), "氨基酸": list(sequence), "保守性": conservation}).round(2))
display(pair_examples.round(3))
"""


ALPHAFOLD_PLOT_CELL = """
# 绘制位置保守性和位置对表征热力图。
fig, axes = plt.subplots(1, 3, figsize=(13.8, 4.8), gridspec_kw={"width_ratios": [0.95, 1.05, 1.15]})
axes[0].bar(range(1, len(sequence) + 1), conservation, color="#2563eb")
axes[0].set_title("位置保守性", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
axes[0].set_xlabel("序列位置")
axes[0].set_ylabel("最大频率")
axes[0].set_ylim(0, 1.05)
axes[0].grid(True, axis="y", color="#e2e8f0", linewidth=0.8)

top_pairs = pair_examples.sort_values("位置对值")
axes[1].barh(top_pairs["位置对"], top_pairs["位置对值"], color="#f97316")
axes[1].set_title("候选位置对分数", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
axes[1].set_xlabel("位置对值")
axes[1].grid(True, axis="x", color="#e2e8f0", linewidth=0.8)

im = axes[2].imshow(pair_repr, cmap="Blues", vmin=0, vmax=1)
axes[2].set_xticks(range(len(sequence)), list(sequence))
axes[2].set_yticks(range(len(sequence)), list(sequence))
axes[2].set_title("位置对表征热力图", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
fig.colorbar(im, ax=axes[2], fraction=0.046, pad=0.04)
plt.tight_layout()
plt.show()
"""


def notebooks() -> dict[str, list]:
    out: dict[str, list] = {}
    out.update(_ch08())
    out.update(_ch09())
    out.update(_ch10())
    out.update(_ch11())
    out.update(_ch12())
    return out


def _ch08() -> dict[str, list]:
    return {
        "ch08_mlp_backprop.ipynb": flatten([
            rs.chapter_link(
                "第 8 章 · 乳腺癌 MLP 分类代码实验",
                "本页训练一个小型神经网络完成经典二分类任务。读者先看特征表，再看训练损失是否下降，最后看混淆矩阵和预测置信度。",
                ["加载 Wisconsin 乳腺癌数据", "训练 MLP 分类器", "绘制损失曲线、混淆矩阵和预测置信度"],
                "../ch8.html",
            ),
            rs.section("0", "经典二分类数据", "每行是一位样本的细胞核测量指标，模型根据这些特征预测良性或恶性类别。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(MLP_DATA_CELL),
            rs.section("1", "训练与预测", "损失曲线用于判断训练是否稳定，混淆矩阵用于找出模型容易混淆的良性和恶性样本。"),
            rs.code(MLP_TRAIN_CELL),
            rs.code(MLP_RESULT_CELL),
            rs.code(MLP_PLOT_CELL),
        ]),
        "ch08_transe_attention.ipynb": flatten([
            rs.chapter_link(
                "第 8 章 · TransE 与注意力代码实验",
                "本页把“关系”和“注意力”都变成可计算表格。TransE 部分看向量平移是否把国家指向首都；Attention 部分看一个词主要关注句子里的哪些词。",
                ["计算国家-首都 TransE 距离", "计算 Transformer 注意力权重", "绘制几何图和热力图"],
                "../ch8.html",
            ),
            rs.section("0", "环境与数据", "先载入表格、向量和画图工具。后续两部分彼此独立，可以分开运行和阅读。"),
            rs.code(DEPENDENCIES_CELL),
            rs.section("1", "关系向量", "正确三元组的距离应该更小，替换实体后的距离应该变大。几何图帮助读者看到 h + r 是否靠近 t。"),
            rs.code(TRANSE_CELL),
            rs.code(TRANSE_PLOT_CELL),
            rs.section("2", "注意力权重", "热力图的每一行代表一个正在读的词，每一列代表它可以关注的词。颜色越深、数值越大，说明关注越强。"),
            rs.code(ATTENTION_CELL),
            rs.code(ATTENTION_PLOT_CELL),
        ]),
    }


def _ch09() -> dict[str, list]:
    return {
        "ch09_bpe.ipynb": flatten([
            rs.chapter_link(
                "第 9 章 · BPE 代码实验",
                "本页用经典英文词频语料演示子词合并。读者重点看每一轮最高频相邻符号是什么，以及词元总数如何下降。",
                ["准备字符级词表", "执行合并步骤", "绘制符号对频次"],
                "../ch9.html",
            ),
            rs.section("0", "词频语料", "先把单词拆成字符序列，并保留每个单词出现频次。高频词会对合并选择产生更大影响。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(BPE_DATA_CELL),
            rs.section("1", "合并过程", "每一轮选择当前最高频符号对，把它合并成更长的子词。图表同时展示选择依据和压缩效果。"),
            rs.code(BPE_RUN_CELL),
            rs.code(BPE_PLOT_CELL),
        ]),
        "ch09_word2vec_analogy.ipynb": flatten([
            rs.chapter_link(
                "第 9 章 · Skip-gram 代码实验",
                "本页用词向量类比帮助读者理解“向量空间里的语义方向”。重点看最近邻和 king - man + woman 的结果。",
                ["运行 Word2Vec 类比", "计算最近邻", "绘制词向量位置"],
                "../ch9.html",
            ),
            rs.section("0", "词向量表", "这里使用一组可解释的二维/三维向量，目的是看清类比关系，而不是训练大模型。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(SKIPGRAM_DATA_CELL),
            rs.section("1", "类比与最近邻", "最近邻展示相似词，类比向量展示方向差。图里的箭头说明 gender 方向如何在词之间迁移。"),
            rs.code(SKIPGRAM_EMBED_CELL),
            rs.code(SKIPGRAM_PLOT_CELL),
        ]),
        "ch09_attention_lm.ipynb": flatten([
            rs.chapter_link(
                "第 9 章 · 因果注意力与二元词语言模型代码实验",
                "本页把下一词预测拆成两件事：因果注意力只能看左侧上下文，二元词统计给出最简单的下一词分布。",
                ["计算因果注意力", "统计二元词频", "绘制注意力热力图"],
                "../ch9.html",
            ),
            rs.section("0", "因果注意力", "因果遮罩会遮住当前位置右侧的词。热力图中右上角为 0，说明模型不能偷看未来。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(SELF_ATTENTION_CELL),
            rs.section("1", "下一词统计", "二元词模型只根据当前词预测下一个词。它很简单，但能帮助读者理解语言模型的条件概率视角。"),
            rs.code(CHAR_LM_CELL),
            rs.code(SELF_ATTENTION_PLOT_CELL),
        ]),
    }


def _ch10() -> dict[str, list]:
    return {
        "ch10_conv2d_numpy.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · 真实照片卷积代码实验",
                "本页用真实花朵照片观察卷积核如何提取边缘。读者先看原图和卷积核，再看局部窗口的计算值，最后看池化如何压缩特征图。",
                ["加载真实照片", "计算 Sobel 卷积", "绘制边缘特征图"],
                "../ch10.html",
            ),
            rs.section("0", "图像与卷积核", "输入图像来自真实照片，Sobel 核会强调竖向边缘。卷积输出越大，表示该区域越像这个边缘模式。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(CONV_DATA_CELL),
            rs.section("1", "卷积与池化", "卷积逐窗口计算局部模式，池化保留局部最强响应。把三张图连起来看，能看到图像如何逐步变成特征。"),
            rs.code(CONV_PROCESS_CELL),
            rs.code(CONV_PLOT_CELL),
        ]),
        "ch10_vit_patchify.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · ViT 图块切分代码实验",
                "本页用真实照片展示 ViT 的第一步：把图片切成固定大小的小块，再把每个小块展开成向量。读者重点看原图网格和图块表格如何对应。",
                ["加载真实照片", "切分 16×16 图块向量", "绘制图块网格"],
                "../ch10.html",
            ),
            rs.section("0", "真实照片切块", "一张 224×224 图片会被切成 14×14 个图块。每个图块展平后是一条向量，后续模型把这些向量当作序列读取。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(PATCHIFY_CELL),
            rs.code(PATCHIFY_PLOT_CELL),
        ]),
        "ch10_mae_masking.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · MAE 遮挡重建代码实验",
                "本页继续使用同一张真实照片，遮住大部分图块，只把少量可见图块交给模型。读者要观察的是：MAE 学习的不是分类，而是从缺失上下文中重建图像。",
                ["加载同一张真实照片", "随机遮住 75% 图块", "绘制可见图和重建基线"],
                "../ch10.html",
            ),
            rs.section("0", "同一张照片", "先复用上一页的图块切分方式，保证读者看到的是同一个图像案例。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(PATCHIFY_CELL),
            rs.section("1", "遮挡与重建", "遮挡图说明哪些图块被隐藏。可见图显示模型能看到的输入，重建基线用于理解“补全缺失区域”的任务形态。"),
            rs.code(MAE_CELL),
            rs.code(MAE_PLOT_CELL),
        ]),
        "ch10_clip_infonce.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · CLIP 真实图文匹配代码实验",
                "本页用真实图片和自然语言提示做图文匹配。读者先看图片和候选文本，再看概率矩阵：每一行应该把更准确的文字描述排在前面。",
                ["加载真实图片和文本提示", "计算图文相似度", "绘制图文匹配概率"],
                "../ch10.html",
            ),
            rs.section("0", "图片与文本提示", "代码会加载预训练 CLIP，但页面重点不是模型下载，而是读懂图文匹配矩阵：行是图片，列是文本，数值越大表示越匹配。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(CLIP_SETUP_CELL),
            rs.code(CLIP_CELL),
            rs.code(CLIP_PLOT_CELL),
        ]),
    }


def _ch11() -> dict[str, list]:
    return {
        "ch11_mdp_value_iteration.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · 冰湖导航价值迭代代码实验",
                "本页把冰湖导航看成一个 MDP：每个格子是状态，每个方向是动作，滑倒会让转移带有不确定性。读者重点看价值如何从终点向外传播。",
                ["读取冰湖环境转移表", "执行价值迭代", "绘制价值与策略"],
                "../ch11.html",
            ),
            rs.section("0", "冰湖环境", "先看地图和转移表。S 是起点，F 是安全冰面，H 是洞，G 是终点；同一个动作可能因为滑动转到不同格子。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(GYM_SETUP_CELL),
            rs.code(MDP_CELL),
            rs.code(MDP_START_CELL),
            rs.section("1", "价值迭代", "先看一个状态的一次 Bellman 更新，再运行完整迭代。误差曲线下降后，策略箭头就代表当前最推荐的动作。"),
            rs.code(VALUE_ONE_STEP_CELL),
            rs.code(VALUE_ITERATION_CELL),
            rs.code(VALUE_PLOT_CELL),
        ]),
        "ch11_td_learning.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · 出租车调度 Q-learning 代码实验",
                "本页让智能体学习接乘客、送乘客。每一步都会产生奖励或惩罚，Q-learning 用这些反馈更新“在某个状态做某个动作”的价值。",
                ["查看初始出租车状态", "记录 TD 目标和 TD 误差", "绘制回报与 Q 表"],
                "../ch11.html",
            ),
            rs.section("0", "出租车任务", "先渲染一个初始状态，确认出租车、乘客和目的地分别在哪里；再看动作含义和一次次 TD 更新。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(GYM_SETUP_CELL),
            rs.code(TD_CELL),
            rs.code(TD_PLOT_CELL),
        ]),
        "ch11_epsilon_greedy.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · 悬崖行走探索策略代码实验",
                "本页比较不同探索强度下的路径学习。悬崖边路线更短但风险更高，探索率越大，智能体越可能尝试随机动作。",
                ["加载悬崖行走任务", "比较不同探索率", "绘制回报与策略"],
                "../ch11.html",
            ),
            rs.section("0", "悬崖行走任务", "训练曲线展示不同探索强度的回报，策略图展示最终学到的动作方向。把两张图合起来看，才能理解探索的代价。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(GYM_SETUP_CELL),
            rs.code(CLIFF_INTRO_CELL),
            rs.code(BANDIT_CELL),
            rs.code(CLIFF_PATH_CELL),
            rs.code(BANDIT_PLOT_CELL),
        ]),
    }


def _ch12() -> dict[str, list]:
    return {
        "ch12_iris_parameter_search.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 鸢尾花分类参数搜索代码实验",
                "本页把“创造”中的搜索思想放到一个真实分类任务里：尝试多组参数，记录验证表现，观察搜索如何逐步找到更好的组合。",
                ["加载鸢尾花数据", "尝试多组模型参数", "绘制搜索轨迹"],
                "../ch12.html",
            ),
            rs.section("0", "分类任务与参数搜索", "先看数据规模和类别，再看每次尝试的验证准确率。散点图中的每个点都是一组参数，颜色越深代表表现越好。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(ANNEALING_CELL),
            rs.code(ANNEALING_PLOT_CELL),
        ]),
        "ch12_mcts.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 冰湖导航 MCTS 规划代码实验",
                "本页让智能体从起点反复模拟未来路线。每个动作会因为滑动到达不同格子，MCTS 会在平均回报和探索项之间分配模拟次数。",
                ["查看起点候选动作", "反复模拟候选路线", "展开下一状态候选", "绘制访问价值"],
                "../ch12.html",
            ),
            rs.section("0", "从起点规划动作", "先看起点的候选动作、滑动概率和一步期望得分。得分由步进代价、靠近终点的进度、掉洞惩罚和到达奖励共同决定。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(MCTS_INTRO_CELL),
            rs.section("1", "模拟与展开", "MCTS 会反复抽样未来路线。根节点表格展示动作访问次数和平均回报，下一状态表格展示推荐动作落到新格子之后如何继续选择。"),
            rs.code(MCTS_CELL),
            rs.code(MCTS_NEXT_CELL),
            rs.code(MCTS_PLOT_CELL),
        ]),
        "ch12_image_diffusion.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 真实图片扩散加噪代码实验",
                "本页用一张真实花朵照片观察扩散模型的前向过程。时间步越靠后，原图信号越弱、噪声越强，图像结构会逐渐被破坏。",
                ["加载真实图片", "按时间步加入噪声", "绘制噪声调度"],
                "../ch12.html",
            ),
            rs.section("0", "图片加噪过程", "先看调度表，再看图片序列。原图权重下降表示图像信号变弱，噪声权重上升表示随机噪声变强。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(DIFFUSION_SETUP_CELL),
            rs.code(DIFFUSION_1D_CELL),
            rs.code(DIFFUSION_1D_PLOT_CELL),
        ]),
        "ch12_image_denoising_diffusion.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 真实图片扩散去噪代码实验",
                "本页用真实花朵照片看扩散任务的直觉：前向过程把图像逐渐变成噪声，去噪器学习把局部图块修复回来。",
                ["加载真实图片图块", "绘制前向加噪", "展示去噪对比"],
                "../ch12.html",
            ),
            rs.section("0", "真实图片图块", "先把一张照片切成可训练的局部图块。干净图像用于对照，后面的噪声图像和去噪图像都要和它比较。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(PHOTO_DENOISE_DATA_CELL),
            rs.section("1", "加噪与去噪", "第一行展示噪声增强后图像结构如何被破坏；第二行比较原图、高噪声输入、去噪输出和误差。"),
            rs.code(PHOTO_FORWARD_CELL),
            rs.code(PHOTO_REVERSE_CELL),
            rs.code(PHOTO_DENOISE_PLOT_CELL),
        ]),
        "ch12_image_patch_gan.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 真实图片图块 GAN 代码实验",
                "本页用真实花朵照片中的局部图块训练一个小型生成对抗网络。读者同时看损失曲线、真实图块和生成图块。",
                ["加载真实图片图块", "训练生成器和判别器", "绘制生成图块"],
                "../ch12.html",
            ),
            rs.section("0", "生成图片图块", "判别器学习区分真实图块和生成图块，生成器学习骗过判别器。生成样本不追求完美，但应该呈现接近照片局部的颜色和纹理。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(GAN_SETUP_CELL),
            rs.code(GAN_CELL),
            rs.code(GAN_PLOT_CELL),
        ]),
        "ch12_image_denoising.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 真实图片去噪重建代码实验",
                "本页把去噪任务单独拿出来看：给模型一张带噪建筑照片，让它输出更干净的图像。读者重点比较噪声输入和去噪输出的均方误差与视觉差异。",
                ["加载真实图片图块", "训练去噪模型", "比较噪声输入和去噪输出"],
                "../ch12.html",
            ),
            rs.section("0", "去噪重建", "这个实验不是完整扩散模型，而是用真实图片做去噪子任务。它帮助读者理解反向扩散每一步要学习的修复方向。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(IMAGE_DENOISING_CELL),
            rs.code(IMAGE_DENOISING_PLOT_CELL),
        ]),
        "ch12_alphafold_concepts.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 蛋白序列位置对表征代码实验",
                "本页用一个短蛋白片段的多序列对齐，观察哪些位置更保守，以及位置两两组合如何形成位置对表征。",
                ["查看多序列对齐", "计算位置保守性", "绘制位置对表征"],
                "../ch12.html",
            ),
            rs.section("0", "序列对齐与位置对表征", "先看多条同源序列怎样对齐，再看每一列的保守性。位置对表征把两个位置的保守性组合起来，作为结构预测中“位置对关系”的简化入口。"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(ALPHAFOLD_CELL),
            rs.code(ALPHAFOLD_PLOT_CELL),
        ]),
    }
