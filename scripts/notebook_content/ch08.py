"""第 8-12 章 · 代码实验。"""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import flatten


DEPENDENCIES_CELL = """
# 导入实验库，并设置图表中文显示。
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
from scipy.optimize import dual_annealing
from scipy.signal import correlate2d
from sklearn.datasets import load_digits, load_iris, load_sample_image, make_moons
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
# 加载 sklearn digits：8x8 手写数字分类是神经网络入门的经典案例。
digits = load_digits()
X_mlp = digits.data / 16.0
y_mlp = digits.target

X_train_mlp, X_test_mlp, y_train_mlp, y_test_mlp = train_test_split(
    X_mlp,
    y_mlp,
    test_size=0.25,
    stratify=y_mlp,
    random_state=8,
)

digits_summary = pd.DataFrame(
    {
        "样本数": [len(X_mlp)],
        "输入维度": [X_mlp.shape[1]],
        "类别数": [len(np.unique(y_mlp))],
        "训练样本": [len(X_train_mlp)],
        "测试样本": [len(X_test_mlp)],
    }
)
display(digits_summary)
display(pd.DataFrame(X_mlp[:5]).round(2))
"""


MLP_TRAIN_CELL = """
# 训练 sklearn MLPClassifier，并读取 loss_curve_。
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
        "loss": classifier.loss_curve_,
    }
).round(4)

display(mlp_trace.iloc[[0, 1, 2, 9, 19, len(mlp_trace) - 1]])
"""


MLP_RESULT_CELL = """
# 查看测试集预测、准确率和混淆矩阵。
test_pred_mlp = mlp.predict(X_test_mlp)
test_prob_mlp = mlp.predict_proba(X_test_mlp)

score_df = pd.DataFrame(
    [{"数据": "digits 测试集", "accuracy": accuracy_score(y_test_mlp, test_pred_mlp)}]
).round(3)
confusion_df = pd.DataFrame(
    confusion_matrix(y_test_mlp, test_pred_mlp),
    index=[f"真实_{i}" for i in range(10)],
    columns=[f"预测_{i}" for i in range(10)],
)
sample_result = pd.DataFrame(
    {
        "真实": y_test_mlp[:12],
        "预测": test_pred_mlp[:12],
        "预测置信度": np.max(test_prob_mlp[:12], axis=1),
    }
).round(3)

display(score_df)
display(sample_result)
display(confusion_df)
"""


MLP_PLOT_CELL = """
# 绘制 loss 曲线和测试样本预测。
fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.6))

axes[0].plot(mlp_trace["轮次"], mlp_trace["loss"], color="#2563eb", linewidth=2.4)
axes[0].set_title("MLP 训练 loss", loc="left", fontweight="bold")
axes[0].set_xlabel("轮次")
axes[0].set_ylabel("loss")
axes[0].grid(True, color="#e2e8f0", linewidth=0.8)

preview = X_test_mlp[:12].reshape(-1, 8, 8)
tile = np.block([[preview[i * 4 + j] for j in range(4)] for i in range(3)])
axes[1].imshow(tile, cmap="gray_r")
axes[1].set_title("测试样本预览", loc="left", fontweight="bold")
axes[1].set_xticks([])
axes[1].set_yticks([])
for i in range(12):
    row = i // 4
    col = i % 4
    axes[1].text(
        col * 8 + 0.4,
        row * 8 + 7.3,
        f"{y_test_mlp[i]}→{test_pred_mlp[i]}",
        color="#0f172a",
        fontsize=8,
        bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "#e2e8f0", "alpha": 0.9},
    )
axes[1].axis("off")

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
# 用一组可解释的 query/key 特征，让同一句话的 attention 更容易读。
tokens = ["the", "cat", "sat", "on", "the", "mat"]
labels = ["the(1)", "cat", "sat", "on", "the(2)", "mat"]
features = ["subject_noun", "verb", "prep", "place_noun", "det"]

K = pd.DataFrame([
    [0, 0, 0, 0, 1],  # the(1): determiner
    [1, 0, 0, 0, 0],  # cat: subject noun
    [0, 1, 0, 0, 0],  # sat: verb
    [0, 0, 1, 0, 0],  # on: preposition
    [0, 0, 0, 0, 1],  # the(2): determiner
    [0, 0, 0, 1, 0],  # mat: place noun
], index=labels, columns=features)

Q = pd.DataFrame([
    [8.0, 0.0, 0.0, 0.0, 0.0],  # the(1) looks for the noun it modifies: cat
    [0.0, 8.0, 0.0, 0.0, 0.0],  # cat looks for the action: sat
    [6.5, 0.0, 0.0, 6.5, 0.0],  # sat looks at the subject and the location
    [0.0, 0.0, 0.0, 8.0, 0.0],  # on points to its object: mat
    [0.0, 0.0, 0.0, 8.0, 0.0],  # the(2) modifies mat
    [0.0, 0.0, 8.0, 0.0, 0.0],  # mat looks back to the preposition: on
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
ax.set_xlabel("被关注的词 key")
ax.set_ylabel("正在读的词 query")

for i in range(len(labels)):
    max_weight = weights[i].max()
    for j in range(len(labels)):
        value = weights[i, j]
        color = "#ffffff" if value > 0.45 else "#0f172a"
        weight = "bold" if value == max_weight else "normal"
        ax.text(j, i, f"{value:.2f}", ha="center", va="center", color=color, fontweight=weight)
        if value == max_weight:
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="#0f172a", linewidth=2.4))

ax.set_title("Attention 权重热力图", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

link_ax.set_xlim(0, 1)
link_ax.set_ylim(-0.7, len(labels) - 0.25)
link_ax.axis("off")
link_ax.text(0.02, len(labels) - 0.15, "每行最高关注", fontsize=13, fontweight="bold", color="#0f172a")
link_ax.text(0.08, len(labels) - 0.65, "当前词", color="#64748b", fontweight="bold")
link_ax.text(0.68, len(labels) - 0.65, "被关注词", color="#64748b", fontweight="bold")

for i in range(len(tokens)):
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
    "word": list(word_freq.keys()),
    "频次": list(word_freq.values()),
    "初始token序列": [" ".join(tuple(word) + ("</w>",)) for word in word_freq],
}))
print("初始加权 token 数:", weighted_token_count(vocab))
"""


