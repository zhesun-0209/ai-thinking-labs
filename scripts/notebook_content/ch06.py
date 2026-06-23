"""Runestone-style Chapter 6 notebooks."""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import boot, flatten

B = boot("ch06", "from reasoning import *\nfrom common.codelens import print_frames as print_codelens")


def notebooks() -> dict[str, list]:
    return {
        "ch06_forward_backward_chain.ipynb": flatten(_forward()),
        "ch06_graph_reasoning.ipynb": flatten(_graph()),
    }


def _forward() -> list[list]:
    return [
        rs.chapter(
            "第 6 章 · 前向链与后向链",
            "Runestone 式阅读 + CodeLens 展示规则库**每一轮**扫描与事实池变化。",
            ["能逐步模拟前向链", "能倒推后向链子目标", "能判断何时用前向/后向"],
        ),
        rs.section("1", "Reading · 推理 = 显式化隐含结论"),
        rs.reading(
            "**前向链（forward chaining）** 从已知事实出发，反复扫描规则「若条件成立则结论入池」。",
            "**后向链（backward chaining）** 从目标出发，分解子目标直到命中事实库。",
        ),
        rs.listing(
            "前向链核心循环",
            """while 有新事实:
    for rule in rules:
        if rule.if in known and rule.then not in known:
            known.add(rule.then)""",
        ),
        *rs.activecode(
            B,
            "data = load_rules()",
            "print('事实库:', data['facts'])",
            "print('规则:')",
            "for r in data['rules']: print(' ', r['id'], r['if'], '⇒', r['then'])",
            caption="加载规则库",
        ),
        rs.self_check("第一轮哪条规则会被触发？", answer="R1: 人(苏格拉底) ⇒ 会死(苏格拉底)"),
        rs.section("2", "CodeLens · 前向链逐步"),
        *rs.activecode(
            "fc = codelens_forward_chain()",
            "print_codelens(fc)",
            caption="每一轮 known 集合变化",
        ),
        *rs.activecode(
            "for line in forward_chain(): print(line)",
            caption="文本 log 对照",
        ),
        rs.section("3", "后向链 CodeLens（目标驱动）"),
        rs.listing("后向链", "goal → 匹配规则 → subgoals → 直到 fact"),
        *rs.activecode(
            "for line in backward_chain(): print(' ', line)",
            caption="后向 trace",
        ),
        rs.summary("前向撒网、后向聚焦；方向不同，都依赖规则完备性。"),
    ]


def _graph() -> list[list]:
    return [
        rs.chapter(
            "第 6 章 · 图谱多跳与路径排序",
            "三元组 + 关系类型约束；CodeLens 式展示多跳 JOIN 与软路径计票。",
            ["能执行模板多跳查询", "能解释关系类型约束", "能读路径计票表"],
        ),
        rs.section("1", "Reading · 图谱不是裸 BFS"),
        rs.reading("边 `(鲁迅,创作,狂人日记)` 的**关系类型**是查询的一部分。"),
        *rs.activecode(
            boot("ch06", "from reasoning import *"),
            "kg = load_kg()",
            "print('模式', kg['query']['pattern'])",
            "print('答案 Y =', kg['query']['answer_y'])",
            "for h,r,t in kg['edges'][:6]: print(f'  ({h})-[{r}]->({t})')",
            caption="加载 KG",
        ),
        rs.section("2", "ActiveCode · 多跳查询逐步"),
        *rs.activecode(
            "for line in graph_multihop(): print(line)",
            caption="鲁迅 → 作品 → 发表于",
        ),
        rs.self_check(
            "去掉「发表于」约束会怎样？",
            answer="会连出语义荒谬的路径，如错把「获得」当发表。",
        ),
        rs.section("3", "路径软排序"),
        *rs.activecode("path_ranking()", caption="路径计票明细"),
        rs.exercises("画出 backward 与 forward 在同一规则库上的搜索树差异。"),
    ]
