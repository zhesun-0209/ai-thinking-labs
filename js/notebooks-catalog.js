/** Notebook catalog for 《AI思维》labs — used by notebooks/*.html */
"use strict";

/** @type {Record<number, { title: string; slug: string; web: string; question: string; items: Array<object> }>} */
const CHAPTER_NOTEBOOKS = {
  5: {
    title: "搜索智能",
    slug: "ch05",
    web: "../ch5.html",
    question: "同一张经典路线图里，为什么不同搜索策略会得到不同探索顺序和路径代价？",
    items: [
      {
        file: "ch05_campus_search.ipynb",
        title: "路线图五种搜索",
        blurb: "从 Arad 到 Bucharest 的经典路线图，对比不同搜索策略怎样展开节点、选择路线。",
        outcomes: ["运行五种搜索函数", "比较路径和总代价"],
        result: "城市图、启发式表、展开过程、路线代价",
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
        title: "动物分类专家系统",
        blurb: "用经典规则链把观察事实推到“老虎”结论，分别跑前向链和后向链。",
        outcomes: ["运行规则表", "观察规则触发路径"],
        result: "事实表、规则表、前向链、后向链、规则路径图",
        tier: "A",
        minutes: 12,
        ready: true,
      },
      {
        file: "ch06_graph_reasoning.ipynb",
        title: "人物知识图谱多跳推理",
        blurb: "用 Marie Curie 小型知识图谱查询到诺贝尔奖节点，展示多跳路径和排序。",
        outcomes: ["加载三元组", "运行多跳查询和路径排序"],
        result: "三元组表、多跳路径、排序解释、路径图",
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
        title: "葡萄酒决策树与鸢尾花聚类",
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
        title: "疾病指标回归与鸢尾花感知机",
        blurb: "用疾病指标回归看误差下降，用鸢尾花二分类看线性边界。",
        outcomes: ["观察回归误差下降", "训练线性分类边界"],
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
        title: "乳腺癌 MLP 分类",
        blurb: "用 Wisconsin 乳腺癌数据训练小型神经网络，观察 loss、混淆矩阵和预测置信度。",
        outcomes: ["训练 MLP 分类器", "查看测试集预测"],
        result: "特征摘要、loss 曲线、混淆矩阵、预测置信度",
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
        file: "ch09_word2vec_analogy.ipynb",
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
        title: "真实照片 Sobel 卷积与 MaxPool",
        blurb: "用真实花朵照片展示边缘卷积和池化压缩。",
        outcomes: ["滑动 Sobel 卷积核", "比较卷积输出和池化输出"],
        result: "真实照片、卷积窗口、边缘特征图、MaxPool 结果",
        tier: "B",
        minutes: 18,
        ready: true,
      },
      {
        file: "ch10_vit_patchify.ipynb",
        title: "真实照片 ViT Patchify",
        blurb: "把一张真实建筑照片切成 16×16 小块，观察图像如何变成一串 patch token。",
        outcomes: ["理解 patch 展平", "查看 token 表"],
        result: "真实图片、patch 网格、token 摘要、局部 patch",
        tier: "B",
        minutes: 15,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch10_mae_masking.ipynb",
        title: "真实照片 MAE 掩码重建",
        blurb: "在同一张真实照片上遮住 75% patch，观察 MAE 的可见输入和重建目标。",
        outcomes: ["观察随机 mask", "理解重建目标"],
        result: "原图、mask map、可见 patch、重建基线",
        tier: "B",
        minutes: 15,
        ready: true,
      },
      {
        file: "ch10_clip_infonce.ipynb",
        title: "CLIP 真实图文匹配",
        blurb: "用预训练 CLIP 匹配真实图片和文本提示，观察正确描述如何获得更高概率。",
        outcomes: ["输入图片和文本提示", "观察图文匹配概率"],
        result: "真实图片、文本 prompt、softmax 概率、对比损失",
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
        title: "冰湖导航价值迭代",
        blurb: "在经典冰湖导航任务里，根据状态转移表计算每个格子的长期价值和最优动作。",
        outcomes: ["拆开 Bellman 更新", "理解 MDP 转移表 P"],
        result: "转移表、价值表、策略箭头、迭代误差",
        tier: "A",
        minutes: 18,
        ready: true,
      },
      {
        file: "ch11_td_learning.ipynb",
        title: "出租车调度 Q-learning",
        blurb: "让智能体学习接送乘客，观察一次动作如何更新 Q 表以及回报如何变化。",
        outcomes: ["理解 TD target", "观察 Q-learning 更新"],
        result: "TD 样本、回报曲线、动作价值、环境渲染",
        tier: "A",
        minutes: 12,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch11_epsilon_greedy.ipynb",
        title: "悬崖行走探索策略",
        blurb: "在经典悬崖行走任务里比较不同探索强度，观察更冒险或更保守的路线。",
        outcomes: ["区分随机探索和当前最优选择", "观察悬崖环境中的策略差异"],
        result: "训练回报、epsilon 对比、学到的策略图",
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
        file: "ch12_iris_parameter_search.ipynb",
        title: "鸢尾花分类参数搜索",
        blurb: "在鸢尾花分类任务里尝试多组模型参数，观察哪些组合让验证准确率更高。",
        outcomes: ["理解参数搜索空间", "观察最优结果如何出现"],
        result: "数据摘要、验证分数、搜索轨迹、参数表现图",
        tier: "A",
        minutes: 12,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch12_mcts.ipynb",
        title: "冰湖导航 MCTS 规划",
        blurb: "从起点反复模拟未来路线，观察访问次数、平均价值和探索项如何共同选择动作。",
        outcomes: ["读懂 UCT 平衡项", "观察 MCTS 如何规划动作"],
        result: "环境地图、根节点统计、UCT 分数、访问价值图",
        tier: "A",
        minutes: 20,
        ready: true,
      },
      {
        file: "ch12_image_diffusion.ipynb",
        title: "真实图片扩散加噪",
        blurb: "把一张花朵照片按时间步逐渐加入噪声，观察信号权重下降、噪声权重上升。",
        outcomes: ["理解噪声调度", "观察真实图片如何逐步变噪"],
        result: "真实图片序列、调度表、信号/噪声权重",
        tier: "B",
        minutes: 15,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch12_image_denoising_diffusion.ipynb",
        title: "真实图片扩散去噪",
        blurb: "用真实花朵照片展示从清晰图像到噪声图像，再到 patch 去噪结果的变化。",
        outcomes: ["观察真实图片如何逐步变噪", "理解去噪模型学的是小步修复方向"],
        result: "真实图片序列、噪声指标、去噪输出、误差图",
        tier: "B",
        minutes: 24,
        ready: true,
      },
      {
        file: "ch12_image_patch_gan.ipynb",
        title: "真实图片 Patch-GAN",
        blurb: "在真实花朵照片 patch 上训练生成器和判别器，观察生成纹理如何接近真实局部图像。",
        outcomes: ["观察生成器与判别器损失", "查看生成 patch"],
        result: "训练曲线、真实 patch、生成 patch、判别器评分",
        tier: "C",
        minutes: 25,
        ready: true,
      },
      {
        file: "ch12_image_denoising.ipynb",
        title: "真实图片去噪重建",
        blurb: "把带噪建筑照片恢复成更干净的图像，对比输入噪声、模型输出和误差。",
        outcomes: ["连接噪声输入和去噪输出", "比较重建误差"],
        result: "MSE 表、原图、带噪输入、去噪输出、误差图",
        tier: "C",
        minutes: 12,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch12_alphafold_concepts.ipynb",
        title: "蛋白序列 Pair 表征",
        blurb: "用胰岛素 A 链片段的多序列对齐观察位置保守性和 pair 表征。",
        outcomes: ["区分 MSA、pair 表征和结构模块", "理解端到端预测链路"],
        result: "MSA、位置保守性、pair 表征热力图",
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

function formatPointList(text) {
  return String(text || "")
    .split(/[、,，]/)
    .map((part) => part.trim())
    .filter(Boolean)
    .join(" · ");
}

function renderNotebookCard(item) {
  if (!item.ready) {
    return `<article class="nb-card nb-card--soon">
      <h3>${item.title}</h3>
      ${item.blurb ? `<p class="nb-card-blurb">${item.blurb}</p>` : ""}
      <p class="nb-soon">即将推出</p>
    </article>`;
  }
  const points = formatPointList(item.result);
  return `<article class="nb-card">
    <h3>${item.title}</h3>
    ${item.blurb ? `<p class="nb-card-blurb">${item.blurb}</p>` : ""}
    ${
      points
        ? `<p class="nb-card-points"><span class="nb-card-points-label">知识点</span><span class="nb-card-points-text">${points}</span></p>`
        : ""
    }
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
          <p>每个 Notebook 都包含本章案例所需代码和数据；下载后按单元格顺序运行即可复现实验输出。</p>
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
