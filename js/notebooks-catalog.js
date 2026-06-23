/** Notebook catalog for 《AI思维》labs — used by notebooks/*.html */
"use strict";

const NOTEBOOKS_REPO = "zhesun-0209/ai-thinking-labs";
const NOTEBOOKS_BRANCH = "main";
const NOTEBOOKS_BASE = `https://github.com/${NOTEBOOKS_REPO}/blob/${NOTEBOOKS_BRANCH}/notebooks`;

const TIER_LABELS = {
  A: "纯 Python · 已预渲染",
  B: "numpy / sklearn · 已预渲染",
  C: "本地 torch · 发布后预渲染",
  D: "概念 · 只读",
};

/** @type {Record<number, { title: string; slug: string; web: string; items: Array<object> }>} */
const CHAPTER_NOTEBOOKS = {
  5: {
    title: "搜索智能",
    slug: "ch05",
    web: "../ch5.html",
    items: [
      {
        file: "ch05_campus_search.ipynb",
        title: "校园图六种搜索",
        blurb: "DFS / BFS / UCS / Greedy / A*，输出与 ch5 地图演示同路径。",
        tier: "A",
        minutes: 15,
        ready: true,
      },
    ],
  },
  6: {
    title: "推理智能",
    slug: "ch06",
    web: "../ch6.html",
    items: [
      {
        file: "ch06_forward_backward_chain.ipynb",
        title: "前向链与后向链",
        blurb: "小规则库逐步推导。",
        tier: "A",
        minutes: 12,
        ready: true,
      },
      {
        file: "ch06_graph_reasoning.ipynb",
        title: "图谱多跳与路径排序",
        blurb: "固定 JSON 三元组上的推理实验。",
        tier: "A",
        minutes: 15,
        ready: true,
      },
    ],
  },
  7: {
    title: "学习智能",
    slug: "ch07",
    web: "../ch7.html",
    items: [
      {
        file: "ch07_decision_tree_kmeans.ipynb",
        title: "决策树与 K-均值",
        blurb: "错题诊断案例。",
        tier: "B",
        minutes: 20,
        ready: true,
      },
      {
        file: "ch07_perceptron_gd.ipynb",
        title: "感知机与梯度下降",
        blurb: "loss 曲线与网页对齐。",
        tier: "B",
        minutes: 18,
        ready: true,
      },
    ],
  },
  8: {
    title: "连接智能",
    slug: "ch08",
    web: "../ch8.html",
    items: [
      {
        file: "ch08_mlp_backprop.ipynb",
        title: "小 MLP 前向与反向传播",
        blurb: "numpy 复现网页同一组数。",
        tier: "B",
        minutes: 25,
        ready: true,
      },
      {
        file: "ch08_transe_attention.ipynb",
        title: "TransE 与 Attention",
        blurb: "玩具三元组 + QKV softmax。",
        tier: "B",
        minutes: 22,
        ready: true,
      },
    ],
  },
  9: {
    title: "语言智能",
    slug: "ch09",
    web: "../ch9.html",
    items: [
      {
        file: "ch09_bpe.ipynb",
        title: "BPE 字节对合并",
        blurb: "「日记→狂人→鲁迅」与 ch9 步进一致。",
        tier: "A",
        minutes: 10,
        ready: true,
      },
      {
        file: "ch09_skipgram_toy.ipynb",
        title: "Skip-gram 玩具词表",
        blurb: "10 词 numpy 训练。",
        tier: "B",
        minutes: 15,
        ready: true,
      },
      {
        file: "ch09_attention_lm.ipynb",
        title: "Self-Attention 与字符 LM",
        blurb: "注意力矩阵 + 下一字符预测。",
        tier: "B",
        minutes: 20,
        ready: true,
      },
    ],
  },
  10: {
    title: "感知智能",
    slug: "ch10",
    web: "../ch10.html",
    items: [
      { file: "ch10_conv2d_numpy.ipynb", title: "4×4 卷积与 MaxPool", tier: "B", minutes: 18, ready: false },
      { file: "ch10_vit_patchify.ipynb", title: "ViT Patch 词元化", tier: "B", minutes: 15, ready: false },
      { file: "ch10_mae_masking.ipynb", title: "MAE 掩码与 MSE", tier: "B", minutes: 15, ready: false },
      { file: "ch10_clip_infonce.ipynb", title: "CLIP InfoNCE", tier: "C", minutes: 20, ready: false },
    ],
  },
  11: {
    title: "行动智能",
    slug: "ch11",
    web: "../ch11.html",
    items: [
      { file: "ch11_mdp_value_iteration.ipynb", title: "MDP 与价值迭代", tier: "A", minutes: 18, ready: false },
      { file: "ch11_td_learning.ipynb", title: "TD(0) 学习", tier: "A", minutes: 12, ready: false },
      { file: "ch11_epsilon_greedy.ipynb", title: "ε-贪心多臂老虎机", tier: "A", minutes: 10, ready: false },
    ],
  },
  12: {
    title: "创造智能",
    slug: "ch12",
    web: "../ch12.html",
    items: [
      { file: "ch12_repr_search_annealing.ipynb", title: "表征搜索与模拟退火", tier: "A", minutes: 12, ready: false },
      { file: "ch12_mcts.ipynb", title: "MCTS 与 UCT", tier: "A", minutes: 20, ready: false },
      { file: "ch12_diffusion_1d.ipynb", title: "1D 玩具扩散（numpy）", tier: "B", minutes: 15, ready: false },
      { file: "ch12_gan_toy.ipynb", title: "2D GAN 玩具", tier: "C", minutes: 25, ready: false },
      { file: "ch12_diffusion_toy.ipynb", title: "小图扩散（本地）", tier: "C", minutes: 30, ready: false },
      { file: "ch12_alphafold_concepts.ipynb", title: "AlphaFold 流程（概念）", tier: "D", minutes: 10, ready: false },
    ],
  },
};

