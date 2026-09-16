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
        blurb: "用 Wisconsin 乳腺癌数据训练小型神经网络，观察训练损失、混淆矩阵和预测置信度。",
        outcomes: ["训练 MLP 分类器", "查看测试集预测"],
        result: "特征摘要、损失曲线、混淆矩阵、预测置信度",
        tier: "B",
        minutes: 25,
        ready: true,
      },
      {
        file: "ch08_transe_attention.ipynb",
        title: "国家-首都 TransE 与注意力",
        blurb: "训练国家到首都的关系向量，再用句子注意力权重看词之间的连接。",
        outcomes: ["训练 TransE 关系向量", "观察查询词如何分配注意力"],
        result: "训练距离、候选尾实体、几何图、注意力权重、最高关注标注",
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
        blurb: "用经典英文词频语料观察高频符号对如何形成子词。",
        outcomes: ["统计高频符号对", "理解子词词表的生成逻辑"],
        result: "初始词表、合并轮次、符号对频次图、词元数变化",
        tier: "A",
        minutes: 10,
        ready: true,
      },
      {
        file: "ch09_word2vec_analogy.ipynb",
        title: "Skip-gram 小语料训练",
        blurb: "从中心词-上下文样本训练词向量，再观察最近邻和 king - man + woman 类比。",
        outcomes: ["生成上下文样本", "训练 Skip-gram", "观察类比向量"],
        result: "训练样本、损失曲线、最近邻、类比相似度、二维投影",
        tier: "B",
        minutes: 15,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch09_attention_lm.ipynb",
        title: "因果注意力与二元词语言模型",
        blurb: "用清晰句子展示因果遮罩、每行最高关注词和下一词分布。",
        outcomes: ["读懂因果遮罩", "查看每个位置关注谁", "连接注意力和下一词预测"],
        result: "可见上下文、最高关注标注、注意力矩阵、二元词概率",
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
    question: "图像如何被卷积、图块、掩码和跨模态对比转成可学习表示？",
    items: [
      {
        file: "ch10_conv2d_numpy.ipynb",
        title: "真实照片 Sobel 卷积与最大池化",
        blurb: "用真实花朵照片展示边缘卷积和池化压缩。",
        outcomes: ["滑动 Sobel 卷积核", "比较卷积输出和池化输出"],
        result: "真实照片、卷积窗口、边缘特征图、最大池化结果",
        tier: "B",
        minutes: 18,
        ready: true,
      },
      {
        file: "ch10_vit_patchify.ipynb",
        title: "真实照片 ViT 图块切分",
        blurb: "把一张真实建筑照片切成 16×16 小块，观察图像如何变成一串图块向量。",
        outcomes: ["理解图块展平", "查看图块向量表"],
        result: "真实图片、图块网格、向量摘要、局部图块",
        tier: "B",
        minutes: 15,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch10_mae_masking.ipynb",
        title: "真实照片 MAE 掩码重建",
        blurb: "用预训练 ViT-MAE 遮住真实照片的大部分图块，再根据可见图块重建遮挡区域。",
        outcomes: ["观察随机遮挡", "运行预训练 MAE 重建", "理解重建目标"],
        result: "原图、遮挡图、可见输入、预测图块、重建结果、误差图",
        tier: "B",
        minutes: 15,
        ready: true,
      },
      {
        file: "ch10_clip_infonce.ipynb",
        title: "CLIP 真实图文匹配",
        blurb: "用预训练 CLIP 匹配真实图片和文本提示，观察正确描述如何获得更高概率。",
        outcomes: ["输入图片和文本提示", "观察图文匹配概率"],
        result: "真实图片、文本提示、归一化概率、对比损失",
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
        blurb: "在经典冰湖导航任务里，先看起点和动作转移，再计算每个格子的长期价值和最优动作。",
        outcomes: ["查看起点动作分布", "拆开一次 Bellman 更新"],
        result: "环境地图、起点转移、Bellman 单步表、价值表、策略箭头、迭代误差",
        tier: "A",
        minutes: 18,
        ready: true,
      },
      {
        file: "ch11_td_learning.ipynb",
        title: "出租车调度 Q-learning",
        blurb: "先渲染出租车初始状态，再观察 Q 表更新，并执行训练后的接送路线。",
        outcomes: ["读懂状态和动作", "观察 Q-learning 更新", "查看训练后路线"],
        result: "初始状态、动作表、TD 样本、训练后路线、回报曲线、Q 值图",
        tier: "A",
        minutes: 12,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch11_epsilon_greedy.ipynb",
        title: "悬崖行走探索策略",
        blurb: "先看起点每个动作的一步结果，再比较不同探索强度下的完成路线。",
        outcomes: ["查看起点候选动作", "区分随机探索和当前最优选择", "观察训练后路径"],
        result: "悬崖地图、起点动作、探索解释、贪心路径、训练回报、探索率对比、策略图",
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
        blurb: "在鸢尾花分类任务里先粗搜参数空间，再围绕当前最好区域局部加密。",
        outcomes: ["理解参数搜索空间", "区分粗搜和局部加密", "观察最优结果如何出现"],
        result: "数据摘要、阶段分数、搜索轨迹、参数表现图",
        tier: "A",
        minutes: 12,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch12_mcts.ipynb",
        title: "冰湖导航 MCTS 规划",
        blurb: "用模拟比较候选路线，按访问次数选择动作；走到新位置后重新规划，观察滑动如何改变下一步选择。",
        outcomes: ["查看起点候选动作", "读懂 UCT 平衡项"],
        result: "起点地图、候选动作、模拟与回传、逐步规划、状态价值、多局比较",
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
        blurb: "用真实花朵照片展示前向加噪，并用公开预训练 DDPM 展示反向采样轨迹。",
        outcomes: ["观察真实图片如何逐步变噪", "理解反向采样轨迹", "比较去噪结果"],
        result: "真实图片序列、噪声指标、预训练 DDPM 轨迹、误差图",
        tier: "B",
        minutes: 24,
        ready: true,
      },
      {
        file: "ch12_image_patch_gan.ipynb",
        title: "28×28 手写数字 GAN",
        blurb: "用清晰放大的公开手写数字训练生成器和判别器，观察生成数字如何接近真实数字。",
        outcomes: ["观察生成器与判别器损失", "对比真实数字和生成数字"],
        result: "训练曲线、真实数字、生成数字、判别器评分",
        tier: "C",
        minutes: 25,
        ready: true,
      },
      {
        file: "ch12_image_denoising.ipynb",
        title: "真实图片去噪重建",
        blurb: "把带噪建筑照片恢复成更干净的图像，对比输入噪声、模型输出和误差。",
        outcomes: ["连接噪声输入和去噪输出", "比较重建误差"],
        result: "均方误差表、原图、带噪输入、去噪输出、误差图",
        tier: "C",
        minutes: 12,
        scope: "extension",
        ready: true,
      },
      {
        file: "ch12_alphafold_concepts.ipynb",
        title: "蛋白序列位置对表征",
        blurb: "用胰岛素 A 链片段的多序列对齐，展示保守性、位置对表征和候选接触图。",
        outcomes: ["读懂 MSA 表", "理解位置对表征从哪里来", "查看候选接触"],
        result: "MSA 表、保守性计算、位置对示例、候选接触、位置对热力图",
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

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);
}

function findNotebook(value) {
  const filename = /\.ipynb$/i.test(value) ? value.replace(/\.ipynb$/i, ".ipynb") : value + ".ipynb";
  return Object.values(CHAPTER_NOTEBOOKS).flatMap((chapter) => chapter.items)
    .find((item) => item.ready && item.file === filename) || null;
}

function renderNotebookCard(item, headingLevel) {
  const title = escapeHtml(item.title);
  const heading = "h" + headingLevel;
  const content = "<" + heading + ">" + title + "</" + heading + ">" +
    (item.blurb ? '<p class="nb-card-blurb">' + escapeHtml(item.blurb) + "</p>" : "");
  if (!item.ready) {
    return '<article class="nb-card"><div>' + content + '</div><p class="nb-soon">即将推出</p></article>';
  }
  const points = String(item.result || "").split(/[、,，]/).map((part) => part.trim()).filter(Boolean).join(" · ");
  return '<article class="nb-card"><div>' + content +
    (points ? '<p class="nb-card-meta"><span class="nb-card-points-label">知识点</span>' + escapeHtml(points) + '</p>' : "") +
    '</div><div class="nb-actions">' +
    '<a class="nb-btn nb-btn--primary" href="' + readerUrl(item.file) + '" aria-label="在线阅读：' + title + '">在线阅读</a>' +
    '<a class="nb-btn" href="' + escapeHtml(item.file) + '" download aria-label="下载 ' + title + ' .ipynb">下载 .ipynb</a>' +
    "</div></article>";
}

function renderChapterSection(chNum, single = false) {
  const ch = CHAPTER_NOTEBOOKS[chNum];
  if (!ch) return "";
  const labelId = single ? "nbPageTitle" : "nbChapterTitle" + chNum;
  const heading = single
    ? '<p class="nb-chapter-count">' + ch.items.length + " 个实验</p>"
    : '<h2 id="' + labelId + '">第 ' + chNum + " 章 · " + escapeHtml(ch.title) + "</h2>";
  return '<section class="nb-chapter" id="ch' + chNum + '" aria-labelledby="' + labelId + '">' +
    '<div class="nb-chapter-head">' + heading +
    '<a class="nb-back-ch" href="' + ch.web + '">第 ' + chNum + ' 章正文</a></div><div class="nb-grid">' +
    ch.items.map((item) => renderNotebookCard(item, single ? 2 : 3)).join("") + "</div></section>";
}

function setPageTitle(title) {
  const titleEl = document.getElementById("nbPageTitle");
  if (titleEl) titleEl.textContent = title;
  document.title = title + " · AI思维 Python 实验";
}

function renderInvalidChapterPage() {
  setPageTitle("未找到该章节");
  const mainEl = document.getElementById("nbMain");
  if (mainEl) {
    mainEl.innerHTML = '<section class="nb-empty"><p>可用章节：第 5-12 章。</p>' +
      '<a class="nb-btn nb-btn--primary" href="chapter.html?ch=5-12">查看全部实验</a></section>';
  }
}

function renderChapterPage(chNum) {
  if (!Number.isInteger(chNum) || !Object.hasOwn(CHAPTER_NOTEBOOKS, chNum)) {
    renderInvalidChapterPage();
    return;
  }
  setPageTitle("第 " + chNum + " 章 · " + CHAPTER_NOTEBOOKS[chNum].title);
  const mainEl = document.getElementById("nbMain");
  if (mainEl) mainEl.innerHTML = renderChapterSection(chNum, true);
}

function renderChapterRangePage(start, end) {
  if (![start, end].every((num) => Number.isInteger(num) && Object.hasOwn(CHAPTER_NOTEBOOKS, num))) {
    renderInvalidChapterPage();
    return;
  }
  const low = Math.min(start, end);
  const high = Math.max(start, end);
  if (low === high) {
    renderChapterPage(low);
    return;
  }
  const chapterNums = Object.keys(CHAPTER_NOTEBOOKS).map(Number).filter((num) => num >= low && num <= high);
  setPageTitle("第 " + low + "-" + high + " 章 · Python 实验");
  const mainEl = document.getElementById("nbMain");
  if (mainEl) mainEl.innerHTML = chapterNums.map((num) => renderChapterSection(num)).join("");
}

function renderIndexPage() {
  window.location.replace("../hub.html");
}

if (typeof window !== "undefined") {
  window.NOTEBOOKS_CATALOG = {
    CHAPTER_NOTEBOOKS,
    readerUrl,
    findNotebook,
    renderChapterPage,
    renderChapterRangePage,
    renderIndexPage,
  };
}
