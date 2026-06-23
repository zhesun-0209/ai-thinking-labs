# Jupyter Notebook 索引

配套《AI思维》第 5–12 章，采用 **[Runestone Academy · PythonDS](https://runestone.academy/ns/books/published/pythonds/index.html)** 式结构：

| 组件 | 作用 |
|------|------|
| **Reading** | 长文概念讲解 |
| **Listing** | 伪代码 / 算法清单 |
| **ActiveCode** | 可运行 Python（真实 execute） |
| **CodeLens** | 分步打印**全部变量状态**（frontier、known、tokens…） |
| **Self-Check** | 预测题 + 可展开答案 |

## 阅读

[索引页](./index.html) → **在线阅读** → `rendered/*.html`（Jupyter Lab 模板 + 嵌入图表）

## 维护

```bash
pip install -r ../scripts/requirements-notebooks.txt
python ../scripts/generate_all_notebooks.py   # 从 scripts/notebook_content/ 生成
python ../scripts/render_notebooks.py
```

内容定义在 `scripts/notebook_content/`；CodeLens 帧在 `labs/common/codelens.py` 与各章 `labs/chNN/` 模块。
