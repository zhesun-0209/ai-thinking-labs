"""BPE byte-pair encoding demo — aligned with ch9.html BPE steps."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

BPE_PATH = Path(__file__).resolve().parent.parent / "common" / "luxun_bpe.json"


def load_bpe_spec() -> dict:
    with BPE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def count_pairs(tokens: list[str]) -> Counter[tuple[str, str]]:
    pairs: Counter[tuple[str, str]] = Counter()
    for i in range(len(tokens) - 1):
        pairs[(tokens[i], tokens[i + 1])] += 1
    return pairs


def merge_pair(tokens: list[str], pair: tuple[str, str], merged: str) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(tokens):
        if i < len(tokens) - 1 and (tokens[i], tokens[i + 1]) == pair:
            out.append(merged)
            i += 2
        else:
            out.append(tokens[i])
            i += 1
    return out


def run_bpe(tokens: list[str], merges: list[dict] | None = None) -> list[list[str]]:
    """Return token sequence after each merge step (including initial)."""
    history = [list(tokens)]
    spec_merges = merges or load_bpe_spec()["merges"]
    current = list(tokens)
    for step in spec_merges:
        pair = tuple(step["pair"])
        merged = step["result"]
        current = merge_pair(current, pair, merged)
        history.append(list(current))
    return history


def run_from_spec() -> list[list[str]]:
    spec = load_bpe_spec()
    return run_bpe(spec["initial_tokens"])


def steps_table() -> pd.DataFrame:
    spec = load_bpe_spec()
    history = run_from_spec()
    rows = [{"步骤": 0, "合并对": "—", "序列": " / ".join(history[0])}]
    for i, merge in enumerate(spec["merges"], start=1):
        pair = "+".join(merge["pair"])
        rows.append({"步骤": i, "合并对": f"{pair}({merge['count']}次)", "序列": " / ".join(history[i])})
    return pd.DataFrame(rows)


def demo_first_merge() -> None:
    spec = load_bpe_spec()
    tokens = list(spec["initial_tokens"])
    pairs = count_pairs(tokens)
    top = pairs.most_common(3)
    print("初始 token:", tokens)
    print("最高频 byte pair TOP3:")
    for (a, b), c in top:
        print(f"  ({a},{b}): {c} 次")
    first = spec["merges"][0]["pair"]
    print(f"\n第 1 次合并 {first} → {spec['merges'][0]['result']}")


def first_merge_table() -> pd.DataFrame:
    spec = load_bpe_spec()
    tokens = list(spec["initial_tokens"])
    pairs = count_pairs(tokens).most_common(3)
    rows = [{"项目": "初始 token", "内容": " / ".join(tokens)}]
    rows.extend({"项目": f"TOP{i} pair", "内容": f"{a}+{b}: {count} 次"} for i, ((a, b), count) in enumerate(pairs, start=1))
    first = spec["merges"][0]
    rows.append({"项目": "第 1 次合并", "内容": f"{'+'.join(first['pair'])} -> {first['result']}"})
    return pd.DataFrame(rows)


def codelens_bpe_merges() -> list:
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from common.codelens import Frame

    spec = load_bpe_spec()
    tokens = list(spec["initial_tokens"])
    frames = [
        Frame(
            0,
            "tokens = initial",
            "字符级切分",
            {"tokens": tokens, "pairs_top3": count_pairs(tokens).most_common(3)},
        ),
    ]
    history = run_bpe(tokens)
    for i, merge in enumerate(spec["merges"], start=1):
        pair = merge["pair"]
        frames.append(
            Frame(
                i,
                f"merge {pair} → {merge['result']}",
                f"第 {i} 次合并（频次 {merge['count']}）",
                {"合并对": pair, "合并后": history[i], "与网页一致": history[i] == merge["tokens_after"]},
            )
        )
    return frames


def animate_bpe_merges() -> None:
    from common.viz_anim import animate_items_row

    frames = codelens_bpe_merges()
    snaps = []
    for f in frames:
        tokens = f.state.get("合并后") or f.state.get("tokens") or []
        pair = f.state.get("合并对")
        merged = None
        if pair and isinstance(pair, (list, tuple)) and len(pair) == 2:
            merged = "".join(pair)
        snaps.append(
            {
                "step": f.step,
                "items": list(tokens) if isinstance(tokens, (list, tuple)) else [str(tokens)],
                "highlight": merged,
                "action": f.narrative,
            }
        )
    animate_items_row(snaps, title="BPE token sequence", fps=0.7)


def print_steps() -> None:
    spec = load_bpe_spec()
    history = run_from_spec()
    print(f"语料提示：{spec['corpus_hint']}\n")
    print("| 步骤 | 合并对 | 合并后 token 序列 | 与网页一致 |")
    print("|------|--------|-------------------|------------|")
    print(f"| 0 字符级 | — | {' / '.join(history[0])} | ✓ |")
    for i, merge in enumerate(spec["merges"], start=1):
        pair = "+".join(merge["pair"])
        tokens = " / ".join(history[i])
        ok = history[i] == merge["tokens_after"]
        print(f"| {i} | {pair}（{merge['count']} 次） | {tokens} | {'✓' if ok else '✗'} |")
    final_ok = history[-1] == spec["final_tokens"]
    print(f"\n最终子词表：{' / '.join(history[-1])}  ({'✓ 与网页一致' if final_ok else '✗ 不一致'})")


if __name__ == "__main__":
    print("BPE 字节对合并 — Python 复现（与 ch9 网页同一案例）\n")
    print_steps()
