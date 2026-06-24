"""第 6 章 · 推理代码实验。"""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import flatten


DEPENDENCIES_CELL = """
# 导入实验库，并设置图表中文显示。
import importlib.util
import logging
import subprocess
import sys
import warnings
from collections import defaultdict, deque
from pathlib import Path

required_packages = {
    "pandas": "pandas>=2.0",
    "matplotlib": "matplotlib>=3.7",
}
missing = [package for module, package in required_packages.items() if importlib.util.find_spec(module) is None]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from IPython.display import display

font_paths = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
]
font_name = "DejaVu Sans"
for path in font_paths:
    if Path(path).exists():
        fm.fontManager.addfont(path)
        font_name = fm.FontProperties(fname=path).get_name()
        break

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")
plt.rcParams.update({
    "figure.dpi": 110,
    "axes.unicode_minus": False,
    "font.family": "sans-serif",
    "font.sans-serif": [font_name, "DejaVu Sans", "sans-serif"],
})
"""


RULE_DATA_CELL = """
# 准备一组可追踪的规则：每条规则由前提 facts 和结论 then 组成。
initial_facts = {"今天下雨", "有雨伞", "需要外出"}
goal = "适合带伞出门"

rules = [
    {"id": "R1", "facts": ["今天下雨"], "then": "路面湿"},
    {"id": "R2", "facts": ["今天下雨", "需要外出"], "then": "可能淋湿"},
    {"id": "R3", "facts": ["可能淋湿", "有雨伞"], "then": "适合带伞出门"},
    {"id": "R4", "facts": ["路面湿"], "then": "行走速度变慢"},
]

facts_df = pd.DataFrame({"初始事实": sorted(initial_facts)})
rules_df = pd.DataFrame(
    [
        {"规则": rule["id"], "前提": " + ".join(rule["facts"]), "结论": rule["then"]}
        for rule in rules
    ]
)

display(facts_df)
display(rules_df)
"""


FORWARD_CHAIN_CELL = """
# 前向链：从已知事实出发，反复触发前提已满足的规则。
def forward_chain(initial_facts, rules, goal):
    known = set(initial_facts)
    fired = set()
    rows = []
    round_id = 0

    while True:
        candidates = []
        for rule in rules:
            if rule["id"] in fired:
                continue
            missing = [fact for fact in rule["facts"] if fact not in known]
            if not missing:
                candidates.append(rule)

        if not candidates:
            break

        for rule in candidates:
            round_id += 1
            before = set(known)
            known.add(rule["then"])
            fired.add(rule["id"])
            rows.append({
                "轮次": round_id,
                "触发规则": rule["id"],
                "前提": " + ".join(rule["facts"]),
                "新增事实": rule["then"] if rule["then"] not in before else "已存在",
                "已知事实": "、".join(sorted(known)),
                "达到目标": rule["then"] == goal or goal in known,
            })
            if goal in known:
                return known, pd.DataFrame(rows)

    return known, pd.DataFrame(rows)


forward_facts, forward_trace = forward_chain(initial_facts, rules, goal)
display(forward_trace)
print("推理结果:", goal in forward_facts)
"""


BACKWARD_CHAIN_CELL = """
# 后向链：从目标倒推需要哪些前提，再逐个证明这些前提。
def backward_chain(goal, initial_facts, rules):
    rows = []
    active = set()

    def prove(target, depth=0):
        if target in initial_facts:
            rows.append({
                "深度": depth,
                "待证明": target,
                "使用规则": "初始事实",
                "子目标": "",
                "结论": "成立",
            })
            return True

        if target in active:
            rows.append({
                "深度": depth,
                "待证明": target,
                "使用规则": "循环依赖",
                "子目标": "",
                "结论": "失败",
            })
            return False

        active.add(target)
        matched = [rule for rule in rules if rule["then"] == target]
        if not matched:
            active.remove(target)
            rows.append({
                "深度": depth,
                "待证明": target,
                "使用规则": "无可用规则",
                "子目标": "",
                "结论": "失败",
            })
            return False

        for rule in matched:
            subgoals = rule["facts"]
            ok = all(prove(item, depth + 1) for item in subgoals)
            rows.append({
                "深度": depth,
                "待证明": target,
                "使用规则": rule["id"],
                "子目标": "、".join(subgoals),
                "结论": "成立" if ok else "失败",
            })
            if ok:
                active.remove(target)
                return True

        active.remove(target)
        return False

    success = prove(goal)
    trace = pd.DataFrame(rows)
    return success, trace.sort_index(ascending=False).reset_index(drop=True)


backward_success, backward_trace = backward_chain(goal, initial_facts, rules)
display(backward_trace)
print("推理结果:", backward_success)
"""


