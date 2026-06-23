"""Chapter 6 reasoning demos — aligned with ch6.js."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

COMMON = Path(__file__).resolve().parent.parent / "common"


def load_rules():
    with (COMMON / "ch6_rules.json").open(encoding="utf-8") as f:
        return json.load(f)


def load_kg():
    with (COMMON / "ch6_kg.json").open(encoding="utf-8") as f:
        return json.load(f)


def facts_goal_table() -> pd.DataFrame:
    data = load_rules()
    return pd.DataFrame(
        [
            {"项目": "初始事实", "内容": "；".join(data["facts"])},
            {"项目": "证明目标", "内容": data["goal"]},
        ]
    )


def rules_table() -> pd.DataFrame:
    data = load_rules()
    return pd.DataFrame(
        [
            {"规则": rule["id"], "IF": " AND ".join(rule["if"]), "THEN": rule["then"]}
            for rule in data["rules"]
        ]
    )


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


def backward_chain_table() -> pd.DataFrame:
    data = load_rules()
    goal = data["goal"]
    sub = goal.replace("终有一死", "会死")
    sub2 = sub.replace("会死", "人")
    return pd.DataFrame(
        [
            {"步": 1, "当前目标": goal, "使用规则": "R2", "下一子目标": sub, "结果": "继续证明"},
            {"步": 2, "当前目标": sub, "使用规则": "R1", "下一子目标": sub2, "结果": "继续证明"},
            {"步": 3, "当前目标": sub2, "使用规则": "事实库", "下一子目标": "—", "结果": "证明成立"},
        ]
    )


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


def kg_query_table() -> pd.DataFrame:
    kg = load_kg()
    return pd.DataFrame(
        [
            {"项目": "查询模板", "内容": kg["query"]["pattern"]},
            {"项目": "答案 Y", "内容": kg["query"]["answer_y"]},
        ]
    )


def graph_edges_table() -> pd.DataFrame:
    kg = load_kg()
    return pd.DataFrame([{"头实体": h, "关系": r, "尾实体": t} for h, r, t in kg["edges"]])


def entity_out_edges(entity: str) -> pd.DataFrame:
    kg = load_kg()
    adj = build_adj(kg)
    return pd.DataFrame([{"实体": entity, "关系": r, "指向": t} for r, t in adj[entity]])


def graph_multihop_table() -> pd.DataFrame:
    kg = load_kg()
    adj = build_adj(kg)
    works = [t for rel, t in adj["鲁迅"] if rel == "创作"]
    rows = [{"跳数": 1, "输入": "鲁迅", "关系约束": "创作", "候选": "；".join(works)}]
    venues = {w: [t for rel, t in adj[w] if rel == "发表于"] for w in works}
    for w, vs in venues.items():
        rows.append({"跳数": 2, "输入": w, "关系约束": "发表于", "候选": "；".join(vs)})
    ans = kg["query"]["answer_y"]
    ok = all(ans in vs for vs in venues.values())
    rows.append({"跳数": "汇总", "输入": "所有作品", "关系约束": "共同 Y", "候选": f"{ans} {'✓' if ok else '✗'}"})
    return pd.DataFrame(rows)


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


def forward_chain_table() -> pd.DataFrame:
    rows = []
    for frame in codelens_forward_chain():
        added = frame.state.get("新增", [])
        known = frame.state.get("known", [])
        rows.append(
            {
                "步": frame.step,
                "动作": frame.narrative,
                "新增事实": "；".join(added) if isinstance(added, list) else "",
                "事实数": len(known) if isinstance(known, list) else "",
                "目标成立": frame.state.get(" proved", ""),
            }
        )
    return pd.DataFrame(rows)


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


def path_ranking_table() -> pd.DataFrame:
    kg = load_kg()
    rows = [{"路径": path, "得分": score} for path, score in kg["path_scores"].items()]
    return pd.DataFrame(rows).sort_values("得分", ascending=False)


def plot_path_ranking() -> None:
    table = path_ranking_table()
    fig, ax = plt.subplots(figsize=(7, 2.6))
    ax.barh(table["路径"], table["得分"], color="#0d6b62")
    ax.invert_yaxis()
    ax.set_xlabel("score")
    ax.set_title("KG path ranking")
    plt.tight_layout()
    plt.show()
