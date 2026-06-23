# Jupyter Notebook 索引

配套《AI思维》第 5–12 章：可下载运行的 Python 代码实验。首个代码单元会准备运行时脚本、数据和依赖，真实执行后导出为静态 HTML。

## 阅读

[index.html](./index.html) 默认展示核心 Notebook；切换「全部」可查看扩展实验。点击 **在线阅读** 进入 `rendered/*.html`，或直接下载 `.ipynb` 运行。

## 维护

```bash
pip install -r ../scripts/requirements-notebooks.txt
python ../scripts/generate_all_notebooks.py
python ../scripts/render_notebooks.py
```

内容定义：`scripts/notebook_content/` · 可视化：`labs/common/viz_anim.py`
