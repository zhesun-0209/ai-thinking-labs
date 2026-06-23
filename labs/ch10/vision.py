"""Chapter 10 vision demos — numpy only."""

from __future__ import annotations

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


def vit_patchify() -> None:
    # 4×4 → 2×2 网格，每格 2×2 patch
    patches = IMG.reshape(2, 2, 2, 2).transpose(0, 2, 1, 3).reshape(4, 4)
    print("4 个 2×2 patch 展平为 token (ViT patchify):")
    for i, p in enumerate(patches):
        print(f"  P{i+1}: {p.astype(int).tolist()}")


def mae_demo() -> None:
    mask = np.array([0, 1, 1, 1])  # 只保留 P1
    print("MAE 掩码 75%: 可见 patch", np.where(mask == 0)[0].tolist())
    print("Encoder 仅处理可见 token; Decoder 重构全部像素 MSE")


def clip_infonce() -> None:
    v_i = np.array([0.9, 0.1, 0.0])
    v_t_pos = np.array([0.85, 0.12, 0.05])
    v_t_neg = np.array([0.1, 0.2, 0.9])
    cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
    print(f"正例 cos={cos(v_i, v_t_pos):.2f} (网页 0.91)")
    print(f"负例 cos={cos(v_i, v_t_neg):.2f} (网页 0.08)")
