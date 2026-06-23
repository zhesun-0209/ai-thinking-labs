"""BPE byte-pair encoding demo — aligned with ch9.html BPE steps."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

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
