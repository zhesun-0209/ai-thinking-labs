# Jupyter Notebook

配套《AI思维》第 5–12 章：可下载运行的 Python 代码实验。首个代码单元内嵌本章所需源码和数据，不再联网下载仓库里的封装脚本。

## 阅读

从各章正文顶部的 **Python 代码实验** 进入本章 Notebook 列表。点击 **在线阅读** 进入 `rendered/*.html`，或直接下载 `.ipynb` 运行。

## 维护

章节 notebook 的产品化开发标准见 [`../docs/notebook-development-sop.md`](../docs/notebook-development-sop.md)。用户可见页面应遵守该 SOP 的文案、代码展开和验收要求。

```bash
pip install -r ../scripts/requirements-notebooks.txt
python ../scripts/generate_all_notebooks.py
python ../scripts/render_notebooks.py
```

内容定义：`scripts/notebook_content/` · 可视化：`labs/common/viz_anim.py`