BPE_RUN_CELL = """
# 连续执行若干次 merge，记录每轮最高频 pair 和 token 数变化。
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
        "合并pair": " + ".join(best_pair),
        "频次": best_count,
        "token数": f"{before_total} → {after_total}",
        "减少": before_total - after_total,
        "当前token序列": " | ".join(state),
    })
    history.append((best_pair, best_count, counts, before_total, after_total))

bpe_trace = pd.DataFrame(bpe_rows)
display(bpe_trace)
"""


BPE_PLOT_CELL = """
# 展示第一轮选择依据和连续 merge 后的压缩过程。
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
ax1.set_title("第一轮 pair 频次", loc="left", fontsize=13, fontweight="bold", color="#0f172a")
for idx, value in enumerate(pair_values):
    ax1.text(value + 0.25, idx, str(value), va="center", color="#0f172a", fontweight="bold" if idx == 0 else "normal")
ax1.grid(True, axis="x", color="#e2e8f0", linewidth=0.8)

ax2 = fig.add_subplot(gs[0, 1])
steps = np.arange(len(token_totals))
ax2.plot(steps, token_totals, marker="o", linewidth=2.4, color="#2563eb")
for x, value in zip(steps, token_totals):
    ax2.text(x, value + 2.0, str(value), ha="center", color="#0f172a")
ax2.set_xticks(steps, ["初始"] + [str(i) for i in range(1, len(token_totals))])
ax2.set_xlabel("merge 轮次")
ax2.set_ylabel("加权 token 数")
ax2.set_title("token 数逐轮下降", loc="left", fontsize=13, fontweight="bold", color="#0f172a")
ax2.grid(True, color="#e2e8f0", linewidth=0.8)

ax3 = fig.add_subplot(gs[1, :])
ax3.set_xlim(0, 1)
ax3.set_ylim(0, len(bpe_trace) + 0.8)
ax3.axis("off")
ax3.text(0.02, len(bpe_trace) + 0.35, "Merge 过程", fontsize=13, fontweight="bold", color="#0f172a")
ax3.text(0.05, len(bpe_trace) - 0.05, "轮次", color="#64748b", fontweight="bold")
ax3.text(0.18, len(bpe_trace) - 0.05, "选中 pair", color="#64748b", fontweight="bold")
ax3.text(0.43, len(bpe_trace) - 0.05, "频次", color="#64748b", fontweight="bold")
ax3.text(0.56, len(bpe_trace) - 0.05, "token 数", color="#64748b", fontweight="bold")
ax3.text(0.76, len(bpe_trace) - 0.05, "减少", color="#64748b", fontweight="bold")

for idx, row in bpe_trace.iterrows():
    y = len(bpe_trace) - idx - 0.65
    ax3.add_patch(plt.Rectangle((0.02, y - 0.22), 0.92, 0.38, color="#eff6ff" if idx % 2 == 0 else "#ffffff", ec="#dbeafe", lw=0.8))
    ax3.text(0.07, y, str(row["轮次"]), ha="center", va="center", color="#0f172a", fontweight="bold")
    ax3.text(0.18, y, row["合并pair"], ha="left", va="center", color="#c2410c", fontweight="bold")
    ax3.text(0.45, y, str(row["频次"]), ha="center", va="center", color="#0f172a")
    ax3.text(0.57, y, row["token数"], ha="left", va="center", color="#0f172a")
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
ax.set_xlabel("royalty")
ax.set_ylabel("gender")
plt.tight_layout()
plt.show()
"""


SELF_ATTENTION_CELL = """
# 加入 causal mask 后，每个位置只能看见自己和左侧 token。
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
# 词 bigram：根据当前词统计下一个词分布。
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
# 绘制 causal attention 热力图。
fig, ax = plt.subplots(figsize=(5.8, 4.8))
im = ax.imshow(weights_lm, cmap="Blues", vmin=0, vmax=weights_lm.max())
ax.set_xticks(range(len(lm_tokens)), lm_tokens)
ax.set_yticks(range(len(lm_tokens)), lm_tokens)
for i in range(len(lm_tokens)):
    for j in range(len(lm_tokens)):
        ax.text(j, i, f"{weights_lm[i, j]:.2f}", ha="center", va="center", color="#0f172a")
ax.set_title("Causal Self-Attention", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
plt.tight_layout()
plt.show()
"""


CONV_DATA_CELL = """
# 使用 sklearn digits 中的手写数字，配合 Sobel 核做边缘检测。
digits = load_digits()
image = digits.images[13] / 16.0
kernel = np.array([
    [-1, 0, 1],
    [-1, 0, 1],
    [-1, 0, 1],
], dtype=float)

feature = correlate2d(image, kernel, mode="valid")
display(pd.DataFrame(image).round(2))
display(pd.DataFrame(kernel.astype(int)))
"""


CONV_PROCESS_CELL = """
# 展开每个窗口的卷积值。
rows = []
for i in range(feature.shape[0]):
    for j in range(feature.shape[1]):
        window = image[i:i + 3, j:j + 3]
        rows.append({
            "位置": f"({i},{j})",
            "窗口": window.astype(int).tolist(),
            "卷积值": round(float((window * kernel).sum()), 3),
        })

conv_df = pd.DataFrame(rows)
display(conv_df.head(8))
display(pd.DataFrame(feature).round(3))
"""


CONV_PLOT_CELL = """
# 绘制输入、卷积输出和 2x2 max pooling。
pool = np.array([
    [feature[i:i + 2, j:j + 2].max() for j in range(0, feature.shape[1], 2)]
    for i in range(0, feature.shape[0], 2)
])

fig, axes = plt.subplots(1, 3, figsize=(10.0, 3.8))
for ax, data, title in zip(axes, [image, feature, pool], ["输入", "卷积输出", "MaxPool"]):
    im = ax.imshow(data, cmap="Blues")
    ax.set_title(title, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, f"{data[i, j]:.1f}", ha="center", va="center", color="#0f172a", fontsize=7)
fig.suptitle("Digits Sobel 卷积", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


PATCHIFY_CELL = """
# 使用 sklearn 内置真实照片 china.jpg，按 ViT 常见设置切成 16x16 patch。
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
        "patch_id": patch_id,
        "行": row,
        "列": col,
        "token维度": patch_tokens.shape[1],
        "R均值": patch[:, :, 0].mean(),
        "G均值": patch[:, :, 1].mean(),
        "B均值": patch[:, :, 2].mean(),
        "亮度标准差": patch.mean(axis=2).std(),
    })

