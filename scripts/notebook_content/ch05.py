"""第 5 章 · 经典图搜索 — 可执行代码实验。"""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import flatten


DEPENDENCIES_CELL = """
# 载入本页会用到的数据处理、队列和绘图工具。
import importlib.util
import logging
import subprocess
import sys
import warnings
from collections import deque
import heapq
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


CAMPUS_GRAPH_CELL = """
# AIMA Romania map：从 Arad 搜索到 Bucharest。
graph = {
    "start": "Arad",
    "goal": "Bucharest",
    "nodes": {
        "Arad": {"name": "Arad", "h": 366},
        "Zerind": {"name": "Zerind", "h": 374},
        "Oradea": {"name": "Oradea", "h": 380},
        "Sibiu": {"name": "Sibiu", "h": 253},
        "Timisoara": {"name": "Timisoara", "h": 329},
        "Lugoj": {"name": "Lugoj", "h": 244},
        "Mehadia": {"name": "Mehadia", "h": 241},
        "Dobreta": {"name": "Dobreta", "h": 242},
        "Craiova": {"name": "Craiova", "h": 160},
        "Rimnicu Vilcea": {"name": "Rimnicu Vilcea", "h": 193},
        "Fagaras": {"name": "Fagaras", "h": 176},
        "Pitesti": {"name": "Pitesti", "h": 100},
        "Bucharest": {"name": "Bucharest", "h": 0},
        "Giurgiu": {"name": "Giurgiu", "h": 77},
        "Urziceni": {"name": "Urziceni", "h": 80},
        "Hirsova": {"name": "Hirsova", "h": 151},
        "Eforie": {"name": "Eforie", "h": 161},
        "Vaslui": {"name": "Vaslui", "h": 199},
        "Iasi": {"name": "Iasi", "h": 226},
        "Neamt": {"name": "Neamt", "h": 234},
    },
    "edges": [
        {"from": "Arad", "to": "Zerind", "cost": 75},
        {"from": "Arad", "to": "Sibiu", "cost": 140},
        {"from": "Arad", "to": "Timisoara", "cost": 118},
        {"from": "Zerind", "to": "Oradea", "cost": 71},
        {"from": "Oradea", "to": "Sibiu", "cost": 151},
        {"from": "Timisoara", "to": "Lugoj", "cost": 111},
        {"from": "Lugoj", "to": "Mehadia", "cost": 70},
        {"from": "Mehadia", "to": "Dobreta", "cost": 75},
        {"from": "Dobreta", "to": "Craiova", "cost": 120},
        {"from": "Craiova", "to": "Rimnicu Vilcea", "cost": 146},
        {"from": "Craiova", "to": "Pitesti", "cost": 138},
        {"from": "Sibiu", "to": "Fagaras", "cost": 99},
        {"from": "Sibiu", "to": "Rimnicu Vilcea", "cost": 80},
        {"from": "Rimnicu Vilcea", "to": "Pitesti", "cost": 97},
        {"from": "Fagaras", "to": "Bucharest", "cost": 211},
        {"from": "Pitesti", "to": "Bucharest", "cost": 101},
        {"from": "Bucharest", "to": "Giurgiu", "cost": 90},
        {"from": "Bucharest", "to": "Urziceni", "cost": 85},
        {"from": "Urziceni", "to": "Hirsova", "cost": 98},
        {"from": "Hirsova", "to": "Eforie", "cost": 86},
        {"from": "Urziceni", "to": "Vaslui", "cost": 142},
        {"from": "Vaslui", "to": "Iasi", "cost": 92},
        {"from": "Iasi", "to": "Neamt", "cost": 87},
    ],
}

start = graph["start"]
goal = graph["goal"]
h = {node: meta["h"] for node, meta in graph["nodes"].items()}
print("起点:", start, "终点:", goal)
"""


ADJACENCY_CELL = """
# 把边表转成邻接表：搜索算法只需要知道“当前节点能走向哪些邻居”。
adj = {}
for edge in graph["edges"]:
    a = edge["from"]
    b = edge["to"]
    cost = edge["cost"]
    adj.setdefault(a, []).append((b, cost))
    adj.setdefault(b, []).append((a, cost))

for neighbors in adj.values():
    neighbors.sort(key=lambda item: item[0])

