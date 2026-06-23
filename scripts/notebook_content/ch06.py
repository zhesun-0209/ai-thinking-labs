"""Chapter 6 executable notebooks."""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import boot, flatten

B = boot(
    "ch06",
    "from reasoning import *",
)


def notebooks() -> dict[str, list]:
    return {
        "ch06_forward_backward_chain.ipynb": flatten(_forward()),
        "ch06_graph_reasoning.ipynb": flatten(_graph()),
    }


def _forward() -> list:
    return [
        rs.chapter_link(
            "第 6 章 · 前向链与后向链",
            ["加载规则与事实", "运行前向链", "运行后向链"],
            "../ch6.html",
        ),
        rs.section("0", "环境与数据"),
        *rs.stepcode(
            B,
            "data = load_rules()",
            "display(facts_goal_table())",
            "display(rules_table())",
        ),
        rs.section("1", "前向链"),
        *rs.stepcode(
            "display(forward_chain_table())",
        ),
        rs.section("2", "后向链"),
        *rs.stepcode("display(backward_chain_table())"),
    ]


def _graph() -> list:
    Bg = boot("ch06", "from reasoning import *")
    return [
        rs.chapter_link(
            "第 6 章 · 图谱多跳与路径排序",
            ["加载三元组图谱", "运行多跳查询", "输出路径排序"],
            "../ch6.html",
        ),
        rs.section("0", "环境与数据"),
        *rs.stepcode(
            Bg,
            "kg = load_kg()",
            "display(kg_query_table())",
            "display(graph_edges_table())",
            "adj = build_adj(kg)",
            "display(entity_out_edges('鲁迅'))",
        ),
        rs.section("1", "多跳查询"),
        *rs.stepcode("display(graph_multihop_table())"),
        rs.section("2", "路径排序"),
        *rs.stepcode("display(path_ranking_table())", "plot_path_ranking()"),
    ]
