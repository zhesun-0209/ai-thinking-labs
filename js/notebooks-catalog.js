/** Notebook catalog for 《AI思维》labs — used by notebooks/*.html */
"use strict";

const NOTEBOOKS_REPO = "zhesun-0209/ai-thinking-labs";
const NOTEBOOKS_BRANCH = "main";
const NOTEBOOKS_BASE = `https://github.com/${NOTEBOOKS_REPO}/blob/${NOTEBOOKS_BRANCH}/notebooks`;

const TIER_META = {
  A: {
    label: "纯 Python",
    summary: "先理解流程，不依赖机器学习库。",
    tone: "green",
  },
  B: {
    label: "numpy / sklearn",
    summary: "把算法拆成数组、矩阵和可视化。",
    tone: "blue",
  },
  C: {
    label: "本地 torch",
    summary: "适合已有 Python 环境后继续动手。",
    tone: "amber",
  },
  D: {
    label: "概念走读",
    summary: "用代码骨架理解系统流程。",
    tone: "violet",
  },
};

const SCOPE_META = {
  core: "核心实验",
  extension: "扩展参考",
};

const LEARNING_PATH = [
  { title: "打开", text: "进入预渲染页面，确认代码单元和输出。" },
  { title: "下载", text: "下载 .ipynb 后直接运行首个环境单元。" },
  { title: "改参数", text: "替换输入、调参数，观察输出变化。" },
  { title: "复现", text: "用同一代码复现章节网页中的关键结果。" },
];