adj
"""


TABLES_CELL = """
# 节点表给出直线距离启发式 h，边表给出相邻城市距离。
nodes_df = pd.DataFrame(
    [
        {"节点": node, "名称": meta["name"], "h(到 Bucharest)": meta["h"]}
        for node, meta in graph["nodes"].items()
    ]
).sort_values("节点")

edges_df = pd.DataFrame(
    [
        {"边": f"{edge['from']}↔{edge['to']}", "代价": edge["cost"]}
        for edge in graph["edges"]
    ]
)

display(nodes_df)
display(edges_df)
"""


DRAWING_CELL = """
# 绘制 Romania map：高亮已展开节点和最终路线。
layout = {
    "Arad": (0.45, 3.25),
    "Zerind": (0.25, 4.18),
    "Oradea": (1.02, 5.02),
    "Sibiu": (2.15, 3.52),
    "Timisoara": (0.38, 2.02),
    "Lugoj": (1.25, 1.32),
    "Mehadia": (1.28, 0.52),
    "Dobreta": (1.62, -0.22),
    "Craiova": (2.95, -0.12),
    "Rimnicu Vilcea": (3.12, 2.35),
    "Fagaras": (4.15, 3.55),
    "Pitesti": (4.42, 1.42),
    "Bucharest": (5.82, 1.18),
    "Giurgiu": (5.58, 0.10),
    "Urziceni": (6.82, 1.90),
    "Hirsova": (7.85, 2.06),
    "Eforie": (8.28, 1.18),
    "Vaslui": (7.55, 3.12),
    "Iasi": (7.25, 4.18),
    "Neamt": (6.45, 4.88),
}


def edge_key(a, b):
    return tuple(sorted((a, b)))


def path_edges(path):
    return {edge_key(path[i], path[i + 1]) for i in range(len(path) - 1)}


def draw_search_result(path=None, trace=None, title="罗马尼亚路线图搜索"):
    path = path or []
    active_edges = path_edges(path)
    visited_nodes = set(path)
    if trace is not None and not trace.empty:
        visited_nodes.update(trace["取出节点"].tolist())

    fig, ax = plt.subplots(figsize=(11.4, 6.4))
    ax.set_facecolor("#fbfcfd")

    drawn_edges = set()
    for a, neighbors in adj.items():
        for b, cost in neighbors:
            key = edge_key(a, b)
            if key in drawn_edges:
                continue
            drawn_edges.add(key)
            x1, y1 = layout[a]
            x2, y2 = layout[b]
            is_path = key in active_edges
            ax.plot(
                [x1, x2],
                [y1, y2],
                color="#2563eb" if is_path else "#cbd5e1",
                linewidth=3.2 if is_path else 1.8,
                solid_capstyle="round",
                zorder=2 if is_path else 1,
            )
            ax.text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                str(cost),
                ha="center",
                va="center",
                fontsize=9,
                color="#1d4ed8" if is_path else "#64748b",
                bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "#e2e8f0"},
                zorder=4,
            )

    for node, (x, y) in layout.items():
        is_start = node == start
        is_goal = node == goal
        is_visited = node in visited_nodes
        face = "#eff6ff" if is_visited else "#ffffff"
        edge = "#2563eb" if is_visited else "#94a3b8"
        if is_start:
            face, edge = "#d1fae5", "#059669"
        if is_goal:
            face, edge = "#ffedd5", "#f97316"
        circle = plt.Circle((x, y), 0.16, facecolor=face, edgecolor=edge, linewidth=1.8, zorder=5)
        ax.add_patch(circle)
        ax.text(x, y, node[:1], ha="center", va="center", fontweight="bold", color="#0f172a", zorder=6)
        ax.text(
            x,
            y - 0.28,
            f"{graph['nodes'][node]['name']}\\nh={h[node]}",
            ha="center",
            va="top",
            fontsize=8,
            color="#475569",
            bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "none", "alpha": 0.85},
        )

    if path:
        total = path_cost(path)
        ax.text(
            0.04,
            0.05,
            f"path: {' -> '.join(path)}   cost={total}",
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=10,
            color="#334155",
            bbox={"boxstyle": "round,pad=0.32", "fc": "white", "ec": "#e2e8f0"},
        )

    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color="#0f172a")
    ax.set_xlim(-0.25, 8.65)
    ax.set_ylim(-0.62, 5.45)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    plt.tight_layout()
    plt.show()