patch_df = pd.DataFrame(patch_summary)
display(patch_df.head(12).round(3))
"""


PATCHIFY_PLOT_CELL = """
# 绘制真实图片 patch 网格和若干具体 patch。
selected_patches = [18, 43, 87, 112, 145, 181]
fig = plt.figure(figsize=(10.8, 6.6))
gs = fig.add_gridspec(2, 6, height_ratios=[3.4, 1.5], hspace=0.22, wspace=0.08)
ax_img = fig.add_subplot(gs[0, :])
ax_img.imshow(vit_image)
ax_img.set_title("真实图片切成 14x14 个 patch", loc="left", fontweight="bold")
ax_img.set_xticks(np.arange(0, 225, patch_size))
ax_img.set_yticks(np.arange(0, 225, patch_size))
ax_img.grid(color="#ffffff", linewidth=0.8)
ax_img.tick_params(labelbottom=False, labelleft=False, length=0)

for slot, patch_id in enumerate(selected_patches):
    row, col = divmod(patch_id, patch_grid)
    ax = fig.add_subplot(gs[1, slot])
    ax.imshow(patches[row, col])
    ax.set_title(f"patch {patch_id}\\n({row},{col})", fontsize=9, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])

fig.suptitle("ViT Patchify：真实照片 -> patch tokens", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


MAE_CELL = """
# MAE masking：在同一张真实图片上随机遮住 75% patch，只保留可见 token。
rng = np.random.default_rng(4)
num_patches = len(patch_tokens)
mask_ratio = 0.75
visible_ids = np.sort(rng.choice(num_patches, size=int(num_patches * (1 - mask_ratio)), replace=False))
masked_ids = np.array([idx for idx in range(num_patches) if idx not in set(visible_ids)])

mae_df = pd.DataFrame({
    "指标": ["总patch数", "可见patch数", "mask patch数", "mask比例"],
    "值": [num_patches, len(visible_ids), len(masked_ids), mask_ratio],
})
display(mae_df)
"""


MAE_PLOT_CELL = """
# 绘制 mask 图像和一个简单的均值重建基线。
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

fig, axes = plt.subplots(1, 4, figsize=(11.2, 3.8))
for ax, data, title in zip(
    axes,
    [vit_image, mask_map, masked_image, recon_image],
    ["原图", "mask map", "可见 patch", "均值重建基线"],
):
    cmap = "Greys" if title == "mask map" else None
    ax.imshow(data, cmap=cmap, vmin=0, vmax=1)
    ax.set_title(title, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
fig.suptitle("MAE masking：同一张真实图片的 patch 遮挡", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


CLIP_CELL = """
# CLIP 官方 API：用真实图片和文本提示计算图文匹配。
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

model_id = "openai/clip-vit-base-patch32"
processor = CLIPProcessor.from_pretrained(model_id)
clip_model = CLIPModel.from_pretrained(model_id)
clip_model.eval()

clip_images = [
    Image.fromarray(load_sample_image("china.jpg")),
    Image.fromarray(load_sample_image("flower.jpg")),
]
image_names = ["china.jpg", "flower.jpg"]
text_prompts = [
    "a photo of a Chinese temple by a lake",
    "a close-up photo of a red flower",
    "a photo of a taxi cab",
    "a photo of a handwritten digit",
]

inputs = processor(text=text_prompts, images=clip_images, return_tensors="pt", padding=True)
with torch.no_grad():
    outputs = clip_model(**inputs)

logits = outputs.logits_per_image
probs = logits.softmax(dim=1)
targets = torch.tensor([0, 1])
clip_loss = F.cross_entropy(logits[:, :2], targets).item()

clip_prob_df = pd.DataFrame(probs.numpy(), index=image_names, columns=text_prompts)
display(clip_prob_df.round(3))
print("image-text contrastive loss:", round(float(clip_loss), 4))
"""


CLIP_PLOT_CELL = """
# 绘制真实图片和 CLIP 图文概率矩阵。
sim_matrix = probs.numpy()
fig = plt.figure(figsize=(11.0, 5.4))
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 2.2], wspace=0.35)

for idx, image in enumerate(clip_images):
    ax_img = fig.add_subplot(gs[0, idx])
    ax_img.imshow(image)
    ax_img.set_title(image_names[idx], fontweight="bold")
    ax_img.set_xticks([])
    ax_img.set_yticks([])

ax = fig.add_subplot(gs[0, 2])
im = ax.imshow(sim_matrix, cmap="YlGnBu", vmin=0, vmax=1)
ax.set_xticks(range(len(text_prompts)), text_prompts, rotation=30, ha="right")
ax.set_yticks(range(len(image_names)), image_names)
for i in range(len(image_names)):
    best = int(np.argmax(sim_matrix[i]))
    for j in range(len(text_prompts)):
        value = sim_matrix[i, j]
        ax.text(j, i, f"{value:.2f}", ha="center", va="center", color="#0f172a", fontweight="bold" if j == best else "normal")
        if j == best:
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="#0f172a", linewidth=2.2))
ax.set_title("CLIP 官方模型：图文匹配概率", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
plt.tight_layout()
plt.show()
"""


GYM_SETUP_CELL = """
# 第 11 章使用 Gymnasium 经典环境，保持和官方教程一致的环境接口。
if importlib.util.find_spec("gymnasium") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gymnasium>=0.29"])

import gymnasium as gym
"""


MDP_CELL = """
# FrozenLake-v1：读取 Gymnasium 官方环境自带的 MDP 转移表 P。
frozen_env = gym.make("FrozenLake-v1", map_name="4x4", is_slippery=True)
n_states = frozen_env.observation_space.n
n_actions = frozen_env.action_space.n
action_names = {0: "Left", 1: "Down", 2: "Right", 3: "Up"}
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
                "state": state,
                "tile": tile,
                "action": action_names[action],
                "prob": prob,
                "next_state": next_state,
                "reward": reward,
                "done": terminated,
            })

