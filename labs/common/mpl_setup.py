"""Matplotlib font setup for notebook figures."""

from __future__ import annotations

import logging
import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.font_manager as fm

# Prefer one fixed CJK face in rendered site; keep local fallbacks for downloaded notebooks.
CJK_FONT = "Noto Sans CJK SC"

_FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

_CJK_NAMES = [
    CJK_FONT,
    "Noto Sans SC",
    "Source Han Sans SC",
    "PingFang SC",
    "Heiti SC",
    "STHeiti",
    "Arial Unicode MS",
    "WenQuanYi Micro Hei",
]

_CONFIGURED = False


def _register_font_files() -> str | None:
    registered: list[str] = []
    for path in _FONT_PATHS:
        p = Path(path)
        if not p.is_file():
            continue
        try:
            fm.fontManager.addfont(str(p))
            prop = fm.FontProperties(fname=str(p))
            name = prop.get_name()
            if name and name not in registered:
                registered.append(name)
        except Exception:
            continue
    return registered[0] if registered else None


def _find_cjk_font() -> str | None:
    from_file = _register_font_files()
    available = {f.name for f in fm.fontManager.ttflist}
    if CJK_FONT in available:
        return CJK_FONT
    if from_file:
        return from_file
    for name in _CJK_NAMES:
        if name in available:
            return name
    return None


def configure_matplotlib() -> None:
    """Notebook 首个绘图 cell 前调用一次。"""
    global _CONFIGURED
    if _CONFIGURED:
        return
    _CONFIGURED = True

    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    warnings.filterwarnings("ignore", message=".*Glyph.*missing from font.*")
    warnings.filterwarnings("ignore", message=".*findfont.*")

    name = _find_cjk_font()
    if name:
        mpl.rcParams["font.sans-serif"] = [name, "DejaVu Sans", "sans-serif"]
        mpl.rcParams["font.family"] = "sans-serif"
    else:
        mpl.rcParams["font.sans-serif"] = ["DejaVu Sans", "sans-serif"]
    mpl.rcParams["axes.unicode_minus"] = False
    mpl.rcParams["figure.dpi"] = 100
    mpl.rcParams["mathtext.default"] = "regular"


def ascii_plot(text: str) -> str:
    """把常见数学符号换成 DejaVu 可显示的 ASCII（用于轴标签/GIF）。"""
    repl = {
        "α": "alpha",
        "β": "beta",
        "γ": "gamma",
        "δ": "delta",
        "ε": "eps",
        "σ": "sigma",
        "ŷ": "y_hat",
        "₁": "1",
        "₂": "2",
        "₃": "3",
        "→": "->",
    }
    out = text
    for k, v in repl.items():
        out = out.replace(k, v)
    return out
