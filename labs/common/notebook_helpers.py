"""Shared helpers for pedagogical notebooks."""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 中文字体：nbconvert 静态页优先使用系统 sans-serif
plt.rcParams.update(
    {
        "figure.figsize": (7.5, 4.2),
        "font.size": 11,
        "axes.unicode_minus": False,
        "font.sans-serif": ["PingFang SC", "Heiti SC", "Arial Unicode MS", "DejaVu Sans"],
    }
)


def repo_root() -> Path:
    cwd = Path.cwd()
    if (cwd / "labs").exists():
        return cwd
    if (cwd.parent / "labs").exists():
        return cwd.parent
    return cwd


BOOTSTRAP = textwrap.dedent(
    """
    import sys
    from pathlib import Path
    ROOT = Path.cwd()
    if not (ROOT / "labs").exists() and (ROOT.parent / "labs").exists():
        ROOT = ROOT.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    """
).strip()


def bootstrap_code(extra: str = "") -> str:
    return BOOTSTRAP + ("\n" + extra.strip() if extra.strip() else "")


def show_df(df: pd.DataFrame, title: str = "") -> None:
    if title:
        print(title)
    print(df.to_string(index=False))


def plot_line_series(
    xs: list,
    ys: list,
    *,
    title: str,
    xlabel: str = "",
    ylabel: str = "",
    markers: bool = True,
) -> None:
    fig, ax = plt.subplots()
    ax.plot(xs, ys, marker="o" if markers else None, linewidth=2)
    ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_scatter_labeled(
    points: np.ndarray,
    labels: np.ndarray | None,
    *,
    title: str,
    label_names: dict[int, str] | None = None,
) -> None:
    fig, ax = plt.subplots()
    if labels is None:
        ax.scatter(points[:, 0], points[:, 1], s=60, c="#0d6b62")
    else:
        for lab in np.unique(labels):
            mask = labels == lab
            name = (label_names or {}).get(int(lab), f"类 {lab}")
            ax.scatter(points[mask, 0], points[mask, 1], s=60, label=name)
        ax.legend()
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
