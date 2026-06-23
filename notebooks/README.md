# Jupyter Notebook 索引

配套网页的 Python 实验，**预渲染为静态 HTML**，国内用户无需 Colab 即可阅读完整过程与输出。

## 阅读方式（推荐）

1. **在线阅读** — 索引页点「在线阅读 ↗」，打开 `rendered/*.html` 教程页  
   - 左侧目录、Markdown 讲解、代码单元与运行结果  
   - 顶栏「隐藏代码 / 显示代码」切换（类似 many 中文 ML 教程）

2. **下载 .ipynb** — 本地 Jupyter / VS Code 可修改重跑

3. **直接跑脚本** — [../labs/README.md](../labs/README.md)

## 当前可阅读

| 预渲染页 | 章节 |
|----------|------|
| [rendered/ch05_campus_search.html](./rendered/ch05_campus_search.html) | 第 5 章 搜索 |
| [rendered/ch09_bpe.html](./rendered/ch09_bpe.html) | 第 9 章 BPE |

## 维护者：重新生成 HTML

```bash
pip install -r ../scripts/requirements-render.txt
python ../scripts/render_notebooks.py
```

GitHub Actions 在每次 push 到 `main` 时会自动执行上述命令后再部署 Pages。

## 设计说明

- 参考常见教程站（D2L / 课程 lab）：叙事 Markdown + 可折叠代码 + 执行输出  
- 不使用 nbviewer / Colab，避免国内访问问题  
- 单页约 5–8 KB（不含外链），适合 GitHub Pages
