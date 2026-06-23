"""Chapter 10 vision demos — pedagogical API."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

IMG = np.arange(16, dtype=float).reshape(4, 4)
KERNEL = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=float)


def conv2d_valid(x: np.ndarray, k: np.ndarray) -> np.ndarray:
    h, w = x.shape
    kh, kw = k.shape
    out = np.zeros((h - kh + 1, w - kw + 1))
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            out[i, j] = (x[i : i + kh, j : j + kw] * k).sum()
    return out


def conv_demo() -> None:
    feat = conv2d_valid(IMG, KERNEL)
    pooled = feat.max()
    print("4×4 输入 → 2×2 卷积特征:")
    print(feat.astype(int))
    print(f"MaxPool → {pooled:.0f}")


def plot_conv() -> None:
    feat = conv2d_valid(IMG, KERNEL)
    fig, axes = plt.subplots(1, 3, figsize=(9, 3))
    axes[0].imshow(IMG, cmap="gray")
    axes[0].set_title("4×4 输入")
    axes[1].imshow(feat, cmap="viridis")
    axes[1].set_title("2×2 卷积")
    axes[2].bar(["max"], [feat.max()], color="#0d6b62")
    axes[2].set_title(f"MaxPool={feat.max():.0f}")
    for ax in axes[:2]:
        ax.axis("off")
    plt.suptitle("CNN 流水线（与 ch10 网页同数）")
    plt.tight_layout()
    plt.show()


def vit_patchify() -> None:
    patches = IMG.reshape(2, 2, 2, 2).transpose(0, 2, 1, 3).reshape(4, 4)
    print("4 个 2×2 patch → token:")
    for i, p in enumerate(patches):
        print(f"  P{i+1}: {p.astype(int).tolist()}")


def plot_patches() -> None:
    fig, axes = plt.subplots(1, 5, figsize=(10, 2.5))
    axes[0].imshow(IMG, cmap="gray")
    axes[0].set_title("原图")
    patches = IMG.reshape(2, 2, 2, 2).transpose(0, 2, 1, 3)
    for i in range(4):
        axes[i + 1].imshow(patches[i // 2, i % 2], cmap="gray")
        axes[i + 1].set_title(f"P{i+1}")
    for ax in axes:
        ax.axis("off")
    plt.suptitle("ViT Patchify")
    plt.tight_layout()
    plt.show()


def mae_demo() -> None:
    mask = np.array([0, 1, 1, 1])
    print("MAE 掩码 75%: 可见 patch 索引", np.where(mask == 0)[0].tolist())
    print("Encoder 只看 25% token → Decoder 重构全图 MSE")


def plot_mae_mask() -> None:
    mask = np.array([0, 1, 1, 1])
    fig, ax = plt.subplots(figsize=(4, 4))
    grid = np.arange(4).reshape(2, 2)
    show = np.where(mask.reshape(2, 2) == 0, grid, np.nan)
    ax.imshow(show, cmap="Greens")
    ax.set_title("MAE：仅 P1 可见（75% 掩码）")
    ax.axis("off")
    plt.tight_layout()
    plt.show()


def clip_infonce() -> None:
    v_i = np.array([0.9, 0.1, 0.0])
    v_t_pos = np.array([0.85, 0.12, 0.05])
    v_t_neg = np.array([0.1, 0.2, 0.9])
    cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
    print(f"正例 cos={cos(v_i, v_t_pos):.2f} (网页 0.91)")
    print(f"负例 cos={cos(v_i, v_t_neg):.2f} (网页 0.08)")


def plot_clip_cos() -> None:
    labels = ["正例图文", "负例图文"]
    vals = [0.91, 0.08]
    fig, ax = plt.subplots()
    ax.bar(labels, vals, color=["#0d6b62", "#e74c3c"])
    ax.set_ylim(0, 1)
    ax.set_title("CLIP：对比学习拉大正负 cos 差距")
    plt.tight_layout()
    plt.show()