display(pd.DataFrame(transition_rows).head(16))
display(pd.DataFrame(lake_map))
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
    "state": np.arange(n_states),
    "tile": lake_map.reshape(-1),
    "best_action": [action_names[a] for a in policy_frozen],
    "V": V_frozen,
    "Q_left": Q_frozen[:, 0],
    "Q_down": Q_frozen[:, 1],
    "Q_right": Q_frozen[:, 2],
    "Q_up": Q_frozen[:, 3],
}).round(4)

display(delta_trace.head(8))
display(delta_trace.tail(5))
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
axes[0].set_title("FrozenLake 最优价值与策略", loc="left", fontweight="bold")
axes[0].set_xticks(range(4))
axes[0].set_yticks(range(4))
fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)

axes[1].plot(delta_trace["iteration"], delta_trace["delta"], color="#2563eb", linewidth=2.2)
axes[1].set_yscale("log")
axes[1].set_title("Bellman 误差收敛", loc="left", fontweight="bold")
axes[1].set_xlabel("iteration")
axes[1].set_ylabel("max |V_new - V_old|")
axes[1].grid(True, color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
"""


TD_CELL = """
# Taxi-v3：用 Q-learning 展示真实环境中的 TD target 和 Q 表更新。
taxi_env = gym.make("Taxi-v3", render_mode="ansi")
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
        td_target = reward + gamma * np.max(Q_taxi[next_state]) * (not (terminated or truncated))
        td_error = td_target - Q_taxi[state, action]
        Q_taxi[state, action] += alpha * td_error
        if len(td_samples) < 12:
            td_samples.append({
                "episode": episode,
                "state": state,
                "action": action,
                "reward": reward,
                "next_state": next_state,
                "TD target": td_target,
                "TD error": td_error,
            })
        state = next_state
        total_reward += reward
        steps += 1

    if episode % 100 == 0:
        training_rows.append({"episode": episode, "reward": total_reward, "steps": steps, "epsilon": epsilon})

taxi_trace = pd.DataFrame(training_rows)
td_trace = pd.DataFrame(td_samples).round(3)
display(td_trace)
display(taxi_trace.tail(8).round(3))
"""


TD_PLOT_CELL = """
# 绘制 Taxi-v3 训练曲线和一个起始状态的动作价值。
start_state, _ = taxi_env.reset(seed=42)
fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.4))
axes[0].plot(taxi_trace["episode"], taxi_trace["reward"], marker="o", color="#2563eb", linewidth=2.0)
axes[0].set_title("Taxi-v3 Q-learning 回报", loc="left", fontweight="bold")
axes[0].set_xlabel("episode")
axes[0].set_ylabel("episode reward")
axes[0].grid(True, color="#e2e8f0", linewidth=0.8)

action_labels = ["south", "north", "east", "west", "pickup", "dropoff"]
axes[1].bar(action_labels, Q_taxi[start_state], color="#f97316")
axes[1].set_title(f"状态 {start_state} 的 Q(s,a)", loc="left", fontweight="bold")
axes[1].tick_params(axis="x", rotation=30)
axes[1].grid(True, axis="y", color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
print(taxi_env.render())
print("greedy action at rendered state:", action_labels[int(np.argmax(Q_taxi[start_state]))])
taxi_env.close()
"""


BANDIT_CELL = """
# CliffWalking-v0：在经典悬崖环境里比较不同 epsilon 的 SARSA。
def train_cliff_sarsa(epsilon, episodes=700, alpha=0.45, gamma=0.99, seed=0):
    env = gym.make("CliffWalking-v0")
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
display(cliff_trace.tail(12))
"""


BANDIT_PLOT_CELL = """
# 绘制 epsilon 对 CliffWalking 学习表现的影响。
fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.6))
for epsilon, part in cliff_trace.groupby("epsilon"):
    axes[0].plot(part["episode"], part["reward"], marker="o", linewidth=2.0, label=f"epsilon={epsilon}")
axes[0].set_title("CliffWalking SARSA 回报", loc="left", fontweight="bold")
axes[0].set_xlabel("episode")
axes[0].set_ylabel("episode reward")
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
axes[1].set_title("epsilon=0.10 学到的策略", loc="left", fontweight="bold")
axes[1].set_xticks([])
axes[1].set_yticks([])
plt.tight_layout()
plt.show()
"""


ANNEALING_CELL = """
# SciPy dual_annealing：在 Iris 数据集上搜索 SVC 的 C 和 gamma。
iris = load_iris(as_frame=True)
X_iris = iris.data
y_iris = iris.target
search_rows = []

def svc_cv_error(params):
    log_c, log_gamma = params
    C = 10 ** log_c
    gamma = 10 ** log_gamma
    model = make_pipeline(
        StandardScaler(),
        SVC(C=C, gamma=gamma, kernel="rbf"),
    )
    scores = cross_val_score(model, X_iris, y_iris, cv=5)
    accuracy = float(scores.mean())
    search_rows.append({
        "trial": len(search_rows) + 1,
        "log10_C": log_c,
        "log10_gamma": log_gamma,
        "C": C,
        "gamma": gamma,
        "cv_accuracy": accuracy,
        "error": 1 - accuracy,
    })
    return 1 - accuracy


result = dual_annealing(
    svc_cv_error,
    bounds=[(-2, 3), (-4, 1)],
    maxiter=45,
    seed=12,
    no_local_search=True,
)
search_df = pd.DataFrame(search_rows)
search_df["best_accuracy"] = search_df["cv_accuracy"].cummax()
best_row = search_df.loc[search_df["cv_accuracy"].idxmax()]
best_params = pd.DataFrame([{
    "best_C": best_row["C"],
    "best_gamma": best_row["gamma"],
    "cv_accuracy": best_row["cv_accuracy"],
    "trials": len(search_df),
}])

