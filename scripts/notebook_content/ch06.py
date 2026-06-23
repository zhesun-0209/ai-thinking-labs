"""第 6 章 notebook — 与 ch5 同等逐步密度。"""

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
            "苏格拉底三段论：逐步展示规则扫描、事实池增长与目标证明。",
            ["逐步模拟前向链", "观察 known 事实池如何扩展", "倒推后向链", "对照 ch6 网页动画"],
            "../ch6.html",
        ),
        rs.section("1", "规则库与事实"),
        rs.reading(
            "每条规则形如 **IF 条件 THEN 结论**。已知事实放在 `known` 集合；每轮扫描全部规则，触发则把结论加入 known。",
            "目标：证明「苏格拉底终有一死」。",
        ),
        rs.listing("规则形式", "IF 人(x) THEN 会死(x)\nIF 会死(x) THEN 终有一死(x)"),
        *rs.stepcode(
            B,
            "data = load_rules()",
            "display(facts_goal_table())",
            "display(rules_table())",
        ),
        rs.self_check("初始 known 里有什么？", answer="人(苏格拉底)"),
        rs.section("2", "前向链：逐轮扫描"),
        rs.subsection("2.1", "扫描循环", "每轮遍历规则列表；条件已在 known 中则结论入池，直到无新事实。"),
        rs.listing(
            "前向链",
            "while changed:\n  for rule in rules:\n    if all(cond in known for cond in rule.if):\n      known.add(rule.then)",
        ),
        *rs.stepcode(
            "fc_frames = codelens_forward_chain()",
            "animate_forward_chain()",
            "display(forward_chain_table())",
        ),
        rs.self_check("第一轮新增哪条事实？", answer="会死(苏格拉底)，由 R1 触发。"),
        rs.self_check("几轮后目标成立？", answer="第二轮 R2 推出终有一死(苏格拉底)。"),
        rs.section("3", "后向链：目标分解"),
        rs.reading("从目标出发，匹配规则结论，把前提变为子目标，直到子目标在 known 中。"),
        rs.listing("后向", "prove(goal):\n  match rule where rule.then == goal\n  prove each subgoal in rule.if"),
        *rs.stepcode("display(backward_chain_table())"),
        rs.section("4", "前向 vs 后向"),
        rs.reading(
            "**前向**：数据驱动，适合已知事实多、目标未知的诊断。",
            "**后向**：目标驱动，适合证明特定结论。",
        ),
        rs.self_check("本例为何前向两轮就够？", answer="规则链短，事实少，每轮都能触发新结论。"),
        rs.summary(
            "前向链用 known 事实池驱动推理；后向链从 goal 倒推子目标。",
            "对照 [ch6.html](../ch6.html) 步进动画验证每一轮 known 变化。",
        ),
        rs.exercises(
            "若增加规则「哲学家(x)→人(x)」，需几轮才能证明目标？",
            "后向链若先匹配 R1 而非 R2，证明路径有何不同？",
        ),
    ]


def _graph() -> list:
    Bg = boot("ch06", "from reasoning import *")
    return [
        rs.chapter_link(
            "第 6 章 · 图谱多跳与路径排序",
            "鲁迅/莫言图谱：带关系类型的多跳 JOIN 与软路径计票。",
            ["理解三元组存储", "多跳查询逐步执行", "关系约束为何必要", "软路径计票"],
            "../ch6.html",
        ),
        rs.section("1", "三元组与查询模板"),
        rs.reading("知识图谱存 **(头实体, 关系, 尾实体)**。查询模板约束关系类型，避免语义错误的边。"),
        rs.listing("模板", "(鲁迅, 创作, ?X) AND (?X, 发表于, ?Y)"),
        *rs.stepcode(
            Bg,
            "kg = load_kg()",
            "display(kg_query_table())",
        ),
        rs.section("2", "边列表与邻接"),
        *rs.stepcode(
            "display(graph_edges_table())",
            "adj = build_adj(kg)",
            "display(entity_out_edges('鲁迅'))",
        ),
        rs.self_check("「发表于」边连接什么？", answer="作品 → 刊物/地点。"),
        rs.section("3", "多跳执行（逐步）"),
        rs.reading("第一跳：找鲁迅创作的作品；第二跳：找各作品发表于何处；第三跳：求共同 Y。"),
        rs.listing("JOIN", "works = {t | (鲁迅,创作,t) in edges}\nvenues[w] = {t | (w,发表于,t) in edges}"),
        *rs.stepcode("display(graph_multihop_table())"),
        rs.self_check("为何必须约束「发表于」？", answer="否则创作边与人物边混连，语义错误。"),
        rs.section("4", "软路径计票"),
        rs.reading("多条推理路径对同一答案投票；得分高者更可信。"),
        *rs.stepcode("display(path_ranking_table())", "plot_path_ranking()"),
        rs.section("5", "硬约束 vs 软推断"),
        rs.reading("**硬约束**：关系类型必须匹配模板。**软推断**：多路径聚合得分。"),
        rs.summary(
            "多跳 = 带关系约束的图 JOIN；软路径计票用于不确定性下的排序。",
            "对照 [ch6.html](../ch6.html) 查看路径高亮。",
        ),
        rs.exercises(
            "若去掉「发表于」约束，会多出哪些错误 Y？",
            "计票得分相同时如何打破平局？",
        ),
    ]