draw_search_result(title="罗马尼亚路线图：Arad 到 Bucharest")
"""


HELPERS_CELL = """
# 路径辅助函数：回溯路线、计算总代价、格式化候选队列。
def reconstruct_path(parent, goal):
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent.get(current)
    return list(reversed(path))


def path_cost(path):
    total = 0
    for a, b in zip(path, path[1:]):
        for nbr, cost in adj[a]:
            if nbr == b:
                total += cost
                break
    return total


def frontier_text(items):
    return " | ".join(items) if items else "∅"
"""


DFS_CELL = """
# DFS：使用栈；最后加入的候选节点最先展开。
def dfs(start, goal, adj):
    stack = [(start, [start], 0)]
    visited = set()
    rows = []
    step = 0

    while stack:
        step += 1
        before = [item[0] for item in stack]
        node, path, cost = stack.pop()

        if node in visited:
            rows.append({
                "步骤": step,
                "边界队列取出前": frontier_text(before),
                "取出节点": node,
                "新增候选": "已访问，跳过",
                "当前路径": "→".join(path),
                "已访问": "→".join(sorted(visited)),
            })
            continue

        visited.add(node)
        if node == goal:
            rows.append({
                "步骤": step,
                "边界队列取出前": frontier_text(before),
                "取出节点": node,
                "新增候选": "到达目标",
                "当前路径": "→".join(path),
                "已访问": "→".join(sorted(visited)),
            })
            return path, pd.DataFrame(rows)

        pushed = []
        for nbr, edge_cost in reversed(adj[node]):
            if nbr not in visited:
                stack.append((nbr, path + [nbr], cost + edge_cost))
                pushed.append(f"{nbr}(cost={cost + edge_cost})")

        rows.append({
            "步骤": step,
            "边界队列取出前": frontier_text(before),
            "取出节点": node,
            "新增候选": frontier_text(pushed),
            "当前路径": "→".join(path),
            "已访问": "→".join(sorted(visited)),
        })

    return [], pd.DataFrame(rows)
"""


BFS_CELL = """
# BFS：使用队列；按边数层级一圈一圈向外扩展。
def bfs(start, goal, adj):
    queue = deque([(start, [start], 0)])
    discovered = {start}
    rows = []
    step = 0

    while queue:
        step += 1
        before = [item[0] for item in queue]
        node, path, cost = queue.popleft()

        if node == goal:
            rows.append({
                "步骤": step,
                "边界队列取出前": frontier_text(before),
                "取出节点": node,
                "新增候选": "到达目标",
                "当前路径": "→".join(path),
                "已发现": "→".join(sorted(discovered)),
            })
            return path, pd.DataFrame(rows)

        added = []
        for nbr, edge_cost in adj[node]:
            if nbr not in discovered:
                discovered.add(nbr)
                queue.append((nbr, path + [nbr], cost + edge_cost))
                added.append(nbr)

        rows.append({
            "步骤": step,
            "边界队列取出前": frontier_text(before),
            "取出节点": node,
            "新增候选": frontier_text(added),
            "当前路径": "→".join(path),
            "已发现": "→".join(sorted(discovered)),
        })

    return [], pd.DataFrame(rows)
"""


UCS_CELL = """
# UCS：按累计代价 g 排序；优先展开当前最便宜的路线。
def ucs(start, goal, adj):
    frontier = [(0, start, [start])]
    best_cost = {start: 0}
    visited = set()
    rows = []
    step = 0

    while frontier:
        step += 1
        before = [f"{item[1]}(g={item[0]})" for item in sorted(frontier)]
        cost, node, path = heapq.heappop(frontier)

        if node in visited:
            continue
        visited.add(node)

        if node == goal:
            rows.append({
                "步骤": step,
                "边界队列取出前": frontier_text(before),
                "取出节点": node,
                "新增候选": "到达目标",
                "当前路径": "→".join(path),
                "g": cost,
            })
            return path, pd.DataFrame(rows)

        added = []
        for nbr, edge_cost in adj[node]:
            new_cost = cost + edge_cost
            if nbr in visited or new_cost >= best_cost.get(nbr, float("inf")):
                continue
            best_cost[nbr] = new_cost
            heapq.heappush(frontier, (new_cost, nbr, path + [nbr]))
            added.append(f"{nbr}(g={new_cost})")

        rows.append({
            "步骤": step,
            "边界队列取出前": frontier_text(before),
            "取出节点": node,
            "新增候选": frontier_text(added),
            "当前路径": "→".join(path),
            "g": cost,
        })

    return [], pd.DataFrame(rows)