display(pd.DataFrame({
    "样本数": [len(X_iris)],
    "特征数": [X_iris.shape[1]],
    "类别": [", ".join(iris.target_names)],
}))
display(best_params.round(4))
display(search_df.tail(10).round(4))
"""


ANNEALING_PLOT_CELL = """
# 绘制超参数搜索轨迹和搜索空间中的高分区域。
fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.7))
axes[0].plot(search_df["trial"], search_df["cv_accuracy"], color="#94a3b8", linewidth=1.4, label="trial accuracy")
axes[0].plot(search_df["trial"], search_df["best_accuracy"], color="#2563eb", linewidth=2.5, label="best so far")
axes[0].set_title("dual_annealing 搜索过程", loc="left", fontweight="bold")
axes[0].set_xlabel("trial")
axes[0].set_ylabel("5-fold CV accuracy")
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
axes[1].set_title("Iris SVC 搜索空间", loc="left", fontweight="bold")
axes[1].set_xlabel("log10(C)")
axes[1].set_ylabel("log10(gamma)")
axes[1].grid(True, color="#e2e8f0", linewidth=0.8)
fig.colorbar(sc, ax=axes[1], fraction=0.046, pad=0.04)
plt.tight_layout()
plt.show()
"""


MCTS_CELL = """
# FrozenLake-v1：用 UCT 从起点做 Monte Carlo Tree Search。
mcts_env = gym.make("FrozenLake-v1", map_name="4x4", is_slippery=True)
mcts_P = mcts_env.unwrapped.P
mcts_map = np.array([
    [cell.decode("utf-8") if isinstance(cell, bytes) else str(cell) for cell in row]
    for row in mcts_env.unwrapped.desc
])
mcts_actions = {0: "Left", 1: "Down", 2: "Right", 3: "Up"}
mcts_arrows = {0: "←", 1: "↓", 2: "→", 3: "↑"}
root_state = 0
rng = np.random.default_rng(12)
N_state = defaultdict(int)
N_action = defaultdict(int)
W_action = defaultdict(float)

def sample_model_step(state, action):
    outcomes = mcts_P[state][action]
    probs = np.array([item[0] for item in outcomes], dtype=float)
    probs = probs / probs.sum()
    idx = rng.choice(len(outcomes), p=probs)
    prob, next_state, reward, done = outcomes[idx]
    return next_state, reward, done


def uct_action(state, c=1.4):
    for action in range(mcts_env.action_space.n):
        if N_action[(state, action)] == 0:
            return action
    scores = []
    for action in range(mcts_env.action_space.n):
        mean_value = W_action[(state, action)] / N_action[(state, action)]
        explore = c * np.sqrt(np.log(N_state[state] + 1) / N_action[(state, action)])
        scores.append(mean_value + explore)
    return int(np.argmax(scores))


def rollout(state, depth_limit=18, gamma=0.99):
    total = 0.0
    discount = 1.0
    for _ in range(depth_limit):
        action = rng.integers(mcts_env.action_space.n)
        state, reward, done = sample_model_step(state, int(action))
        total += discount * reward
        discount *= gamma
        if done:
            break
    return total


simulation_rows = []
for simulation in range(1, 1201):
    state = root_state
    path = []
    total_reward = 0.0
    discount = 1.0
    done = False
    for depth in range(18):
        action = uct_action(state)
        path.append((state, action))
        next_state, reward, done = sample_model_step(state, action)
        total_reward += discount * reward
        discount *= 0.99
        state = next_state
        if done:
            break
    if not done:
        total_reward += discount * rollout(state)

    for state, action in path:
        N_state[state] += 1
        N_action[(state, action)] += 1
        W_action[(state, action)] += total_reward
    if simulation % 200 == 0:
        simulation_rows.append({"simulation": simulation, "root_visits": N_state[root_state]})

root_rows = []
for action in range(mcts_env.action_space.n):
    visits = N_action[(root_state, action)]
    mean_value = W_action[(root_state, action)] / visits if visits else 0
    explore = 1.4 * np.sqrt(np.log(N_state[root_state] + 1) / visits) if visits else 0
    root_rows.append({
        "action": mcts_actions[action],
        "visits": visits,
        "mean_value": mean_value,
        "explore": explore,
        "UCT": mean_value + explore,
    })

mcts_root_df = pd.DataFrame(root_rows).sort_values("UCT", ascending=False).reset_index(drop=True)
mcts_sim_df = pd.DataFrame(simulation_rows)
display(pd.DataFrame(mcts_map))
display(mcts_root_df.round(4))
print("root action:", mcts_root_df.loc[0, "action"])
"""


MCTS_PLOT_CELL = """
# 绘制根节点动作统计和 MCTS 访问到的状态价值。
fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.7))
x = np.arange(len(mcts_root_df))
axes[0].bar(x, mcts_root_df["mean_value"], color="#2563eb", label="mean value")
axes[0].bar(x, mcts_root_df["explore"], bottom=mcts_root_df["mean_value"], color="#f97316", label="exploration")
axes[0].set_xticks(x, mcts_root_df["action"])
axes[0].set_title("Root UCT 组成", loc="left", fontweight="bold")
axes[0].set_ylabel("score")
axes[0].grid(True, axis="y", color="#e2e8f0", linewidth=0.8)
axes[0].legend()

value_grid = np.zeros(16)
policy_grid = np.full(16, -1)
for state in range(16):
    values = []
    for action in range(mcts_env.action_space.n):
        visits = N_action[(state, action)]
        values.append(W_action[(state, action)] / visits if visits else np.nan)
    if not np.all(np.isnan(values)):
        policy_grid[state] = int(np.nanargmax(values))
        value_grid[state] = float(np.nanmax(values))
value_grid = value_grid.reshape(4, 4)
policy_grid = policy_grid.reshape(4, 4)

im = axes[1].imshow(value_grid, cmap="YlGnBu", vmin=0, vmax=max(0.01, value_grid.max()))
for state in range(16):
    r, c = divmod(state, 4)
    tile = mcts_map[r, c]
    arrow = "" if tile in {"H", "G"} or policy_grid[r, c] < 0 else mcts_arrows[int(policy_grid[r, c])]
    axes[1].text(c, r, f"{tile}\\n{value_grid[r, c]:.2f}\\n{arrow}", ha="center", va="center", color="#0f172a", fontweight="bold")
