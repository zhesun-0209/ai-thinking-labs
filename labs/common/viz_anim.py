"""栈 / 队列 / 优先队列 状态 GIF 动画（静态页可播放）。"""

from __future__ import annotations

import base64
import html
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Literal

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML, display
from matplotlib.animation import FuncAnimation, PillowWriter

from common.mpl_setup import ascii_plot, configure_matplotlib

ContainerKind = Literal["queue", "stack", "priority"]


def _chip_label(item: Any, idx: int) -> str:
    text = str(item)
    text = ascii_plot(text) if text.isascii() else text
    return textwrap.shorten(text, width=18, placeholder="...")


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
    encoded = base64.b64encode(data).decode("ascii")
    alt = html.escape(caption or "Frontier animation")
    display(HTML(f'<img class="ai-labs-anim" alt="{alt}" src="data:image/gif;base64,{encoded}" />'))


def _draw_label(ax, x: float, y: float, text: str, *, color: str = "#475569", size: int = 9) -> None:
    ax.text(x, y, text, ha="center", va="center", color=color, fontsize=size, fontweight="bold")


def _draw_item(ax, x: float, y: float, w: float, h: float, text: str, *, active: bool, idx: int) -> None:
    face = "#dc4d37" if active else "#0f766e"
    edge = "#ffffff" if active else "#d1fae5"
    rect = mpatches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.04,rounding_size=0.08",
        facecolor=face,
        edgecolor=edge,
        linewidth=1.6,
    )
    ax.add_patch(rect)
    ax.text(
        x + w / 2,
        y + h / 2,
        _chip_label(text, idx),
        ha="center",
        va="center",
        color="#ffffff",
        fontsize=9,
        fontweight="bold",
    )


def _draw_container(ax, items: list[str], kind: ContainerKind, highlight: str | None = None) -> None:
    ax.clear()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.4)
    ax.axis("off")
    ax.set_facecolor("#f8fafc")
    labels = {
        "queue": ("Queue / 队列", "FIFO: 左端 popleft()，右端 append()"),
        "stack": ("Stack / 栈", "LIFO: 栈顶 pop()，栈顶 append()"),
        "priority": ("Priority queue / 优先队列", "每轮先按 key 排序，再取最小项"),
    }
    title, subtitle = labels[kind]
    ax.text(0.25, 3.05, title, fontsize=13, fontweight="bold", color="#0f172a")
    ax.text(0.25, 2.78, subtitle, fontsize=9.5, color="#64748b")
    if not items:
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (3.8, 1.15),
                2.4,
                0.7,
                boxstyle="round,pad=0.06,rounding_size=0.12",
                facecolor="#ffffff",
                edgecolor="#dbe4ef",
            )
        )
        ax.text(5, 1.5, "(empty)", ha="center", va="center", fontsize=11, color="#94a3b8")
        return

    if kind == "queue":
        n = len(items)
        w = min(1.35, 7.2 / max(n, 1))
        gap = 0.12
        y = 1.25
        start = 1.2
        ax.plot([start - 0.2, start + n * (w + gap) - gap + 0.2], [y - 0.12, y - 0.12], color="#cbd5e1", lw=2)
        for i, item in enumerate(items):
            x = start + i * (w + gap)
            _draw_item(ax, x, y, w, 0.78, item, active=item == highlight, idx=i)
        _draw_label(ax, start, y - 0.46, "front", color="#0f766e")
        _draw_label(ax, start + (n - 1) * (w + gap) + w, y - 0.46, "back", color="#0f766e")
        ax.annotate(
            "popleft()",
            xy=(start - 0.08, y + 0.39),
            xytext=(0.25, y + 0.39),
            ha="left",
            va="center",
            color="#dc4d37",
            fontsize=9,
            fontweight="bold",
            arrowprops=dict(arrowstyle="<-", lw=2.2, color="#dc4d37"),
        )
        ax.annotate(
            "append()",
            xy=(start + n * (w + gap) - gap + 0.08, y + 0.39),
            xytext=(9.55, y + 0.39),
            ha="right",
            va="center",
            color="#0f766e",
            fontsize=9,
            fontweight="bold",
            arrowprops=dict(arrowstyle="->", lw=2.2, color="#0f766e"),
        )
        return

    if kind == "priority":
        n = len(items)
        w = min(1.5, 7.4 / max(n, 1))
        gap = 0.12
        y = 1.22
        start = 1.1
        for i, item in enumerate(items):
            x = start + i * (w + gap)
            _draw_item(ax, x, y, w, 0.82, item, active=item == highlight, idx=i)
            ax.text(x + w / 2, y - 0.28, f"#{i + 1}", ha="center", va="center", fontsize=8, color="#64748b")
        ax.annotate(
            "pop_min()",
            xy=(start - 0.05, y + 0.41),
            xytext=(0.18, y + 0.41),
            ha="left",
            va="center",
            color="#dc4d37",
            fontsize=9,
            fontweight="bold",
            arrowprops=dict(arrowstyle="<-", lw=2.2, color="#dc4d37"),
        )
        ax.text(start, y - 0.58, "lowest key", ha="left", va="center", fontsize=9, color="#0f766e", fontweight="bold")
        return

    n = len(items)
    h = min(0.58, 2.2 / max(n, 1))
    gap = 0.08
    w = 2.0
    x = 4.0
    bottom = 0.46
    for i, item in enumerate(items):
        y = bottom + i * (h + gap)
        _draw_item(ax, x, y, w, h, item, active=item == highlight, idx=i)
    top_y = bottom + (n - 1) * (h + gap) + h / 2
    ax.annotate(
        "pop()",
        xy=(x + w + 0.08, top_y),
        xytext=(8.5, top_y),
        ha="right",
        va="center",
        color="#dc4d37",
        fontsize=9,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", lw=2.2, color="#dc4d37"),
    )
    ax.text(x - 0.18, top_y, "top", ha="right", va="center", fontsize=9, color="#0f766e", fontweight="bold")
    ax.text(x + w / 2, bottom - 0.25, "bottom", ha="center", va="center", fontsize=8, color="#64748b")


