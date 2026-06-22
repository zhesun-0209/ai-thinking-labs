"use strict";

/* Chapter 8 · 连接智能 */

const C = window.courseCopyPrompts?.ch8 || {};
const viz = window.courseViz;

const ch8Config = {
  modules: {
    intro: {
      key: "intro",
      cells: [{
        prompt: "在动手之前，先建立一条主线：**前向 = 算输出，反向 = 分责任，嵌入 = 向量化符号，注意力 = 软查询**。\n\n请认准 MLP 架构图——接下来的演示都会沿着这张「流水线」理解数据流。",
        architectureKey: "mlp",
        vibeTip: "重点看数据如何在层间流动，不必先背求导公式。",
        copyPrompt: C.intro,
      }],
    },
    activations: {
      key: "activations",
      cells: [{
        prompt: "没有激活函数，多层线性叠起来仍是一条直线——**非线性从激活来**。请对照三条曲线：隐藏层常用 ReLU，输出概率用 Sigmoid。",
        demoKey: "activations",
        interactive: true,
        vibeTip: "追问自己：如果全是线性层，网络能拟合 XOR 吗？",
        copyPrompt: C.activations,
      }],
    },
    compare: { key: "compare", cells: [{
      prompt: "前向/反向、TransE、Attention 各解决什么问题？请对照下表，各用本页小例子一句话说明适用场景。",
      tableKey: "ch8-compare",
      copyPrompt: C.compare,
    }] },
  },
  notebooks: {
    forward: {
      key: "forward",
      mentorKey: "ch8-forward",
      title: "前向传播",
      subtitle: "流水线从左到右 — 先会「算」，再学「改」",
      cells: [
        {
          prompt: "**为什么先学前向？** 因为反向传播需要一张「送货单」——前向时保存每层激活 a，反向才知道每站收了多少货。",
          architectureKey: "mlp",
          vibeTip: "把每层想成工厂一站：输入产品 → 加工 → 输出给下一站。",
          copyPrompt: C.forwardConcept,
        },
        {
          prompt: "请观看步进演示。输入 x=[6.2, 0.8]（血糖、运动），逐层点亮，直到 ŷ=0.82。",
          demoKey: "forward",
          labTarget: "forward",
          interactive: true,
          outputLabel: "步进演示",
          copyPrompt: C.forwardDemo,
        },
        {
          mentorCell: "misconception",
          mentorKey: "ch8-forward",
        },
        {
          mentorCell: "selfCheck",
          mentorKey: "ch8-forward",
          copyPrompt: C.forwardSelfCheck,
        },
        {
          mentorCell: "when",
          mentorKey: "ch8-forward",
          prompt: "在实验室切换「前向」反复播放，直到你能 **预测下一步哪层被点亮**。",
          labTarget: "forward",
          copyPrompt: C.forwardLab,
        },
      ],
    },
    backward: {
      key: "backward",
      mentorKey: "ch8-backward",
      title: "反向传播",
      subtitle: "误差溯源 — 谁该为最终错误负责",
      cells: [
        {
          prompt: "**反向在分责任**：输出层误差最大，通过链式法则按贡献分给各层 W。ReLU 在 z≤0 处「截断」责任——该神经元前向没激活，就不更新。",
          architectureKey: "mlp",
          vibeTip: "快递丢件：从收件问题倒查每一环。",
          copyPrompt: C.backwardConcept,
        },
        {
          prompt: "观看步进：δ 从输出出现，逐层回传。",
          demoKey: "backward",
          labTarget: "backward",
          interactive: true,
          copyPrompt: C.backwardDemo,
        },
        {
          mentorCell: "misconception",
          mentorKey: "ch8-backward",
        },
        {
          mentorCell: "selfCheck",
          mentorKey: "ch8-backward",
        },
        { mentorCell: "when", mentorKey: "ch8-backward", labTarget: "backward" },
      ],
    },
    transe: {
      key: "transe",
      mentorKey: "ch8-transe",
      title: "TransE 图谱嵌入",
      subtitle: "关系 = 向量空间里的平移",
      cells: [
        {
          prompt: "符号推理用规则；连接智能把 **(鲁迅,创作,呐喊)** 变成可计算的 h+r≈t。负采样防止模型把所有实体叠在同一点。",
          architectureKey: "transe",
          vibeTip: "几何直觉：从「鲁迅」出发，加上「创作」向量，应落在「呐喊」附近。",
          copyPrompt: C.transeConcept,
        },
        {
          prompt: "观看步进：正例距离缩小，负例（红楼梦）被推远。",
          demoKey: "transe",
          labTarget: "transe",
          interactive: true,
          copyPrompt: C.transeDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch8-transe" },
        { mentorCell: "selfCheck", mentorKey: "ch8-transe" },
        { mentorCell: "when", mentorKey: "ch8-transe" },
      ],
    },
    attention: {
      key: "attention",
      mentorKey: "ch8-attention",
      title: "Encoder–Decoder 注意力",
      subtitle: "翻译时「该看源句哪几个词」",
      cells: [
        {
          prompt: "RNN 把源句压成一个向量，长句会丢信息。**Attention 让解码每一步「软查询」Encoder 全部位置**——这是 Transformer 的核心思想之一。",
          architectureKey: "encoder-decoder",
          architectureStep: { highlight: ["enc", "dec", "attn"] },
          vibeTip: "图书馆：Q=你的问题，K=索引卡，V=书页内容。",
          copyPrompt: C.attentionConcept,
        },
        {
          prompt: "先看架构图里 Attention 桥，再看热力图：解码「日记」为何 heavily attend「写」？",
          demoKey: "attention",
          labTarget: "attention",
          interactive: true,
          outputLabel: "注意力热力图",
          copyPrompt: C.attentionDemo,
        },
        {
          mentorCell: "misconception",
          mentorKey: "ch8-attention",
        },
        {
          mentorCell: "selfCheck",
          mentorKey: "ch8-attention",
        },
        { mentorCell: "when", mentorKey: "ch8-attention", labTarget: "attention" },
      ],
    },
  },
  demos: {
    activations: {
      key: "activations",
      architectureKey: "mlp",
      stepLabels: ["ReLU", "Sigmoid", "对比"],
      trace: [
        { title: "ReLU", summary: "隐藏层常用：负半轴截断为 0。", reason: "max(0,x) 引入非线性。", highlight: "relu" },
        { title: "Sigmoid", summary: "输出概率 ŷ∈(0,1)。", reason: "适合二分类输出。", highlight: "sigmoid" },
        { title: "对比", summary: "多层线性仍等价于一层线性；XOR 需要非线性。", reason: "必须有激活函数。", highlight: null, mode: "xor" },
      ],
      render(v, s) {
        if (s.mode === "xor") {
          window.courseViz.renderXorDemo(v);
          return;
        }
        window.courseViz.renderActivationCurves(v, s.highlight);
      },
    },
    forward: {
      key: "forward",
      architectureKey: "mlp",
      stepLabels: ["输入", "隐藏", "输出"],
      trace: [
        { title: "输入层", summary: "原始特征进入网络。", reason: "x 不做非线性。", fields: [{ label: "x", value: "[6.2, 0.8]" }], activeLayer: 0, architectureStep: { highlight: ["in"] } },
        { title: "隐藏层 ReLU", summary: "线性后截断负值。", reason: "负半轴梯度为 0。", fields: [{ label: "h", value: "[0.71, 0.45]" }], activeLayer: 1, architectureStep: { highlight: ["hid"] } },
        { title: "输出 Sigmoid", summary: "高风险概率。", reason: "ŷ∈(0,1) 可解释。", fields: [{ label: "ŷ", value: "0.82" }], activeLayer: 2, architectureStep: { highlight: ["out"] } },
      ],
      render(v, s) { viz.renderMLP(v, s); },
    },
    backward: {
      key: "backward",
      architectureKey: "mlp",
      stepLabels: ["δ_out", "δ_h", "∂W"],
      trace: [
        { title: "输出层 δ", summary: "误差从这里出发。", fields: [{ label: "δ_out", value: "0.036" }], phase: 0, architectureStep: { highlight: ["out"] } },
        { title: "隐藏层 δ", summary: "链式法则回传。", fields: [{ label: "δ_h", value: "[0.018, 0.011]" }], phase: 1, architectureStep: { highlight: ["hid"] } },
        { title: "更新 W", summary: "W ← W − η∇W，η=0.01。", fields: [{ label: "ΔW_h", value: "[−0.00018, −0.00011]" }, { label: "ΔW_out", value: "−0.00036" }, { label: "关键", value: "需前向保存 a" }], phase: 2, architectureStep: { highlight: ["hid"] } },
      ],
      render(v, s) { viz.renderMLPBackward(v, s); },
    },
    transe: {
      key: "transe",
      architectureKey: "transe",
      stepLabels: ["嵌入", "正例", "负例", "更新"],
      trace: [
        {
          title: "嵌入三元组",
          summary: "把 (鲁迅, 创作, 呐喊) 放进向量空间。",
          reason: "TransE 的核心假设是：头实体向量 h 加上关系向量 r，应接近尾实体向量 t。",
          fields: [{ label: "形式", value: "h + r ≈ t" }, { label: "维度 d", value: "64" }],
          kind: "init",
        },
        {
          title: "正例拉近",
          summary: "正确尾实体「呐喊」应靠近预测点 h+r。",
          reason: "正例距离 d⁺=||h+r−t|| 越小，说明这条真实三元组越容易被模型打高分。",
          fields: [{ label: "正例", value: "(鲁迅, 创作, 呐喊)" }, { label: "d⁺", value: "0.31" }],
          dist: 0.31,
          kind: "pos",
        },
        {
          title: "负例推远",
          summary: "把尾实体替换成错误的「红楼梦」，模型应把它推远。",
          reason: "负例距离 d⁻=||h+r−t′|| 越大，越能区分真实事实和错误事实。",
          fields: [{ label: "负例", value: "(鲁迅, 创作, 红楼梦)" }, { label: "d⁻", value: "2.08" }],
          dist: 2.08,
          kind: "neg",
        },
        {
          title: "Margin 更新",
          summary: "训练目标不是让所有距离都小，而是让正例明显比负例近。",
          reason: "损失 L=max(0, margin+d⁺−d⁻)。当 d⁻ 足够大、d⁺ 足够小时，这一步损失变为 0。",
          fields: [{ label: "margin", value: "1.0" }, { label: "d⁺ / d⁻", value: "0.28 / 2.08" }],
          dist: 0.28,
          kind: "update",
        },
      ],
      render(v, s) { viz.renderTransE(v, s); },
    },
    attention: {
      key: "attention",
      architectureKey: "encoder-decoder",
      stepLabels: ["Q 查询 K", "Softmax", "加权 V"],
      trace: [
        {
          title: "Q 查询 Encoder 的 K",
          summary: "Decoder 当前要生成「日记」，先拿 Q 去问源句每个位置。",
          reason: "Q 来自 Decoder 当前状态；K/V 来自 Encoder 对「鲁迅 写 日记」的编码。",
          fields: [{ label: "最高分", value: "写：2.1" }],
          mode: "cross",
          phase: "score",
          queryToken: "日记",
          sourceTokens: ["鲁迅", "写", "日记"],
          scores: [0.4, 2.1, 0.3],
          weights: [0.05, 0.8, 0.15],
          focusIndex: 1,
          architectureStep: { highlight: ["attn"] },
        },
        {
          title: "Softmax 变权重",
          summary: "分数归一化后，「写」占 0.80，说明当前步主要看谓语位置。",
          reason: "Softmax 后所有权重相加为 1，注意力不是硬选择一个词，而是软分配。",
          fields: [{ label: "权重和", value: "1.00" }, { label: "α(写)", value: "0.80" }],
          mode: "cross",
          phase: "softmax",
          queryToken: "日记",
          sourceTokens: ["鲁迅", "写", "日记"],
          scores: [0.4, 2.1, 0.3],
          weights: [0.05, 0.8, 0.15],
          focusIndex: 1,
          architectureStep: { highlight: ["attn"] },
        },
        {
          title: "加权 V 得上下文",
          summary: "按 α 加权各位置 V，得到当前 Decoder 需要的上下文向量。",
          reason: "「写」的 V 贡献最大，因此输出「日记」时保留了动宾关系线索。",
          fields: [{ label: "context", value: "ΣαᵢVᵢ" }, { label: "最大贡献", value: "写 0.80" }],
          mode: "cross",
          phase: "context",
          queryToken: "日记",
          sourceTokens: ["鲁迅", "写", "日记"],
          scores: [0.4, 2.1, 0.3],
          weights: [0.05, 0.8, 0.15],
          focusIndex: 1,
          architectureStep: { highlight: ["enc", "dec", "attn"] },
        },
      ],
      render(v, s) { viz.renderAttentionFlow(v, s); },
    },
  },
  tables: {
    "ch8-compare": `<div class="table-wrap compact"><table class="run-table compact comparison-table"><thead><tr><th>模块</th><th>怎么理解</th><th>适用场景</th></tr></thead><tbody>
      <tr><td>前向/反向</td><td>流水线 + 分责任</td><td>训练任何可微网络</td></tr>
      <tr><td>TransE</td><td>关系=平移</td><td>图谱补全、链接预测</td></tr>
      <tr><td>Attention</td><td>软查询</td><td>对齐、长依赖</td></tr></tbody></table></div>`,
  },
  labAlgos: [
    { key: "forward", label: "前向", demo: "forward", desc: "预测下一步哪层点亮 — 对照 MLP 架构图。" },
    { key: "backward", label: "反向", demo: "backward", desc: "δ 如何沿计算图回传 — 不是反向执行网络。" },
    { key: "transe", label: "TransE", demo: "transe", desc: "h+r≈t 正例拉近、负例推远。" },
    { key: "attention", label: "注意力", demo: "attention", desc: "Q 查 K、Softmax 成权重、再加权 V。" },
    { key: "activations", label: "激活", demo: "activations", desc: "ReLU / Sigmoid 曲线与非线性。" },
  ],
};

courseShared.bootstrapChapter(
  {
    chapterNum: 8,
    pageTitle: "连接网络 · 分步理解",
    eyebrow: "《AI思维》第8章 · 连接智能",
    title: "前向反向与嵌入，小例子讲清楚",
    readingMeta: "约 30 分钟 · 5 种演示",
    sections: [{ id: "hero", label: "开篇" }, { id: "m0", label: "概览" }, { id: "m1", label: "MLP" }, { id: "m2", label: "嵌入" }, { id: "m3", label: "注意力" }, { id: "m4", label: "对比" }, { id: "lab", label: "实验室" }],
  },
  ch8Config,
);
