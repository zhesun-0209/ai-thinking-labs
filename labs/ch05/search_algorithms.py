"""Campus graph search algorithms — aligned with ch5.html / app.js."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path

GRAPH_PATH = Path(__file__).resolve().parent.parent / "common" / "campus_graph.json"


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


def _run(
    name: str,
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

    algos = {
        "dfs": lambda: _run("dfs", adj, h, start, goal, reverse_neighbors=True, pop_end=True),
        "bfs": lambda: _run("bfs", adj, h, start, goal),
        "ucs": lambda: _run(
            "ucs",
            adj,
            h,
            start,
            goal,
            sort_fn=lambda e: (e["g"], e["id"]),
            mode="cost",
        ),
        "greedy": lambda: _run(
            "greedy",
            adj,
            h,
            start,
            goal,
            sort_fn=lambda e: (e["h"], e["id"]),
        ),
        "astar": lambda: _run(
            "astar",
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
    graph = graph or load_graph()
    expected = graph["expected"]
    results = run_all(graph)
    labels = {"dfs": "DFS", "bfs": "BFS", "ucs": "UCS", "greedy": "Greedy", "astar": "A*"}
    print("| 算法 | 路径 | 步数 | 代价 | 与网页一致 |")
    print("|------|------|------|------|------------|")
    for key, label in labels.items():
        r = results[key]
        exp = expected[key]
        path_str = "→".join(r["path"])
        ok = r["path"] == exp["path"] and r["cost"] == exp["cost"]
        print(f"| {label} | {path_str} | {r['steps']} | {r['cost']} | {'✓' if ok else '✗'} |")


if __name__ == "__main__":
    print("校园搜索图 — Python 复现（与 ch5 网页同一案例）\n")
    print_comparison()