def animate_container(
    snapshots: list[dict[str, Any]],
    kind: ContainerKind = "queue",
    caption: str = "",
    fps: float = 1.2,
) -> None:
    configure_matplotlib()
    if not snapshots:
        return
    fig, (ax_c, ax_t) = plt.subplots(2, 1, figsize=(10, 4.8), gridspec_kw={"height_ratios": [3, 1.2]})

    def _update(i: int):
        snap = snapshots[i]
        items = list(snap.get("items") or [])
        pop = snap.get("pop")
        _draw_container(ax_c, items, kind, highlight=pop)
        ax_t.clear()
        ax_t.set_xlim(0, 1)
        ax_t.set_ylim(0, 1)
        ax_t.axis("off")
        step = snap.get("step", i)
        action = snap.get("action", "")
        ax_t.add_patch(
            mpatches.FancyBboxPatch(
                (0.02, 0.12),
                0.96,
                0.76,
                transform=ax_t.transAxes,
                boxstyle="round,pad=0.02,rounding_size=0.03",
                facecolor="#ffffff",
                edgecolor="#dbe4ef",
            )
        )
        ax_t.text(0.05, 0.62, f"Step {step}", fontsize=11, fontweight="bold", color="#0f172a", transform=ax_t.transAxes)
        if action:
            action_text = ascii_plot(str(action)) if str(action).isascii() else str(action)
            ax_t.text(0.2, 0.62, action_text, fontsize=11, color="#dc4d37", fontweight="bold", transform=ax_t.transAxes)
        extra = snap.get("extra", "")
        if extra:
            extra_text = ascii_plot(str(extra)) if str(extra).isascii() else str(extra)
            extra_text = textwrap.shorten(extra_text, width=95, placeholder="...")
            ax_t.text(0.05, 0.26, extra_text, fontsize=9.5, color="#475569", transform=ax_t.transAxes)

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
    configure_matplotlib()
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
                ax_c.text(x + w / 2, 1.05, _chip_label(item, j), ha="center", va="center", color="white", fontsize=9)
        ax_t.clear()
        ax_t.axis("off")
        ax_t.text(0.02, 0.55, f"Step {snap.get('step', i)}", fontsize=11)
        extra = snap.get("extra", "")
        if extra and str(extra).isascii():
            ax_t.text(0.02, 0.12, ascii_plot(str(extra)), fontsize=10, color="#555")

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
    configure_matplotlib()
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
        ax_t.text(0.02, 0.55, f"Step {snap.get('step', i)}", fontsize=11)
        extra = snap.get("extra", "")
        if extra and str(extra).isascii():
            ax_t.text(0.02, 0.12, ascii_plot(str(extra)), fontsize=10, color="#555")

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

    configure_matplotlib()
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
        ax_t.text(0.02, 0.55, f"Step {snap.get('step', i)}", fontsize=10)

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
