"""Chapter 6 reasoning demos — aligned with ch6.js."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

COMMON = Path(__file__).resolve().parent.parent / "common"


def load_rules():
    with (COMMON / "ch6_rules.json").open(encoding="utf-8") as f:
        return json.load(f)


def load_kg():
    with (COMMON / "ch6_kg.json").open(encoding="utf-8") as f:
        return json.load(f)


def forward_chain(max_steps: int = 10) -> list[str]:
    data = load_rules()
    known = set(data["facts"])
    log = [f"初始事实: {', '.join(sorted(known))}"]
    for step in range(1, max_steps + 1):
        added = []
        for rule in data["rules"]:
            cond = rule["if"][0]
            pred = cond.split("(")[0]
            var = cond[cond.index("(") + 1 : cond.index(")")]
            inst = cond.replace(f"({var})", "(苏格拉底)")
            if inst in known:
                concl = rule["then"].replace(f"({var})", "(苏格拉底)")
                if concl not in known:
                    known.add(concl)
                    added.append(f"{rule['id']}: {inst} ⇒ {concl}")
        if not added:
            break
        log.append(f"第 {step} 轮: " + "; ".join(added))
    log.append(f"目标 {data['goal']}: {'✓' if data['goal'] in known else '✗'}")
    return log


def backward_chain() -> list[str]:
    data = load_rules()
    goal = data["goal"]
    log = [f"目标: {goal}"]
    sub = goal.replace("终有一死", "会死")
    log.append(f"子目标: {sub} (R2)")
    sub2 = sub.replace("会死", "人")
    log.append(f"子目标: {sub2} (R1)")
    log.append(f"匹配事实: {sub2 in data['facts']} → 证明成立")
    return log


def build_adj(kg: dict) -> dict[str, list[tuple[str, str]]]:
    adj: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for h, r, t in kg["edges"]:
        adj[h].append((r, t))
    return adj


def graph_multihop() -> list[str]:
    kg = load_kg()
    adj = build_adj(kg)
    works = [t for rel, t in adj["鲁迅"] if rel == "创作"]
    lines = [f"鲁迅创作: {', '.join(works)}"]
    venues = {w: [t for rel, t in adj[w] if rel == "发表于"] for w in works}
    for w, vs in venues.items():
        lines.append(f"{w} 发表于: {', '.join(vs)}")
    ans = kg["query"]["answer_y"]
    ok = all(ans in vs for vs in venues.values())
    lines.append(f"共同发表于 {ans}: {'✓' if ok else '✗'}")
    return lines


def path_ranking() -> None:
    kg = load_kg()
    scores = kg["path_scores"]
    print("| 路径 | 得分 |")
    print("|------|------|")
    for path, sc in scores.items():
        print(f"| {path} | {sc} |")
    print(f"\n最高分路径: {max(scores, key=scores.get)}")
