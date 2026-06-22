"use strict";

/* Chapter 7 · 学习智能 — 对齐第5章 + 决策树架构图 */

const { entropy, infoGain, fmt, renderDecisionTree, renderConfusionMatrix, drawScatterRegression, drawKMeans, drawPerceptron } = window.courseViz;
const C = window.courseCopyPrompts?.ch7 || {};

const GD_POINTS = [
  [50, 98], [70, 112], [90, 132], [110, 145], [130, 160], [150, 178], [170, 195], [190, 210],
];
const GD_LINES = [
  [50, 80, 190, 130, 8420],
  [50, 88, 190, 160, 5200],
  [50, 92, 190, 185, 3100],
  [50, 96, 190, 205, 1800],
  [50, 100, 190, 215, 920],
];

const PERCEPTRON_PTS = [
  [22, 88, 1], [46, 74, 1], [64, 96, 1], [86, 82, 1],
  [92, 28, -1], [116, 12, -1], [136, 44, -1], [160, 24, -1],
];
const PERCEPTRON_STEPS = [
  { wx: -0.10, wy: 1, b: -88 },
  { wx: -0.10, wy: 1, b: -78 },
  { wx: -0.10, wy: 1, b: -72 },
  { wx: -0.10, wy: 1, b: -66 },
];

function perceptronMistakes(model) {
  return PERCEPTRON_PTS.flatMap(([x, y, label], i) => (label * (model.wx * x + model.wy * y + model.b) <= 0 ? [i] : []));
}

const KMEANS_PTS = [
  [34, 82], [42, 78], [50, 88], [58, 74], [62, 82], [64, 70],
  [66, 60], [70, 68], [74, 56], [78, 44], [84, 52], [88, 38], [92, 60], [96, 48],
];
const KMEANS_STEPS = [
  { centers: [[38, 86], [74, 66]], assign: null, counts: "未分配" },
  { centers: [[38, 86], [74, 66]], assign: [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], counts: "3+11" },
  { centers: [[42, 82.7], [75.6, 59.3]], assign: [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], counts: "3+11", prevCenters: [[38, 86], [74, 66]] },
  { centers: [[42, 82.7], [75.6, 59.3]], assign: [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1], prevAssign: [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], counts: "5+9", switched: "2 点" },
  { centers: [[49.2, 80.8], [79.1, 55.1]], assign: [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1], counts: "5+9", prevCenters: [[42, 82.7], [75.6, 59.3]] },
  { centers: [[51.7, 79], [81, 53.3]], assign: [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1], prevAssign: [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1], counts: "6+8", switched: "1 点", prevCenters: [[49.2, 80.8], [79.1, 55.1]] },
];

const parentCounts = [20, 18, 12];
const gainScore = infoGain(parentCounts, [
  { counts: [20, 0, 0] },
  { counts: [0, 18, 12] },
]);
const gainConcept = infoGain([0, 18, 12], [
  { counts: [0, 18, 0] },
  { counts: [0, 0, 12] },
]);
const parentEntropy = entropy(parentCounts);
const ERROR_TREE = {
  id: "root",
  question: "作业是否含具体分数？",
  entropy: parentEntropy,
  gain: gainScore,
  yes: { id: "leaf-calc", leaf: true, label: "叶节点", count: 20, prediction: "计算错误" },
  no: {
    id: "split-concept",
    question: "是否概念/定义题？",
    entropy: 0.99,
    gain: 0.17,
    yes: { id: "leaf-concept", leaf: true, label: "叶节点", count: 18, prediction: "概念混淆" },
    no: { id: "leaf-careless", leaf: true, label: "叶节点", count: 12, prediction: "粗心" },
  },
};

