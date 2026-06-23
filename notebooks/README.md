# Jupyter Notebook 索引

配套《AI思维》第 5–12 章的 Python 实验。**由 Jupyter 真实执行后**，用 `nbconvert --template lab` 导出为静态 HTML，国内可直接阅读，无需 Colab。

## 阅读方式

1. **在线阅读** — [index.html](./index.html) 点「在线阅读 ↗」，打开 `rendered/*.html`（官方 Jupyter Lab 样式，含代码与执行输出）
2. **下载 .ipynb** — 本地 Jupyter / VS Code 修改重跑
3. **直接跑脚本** — [../labs/README.md](../labs/README.md)

## 维护者：重新生成

```bash
pip install -r ../scripts/requirements-notebooks.txt
python -m ipykernel install --user --name python3
python ../scripts/generate_all_notebooks.py   # 可选：从 manifest 重建 .ipynb
python ../scripts/render_notebooks.py         # 执行 + 导出 HTML
```

GitHub Actions 在 push 到 `main` 时自动执行后部署 Pages。

## 技术说明

- 执行：`jupyter nbconvert --execute --inplace`
- 导出：`jupyter nbconvert --to html --template lab --embed-images`
- 顶栏导航由 `scripts/render_notebooks.py` 注入，链回索引与章节目录
