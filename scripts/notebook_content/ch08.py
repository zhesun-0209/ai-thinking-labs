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
from sklearn.datasets import load_digits
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import log_loss, mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
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
# 准备二分类样本：两个输入特征对应一个标签。
X_mlp = np.array([
    [0.12, 0.10],
    [0.20, 0.26],
    [0.28, 0.18],
    [0.36, 0.33],
    [0.64, 0.60],
    [0.72, 0.70],
    [0.82, 0.76],
    [0.92, 0.88],
])
y_mlp = np.array([0, 0, 0, 0, 1, 1, 1, 1])

mlp_df = pd.DataFrame(X_mlp, columns=["特征1", "特征2"])
mlp_df["标签"] = y_mlp
display(mlp_df)
"""


MLP_TRAIN_CELL = """
# 训练 sklearn MLPClassifier，并记录每轮 loss。
mlp = make_pipeline(
    StandardScaler(),
    MLPClassifier(
        hidden_layer_sizes=(3,),
        activation="relu",
        solver="sgd",
        learning_rate_init=0.08,
        max_iter=1,
        warm_start=True,
        random_state=2,
    ),
)

loss_rows = []
for epoch in range(1, 41):
    mlp.fit(X_mlp, y_mlp)
    classifier = mlp.named_steps["mlpclassifier"]
    prob = mlp.predict_proba(X_mlp)[:, 1]
    loss_rows.append({
        "轮次": epoch,
        "loss": round(classifier.loss_, 4),
        "平均正类概率": round(float(prob.mean()), 4),
    })

mlp_trace = pd.DataFrame(loss_rows)
display(mlp_trace.tail(8))
"""


MLP_RESULT_CELL = """
# 查看每个样本的预测概率。
mlp_prob = mlp.predict_proba(X_mlp)[:, 1]
mlp_result = mlp_df.copy()
mlp_result["预测为1的概率"] = np.round(mlp_prob, 3)
mlp_result["预测标签"] = (mlp_prob >= 0.5).astype(int)
display(mlp_result)
"""


MLP_PLOT_CELL = """
# 绘制 loss 曲线和这个小网络的层级结构。
fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.6))

axes[0].plot(mlp_trace["轮次"], mlp_trace["loss"], color="#2563eb", linewidth=2.4)
axes[0].set_title("MLP 训练 loss", loc="left", fontweight="bold")
axes[0].set_xlabel("轮次")
axes[0].set_ylabel("loss")
axes[0].grid(True, color="#e2e8f0", linewidth=0.8)

layer_x = [0, 1.4, 2.8]
layer_y = [[0.8, 1.8], [0.45, 1.3, 2.15], [1.3]]
for i, ys in enumerate(layer_y):
    for y in ys:
        axes[1].scatter(layer_x[i], y, s=700, color="#eff6ff", edgecolor="#2563eb", linewidth=1.7, zorder=3)
for y1 in layer_y[0]:
    for y2 in layer_y[1]:
        axes[1].plot([layer_x[0], layer_x[1]], [y1, y2], color="#cbd5e1", linewidth=1.3, zorder=1)
for y1 in layer_y[1]:
    axes[1].plot([layer_x[1], layer_x[2]], [y1, layer_y[2][0]], color="#cbd5e1", linewidth=1.3, zorder=1)
axes[1].text(0, 2.55, "输入", ha="center", fontweight="bold")
axes[1].text(1.4, 2.55, "隐藏层", ha="center", fontweight="bold")
axes[1].text(2.8, 2.55, "输出", ha="center", fontweight="bold")
axes[1].set_title("网络结构", loc="left", fontweight="bold")
axes[1].set_xlim(-0.45, 3.25)
axes[1].set_ylim(0.0, 2.85)
axes[1].axis("off")

plt.tight_layout()
plt.show()
"""


TRANSE_CELL = """
# TransE：比较正确三元组和替换实体后的距离。
entity_vec = {
    "鲁迅": np.array([0.10, 0.82]),
    "《呐喊》": np.array([0.72, 0.60]),
    "《边城》": np.array([0.20, 0.15]),
    "沈从文": np.array([0.08, 0.20]),
}
relation_vec = {"创作": np.array([0.60, -0.18])}