/** @type {Record<number, { title: string; slug: string; web: string; question: string; items: Array<object> }>} */
const CHAPTER_NOTEBOOKS = {
  5: {
    title: "搜索智能",
    slug: "ch05",
    web: "../ch5.html",
    question: "同一张校园图里，为什么不同搜索策略会得到不同探索顺序和路径代价？",
    items: [
      {
        file: "ch05_campus_search.ipynb",
        title: "校园图五种搜索",
        blurb: "DFS / BFS / UCS / Greedy / A*，输出与 ch5 地图演示同路径。",
        outcomes: ["运行五种搜索函数", "比较路径和总代价"],
        result: "路径表、校园图、结果校验",
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
    question: "规则和图谱如何把已知事实一步步扩展成可解释的结论？",
    items: [
      {
        file: "ch06_forward_backward_chain.ipynb",
        title: "前向链与后向链",
        blurb: "小规则库逐步推导。",
        outcomes: ["运行规则表", "输出前向链和后向链结果"],
        result: "事实表、规则表、推理结果表",
        tier: "A",
        minutes: 12,
        ready: true,
      },
      {
        file: "ch06_graph_reasoning.ipynb",
        title: "图谱多跳与路径排序",
        blurb: "固定 JSON 三元组上的推理实验。",
        outcomes: ["加载三元组 JSON", "运行多跳查询和路径排序"],
        result: "三元组加载、多跳路径、排序解释",
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
    question: "模型如何从数据中形成边界、簇和误差下降的反馈？",
    items: [
      {
        file: "ch07_decision_tree_kmeans.ipynb",
        title: "决策树与 K-均值",
        blurb: "sklearn DecisionTreeClassifier + KMeans。",
        outcomes: ["调用 sklearn 决策树", "调用 sklearn KMeans"],
        result: "特征重要度、树文本、聚类中心图",
        tier: "B",
        minutes: 20,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch07_perceptron_gd.ipynb",
        title: "感知机与梯度下降",
        blurb: "loss 曲线与网页对齐。",
        outcomes: ["运行实验函数", "输出 loss 曲线和线性边界"],
        result: "决策边界、参数更新、误差曲线",
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
    question: "向量、神经元和注意力如何把离散对象连接成可计算关系？",
    items: [
      {
        file: "ch08_mlp_backprop.ipynb",
        title: "MLPClassifier",
        blurb: "sklearn Pipeline + MLPClassifier。",
        outcomes: ["调用 sklearn MLPClassifier", "输出预测概率"],
        result: "预测概率表、网络结构图",
        tier: "B",
        minutes: 25,
        ready: true,
      },
      {
        file: "ch08_transe_attention.ipynb",
        title: "TransE 与 Attention",
        blurb: "玩具三元组 + QKV softmax。",
        outcomes: ["把关系看成向量平移", "观察 query 如何分配注意力"],
        result: "关系向量、注意力权重、softmax 表",
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
    question: "文本如何从符号拆分、共现学习到上下文预测？",
    items: [
      {
        file: "ch09_bpe.ipynb",
        title: "BPE 字节对合并",
        blurb: "「日记→狂人→鲁迅」与 ch9 步进一致。",
        outcomes: ["手算高频 pair 合并", "理解子词词表的生成逻辑"],
        result: "合并轮次、词表变化、分词结果",
        tier: "A",
        minutes: 10,
        ready: true,
      },
      {
        file: "ch09_skipgram_toy.ipynb",
        title: "Skip-gram 玩具词表",
        blurb: "10 词 numpy 训练。",
        outcomes: ["把上下文窗口转成训练样本", "观察相近词向量如何靠近"],
        result: "共现样本、词向量、相似度表",
        tier: "B",
        minutes: 15,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch09_attention_lm.ipynb",
        title: "Self-Attention 与字符 LM",
        blurb: "注意力矩阵 + 下一字符预测。",
        outcomes: ["读懂 QK 打分和 V 聚合", "连接注意力和下一 token 预测"],
        result: "注意力矩阵、字符概率、预测示例",
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
    question: "图像如何被卷积、patch、掩码和跨模态对比转成可学习表示？",
    items: [
      {
        file: "ch10_conv2d_numpy.ipynb",
        title: "4×4 卷积与 MaxPool",
        blurb: "从一个小矩阵看局部连接、权值共享和池化压缩。",
        outcomes: ["手动滑动卷积核", "比较卷积输出和池化输出"],
        result: "卷积窗口、特征图、MaxPool 结果",
        tier: "B",
        minutes: 18,
        ready: true,
      },
      {
        file: "ch10_vit_patchify.ipynb",
        title: "ViT Patch 词元化",
        blurb: "把图像切成 patch，再组织成 Transformer token 序列。",
        outcomes: ["理解 patch 展平与线性映射", "看位置编码如何补回顺序"],
        result: "patch 网格、token 矩阵、位置向量",
        tier: "B",
        minutes: 15,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch10_mae_masking.ipynb",
        title: "MAE 掩码与 MSE",
        blurb: "用可见 patch 重建被遮挡区域，理解自监督信号。",
        outcomes: ["观察随机 mask 采样", "用重建误差解释训练目标"],
        result: "mask 图、重建向量、MSE 分解",
        tier: "B",
        minutes: 15,
        ready: true,
      },
      {
        file: "ch10_clip_infonce.ipynb",
        title: "CLIP InfoNCE",
        blurb: "用图文相似度矩阵理解跨模态对齐。",
        outcomes: ["读懂对角线正样本", "比较温度系数对概率的影响"],
        result: "相似度矩阵、softmax 概率、对比损失",
        tier: "C",
        minutes: 20,
        scope: "extension",
        ready: true,
      },
    ],
  },
  11: {
    title: "行动智能",
    slug: "ch11",
    web: "../ch11.html",
    question: "智能体如何用价值、探索和时序差分把行动变成策略？",
    items: [
      {
        file: "ch11_mdp_value_iteration.ipynb",
        title: "MDP 与价值迭代",
        blurb: "在小网格世界中迭代状态价值，观察策略逐步稳定。",
        outcomes: ["拆开 Bellman 更新", "比较折扣系数对长期回报的影响"],
        result: "价值表、策略箭头、迭代误差",
        tier: "A",
        minutes: 18,
        ready: true,
      },
      {
        file: "ch11_td_learning.ipynb",
        title: "TD(0) 学习",
        blurb: "用一步 bootstrap 更新价值估计。",
        outcomes: ["理解 TD target", "观察在线更新和完整回合的差异"],
        result: "采样轨迹、TD 误差、价值变化",
        tier: "A",
        minutes: 12,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch11_epsilon_greedy.ipynb",
        title: "epsilon-贪心多臂老虎机",
        blurb: "在探索和利用之间切换，比较不同 epsilon 的累计回报。",
        outcomes: ["区分随机探索和当前最优选择", "看 regret 如何随策略变化"],
        result: "动作计数、平均奖励、累计 regret",
        tier: "A",
        minutes: 10,
        ready: true,
      },
    ],
  },
  12: {
    title: "创造智能",
    slug: "ch12",
    web: "../ch12.html",
    question: "搜索、生成和结构预测如何把模型从识别推向创造？",
    items: [
      {
        file: "ch12_repr_search_annealing.ipynb",
        title: "表征搜索与模拟退火",
        blurb: "用温度控制探索强度，在候选表征里寻找更低 loss。",
        outcomes: ["理解接受差解的意义", "观察温度下降后的搜索收敛"],
        result: "候选轨迹、温度表、loss 曲线",
        tier: "A",
        minutes: 12,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch12_mcts.ipynb",
        title: "MCTS 与 UCT",
        blurb: "四步循环：选择、扩展、模拟、回传。",
        outcomes: ["读懂 UCT 平衡项", "追踪访问次数和价值回传"],
        result: "搜索树、访问计数、UCT 分数",
        tier: "A",
        minutes: 20,
        ready: true,
      },
      {
        file: "ch12_diffusion_1d.ipynb",
        title: "1D 玩具扩散（numpy）",
        blurb: "在一维信号上观察加噪和去噪的方向。",
        outcomes: ["理解前向扩散如何破坏结构", "把去噪看成逐步修复"],
        result: "噪声曲线、去噪步骤、误差对比",
        tier: "B",
        minutes: 15,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch12_diffusion_digits.ipynb",
        title: "小图像 Diffusion 经典缩影",
        blurb: "用 8×8 手写数字展示 DDPM 的前向加噪、反向去噪和采样轨迹。",
        outcomes: ["观察清晰数字如何逐步变噪", "理解去噪模型学的是小步修复方向"],
        result: "digits 图像序列、噪声调度表、反向去噪轨迹",
        tier: "B",
        minutes: 24,
        ready: true,
      },
      {
        file: "ch12_gan_toy.ipynb",
        title: "2D GAN 玩具",
        blurb: "用二维点分布理解生成器和判别器的博弈。",
        outcomes: ["观察判别边界变化", "理解生成分布靠近真实分布"],
        result: "点云图、判别分数、训练轨迹",
        tier: "C",
        minutes: 25,
        ready: true,
      },
      {
        file: "ch12_diffusion_toy.ipynb",
        title: "扩散去噪概念（1D 扩展）",
        blurb: "用一维轨迹补充理解反向过程。",
        outcomes: ["连接前向噪声和反向去噪", "把图像案例抽象回公式"],
        result: "前向/反向概念线",
        tier: "C",
        minutes: 12,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch12_alphafold_concepts.ipynb",
        title: "AlphaFold 流程（概念）",
        blurb: "用流程化代码骨架理解从序列到结构的关键模块。",
        outcomes: ["区分 MSA、pair 表征和结构模块", "理解端到端预测链路"],
        result: "模块流程、张量形状、概念检查",
        tier: "D",
        minutes: 10,
        scope: "extension",
        ready: true,
      },
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

function chapterEntries() {
  return Object.keys(CHAPTER_NOTEBOOKS)
    .sort((a, b) => Number(a) - Number(b))
    .map((n) => [Number(n), CHAPTER_NOTEBOOKS[n]]);
}

function notebookEntries(chapterFilter = null) {
  return chapterEntries()
    .filter(([chNum]) => chapterFilter === null || chNum === chapterFilter)
    .flatMap(([chNum, ch]) => ch.items.map((item) => ({ ...item, chNum, chapterTitle: ch.title, chapterQuestion: ch.question })));
}

function minutesLabel(minutes) {
  if (minutes <= 12) return "短练习";
  if (minutes <= 20) return "标准练习";
  return "进阶练习";
}

function itemScope(item) {
  return item.scope || "core";
}

function renderPills(item) {
  const tier = TIER_META[item.tier] || { label: item.tier, tone: "green" };
  const scope = itemScope(item);
  return `<div class="nb-pills" aria-label="学习属性">
    <span class="nb-pill nb-pill--chapter">第 ${item.chNum} 章</span>
    <span class="nb-pill ${scope === "core" ? "nb-pill--core" : "nb-pill--extension"}">${SCOPE_META[scope]}</span>
    <span class="nb-pill nb-pill--${tier.tone}">${item.tier} 层 · ${tier.label}</span>
    <span class="nb-pill">${minutesLabel(item.minutes)} · ${item.minutes} 分钟</span>
  </div>`;
}

function renderNotebookCard(item) {
  const tier = TIER_META[item.tier] || { label: item.tier, summary: "", tone: "green" };
  const outcomes = (item.outcomes || []).map((text) => `<li>${text}</li>`).join("");
  if (!item.ready) {
    return `<article class="nb-card nb-card--soon" data-tier="${item.tier}" data-scope="${itemScope(item)}" data-chapter="${item.chNum}" data-minutes="${item.minutes}">
      ${renderPills(item)}
      <h3>${item.title}</h3>
      ${item.blurb ? `<p class="nb-card-blurb">${item.blurb}</p>` : ""}
      <p class="nb-soon">即将推出</p>
    </article>`;
  }
  return `<article class="nb-card" data-tier="${item.tier}" data-scope="${itemScope(item)}" data-chapter="${item.chNum}" data-minutes="${item.minutes}" data-search="${[
    item.file,
    item.id,
    item.title,
    item.blurb,
    item.result,
    item.chapterTitle,
    item.chapterQuestion,
    ...(item.outcomes || []),
    tier.label,
    SCOPE_META[itemScope(item)],
  ]
    .join(" ")
    .toLowerCase()}">
    ${renderPills(item)}
    <h3>${item.title}</h3>
    ${item.blurb ? `<p class="nb-card-blurb">${item.blurb}</p>` : ""}
    <div class="nb-card-detail">
      <div>
        <strong>观察重点</strong>
        <ul>${outcomes}</ul>
      </div>
      <div>
        <strong>代码产出</strong>
        <p>${item.result}</p>
      </div>
    </div>
    <div class="nb-actions">
      <a class="nb-btn nb-btn--primary" href="${readerUrl(item.file)}">在线阅读</a>
      <a class="nb-btn" href="${item.file}" download>下载 .ipynb</a>
      <a class="nb-btn" href="${githubUrl(item.file)}" target="_blank" rel="noopener noreferrer">GitHub 源码 ↗</a>
    </div>
  </article>`;
}

function catalogStats(entries = notebookEntries()) {
  const ready = entries.filter((item) => item.ready);
  const core = ready.filter((item) => itemScope(item) === "core");
  return {
    total: ready.length,
    core: core.length,
    minutes: core.reduce((sum, item) => sum + item.minutes, 0),
    chapters: new Set(core.map((item) => item.chNum)).size,
  };
}

function renderOverview(chapterFilter = null) {
  const entries = notebookEntries(chapterFilter);
  const stats = catalogStats(entries);
  return `<section class="nb-overview" aria-labelledby="nbOverviewTitle">
    <div>
      <p class="nb-kicker">代码实验台</p>
      <h2 id="nbOverviewTitle">${chapterFilter ? `第 ${chapterFilter} 章学习包` : "从交互理解到可复现实验"}</h2>
      <p>${chapterFilter ? CHAPTER_NOTEBOOKS[chapterFilter].question : "每个 Notebook 都是可下载运行的代码实验：首个单元准备依赖和数据，后续单元调用主流库或轻量 numpy 示例复现关键结果。"}</p>
    </div>
    <dl class="nb-stats">
      <div><dt>${stats.core}</dt><dd>核心实验</dd></div>
      <div><dt>${stats.total}</dt><dd>可读总数</dd></div>
      <div><dt>${stats.chapters}</dt><dd>覆盖章节</dd></div>
    </dl>
  </section>`;
}

function renderLearningPath() {
  return `<section class="nb-path" aria-label="学习路线">
    ${LEARNING_PATH.map(
      (step, index) => `<article>
        <span>${index + 1}</span>
        <strong>${step.title}</strong>
        <p>${step.text}</p>
      </article>`,
    ).join("")}
  </section>`;
}

function renderControls(chapterFilter = null) {
  const entries = notebookEntries(chapterFilter);
  const tiers = [...new Set(entries.map((item) => item.tier))];
  const coreCount = entries.filter((item) => itemScope(item) === "core").length;
  return `<section class="nb-controls" aria-label="Notebook 筛选">
    <label class="nb-search">
      <span>查找 Notebook</span>
      <input id="nbSearch" type="search" placeholder="搜索算法、章节、产出..." autocomplete="off" />
    </label>
    <div class="nb-segmented nb-scope-filter" role="group" aria-label="展示范围">
      <button class="is-active" type="button" data-scope="core" aria-pressed="true">核心</button>
      <button type="button" data-scope="all" aria-pressed="false">全部</button>
    </div>
    <div class="nb-segmented nb-tier-filter" role="group" aria-label="难度层级">
      <button class="is-active" type="button" data-tier="all" aria-pressed="true">全部</button>
      ${tiers.map((tier) => `<button type="button" data-tier="${tier}" aria-pressed="false">${tier} 层</button>`).join("")}
    </div>
    <p class="nb-count" id="nbCount" aria-live="polite">${coreCount} 个核心实验</p>
  </section>`;
}

function renderChapterSection(chNum, opts = {}) {
  const ch = CHAPTER_NOTEBOOKS[chNum];
  if (!ch) return "";
  const heading =
    opts.heading !== false
      ? `<div class="nb-chapter-head">
        <span class="nb-chapter-num">${chNum}</span>
        <div>
          <p class="nb-chapter-question">${ch.question}</p>
          <h2>${ch.title}</h2>
          <a class="nb-back-ch" href="${ch.web}">返回第 ${chNum} 章网页</a>
        </div>
      </div>`
      : "";
  const cards = ch.items.map((item) => renderNotebookCard({ ...item, chNum, chapterTitle: ch.title, chapterQuestion: ch.question })).join("");
  return `<section class="nb-chapter" id="ch${chNum}">${heading}<div class="nb-grid">${cards}</div></section>`;
}

function filterCards() {
  const searchEl = document.getElementById("nbSearch");
  const countEl = document.getElementById("nbCount");
  const query = (searchEl?.value || "").trim().toLowerCase();
  const activeTier = document.querySelector(".nb-tier-filter button.is-active")?.dataset.tier || "all";
  const activeScope = document.querySelector(".nb-scope-filter button.is-active")?.dataset.scope || "core";
  const cards = [...document.querySelectorAll(".nb-card")];
  const isFiltered = Boolean(query) || activeTier !== "all" || activeScope !== "core";
  let shown = 0;
  cards.forEach((card) => {
    const matchesTier = activeTier === "all" || card.dataset.tier === activeTier;
    const matchesScope = activeScope === "all" || card.dataset.scope === "core";
    const matchesQuery = !query || (card.dataset.search || card.textContent.toLowerCase()).includes(query);
    const visible = matchesTier && matchesScope && matchesQuery;
    card.hidden = !visible;
    if (visible) shown += 1;
  });

  document.querySelectorAll(".nb-chapter").forEach((section) => {
    const visibleCards = section.querySelectorAll(".nb-card:not([hidden])").length;
    section.hidden = visibleCards === 0;
  });

  const emptyEl = document.querySelector(".nb-empty");
  if (emptyEl) emptyEl.hidden = shown !== 0;
  document.querySelectorAll(".nb-toc").forEach((toc) => {
    toc.hidden = isFiltered;
  });
  if (countEl) countEl.textContent = `${shown} 个${activeScope === "core" ? "核心" : ""}实验`;
}

function setupControls() {
  const searchEl = document.getElementById("nbSearch");
  searchEl?.addEventListener("input", filterCards);
  document.querySelectorAll(".nb-segmented button").forEach((button) => {
    button.addEventListener("click", () => {
      button.closest(".nb-segmented")?.querySelectorAll("button").forEach((item) => {
        item.classList.remove("is-active");
        item.setAttribute("aria-pressed", "false");
      });
      button.classList.add("is-active");
      button.setAttribute("aria-pressed", "true");
      filterCards();
    });
  });
  filterCards();
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
    mainEl.innerHTML = `
      ${renderOverview(chNum)}
      ${renderControls(chNum)}
      ${renderChapterSection(chNum)}
      <p class="nb-empty" hidden>没有匹配的 Notebook。</p>
      <p class="nb-foot"><a href="index.html">全部 Notebook 索引</a> · <a href="../labs/README.md">labs/ 脚本说明 ↗</a></p>`;
    setupControls();
  }
}

function renderIndexPage() {
  const mainEl = document.getElementById("nbMain");
  if (!mainEl) return;
  const sections = chapterEntries().map(([n]) => renderChapterSection(n)).join("");
  mainEl.innerHTML = `
    ${renderOverview()}
    ${renderLearningPath()}
    ${renderControls()}
    <nav class="nb-toc" aria-label="章节 Notebook 索引">
      ${chapterEntries()
        .map(([n, ch]) => {
          const ready = ch.items.filter((item) => item.ready).length;
          const core = ch.items.filter((item) => item.ready && itemScope(item) === "core").length;
          return `<a href="chapter.html?ch=${n}"><span>第 ${n} 章</span><strong>${ch.title}</strong><em>${core} 核心 · ${ready} 可读</em></a>`;
        })
        .join("")}
    </nav>
    ${sections}
    <p class="nb-empty" hidden>没有匹配的 Notebook。</p>`;
  setupControls();
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
