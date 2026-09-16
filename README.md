# 《AI思维》算法交互学习页

配套《AI思维》第二部分第 5–12 章的静态交互网页，无需安装，浏览器直接打开即可。

## 分享链接

- **站点首页（目录）**：https://zhesun-0209.github.io/ai-thinking-labs/
- 第 5 章搜索：https://zhesun-0209.github.io/ai-thinking-labs/ch5.html
- 第 6–12 章：`ch6.html` … `ch12.html`

Hub 目录页使用独立轻量 `hub.css`；章节页采用系统字体栈，无需加载 Google Fonts。

## Python 代码实验

- 各章正文顶部的 **Python 代码实验** 按钮会打开本章 Notebook 列表
- **在线阅读**保留 Markdown、代码和已保存的运行结果，例如 [第 5 章搜索](https://zhesun-0209.github.io/ai-thinking-labs/notebooks/rendered/ch05_campus_search.html)。网页本身不执行 Python。
- 第 5–12 章共 24 本 notebook，可单独下载。依赖安装与初始化保留在下载版中；部分实验需要联网获取公开数据或模型权重，并非全部离线运行。
- 课程正文与 Notebook 可以采用不同案例，不要求例子一一对应。

维护者仅更新阅读页外观或导出已有结果：

```bash
pip install -r scripts/requirements-notebooks.txt
python scripts/render_notebooks.py --export-only
```

更改实验代码时，按 [Notebook 维护流程](docs/notebook-development-sop.md) 仅生成目标文件，再显式执行。生成器会覆盖源 Notebook，不能在只改外观时全量运行：

```bash
python -m ipykernel install --user --name python3
python scripts/render_notebooks.py ch05_campus_search.ipynb --execute
```

`render_notebooks.py` 默认只导出；`--execute` 才会启动内核并写回运行结果。GitHub Pages 发布只打包已审阅的静态文件，不在 CI 下载或运行模型。

## 本地预览

```bash
python3 -m http.server 8766
# 打开 http://localhost:8766/hub.html
```

## 发布与迁移

GitHub Pages 工作流使用 `scripts/build_site.py` 的文件白名单，发布产物不包含开发脚本、实验源目录、审计文档或版本控制文件。

```bash
# 输出目录必须位于仓库外，且尚不存在。
python3 scripts/build_site.py --site-url https://shapeofai.cn --output /tmp/shapeofai-release
```

- [审计汇总](docs/audit-2026-09-overview.md)
- [腾讯云境外服务器选型](docs/tencent-server-options.md)
- [部署、域名切换与回滚](docs/migration-tencent.md)

`shapeofai.cn` 是迁移目标，并不表示已经上线；购买服务器及 DNS 切换需另行完成。
