# Jupyter Notebook 索引

配套网页的可执行 Python 实验。**在章节页点击「Python 代码实验 ↗」会在新标签页打开**，不拉长章节正文。

## 当前可用（P0）

| Notebook | 章节 | 说明 |
|----------|------|------|
| [ch05_campus_search.ipynb](./ch05_campus_search.ipynb) | 第 5 章 | 校园图六种搜索，输出与网页一致 |
| [ch09_bpe.ipynb](./ch09_bpe.ipynb) | 第 9 章 | BPE 合并步骤与 ch9 演示对齐 |

## 打开方式

1. **下载 .ipynb** — 本地 Jupyter / VS Code
2. **在 Colab 打开** — Notebook 索引页上的按钮（需 Google 账号）
3. **直接跑脚本** — 见 [../labs/README.md](../labs/README.md)

## 依赖

- P0：Python 3.10+，仅标准库
- 后续 B 层：`pip install -r ../labs/requirements-min.txt`
- C 层（Colab）：notebook 内 `%pip install torch` 等

## 模板结构

每个 notebook 包含：与网页对照表 → 加载 `labs/common` 数据 → 分步代码 → 结果汇总 → 练习。