axes[1].set_title("MCTS 估计状态价值", loc="left", fontweight="bold")
axes[1].set_xticks(range(4))
axes[1].set_yticks(range(4))
fig.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)
plt.tight_layout()
plt.show()
"""


DIFFUSION_1D_CELL = """
# Diffusers 官方 scheduler：在真实图片上执行 DDPM 前向加噪。
diffusion_packages = {
    "torch": "torch>=2.2",
    "diffusers": "diffusers>=0.30",
}
missing = [package for module, package in diffusion_packages.items() if importlib.util.find_spec(module) is None]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

import torch
from diffusers import DDPMScheduler

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
        "timestep": t,
        "alpha_bar": alpha_bar,
        "signal_weight": np.sqrt(alpha_bar),
        "noise_weight": np.sqrt(1 - alpha_bar),
        "pixel_std": float(image.std()),
    })

diff_1d_df = pd.DataFrame(diff_rows)
display(diff_1d_df.round(4))
"""


DIFFUSION_1D_PLOT_CELL = """
# 绘制真实图片在不同 timestep 下的前向扩散效果。
fig, axes = plt.subplots(1, len(ddpm_images), figsize=(11.2, 3.1))
for ax, image, timestep in zip(axes, ddpm_images, timesteps):
    ax.imshow(image)
    ax.set_title(f"t={timestep}", fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
fig.suptitle("DDPMScheduler：真实图片前向加噪", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


DIGITS_DATA_CELL = """
# 使用 sklearn digits 数据，选出一个 8x8 手写数字。
digits = load_digits()
digit_label = 3
digit_indices = np.where(digits.target == digit_label)[0]
clean_digit = digits.images[digit_indices[4]] / 16.0
prototype_digit = digits.images[digit_indices].mean(axis=0) / 16.0

display(pd.DataFrame(clean_digit).round(2))
print("样本数量:", len(digit_indices), "目标数字:", digit_label)
"""


DIGITS_FORWARD_CELL = """
# 前向加噪：同一个数字在不同 t 下逐渐变得更难辨认。
rng = np.random.default_rng(11)
digit_noise = rng.normal(size=clean_digit.shape)
digit_steps = [0.0, 0.25, 0.50, 0.75]
digit_forward = []
for level in digit_steps:
    noisy = np.sqrt(1 - level) * clean_digit + np.sqrt(level) * digit_noise
    digit_forward.append(noisy)

digit_forward_df = pd.DataFrame({
    "噪声强度": digit_steps,
    "MSE": [round(mean_squared_error(clean_digit, img), 4) for img in digit_forward],
})
display(digit_forward_df)
"""


DIGITS_REVERSE_CELL = """
# 反向去噪示例：用同类数字原型把 noisy 图像拉回数字形状。
noisy_digit = digit_forward[-1]
denoised_digit = 0.58 * noisy_digit + 0.42 * prototype_digit
digits_summary = pd.DataFrame(
    [
        {"图像": "noisy", "相对clean的MSE": mean_squared_error(clean_digit, noisy_digit)},
        {"图像": "denoised", "相对clean的MSE": mean_squared_error(clean_digit, denoised_digit)},
    ]
).round(4)
display(digits_summary)
"""


DIGITS_PLOT_CELL = """
# 绘制前向加噪和去噪对比。
fig, axes = plt.subplots(2, 4, figsize=(9.5, 5.1))
for ax, img, level in zip(axes[0], digit_forward, digit_steps):
    ax.imshow(img, cmap="gray_r")
    ax.set_title(f"noise={level:.2f}", fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
for ax, img, title in zip(axes[1], [clean_digit, noisy_digit, prototype_digit, denoised_digit], ["clean", "noisy", "prototype", "denoised"]):
    ax.imshow(img, cmap="gray_r")
    ax.set_title(title, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
fig.suptitle("Digits diffusion", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


GAN_CELL = """
# PyTorch GAN：在 sklearn Digits 真实手写数字上训练生成器和判别器。
gan_packages = {"torch": "torch>=2.2"}
missing = [package for module, package in gan_packages.items() if importlib.util.find_spec(module) is None]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

import torch
from torch import nn

torch.manual_seed(7)
digits = load_digits()
real_digits = torch.tensor(digits.images / 16.0 * 2 - 1, dtype=torch.float32).reshape(-1, 64)
latent_dim = 16
batch_size = 96

generator = nn.Sequential(
    nn.Linear(latent_dim, 64),
    nn.ReLU(),
    nn.Linear(64, 128),
    nn.ReLU(),
    nn.Linear(128, 64),
    nn.Tanh(),
)
discriminator = nn.Sequential(
    nn.Linear(64, 128),
    nn.LeakyReLU(0.2),
    nn.Linear(128, 64),
    nn.LeakyReLU(0.2),
    nn.Linear(64, 1),
)
loss_fn = nn.BCEWithLogitsLoss()
opt_g = torch.optim.Adam(generator.parameters(), lr=0.0015, betas=(0.5, 0.999))
opt_d = torch.optim.Adam(discriminator.parameters(), lr=0.0015, betas=(0.5, 0.999))
gan_rows = []

for step in range(1, 501):
    idx = torch.randint(0, len(real_digits), (batch_size,))
    real_batch = real_digits[idx]
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
                "step": step,
                "D_loss": float(d_loss),
                "G_loss": float(g_loss),
                "D(real)": float(torch.sigmoid(discriminator(real_batch)).mean()),
                "D(fake)": float(torch.sigmoid(discriminator(generator(torch.randn(batch_size, latent_dim)))).mean()),
            })

with torch.no_grad():
    gan_samples = generator(torch.randn(16, latent_dim)).reshape(16, 8, 8).numpy()
gan_trace = pd.DataFrame(gan_rows)
display(gan_trace.round(3))
"""


GAN_PLOT_CELL = """
# 绘制训练曲线和生成的 digits 样本。
fig = plt.figure(figsize=(10.6, 6.0))
gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 1.6], hspace=0.38, wspace=0.18)
ax_loss = fig.add_subplot(gs[0, :2])
ax_score = fig.add_subplot(gs[0, 2:])
ax_loss.plot(gan_trace["step"], gan_trace["D_loss"], color="#2563eb", linewidth=2.0, label="D loss")
ax_loss.plot(gan_trace["step"], gan_trace["G_loss"], color="#f97316", linewidth=2.0, label="G loss")
ax_loss.set_title("GAN loss", loc="left", fontweight="bold")
ax_loss.grid(True, color="#e2e8f0", linewidth=0.8)
ax_loss.legend()

