# Jupyter Notebook 索引

配套《AI思维》第 5–12 章：**逐步演示**各章算法（分步输出、队列/栈 GIF、图表），真实执行后导出为静态 HTML。

## 阅读

[index.html](./index.html) → **在线阅读** → `rendered/*.html`

## 维护

```bash
pip install -r ../scripts/requirements-notebooks.txt
python ../scripts/generate_all_notebooks.py
python ../scripts/render_notebooks.py
```

内容定义：`scripts/notebook_content/` · 可视化：`labs/common/viz_anim.py`
