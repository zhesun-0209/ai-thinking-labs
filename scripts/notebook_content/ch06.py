"""第 6 章 · 推理代码实验。"""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import flatten


DEPENDENCIES_CELL = """
# 载入本页会用到的数据表、队列和绘图工具。
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
# 动物分类专家系统：用规则把观察事实推到物种结论。
initial_facts = {"有毛发", "吃肉", "黄褐色", "有黑色条纹"}
goal = "老虎"

rules = [
    {"id": "R1", "facts": ["有毛发"], "then": "哺乳动物"},
    {"id": "R2", "facts": ["有奶"], "then": "哺乳动物"},
    {"id": "R3", "facts": ["有羽毛"], "then": "鸟类"},
    {"id": "R4", "facts": ["哺乳动物", "吃肉"], "then": "食肉动物"},
    {"id": "R5", "facts": ["哺乳动物", "有蹄"], "then": "有蹄类"},
    {"id": "R6", "facts": ["食肉动物", "黄褐色", "有黑色斑点"], "then": "猎豹"},
    {"id": "R7", "facts": ["食肉动物", "黄褐色", "有黑色条纹"], "then": "老虎"},
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
# 画出规则触发路径：每条规则一行，多前提规则会分层连到同一个规则节点。
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
        if len(rule["facts"]) == 1:
            premise_offsets = [0]
        else:
            center = (len(rule["facts"]) - 1) / 2
            premise_offsets = [(center - idx) * 0.22 for idx in range(len(rule["facts"]))]
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


draw_rule_flow(initial_facts, rules, forward_trace, "动物分类专家系统：前向链触发路径")
"""


KG_DATA_CELL = """
# Wikidata 风格知识图谱：三元组表示为 head-relation-tail。
triples = [
    ("玛丽·居里", "获得", "诺贝尔物理学奖"),
    ("玛丽·居里", "获得", "诺贝尔化学奖"),
    ("诺贝尔物理学奖", "类型", "诺贝尔奖"),
    ("诺贝尔化学奖", "类型", "诺贝尔奖"),
    ("玛丽·居里", "研究", "放射性"),
    ("放射性", "属于", "物理学"),
    ("物理学", "关联", "诺贝尔物理学奖"),
    ("玛丽·居里", "任职", "巴黎大学"),
    ("巴黎大学", "位于", "巴黎"),
    ("皮埃尔·居里", "合作", "玛丽·居里"),
]

start_entity = "玛丽·居里"
target_entity = "诺贝尔奖"

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
# 路径排序：更短路径优先；与目标语义更近的关系获得轻微加分。
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
    for path_id, path in enumerate(paths):
        hop_count = len(path)
        relation_bonus = sum(1 for edge in path if edge["relation"] in {"获得", "类型", "关联"})
        score = 1 / hop_count + 0.08 * relation_bonus
        rows.append({
            "path_id": path_id,
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
        "玛丽·居里": (0.25, 1.5),
        "诺贝尔物理学奖": (1.95, 2.25),
        "诺贝尔化学奖": (1.95, 0.78),
        "诺贝尔奖": (3.72, 1.5),
        "放射性": (1.88, 3.25),
        "物理学": (3.50, 3.25),
        "巴黎大学": (1.88, -0.05),
        "巴黎": (3.50, -0.05),
        "皮埃尔·居里": (0.22, 2.85),
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
        ax.scatter(x, y, s=1180, color=face, edgecolor=edge, linewidth=1.7, zorder=3)
        ax.text(x, y, node, ha="center", va="center", fontsize=8.8, fontweight="bold", color="#0f172a", zorder=4)

    ax.set_title("知识图谱多跳路径", loc="left", fontsize=14, fontweight="bold", color="#0f172a")
    ax.set_xlim(-0.35, 4.25)
    ax.set_ylim(-0.45, 3.65)
    ax.axis("off")
    plt.tight_layout()
    plt.show()


best_path = paths[int(ranked_paths.loc[0, "path_id"])]
draw_kg_path(triples, best_path)
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
            "本页用一个动物分类专家系统观察“事实如何触发规则”。前向链从已知事实往外推，后向链从目标倒推需要证明的条件；两种方向得到同一个结论，但过程完全不同。",
            ["构建动物分类规则库", "运行前向链和后向链", "展示推理轨迹与规则图"],
            "../ch6.html",
        ),
        rs.section("0", "规则库", "先看初始事实和规则表。每条规则都有一组前提和一个结论，推理过程就是不断检查“前提是否已经满足”。"),
        rs.code(DEPENDENCIES_CELL),
        rs.code(RULE_DATA_CELL),
        rs.section("1", "前向链", "前向链适合回答“这些事实还能推出什么”。它每一轮寻找可触发规则，把新结论加入已知事实集合。"),
        rs.code(FORWARD_CHAIN_CELL),
        rs.section("2", "后向链", "后向链适合回答“为了证明目标，还缺哪些条件”。它从目标出发，把目标拆成更小的子目标，直到命中初始事实。"),
        rs.code(BACKWARD_CHAIN_CELL),
        rs.section("3", "推理路径图", "图里每一行是一条被触发的规则。绿色是初始事实，蓝色是中间结论，橙色是最终目标。"),
        rs.code(RULE_PLOT_CELL),
    ]


def _graph() -> list:
    return [
        rs.chapter_link(
            "第 6 章 · 图谱多跳推理代码实验",
            "本页把人物、奖项、研究方向写成三元组图谱。读者要观察的不是普通 BFS，而是“每一跳关系是否符合查询意图”。",
            ["准备 Wikidata 风格三元组", "运行多跳查询", "展示路径排序与结果图"],
            "../ch6.html",
        ),
        rs.section("0", "知识图谱", "先看三元组表：head 是起点实体，relation 是关系类型，tail 是指向实体。多跳查询会沿着关系一层层展开。"),
        rs.code(DEPENDENCIES_CELL),
        rs.code(KG_DATA_CELL),
        rs.code(KG_ADJ_CELL),
        rs.section("1", "多跳查询", "查询过程会记录 frontier 和新增路径。读者重点看路径是如何从起点实体一步步抵达目标实体的。"),
        rs.code(GRAPH_REASONING_CELL),
        rs.section("2", "路径排序", "同一个目标可能有多条路径。这里把短路径和语义更贴近的关系排在前面，帮助读者理解为什么要给路径排序。"),
        rs.code(PATH_RANK_CELL),
        rs.section("3", "结果图", "最后只高亮最高分路径，避免整张图太拥挤。读者可以把它当作“多跳推理的证据链”。"),
        rs.code(KG_PLOT_CELL),
    ]