ax_score.plot(gan_trace["step"], gan_trace["D(real)"], color="#16a34a", linewidth=2.0, label="D(real)")
ax_score.plot(gan_trace["step"], gan_trace["D(fake)"], color="#dc2626", linewidth=2.0, label="D(fake)")
ax_score.set_title("判别器输出", loc="left", fontweight="bold")
ax_score.grid(True, color="#e2e8f0", linewidth=0.8)
ax_score.legend()

sample_tile = np.block([[gan_samples[i * 4 + j] for j in range(4)] for i in range(4)])
ax_img = fig.add_subplot(gs[1, :])
ax_img.imshow((sample_tile + 1) / 2, cmap="gray_r", vmin=0, vmax=1)
ax_img.set_title("生成样本", loc="left", fontweight="bold")
ax_img.set_xticks([])
ax_img.set_yticks([])
fig.suptitle("PyTorch GAN on Digits", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


DIFFUSION_TOY_CELL = """
# Digits 去噪自编码器：把带噪手写数字恢复成干净图像。
digits = load_digits()
X_clean = digits.data / 16.0
rng = np.random.default_rng(19)
noise_sigma = 0.42
X_noisy = np.clip(X_clean + rng.normal(0, noise_sigma, X_clean.shape), 0, 1)

X_train_noisy, X_test_noisy, X_train_clean, X_test_clean = train_test_split(
    X_noisy,
    X_clean,
    test_size=0.2,
    random_state=19,
)
denoiser = make_pipeline(
    StandardScaler(),
    MLPRegressor(hidden_layer_sizes=(96,), max_iter=160, random_state=19),
)
denoiser.fit(X_train_noisy, X_train_clean)
X_denoised = np.clip(denoiser.predict(X_test_noisy), 0, 1)

denoise_summary = pd.DataFrame(
    [
        {"图像": "noisy", "MSE": mean_squared_error(X_test_clean, X_test_noisy)},
        {"图像": "denoised", "MSE": mean_squared_error(X_test_clean, X_denoised)},
    ]
).round(4)
display(denoise_summary)
"""


DIFFUSION_TOY_PLOT_CELL = """
# 绘制干净图像、加噪输入和模型去噪输出。
preview_n = 10
clean_tile = np.block([[X_test_clean[i * 5 + j].reshape(8, 8) for j in range(5)] for i in range(2)])
noisy_tile = np.block([[X_test_noisy[i * 5 + j].reshape(8, 8) for j in range(5)] for i in range(2)])
denoised_tile = np.block([[X_denoised[i * 5 + j].reshape(8, 8) for j in range(5)] for i in range(2)])

fig, axes = plt.subplots(3, 1, figsize=(9.6, 5.8))
for ax, image, title in zip(axes, [clean_tile, noisy_tile, denoised_tile], ["clean", "noisy input", "denoised output"]):
    ax.imshow(image, cmap="gray_r", vmin=0, vmax=1)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
fig.suptitle("Digits denoising autoencoder", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


ALPHAFOLD_CELL = """
# AlphaFold 概念实验：用 insulin A-chain 风格 MSA 计算保守性和 pair 表征。
sequence = "GIVEQCCTSICSLYQLENYCN"
msa = [
    "GIVEQCCTSICSLYQLENYCN",
    "GIVEQCCASVCSLYQLENYCN",
    "GIVEQCCTSICSLYQLENFCN",
    "GLVEQCCTSICSLYQLENYCN",
    "GIVEQCCTSVCSLYQLENYCN",
]
msa_arr = np.array([list(row) for row in msa])
conservation = []
for col in msa_arr.T:
    counts = Counter(col)
    conservation.append(counts.most_common(1)[0][1] / len(col))
conservation = np.array(conservation)
pair_repr = np.outer(conservation, conservation)

pipeline_df = pd.DataFrame(
    [
        {"阶段": "MSA", "输出": f"{len(msa)} 条同源序列"},
        {"阶段": "保守性", "输出": "每个位置的最大频率"},
        {"阶段": "Pair 表征", "输出": f"{pair_repr.shape[0]}x{pair_repr.shape[1]} 矩阵"},
    ]
)
display(pipeline_df)
display(pd.DataFrame({"位置": range(1, len(sequence) + 1), "氨基酸": list(sequence), "保守性": conservation}).round(2))
"""


ALPHAFOLD_PLOT_CELL = """
# 绘制 pair 表征热力图。
fig, ax = plt.subplots(figsize=(6.0, 5.2))
im = ax.imshow(pair_repr, cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(len(sequence)), list(sequence))
ax.set_yticks(range(len(sequence)), list(sequence))
ax.set_title("Pair representation", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
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
                "第 8 章 · MLPClassifier 代码实验",
                ["训练 Digits 手写数字分类器", "查看混淆矩阵", "绘制 loss 和样本预测"],
                "../ch8.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(MLP_DATA_CELL),
            rs.section("1", "训练过程"),
            rs.code(MLP_TRAIN_CELL),
            rs.code(MLP_RESULT_CELL),
            rs.code(MLP_PLOT_CELL),
        ]),
        "ch08_transe_attention.ipynb": flatten([
            rs.chapter_link(
                "第 8 章 · TransE 与 Attention 代码实验",
                ["计算国家-首都 TransE 距离", "计算 Transformer attention 权重", "绘制几何图和热力图"],
                "../ch8.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.section("1", "TransE"),
            rs.code(TRANSE_CELL),
            rs.code(TRANSE_PLOT_CELL),
            rs.section("2", "Attention"),
            rs.code(ATTENTION_CELL),
            rs.code(ATTENTION_PLOT_CELL),
        ]),
    }


