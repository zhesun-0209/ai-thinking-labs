"""Campus graph search algorithms — pedagogical API for ch5 notebook."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Callable

import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys_path_common = Path(__file__).resolve().parent.parent
import sys as _sys

if str(sys_path_common) not in _sys.path:
    _sys.path.insert(0, str(sys_path_common))
from common.codelens import Frame  # noqa: E402
from common.mpl_setup import configure_matplotlib  # noqa: E402

GRAPH_PATH = Path(__file__).resolve().parent.parent / "common" / "campus_graph.json"

# 与 ch5.html 地图布局大致一致（仅用于可视化）
LAYOUT = {
    "x": (0.25, 1.15),
    "c2": (0.75, 2.45),
    "j": (1.85, 2.08),
    "s2": (3.15, 2.25),
    "s1": (1.9, 0.62),
    "t": (3.25, 0.62),
    "c1": (4.65, 0.68),
}

ALGO_META = {
    "bfs": {
        "label": "BFS",
        "name": "广度优先搜索",
        "container": "queue",
        "container_name": "Queue / 队列",
        "pop_code": "frontier.popleft()",
        "push_code": "append(right)",
        "sort_note": "保持入队顺序，左端先出",
        "selection_rule": "选最早加入的候选节点",
        "focus": "看层数：先把距离起点 1 条边的节点都试完，再试 2 条边。",
        "sort_fn": None,
        "pop_end": False,
        "reverse_neighbors": False,
        "mode": "default",
        "key_label": "",
    },
    "dfs": {
        "label": "DFS",
        "name": "深度优先搜索",
        "container": "stack",
        "container_name": "Stack / 栈",
        "pop_code": "stack.pop()",
        "push_code": "append(top)",
        "sort_note": "后进先出，栈顶先出",
        "selection_rule": "选最后加入的候选节点",
        "focus": "看探索顺序：一条路先尽量走深，走不通再回到别的候选。",
        "sort_fn": None,
        "pop_end": True,
        "reverse_neighbors": True,
        "mode": "default",
        "key_label": "",
    },
    "ucs": {
        "label": "UCS",
        "name": "一致代价搜索",
        "container": "priority",
        "container_name": "Priority queue / 优先队列",
        "pop_code": "pop_min(g)",
        "push_code": "push by g",
        "sort_note": "按累计代价 g 从小到大取出",
        "selection_rule": "选当前累计代价 g 最小的节点",
        "focus": "看总路程：每一步都优先确认当前已知最便宜的路线。",
        "sort_fn": lambda e: (e["g"], e["id"]),
        "pop_end": False,
        "reverse_neighbors": False,
        "mode": "cost",
        "key_label": "g",
    },
    "greedy": {
        "label": "Greedy",
        "name": "贪心最佳优先搜索",
        "container": "priority",
        "container_name": "Priority queue / 优先队列",
        "pop_code": "pop_min(h)",
        "push_code": "push by h",
        "sort_note": "按启发式 h 从小到大取出",
        "selection_rule": "选估计离目标最近 h 最小的节点",
        "focus": "看直觉距离：它只相信当前位置到目标的估计，不关心已经走了多远。",
        "sort_fn": lambda e: (e["h"], e["id"]),
        "pop_end": False,
        "reverse_neighbors": False,
        "mode": "default",
        "key_label": "h",
    },
    "astar": {
        "label": "A*",
        "name": "A* 搜索",
        "container": "priority",
        "container_name": "Priority queue / 优先队列",
        "pop_code": "pop_min(f)",
        "push_code": "push by f=g+h",
        "sort_note": "按 f=g+h 从小到大取出",
        "selection_rule": "选 f=g+h 最小的节点",
        "focus": "看综合判断：同时考虑已经走过的代价 g 和到目标的估计 h。",
        "sort_fn": lambda e: (e["f"], e["h"], e["g"], e["id"]),
        "pop_end": False,
        "reverse_neighbors": False,
        "mode": "cost",
        "key_label": "f",
    },
}


def load_graph() -> dict:
    with GRAPH_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def build_adjacency(edges: list[dict]) -> dict[str, list[tuple[str, int]]]:
    adj: dict[str, list[tuple[str, int]]] = {}
    for edge in edges:
        a, b, cost = edge["from"], edge["to"], edge["cost"]
        adj.setdefault(a, []).append((b, cost))
        adj.setdefault(b, []).append((a, cost))
    for neighbors in adj.values():
        neighbors.sort(key=lambda x: x[0])
    return adj


def path_cost(path: list[str], adj: dict[str, list[tuple[str, int]]]) -> int:
    total = 0
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        for nbr, c in adj[a]:
            if nbr == b:
                total += c
                break
    return total


def reconstruct(parent: dict[str, str], goal: str) -> list[str]:
    path: list[str] = []
    cur: str | None = goal
    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)
    path.reverse()
    return path


def graph_summary(graph: dict | None = None) -> pd.DataFrame:
    graph = graph or load_graph()
    rows = []
    for nid, meta in graph["nodes"].items():
        rows.append({"节点": nid, "名称": meta["name"], "h(到操场)": meta["h"]})
    return pd.DataFrame(rows).sort_values("节点")


def edges_table(graph: dict | None = None) -> pd.DataFrame:
    graph = graph or load_graph()
    rows = [{"边": f"{e['from']}↔{e['to']}", "代价": e["cost"]} for e in graph["edges"]]
    return pd.DataFrame(rows)


def neighbors_table(node: str, graph: dict | None = None) -> pd.DataFrame:
    graph = graph or load_graph()
    adj = build_adjacency(graph["edges"])
    h = {k: v["h"] for k, v in graph["nodes"].items()}
    rows = [{"邻居": n, "边代价": c, "h": h[n]} for n, c in adj[node]]
    return pd.DataFrame(rows)


def first_step_scores(graph: dict | None = None) -> pd.DataFrame:
    """从 x 出发时各邻居的 g、h、f（A* 第一步对照）。"""
    graph = graph or load_graph()
    start = graph["start"]
    adj = build_adjacency(graph["edges"])
    h = {k: v["h"] for k, v in graph["nodes"].items()}
    rows = []
    for nbr, cost in adj[start]:
        g, hv = cost, h[nbr]
        rows.append({"邻居": nbr, "g": g, "h": hv, "f=g+h": g + hv, "名称": graph["nodes"][nbr]["name"]})
    return pd.DataFrame(rows).sort_values("f=g+h")


def container_cheatsheet() -> pd.DataFrame:
    """Show how each search algorithm treats the frontier container."""
    rows = []
    for key in ["bfs", "dfs", "ucs", "greedy", "astar"]:
        meta = ALGO_META[key]
        rows.append(
            {
                "算法": meta["label"],
                "frontier 类型": meta["container_name"],
                "取出动作": meta["pop_code"],
                "加入动作": meta["push_code"],
                "下一步选择规则": meta["sort_note"],
            }
        )
    return pd.DataFrame(rows)


def algorithm_overview(graph: dict | None = None) -> pd.DataFrame:
    """Reader-facing comparison: what each algorithm optimizes in this example."""
    graph = graph or load_graph()
    results = run_all(graph)
    rows = []
    for key in ["bfs", "dfs", "ucs", "greedy", "astar"]:
        meta = ALGO_META[key]
        result = results[key]
        rows.append(
            {
                "算法": f"{meta['label']} · {meta['name']}",
                "下一步选择规则": meta["selection_rule"],
                "本例路径": " → ".join(result["path"]),
                "总代价": result["cost"],
                "读者要观察的点": meta["focus"],
            }
        )
    return pd.DataFrame(rows)


def _entry_label(entry: dict, algo: str) -> str:
    if not isinstance(entry, dict):
        return str(entry)
    nid = entry["id"]
    meta = ALGO_META[algo]
    key = meta["key_label"]
    if not key:
        return nid
    if key == "f":
        return f"{nid} f={entry.get('f', 0)}"
    return f"{nid} {key}={entry.get(key, 0)}"


def _frontier_text(frontier: list[dict], algo: str) -> str:
    if not frontier:
        return "∅"
    return " | ".join(_entry_label(entry, algo) for entry in frontier)


def _apply_frontier_scores(frontier: list[dict], h: dict[str, int], g_scores: dict[str, int]) -> None:
    for entry in frontier:
        nid = entry["id"]
        entry["h"] = h[nid]
        entry["g"] = g_scores.get(nid, entry["g"])
        entry["f"] = entry["g"] + entry["h"]


def operation_trace(algo: str, graph: dict | None = None, max_steps: int = 12) -> pd.DataFrame:
    """Readable frontier operations: before pop, pop method, pushes, and next frontier."""
    graph = graph or load_graph()
    start, goal = graph["start"], graph["goal"]
    h = {k: v["h"] for k, v in graph["nodes"].items()}
    adj = build_adjacency(graph["edges"])
    meta = ALGO_META[algo]

    frontier: list[dict] = [{"id": start, "g": 0, "h": h[start], "f": h[start]}]
    in_frontier = {start}
    visited: set[str] = set()
    visited_order: list[str] = []
    parent: dict[str, str] = {}
    g_scores: dict[str, int] = {start: 0}
    rows = []

    for step in range(1, max_steps + 1):
        if not frontier:
            break
        if meta["sort_fn"]:
            frontier.sort(key=meta["sort_fn"])
        before = [dict(entry) for entry in frontier]
        current = frontier.pop() if meta["pop_end"] else frontier.pop(0)
        cid = current["id"]
        in_frontier.discard(cid)
        after_pop = [dict(entry) for entry in frontier]

        if cid in visited:
            rows.append(
                {
                    "步": step,
                    "算法": meta["label"],
                    "取出动作": meta["pop_code"],
                    "取出节点": cid,
                    "frontier 取出前": _frontier_text(before, algo),
                    "frontier 取出后": _frontier_text(after_pop, algo),
                    "新加入 / 更新": "已访问，跳过",
                    "下一轮 frontier": _frontier_text(frontier, algo),
                    "visited": "→".join(visited_order) or "∅",
                    "到达?": False,
                }
            )
            continue

        visited.add(cid)
        visited_order.append(cid)
        reached = cid == goal
        added: list[str] = []

        if not reached:
            neighbors = adj[cid]
            ordered = list(reversed(neighbors)) if meta["reverse_neighbors"] else neighbors
            for nbr, edge_cost in ordered:
                if nbr in visited:
                    continue
                next_g = g_scores[cid] + edge_cost
                if meta["mode"] == "cost":
                    if next_g >= g_scores.get(nbr, 10**9):
                        continue
                    g_scores[nbr] = next_g
                    parent[nbr] = cid
                    if nbr in in_frontier:
                        frontier[:] = [e for e in frontier if e["id"] != nbr]
                        in_frontier.discard(nbr)
                        added.append(f"update {nbr}")
                    else:
                        added.append(f"push {nbr}")
                    frontier.append({"id": nbr, "g": next_g, "h": h[nbr], "f": next_g + h[nbr]})
                    in_frontier.add(nbr)
                    continue
                if nbr in in_frontier:
                    if meta["reverse_neighbors"]:
                        parent[nbr] = cid
                    continue
                parent[nbr] = cid
                g_scores[nbr] = next_g
                frontier.append({"id": nbr, "g": next_g, "h": h[nbr], "f": next_g + h[nbr]})
                in_frontier.add(nbr)
                added.append(f"push {nbr}")

        _apply_frontier_scores(frontier, h, g_scores)
        if meta["sort_fn"]:
            frontier.sort(key=meta["sort_fn"])
        rows.append(
            {
                "步": step,
                "算法": meta["label"],
                "取出动作": meta["pop_code"],
                "取出节点": cid,
                "frontier 取出前": _frontier_text(before, algo),
                "frontier 取出后": _frontier_text(after_pop, algo),
                "新加入 / 更新": "；".join(added) if added else "—",
                "下一轮 frontier": _frontier_text(frontier, algo),
                "visited": "→".join(visited_order),
                "到达?": reached,
            }
        )
        if reached:
            break

    return pd.DataFrame(rows)


def _candidate_label(nid: str, next_g: int, h_value: int, algo: str, parent: str) -> str:
    if algo == "bfs" or algo == "dfs":
        return f"{nid} ← {parent}"
    if algo == "ucs":
        return f"{nid}(g={next_g}) ← {parent}"
    if algo == "greedy":
        return f"{nid}(h={h_value}) ← {parent}"
    return f"{nid}(g={next_g}, h={h_value}, f={next_g + h_value}) ← {parent}"


def _decision_reason(chosen: dict, algo: str) -> str:
    meta = ALGO_META[algo]
    nid = chosen["id"]
    if algo == "bfs":
        return f"{nid} 最早进入候选节点列表"
    if algo == "dfs":
        return f"{nid} 是最后加入的候选节点"
    if algo == "ucs":
        return f"{nid} 的累计代价 g={chosen['g']} 最小"
    if algo == "greedy":
        return f"{nid} 的启发式 h={chosen['h']} 最小"
    if algo == "astar":
        return f"{nid} 的 f=g+h={chosen['f']} 最小"
    return meta["selection_rule"]


def algorithm_steps(algo: str, graph: dict | None = None, max_steps: int = 12) -> pd.DataFrame:
    """Reader-facing algorithm steps: choose, expand, and update candidates."""
    graph = graph or load_graph()
    start, goal = graph["start"], graph["goal"]
    h = {k: v["h"] for k, v in graph["nodes"].items()}
    adj = build_adjacency(graph["edges"])
    meta = ALGO_META[algo]

    frontier: list[dict] = [{"id": start, "g": 0, "h": h[start], "f": h[start]}]
    in_frontier = {start}
    visited: set[str] = set()
    visited_order: list[str] = []
    parent: dict[str, str] = {}
    g_scores: dict[str, int] = {start: 0}
    rows = []

    for step in range(1, max_steps + 1):
        if not frontier:
            break
        if meta["sort_fn"]:
            frontier.sort(key=meta["sort_fn"])
        before = [dict(entry) for entry in frontier]
        current = frontier.pop() if meta["pop_end"] else frontier.pop(0)
        cid = current["id"]
        in_frontier.discard(cid)

        if cid in visited:
            rows.append(
                {
                    "步骤": step,
                    "选择节点": cid,
                    "为什么选它": "该节点已经访问过，本轮跳过",
                    "扩展出的新候选": "—",
                    "下一轮待探索": _frontier_text(frontier, algo),
                    "已访问顺序": " → ".join(visited_order) or "∅",
                    "状态": "跳过",
                }
            )
            continue

        visited.add(cid)
        visited_order.append(cid)
        reached = cid == goal
        discovered: list[str] = []

        if not reached:
            neighbors = adj[cid]
            ordered = list(reversed(neighbors)) if meta["reverse_neighbors"] else neighbors
            for nbr, edge_cost in ordered:
                if nbr in visited:
                    continue
                next_g = g_scores[cid] + edge_cost
                if meta["mode"] == "cost":
                    if next_g >= g_scores.get(nbr, 10**9):
                        continue
                    g_scores[nbr] = next_g
                    parent[nbr] = cid
                    if nbr in in_frontier:
                        frontier[:] = [e for e in frontier if e["id"] != nbr]
                        in_frontier.discard(nbr)
                    frontier.append({"id": nbr, "g": next_g, "h": h[nbr], "f": next_g + h[nbr]})
                    in_frontier.add(nbr)
                    discovered.append(_candidate_label(nbr, next_g, h[nbr], algo, cid))
                    continue
                if nbr in in_frontier:
                    if meta["reverse_neighbors"]:
                        parent[nbr] = cid
                    continue
                parent[nbr] = cid
                g_scores[nbr] = next_g
                frontier.append({"id": nbr, "g": next_g, "h": h[nbr], "f": next_g + h[nbr]})
                in_frontier.add(nbr)
                discovered.append(_candidate_label(nbr, next_g, h[nbr], algo, cid))

        _apply_frontier_scores(frontier, h, g_scores)
        if meta["sort_fn"]:
            frontier.sort(key=meta["sort_fn"])
        rows.append(
            {
                "步骤": step,
                "选择节点": cid,
                "为什么选它": _decision_reason(current, algo),
                "扩展出的新候选": "；".join(discovered) if discovered else "—",
                "下一轮待探索": _frontier_text(frontier, algo),
                "已访问顺序": " → ".join(visited_order),
                "状态": "到达目标" if reached else "继续",
            }
        )
        if reached:
            break

    return pd.DataFrame(rows)


def algorithm_result(algo: str, graph: dict | None = None) -> pd.DataFrame:
    """One-row result table for the algorithm currently being studied."""
    graph = graph or load_graph()
    adj = build_adjacency(graph["edges"])
    result = run_all(graph)[algo]
    path = result["path"]
    return pd.DataFrame(
        [
            {
                "算法": f"{ALGO_META[algo]['label']} · {ALGO_META[algo]['name']}",
                "路径": " → ".join(path),
                "边数": max(len(path) - 1, 0),
                "总代价": path_cost(path, adj) if path else 0,
                "结论": ALGO_META[algo]["focus"],
            }
        ]
    )


def _expand_neighbors(
    current: str,
    g: int,
    adj: dict[str, list[tuple[str, int]]],
    visited: set[str],
    in_frontier: set[str],
    parent: dict[str, str],
    g_scores: dict[str, int],
    frontier: list,
    *,
    reverse_neighbors: bool = False,
    mode: str = "default",
) -> None:
    neighbors = adj[current]
    ordered = list(reversed(neighbors)) if reverse_neighbors else neighbors
    for nbr, edge_cost in ordered:
        if nbr in visited:
            continue
        next_g = g + edge_cost
        if mode == "cost":
            if next_g >= g_scores.get(nbr, 10**9):
                continue
            g_scores[nbr] = next_g
            parent[nbr] = current
            if nbr in in_frontier:
                frontier[:] = [e for e in frontier if e["id"] != nbr]
                in_frontier.discard(nbr)
            frontier.append({"id": nbr, "g": next_g, "h": 0, "f": next_g})
            in_frontier.add(nbr)
            continue
        if nbr in in_frontier:
            if reverse_neighbors:
                parent[nbr] = current
            continue
        parent[nbr] = current
        g_scores[nbr] = next_g
        frontier.append({"id": nbr, "g": next_g, "h": 0, "f": next_g})
        in_frontier.add(nbr)


def trace_search(
    algo: str,
    graph: dict | None = None,
    max_steps: int = 12,
) -> pd.DataFrame:
    """Compatibility wrapper: return the richer frontier-operation trace."""
    return operation_trace(algo, graph=graph, max_steps=max_steps)


def manual_bfs_two_steps() -> None:
    """手算 BFS 前两步，与网页动画对齐。"""
    print("初始 frontier = deque(['x'])")
    print("第 1 步：弹出 x，按字母序入队 c2, j, s1")
    print("  frontier = ['c2', 'j', 's1']")
    print("第 2 步：弹出 c2（队头），无新目标；再弹出 j…")
    print("  …直到队头为 s1 时展开，发现邻居 c1=目标")
    print("最终路径：x → s1 → c1（2 步，代价 8）")


def comparison_table(graph: dict | None = None) -> pd.DataFrame:
    graph = graph or load_graph()
    expected = graph["expected"]
    results = run_all(graph)
    labels = {"dfs": "DFS", "bfs": "BFS", "ucs": "UCS", "greedy": "Greedy", "astar": "A*"}
    rows = []
    for key, label in labels.items():
        r = results[key]
        exp = expected[key]
        rows.append(
            {
                "算法": label,
                "路径": "→".join(r["path"]),
                "步数": r["steps"],
                "代价": r["cost"],
                "与网页": "✓" if r["path"] == exp["path"] and r["cost"] == exp["cost"] else "✗",
            }
        )
    return pd.DataFrame(rows)


def plot_campus(
    path: list[str] | None = None,
    *,
    title: str = "校园搜索图",
    highlight: list[str] | None = None,
) -> None:
    graph = load_graph()
    configure_matplotlib()
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    _draw_campus_map(ax, graph, path=path, highlight=highlight, title=title)
    plt.tight_layout()
    plt.show()


def _edge_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def _path_edges(path: list[str] | None) -> set[tuple[str, str]]:
    if not path:
        return set()
    return {_edge_key(path[i], path[i + 1]) for i in range(len(path) - 1)}


def _label_offset(a: str, b: str) -> tuple[float, float]:
    x1, y1 = LAYOUT[a]
    x2, y2 = LAYOUT[b]
    dx, dy = x2 - x1, y2 - y1
    norm = float(np.hypot(dx, dy)) or 1.0
    return (-dy / norm * 0.08, dx / norm * 0.08)


def _draw_campus_map(
    ax,
    graph: dict,
    *,
    path: list[str] | None = None,
    highlight: list[str] | None = None,
    title: str = "Campus search map",
    compact: bool = False,
) -> None:
    """Draw a polished route map shared by single-path and comparison plots."""
    adj = build_adjacency(graph["edges"])
    active_nodes = set(path or []) | set(highlight or [])
    active_edges = _path_edges(path)
    start, goal = graph["start"], graph["goal"]

    ax.set_facecolor("#fbfcfd")
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (-0.08, 0.28),
            5.16,
            2.44,
            boxstyle="round,pad=0.04,rounding_size=0.08",
            facecolor="#ffffff",
            edgecolor="#e5e7eb",
            linewidth=1.2,
            zorder=0,
        )
    )
    ax.add_patch(
        mpatches.Rectangle(
            (-0.15, 1.42),
            5.35,
            0.18,
            facecolor="#eef2f7",
            edgecolor="none",
            alpha=0.8,
            zorder=0,
        )
    )

    drawn = set()
    for a, neighbors in adj.items():
        for b, cost in neighbors:
            key = _edge_key(a, b)
            if key in drawn:
                continue
            drawn.add(key)
            x1, y1 = LAYOUT[a]
            x2, y2 = LAYOUT[b]
            is_path = key in active_edges
            color = "#2563eb" if is_path else "#cbd5e1"
            width = 3.4 if is_path else 1.8
            (line,) = ax.plot(
                [x1, x2],
                [y1, y2],
                color=color,
                linewidth=width,
                solid_capstyle="round",
                alpha=0.95 if is_path else 0.86,
                zorder=2 if is_path else 1,
            )
            line.set_path_effects([pe.Stroke(linewidth=width + 2.0, foreground="#ffffff", alpha=0.95), pe.Normal()])
            dx, dy = _label_offset(a, b)
            ax.text(
                (x1 + x2) / 2 + dx,
                (y1 + y2) / 2 + dy,
                f"{cost}",
                ha="center",
                va="center",
                fontsize=8 if compact else 9,
                color="#1d4ed8" if is_path else "#64748b",
                bbox=dict(
                    boxstyle="round,pad=0.18,rounding_size=0.08",
                    facecolor="#eff6ff" if is_path else "#ffffff",
                    edgecolor="#bfdbfe" if is_path else "#e2e8f0",
                    linewidth=0.9,
                    alpha=0.98,
                ),
                zorder=5,
            )

    for nid, (px, py) in LAYOUT.items():
        name = graph["nodes"][nid]["name"]
        h = graph["nodes"][nid]["h"]
        face = "#ffffff"
        edge = "#94a3b8"
        text_color = "#0f172a"
        if nid in active_nodes:
            face = "#eff6ff"
            edge = "#2563eb"
            text_color = "#1e3a8a"
        if nid == start:
            face = "#ecfdf5"
            edge = "#059669"
            text_color = "#065f46"
        if nid == start and nid in active_nodes:
            face = "#d1fae5"
            edge = "#059669"
            text_color = "#065f46"
        if nid == goal:
            face = "#fff7ed"
            edge = "#f97316"
            text_color = "#9a3412"
        if nid == goal and nid in active_nodes:
            face = "#ffedd5"
            edge = "#f97316"
            text_color = "#9a3412"
        radius = 0.17 if compact else 0.23
        ax.add_patch(
            mpatches.Circle(
                (px, py),
                radius,
                facecolor=face,
                edgecolor=edge,
                linewidth=1.8,
                zorder=6,
            )
        )
        ax.text(
            px,
            py,
            nid,
            ha="center",
            va="center",
            fontsize=8 if compact else 9,
            color=text_color,
            zorder=7,
            fontweight="bold",
        )
        if not compact:
            ax.text(
                px,
                py - 0.43,
                f"{name}  h={h}",
                ha="center",
                va="top",
                fontsize=8,
                color="#475569",
                zorder=7,
                bbox=dict(boxstyle="round,pad=0.14,rounding_size=0.06", facecolor="#ffffff", edgecolor="none", alpha=0.82),
            )

    if path:
        path_text = " -> ".join(path)
        cost = path_cost(path, adj)
        ax.text(
            0.04,
            0.06,
            f"path: {path_text}   cost={cost}",
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=8 if compact else 10,
            color="#334155",
            bbox=dict(boxstyle="round,pad=0.28,rounding_size=0.08", facecolor="#ffffff", edgecolor="#e2e8f0"),
            zorder=8,
        )

    ax.set_title(title, loc="left", fontsize=10 if compact else 14, fontweight="bold", color="#0f172a", pad=10)
    ax.set_xlim(-0.25, 5.15)
    ax.set_ylim(0.18, 2.85)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")


def plot_all_paths(graph: dict | None = None) -> None:
    graph = graph or load_graph()
    configure_matplotlib()
    results = run_all(graph)
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.4))
    labels = ["dfs", "bfs", "ucs", "greedy", "astar"]
    for ax, key in zip(axes.flat, labels):
        path = results[key]["path"]
        cost = results[key]["cost"]
        title = f"{ALGO_META[key]['label']} · cost {cost}"
        _draw_campus_map(ax, graph, path=path, title=title, compact=True)
    axes.flat[-1].axis("off")
    plt.suptitle("同一校园图上的五种搜索结果", y=0.99, fontsize=15, fontweight="bold")
    plt.tight_layout()
    plt.show()


def _run(
    adj: dict[str, list[tuple[str, int]]],
    h: dict[str, int],
    start: str,
    goal: str,
    *,
    reverse_neighbors: bool = False,
    pop_end: bool = False,
    sort_fn=None,
    mode: str = "default",
) -> tuple[list[str], int]:
    frontier: list[dict] = [{"id": start, "g": 0, "h": h[start], "f": h[start]}]
    in_frontier = {start}
    visited: set[str] = set()
    parent: dict[str, str] = {}
    g_scores: dict[str, int] = {start: 0}

    while frontier:
        if sort_fn:
            frontier.sort(key=sort_fn)
        current = frontier.pop() if pop_end else frontier.pop(0)
        cid = current["id"]
        in_frontier.discard(cid)
        if cid in visited:
            continue
        visited.add(cid)
        g = g_scores[cid]

        if cid == goal:
            return reconstruct(parent, goal), g

        _expand_neighbors(
            cid,
            g,
            adj,
            visited,
            in_frontier,
            parent,
            g_scores,
            frontier,
            reverse_neighbors=reverse_neighbors,
            mode=mode,
        )
        for entry in frontier:
            nid = entry["id"]
            entry["h"] = h[nid]
            entry["f"] = g_scores.get(nid, entry["g"]) + h[nid]

    return [], 0


def run_all(graph: dict | None = None) -> dict[str, dict]:
    graph = graph or load_graph()
    start, goal = graph["start"], graph["goal"]
    h = {k: v["h"] for k, v in graph["nodes"].items()}
    adj = build_adjacency(graph["edges"])

    algos: dict[str, Callable[[], tuple[list[str], int]]] = {
        "dfs": lambda: _run(adj, h, start, goal, reverse_neighbors=True, pop_end=True),
        "bfs": lambda: _run(adj, h, start, goal),
        "ucs": lambda: _run(
            adj, h, start, goal, sort_fn=lambda e: (e["g"], e["id"]), mode="cost"
        ),
        "greedy": lambda: _run(adj, h, start, goal, sort_fn=lambda e: (e["h"], e["id"])),
        "astar": lambda: _run(
            adj,
            h,
            start,
            goal,
            sort_fn=lambda e: (e["f"], e["h"], e["g"], e["id"]),
            mode="cost",
        ),
    }

    out: dict[str, dict] = {}
    for key, fn in algos.items():
        path, _g = fn()
        cost = path_cost(path, adj) if path else 0
        out[key] = {"path": path, "steps": max(len(path) - 1, 0), "cost": cost}
    return out


def print_comparison(graph: dict | None = None) -> None:
    df = comparison_table(graph)
    print(df.to_string(index=False))


def verify_against_web(graph: dict | None = None) -> None:
    graph = graph or load_graph()
    results = run_all(graph)
    for key, exp in graph["expected"].items():
        r = results[key]
        assert r["path"] == exp["path"], f"{key} path mismatch"
        assert r["cost"] == exp["cost"], f"{key} cost mismatch"
    print("✓ 五种算法路径与 ch5.html 完全一致")


if __name__ == "__main__":
    print("校园搜索图 — Python 复现（与 ch5 网页同一案例）\n")
    print_comparison()


# ── CodeLens：逐步展示全部变量 ─────────────────────────────


def codelens_build_adjacency(graph: dict | None = None) -> list[Frame]:
    """逐条边构建邻接表，每加一条边输出一次 adj。"""
    graph = graph or load_graph()
    adj: dict[str, list[tuple[str, int]]] = {}
    frames: list[Frame] = [
        Frame(0, "adj = {}", "初始化空邻接表", {"adj": adj, "已处理边": 0}),
    ]
    for i, edge in enumerate(graph["edges"], start=1):
        a, b, cost = edge["from"], edge["to"], edge["cost"]
        adj.setdefault(a, []).append((b, cost))
        adj.setdefault(b, []).append((a, cost))
        for neighbors in adj.values():
            neighbors.sort(key=lambda x: x[0])
        snap = {k: list(v) for k, v in adj.items()}
        frames.append(
            Frame(
                i,
                f"添加 {a}↔{b} cost={cost}",
                f"第 {i} 条边写入邻接表",
                {"adj": snap, "边": f"{a}↔{b}", "代价": cost},
            )
        )
    return frames


def codelens_bfs(graph: dict | None = None) -> list[Frame]:
    """BFS CodeLens：每次 pop / 入队都记录 queue、visited、parent。"""
    graph = graph or load_graph()
    start, goal = graph["start"], graph["goal"]
    adj = build_adjacency(graph["edges"])
    frontier: list[str] = [start]
    visited: set[str] = set()
    parent: dict[str, str] = {}
    frames: list[Frame] = []
    step = 0
    frames.append(
        Frame(
            step,
            "frontier = [start]",
            "BFS 初始化：队列仅含起点",
            {"frontier": list(frontier), "visited": set(visited), "parent": dict(parent)},
        )
    )
    while frontier:
        step += 1
        current = frontier.pop(0)
        if current in visited:
            frames.append(
                Frame(
                    step,
                    f"current={current} 已访问，跳过",
                    "重复入队节点被忽略",
                    {"frontier": list(frontier), "visited": set(visited), "current": current},
                )
            )
            continue
        visited.add(current)
        frames.append(
            Frame(
                step,
                f"current = frontier.pop(0)  # {current}",
                "弹出队头并标记 visited",
                {
                    "current": current,
                    "frontier": list(frontier),
                    "visited": set(visited),
                    "到达目标?": current == goal,
                },
            )
        )
        if current == goal:
            path = reconstruct(parent, goal)
            frames.append(
                Frame(
                    step + 1,
                    "break",
                    "发现目标，沿 parent 回溯路径",
                    {"path": path, "步数": len(path) - 1, "代价": path_cost(path, adj)},
                )
            )
            break
        for nbr, edge_cost in adj[current]:
            if nbr not in visited and nbr not in frontier:
                parent[nbr] = current
                frontier.append(nbr)
                frames.append(
                    Frame(
                        step,
                        f"frontier.append({nbr})  # 经 {current} 来，边权 {edge_cost}",
                        f"扩展邻居 {nbr}",
                        {
                            "扩展": nbr,
                            "经": current,
                            "frontier": list(frontier),
                            "parent": dict(parent),
                        },
                    )
                )
    return frames


def codelens_dfs(graph: dict | None = None) -> list[Frame]:
    """DFS CodeLens：栈顶弹出，邻居逆序入栈（与网页一致）。"""
    graph = graph or load_graph()
    start, goal = graph["start"], graph["goal"]
    adj = build_adjacency(graph["edges"])
    stack = [start]
    visited: set[str] = set()
    parent: dict[str, str] = {}
    frames: list[Frame] = []
    step = 0
    frames.append(
        Frame(0, "stack=[start]", "DFS 初始化", {"stack": list(stack), "visited": set(visited)}),
    )
    while stack:
        step += 1
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        frames.append(
            Frame(
                step,
                f"current = stack.pop()  # {current}",
                "栈顶弹出",
                {"current": current, "stack": list(stack), "visited": set(visited)},
            )
        )
        if current == goal:
            path = reconstruct(parent, goal)
            frames.append(
                Frame(step, "break", "到达目标", {"path": path, "代价": path_cost(path, adj)}),
            )
            break
        for nbr, edge_cost in reversed(adj[current]):
            if nbr not in visited and nbr not in stack:
                parent[nbr] = current
                stack.append(nbr)
                frames.append(
                    Frame(
                        step,
                        f"stack.append({nbr})",
                        f"逆序入栈邻居 {nbr} (cost={edge_cost})",
                        {"stack": list(stack), "parent": dict(parent)},
                    )
                )
    return frames


def print_codelens(frames: list[Frame], limit: int | None = None) -> None:
    from common.codelens import print_frames

    print_frames(frames, stop=limit)


def animate_bfs_queue() -> None:
    animate_search_frontier("bfs")


def animate_dfs_stack() -> None:
    animate_search_frontier("dfs")


def _frontier_items(text: object) -> list[str]:
    value = str(text)
    if not value or value == "∅":
        return []
    return [part.strip() for part in value.split("|") if part.strip()]


def _pop_label(items: list[str], node: str) -> str | None:
    for item in items:
        if item == node or item.startswith(f"{node} "):
            return item
    return items[-1] if items else None


def animate_search_frontier(algo: str) -> None:
    """Animate the exact frontier operation table for any graph-search algorithm."""
    from common.viz_anim import animate_container

    meta = ALGO_META[algo]
    trace = operation_trace(algo)
    snapshots = []
    for _, row in trace.iterrows():
        items = _frontier_items(row["frontier 取出前"])
        node = str(row["取出节点"])
        added = str(row["新加入 / 更新"])
        next_frontier = str(row["下一轮 frontier"])
        snapshots.append(
            {
                "step": int(row["步"]),
                "items": items,
                "pop": _pop_label(items, node),
                "action": f"{row['取出动作']} -> {node}",
                "extra": f"加入/更新: {added}  |  下一轮: {next_frontier}",
            }
        )
    animate_container(
        snapshots,
        kind=meta["container"],
        caption=f"{meta['label']}: {meta['container_name']} frontier 动画",
    )
