# 《AI思维》算法交互学习页

配套《AI思维》第二部分第 5–12 章的静态交互网页，无需安装，浏览器直接打开即可。

## 分享链接

- **站点首页（目录）**：https://zhesun-0209.github.io/ai-thinking-labs/
- 第 5 章搜索：https://zhesun-0209.github.io/ai-thinking-labs/ch5.html
- 第 6–12 章：`ch6.html` … `ch12.html`

Hub 目录页使用独立轻量 `hub.css`；章节页采用系统字体栈，无需加载 Google Fonts。

## Python 代码实验

- **Notebook 索引**：https://zhesun-0209.github.io/ai-thinking-labs/notebooks/index.html  
- **预渲染阅读**（无需 Colab）：例如 [ch5 搜索实验](https://zhesun-0209.github.io/ai-thinking-labs/notebooks/rendered/ch05_campus_search.html)  
- 第 5 章搜索、第 9 章 BPE 已可在线阅读；其余章节见索引「即将推出」

维护者重新生成 HTML：

```bash
pip install -r scripts/requirements-render.txt
python scripts/render_notebooks.py
```

## 本地预览

```bash
python3 -m http.server 8766
# 打开 http://localhost:8766/hub.html
```
