"""Runestone-style Chapter 5 — campus graph search (full detail)."""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import boot, flatten

B = boot("ch05", "from search_algorithms import *")


def notebooks() -> dict[str, list]:
    return {"ch05_campus_search.ipynb": flatten(_cells())}


def _cells() -> list[list]:
    return [
        rs.chapter(
            "第 5 章 · 图搜索算法",
            "在同一校园图上，用 **CodeLens 分步** 观察 BFS、DFS、UCS、Greedy、A* 的队列/栈/优先队列如何驱动搜索。",
            [
                "能用邻接表表示无向加权图，并手工模拟 frontier 变化",
                "能逐步执行 BFS/DFS，解释每一步 queue/stack 的内容",
                "能区分「步数最少」与「代价最少」，并用 UCS/A* 验证",
                "能将 Python 实现与 [ch5.html](../ch5.html) 动画逐步对应",
            ],
        ),
        rs.section(
            "1",
            "图与搜索问题",
            "Runestone《Problem Solving with Algorithms and Data Structures》第 8 章从**图的基本词汇**讲起。我们把校园地图抽象为：",
        ),
        rs.reading(
            "**顶点（vertex）** 表示地点（校门口 `x`、食堂 `s1`、操场 `c1` …）。",
            "**边（edge）** 表示可通行的道路，附带**正整数权重**（步行分钟数）。",
            "**搜索问题**：给定起点与目标，找一条路径。不同算法对「下一步探索谁」的规则不同——这就是本章核心。",
        ),
        rs.listing(
            "搜索问题形式化",
            """START = x
GOAL  = c1
PATH  = [v0, v1, ..., vk]  其中相邻顶点之间有边
COST(PATH) = sum(边权 along PATH)""",
        ),
        rs.self_check(
            "在无向图中，边 x↔s1 与 s1↔x 是否同一条路？",
            answer="是。邻接表通常双向各存一条，便于从任意端点扩展。",
        ),
        rs.section("2", "Listing：加载数据（ActiveCode）"),
        rs.subsection("2.1", "从 JSON 读取与网页相同的图"),
        *rs.activecode(
            B,
            "graph = load_graph()",
            "start, goal = graph['start'], graph['goal']",
            "print('起点', start, '→ 目标', goal)",
            "display(graph_summary())",
            caption="读取节点与启发式 h",
        ),
        *rs.activecode(
            "display(edges_table())",
            "plot_campus(title='图 5-1 · 校园图（边权 + h）')",
            caption="边表与可视化",
        ),
        rs.self_check(
            "从 x 出发的三个邻居是谁？按**字母序** BFS 入队顺序是什么？",
            hint="运行下一 ActiveCode 前请先预测。",
            answer="邻居 c2, j, s1（字母序）。BFS 第一层入队顺序即 c2 → j → s1。",
        ),
        *rs.activecode("display(neighbors_table('x'))", caption="x 的邻居与 h"),
        rs.section("3", "Listing + CodeLens：构建邻接表"),
        rs.reading(
            "PythonDS 先教 **Graph ADT**，再教 BFS。我们逐条边把 JSON 写入 `adj`，"
            "每写一条就打印当前邻接表——等价于 Runestone 的 CodeLens 观察引用结构如何生长。",
        ),
        rs.listing(
            "邻接表构建（核心循环）",
            """adj = {}
for edge in edges:
    a, b, cost = edge['from'], edge['to'], edge['cost']
    adj.setdefault(a, []).append((b, cost))
    adj.setdefault(b, []).append((a, cost))
    sort each adjacency list by neighbor id""",
        ),
        *rs.activecode(
            "frames_adj = codelens_build_adjacency()",
            "print(f'共 {len(frames_adj)-1} 条边，{len(frames_adj)} 个 CodeLens 帧')",
            "print_codelens(frames_adj, limit=4)",
            "print('…')",
            "print_codelens(frames_adj[-2:])",
            caption="CodeLens · 邻接表构建（首尾帧）",
        ),
        *rs.activecode(
            "adj = build_adjacency(graph['edges'])",
            "print('完整 adj[x] =', adj['x'])",
            caption="验证最终 adj",
        ),
        rs.section("4", "广度优先搜索 BFS"),
        rs.subsection(
            "4.1",
            "Reading：队列与层序",
            "BFS 用 **FIFO 队列**。从起点开始，每次弹出**队头**，把未访问邻居加到**队尾**。"
            "在**等权图**上，BFS 第一次到达目标时步数最少。",
        ),
        rs.listing(
            "BFS 伪代码（PythonDS 风格）",
            """function BFS(start, goal):
    frontier ← Queue([start])
    visited ← {}
    parent ← {}
    while frontier not empty:
        current ← frontier.dequeue()
        if current == goal: return path(parent, goal)
        for each neighbor n of current:
            if n not visited and n not in frontier:
                parent[n] ← current
                frontier.enqueue(n)
        mark current visited""",
        ),
        rs.self_check(
            "下一步弹出队头时，frontier 第一个元素是谁？（从 x 开始第一轮扩展后）",
            answer="c2（字母序：c2, j, s1 入队后，队头是 c2）。",
        ),
        rs.subsection("4.2", "CodeLens · BFS 完整逐步执行"),
        *rs.activecode(
            "bfs_frames = codelens_bfs()",
            "print(f'BFS 共 {len(bfs_frames)} 个 CodeLens 帧')",
            caption="生成全部 BFS 帧",
        ),
        *rs.activecode(
            "print_codelens(bfs_frames, limit=8)",
            caption="CodeLens · BFS 第 1–8 帧",
        ),
        *rs.activecode(
            "print_codelens(bfs_frames[8:])",
            caption="CodeLens · BFS 剩余帧",
        ),
        *rs.activecode(
            "display(trace_search('bfs'))",
            "path_bfs = run_all()['bfs']['path']",
            "print('最终路径:', '→'.join(path_bfs))",
            "print('代价:', path_cost(path_bfs, adj))",
            "plot_campus(path_bfs, title='BFS 路径（2 步，代价 8）')",
            caption="汇总表 + 路径图",
        ),
        rs.self_check(
            "BFS 2 步到达，但代价 8 不是最低——为什么？",
            answer="BFS 优化的是**边数（步数）**，不是**边权之和**。本图边权不同，需 UCS/A*。",
        ),
        rs.section("5", "深度优先搜索 DFS"),
        rs.subsection(
            "5.1",
            "Reading：栈与回溯",
            "DFS 用 **LIFO 栈**。邻居按**逆字母序**入栈时，会先深入 `j → s2 → s1`，"
            "再到达 `c1`。路径更长、代价更高，但仍能找到目标。",
        ),
        rs.listing(
            "DFS 伪代码",
            """function DFS(start, goal):
    stack ← [start]
    while stack not empty:
        current ← stack.pop()
        if current visited: continue
        mark visited
        if current == goal: return path
        for neighbor in reverse(sorted(neighbors(current))):
            stack.push(neighbor)""",
        ),
        *rs.activecode(
            "dfs_frames = codelens_dfs()",
            "print_codelens(dfs_frames, limit=10)",
            caption="CodeLens · DFS 前 10 帧",
        ),
        *rs.activecode(
            "print_codelens(dfs_frames[10:])",
            "display(trace_search('dfs'))",
            "plot_campus(run_all()['dfs']['path'], title='DFS 路径（4 步，代价 13）')",
            caption="DFS 剩余帧与结果",
        ),
        rs.section("6", "一致代价搜索 UCS"),
        rs.reading(
            "UCS 使用**优先队列**，键为 **g(n)**——从起点到 n 的累计代价。"
            "每次弹出 g 最小的节点。本例最优路径 `x→s1→t→c1`，代价 **7**。",
        ),
        rs.listing("UCS 键函数", "priority = g(n)  # 累计边权"),
        *rs.activecode(
            "display(trace_search('ucs'))",
            "plot_campus(run_all()['ucs']['path'], title='UCS 最优代价 7')",
            caption="UCS trace",
        ),
        rs.section("7", "Greedy 与 A*"),
        rs.reading(
            "**Greedy** 按 **h(n)** 排序（估计到目标的距离）。**A*** 按 **f(n)=g(n)+h(n)**。"
            "从 x 出发第一步：超市 c2 的 f=7+1=8，食堂 s1 的 f=2+3=5，故 A* 先展开 s1。",
        ),
        rs.listing("A* 评估", "f(n) = g(n) + h(n)"),
        *rs.activecode(
            "display(first_step_scores())",
            caption="x 处各邻居 g、h、f 明细",
        ),
        *rs.activecode(
            "display(trace_search('greedy'))",
            "display(trace_search('astar'))",
            caption="Greedy 与 A* 逐步 trace",
        ),
        rs.section("8", "五种算法对照"),
        *rs.activecode(
            "display(comparison_table())",
            "plot_all_paths()",
            "verify_against_web()",
            caption="与 ch5.html 交叉验证",
        ),
        rs.summary(
            "**队列 BFS** 保证最少步数；**栈 DFS** 不保证最优；**UCS/A*** 在加权图上 pursuit 最低代价。",
            "Runestone 强调边读边运行——本 notebook 用 CodeLens 帧展示**每一步**的 frontier/stack 与 parent。",
            "回到 [ch5.html](../ch5.html) 实验室，对照动画逐步预测下一帧。",
        ),
        rs.exercises(
            "若所有边权改为 1，BFS 与 UCS 路径是否相同？用代码修改 `edges` 后验证。",
            "把 DFS 入栈顺序改为正字母序，路径如何变化？",
            "解释 MiniMax（网页第 6 种）与 campus 单智能体搜索的本质区别。",
        ),
    ]
