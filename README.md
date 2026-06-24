# 《AI思维》算法交互学习页

配套《AI思维》第二部分第 5–12 章的静态交互网页，无需安装，浏览器直接打开即可。

## 分享链接

- **站点首页（目录）**：https://zhesun-0209.github.io/ai-thinking-labs/
- 第 5 章搜索：https://zhesun-0209.github.io/ai-thinking-labs/ch5.html
- 第 6–12 章：`ch6.html` … `ch12.html`

Hub 目录页使用独立轻量 `hub.css`；章节页采用系统字体栈，无需加载 Google Fonts。

## Python 代码实验

- 各章正文顶部的 **Python 代码实验** 按钮会打开本章 Notebook 列表
- **Jupyter 预渲染**（真实执行 + Lab 模板，无需 Colab）：例如 [ch5 搜索](https://zhesun-0209.github.io/ai-thinking-labs/notebooks/rendered/ch05_campus_search.html)
- 第 5–12 章共 24 本 notebook 均可在线阅读；下载 `.ipynb` 后，首个单元会使用 notebook 内嵌源码和数据准备运行环境

维护者重新生成：

```bash
pip install -r scripts/requirements-notebooks.txt
python -m ipykernel install --user --name python3
python scripts/generate_all_notebooks.py
python scripts/render_notebooks.py
```

## 本地预览

```bash
python3 -m http.server 8766
# 打开 http://localhost:8766/hub.html
```
