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


def codelens_forward_chain(max_steps: int = 10) -> list:
    """前向链每一轮：已知事实集 + 新推导。"""
    from common.codelens import Frame

    data = load_rules()
    known = set(data["facts"])
    frames = [
        Frame(0, "known = facts", "初始化", {"known": sorted(known), "goal": data["goal"]}),
    ]
    step = 0
    for round_i in range(1, max_steps + 1):
        added = []
        for rule in data["rules"]:
            cond = rule["if"][0]
            var = cond[cond.index("(") + 1 : cond.index(")")]
            inst = cond.replace(f"({var})", "(苏格拉底)")
            if inst in known:
                concl = rule["then"].replace(f"({var})", "(苏格拉底)")
                if concl not in known:
                    known.add(concl)
                    added.append(f"{rule['id']}: {inst} ⇒ {concl}")
        if not added:
            break
        step += 1
        frames.append(
            Frame(
                step,
                f"round {round_i} scan rules",
                f"第 {round_i} 轮触发 {len(added)} 条规则",
                {"新增": added, "known": sorted(known)},
            )
        )
    frames.append(
        Frame(
            step + 1,
            "check goal",
            "检查目标是否在 known 中",
            {"goal": data["goal"], " proved": data["goal"] in known},
        )
    )
    return frames


def animate_forward_chain() -> None:
    from common.viz_anim import animate_items_row

    frames = codelens_forward_chain()
    snaps = []
    for f in frames:
        known = f.state.get("known", [])
        if isinstance(known, (list, tuple)):
            items = [str(x) for x in known]
        else:
            items = []
        new_items = f.state.get("新增", [])
        highlight = None
        if new_items and isinstance(new_items, list) and new_items:
            highlight = str(new_items[-1]).split(":")[-1].strip() if ":" in str(new_items[-1]) else None
        snaps.append(
            {
                "step": f.step,
                "items": items,
                "highlight": highlight,
                "action": f.narrative,
                "extra": "; ".join(str(x) for x in new_items) if new_items else "",
            }
        )
    animate_items_row(snaps, title="Known facts (forward chain)")


def path_ranking() -> None:
    kg = load_kg()
    scores = kg["path_scores"]
    print("| 路径 | 得分 |")
    print("|------|------|")
    for path, sc in scores.items():
        print(f"| {path} | {sc} |")
    print(f"\n最高分路径: {max(scores, key=scores.get)}")
