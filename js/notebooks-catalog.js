/** Notebook catalog for 《AI思维》labs — used by notebooks/*.html */
"use strict";

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
        title: "Wine 决策树与 Iris KMeans",
        blurb: "Wine 分类、Iris 聚类，展示特征重要性和不同 k 的效果。",
        outcomes: ["训练 Wine 决策树", "比较 Iris 聚类 k 值"],
        result: "树结构、特征重要性、混淆矩阵、肘部曲线",
        tier: "B",
        minutes: 20,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch07_perceptron_gd.ipynb",
        title: "Diabetes SGD 与 Iris Perceptron",
        blurb: "Diabetes 回归看梯度下降，Iris 二分类看线性边界。",
        outcomes: ["运行 SGDRegressor", "训练 Perceptron"],
        result: "MSE 曲线、回归直线、感知机边界、阈值表",
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
        title: "Digits MLPClassifier",
        blurb: "用 sklearn MLPClassifier 训练 8×8 手写数字分类器。",
        outcomes: ["训练 Digits MLP", "查看测试集预测"],
        result: "loss 曲线、准确率、样本预测、混淆矩阵",
        tier: "B",
        minutes: 25,
        ready: true,
      },
      {
        file: "ch08_transe_attention.ipynb",
        title: "国家-首都 TransE 与 Attention",
        blurb: "France→Paris 的向量平移，加上句子 attention 权重热力图。",
        outcomes: ["计算 TransE 距离", "观察 query 如何分配注意力"],
        result: "距离表、几何图、attention 权重、最高关注标注",
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
        title: "BPE 经典词表合并",
        blurb: "用 low / lower / newest / widest / newer 的词频语料观察高频 pair 如何形成子词。",
        outcomes: ["统计高频 pair", "理解子词词表的生成逻辑"],
        result: "初始词表、合并轮次、pair 频次图、token 数变化",
        tier: "A",
        minutes: 10,
        ready: true,
      },
      {
        file: "ch09_skipgram_toy.ipynb",
        title: "Word2Vec 类比向量",
        blurb: "用 king - man + woman ≈ queen 观察词向量的线性关系。",
        outcomes: ["计算最近邻", "观察类比向量"],
        result: "词向量表、最近邻、类比相似度、二维图",
        tier: "B",
        minutes: 15,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch09_attention_lm.ipynb",
        title: "Causal Attention 与词 Bigram LM",
        blurb: "用 to be or not to be 展示因果注意力和下一词分布。",
        outcomes: ["读懂 causal mask", "连接注意力和下一词预测"],
        result: "注意力矩阵、bigram 概率、预测表",
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
        title: "Digits Sobel 卷积与 MaxPool",
        blurb: "用手写数字图像展示边缘卷积和池化压缩。",
        outcomes: ["滑动 Sobel 卷积核", "比较卷积输出和池化输出"],
        result: "输入图像、卷积窗口、特征图、MaxPool 结果",
        tier: "B",
        minutes: 18,
        ready: true,
      },
      {
        file: "ch10_vit_patchify.ipynb",
        title: "Digits ViT Patchify",
        blurb: "把 8×8 手写数字切成 patch token，观察 Transformer 的图像输入。",
        outcomes: ["理解 patch 展平", "查看 token 表"],
        result: "原图、patch 网格、token 矩阵",
        tier: "B",
        minutes: 15,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch10_mae_masking.ipynb",
        title: "Digits MAE 掩码重建",
        blurb: "遮住部分手写数字 patch，用可见 patch 均值做重建对照。",
        outcomes: ["观察随机 mask", "理解重建目标"],
        result: "原图、可见 patch、均值重建图",
        tier: "B",
        minutes: 15,
        ready: true,
      },
      {
        file: "ch10_clip_infonce.ipynb",
        title: "Digits CLIP InfoNCE",
        blurb: "匹配 digit 图像原型和文本标签，观察对角线正样本。",
        outcomes: ["读懂图文相似度矩阵", "计算 InfoNCE loss"],
        result: "图文相似度矩阵、softmax 概率、对比损失",
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
        blurb: "在经典 4×4 Gridworld 中迭代状态价值，观察策略逐步稳定。",
        outcomes: ["拆开 Bellman 更新", "比较折扣系数对长期回报的影响"],
        result: "价值表、策略箭头、迭代误差",
        tier: "A",
        minutes: 18,
        ready: true,
      },
      {
        file: "ch11_td_learning.ipynb",
        title: "TD(0) 学习",
        blurb: "用 Sutton random walk 展示一步 bootstrap 的在线价值更新。",
        outcomes: ["理解 TD target", "观察 random walk 更新"],
        result: "采样轨迹、TD 误差、价值变化",
        tier: "A",
        minutes: 12,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch11_epsilon_greedy.ipynb",
        title: "10-armed Bandit ε-greedy",
        blurb: "在经典 10 臂老虎机中比较不同 epsilon 的平均奖励。",
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
        title: "TSP 模拟退火",
        blurb: "用旅行商问题观察温度、差解接受和路线长度下降。",
        outcomes: ["理解接受差解的意义", "观察路线搜索收敛"],
        result: "城市坐标、温度表、最佳路线、距离曲线",
        tier: "A",
        minutes: 12,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch12_mcts.ipynb",
        title: "Tic-tac-toe MCTS 与 UCT",
        blurb: "用井字棋候选落子展示平均价值和探索项如何合成 UCT。",
        outcomes: ["读懂 UCT 平衡项", "比较候选落子"],
        result: "棋盘、访问计数、平均价值、UCT 分数",
        tier: "A",
        minutes: 20,
        ready: true,
      },
      {
        file: "ch12_diffusion_1d.ipynb",
        title: "双峰分布 1D Diffusion",
        blurb: "从双峰分布逐步混入高斯噪声，观察结构如何被前向扩散抹平。",
        outcomes: ["理解前向扩散如何破坏结构", "观察噪声调度"],
        result: "alpha_bar 表、分布直方图、噪声统计",
        tier: "B",
        minutes: 15,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch12_diffusion_digits.ipynb",
        title: "Digits Diffusion",
        blurb: "用 8×8 手写数字展示 DDPM 的前向加噪、反向去噪和采样轨迹。",
        outcomes: ["观察清晰数字如何逐步变噪", "理解去噪模型学的是小步修复方向"],
        result: "digits 图像序列、噪声调度表、反向去噪轨迹",
        tier: "B",
        minutes: 24,
        ready: true,
      },
      {
        file: "ch12_gan_toy.ipynb",
        title: "Two Moons GAN",
        blurb: "用 two moons 分布理解生成器和判别器的博弈。",
        outcomes: ["观察判别边界变化", "理解生成分布靠近真实分布"],
        result: "点云图、判别分数、训练轨迹",
        tier: "C",
        minutes: 25,
        ready: true,
      },
      {
        file: "ch12_diffusion_toy.ipynb",
        title: "Two Moons Diffusion",
        blurb: "用 two moons 二维点云展示加噪和去噪方向。",
        outcomes: ["连接前向噪声和反向去噪", "观察二维分布恢复"],
        result: "clean、noisy、denoised 点云",
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

function renderNotebookCard(item) {
  if (!item.ready) {
    return `<article class="nb-card nb-card--soon">
      <h3>${item.title}</h3>
      ${item.blurb ? `<p class="nb-card-blurb">${item.blurb}</p>` : ""}
      <p class="nb-soon">即将推出</p>
    </article>`;
  }
  const details = [item.blurb, item.result].filter(Boolean).join(" · ");
  return `<article class="nb-card">
    <h3>${item.title}</h3>
    ${details ? `<p class="nb-card-blurb">${details}</p>` : ""}
    <div class="nb-actions">
      <a class="nb-btn nb-btn--primary" href="${readerUrl(item.file)}">在线阅读</a>
      <a class="nb-btn" href="${item.file}" download>下载 .ipynb</a>
    </div>
  </article>`;
}

function renderChapterSection(chNum) {
  const ch = CHAPTER_NOTEBOOKS[chNum];
  if (!ch) return "";
  const cards = ch.items.map((item) => renderNotebookCard(item)).join("");
  return `<section class="nb-chapter" id="ch${chNum}">
    <div class="nb-chapter-head">
      <span class="nb-chapter-num">${chNum}</span>
      <div>
        <p class="nb-chapter-question">${ch.question}</p>
        <h2>${ch.title}</h2>
        <a class="nb-back-ch" href="${ch.web}">返回第 ${chNum} 章网页</a>
      </div>
    </div>
    <div class="nb-grid">${cards}</div>
  </section>`;
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
      <section class="nb-overview" aria-labelledby="nbOverviewTitle">
        <div>
          <p class="nb-kicker">Python 代码实验</p>
          <h2 id="nbOverviewTitle">第 ${chNum} 章代码实验</h2>
          <p>Notebook 内嵌本章运行所需的源码和数据；下载后直接运行首个单元即可复现输出。</p>
        </div>
      </section>
      ${renderChapterSection(chNum)}`;
  }
}

function renderIndexPage() {
  window.location.replace("../hub.html");
}

if (typeof window !== "undefined") {
  window.NOTEBOOKS_CATALOG = {
    CHAPTER_NOTEBOOKS,
    readerUrl,
    renderChapterPage,
    renderIndexPage,
  };
}
