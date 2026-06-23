"""第 5 章 · 校园图搜索 — 可执行代码实验。"""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import boot, flatten

B = boot(
    "ch05",
    "from search_algorithms import *",
)


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
            "graph = load_graph()",
            "adj = build_adjacency(graph['edges'])",
            "print('start:', graph['start'], 'goal:', graph['goal'])",
            "display(graph_summary())",
            "display(edges_table())",
            "plot_campus(title='Campus graph')",
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
            "plot_campus(path, title=f'{algo.upper()} path')",
        ),
        rs.section("3", "校验"),
        *rs.stepcode(
            "verify_against_web(graph)",
        ),
    ]