triples = [
    ("鲁迅", "创作", "《呐喊》", "正例"),
    ("鲁迅", "创作", "《边城》", "替换尾实体"),
    ("沈从文", "创作", "《呐喊》", "替换头实体"),
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
h = entity_vec["鲁迅"]
r = relation_vec["创作"]
target_point = h + r

for name, vec in entity_vec.items():
    ax.scatter(vec[0], vec[1], s=170, color="#ffffff", edgecolor="#2563eb", linewidth=1.7)
    ax.text(vec[0] + 0.02, vec[1] + 0.02, name, color="#0f172a")

ax.arrow(h[0], h[1], r[0], r[1], width=0.006, head_width=0.035, color="#f97316", length_includes_head=True)
ax.scatter(target_point[0], target_point[1], s=210, marker="X", color="#f97316", edgecolor="#0f172a", linewidth=1.0)
ax.text(target_point[0] + 0.02, target_point[1] - 0.05, "鲁迅 + 创作", color="#c2410c")
ax.set_title("TransE 距离示意", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xlabel("维度1")
ax.set_ylabel("维度2")
ax.grid(True, color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
"""


ATTENTION_CELL = """
# Scaled dot-product attention：计算分数、权重和加权输出。
tokens = ["我", "喜欢", "学习", "AI"]
X_attn = np.array([
    [0.8, 0.1, 0.0],
    [0.7, 0.2, 0.2],
    [0.1, 0.8, 0.3],
    [0.2, 0.4, 0.9],
])
Wq = np.array([[0.7, 0.1], [0.2, 0.8], [0.1, 0.3]])
Wk = np.array([[0.6, 0.2], [0.3, 0.7], [0.2, 0.4]])
Wv = np.array([[0.5, 0.1], [0.2, 0.7], [0.3, 0.5]])

Q = X_attn @ Wq
K = X_attn @ Wk
V = X_attn @ Wv
scores = Q @ K.T / math.sqrt(K.shape[1])
weights = np.exp(scores - scores.max(axis=1, keepdims=True))
weights = weights / weights.sum(axis=1, keepdims=True)
attn_output = weights @ V

display(pd.DataFrame(np.round(weights, 3), index=tokens, columns=tokens))
display(pd.DataFrame(np.round(attn_output, 3), index=tokens, columns=["输出1", "输出2"]))
"""


ATTENTION_PLOT_CELL = """
# 绘制 attention 权重热力图。
fig, ax = plt.subplots(figsize=(6.2, 5.0))
im = ax.imshow(weights, cmap="Blues", vmin=0, vmax=weights.max())
ax.set_xticks(range(len(tokens)), tokens)
ax.set_yticks(range(len(tokens)), tokens)
for i in range(len(tokens)):
    for j in range(len(tokens)):
        ax.text(j, i, f"{weights[i, j]:.2f}", ha="center", va="center", color="#0f172a")
ax.set_title("Attention 权重", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
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
# 准备窗口为 1 的 Skip-gram 样本。
sentence = "鲁迅 写 小说 鲁迅 关注 人 也 关注 社会 小说 影响 读者".split()
window = 1
pairs = []
for i, center in enumerate(sentence):
    for j in range(max(0, i - window), min(len(sentence), i + window + 1)):
        if i != j:
            pairs.append((center, sentence[j]))

pair_df = pd.DataFrame(pairs, columns=["中心词", "上下文词"])
display(pair_df.head(12))
"""


SKIPGRAM_EMBED_CELL = """
# 用共现矩阵和 TruncatedSVD 得到二维词向量。
vocab_words = sorted(set(sentence))
word_to_id = {word: i for i, word in enumerate(vocab_words)}
cooc = np.zeros((len(vocab_words), len(vocab_words)))
for center, context in pairs:
    cooc[word_to_id[center], word_to_id[context]] += 1

svd = TruncatedSVD(n_components=2, random_state=0)
emb = svd.fit_transform(cooc)
emb = normalize(emb)
sim = cosine_similarity(emb)

emb_df = pd.DataFrame(emb, index=vocab_words, columns=["dim1", "dim2"])
nearest = pd.DataFrame(
    [
        {"词": word, "最近邻": vocab_words[np.argsort(sim[i])[-2]], "相似度": round(np.sort(sim[i])[-2], 3)}
        for word, i in word_to_id.items()
    ]
)
display(nearest)
"""


SKIPGRAM_PLOT_CELL = """
# 绘制词向量位置。
fig, ax = plt.subplots(figsize=(7.4, 5.2))
ax.scatter(emb[:, 0], emb[:, 1], s=130, color="#eff6ff", edgecolor="#2563eb", linewidth=1.6)
for word, i in word_to_id.items():
    ax.text(emb[i, 0] + 0.02, emb[i, 1] + 0.02, word, color="#0f172a")
ax.axhline(0, color="#e2e8f0", linewidth=1)
ax.axvline(0, color="#e2e8f0", linewidth=1)
ax.set_title("Skip-gram 共现向量", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xlabel("dim1")
ax.set_ylabel("dim2")
plt.tight_layout()
plt.show()
"""


SELF_ATTENTION_CELL = """
# 加入 causal mask 后，每个位置只能看见自己和左侧 token。
lm_tokens = list("学习AI")
X_lm = np.array([
    [0.8, 0.1, 0.0],
    [0.2, 0.8, 0.1],
    [0.1, 0.3, 0.9],
    [0.2, 0.4, 0.8],
])
scores_lm = X_lm @ X_lm.T / math.sqrt(X_lm.shape[1])
mask = np.triu(np.ones_like(scores_lm), k=1).astype(bool)
scores_lm = np.where(mask, -1e9, scores_lm)
weights_lm = np.exp(scores_lm - scores_lm.max(axis=1, keepdims=True))
weights_lm = weights_lm / weights_lm.sum(axis=1, keepdims=True)

display(pd.DataFrame(np.round(weights_lm, 3), index=lm_tokens, columns=lm_tokens))
"""


CHAR_LM_CELL = """
# 字符 bigram：根据当前字符统计下一个字符分布。
text = "学习AI学习语言模型学习AI应用"
bigram = defaultdict(Counter)
for a, b in zip(text, text[1:]):
    bigram[a][b] += 1

lm_rows = []
for char, counts in bigram.items():
    total = sum(counts.values())
    best_char, best_count = counts.most_common(1)[0]
    lm_rows.append({
        "当前字符": char,
        "最可能下一个字符": best_char,
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
# 准备 6x6 输入图像和 3x3 边缘检测核。
image = np.array([
    [0, 0, 0, 1, 1, 1],
    [0, 0, 0, 1, 1, 1],
    [0, 0, 0, 1, 1, 1],
    [0, 0, 0, 1, 1, 1],
    [0, 0, 0, 1, 1, 1],
    [0, 0, 0, 1, 1, 1],
], dtype=float)
kernel = np.array([
    [-1, 0, 1],
    [-1, 0, 1],
    [-1, 0, 1],
], dtype=float)

feature = correlate2d(image, kernel, mode="valid")
display(pd.DataFrame(image.astype(int)))
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
            "卷积值": int((window * kernel).sum()),
        })

conv_df = pd.DataFrame(rows)
display(conv_df.head(8))
display(pd.DataFrame(feature.astype(int)))
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
            ax.text(j, i, f"{data[i, j]:.0f}", ha="center", va="center", color="#0f172a")
fig.suptitle("卷积特征提取", x=0.08, ha="left", fontsize=14, fontweight="bold", color="#0f172a")
plt.tight_layout()
plt.show()
"""


PATCHIFY_CELL = """
# 把 8x8 图像切成 2x2 patch token。
vit_image = np.arange(64).reshape(8, 8)
patch_size = 2
patches = vit_image.reshape(4, patch_size, 4, patch_size).swapaxes(1, 2)
patch_tokens = patches.reshape(-1, patch_size * patch_size)

patch_df = pd.DataFrame(patch_tokens, columns=["p00", "p01", "p10", "p11"])
patch_df.insert(0, "patch_id", range(len(patch_df)))
display(patch_df.head(8))
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
# CLIP / InfoNCE：图像向量和文本向量先归一化，再计算相似度矩阵。
image_names = ["校园图", "手写数字", "知识图谱"]
text_names = ["一张校园路径图", "一个手写数字", "实体关系网络"]

image_emb = normalize(np.array([
    [0.90, 0.10, 0.12],
    [0.15, 0.88, 0.20],
    [0.18, 0.22, 0.90],
]))
text_emb = normalize(np.array([
    [0.86, 0.16, 0.10],
    [0.10, 0.90, 0.24],
    [0.20, 0.18, 0.88],
]))

temperature = 0.08
logits = image_emb @ text_emb.T / temperature
probs = np.exp(logits - logits.max(axis=1, keepdims=True))
probs = probs / probs.sum(axis=1, keepdims=True)
clip_loss = log_loss(np.arange(3), probs, labels=np.arange(3))

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
# 准备一个学习路径 MDP：状态、动作、转移概率和即时奖励。
states = ["S0", "S1", "S2", "S3"]
actions = {
    "S0": ["刷题", "看讲解"],
    "S1": ["复盘", "继续"],
    "S2": ["测验"],
    "S3": [],
}
transitions = {
    ("S0", "刷题"): [("S1", 0.75, 1.0), ("S0", 0.25, -0.2)],
    ("S0", "看讲解"): [("S1", 0.55, 0.6), ("S0", 0.45, 0.0)],
    ("S1", "复盘"): [("S2", 0.80, 1.2), ("S1", 0.20, 0.0)],
    ("S1", "继续"): [("S2", 0.60, 0.7), ("S1", 0.40, -0.1)],
    ("S2", "测验"): [("S3", 1.00, 2.0)],
}

display(pd.DataFrame(
    [
        {"状态": s, "动作": a, "转移": transitions[(s, a)]}
        for s, acts in actions.items()
        for a in acts
    ]
))
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
# 绘制各状态价值随迭代收敛。
fig, ax = plt.subplots(figsize=(8.2, 5.0))
for state in states:
    ax.plot(value_trace["轮次"], value_trace[state], marker="o", linewidth=2.0, label=state)
ax.set_title("价值迭代收敛", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xlabel("轮次")
ax.set_ylabel("V(s)")
ax.grid(True, color="#e2e8f0", linewidth=0.8)
ax.legend()
plt.tight_layout()
plt.show()
"""


TD_CELL = """
# TD(0)：用下一状态价值修正当前状态价值。
trajectory = [
    ("S0", 0.0, "S1"),
    ("S1", 1.0, "S2"),
    ("S2", 2.0, "S3"),
    ("S0", 0.5, "S1"),
    ("S1", 1.2, "S2"),
]
V_td = defaultdict(float)
alpha = 0.4
gamma = 0.9
td_rows = []

for step, (state, reward, next_state) in enumerate(trajectory, start=1):
    target = reward + gamma * V_td[next_state]
    old = V_td[state]
    V_td[state] = old + alpha * (target - old)
    td_rows.append({
        "步": step,
        "状态": state,
        "奖励": reward,
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
td_values = pd.Series({state: V_td[state] for state in states})
td_values.plot(kind="bar", ax=ax, color="#2563eb")
ax.set_title("TD(0) 状态价值", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_ylabel("V(s)")
ax.grid(True, axis="y", color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
"""


BANDIT_CELL = """
# epsilon-greedy：在探索和利用之间切换。
def run_bandit(epsilon, steps=120, seed=0):
    rng = np.random.default_rng(seed)
    true_means = np.array([0.20, 0.35, 0.55])
    estimates = np.zeros(3)
    counts = np.zeros(3)
    rows = []
    total_reward = 0.0

    for step in range(1, steps + 1):
        explore = rng.random() < epsilon
        action = rng.integers(3) if explore else int(np.argmax(estimates))
        reward = rng.normal(true_means[action], 0.08)
        counts[action] += 1
        estimates[action] += (reward - estimates[action]) / counts[action]
        total_reward += reward
        if step % 20 == 0:
            rows.append({
                "epsilon": epsilon,
                "步数": step,
                "累计奖励": round(total_reward, 2),
                "动作0次数": int(counts[0]),
                "动作1次数": int(counts[1]),
                "动作2次数": int(counts[2]),
            })
    return pd.DataFrame(rows)


bandit_trace = pd.concat([run_bandit(0.05, seed=1), run_bandit(0.25, seed=1)], ignore_index=True)
display(bandit_trace)
"""


BANDIT_PLOT_CELL = """
# 绘制不同 epsilon 的累计奖励。
fig, ax = plt.subplots(figsize=(7.6, 4.8))
for epsilon, part in bandit_trace.groupby("epsilon"):
    ax.plot(part["步数"], part["累计奖励"], marker="o", linewidth=2.2, label=f"epsilon={epsilon}")
ax.set_title("epsilon-greedy 累计奖励", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xlabel("步数")
ax.set_ylabel("累计奖励")
ax.grid(True, color="#e2e8f0", linewidth=0.8)
ax.legend()
plt.tight_layout()
plt.show()
"""


ANNEALING_CELL = """
# 使用 scipy dual_annealing 搜索二维表征，使目标函数尽量小。
def objective(vec):
    x, y = vec
    return (x - 1.4) ** 2 + (y + 0.6) ** 2 + 0.35 * np.sin(4 * x) * np.cos(3 * y)

anneal_trace = []

def collect_state(x, f, context):
    anneal_trace.append({"候选x": x[0], "候选y": x[1], "loss": f, "context": context})

result = dual_annealing(objective, bounds=[(-3, 3), (-3, 3)], maxiter=35, seed=3, callback=collect_state)
anneal_df = pd.DataFrame(anneal_trace)
if anneal_df.empty:
    anneal_df = pd.DataFrame([{"候选x": result.x[0], "候选y": result.x[1], "loss": result.fun, "context": 0}])

display(anneal_df.tail(8).round(4))
print("best:", np.round(result.x, 4), "loss:", round(float(result.fun), 4))
"""


ANNEALING_PLOT_CELL = """
# 绘制搜索轨迹和 loss。
grid_x = np.linspace(-3, 3, 120)
grid_y = np.linspace(-3, 3, 120)
xx, yy = np.meshgrid(grid_x, grid_y)
zz = objective([xx, yy])

fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.5))
axes[0].contourf(xx, yy, zz, levels=24, cmap="Blues")
axes[0].plot(anneal_df["候选x"], anneal_df["候选y"], color="#f97316", marker="o", linewidth=1.6)
axes[0].scatter(result.x[0], result.x[1], marker="X", s=220, color="#ef4444", edgecolor="#0f172a")
axes[0].set_title("搜索轨迹", loc="left", fontweight="bold")
axes[0].set_xlabel("x")
axes[0].set_ylabel("y")

axes[1].plot(range(1, len(anneal_df) + 1), anneal_df["loss"], color="#2563eb", linewidth=2.2)
axes[1].set_title("候选 loss", loc="left", fontweight="bold")
axes[1].set_xlabel("记录点")
axes[1].set_ylabel("loss")
axes[1].grid(True, color="#e2e8f0", linewidth=0.8)
plt.tight_layout()
plt.show()
"""


MCTS_CELL = """
# MCTS / UCT：根据平均价值和探索项选择下一条分支。
parent_visits = 42
moves = pd.DataFrame(
    {
        "走法": ["A", "B", "C", "D"],
        "访问次数": [18, 10, 8, 6],
        "累计价值": [11.2, 7.8, 5.0, 4.7],
    }
)
explore_c = 1.4
moves["平均价值"] = moves["累计价值"] / moves["访问次数"]
moves["探索项"] = explore_c * np.sqrt(np.log(parent_visits) / moves["访问次数"])
moves["UCT"] = moves["平均价值"] + moves["探索项"]
moves = moves.sort_values("UCT", ascending=False).reset_index(drop=True)
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
ax.set_title("UCT 分数", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_ylabel("分数")
ax.grid(True, axis="y", color="#e2e8f0", linewidth=0.8)
ax.legend()
plt.tight_layout()
plt.show()
"""


DIFFUSION_1D_CELL = """
# 1D diffusion：按噪声调度逐步把 x0 混入高斯噪声。
rng = np.random.default_rng(7)
x0 = 1.0
betas = np.linspace(0.04, 0.22, 8)
alphas = 1 - betas
alpha_bars = np.cumprod(alphas)
noise = rng.normal(size=len(betas))

diff_rows = []
xs = []
for t, (alpha_bar, eps) in enumerate(zip(alpha_bars, noise), start=1):
    xt = np.sqrt(alpha_bar) * x0 + np.sqrt(1 - alpha_bar) * eps
    xs.append(xt)
    diff_rows.append({"t": t, "alpha_bar": round(alpha_bar, 3), "noise": round(eps, 3), "x_t": round(float(xt), 3)})

diff_1d_df = pd.DataFrame(diff_rows)
display(diff_1d_df)
"""


DIFFUSION_1D_PLOT_CELL = """
# 绘制前向加噪和概念性反向去噪轨迹。
reverse = np.linspace(xs[-1], x0, len(xs))
fig, ax = plt.subplots(figsize=(7.4, 4.8))
ax.plot(diff_1d_df["t"], diff_1d_df["x_t"], marker="o", linewidth=2.2, label="前向加噪")
ax.plot(diff_1d_df["t"], reverse, marker="o", linewidth=2.2, label="反向去噪")
ax.axhline(x0, color="#94a3b8", linestyle="--", linewidth=1.4, label="x0")
ax.set_title("1D Diffusion 轨迹", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
ax.set_xlabel("t")
ax.set_ylabel("数值")
ax.grid(True, color="#e2e8f0", linewidth=0.8)
ax.legend()
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
# GAN 玩具过程：判别器由 sklearn MLPClassifier 训练，生成分布逐步靠近真实分布。
rng = np.random.default_rng(5)
fake_mean = -1.4
gan_rows = []

for step in range(1, 9):
    real = rng.normal(1.2, 0.35, size=120)
    fake = rng.normal(fake_mean, 0.45, size=120)
    X_disc = np.concatenate([real, fake]).reshape(-1, 1)
    y_disc = np.array([1] * len(real) + [0] * len(fake))
    disc = MLPClassifier(hidden_layer_sizes=(6,), max_iter=400, random_state=step)
    disc.fit(X_disc, y_disc)
    fake_score = disc.predict_proba(fake.reshape(-1, 1))[:, 1].mean()
    real_score = disc.predict_proba(real.reshape(-1, 1))[:, 1].mean()
    fake_mean += 0.28 * (real.mean() - fake.mean())
    gan_rows.append({
        "轮次": step,
        "生成均值": round(fake.mean(), 3),
        "D(real)": round(float(real_score), 3),
        "D(fake)": round(float(fake_score), 3),
    })

gan_trace = pd.DataFrame(gan_rows)
display(gan_trace)
"""


GAN_PLOT_CELL = """
# 绘制 D(fake) 变化和最终一维分布。
fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.4))
axes[0].plot(gan_trace["轮次"], gan_trace["D(fake)"], marker="o", linewidth=2.2, color="#2563eb")
axes[0].set_title("判别器对生成样本的评分", loc="left", fontweight="bold")
axes[0].set_xlabel("轮次")
axes[0].set_ylabel("D(fake)")
axes[0].grid(True, color="#e2e8f0", linewidth=0.8)

axes[1].hist(real, bins=18, alpha=0.65, label="real", color="#2563eb")
axes[1].hist(fake, bins=18, alpha=0.65, label="fake", color="#f97316")
axes[1].set_title("最后一轮分布", loc="left", fontweight="bold")
axes[1].legend()
plt.tight_layout()
plt.show()
"""


DIFFUSION_TOY_CELL = """
# 用一组二维点演示加噪和去噪方向。
rng = np.random.default_rng(9)
clean_points = rng.normal([1.0, 1.0], [0.18, 0.18], size=(80, 2))
noise_points = rng.normal(size=clean_points.shape)
noise_level = 0.65
noisy_points = np.sqrt(1 - noise_level) * clean_points + np.sqrt(noise_level) * noise_points
denoised_points = 0.55 * noisy_points + 0.45 * clean_points.mean(axis=0)

toy_summary = pd.DataFrame(
    [
        {"阶段": "noisy", "到clean中心的平均距离": np.linalg.norm(noisy_points - clean_points.mean(axis=0), axis=1).mean()},
        {"阶段": "denoised", "到clean中心的平均距离": np.linalg.norm(denoised_points - clean_points.mean(axis=0), axis=1).mean()},
    ]
).round(3)
display(toy_summary)
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
                ["训练 sklearn MLPClassifier", "查看预测概率", "绘制 loss 和网络结构"],
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
                ["计算 TransE 距离", "计算 attention 权重", "绘制几何图和热力图"],
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
                ["生成中心词-上下文样本", "计算二维词向量", "绘制词向量位置"],
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
                ["计算 2D 卷积", "展开窗口过程", "绘制特征图"],
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
                ["切分 patch token", "查看 token 表", "绘制 patch"],
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
                ["切分 patch", "随机 mask", "绘制重建图"],
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
                ["计算图文相似度", "计算 InfoNCE loss", "绘制相似度矩阵"],
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
                ["准备 MDP 转移表", "执行价值迭代", "绘制收敛曲线"],
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
                ["执行 bootstrap 更新", "输出 TD target", "绘制状态价值"],
                "../ch11.html",
            ),
            rs.section("0", "环境与数据"),
            rs.code(DEPENDENCIES_CELL),
            rs.code(MDP_CELL),
            rs.section("1", "TD 更新"),
            rs.code(TD_CELL),
            rs.code(TD_PLOT_CELL),
        ]),
        "ch11_epsilon_greedy.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · epsilon-greedy 代码实验",
                ["模拟多臂老虎机", "比较不同 epsilon", "绘制累计奖励"],
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
                ["使用 scipy dual_annealing", "记录候选 loss", "绘制搜索轨迹"],
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
                ["计算平均价值", "计算探索项", "绘制 UCT 分数"],
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
                ["训练 sklearn 判别器", "移动生成分布", "绘制判别器评分"],
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
                ["生成二维点", "加入高斯噪声", "绘制去噪方向"],
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
