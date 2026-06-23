"""栈 / 队列 / 优先队列 状态 GIF 动画（静态页可播放）。"""

from __future__ import annotations

import io
import tempfile
from pathlib import Path
from typing import Any, Literal

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import Image, display
from matplotlib.animation import FuncAnimation, PillowWriter

ContainerKind = Literal["queue", "stack", "priority"]


def _gif_bytes(anim: FuncAnimation, fps: float) -> bytes:
    """Save animation to GIF bytes (PillowWriter needs a real file path)."""
    fd, path = tempfile.mkstemp(suffix=".gif")
    import os

    os.close(fd)
    try:
        anim.save(path, writer=PillowWriter(fps=fps))
        return Path(path).read_bytes()
    finally:
        Path(path).unlink(missing_ok=True)


def _show_gif(anim: FuncAnimation, fps: float, caption: str = "") -> None:
    data = _gif_bytes(anim, fps)
    if caption:
        print(caption)
    display(Image(data=data))


def _draw_container(ax, items: list[str], kind: ContainerKind, highlight: str | None = None) -> None:
    ax.clear()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    labels = {"queue": "Queue (FIFO)", "stack": "Stack (LIFO)", "priority": "Priority Queue"}
    ax.text(0.2, 2.6, labels[kind], fontsize=12, fontweight="bold")
    if not items:
        ax.text(5, 1.2, "(empty)", ha="center", fontsize=11, color="#888")
        return
    n = len(items)
    w = min(1.4, 8.0 / max(n, 1))
    for i, item in enumerate(items):
        x = 0.5 + i * (w + 0.15)
        color = "#c0392b" if item == highlight else "#0d6b62"
        rect = mpatches.FancyBboxPatch(
            (x, 0.8), w, 1.0, boxstyle="round,pad=0.05", facecolor=color, edgecolor="white", linewidth=1.5
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, 1.3, str(item), ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    if kind == "queue":
        ax.annotate("", xy=(0.3, 1.3), xytext=(0.05, 1.3), arrowprops=dict(arrowstyle="->", lw=2, color="#333"))
        ax.text(0.05, 0.4, "dequeue", fontsize=8)
        ax.annotate("", xy=(9.5, 1.3), xytext=(9.95, 1.3), arrowprops=dict(arrowstyle="->", lw=2, color="#333"))
        ax.text(9.2, 0.4, "enqueue", fontsize=8)
    elif kind == "stack":
        ax.text(9.2, 2.35, "top -> pop", fontsize=8, ha="right")


def animate_container(
    snapshots: list[dict[str, Any]],
    kind: ContainerKind = "queue",
    caption: str = "",
    fps: float = 1.2,
) -> None:
    if not snapshots:
        return
    fig, (ax_c, ax_t) = plt.subplots(2, 1, figsize=(9, 4), gridspec_kw={"height_ratios": [2, 1]})

    def _update(i: int):
        snap = snapshots[i]
        items = list(snap.get("items") or [])
        pop = snap.get("pop")
        _draw_container(ax_c, items, kind, highlight=pop)
        ax_t.clear()
        ax_t.axis("off")
        step = snap.get("step", i)
        action = snap.get("action", "")
        ax_t.text(0.02, 0.6, f"Step {step}: {action}", fontsize=11)
        extra = snap.get("extra", "")
        if extra:
            ax_t.text(0.02, 0.15, extra, fontsize=10, color="#555")

    anim = FuncAnimation(fig, _update, frames=len(snapshots), interval=int(1000 / fps), repeat=True)
    _show_gif(anim, fps, caption)
    plt.close(fig)


def animate_items_row(
    snapshots: list[dict[str, Any]],
    *,
    title: str = "State",
    fps: float = 1.0,
) -> None:
    """通用横向 token / 事实列表动画。"""
    if not snapshots:
        return
    fig, (ax_c, ax_t) = plt.subplots(2, 1, figsize=(9, 3.5), gridspec_kw={"height_ratios": [2, 1]})

    def _update(i: int):
        snap = snapshots[i]
        items = list(snap.get("items") or [])
        highlight = snap.get("highlight")
        ax_c.clear()
        ax_c.set_xlim(0, 10)
        ax_c.set_ylim(0, 2.5)
        ax_c.axis("off")
        ax_c.text(0.2, 2.2, title, fontsize=12, fontweight="bold")
        if not items:
            ax_c.text(5, 1.0, "(empty)", ha="center", color="#888")
        else:
            w = min(1.2, 8.5 / max(len(items), 1))
            for j, item in enumerate(items):
                x = 0.3 + j * (w + 0.12)
                color = "#c0392b" if item == highlight else "#0d6b62"
                rect = mpatches.FancyBboxPatch(
                    (x, 0.6), w, 0.9, boxstyle="round,pad=0.04", facecolor=color, edgecolor="white"
                )
                ax_c.add_patch(rect)
                ax_c.text(x + w / 2, 1.05, str(item), ha="center", va="center", color="white", fontsize=9)
        ax_t.clear()
        ax_t.axis("off")
        ax_t.text(0.02, 0.55, f"Step {snap.get('step', i)}: {snap.get('action', '')}", fontsize=11)
        extra = snap.get("extra", "")
        if extra:
            ax_t.text(0.02, 0.12, extra, fontsize=10, color="#555")

    anim = FuncAnimation(fig, _update, frames=len(snapshots), interval=int(1000 / fps), repeat=True)
    _show_gif(anim, fps)
    plt.close(fig)


def animate_bar_values(
    snapshots: list[dict[str, Any]],
    *,
    title: str = "Values",
    ylabel: str = "value",
    fps: float = 1.0,
) -> None:
    """逐步柱状图（价值迭代、UCT 等）。"""
    if not snapshots:
        return
    all_labels: list[str] = []
    for s in snapshots:
        for k in s.get("values", {}):
            if k not in all_labels:
                all_labels.append(k)
    ymax = max(max(s.get("values", {}).values(), default=0) for s in snapshots) * 1.15 or 1.0
    fig, (ax_c, ax_t) = plt.subplots(2, 1, figsize=(7, 4.5), gridspec_kw={"height_ratios": [3, 1]})

    def _update(i: int):
        snap = snapshots[i]
        vals = snap.get("values", {})
        ax_c.clear()
        labels = all_labels or list(vals.keys())
        heights = [vals.get(k, 0) for k in labels]
        colors = ["#c0392b" if k == snap.get("highlight") else "#0d6b62" for k in labels]
        ax_c.bar(labels, heights, color=colors)
        ax_c.set_ylim(0, ymax)
        ax_c.set_ylabel(ylabel)
        ax_c.set_title(title)
        ax_c.grid(True, axis="y", alpha=0.3)
        ax_t.clear()
        ax_t.axis("off")
        ax_t.text(0.02, 0.55, f"Step {snap.get('step', i)}: {snap.get('action', '')}", fontsize=11)
        extra = snap.get("extra", "")
        if extra:
            ax_t.text(0.02, 0.12, extra, fontsize=10, color="#555")

    anim = FuncAnimation(fig, _update, frames=len(snapshots), interval=int(1000 / fps), repeat=True)
    _show_gif(anim, fps)
    plt.close(fig)


def animate_grid_highlight(
    snapshots: list[dict[str, Any]],
    *,
    grid: np.ndarray | None = None,
    title: str = "Grid",
    fps: float = 1.0,
) -> None:
    """卷积窗口滑动：高亮 patch 区域。"""
    import numpy as np

    if not snapshots:
        return
    fig, (ax_c, ax_t) = plt.subplots(2, 1, figsize=(4.5, 5), gridspec_kw={"height_ratios": [3, 1]})

    def _update(i: int):
        snap = snapshots[i]
        g = snap.get("grid")
        if g is None and grid is not None:
            g = grid
        ax_c.clear()
        if g is not None:
            ax_c.imshow(g, cmap="gray", vmin=g.min(), vmax=g.max())
            r0, c0, kh, kw = snap.get("patch", (0, 0, 1, 1))
            rect = mpatches.Rectangle((c0 - 0.5, r0 - 0.5), kw, kh, fill=False, edgecolor="#c0392b", linewidth=2)
            ax_c.add_patch(rect)
            out = snap.get("out_val")
            if out is not None:
                ax_c.text(g.shape[1] - 0.3, -0.8, f"out={out:.1f}", fontsize=10, color="#c0392b")
        ax_c.set_title(title)
        ax_c.axis("off")
        ax_t.clear()
        ax_t.axis("off")
        ax_t.text(0.02, 0.55, f"Step {snap.get('step', i)}: {snap.get('action', '')}", fontsize=10)

    anim = FuncAnimation(fig, _update, frames=len(snapshots), interval=int(1000 / fps), repeat=True)
    _show_gif(anim, fps)
    plt.close(fig)


def snapshots_from_codelens(frames, key: str = "frontier", kind: ContainerKind = "queue") -> list[dict]:
    snaps: list[dict] = []
    for f in frames:
        raw = f.state.get(key, f.state.get("stack", []))
        if isinstance(raw, str):
            items = [] if raw in ("∅", "", "[]") else raw.split("→")
        elif isinstance(raw, (list, tuple)):
            items = [str(x) for x in raw]
        else:
            items = []
        pop = f.state.get("current") or f.state.get("弹出")
        extra_parts = []
        if "visited" in f.state:
            extra_parts.append(f"visited={f.state['visited']}")
        if "parent" in f.state and f.state["parent"]:
            extra_parts.append(f"parent={f.state['parent']}")
        snaps.append(
            {
                "step": f.step,
                "items": items,
                "pop": str(pop) if pop else None,
                "action": f.narrative,
                "extra": "  ".join(extra_parts),
            }
        )
    return snaps
