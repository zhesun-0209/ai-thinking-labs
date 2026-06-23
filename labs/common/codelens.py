"""CodeLens-style execution frames — print every variable change."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Frame:
    step: int
    line: str
    narrative: str
    state: dict[str, Any] = field(default_factory=dict)

    def print(self) -> None:
        print(f"── Step {self.step} ── {self.narrative}")
        print(f"   执行: {self.line}")
        for k, v in self.state.items():
            print(f"   {k} = {v!r}")


def print_frames(frames: list[Frame], start: int = 0, stop: int | None = None) -> None:
    for f in frames[start:stop]:
        f.print()
        print()


def frames_to_table(frames: list[Frame], keys: list[str]) -> "pd.DataFrame":
    import pandas as pd

    rows = []
    for f in frames:
        row = {"步": f.step, "说明": f.narrative}
        for k in keys:
            row[k] = f.state.get(k, "")
        rows.append(row)
    return pd.DataFrame(rows)
