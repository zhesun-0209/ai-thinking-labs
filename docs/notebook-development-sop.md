# Notebook 代码实验开发 SOP

本 SOP 以第 5 章图搜索 notebook 为基准，用于开发第 6–12 章的 Python 代码实验页。

## 目标

每个 notebook 都应像一个可执行的学习产品，而不是工程 Demo。章节网页负责完整讲解，notebook 负责让读者运行同一案例、看见关键变量、过程表和结果图。

## 页面标准

- 首屏只说明本章会运行什么，不解释工程实现方式。
- 可见代码必须让读者学到核心写法：数据结构、核心函数、运行 cell、结果展示要在页面上看得到。
- 不使用“直接定义”“明确定义”“课程封装”“不下载”“本 notebook”等实现型措辞。
- 注释写学习动作和观察点，例如“构建邻接表”“查看队列展开过程”“按 f=g+h 选择节点”。
- 不出现网页对比、期望结果、校验、assert 作为章节主体内容。
- 每个核心算法或模型至少有一个运行 cell 展示过程表或关键中间变量，并生成结果图。

## 代码结构

按以下顺序组织 cell：

1. 依赖与显示设置  
   导入公开库，设置中文字体和图表参数。不要输出字体名、路径、环境诊断等工程信息。

2. 案例数据  
   在可见 cell 中给出本章最小可运行数据。读者下载 `.ipynb` 后，不应因为缺少本地数据而无法运行。

3. 数据视图  
   用表格展示输入数据、关键字段和含义。

4. 可视化函数  
   如果需要画图，画图函数本身可以写在 notebook 中。函数名应是领域动作，例如 `draw_search_result`，避免 `plot_campus` 这类隐藏大量逻辑的黑箱调用。

5. 核心算法或主流库调用  
   - 基础算法章节：写出 `def dfs`、`def bfs` 这类具体函数，让读者看到 frontier、visited、parent、score 如何变化。
   - 机器学习章节：优先调用 sklearn、scipy、torch、transformers 等主流封装；不要手搓读者不该手搓的工业模型。
   - 每个函数只承担一个清晰任务，避免一个 `run_all` 隐藏所有学习内容。

6. 逐个运行  
   每个算法或模型单独一个运行 cell：输出过程表、中间变量或训练摘要，并生成图。

7. 汇总  
   汇总路径、代价、指标、预测结果等学习结论。不要把汇总写成测试报告。

## 文案禁用清单

用户可见 notebook 和 rendered HTML 中不得出现：

- 直接定义
- 明确定义
- 准备公开库
- 本 notebook
- 不下载
- 课程封装
- 图像生成代码也放在
- 完整讲解请看
- 这里只保留
- 期望结果
- 与网页
- 校验

## 第 5 章验收基线

第 5 章当前满足的基线：

- 可见 cell 构建校园图和邻接表。
- 可见 cell 实现 `def dfs`、`def bfs`、`def ucs`、`def greedy`、`def astar`。
- 每个算法都有过程表和路径图。
- 页面不出现 `plot_campus`、`run_all(graph)`、`comparison_table(graph)`、`verify_against_web(graph)`。
- 页面不出现字体缺失 warning。
- 下载版 `.ipynb` 可在空目录独立执行。

## 本地验收

开发某一章时只生成并渲染相关 notebook：

```bash
python - <<'PY'
import sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
from generate_all_notebooks import write_notebook
from notebook_content import ch05
for name, cells in ch05.notebooks().items():
    write_notebook(name, cells)
PY
python scripts/render_notebooks.py ch05_campus_search.ipynb
```

将 `ch05` 和 notebook 文件名替换为当前章节。

验收时至少检查：

- `.ipynb` 执行无 error output。
- rendered HTML 不含禁用文案。
- rendered HTML 不含字体 warning：`Glyph`、`missing from font`、`findfont`。
- 下载版 `.ipynb` 拷到空目录后可执行。
- 浏览器页面无横向溢出，图表和表格完整显示。

## 推送节奏

批注阶段只做本地重生成和浏览器刷新。多个问题确认后再统一 commit、push、等待 Pages 部署。
