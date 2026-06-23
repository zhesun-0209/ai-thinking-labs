"""Campus graph search algorithms — pedagogical API for ch5 notebook."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys_path_common = Path(__file__).resolve().parent.parent
import sys as _sys

if str(sys_path_common) not in _sys.path:
    _sys.path.insert(0, str(sys_path_common))
from common.codelens import Frame  # noqa: E402

GRAPH_PATH = Path(__file__).resolve().parent.parent / "common" / "campus_graph.json"

# 与 ch5.html 地图布局大致一致（仅用于可视化）
LAYOUT = {
    "x": (0.0, 1.0),
    "c2": (0.0, 2.2),
    "j": (1.4, 2.0),
    "s2": (2.6, 2.0),
    "s1": (1.4, 0.6),
    "t": (2.8, 0.6),
    "c1": (4.0, 0.6),
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
    """逐步 trace：弹出节点、frontier、visited、是否到达目标。"""
    graph = graph or load_graph()
    start, goal = graph["start"], graph["goal"]
    h = {k: v["h"] for k, v in graph["nodes"].items()}
    adj = build_adjacency(graph["edges"])

    cfg = {
        "dfs": dict(reverse_neighbors=True, pop_end=True, sort_fn=None, mode="default"),
        "bfs": dict(reverse_neighbors=False, pop_end=False, sort_fn=None, mode="default"),
        "ucs": dict(
            reverse_neighbors=False,
            pop_end=False,
            sort_fn=lambda e: (e["g"], e["id"]),
            mode="cost",
        ),
        "greedy": dict(
            reverse_neighbors=False,
            pop_end=False,
            sort_fn=lambda e: (e["h"], e["id"]),
            mode="default",
        ),
        "astar": dict(
            reverse_neighbors=False,
            pop_end=False,
            sort_fn=lambda e: (e["f"], e["h"], e["g"], e["id"]),
            mode="cost",
        ),
    }[algo]

    frontier: list[dict] = [{"id": start, "g": 0, "h": h[start], "f": h[start]}]
    in_frontier = {start}
    visited: set[str] = set()
    parent: dict[str, str] = {}
    g_scores: dict[str, int] = {start: 0}
    rows = []

    for step in range(1, max_steps + 1):
        if not frontier:
            break
        if cfg["sort_fn"]:
            frontier.sort(key=cfg["sort_fn"])
        current = frontier.pop() if cfg["pop_end"] else frontier.pop(0)
        cid = current["id"]
        if cid in visited:
            continue
        visited.add(cid)
        g = g_scores[cid]
        frontier_ids = [e["id"] for e in frontier]
        rows.append(
            {
                "步": step,
                "弹出": cid,
                "g": g,
                "h": h[cid],
                "frontier": "→".join(frontier_ids) or "∅",
                "visited": "→".join(sorted(visited)),
                "到达?": cid == goal,
            }
        )
        if cid == goal:
            break
        _expand_neighbors(
            cid,
            g,
            adj,
            visited,
            in_frontier,
            parent,
            g_scores,
            frontier,
            reverse_neighbors=cfg["reverse_neighbors"],
            mode=cfg["mode"],
        )
        for entry in frontier:
            nid = entry["id"]
            entry["h"] = h[nid]
            entry["f"] = g_scores.get(nid, entry["g"]) + h[nid]

    return pd.DataFrame(rows)


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
    fig, ax = plt.subplots(figsize=(8, 4.5))
    adj = build_adjacency(graph["edges"])
    drawn = set()
    for a, neighbors in adj.items():
        for b, cost in neighbors:
            key = tuple(sorted((a, b)))
            if key in drawn:
                continue
            drawn.add(key)
            x1, y1 = LAYOUT[a]
            x2, y2 = LAYOUT[b]
            ax.plot([x1, x2], [y1, y2], color="#bbb", linewidth=2, zorder=1)
            ax.text((x1 + x2) / 2, (y1 + y2) / 2, str(cost), fontsize=9, color="#666")

    for nid, (px, py) in LAYOUT.items():
        name = graph["nodes"][nid]["name"]
        h = graph["nodes"][nid]["h"]
        color = "#0d6b62"
        if highlight and nid in highlight:
            color = "#e67e22"
        if path and nid in path:
            color = "#c0392b"
        ax.scatter(px, py, s=400, c=color, zorder=3, edgecolors="white", linewidths=1.5)
        ax.text(px, py, f"{nid}\nh={h}", ha="center", va="center", fontsize=9, color="white", zorder=4, fontweight="bold")

    if path and len(path) > 1:
        xs = [LAYOUT[n][0] for n in path]
        ys = [LAYOUT[n][1] for n in path]
        ax.plot(xs, ys, color="#c0392b", linewidth=3, marker="o", markersize=6, zorder=2, label="path")
        ax.legend(loc="upper left")

    ax.set_title(title)
    ax.axis("off")
    plt.tight_layout()
    plt.show()


def plot_all_paths(graph: dict | None = None) -> None:
    graph = graph or load_graph()
    results = run_all(graph)
    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    labels = ["dfs", "bfs", "ucs", "greedy", "astar"]
    titles = ["DFS", "BFS", "UCS", "Greedy", "A*"]
    for ax, key, title in zip(axes.flat, labels, titles):
        path = results[key]["path"]
        adj = build_adjacency(graph["edges"])
        drawn = set()
        for a, neighbors in adj.items():
            for b, _ in neighbors:
                k = tuple(sorted((a, b)))
                if k in drawn:
                    continue
                drawn.add(k)
                x1, y1 = LAYOUT[a]
                x2, y2 = LAYOUT[b]
                ax.plot([x1, x2], [y1, y2], color="#ddd", linewidth=1.5, zorder=1)
        for nid, (px, py) in LAYOUT.items():
            ax.scatter(px, py, s=120, c="#0d6b62" if nid not in path else "#c0392b", zorder=2)
            ax.text(px, py - 0.15, nid, ha="center", fontsize=7)
        if len(path) > 1:
            xs = [LAYOUT[n][0] for n in path]
            ys = [LAYOUT[n][1] for n in path]
            ax.plot(xs, ys, color="#c0392b", linewidth=2, zorder=3)
        cost = results[key]["cost"]
        ax.set_title(f"{title}\n{'->'.join(path)} cost={cost}")
        ax.axis("off")
    axes.flat[-1].axis("off")
    plt.suptitle("Five search paths (same campus graph)", y=1.02)
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
    from common.viz_anim import animate_container, snapshots_from_codelens

    frames = codelens_bfs()
    snaps = snapshots_from_codelens(frames, key="frontier", kind="queue")
    animate_container(snaps, kind="queue", caption="BFS: queue state at each step (GIF)")


def animate_dfs_stack() -> None:
    from common.viz_anim import animate_container, snapshots_from_codelens

    frames = codelens_dfs()
    snaps = []
    for f in frames:
        raw = f.state.get("stack", [])
        items = list(raw) if isinstance(raw, (list, tuple)) else str(raw).split("→")
        snaps.append(
            {
                "step": f.step,
                "items": items,
                "pop": f.state.get("current"),
                "action": f.narrative,
                "extra": f"visited={f.state.get('visited', set())}",
            }
        )
    animate_container(snaps, kind="stack", caption="DFS: stack state at each step (GIF)")