RULE_PLOT_CELL = """
# 画出规则触发路径：每条规则一行，避免交叉线影响阅读。
def draw_rule_flow(initial_facts, rules, trace, title):
    if "触发规则" in trace:
        used_order = [rid for rid in trace["触发规则"].tolist() if str(rid).startswith("R")]
    else:
        used_order = [rid for rid in trace.get("使用规则", []).tolist() if str(rid).startswith("R")]
    used_order = list(dict.fromkeys(used_order))
    selected_rules = [rule for rid in used_order for rule in rules if rule["id"] == rid]

    fig, ax = plt.subplots(figsize=(10.8, 5.0))
    ax.set_facecolor("#fbfcfd")

    def chip_style(text, role):
        if role == "initial":
            return {"fc": "#dcfce7", "ec": "#16a34a"}
        if role == "goal":
            return {"fc": "#ffedd5", "ec": "#f97316"}
        if role == "derived":
            return {"fc": "#eff6ff", "ec": "#2563eb"}
        return {"fc": "#ffffff", "ec": "#94a3b8"}

    def draw_chip(x, y, text, role):
        style = chip_style(text, role)
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=9.2,
            color="#0f172a",
            zorder=5,
            bbox={
                "boxstyle": "round,pad=0.38",
                "fc": style["fc"],
                "ec": style["ec"],
                "lw": 1.45,
            },
        )

    def fact_role(fact, conclusion=False):
        if fact == goal:
            return "goal"
        if fact in initial_facts:
            return "initial"
        if conclusion:
            return "derived"
        return "other"

    y_positions = list(reversed(range(len(selected_rules))))
    for row_index, (rule, y) in enumerate(zip(selected_rules, y_positions), start=1):
        ax.axhspan(y - 0.46, y + 0.46, color="#f8fafc" if row_index % 2 else "#ffffff", zorder=0)
        premise_offsets = [0] if len(rule["facts"]) == 1 else [0.2, -0.2]
        for fact, offset in zip(rule["facts"], premise_offsets):
            fy = y + offset
            draw_chip(0.56, fy, fact, fact_role(fact))
            ax.annotate(
                "",
                xy=(1.78, y),
                xytext=(1.10, fy),
                arrowprops={"arrowstyle": "-|>", "color": "#64748b", "lw": 2.0, "shrinkA": 6, "shrinkB": 8},
                zorder=2,
            )

        ax.text(
            2.08,
            y,
            rule["id"],
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="#1e3a8a",
            zorder=5,
            bbox={"boxstyle": "round,pad=0.42", "fc": "#dbeafe", "ec": "#2563eb", "lw": 1.7},
        )
        ax.annotate(
            "",
            xy=(3.28, y),
            xytext=(2.38, y),
            arrowprops={"arrowstyle": "-|>", "color": "#2563eb", "lw": 2.5, "shrinkA": 8, "shrinkB": 8},
            zorder=2,
        )
        draw_chip(3.9, y, rule["then"], fact_role(rule["then"], conclusion=True))

    ax.text(0.56, len(selected_rules) - 0.24, "前提", ha="center", fontweight="bold", color="#334155")
    ax.text(2.08, len(selected_rules) - 0.24, "规则", ha="center", fontweight="bold", color="#334155")
    ax.text(3.9, len(selected_rules) - 0.24, "结论", ha="center", fontweight="bold", color="#334155")
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color="#0f172a")
    ax.set_xlim(-0.18, 4.55)
    ax.set_ylim(-0.65, len(selected_rules) - 0.02)
    ax.axis("off")
    plt.tight_layout()
    plt.show()


draw_rule_flow(initial_facts, rules, forward_trace, "前向链触发路径")
"""


