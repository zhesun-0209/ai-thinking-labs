"""Matplotlib 中文字体 — 本地与 CI 一致，避免缺字乱码。"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.font_manager as fm


def _find_cjk_font() -> str | None:
    candidates = [
        "Noto Sans CJK SC",
        "Noto Sans SC",
        "Source Han Sans SC",
        "WenQuanYi Micro Hei",
        "PingFang SC",
        "Heiti SC",
        "STHeiti",
        "Arial Unicode MS",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            return name
    return None


def configure_matplotlib() -> None:
    """Notebook 首个绘图 cell 前调用一次。"""
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    warnings.filterwarnings("ignore", message=".*Glyph.*missing from font.*")
    warnings.filterwarnings("ignore", message=".*findfont.*")

    name = _find_cjk_font()
    if name:
        mpl.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
    else:
        mpl.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    mpl.rcParams["axes.unicode_minus"] = False
    mpl.rcParams["figure.dpi"] = 100


def use_ascii_on_axes(ax, title: str = "") -> None:
    """图表内仅用 ASCII 时设置标题（避免无 CJK 字体乱码）。"""
    if title:
        ax.set_title(title)
