"""Rich notebook cells for chapter 6."""

from __future__ import annotations

from notebook_content import callout, code, md, section

BOOT = """
import sys
from pathlib import Path
ROOT = Path.cwd()
if not (ROOT / "labs").exists() and (ROOT.parent / "labs").exists():
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "labs" / "ch06"))
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "Arial Unicode MS", "DejaVu Sans"]
from IPython.display import display
from reasoning import *
""".strip()


def notebooks() -> dict[str, list]:
    return {
        "ch06_forward_backward_chain.ipynb": _forward_backward(),
        "ch06_graph_reasoning.ipynb": _graph(),
    }


def _forward_backward() -> list:
    return [
        md(
            """# 第 6 章 · 前向链与后向链

> 配套 [ch6.html](../ch6.html) · **15 分钟** · 案例：苏格拉底三段论

**带走什么**：能判断何时**从事实前推**（前向链）、何时**从目标倒推**（后向链）。"""
        ),
        section("1. 规则库与事实", "推理 = 在既定表征下把隐含结论显式化。下面与网页使用同一 JSON 规则库。"),
        code(
            f"""{BOOT}
data = load_rules()
print("事实库:", ", ".join(data["facts"]))
print("目标:", data["goal"])
for r in data["rules"]:
    print(f"  {{r['id']}}: {{r['if'][0]}} ⇒ {{r['then']}}")"""
        ),
        section("2. 前向链：数据驱动撒网", "**心智模型**：事实池 + 规则扫描；能推则推，直到推不动。"),
        callout("预测", "第一轮哪条规则会被触发？会新增哪条事实？"),
        code(
            """for line in forward_chain():
    print(line)
print("\\n↔ 网页动画：每轮高亮被触发的规则 ✓")"""
        ),
        callout("误区", "前向链不一定比后向链「更正确」——方向不同，都依赖规则是否完备。"),
        section("3. 后向链：从目标倒推", "**心智模型**：目标栈 → 匹配规则 → 子目标 → 直到命中事实。"),
        code(
            """print("后向证明 trace：")
for line in backward_chain():
    print(" ", line)"""
        ),
        callout(
            "自测",
            "若只有目标、事实很少，你会选前向还是后向？本例目标明确，后向更聚焦。",
        ),
        md(
            """### 小结
| 方向 | 驱动 | 本例 |
|------|------|------|
| 前向 | 已知事实 | 多轮扫描直到推出「终有一死(苏格拉底)」 |
| 后向 | 目标 | 终有一死 → 会死 → 人 → 命中事实 |

回到 [ch6.html](../ch6.html) 对比两种链的步进动画。"""
        ),
    ]


def _graph() -> list:
    return [
        md(
            """# 第 6 章 · 图谱多跳与路径排序

> 配套 [ch6.html](../ch6.html) · 案例：鲁迅 / 莫言文学知识图谱"""
        ),
        section("1. 知识图谱结构", "三元组 (头, 关系, 尾) + **关系类型约束**——不是裸 BFS。"),
        code(
            BOOT
            + """
kg = load_kg()
print("查询模式:", kg["query"]["pattern"])
print("标准答案 Y =", kg["query"]["answer_y"])
print("\\n边（节选）:")
for h, r, t in kg["edges"][:8]:
    print(f"  ({h}) --[{r}]--> ({t})")"""
        ),
        section("2. 多跳查询", "模板 `(鲁迅,创作,?X)` 且 `(?X,发表于,?Y)` 像 SQL JOIN。"),
        callout("预测", "鲁迅创作的作品有哪些？它们是否都发表于同一期刊？"),
        code(
            """for line in graph_multihop():
    print(line)"""
        ),
        callout(
            "误区",
            "图谱推理 ≠ 忽略边类型的图搜索——否则会连出「鲁迅→发表于→桌子」这类荒谬路径。",
        ),
        section("3. 软自洽：路径计票排序", "缺直接边时，多条间接路径**计票**；硬约束仍守关系类型。"),
        code("path_ranking()"),
        md(
            """### 思考题
- 若去掉「发表于」约束，会多出哪些错误答案？
- 「莫言→获得→诺奖→代表→红高粱」哪一段是软推断？

实现见 `labs/ch06/reasoning.py`。"""
        ),
    ]