KG_DATA_CELL = """
# 准备小型知识图谱：三元组表示为 head-relation-tail。
triples = [
    ("鲁迅", "创作", "《呐喊》"),
    ("鲁迅", "创作", "《彷徨》"),
    ("《呐喊》", "收录", "《狂人日记》"),
    ("《呐喊》", "主题", "国民性批判"),
    ("《狂人日记》", "体裁", "小说"),
    ("《彷徨》", "收录", "《祝福》"),
    ("《祝福》", "人物", "祥林嫂"),
    ("鲁迅", "身份", "作家"),
    ("作家", "关联", "文学作品"),
]

start_entity = "鲁迅"
target_entity = "祥林嫂"

kg_df = pd.DataFrame(triples, columns=["head", "relation", "tail"])
display(kg_df)
"""


KG_ADJ_CELL = """
# 把三元组转成邻接表，保留关系名称，便于输出可读路径。
kg_adj = defaultdict(list)
for head, relation, tail in triples:
    kg_adj[head].append((tail, relation))

out_edges = pd.DataFrame(
    [
        {"实体": start_entity, "关系": relation, "指向": tail}
        for tail, relation in kg_adj[start_entity]
    ]
)
display(out_edges)
"""


GRAPH_REASONING_CELL = """
# 多跳查询：用队列逐层展开，记录每一步 frontier 和新路径。
def find_paths(start, target, kg_adj, max_hops=3):
    queue = deque([(start, [])])
    rows = []
    paths = []
    step = 0

    while queue:
        step += 1
        entity, path = queue.popleft()
        frontier_before = [item[0] for item in queue]

        if len(path) >= max_hops:
            rows.append({
                "步骤": step,
                "展开实体": entity,
                "frontier": "、".join(frontier_before) or "空",
                "新增路径": "达到跳数上限",
            })
            continue

        new_items = []
        for nxt, relation in kg_adj.get(entity, []):
            if any(edge["tail"] == nxt for edge in path):
                continue
            new_path = path + [{"head": entity, "relation": relation, "tail": nxt}]
            new_items.append(f"{entity}-{relation}->{nxt}")
            if nxt == target:
                paths.append(new_path)
            else:
                queue.append((nxt, new_path))

        rows.append({
            "步骤": step,
            "展开实体": entity,
            "frontier": "、".join(frontier_before) or "空",
            "新增路径": "；".join(new_items) or "无",
        })

    return paths, pd.DataFrame(rows)


paths, graph_trace = find_paths(start_entity, target_entity, kg_adj, max_hops=3)
display(graph_trace)
"""


PATH_RANK_CELL = """
# 路径排序：更短路径优先；含有目标人物关系的路径获得轻微加分。
def path_to_text(path):
    if not path:
        return ""
    pieces = [path[0]["head"]]
    for edge in path:
        pieces.append(f"-{edge['relation']}->")
        pieces.append(edge["tail"])
    return "".join(pieces)


def rank_paths(paths):
    rows = []
    for path in paths:
        hop_count = len(path)
        relation_bonus = sum(1 for edge in path if edge["relation"] in {"人物", "收录"})
        score = 1 / hop_count + 0.08 * relation_bonus
        rows.append({
            "路径": path_to_text(path),
            "跳数": hop_count,
            "关系加分": round(0.08 * relation_bonus, 2),
            "排序分": round(score, 3),
        })
    return pd.DataFrame(rows).sort_values("排序分", ascending=False).reset_index(drop=True)


ranked_paths = rank_paths(paths)
display(ranked_paths)
"""


