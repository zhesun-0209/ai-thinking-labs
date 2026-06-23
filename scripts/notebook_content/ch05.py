"""第 5 章 · 校园图搜索 — 完整逐步演示。"""

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
            "第 5 章 · 图搜索算法",
            "在同一张校园图上，逐步比较 BFS、DFS、UCS、Greedy、A* 每一轮如何选择节点、扩展候选、得到路径。",
            [
                "先读懂图搜索问题：节点、边权、起点、目标",
                "逐算法查看“选择节点 → 扩展候选 → 更新待探索节点”的步骤",
                "比较最少边数、最低代价、启发式搜索三种目标的差异",
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
            "plot_campus(title='校园图：边权与启发式 h')",
        ),
        rs.reading("先看起点 `x` 的邻居：不同算法从同一组候选出发，但下一步选择规则不同。"),
        *rs.stepcode("display(neighbors_table('x'))", "display(algorithm_overview())"),
        *rs.stepcode("adj = build_adjacency(graph['edges'])", "print('adj[x] =', adj['x'])"),
        rs.section("3", "BFS：先保证边数最少"),
        rs.reading(
            "BFS 的问题不是“哪条路最近”，而是“经过的边数最少”。",
            "读步骤表时重点看：它按进入候选列表的先后顺序扩展，因此会先完成浅层节点。"
        ),
        rs.listing(
            "BFS 伪代码",
            "把起点放入待探索节点\n每轮选择最早加入的节点\n把它的未访问邻居加入待探索节点",
        ),
        *rs.stepcode("display(algorithm_steps('bfs'))", "display(algorithm_result('bfs'))"),
        *rs.stepcode(
            "path_bfs = run_all()['bfs']['path']",
            "print('path:', '->'.join(path_bfs), ' cost:', path_cost(path_bfs, adj))",
            "plot_campus(path_bfs, title='BFS 路径：边数最少，但代价不是最低')",
        ),
        rs.self_check("BFS 2 步但代价 8 不是最低——为什么？", answer="BFS 优化边数，不优化边权之和。"),
        rs.section("4", "DFS：先沿一条路走深"),
        rs.reading(
            "DFS 关注的是探索顺序，不承诺最少边数，也不承诺最低代价。",
            "读步骤表时重点看：它会优先处理最近加入的候选，因此路径受邻居顺序影响很大。"
        ),
        rs.listing(
            "DFS 伪代码",
            "把起点放入待探索节点\n每轮选择最近加入的节点\n若没到目标，就继续加入它的邻居",
        ),
        *rs.stepcode("display(algorithm_steps('dfs'))", "display(algorithm_result('dfs'))"),
        *rs.stepcode(
            "plot_campus(run_all()['dfs']['path'], title='DFS 路径：取决于探索顺序')",
        ),
        rs.self_check("DFS 路径是否最优？", answer="否，本例 4 步代价 13，非最低。"),
        rs.section("5", "UCS：先确认当前总代价最低的路"),
        rs.reading(
            "UCS 每轮选择累计代价 `g` 最小的候选节点。",
            "读步骤表时重点看：当发现更便宜的到达方式时，它会更新候选节点的代价。"
        ),
        rs.listing(
            "UCS 伪代码",
            "记录从起点到每个候选节点的累计代价 g\n每轮选择 g 最小的节点\n若经当前节点到邻居更便宜，就更新该邻居",
        ),
        *rs.stepcode(
            "display(algorithm_steps('ucs'))",
            "display(algorithm_result('ucs'))",
            "plot_campus(run_all()['ucs']['path'], title='UCS 路径：总代价最低')",
        ),
        rs.self_check("UCS 与 BFS 路径差异？", answer="UCS 代价 7 更优；BFS 步数更少但代价 8。"),
        rs.section("6", "Greedy：只看离目标的估计距离"),
        rs.reading(
            "Greedy 每轮选择 `h` 最小的候选节点，也就是看起来离目标最近的节点。",
            "它很直观，但忽略已经走过的代价，因此不保证总路径最低。"
        ),
        *rs.stepcode("display(first_step_scores())"),
        *rs.stepcode(
            "display(algorithm_steps('greedy'))",
            "display(algorithm_result('greedy'))",
            "plot_campus(run_all()['greedy']['path'], title='Greedy 路径：只按 h 选择')",
        ),
        rs.section("7", "A*：同时看已走代价和剩余估计"),
        rs.reading(
            "A* 每轮选择 `f=g+h` 最小的候选节点。",
            "`g` 表示已经付出的代价，`h` 表示到目标的估计距离；这让 A* 比 Greedy 更稳。"
        ),
        rs.listing(
            "A* 伪代码",
            "g = 从起点走到当前节点的真实代价\nh = 当前节点到目标的估计代价\nf = g + h\n每轮选择 f 最小的节点",
        ),
        *rs.stepcode(
            "display(algorithm_steps('astar'))",
            "display(algorithm_result('astar'))",
            "plot_campus(run_all()['astar']['path'], title='A* 路径：按 f=g+h 综合选择')",
        ),
        rs.self_check("A* 在本图是否最优？", answer="是，与 UCS 同路径代价 7。"),
        rs.section("8", "五种算法对照"),
        *rs.stepcode("display(comparison_table())"),
        *rs.stepcode("plot_all_paths()"),
        *rs.stepcode("verify_against_web()"),
        rs.summary(
            "BFS 保证最少边数；DFS 体现探索顺序；UCS 按真实累计代价找最低代价路径。",
            "Greedy 只看启发式估计；A* 把真实代价 g 与估计代价 h 合在一起看。",
        ),
        rs.exercises(
            "若所有边权为 1，BFS 与 UCS 路径是否相同？",
            "Greedy 只看 h 时，在哪些图上可能走出更贵路径？",
        ),
    ]
