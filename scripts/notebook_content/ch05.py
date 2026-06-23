"""第 5 章 · 校园图搜索 — 完整逐步演示。"""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import boot, flatten

B = boot(
    "ch05",
    "from search_algorithms import *\nfrom common.codelens import print_frames as print_codelens\nfrom common.viz_anim import animate_container, snapshots_from_codelens",
)


def notebooks() -> dict[str, list]:
    return {"ch05_campus_search.ipynb": flatten(_cells())}


def _cells() -> list:
    return [
        rs.chapter_link(
            "第 5 章 · 图搜索算法",
            "在同一校园图上，逐步观察 BFS、DFS、UCS、Greedy、A* 的**队列 / 栈 / 优先队列**如何驱动搜索，并对照 [ch5.html](../ch5.html) 动画。",
            [
                "用邻接表表示无向加权图",
                "逐步执行 BFS/DFS，解释每一步 frontier 变化",
                "区分「步数最少」与「代价最少」",
            ],
            "../ch5.html",
        ),
        rs.section("1", "图与搜索问题"),
        rs.reading(
            "**顶点**表示地点（`x` 校门口、`s1` 食堂、`c1` 操场）。**边**附带步行分钟数（权重）。",
            "**搜索**：从起点到目标找路径；算法差异在于「下一步探索哪个节点」。",
        ),
        rs.listing(
            "形式化",
            "START=x, GOAL=c1\nPATH = 相邻顶点序列\nCOST = 路径上边权之和",
        ),
        rs.self_check("无向边 x↔s1 在邻接表中如何存储？", answer="两端各存一条，便于双向扩展。"),
        rs.section("2", "加载校园图"),
        *rs.stepcode(
            B,
            "graph = load_graph()",
            "print('起点', graph['start'], '-> 目标', graph['goal'])",
            "display(graph_summary())",
            "display(edges_table())",
            "plot_campus(title='Campus graph (edge cost, h)')",
        ),
        *rs.stepcode("display(neighbors_table('x'))"),
        rs.section("3", "构建邻接表（逐步）"),
        rs.listing(
            "核心循环",
            "for edge in edges:\n    adj[a].append((b,cost)); adj[b].append((a,cost))",
        ),
        *rs.stepcode(
            "frames_adj = codelens_build_adjacency()",
            "print_codelens(frames_adj)",
        ),
        *rs.stepcode("adj = build_adjacency(graph['edges'])", "print('adj[x] =', adj['x'])"),
        rs.section("4", "广度优先 BFS"),
        rs.subsection("4.1", "队列与层序", "FIFO 队列：队头出、队尾进。等权图上保证**最少步数**。"),
        rs.listing(
            "BFS",
            "while queue:\n  u = queue.pop(0)\n  for v in neighbors(u): queue.append(v)",
        ),
        *rs.stepcode("bfs_frames = codelens_bfs()", "print_codelens(bfs_frames)"),
        *rs.stepcode("animate_bfs_queue()"),
        *rs.stepcode(
            "display(trace_search('bfs'))",
            "path_bfs = run_all()['bfs']['path']",
            "print('path:', '->'.join(path_bfs), ' cost:', path_cost(path_bfs, adj))",
            "plot_campus(path_bfs, title='BFS path (2 steps, cost 8)')",
        ),
        rs.self_check("BFS 2 步但代价 8 不是最低——为什么？", answer="BFS 优化边数，不优化边权之和。"),
        rs.section("5", "深度优先 DFS"),
        rs.subsection("5.1", "栈与回溯", "LIFO 栈：栈顶出；本图先深入 j→s2→s1。"),
        rs.listing("DFS", "while stack:\n  u = stack.pop()\n  push unvisited neighbors"),
        *rs.stepcode("dfs_frames = codelens_dfs()", "print_codelens(dfs_frames)"),
        *rs.stepcode("animate_dfs_stack()"),
        *rs.stepcode(
            "display(trace_search('dfs'))",
            "plot_campus(run_all()['dfs']['path'], title='DFS path (4 steps, cost 13)')",
        ),
        rs.self_check("DFS 路径是否最优？", answer="否，本例 4 步代价 13，非最低。"),
        rs.section("6", "一致代价 UCS"),
        rs.reading("优先队列按 **g(n)** 累计代价排序。本例最优 x→s1→t→c1，代价 7。"),
        rs.listing("UCS", "frontier = PriorityQueue by g(n)"),
        *rs.stepcode(
            "display(trace_search('ucs'))",
            "plot_campus(run_all()['ucs']['path'], title='UCS optimal cost 7')",
        ),
        rs.self_check("UCS 与 BFS 路径差异？", answer="UCS 代价 7 更优；BFS 步数更少但代价 8。"),
        rs.section("7", "Greedy 与 A*"),
        rs.reading("Greedy 按 h；A* 按 f=g+h。从 x：c2 的 f=8，s1 的 f=5，故先展开 s1。"),
        *rs.stepcode("display(first_step_scores())"),
        *rs.stepcode("display(trace_search('greedy'))"),
        *rs.stepcode("display(trace_search('astar'))"),
        rs.self_check("A* 在本图是否最优？", answer="是，与 UCS 同路径代价 7。"),
        rs.section("8", "五种算法对照"),
        *rs.stepcode("display(comparison_table())"),
        *rs.stepcode("plot_all_paths()"),
        *rs.stepcode("verify_against_web()"),
        rs.summary(
            "BFS 队列保证最少步数；DFS 栈不保证最优；UCS/A* 在加权图上求最低代价。",
            "对照 [ch5.html](../ch5.html) 步进动画验证每一步预测。",
        ),
        rs.exercises(
            "若所有边权为 1，BFS 与 UCS 路径是否相同？",
            "改变 DFS 入栈顺序，路径如何变化？",
        ),
    ]