KG_PLOT_CELL = """
# 绘制最高分路径：突出多跳推理经过的实体和关系。
def draw_kg_path(triples, best_path):
    nodes = sorted(set([h for h, _, _ in triples] + [t for _, _, t in triples]))
    layout = {
        "鲁迅": (0.1, 1.2),
        "《呐喊》": (1.45, 1.8),
        "《彷徨》": (1.45, 0.62),
        "《狂人日记》": (2.8, 2.2),
        "国民性批判": (2.9, 1.42),
        "《祝福》": (2.82, 0.62),
        "祥林嫂": (4.12, 0.62),
        "作家": (1.45, 2.75),
        "文学作品": (2.85, 2.75),
        "小说": (4.12, 2.2),
    }
    active = {(edge["head"], edge["relation"], edge["tail"]) for edge in best_path}
    active_nodes = {edge["head"] for edge in best_path} | {edge["tail"] for edge in best_path}

    fig, ax = plt.subplots(figsize=(9.5, 5.0))
    ax.set_facecolor("#fbfcfd")
    for head, relation, tail in triples:
        x1, y1 = layout[head]
        x2, y2 = layout[tail]
        is_active = (head, relation, tail) in active
        ax.annotate(
            "",
            xy=(x2 - 0.18, y2),
            xytext=(x1 + 0.18, y1),
            arrowprops={
                "arrowstyle": "->",
                "color": "#2563eb" if is_active else "#cbd5e1",
                "lw": 2.4 if is_active else 1.4,
            },
            zorder=1,
        )
        ax.text(
            (x1 + x2) / 2,
            (y1 + y2) / 2 + 0.08,
            relation,
            ha="center",
            va="center",
            fontsize=8,
            color="#1d4ed8" if is_active else "#64748b",
            bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "#e2e8f0"},
            zorder=2,
        )

    for node in nodes:
        x, y = layout[node]
        is_active = node in active_nodes
        face = "#eff6ff" if is_active else "#ffffff"
        edge = "#2563eb" if is_active else "#94a3b8"
        if node == start_entity:
            face, edge = "#dcfce7", "#16a34a"
        if node == target_entity:
            face, edge = "#ffedd5", "#f97316"
        ax.scatter(x, y, s=1050, color=face, edgecolor=edge, linewidth=1.7, zorder=3)
        ax.text(x, y, node, ha="center", va="center", fontsize=9, fontweight="bold", color="#0f172a", zorder=4)

    ax.set_title("知识图谱路径", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
    ax.set_xlim(-0.35, 4.55)
    ax.set_ylim(0.18, 3.15)
    ax.axis("off")
    plt.tight_layout()
    plt.show()


draw_kg_path(triples, paths[ranked_paths.index[0]])
"""


def notebooks() -> dict[str, list]:
    return {
        "ch06_forward_backward_chain.ipynb": flatten(_forward()),
        "ch06_graph_reasoning.ipynb": flatten(_graph()),
    }


def _forward() -> list:
    return [
        rs.chapter_link(
            "第 6 章 · 规则链推理代码实验",
            ["准备事实与规则表", "运行前向链和后向链", "展示推理轨迹与规则图"],
            "../ch6.html",
        ),
        rs.section("0", "环境与数据"),
        rs.code(DEPENDENCIES_CELL),
        rs.code(RULE_DATA_CELL),
        rs.section("1", "前向链"),
        rs.code(FORWARD_CHAIN_CELL),
        rs.section("2", "后向链"),
        rs.code(BACKWARD_CHAIN_CELL),
        rs.section("3", "推理路径图"),
        rs.code(RULE_PLOT_CELL),
    ]


def _graph() -> list:
    return [
        rs.chapter_link(
            "第 6 章 · 图谱多跳推理代码实验",
            ["准备三元组图谱", "运行多跳查询", "展示路径排序与结果图"],
            "../ch6.html",
        ),
        rs.section("0", "环境与数据"),
        rs.code(DEPENDENCIES_CELL),
        rs.code(KG_DATA_CELL),
        rs.code(KG_ADJ_CELL),
        rs.section("1", "多跳查询"),
        rs.code(GRAPH_REASONING_CELL),
        rs.section("2", "路径排序"),
        rs.code(PATH_RANK_CELL),
        rs.section("3", "结果图"),
        rs.code(KG_PLOT_CELL),
    ]