def _ch09() -> dict[str, list]:
    return {
        "ch09_bpe.ipynb": flatten([
            rs.chapter_link(
                "第 9 章 · BPE 代码实验",
                ["准备字符级词表", "执行 merge 步骤", "绘制 pair 频次"],
                "../ch9.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(BPE_DATA_CELL),
            rs.section("1", "Merge 过程"),
            rs.code(BPE_RUN_CELL),
            rs.code(BPE_PLOT_CELL),
        ]),
        "ch09_skipgram_toy.ipynb": flatten([
            rs.chapter_link(
                "第 9 章 · Skip-gram 代码实验",
                ["运行 Word2Vec 类比", "计算最近邻", "绘制词向量位置"],
                "../ch9.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(SKIPGRAM_DATA_CELL),
            rs.section("1", "词向量"),
            rs.code(SKIPGRAM_EMBED_CELL),
            rs.code(SKIPGRAM_PLOT_CELL),
        ]),
        "ch09_attention_lm.ipynb": flatten([
            rs.chapter_link(
                "第 9 章 · Causal Attention 与词 Bigram LM 代码实验",
                ["计算 causal attention", "统计词 bigram", "绘制 attention 热力图"],
                "../ch9.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(SELF_ATTENTION_CELL),
            rs.section("1", "词 Bigram LM"),
            rs.code(CHAR_LM_CELL),
            rs.code(SELF_ATTENTION_PLOT_CELL),
        ]),
    }


def _ch10() -> dict[str, list]:
    return {
        "ch10_conv2d_numpy.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · 卷积代码实验",
                ["加载 Digits 图像", "计算 Sobel 卷积", "绘制特征图"],
                "../ch10.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(CONV_DATA_CELL),
            rs.section("1", "卷积过程"),
            rs.code(CONV_PROCESS_CELL),
            rs.code(CONV_PLOT_CELL),
        ]),
        "ch10_vit_patchify.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · ViT Patchify 代码实验",
                ["加载真实照片", "切分 16×16 patch token", "绘制 patch 网格"],
                "../ch10.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(PATCHIFY_CELL),
            rs.code(PATCHIFY_PLOT_CELL),
        ]),
        "ch10_mae_masking.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · MAE Masking 代码实验",
                ["加载同一张真实照片", "随机 mask 75% patch", "绘制可见图和重建基线"],
                "../ch10.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(PATCHIFY_CELL),
            rs.section("1", "Mask"),
            rs.code(MAE_CELL),
            rs.code(MAE_PLOT_CELL),
        ]),
        "ch10_clip_infonce.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · CLIP / InfoNCE 代码实验",
                ["加载真实图片和文本 prompt", "运行官方 CLIPModel", "绘制图文匹配概率"],
                "../ch10.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(CLIP_CELL),
            rs.code(CLIP_PLOT_CELL),
        ]),
    }


def _ch11() -> dict[str, list]:
    return {
        "ch11_mdp_value_iteration.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · MDP 与价值迭代代码实验",
                ["读取 FrozenLake-v1 转移表", "执行价值迭代", "绘制价值与策略"],
                "../ch11.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(GYM_SETUP_CELL),
            rs.code(MDP_CELL),
            rs.section("1", "价值迭代"),
            rs.code(VALUE_ITERATION_CELL),
            rs.code(VALUE_PLOT_CELL),
        ]),
        "ch11_td_learning.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · Taxi-v3 Q-learning 代码实验",
                ["加载 Taxi-v3 环境", "记录 TD target 和 TD error", "绘制回报与 Q 表"],
                "../ch11.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(GYM_SETUP_CELL),
            rs.code(TD_CELL),
            rs.code(TD_PLOT_CELL),
        ]),
        "ch11_epsilon_greedy.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · CliffWalking SARSA 代码实验",
                ["加载 CliffWalking-v0 环境", "比较不同 epsilon", "绘制回报与策略"],
                "../ch11.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(GYM_SETUP_CELL),
            rs.code(BANDIT_CELL),
            rs.code(BANDIT_PLOT_CELL),
        ]),
    }


def _ch12() -> dict[str, list]:
    return {
        "ch12_repr_search_annealing.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · Iris SVC 退火搜索代码实验",
                ["加载 Iris 数据集", "用 dual_annealing 搜索超参数", "绘制搜索轨迹"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(ANNEALING_CELL),
            rs.code(ANNEALING_PLOT_CELL),
        ]),
        "ch12_mcts.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · FrozenLake MCTS / UCT 代码实验",
                ["加载 FrozenLake-v1", "运行 UCT 模拟", "绘制访问价值"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(GYM_SETUP_CELL),
            rs.code(MCTS_CELL),
            rs.code(MCTS_PLOT_CELL),
        ]),
        "ch12_diffusion_1d.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · Diffusers DDPM Scheduler 代码实验",
                ["加载真实图片", "调用 DDPMScheduler 前向加噪", "绘制噪声调度"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(DIFFUSION_1D_CELL),
            rs.code(DIFFUSION_1D_PLOT_CELL),
        ]),
        "ch12_diffusion_digits.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · Digits Diffusion 代码实验",
                ["加载 sklearn digits", "绘制前向加噪", "展示原型去噪"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(DIGITS_DATA_CELL),
            rs.section("1", "加噪与去噪"),
            rs.code(DIGITS_FORWARD_CELL),
            rs.code(DIGITS_REVERSE_CELL),
            rs.code(DIGITS_PLOT_CELL),
        ]),
        "ch12_gan_toy.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · Digits GAN 代码实验",
                ["加载 sklearn Digits", "训练 PyTorch GAN", "绘制生成样本"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(GAN_CELL),
            rs.code(GAN_PLOT_CELL),
        ]),
        "ch12_diffusion_toy.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · Digits 去噪自编码器代码实验",
                ["加载 Digits 数据", "训练 MLPRegressor 去噪器", "比较 noisy 与 denoised"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(DIFFUSION_TOY_CELL),
            rs.code(DIFFUSION_TOY_PLOT_CELL),
        ]),
        "ch12_alphafold_concepts.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · AlphaFold 概念代码实验",
                ["读取 MSA", "计算位置保守性", "绘制 pair 表征"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(ALPHAFOLD_CELL),
            rs.code(ALPHAFOLD_PLOT_CELL),
        ]),
    }
