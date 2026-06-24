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
from IPython.display import display
from scipy.optimize import dual_annealing
from scipy.signal import correlate2d
from sklearn.datasets import load_digits, make_moons
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import accuracy_score, confusion_matrix, log_loss, mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, normalize

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
# 准备 BPE 语料，把每个词拆成字符序列。
corpus = ["low", "lower", "newest", "widest"]
vocab = Counter(tuple(word) + ("</w>",) for word in corpus)

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


display(pd.DataFrame({"token序列": [" ".join(k) for k in vocab.keys()], "频次": list(vocab.values())}))
"""


BPE_RUN_CELL = """
# 连续执行若干次 merge，记录每轮最高频 pair。
bpe_rows = []
history = []
current_vocab = vocab.copy()

for step in range(1, 7):
    counts = pair_counts(current_vocab)
    best_pair, best_count = counts.most_common(1)[0]
    current_vocab = merge_pair(current_vocab, best_pair)
    state = [" ".join(symbols) for symbols in current_vocab.keys()]
    bpe_rows.append({
        "轮次": step,
        "合并pair": " + ".join(best_pair),
        "频次": best_count,
        "当前token序列": " | ".join(state),
    })
    history.append((best_pair, counts))

bpe_trace = pd.DataFrame(bpe_rows)
display(bpe_trace)
"""


BPE_PLOT_CELL = """
# 绘制第一轮 pair 频次。
first_counts = history[0][1]
top_pairs = first_counts.most_common(6)
labels = ["+".join(pair) for pair, _ in top_pairs]
values = [count for _, count in top_pairs]

fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.bar(labels, values, color="#2563eb")
ax.set_title("BPE 第一轮 pair 频次", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_ylabel("频次")
ax.grid(True, axis="y", color="#e2e8f0", linewidth=0.8)
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
# 把一张 8x8 手写数字图像切成 2x2 patch token。
digits = load_digits()
vit_image = digits.images[8] / 16.0
patch_size = 2
patches = vit_image.reshape(4, patch_size, 4, patch_size).swapaxes(1, 2)
patch_tokens = patches.reshape(-1, patch_size * patch_size)

patch_df = pd.DataFrame(patch_tokens, columns=["p00", "p01", "p10", "p11"])
patch_df.insert(0, "patch_id", range(len(patch_df)))
display(patch_df.head(8).round(2))
"""


PATCHIFY_PLOT_CELL = """
# 绘制原图和前几个 patch。
fig, axes = plt.subplots(1, 5, figsize=(10.5, 2.8))
axes[0].imshow(vit_image, cmap="Blues")
axes[0].set_title("原图", fontweight="bold")
axes[0].set_xticks([])
axes[0].set_yticks([])
for idx in range(4):
    axes[idx + 1].imshow(patch_tokens[idx].reshape(2, 2), cmap="Blues")
    axes[idx + 1].set_title(f"patch {idx}", fontweight="bold")
    axes[idx + 1].set_xticks([])
    axes[idx + 1].set_yticks([])
fig.suptitle("ViT Patchify", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


MAE_CELL = """
# MAE masking：随机遮住一部分 patch，只保留可见 token。
rng = np.random.default_rng(4)
num_patches = len(patch_tokens)
mask_ratio = 0.5
visible_ids = np.sort(rng.choice(num_patches, size=int(num_patches * (1 - mask_ratio)), replace=False))
masked_ids = np.array([idx for idx in range(num_patches) if idx not in set(visible_ids)])

mae_df = pd.DataFrame({
    "patch_id": range(num_patches),
    "状态": ["可见" if idx in set(visible_ids) else "mask" for idx in range(num_patches)],
})
display(mae_df)
"""


MAE_PLOT_CELL = """
# 绘制 mask 图像和均值重建图像。
masked_image = vit_image.astype(float).copy()
recon_image = vit_image.astype(float).copy()
visible_mean = patch_tokens[visible_ids].mean()

for patch_id in masked_ids:
    row = patch_id // 4
    col = patch_id % 4
    masked_image[row * 2:(row + 1) * 2, col * 2:(col + 1) * 2] = np.nan
    recon_image[row * 2:(row + 1) * 2, col * 2:(col + 1) * 2] = visible_mean

fig, axes = plt.subplots(1, 3, figsize=(9.5, 3.4))
for ax, data, title in zip(axes, [vit_image, masked_image, recon_image], ["原图", "可见 patch", "均值重建"]):
    ax.imshow(data, cmap="Blues")
    ax.set_title(title, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
fig.suptitle("MAE masking", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


CLIP_CELL = """
# CLIP / InfoNCE：用 digits 原型图像和文本标签构造图文匹配矩阵。
digits = load_digits()
label_ids = [0, 1, 2, 3, 4]
image_names = [f"digit {i}" for i in label_ids]
text_names = [f"text: number {i}" for i in label_ids]

image_proto = []
for label in label_ids:
    image_proto.append(digits.data[digits.target == label].mean(axis=0))
image_emb = normalize(np.array(image_proto))

text_emb = np.zeros((len(label_ids), image_emb.shape[1]))
for row, label in enumerate(label_ids):
    text_emb[row, label * 6:label * 6 + 6] = 1.0
    text_emb[row] += 0.08 * image_emb[row]
text_emb = normalize(text_emb)

temperature = 0.08
logits = image_emb @ text_emb.T / temperature
probs = np.exp(logits - logits.max(axis=1, keepdims=True))
probs = probs / probs.sum(axis=1, keepdims=True)
clip_loss = log_loss(np.arange(len(label_ids)), probs, labels=np.arange(len(label_ids)))

display(pd.DataFrame(np.round(image_emb @ text_emb.T, 3), index=image_names, columns=text_names))
print("InfoNCE loss:", round(float(clip_loss), 4))
"""


CLIP_PLOT_CELL = """
# 绘制图文相似度矩阵。
sim_matrix = image_emb @ text_emb.T
fig, ax = plt.subplots(figsize=(6.6, 5.2))
im = ax.imshow(sim_matrix, cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(len(text_names)), text_names, rotation=20, ha="right")
ax.set_yticks(range(len(image_names)), image_names)
for i in range(len(image_names)):
    for j in range(len(text_names)):
        ax.text(j, i, f"{sim_matrix[i, j]:.2f}", ha="center", va="center", color="#0f172a")
ax.set_title("CLIP 图文相似度", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
plt.tight_layout()
plt.show()
"""


MDP_CELL = """
# Gridworld：4x4 网格，左上和右下为终止状态，每走一步奖励 -1。
grid_size = 4
terminal_states = {"s00", "s33"}
states = [f"s{r}{c}" for r in range(grid_size) for c in range(grid_size)]
move_delta = {"上": (-1, 0), "下": (1, 0), "左": (0, -1), "右": (0, 1)}

actions = {}
transitions = {}
for r in range(grid_size):
    for c in range(grid_size):
        state = f"s{r}{c}"
        if state in terminal_states:
            actions[state] = []
            continue
        actions[state] = list(move_delta)
        for action, (dr, dc) in move_delta.items():
            nr = min(grid_size - 1, max(0, r + dr))
            nc = min(grid_size - 1, max(0, c + dc))
            next_state = f"s{nr}{nc}"
            transitions[(state, action)] = [(next_state, 1.0, -1.0)]

display(pd.DataFrame(
    [
        {"状态": s, "动作": a, "转移": transitions[(s, a)]}
        for s, acts in actions.items()
        for a in acts
    ]
).head(12))
"""


VALUE_ITERATION_CELL = """
# 价值迭代：反复应用 Bellman 最优方程。
def value_iteration(states, actions, transitions, gamma=0.9, iterations=12):
    V = {state: 0.0 for state in states}
    rows = []
    policy_rows = []

    for it in range(1, iterations + 1):
        new_V = V.copy()
        for state in states:
            if not actions[state]:
                continue
            q_values = {}
            for action in actions[state]:
                q_values[action] = sum(
                    prob * (reward + gamma * V[next_state])
                    for next_state, prob, reward in transitions[(state, action)]
                )
            best_action = max(q_values, key=q_values.get)
            new_V[state] = q_values[best_action]
            if it == iterations:
                policy_rows.append({"状态": state, "最优动作": best_action, "Q值": round(q_values[best_action], 3)})
        V = new_V
        row = {"轮次": it}
        row.update({state: round(value, 3) for state, value in V.items()})
        rows.append(row)

    return pd.DataFrame(rows), pd.DataFrame(policy_rows)


value_trace, policy_df = value_iteration(states, actions, transitions)
display(value_trace.tail(6))
display(policy_df)
"""


VALUE_PLOT_CELL = """
# 绘制 Gridworld 最终价值和最优动作。
final_values = value_trace.iloc[-1][states].to_dict()
value_grid = np.array([[final_values[f"s{r}{c}"] for c in range(grid_size)] for r in range(grid_size)])
policy_map = dict(zip(policy_df["状态"], policy_df["最优动作"]))
arrow = {"上": "↑", "下": "↓", "左": "←", "右": "→"}

fig, ax = plt.subplots(figsize=(6.2, 5.6))
im = ax.imshow(value_grid, cmap="Blues")
for r in range(grid_size):
    for c in range(grid_size):
        state = f"s{r}{c}"
        label = "T" if state in terminal_states else arrow[policy_map[state]]
        ax.text(c, r, f"{value_grid[r, c]:.1f}\\n{label}", ha="center", va="center", color="#0f172a", fontweight="bold")
ax.set_title("Gridworld 价值迭代", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xticks(range(grid_size))
ax.set_yticks(range(grid_size))
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
plt.tight_layout()
plt.show()
"""


TD_CELL = """
# Sutton random walk：A-B-C-D-E 五个非终止状态，右端奖励为 1。
rw_states = ["A", "B", "C", "D", "E"]
V_td = defaultdict(lambda: 0.5)
V_td["L"] = 0.0
V_td["R"] = 0.0
alpha = 0.4
gamma = 1.0
episodes = [
    ["C", "D", "E", "R"],
    ["C", "B", "A", "L"],
    ["C", "D", "C", "D", "E", "R"],
]
td_rows = []

step = 0
for episode_id, episode in enumerate(episodes, start=1):
    for state, next_state in zip(episode, episode[1:]):
        if state in {"L", "R"}:
            continue
        step += 1
        reward = 1.0 if next_state == "R" else 0.0
        target = reward + gamma * V_td[next_state]
        old = V_td[state]
        V_td[state] = old + alpha * (target - old)
        td_rows.append({
            "episode": episode_id,
            "步": step,
            "状态": state,
            "下一状态": next_state,
            "TD target": round(target, 3),
            "更新后V": round(V_td[state], 3),
        })

td_trace = pd.DataFrame(td_rows)
display(td_trace)
"""


TD_PLOT_CELL = """
# 绘制 TD 更新后的状态价值。
fig, ax = plt.subplots(figsize=(6.8, 4.6))
td_values = pd.Series({state: V_td[state] for state in rw_states})
td_values.plot(kind="bar", ax=ax, color="#2563eb")
ax.set_title("Random walk TD(0) 状态价值", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_ylabel("V(s)")
ax.grid(True, axis="y", color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
"""


BANDIT_CELL = """
# epsilon-greedy：在探索和利用之间切换。
def run_bandit(epsilon, steps=500, seed=0):
    rng = np.random.default_rng(seed)
    true_means = rng.normal(0.0, 1.0, size=10)
    estimates = np.zeros(10)
    counts = np.zeros(10)
    rows = []
    total_reward = 0.0
    optimal_action = int(np.argmax(true_means))
    optimal_hits = 0

    for step in range(1, steps + 1):
        explore = rng.random() < epsilon
        action = rng.integers(10) if explore else int(np.argmax(estimates))
        reward = rng.normal(true_means[action], 1.0)
        counts[action] += 1
        estimates[action] += (reward - estimates[action]) / counts[action]
        total_reward += reward
        optimal_hits += int(action == optimal_action)
        if step % 50 == 0:
            rows.append({
                "epsilon": epsilon,
                "步数": step,
                "平均奖励": round(total_reward / step, 3),
                "最优动作比例": round(optimal_hits / step, 3),
            })
    return pd.DataFrame(rows)


bandit_trace = pd.concat([run_bandit(0.0, seed=1), run_bandit(0.1, seed=1), run_bandit(0.3, seed=1)], ignore_index=True)
display(bandit_trace)
"""


BANDIT_PLOT_CELL = """
# 绘制不同 epsilon 的平均奖励。
fig, ax = plt.subplots(figsize=(7.6, 4.8))
for epsilon, part in bandit_trace.groupby("epsilon"):
    ax.plot(part["步数"], part["平均奖励"], marker="o", linewidth=2.2, label=f"epsilon={epsilon}")
ax.set_title("10-armed bandit 平均奖励", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xlabel("步数")
ax.set_ylabel("平均奖励")
ax.grid(True, color="#e2e8f0", linewidth=0.8)
ax.legend()
plt.tight_layout()
plt.show()
"""


ANNEALING_CELL = """
# TSP 旅行商问题：用模拟退火交换城市顺序，寻找较短回路。
cities = pd.DataFrame(
    {
        "城市": ["A", "B", "C", "D", "E", "F", "G", "H"],
        "x": [0.1, 0.4, 0.9, 1.4, 1.6, 1.0, 0.5, 0.2],
        "y": [0.2, 0.8, 0.7, 0.3, 1.1, 1.5, 1.4, 1.0],
    }
)
coords = cities[["x", "y"]].to_numpy()

def route_length(route):
    ordered = coords[route]
    closed = np.vstack([ordered, ordered[0]])
    return float(np.linalg.norm(np.diff(closed, axis=0), axis=1).sum())

rng = np.random.default_rng(12)
route = np.arange(len(cities))
rng.shuffle(route)
best_route = route.copy()
best_loss = route_length(route)
current_loss = best_loss
anneal_rows = []

for step in range(1, 401):
    temperature = 1.2 * (0.992 ** step)
    candidate = route.copy()
    i, j = rng.choice(len(route), size=2, replace=False)
    candidate[i], candidate[j] = candidate[j], candidate[i]
    candidate_loss = route_length(candidate)
    accept = candidate_loss < current_loss or rng.random() < np.exp((current_loss - candidate_loss) / max(temperature, 1e-6))
    if accept:
        route = candidate
        current_loss = candidate_loss
    if current_loss < best_loss:
        best_route = route.copy()
        best_loss = current_loss
    if step % 40 == 0:
        anneal_rows.append({"步": step, "温度": temperature, "当前距离": current_loss, "最佳距离": best_loss})

anneal_df = pd.DataFrame(anneal_rows).round(4)
display(cities)
display(anneal_df)
print("best route:", " -> ".join(cities.iloc[best_route]["城市"].tolist()))
"""


ANNEALING_PLOT_CELL = """
# 绘制 TSP 路线和距离下降。
fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.5))
best_coords = coords[best_route]
closed = np.vstack([best_coords, best_coords[0]])
axes[0].plot(closed[:, 0], closed[:, 1], "-o", color="#2563eb", linewidth=2.2)
for idx, row in cities.iterrows():
    axes[0].text(row["x"] + 0.03, row["y"] + 0.03, row["城市"], color="#0f172a", fontweight="bold")
axes[0].set_title("TSP 最佳路线", loc="left", fontweight="bold")
axes[0].set_aspect("equal", adjustable="box")
axes[0].grid(True, color="#e2e8f0", linewidth=0.8)

axes[1].plot(anneal_df["步"], anneal_df["当前距离"], color="#94a3b8", linewidth=1.8, label="当前距离")
axes[1].plot(anneal_df["步"], anneal_df["最佳距离"], color="#2563eb", linewidth=2.4, label="最佳距离")
axes[1].set_title("退火搜索过程", loc="left", fontweight="bold")
axes[1].set_xlabel("步")
axes[1].set_ylabel("路线长度")
axes[1].grid(True, color="#e2e8f0", linewidth=0.8)
axes[1].legend()
plt.tight_layout()
plt.show()
"""


MCTS_CELL = """
# Tic-tac-toe 井字棋局面：用 UCT 在候选落子中平衡价值和探索。
board = np.array([
    ["X", "O", "X"],
    [" ", "O", " "],
    [" ", "X", " "],
])
candidate_moves = [(1, 0), (1, 2), (2, 0), (2, 2)]
parent_visits = 128
moves = pd.DataFrame(
    {
        "走法": [f"({r},{c})" for r, c in candidate_moves],
        "访问次数": [42, 30, 34, 22],
        "累计价值": [24.8, 16.2, 24.0, 11.5],
    }
)
explore_c = 1.4
moves["平均价值"] = moves["累计价值"] / moves["访问次数"]
moves["探索项"] = explore_c * np.sqrt(np.log(parent_visits) / moves["访问次数"])
moves["UCT"] = moves["平均价值"] + moves["探索项"]
moves = moves.sort_values("UCT", ascending=False).reset_index(drop=True)
display(pd.DataFrame(board))
display(moves.round(3))
print("选择走法:", moves.loc[0, "走法"])
"""


MCTS_PLOT_CELL = """
# 绘制 UCT 组成。
fig, ax = plt.subplots(figsize=(7.4, 4.8))
x = np.arange(len(moves))
ax.bar(x, moves["平均价值"], label="平均价值", color="#2563eb")
ax.bar(x, moves["探索项"], bottom=moves["平均价值"], label="探索项", color="#f97316")
ax.set_xticks(x, moves["走法"])
ax.set_title("Tic-tac-toe UCT 分数", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_ylabel("分数")
ax.grid(True, axis="y", color="#e2e8f0", linewidth=0.8)
ax.legend()
plt.tight_layout()
plt.show()
"""


DIFFUSION_1D_CELL = """
# 1D diffusion：从双峰分布出发，按噪声调度逐步混入高斯噪声。
rng = np.random.default_rng(7)
left = rng.normal(-2.0, 0.28, size=300)
right = rng.normal(2.0, 0.28, size=300)
x0_samples = np.concatenate([left, right])
eps_samples = rng.normal(size=x0_samples.shape)
betas = np.linspace(0.03, 0.20, 8)
alphas = 1 - betas
alpha_bars = np.cumprod(alphas)

diff_rows = []
xs = []
for t, alpha_bar in enumerate(alpha_bars, start=1):
    xt = np.sqrt(alpha_bar) * x0_samples + np.sqrt(1 - alpha_bar) * eps_samples
    xs.append(xt)
    diff_rows.append({
        "t": t,
        "alpha_bar": round(alpha_bar, 3),
        "均值": round(float(xt.mean()), 3),
        "标准差": round(float(xt.std()), 3),
        "5%分位": round(float(np.quantile(xt, 0.05)), 3),
        "95%分位": round(float(np.quantile(xt, 0.95)), 3),
    })

diff_1d_df = pd.DataFrame(diff_rows)
display(diff_1d_df)
"""


DIFFUSION_1D_PLOT_CELL = """
# 绘制不同 t 下的一维分布。
snapshots = [x0_samples, xs[1], xs[4], xs[-1]]
titles = ["t=0", "t=2", "t=5", "t=8"]
fig, axes = plt.subplots(1, 4, figsize=(10.5, 3.2), sharex=True, sharey=True)
for ax, values, title in zip(axes, snapshots, titles):
    ax.hist(values, bins=32, color="#2563eb", alpha=0.78)
    ax.set_title(title, fontweight="bold")
    ax.grid(True, axis="y", color="#e2e8f0", linewidth=0.8)
fig.suptitle("双峰分布的前向扩散", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
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
# GAN 判别器示意：two moons 真实分布与生成分布逐步靠近。
rng = np.random.default_rng(5)
real, _ = make_moons(n_samples=240, noise=0.08, random_state=5)
fake_shift = np.array([1.4, -0.8])
gan_rows = []

for step in range(1, 9):
    fake = make_moons(n_samples=240, noise=0.16, random_state=step)[0] + fake_shift
    X_disc = np.vstack([real, fake])
    y_disc = np.array([1] * len(real) + [0] * len(fake))
    disc = MLPClassifier(hidden_layer_sizes=(16,), max_iter=500, random_state=step)
    disc.fit(X_disc, y_disc)
    fake_score = disc.predict_proba(fake)[:, 1].mean()
    real_score = disc.predict_proba(real)[:, 1].mean()
    fake_shift *= 0.72
    gan_rows.append({
        "轮次": step,
        "生成分布偏移": round(float(np.linalg.norm(fake_shift)), 3),
        "D(real)": round(float(real_score), 3),
        "D(fake)": round(float(fake_score), 3),
    })

gan_trace = pd.DataFrame(gan_rows)
display(gan_trace)
"""


GAN_PLOT_CELL = """
# 绘制 D(fake) 变化和最终 two moons 分布。
fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.4))
axes[0].plot(gan_trace["轮次"], gan_trace["D(fake)"], marker="o", linewidth=2.2, color="#2563eb")
axes[0].set_title("判别器对生成样本的评分", loc="left", fontweight="bold")
axes[0].set_xlabel("轮次")
axes[0].set_ylabel("D(fake)")
axes[0].grid(True, color="#e2e8f0", linewidth=0.8)

axes[1].scatter(real[:, 0], real[:, 1], s=24, alpha=0.75, label="real", color="#2563eb")
axes[1].scatter(fake[:, 0], fake[:, 1], s=24, alpha=0.75, label="fake", color="#f97316")
axes[1].set_title("最后一轮分布", loc="left", fontweight="bold")
axes[1].legend()
axes[1].set_aspect("equal", adjustable="box")
plt.tight_layout()
plt.show()
"""


DIFFUSION_TOY_CELL = """
# 用 two moons 经典二维数据演示加噪和去噪方向。
rng = np.random.default_rng(9)
clean_points, moon_label = make_moons(n_samples=180, noise=0.06, random_state=9)
noise_points = rng.normal(size=clean_points.shape)
noise_level = 0.65
noisy_points = np.sqrt(1 - noise_level) * clean_points + np.sqrt(noise_level) * noise_points
denoised_points = 0.55 * noisy_points + 0.45 * clean_points

diffusion_summary = pd.DataFrame(
    [
        {"阶段": "noisy", "到clean中心的平均距离": np.linalg.norm(noisy_points - clean_points.mean(axis=0), axis=1).mean()},
        {"阶段": "denoised", "到clean中心的平均距离": np.linalg.norm(denoised_points - clean_points.mean(axis=0), axis=1).mean()},
    ]
).round(3)
display(diffusion_summary)
"""


DIFFUSION_TOY_PLOT_CELL = """
# 绘制二维点的加噪和去噪。
fig, axes = plt.subplots(1, 3, figsize=(10.0, 3.8), sharex=True, sharey=True)
for ax, pts, title, color in zip(
    axes,
    [clean_points, noisy_points, denoised_points],
    ["clean", "noisy", "denoised"],
    ["#2563eb", "#f97316", "#16a34a"],
):
    ax.scatter(pts[:, 0], pts[:, 1], s=35, alpha=0.8, color=color, edgecolors="white", linewidth=0.4)
    ax.set_title(title, fontweight="bold")
    ax.grid(True, color="#e2e8f0", linewidth=0.8)
fig.suptitle("二维 diffusion 概念实验", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


ALPHAFOLD_CELL = """
# AlphaFold 概念实验：从 MSA 计算保守性，再形成 pair 表征矩阵。
sequence = "MKTFFVLLL"
msa = [
    "MKTFFVLLL",
    "MKTFFVILM",
    "MKSFFVLLL",
    "MRTYFVLLL",
    "MKTFFALLL",
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
                "第 9 章 · Self-Attention 与字符 LM 代码实验",
                ["计算 causal attention", "统计字符 bigram", "绘制 attention 热力图"],
                "../ch9.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(SELF_ATTENTION_CELL),
            rs.section("1", "字符语言模型"),
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
                ["切分 Digits patch token", "查看 token 表", "绘制 patch"],
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
                ["切分 Digits patch", "随机 mask", "绘制重建图"],
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
                ["匹配 Digits 图像与文本标签", "计算 InfoNCE loss", "绘制相似度矩阵"],
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
                ["准备 Gridworld 转移表", "执行价值迭代", "绘制价值与策略"],
                "../ch11.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(MDP_CELL),
            rs.section("1", "价值迭代"),
            rs.code(VALUE_ITERATION_CELL),
            rs.code(VALUE_PLOT_CELL),
        ]),
        "ch11_td_learning.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · TD(0) 代码实验",
                ["运行 Sutton random walk", "输出 TD target", "绘制状态价值"],
                "../ch11.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(TD_CELL),
            rs.code(TD_PLOT_CELL),
        ]),
        "ch11_epsilon_greedy.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · epsilon-greedy 代码实验",
                ["模拟 10-armed bandit", "比较不同 epsilon", "绘制平均奖励"],
                "../ch11.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(BANDIT_CELL),
            rs.code(BANDIT_PLOT_CELL),
        ]),
    }


def _ch12() -> dict[str, list]:
    return {
        "ch12_repr_search_annealing.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 表征搜索与退火代码实验",
                ["运行 TSP 模拟退火", "记录路线长度", "绘制搜索轨迹"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(ANNEALING_CELL),
            rs.code(ANNEALING_PLOT_CELL),
        ]),
        "ch12_mcts.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · MCTS / UCT 代码实验",
                ["准备 Tic-tac-toe 局面", "计算探索项", "绘制 UCT 分数"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(MCTS_CELL),
            rs.code(MCTS_PLOT_CELL),
        ]),
        "ch12_diffusion_1d.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 1D Diffusion 代码实验",
                ["执行前向加噪", "查看噪声调度", "绘制反向轨迹"],
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
                "第 12 章 · GAN 代码实验",
                ["训练 two moons 判别器", "移动生成分布", "绘制判别器评分"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(GAN_CELL),
            rs.code(GAN_PLOT_CELL),
        ]),
        "ch12_diffusion_toy.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 二维 Diffusion 代码实验",
                ["生成 two moons 数据", "加入高斯噪声", "绘制去噪方向"],
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
