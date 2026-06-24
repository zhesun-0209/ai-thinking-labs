"""第 5 章 · 校园图搜索 — 可执行代码实验。"""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import boot, flatten

B = boot(
    "ch05",
    "from search_algorithms import *",
)

CAMPUS_GRAPH_CELL = """
# 导入表格展示工具，并直接在 notebook 中定义校园图。
import pandas as pd
from IPython.display import display

graph = {
    "start": "x",
    "goal": "c1",
    "nodes": {
        "x": {"name": "校门口", "h": 7},
        "c2": {"name": "超市", "h": 1},
        "j": {"name": "教学楼", "h": 4},
        "s2": {"name": "实验楼", "h": 4},
        "s1": {"name": "食堂", "h": 3},
        "t": {"name": "图书馆", "h": 2},
        "c1": {"name": "操场", "h": 0},
    },
    "edges": [
        {"from": "x", "to": "c2", "cost": 7},
        {"from": "x", "to": "j", "cost": 2},
        {"from": "x", "to": "s1", "cost": 2},
        {"from": "j", "to": "s2", "cost": 4},
        {"from": "s2", "to": "s1", "cost": 1},
        {"from": "s1", "to": "t", "cost": 3},
        {"from": "s1", "to": "c1", "cost": 6},
        {"from": "t", "to": "c1", "cost": 2},
    ],
    "expected": {
        "dfs": {"path": ["x", "j", "s2", "s1", "c1"], "steps": 4, "cost": 13},
        "bfs": {"path": ["x", "s1", "c1"], "steps": 2, "cost": 8},
        "ucs": {"path": ["x", "s1", "t", "c1"], "steps": 3, "cost": 7},
        "greedy": {"path": ["x", "s1", "c1"], "steps": 2, "cost": 8},
        "astar": {"path": ["x", "s1", "t", "c1"], "steps": 3, "cost": 7},
    },
}
"""

ADJACENCY_CELL = """
# 用边表直接构造邻接表：每条无向边同时写入两个方向。
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


def notebooks() -> dict[str, list]:
    return {"ch05_campus_search.ipynb": flatten(_cells())}


def _cells() -> list:
    return [
        rs.chapter_link(
            "第 5 章 · 图搜索代码实验",
            [
                "准备校园图数据",
                "运行 BFS、DFS、UCS、Greedy、A*",
                "输出路径、代价和校验结果",
            ],
            "../ch5.html",
        ),
        rs.section("0", "环境与数据"),
        *rs.stepcode(
            B,
            CAMPUS_GRAPH_CELL,
            ADJACENCY_CELL,
            "print('start:', graph['start'], 'goal:', graph['goal'])",
            "nodes_df = pd.DataFrame([\n    {'节点': nid, '名称': meta['name'], 'h(到操场)': meta['h']}\n    for nid, meta in graph['nodes'].items()\n]).sort_values('节点')\ndisplay(nodes_df)",
            "edges_df = pd.DataFrame([\n    {'边': f\"{edge['from']}↔{edge['to']}\", '代价': edge['cost']}\n    for edge in graph['edges']\n])\ndisplay(edges_df)",
            "plot_campus(graph=graph, title='Campus graph')",
        ),
        rs.section("1", "运行所有算法"),
        *rs.stepcode(
            "results = run_all(graph)",
            "display(comparison_table(graph))",
            "plot_all_paths(graph)",
        ),
        rs.section("2", "单独运行一个算法"),
        *rs.stepcode(
            "algo = 'astar'",
            "path = results[algo]['path']",
            "cost = path_cost(path, adj)",
            "print(algo, 'path:', ' -> '.join(path), 'cost:', cost)",
            "plot_campus(path, graph=graph, title=f'{algo.upper()} path')",
        ),
        rs.section("3", "校验"),
        *rs.stepcode(
            "verify_against_web(graph)",
        ),
    ]
