# 《AI思维》算法交互学习页

配套《AI思维》第二部分第 5–12 章的静态交互网页，无需安装，浏览器直接打开即可。

## 分享链接

- **站点首页（目录）**：https://zhesun-0209.github.io/ai-thinking-labs/
- 第 5 章搜索：https://zhesun-0209.github.io/ai-thinking-labs/ch5.html
- 第 6–12 章：`ch6.html` … `ch12.html`

Hub 目录页使用独立轻量 `hub.css`；章节页采用系统字体栈，无需加载 Google Fonts。

## Python 代码实验

- **Notebook 索引（新标签页打开）**：https://zhesun-0209.github.io/ai-thinking-labs/notebooks/index.html
- 第 5 章搜索、第 9 章 BPE 已提供可运行 Notebook 与 `labs/` 脚本；其余章节见索引中的「即将推出」条目。

本地跑脚本：

```bash
cd labs
python3 ch05/search_algorithms.py
python3 ch09/bpe.py
```

## 本地预览

```bash
python3 -m http.server 8766
# 打开 http://localhost:8766/hub.html
```
