"""Notebook cell builders."""

from __future__ import annotations

Cell = tuple[str, str]  # ("md"|"code", source)


def md(text: str) -> Cell:
    return ("md", text.strip())


def code(text: str) -> Cell:
    return ("code", text.strip())


def section(title: str, body: str = "") -> Cell:
    return md(f"## {title}\n\n{body}".strip())


def callout(kind: str, text: str) -> Cell:
    icons = {"预测": "🤔", "误区": "⚠️", "自测": "✅", "小结": "📌", "目标": "🎯"}
    return md(f"**{icons.get(kind, '💡')} {kind}** · {text}")


def all_notebooks() -> dict[str, list[Cell]]:
    from notebook_content import ch05, ch06, ch07, ch08

    return {
        **ch05.notebooks(),
        **ch06.notebooks(),
        **ch07.notebooks(),
        **ch08.notebooks(),
    }