const ch7Config = {
  modules: {
    intro: {
      key: "intro",
      cells: [{
        prompt: "学习 = 用更短的描述（树、直线、簇中心）压缩数据。请先认准 **决策树架构图**，再记五个算法各自「压缩成什么」。",
        architectureKey: "decision-tree",
        vibeTip: "内层优化损失（MSE、熵）；外层优化指标（P/R/F1）。",
        copyPrompt: C.intro,
      }],
    },
    compare: {
      key: "compare",
      cells: [{
        prompt: "监督学习需要标签；无监督在数据内部找结构；评估指标帮助选模型与调阈值。",
        tableKey: "ch7-compare",
        copyPrompt: C.compare,
      }],
    },
  },
  notebooks: {
    tree: {
      key: "tree",
      mentorKey: "ch7-tree",
      title: "决策树 + 信息增益",
      subtitle: "50 道错题 · 熵 → 增益 → 分裂",
      cells: [
        {
          prompt: "**学习 = 压缩数据**。决策树用一串问题把 50 道错题分成更纯的子集；信息增益选「问哪个最划算」。",
          architectureKey: "decision-tree",
          vibeTip: "二十 Questions：每个问题把人群分成更纯的两堆。",
          copyPrompt: C.treeConcept,
        },
        {
          prompt: "请观看步进：对照架构图，看「含分数?→计算错误 / 概念题?→概念混淆 / 否则→粗心」。",
          vibeTip: `含分数分裂增益 ≈ ${fmt(gainScore)}（左子树纯为计算错误）；概念题分裂在右子树增益 ≈ ${fmt(gainConcept)}。`,
          demoKey: "tree",
          interactive: true,
          labTarget: "tree",
          copyPrompt: C.treeDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch7-tree" },
        { mentorCell: "selfCheck", mentorKey: "ch7-tree" },
        { mentorCell: "when", mentorKey: "ch7-tree", labTarget: "tree" },
      ],
    },
    gd: {
      key: "gd",
      mentorKey: "ch7-gd",
      title: "线性回归 + 梯度下降",
      subtitle: "房价 ≈ w·面积 + b",
      cells: [
        {
          prompt: "均方误差 MSE 衡量拟合好坏；梯度指向损失上升最快方向，**沿负梯度小步更新** w,b。",
          vibeTip: "蒙眼下山：摸局部坡度，朝最陡下坡挪一步。",
          copyPrompt: C.gdConcept,
        },
        {
          prompt: "观察拟合直线与损失同步下降的 5 步迭代。η 过大震荡，过小收敛慢。",
          demoKey: "gd",
          interactive: true,
          labTarget: "gd",
          copyPrompt: C.gdDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch7-gd" },
        { mentorCell: "selfCheck", mentorKey: "ch7-gd" },
        { mentorCell: "when", mentorKey: "ch7-gd" },
      ],
    },
    perceptron: {
      key: "perceptron",
      mentorKey: "ch7-perceptron",
      title: "感知机线性分类",
      subtitle: "分错才更新 · w,b 同步更新",
      cells: [
        {
          prompt: "线性可分二维点：错分时 w ← w + η·y·x，b ← b + η·y，等价于**移动/旋转决策边界**。XOR 线性不可分，单层感知机学不会。",
          vibeTip: "只在分错时更新——对了就不动。",
          copyPrompt: C.perceptronConcept,
        },
        {
          prompt: "观看步进：哪一点触发更新？边界如何旋转？",
          demoKey: "perceptron",
          interactive: true,
          labTarget: "perceptron",
          copyPrompt: C.perceptronDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch7-perceptron" },
        { mentorCell: "selfCheck", mentorKey: "ch7-perceptron" },
        { mentorCell: "when", mentorKey: "ch7-perceptron" },
      ],
    },
    kmeans: {
      key: "kmeans",
      mentorKey: "ch7-kmeans",
      title: "K-均值聚类",
      subtitle: "E 步分配 · M 步更新中心",
      cells: [
        {
          prompt: "无标签成绩散点，K=2。E 步每点归最近中心，M 步中心移到簇均值，直到分配稳定。",
          vibeTip: "K 个磁铁：点被吸住，磁铁再移到簇内平均位置。",
          copyPrompt: C.kmeansConcept,
        },
        {
          prompt: "观看步进：分配与中心如何交替更新？",
          demoKey: "kmeans",
          interactive: true,
          labTarget: "kmeans",
          copyPrompt: C.kmeansDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch7-kmeans" },
        { mentorCell: "selfCheck", mentorKey: "ch7-kmeans" },
        { mentorCell: "when", mentorKey: "ch7-kmeans" },
      ],
    },
    metrics: {
      key: "metrics",
      mentorKey: "ch7-metrics",
      title: "混淆矩阵 → P / R / F1",
      subtitle: "外层评估 · 调阈值",
      cells: [
        {
          prompt: "同一模型输出概率，阈值 τ 不同 → TP/FP/FN/TN 变化 → P、R、F1 此消彼长。这是**外层优化**，与内层损失分开。",
          vibeTip: "抓逃犯：严门槛少误抓（P↑）但漏抓多（R↓）。",
          copyPrompt: C.metricsConcept,
        },
        {
          prompt: "步进切换三档阈值 τ=0.35 / 0.50 / 0.65，观察 TP/FP/FN/TN 与 P、R、F1 如何此消彼长。",
          demoKey: "metrics",
          interactive: true,
          labTarget: "metrics",
          copyPrompt: C.metricsDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch7-metrics" },
        { mentorCell: "selfCheck", mentorKey: "ch7-metrics" },
        { mentorCell: "when", mentorKey: "ch7-metrics" },
      ],
    },
  },
  demos: {
    tree: {
      key: "tree",
      stepLabels: ["根·算熵", "比增益", "分裂1", "分裂2", "完整树"],
      trace: [
        {
          title: "根节点 · 计算熵",
          summary: "50 题三类错因，分布均匀-ish，熵较高。",
          reason: "H(S) = −Σ p_k log₂ p_k，三类占比 20/50、18/50、12/50。",
          fields: [
            { label: "样本", value: "50 题" },
            { label: "H(S)", value: fmt(entropy(parentCounts)) },
            { label: "候选特征", value: "含分数 / 概念题" },
          ],
          highlight: ["root"],
        },
        {
          title: "比较信息增益",
          summary: "「含分数」分裂增益明显更大。",
          reason: "ΔH = H(父) − Σ (|S_v|/|S|) H(S_v)。含分数使左子树纯为计算错误。",
          fields: [
            { label: "H(父)", value: fmt(entropy(parentCounts)) },
            { label: "ΔH(含分数)", value: fmt(gainScore) },
            { label: "ΔH(概念题@根)", value: fmt(infoGain(parentCounts, [{ counts: [0, 18, 12] }])) + "（较小）" },
          ],
          highlight: ["root"],
        },
        {
          title: "第一次分裂",
          summary: "按「含分数=是」得到纯叶：计算错误。",
          reason: "20 题全部同一类 → 子树熵为 0，无需再分。",
          fields: [
            { label: "左叶", value: "20 题 → 计算错误" },
            { label: "H(左)", value: "0" },
          ],
          highlight: ["root", "leaf-calc"],
        },
        {
          title: "右子树再分",
          summary: "剩余 30 题按「概念题」分裂。",
          reason: "概念题=是 → 18 题概念混淆；否 → 12 题粗心。",
          fields: [
            { label: "ΔH(概念题)", value: fmt(gainConcept) },
            { label: "右左叶", value: "概念混淆 (18)" },
            { label: "右右叶", value: "粗心 (12)" },
          ],
          highlight: ["split-concept", "leaf-concept", "leaf-careless"],
        },
        {
          title: "完整决策树",
          summary: "可解释的 if-else 规则，可用于新错题诊断。",
          reason: "树深度 2，三条路径对应三种错因，与数据完全拟合（演示用，真实场景需剪枝防过拟合）。",
          fields: [{ label: "规则数", value: "3 条叶路径" }],
          highlight: ["root", "leaf-calc", "split-concept", "leaf-concept", "leaf-careless"],
        },
      ],
      render(v, s) {
        renderDecisionTree(v, ERROR_TREE, s.highlight || []);
      },
    },
    gd: {
      key: "gd",
      stepLabels: ["t=0", "t=1", "t=2", "t=3", "收敛"],
      trace: GD_LINES.map(([x0, y0, x1, y1, loss], i) => ({
        title: i === 0 ? "随机初始化 w,b" : i === GD_LINES.length - 1 ? "损失趋稳" : `梯度下降第 ${i} 步`,
        summary: i === 0 ? "直线偏离数据，MSE 很高。" : `MSE 降至 ${loss}。`,
        reason: i === 0 ? "随机 w,b 给出较差拟合。" : "沿 −∇MSE 更新参数，直线向数据靠拢。",
        fields: [
          { label: "MSE", value: String(loss) },
          { label: "η", value: "0.01" },
        ],
        lineIdx: i,
      })),
      render(v, s) {
        courseShared.renderCanvasDemo(v, s, (ctx, w, h) => {
          const line = GD_LINES[s.lineIdx];
          const [x0, y0, x1, y1, loss] = line;
          const slope = (y1 - y0) / (x1 - x0);
          const intercept = y0 - slope * x0;
          drawScatterRegression(ctx, w, h, GD_POINTS, line, {
            xLabel: "面积 m²",
            yLabel: "房价（万）",
            loss,
            w: slope,
            b: intercept,
            eta: "0.01",
            step: s.lineIdx,
          });
        });
      },
    },
    perceptron: {
      key: "perceptron",
      stepLabels: ["初", "更新1", "更新2", "收敛"],
      trace: PERCEPTRON_STEPS.map((model, i) => {
        const wrongCount = perceptronMistakes(model).length;
        return {
          title: i === 0 ? "初始随机边界" : wrongCount === 0 ? "线性可分 · 全部分对" : `错分驱动更新 ${i}`,
          summary: wrongCount === 0 ? "没有样本被错分，边界收敛。" : `蓝色空心圈标出当前真实错分的 ${wrongCount} 个样本。`,
          reason: "感知机更新：若 y·(⟨w,x⟩+b)≤0，则 w←w+ηyx，b←b+ηy。",
          fields: [
            { label: "步数", value: String(i) },
            { label: "错分", value: `${wrongCount} 个` },
          ],
          model,
          prevModel: i > 0 ? PERCEPTRON_STEPS[i - 1] : null,
          wrongCount,
          converged: wrongCount === 0,
        };
      }),
      render(v, s) {
        courseShared.renderCanvasDemo(v, s, (ctx, w, h) =>
          drawPerceptron(ctx, w, h, PERCEPTRON_PTS, s.model, null, { wrongCount: s.wrongCount, converged: s.converged, prevModel: s.prevModel }),
        );
      },
    },
    kmeans: {
      key: "kmeans",
      stepLabels: ["初始化", "E1", "M1", "E2", "M2", "收敛"],
      trace: [
        { title: "随机初始化中心", summary: "C₁、C₂ 放在两个候选位置，所有点暂未着色。", reason: "K=2，先随机给出两个质心。", fields: [{ label: "分配", value: "未开始" }], step: 0 },
        { title: "E1 · 首次分配", summary: "每个点分给最近质心，右侧质心暂时吸走了过多中间点。", reason: "assign(i)=argmin_k ||x_i−μ_k||。", fields: [{ label: "分配", value: "3+11" }], step: 1 },
        { title: "M1 · 质心移动", summary: "质心移到各自簇内均值，C₂ 被拉向右下，C₁ 留在左上。", reason: "μ_k = (1/|C_k|) Σ x_i。", fields: [{ label: "中心", value: "第一次更新" }], step: 2 },
        { title: "E2 · 两个点换簇", summary: "两个边界点离 C₁ 更近，从 C₂ 切回 C₁。", reason: "质心位置变化后，最近中心也会变化。", fields: [{ label: "分配", value: "5+9" }], step: 3 },
        { title: "M2 · 再次更新", summary: "C₁ 继续向过渡点靠近，C₂ 稳定在右下区域。", reason: "按新的簇成员重新求均值。", fields: [{ label: "中心", value: "第二次更新" }], step: 4 },
        { title: "收敛", summary: "最后一个过渡点切到 C₁，之后分配不再变化。", reason: "再执行 E/M 步，簇成员保持稳定。", fields: [{ label: "分配", value: "6+8" }], step: 5 },
      ],
      render(v, s) {
        const st = KMEANS_STEPS[s.step];
        courseShared.renderCanvasDemo(v, s, (ctx, w, h) =>
          drawKMeans(ctx, w, h, KMEANS_PTS, st.centers, st.assign, {
            prevAssign: st.prevAssign,
            prevCenters: st.prevCenters,
            counts: st.counts,
            switched: st.switched,
          }),
        );
      },
    },
    metrics: {
      key: "metrics",
      stepLabels: ["τ=0.35", "τ=0.50", "τ=0.65"],
      trace: [
        { title: "低阈值 τ=0.35", summary: "模型激进，召回高、误报多。", reason: "更多样本被判为正类。", tp: 42, fp: 28, fn: 8, tn: 22, thr: 0.35 },
        { title: "中阈值 τ=0.50", summary: "P 与 R 较均衡。", reason: "默认分类边界。", tp: 38, fp: 12, fn: 12, tn: 38, thr: 0.50 },
        { title: "高阈值 τ=0.65", summary: "模型保守，精确高、漏检多。", reason: "只有高置信度才判正。", tp: 30, fp: 4, fn: 20, tn: 46, thr: 0.65 },
      ],
      render(v, s) {
        renderConfusionMatrix(v, { tp: s.tp, fp: s.fp, fn: s.fn, tn: s.tn, thr: s.thr });
      },
    },
  },
  tables: {
    "ch7-compare": `<div class="table-wrap compact"><table class="run-table compact comparison-table"><thead><tr><th>算法</th><th>监督</th><th>产出</th><th>典型指标</th></tr></thead><tbody>
      <tr><td>决策树</td><td>有</td><td>if-else 树</td><td>准确率、可解释性</td></tr>
      <tr><td>线性回归</td><td>有</td><td>w, b</td><td>MSE、R²</td></tr>
      <tr><td>感知机</td><td>有</td><td>超平面</td><td>错分率</td></tr>
      <tr><td>K-均值</td><td>无</td><td>簇中心</td><td>簇内 SSE</td></tr>
      <tr><td>评估</td><td>—</td><td>混淆矩阵</td><td>P, R, F1</td></tr></tbody></table></div>`,
  },
  labAlgos: [
    { key: "tree", label: "决策树", demo: "tree", desc: "50 道错题：逐步计算熵与信息增益，构建可解释分类树。" },
    { key: "gd", label: "梯度下降", demo: "gd", desc: "房价回归：观察 MSE 随梯度下降迭代而减小。" },
    { key: "perceptron", label: "感知机", demo: "perceptron", desc: "二维点分错时旋转决策边界。" },
    { key: "kmeans", label: "K-均值", demo: "kmeans", desc: "成绩散点：E/M 两步交替直到簇分配稳定。" },
    { key: "metrics", label: "评估指标", demo: "metrics", desc: "步进切换 τ=0.35/0.50/0.65，对照 TP/FP 与 P/R/F1。" },
  ],
};

window.courseShared.bootstrapChapter(
  {
    chapterNum: 7,
    pageTitle: "学习算法 · 案例分步理解",
    eyebrow: "《AI思维》第7章 · 学习智能",
    title: "五种学习方法，错题案例讲清楚",
    readingMeta: "约 28 分钟 · 5 种算法",
    sections: [
      { id: "hero", label: "开篇" },
      { id: "m0", label: "概览" },
      { id: "m1", label: "监督" },
      { id: "m2", label: "无监督" },
      { id: "m3", label: "评估" },
      { id: "m4", label: "对比" },
      { id: "lab", label: "实验室" },
    ],
  },
  ch7Config,
);