function stem(filename) {
  return filename.replace(/\.ipynb$/i, "");
}

function readerUrl(filename) {
  return `rendered/${stem(filename)}.html`;
}

function githubUrl(filename) {
  return `${NOTEBOOKS_BASE}/${filename}`;
}

function renderNotebookCard(item) {
  const tier = TIER_LABELS[item.tier] || item.tier;
  const meta = [`${item.tier} 层`, `约 ${item.minutes} 分钟`, tier].join(" · ");
  if (!item.ready) {
    return `<article class="nb-card nb-card--soon">
      <h3>${item.title}</h3>
      ${item.blurb ? `<p>${item.blurb}</p>` : ""}
      <p class="nb-meta">${meta}</p>
      <p class="nb-soon">即将推出（发布后提供预渲染 HTML）</p>
    </article>`;
  }
  return `<article class="nb-card">
    <h3>${item.title}</h3>
    ${item.blurb ? `<p>${item.blurb}</p>` : ""}
    <p class="nb-meta">${meta}</p>
    <div class="nb-actions">
      <a class="nb-btn nb-btn--primary" href="${readerUrl(item.file)}" target="_blank" rel="noopener noreferrer">在线阅读 ↗</a>
      <a class="nb-btn" href="${item.file}" download>下载 .ipynb</a>
      <a class="nb-btn" href="${githubUrl(item.file)}" target="_blank" rel="noopener noreferrer">GitHub 源码 ↗</a>
    </div>
  </article>`;
}

function renderChapterSection(chNum, opts = {}) {
  const ch = CHAPTER_NOTEBOOKS[chNum];
  if (!ch) return "";
  const heading =
    opts.heading !== false
      ? `<div class="nb-chapter-head">
        <span class="nb-chapter-num">${chNum}</span>
        <div>
          <h2>${ch.title}</h2>
          <a class="nb-back-ch" href="${ch.web}">返回第 ${chNum} 章网页 ↗</a>
        </div>
      </div>`
      : "";
  const cards = ch.items.map(renderNotebookCard).join("");
  return `<section class="nb-chapter" id="ch${chNum}">${heading}<div class="nb-grid">${cards}</div></section>`;
}

function renderChapterPage(chNum) {
  const ch = CHAPTER_NOTEBOOKS[chNum];
  if (!ch) {
    document.body.innerHTML = "<main class='nb-main'><p>未找到该章节。</p></main>";
    return;
  }
  const titleEl = document.getElementById("nbPageTitle");
  const mainEl = document.getElementById("nbMain");
  if (titleEl) titleEl.textContent = `第 ${chNum} 章 · ${ch.title} · Python 实验`;
  if (mainEl) {
    const cards = ch.items.map(renderNotebookCard).join("");
    mainEl.innerHTML = `
      <p class="nb-lead">Notebook 由 Jupyter 真实执行后导出。含<strong>学习目标、分步讲解、图表与自测</strong>，与章节网页互补；国内可直接阅读。</p>
      <div class="nb-chapter-head">
        <span class="nb-chapter-num">${chNum}</span>
        <div>
          <h2>${ch.title}</h2>
          <a class="nb-back-ch" href="${ch.web}">返回第 ${chNum} 章网页 ↗</a>
        </div>
      </div>
      <div class="nb-grid">${cards}</div>
      <p class="nb-foot"><a href="index.html">← 全部 Notebook 索引</a> · <a href="../labs/README.md">labs/ 脚本说明 ↗</a></p>`;
  }
}

function renderIndexPage() {
  const mainEl = document.getElementById("nbMain");
  if (!mainEl) return;
  const sections = Object.keys(CHAPTER_NOTEBOOKS)
    .sort((a, b) => Number(a) - Number(b))
    .map((n) => renderChapterSection(Number(n)))
    .join("");
  mainEl.innerHTML = `
    <p class="nb-lead">配套《AI思维》第 5–12 章。点击<strong>在线阅读</strong>打开 Jupyter Lab 预渲染页（真实执行输出），不依赖 Google Colab。</p>
    <ul class="nb-toc">
      ${Object.keys(CHAPTER_NOTEBOOKS)
        .sort((a, b) => Number(a) - Number(b))
        .map(
          (n) =>
            `<li><a href="chapter.html?ch=${n}">第 ${n} 章 ${CHAPTER_NOTEBOOKS[n].title}</a> · ${CHAPTER_NOTEBOOKS[n].items.filter((i) => i.ready).length}/${CHAPTER_NOTEBOOKS[n].items.length} 可阅读</li>`,
        )
        .join("")}
    </ul>
    ${sections}`;
}

if (typeof window !== "undefined") {
  window.NOTEBOOKS_CATALOG = {
    CHAPTER_NOTEBOOKS,
    readerUrl,
    githubUrl,
    renderChapterPage,
    renderIndexPage,
  };
}