"""


GREEDY_CELL = """
# Greedy：只看启发式 h；优先展开看起来更接近目标的节点。
def greedy(start, goal, adj, h):
    frontier = [(h[start], 0, start, [start])]
    visited = set()
    rows = []
    step = 0

    while frontier:
        step += 1
        before = [f"{item[2]}(h={item[0]})" for item in sorted(frontier)]
        h_value, cost, node, path = heapq.heappop(frontier)

        if node in visited:
            continue
        visited.add(node)

        if node == goal:
            rows.append({
                "步骤": step,
                "边界队列取出前": frontier_text(before),
                "取出节点": node,
                "新增候选": "到达目标",
                "当前路径": "→".join(path),
                "h": h_value,
                "实际代价": cost,
            })
            return path, pd.DataFrame(rows)

        added = []
        for nbr, edge_cost in adj[node]:
            if nbr in visited:
                continue
            new_cost = cost + edge_cost
            heapq.heappush(frontier, (h[nbr], new_cost, nbr, path + [nbr]))
            added.append(f"{nbr}(h={h[nbr]})")

        rows.append({
            "步骤": step,
            "边界队列取出前": frontier_text(before),
            "取出节点": node,
            "新增候选": frontier_text(added),
            "当前路径": "→".join(path),
            "h": h_value,
            "实际代价": cost,
        })

    return [], pd.DataFrame(rows)
"""


ASTAR_CELL = """
# A*：按 f=g+h 排序；同时考虑已走代价和剩余距离估计。
def astar(start, goal, adj, h):
    frontier = [(h[start], h[start], 0, start, [start])]
    best_cost = {start: 0}
    visited = set()
    rows = []
    step = 0

    while frontier:
        step += 1
        before = [f"{item[3]}(f={item[0]}, g={item[2]}, h={item[1]})" for item in sorted(frontier)]
        f_value, h_value, cost, node, path = heapq.heappop(frontier)

        if node in visited:
            continue
        visited.add(node)

        if node == goal:
            rows.append({
                "步骤": step,
                "边界队列取出前": frontier_text(before),
                "取出节点": node,
                "新增候选": "到达目标",
                "当前路径": "→".join(path),
                "g": cost,
                "h": h_value,
                "f": f_value,
            })
            return path, pd.DataFrame(rows)

        added = []
        for nbr, edge_cost in adj[node]:
            new_cost = cost + edge_cost
            if nbr in visited or new_cost >= best_cost.get(nbr, float("inf")):
                continue
            best_cost[nbr] = new_cost
            new_h = h[nbr]
            new_f = new_cost + new_h
            heapq.heappush(frontier, (new_f, new_h, new_cost, nbr, path + [nbr]))
            added.append(f"{nbr}(f={new_f}, g={new_cost}, h={new_h})")

        rows.append({
            "步骤": step,
            "边界队列取出前": frontier_text(before),
            "取出节点": node,
            "新增候选": frontier_text(added),
            "当前路径": "→".join(path),
            "g": cost,
            "h": h_value,
            "f": f_value,
        })

    return [], pd.DataFrame(rows)
