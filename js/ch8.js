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
      prompt: "前向/反向、TransE、注意力各解决什么问题？请对照下表，各用本页小例子一句话说明适用场景。",
      tableKey: "ch8-compare",
      copyPrompt: C.compare,
    }] },
  },
  notebooks: {
    forward: {
      key: "forward",
      mentorKey: "ch8-forward",
      title: "多层感知机前向传播",
      subtitle: "流水线从左到右 — 先会「算」，再学「改」",
      cells: [
        {
          prompt: "**为什么先学前向？** 因为反向传播需要一张「送货单」——前向时保存每层激活 a，反向才知道每站收了多少货。",
          architectureKey: "mlp",
          vibeTip: "把每层想成工厂一站：输入产品 → 加工 → 输出给下一站。",
          copyPrompt: C.forwardConcept,
        },
        {
          prompt: "请观看步进演示。输入 x=[6.2, 0.8]（血糖、运动），经给定参数计算到 ŷ=0.82。数值仅用于演示，不是经过验证的健康风险估计。",
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
          prompt: "**反向传播计算梯度**：从损失出发，用链式法则求各层参数的偏导数，梯度不一定在输出层最大。ReLU 在 z<0 时导数为 0，在 z=0 处通常约定取 0。",
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
          prompt: "观看一次联合更新前后的示意：正例距离缩小，负例（红楼梦）距离增大；随后检查间隔损失。图上坐标只是投影示意。",
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
      title: "编码器-解码器注意力",
      subtitle: "生成时「该看输入序列哪些位置」",
      cells: [
        {
          prompt: "RNN 把源句压成一个向量，长句会丢信息。**注意力机制让解码每一步都能软查询编码器里的全部位置**——这是 Transformer 的核心思想之一。",
          architectureKey: "encoder-decoder",
          architectureStep: { highlight: ["enc", "dec", "attn"] },
          vibeTip: "图书馆：Q=你的问题，K=索引卡，V=书页内容。",
          copyPrompt: C.attentionConcept,
        },
        {
          prompt: "先看架构图里的注意力桥，再按给定分数计算权重。本例解码「日记」时，「写」权重最大；这是示意数值，不是语法规则。",
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
        { title: "隐藏层 ReLU", summary: "h=ReLU(W₁x+b₁)。", reason: "W₁=[[0.1,0.1],[0.05,0.2]]，b₁=[0.01,−0.02]，两维均为正。", fields: [{ label: "h", value: "[0.71, 0.45]" }], activeLayer: 1, architectureStep: { highlight: ["hid"] } },
        { title: "输出 Sigmoid", summary: "得到正类概率的教学示例值。", reason: "W₂=[0.5,0.3]，b₂=ln(0.82/0.18)−0.5×0.71−0.3×0.45，故 σ(W₂h+b₂)=0.82。", fields: [{ label: "ŷ", value: "0.82" }], activeLayer: 2, architectureStep: { highlight: ["out"] } },
      ],
      render(v, s) { viz.renderMLP(v, s); },
    },
    backward: {
      key: "backward",
      architectureKey: "mlp",
      stepLabels: ["δ_out", "δ_h", "∂W"],
      trace: [
        { title: "输出层 δ", summary: "设标签 y=1，使用二元交叉熵损失，δ_out=ŷ−y。", fields: [{ label: "δ_out", value: "−0.18" }], phase: 0, architectureStep: { highlight: ["out"] } },
        { title: "隐藏层 δ", summary: "δ_h=W₂ᵀδ_out，与 ReLU 导数逐元素相乘。", fields: [{ label: "δ_h", value: "[−0.09, −0.054]" }], phase: 1, architectureStep: { highlight: ["hid"] } },
        { title: "更新 W", summary: "W ← W − η∇W，η=0.01；权重梯度还需乘前一层激活。", fields: [{ label: "ΔW_h", value: "−ηδ_h xᵀ（2×2 矩阵）" }, { label: "ΔW_out", value: "[0.001278, 0.000810]" }, { label: "Δb_out", value: "0.0018" }], phase: 2, architectureStep: { highlight: ["hid"] } },
      ],
      render(v, s) { viz.renderMLPBackward(v, s); },
    },
    transe: {
      key: "transe",
      architectureKey: "transe",
      stepLabels: ["嵌入", "正例", "负例", "损失"],
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
          title: "检查间隔损失",
          summary: "此时负例比正例远超过 margin，无需继续拉近这一正例。",
          reason: "L=max(0,1+0.31−2.08)=0。忽略正则化等其他损失时，这一对样本的间隔损失不再推动更新。",
          fields: [{ label: "margin", value: "1.0" }, { label: "d⁺ / d⁻", value: "0.31 / 2.08" }],
          dist: 0.31,
          kind: "update",
        },
      ],
      render(v, s) { viz.renderTransE(v, s); },
    },
    attention: {
      key: "attention",
      architectureKey: "encoder-decoder",
      stepLabels: ["Q 查询 K", "归一化", "加权 V"],
      trace: [
        {
          title: "Q 查询编码器的 K",
          summary: "解码器当前要生成「日记」，先拿 Q 去问源句每个位置。",
          reason: "Q 来自解码器当前状态；K/V 来自编码器对「鲁迅 写 日记」的编码。",
          fields: [{ label: "最高分", value: "写：2.1" }],
          mode: "cross",
          phase: "score",
          queryToken: "日记",
          sourceTokens: ["鲁迅", "写", "日记"],
          scores: [0.4, 2.1, 0.3],
          weights: viz.softmax([0.4, 2.1, 0.3]),
          focusIndex: 1,
          architectureStep: { highlight: ["attn"] },
        },
        {
          title: "Softmax 归一化",
          summary: "按给定分数计算 Softmax，「写」的权重约为 0.74。",
          reason: "Softmax 后所有权重相加为 1，注意力不是硬选择一个词，而是软分配。",
          fields: [{ label: "权重和", value: "1.00" }, { label: "α(写)", value: "0.74" }],
          mode: "cross",
          phase: "softmax",
          queryToken: "日记",
          sourceTokens: ["鲁迅", "写", "日记"],
          scores: [0.4, 2.1, 0.3],
          weights: viz.softmax([0.4, 2.1, 0.3]),
          focusIndex: 1,
          architectureStep: { highlight: ["attn"] },
        },
        {
          title: "加权 V 得上下文",
          summary: "按 α 加权各位置 V，得到当前解码器需要的上下文向量。",
          reason: "「写」的加权系数最大；实际贡献还取决于 V 的数值，不能把注意力权重直接当作下一词概率。",
          fields: [{ label: "上下文", value: "ΣαᵢVᵢ" }, { label: "最大权重", value: "写 0.74" }],
          mode: "cross",
          phase: "context",
          queryToken: "日记",
          sourceTokens: ["鲁迅", "写", "日记"],
          scores: [0.4, 2.1, 0.3],
          weights: viz.softmax([0.4, 2.1, 0.3]),
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
      <tr><td>注意力</td><td>软查询</td><td>对齐、长依赖</td></tr></tbody></table></div>`,
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
    title: "连接网络 · 前向传播与表示学习",
    readingMeta: "约 30 分钟 · 5 种演示",
    sections: [{ id: "hero", label: "开篇" }, { id: "m0", label: "概览" }, { id: "m1", label: "MLP" }, { id: "m2", label: "嵌入" }, { id: "m3", label: "注意力" }, { id: "m4", label: "对比" }, { id: "lab", label: "实验室" }],
  },
  ch8Config,
);