"""


RUN_DFS_CELL = """
# 运行 DFS：查看栈的展开过程和最终路线。
dfs_path, dfs_trace = dfs(start, goal, adj)
display(dfs_trace)
draw_search_result(dfs_path, dfs_trace, "DFS：栈后进先出")
"""


RUN_BFS_CELL = """
# 运行 BFS：查看队列的展开过程和最终路线。
bfs_path, bfs_trace = bfs(start, goal, adj)
display(bfs_trace)
draw_search_result(bfs_path, bfs_trace, "BFS：队列先进先出")
"""


RUN_UCS_CELL = """
# 运行 UCS：查看按累计代价 g 选择节点的过程。
ucs_path, ucs_trace = ucs(start, goal, adj)
display(ucs_trace)
draw_search_result(ucs_path, ucs_trace, "UCS：累计代价最小优先")
"""


RUN_GREEDY_CELL = """
# 运行 Greedy：查看按启发式 h 选择节点的过程。
greedy_path, greedy_trace = greedy(start, goal, adj, h)
display(greedy_trace)
draw_search_result(greedy_path, greedy_trace, "贪心搜索：启发式最小优先")
"""


RUN_ASTAR_CELL = """
# 运行 A*：查看按 f=g+h 选择节点的过程。
astar_path, astar_trace = astar(start, goal, adj, h)
display(astar_trace)
draw_search_result(astar_path, astar_trace, "A*：g+h 最小优先")
"""


SUMMARY_CELL = """
# 汇总五种搜索策略的路线、边数和总代价。
summary_df = pd.DataFrame(
    [
        {"算法": "DFS", "路径": "→".join(dfs_path), "边数": len(dfs_path) - 1, "代价": path_cost(dfs_path)},
        {"算法": "BFS", "路径": "→".join(bfs_path), "边数": len(bfs_path) - 1, "代价": path_cost(bfs_path)},
        {"算法": "UCS", "路径": "→".join(ucs_path), "边数": len(ucs_path) - 1, "代价": path_cost(ucs_path)},
        {"算法": "Greedy", "路径": "→".join(greedy_path), "边数": len(greedy_path) - 1, "代价": path_cost(greedy_path)},
        {"算法": "A*", "路径": "→".join(astar_path), "边数": len(astar_path) - 1, "代价": path_cost(astar_path)},
    ]
)
display(summary_df)
"""


def notebooks() -> dict[str, list]:
    return {"ch05_campus_search.ipynb": flatten(_cells())}


def _cells() -> list:
    return [
        rs.chapter_link(
            "第 5 章 · 经典路线图搜索代码实验",
            "本页把同一张路线图交给五种搜索策略。读者先确认城市、道路和启发式距离，再逐个运行算法，看边界队列如何变化，最后比较它们找到的路线和代价。",
            [
                "构建路线图和邻接表",
                "实现 DFS、BFS、UCS、贪心搜索、A*",
                "查看每个算法的展开过程、路径图和代价",
            ],
            "../ch5.html",
        ),
        rs.section("0", "图数据与画图", "先把问题转成图：节点是城市，边是道路距离，h 是到终点的直线距离估计。后面的所有算法都只读取这张图。"),
        *rs.stepcode(
            DEPENDENCIES_CELL,
            CAMPUS_GRAPH_CELL,
            ADJACENCY_CELL,
            TABLES_CELL,
            DRAWING_CELL,
        ),
        rs.section("1", "搜索算法", "这一组代码单元保留完整算法代码。重点看每种算法的边界队列：DFS 用栈，BFS 用队列，UCS、贪心搜索和 A* 用优先队列，但排序依据不同。"),
        *rs.stepcode(
            HELPERS_CELL,
            DFS_CELL,
            BFS_CELL,
            UCS_CELL,
            GREEDY_CELL,
            ASTAR_CELL,
        ),
        rs.section("2", "逐个运行并查看过程", "每个算法都会输出展开表和路径图。展开表用于看“下一步为什么选它”，路径图用于看“最终路线是否真的更短”。"),
        rs.subsection("2.1", "DFS"),
        *rs.stepcode(RUN_DFS_CELL),
        rs.subsection("2.2", "BFS"),
        *rs.stepcode(RUN_BFS_CELL),
        rs.subsection("2.3", "UCS"),
        *rs.stepcode(RUN_UCS_CELL),
        rs.subsection("2.4", "贪心搜索"),
        *rs.stepcode(RUN_GREEDY_CELL),
        rs.subsection("2.5", "A*"),
        *rs.stepcode(RUN_ASTAR_CELL),
        rs.section("3", "结果汇总", "最后把路线、边数和总代价放在一起。读者可以直接比较：少走几条边不一定总代价最低，只看启发式也可能走偏。"),
        *rs.stepcode(SUMMARY_CELL),
    ]
