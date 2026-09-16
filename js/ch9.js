"use strict";

/* Chapter 9 · 语言智能 — 对齐第5章 + Transformer 架构图 */

const C = window.courseCopyPrompts?.ch9 || {};

const ch9Config = {
  modules: {
    intro: {
      key: "intro",
      cells: [{
        prompt: "语言模型流水线：分词 → 向量 → 上下文建模 → 生成。固定短句「鲁迅 写 了 狂人 日记」贯穿本章。请先认准 **Transformer 编码器块** 架构图——现代语言模型的核心积木。",
        architectureKey: "transformer",
        architectureStep: { highlight: ["attn", "ffn"] },
        vibeTip: "自注意力在编码器里让每个词「看见」全句；GPT 类语言模型使用仅解码器变体（见语言模型模块）。",
        copyPrompt: C.intro,
      }],
    },
    workflow: {
      key: "workflow",
      cells: [{
        prompt: "**CoT（思维链）提示**让模型给出中间步骤；**SFT（监督微调）**用输入与示范回答训练模型、更新参数。请对比直接作答、分步作答与监督微调的区别。",
        demoKey: "workflow",
        interactive: true,
        vibeTip: "这里的 CoT 提示不更新参数；SFT 是训练过程，可改善任务表现与指令遵循，不只是改变格式。",
        copyPrompt: C.workflow,
      }],
    },
    compare: {
      key: "compare",
      cells: [{
        prompt: "分词、向量表示、上下文建模与生成各解决什么问题？**BPE、Skip-gram、自注意力、语言模型**分别展示这些思想；现代语言模型通常联合训练嵌入层，并不必须先训练 Skip-gram。",
        tableKey: "ch9-compare",
        outputLabel: "对比表",
        copyPrompt: C.compare,
      }],
    },
  },
  notebooks: {
    bpe: {
      key: "bpe",
      mentorKey: "ch9-bpe",
      title: "BPE 子词分词", subtitle: "字节对合并",
      cells: [
        {
          prompt: "BPE 从字符开始，反复合并**最高频相邻对**，在字与词之间找粒度。合并顺序取决于语料统计，不是人工规则。",
          vibeTip: "像拼乐高：常用片段先固定成块。",
          copyPrompt: C.bpeConcept,
        },
        {
          prompt: "请观看步进：按预设合并顺序处理「鲁迅写了狂人日记」，观察词元序列如何变短。训练词表时，每次合并会加入一个新词元，并不是缩小词表。",
          demoKey: "bpe", labTarget: "bpe", interactive: true,
          copyPrompt: C.bpeDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch9-bpe" },
        { mentorCell: "selfCheck", mentorKey: "ch9-bpe" },
        { mentorCell: "when", mentorKey: "ch9-bpe" },
      ],
    },
    w2v: {
      key: "w2v",
      mentorKey: "ch9-w2v",
      title: "Word2Vec Skip-gram", subtitle: "分布式语义",
      cells: [
        {
          prompt: "Skip-gram：用中心词「鲁迅」预测上下文「写」。负采样训练提高正例的点积、降低负例的点积，学习的是**统计共现，不是词典定义**。",
          architectureKey: "skipgram",
          vibeTip: "中心=鲁迅，正例=写，负例=桌子。",
          copyPrompt: C.w2vConcept,
        },
        {
          prompt: "观看步进：观察中心词与正例/负例的推拉。",
          demoKey: "w2v", labTarget: "w2v", interactive: true, outputLabel: "训练动画",
          copyPrompt: C.w2vDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch9-w2v" },
        { mentorCell: "selfCheck", mentorKey: "ch9-w2v" },
        { mentorCell: "when", mentorKey: "ch9-w2v" },
      ],
    },
    selfattn: {
      key: "selfattn",
      mentorKey: "ch9-selfattn",
      title: "自注意力", subtitle: "Q/K/V 来自同一句",
      cells: [
        {
          prompt: "自注意力：句「鲁迅 写 了 狂人 日记」中每个词用 Q 查询全句 K，经 Softmax 得到权重，再加权 V。**需位置编码**才有顺序感。",
          architectureKey: "transformer",
          architectureStep: { highlight: ["attn"] },
          vibeTip: "热力图一行 = 一个词「看向」全句哪些位置。",
          copyPrompt: C.selfattnConcept,
        },
        {
          prompt: "对照 Transformer 块架构图，再看热力图步进。",
          demoKey: "selfattn", labTarget: "selfattn", interactive: true,
          copyPrompt: C.selfattnDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch9-selfattn" },
        { mentorCell: "selfCheck", mentorKey: "ch9-selfattn" },
        { mentorCell: "when", mentorKey: "ch9-selfattn", labTarget: "selfattn" },
      ],
    },
    lm: {
      key: "lm",
      mentorKey: "ch9-lm",
      title: "自回归语言模型", subtitle: "下一词预测",
      cells: [
        {
          prompt: "语言模型：P(w₁…w_n)=Π P(w_i|w_{<i})。前缀「鲁迅」→「写」→「了」… **GPT = 仅解码器块堆叠**（因果掩码自注意力），自回归接龙生成下一词元。",
          architectureKey: "decoder-only",
          vibeTip: "整句概率 = 各步条件概率连乘。自注意力节用的是编码器积木；语言模型节用仅解码器结构。",
          copyPrompt: C.lmConcept,
        },
        {
          prompt: "观看步进：看前缀如何一步步扩展，困惑度如何理解。",
          demoKey: "lm", labTarget: "lm", interactive: true,
          copyPrompt: C.lmDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch9-lm" },
        { mentorCell: "selfCheck", mentorKey: "ch9-lm" },
        { mentorCell: "when", mentorKey: "ch9-lm" },
      ],
    },
  },
  demos: {
    bpe: {
      key: "bpe", stepLabels: ["字符", "合并日记", "合并狂人", "合并鲁迅"],
      trace: [
        { tokens: ["鲁","迅","写","了","狂","人","日","记"], pair: ["日","记"], title: "字符级输入", summary: "句子先被拆成字符词元；本例预设依次合并日+记、狂+人、鲁+迅。", reason: "真实合并顺序来自训练语料的频率统计，不能由这一句话确定。", fields: [{ label: "本步合并", value: "日+记" }] },
        { tokens: ["鲁","迅","写","了","狂","人","日记"], highlight: ["日记"], title: "合并日记", summary: "按预设第一条合并规则，将「日+记」合成一个词元。", reason: "实际训练时会统计语料中的相邻对，再确定合并顺序。", fields: [{ label: "新词元", value: "日记" }] },
        { tokens: ["鲁","迅","写","了","狂人","日记"], highlight: ["狂人","日记"], title: "合并狂人", summary: "继续把「狂+人」合成「狂人」。", reason: "每次合并都会减少序列长度，但仍保留可拆分能力。", fields: [{ label: "长度", value: "7→6" }] },
        { tokens: ["鲁迅","写","了","狂人","日记"], highlight: ["鲁迅","狂人","日记"], title: "形成子词表", summary: "得到「鲁迅 / 写 / 了 / 狂人 / 日记」这些子词词元。", reason: "语言模型后续预测的是词元，不是原始汉字或完整词典词。", fields: [{ label: "输出", value: "子词序列" }] },
      ],
      render(v, s) {
        courseShared.renderTokenStrip(v, s.tokens, s.highlight || []);
        if (s.pair) v.innerHTML += `<p class="output-caption">预设合并对：${s.pair.join("+")}</p>`;
      },
    },
    w2v: {
      key: "w2v",
      architectureKey: "skipgram",
      stepLabels: ["窗口", "正例", "负例", "完成"],
      trace: [
        { title: "取上下文窗口", summary: "中心词是「鲁迅」，窗口里出现上下文词「写」。", reason: "Skip-gram 用中心词预测上下文词。", phase: 0, caption: "中心词预测上下文「写」。", fields: [{ label: "正例对", value: "鲁迅→写" }] },
        { title: "正例拉近", summary: "提高中心词向量 v_鲁迅 与上下文向量 u_写 的点积。", reason: "两者来自不同的参数矩阵；图中距离仅作直觉示意。", phase: 1, caption: "正例点积示意：0.42 → 0.68", fields: [{ label: "正例点积", value: "0.42→0.68" }] },
        { title: "负采样推远", summary: "将采样词「桌子」作为负例，降低 v_鲁迅 与 u_桌子 的点积。", reason: "负例来自采样分布，不保证语义上总是不相关。", phase: 2, caption: "负例点积示意：0.15 → −0.22", fields: [{ label: "负例点积", value: "0.15→−0.22" }] },
        { title: "更新向量空间", summary: "大量上下文窗口共同塑造词向量的统计语义。", reason: "语境相似的词可能有相似表示，但共现不等于语义相同。", phase: 3, caption: "图中位置示意训练方向，不代表实际向量坐标。", fields: [{ label: "学习信号", value: "上下文共现" }] },
      ],
      render(v, s) { window.courseViz.renderWord2Vec(v, s); },
    },
    selfattn: {
      key: "selfattn",
      architectureKey: "transformer",
      stepLabels: ["Q 查询 K", "归一化", "加权 V"],
      trace: [
        {
          title: "Q(写) 查询全句 K",
          summary: "「写」这个位置生成 Q，去看同一句每个词元的 K。",
          reason: "自注意力的 Q/K/V 都来自同一句；这里最高分指向主语「鲁迅」。",
          fields: [{ label: "最高分", value: "鲁迅：1.2" }],
          mode: "self",
          phase: "score",
          queryToken: "写",
          sourceTokens: ["鲁迅", "写", "了", "狂人", "日记"],
          scores: [1.2, 0.7, 0.1, 0.6, 0.3],
          weights: window.courseViz.softmax([1.2, 0.7, 0.1, 0.6, 0.3]),
          focusIndex: 0,
          architectureStep: { highlight: ["attn"] },
        },
        {
          title: "Softmax 归一化",
          summary: "权重显示「写」主要看向「鲁迅」，也保留自身和宾语线索。",
          reason: "这里用预设分数演示 Softmax；真实模型中的分数由训练得到的 Q/K 计算。",
          fields: [{ label: "α(鲁迅)", value: "0.35" }, { label: "权重和", value: "1.00" }],
          mode: "self",
          phase: "softmax",
          queryToken: "写",
          sourceTokens: ["鲁迅", "写", "了", "狂人", "日记"],
          scores: [1.2, 0.7, 0.1, 0.6, 0.3],
          weights: window.courseViz.softmax([1.2, 0.7, 0.1, 0.6, 0.3]),
          focusIndex: 0,
          architectureStep: { highlight: ["attn"] },
        },
        {
          title: "加权 V 得新表示",
          summary: "「写」的新向量混入主语和宾语信息，不再只是孤立词向量。",
          reason: "输出是 ΣαᵢVᵢ，再送入后续 FFN；位置编码负责保留词序。",
          fields: [{ label: "输出", value: "写′" }, { label: "最大权重", value: "鲁迅 0.35" }],
          mode: "self",
          phase: "context",
          queryToken: "写",
          sourceTokens: ["鲁迅", "写", "了", "狂人", "日记"],
          scores: [1.2, 0.7, 0.1, 0.6, 0.3],
          weights: window.courseViz.softmax([1.2, 0.7, 0.1, 0.6, 0.3]),
          focusIndex: 0,
          architectureStep: { highlight: ["attn", "ffn"] },
        },
      ],
      render(v, s) { window.courseViz.renderAttentionFlow(v, s); },
    },
    lm: {
      key: "lm",
      architectureKey: "decoder-only",
      stepLabels: ["预测写", "预测了", "预测狂人", "预测日记", "续写概率"],
      trace: [
        { title: "第一步", summary: "给定前缀「鲁迅」，用示意分布预测下一词元。", prefix: ["鲁迅"], candidates: [{ w: "写", p: 0.64 }, { w: "是", p: 0.12 }, { w: "的", p: 0.08 }, { w: "其他合计", p: 0.16 }] },
        { title: "第二步", summary: "链式扩展：P(了|鲁迅 写)。", prefix: ["鲁迅", "写"], candidates: [{ w: "了", p: 0.58 }, { w: "过", p: 0.21 }, { w: "的", p: 0.09 }, { w: "其他合计", p: 0.12 }] },
        { title: "第三步", summary: "预测下一子词词元「狂人」。", prefix: ["鲁迅", "写", "了"], candidates: [{ w: "狂人", p: 0.41 }, { w: "《", p: 0.18 }, { w: "一", p: 0.11 }, { w: "其他合计", p: 0.30 }] },
        { title: "第四步", summary: "P(日记|鲁迅 写 了 狂人)=0.42。", prefix: ["鲁迅", "写", "了", "狂人"], candidates: [{ w: "日记", p: 0.42 }, { w: "其他合计", p: 0.58 }] },
        { title: "续写概率与困惑度", summary: "给定「鲁迅」，4 个后续词元的条件概率连乘约为 0.06392，PPL≈1.99。", reason: "只评估这 4 个词元，不含前缀或结束符；不是整句的无条件概率。", prefix: ["鲁迅", "写", "了", "狂人", "日记"], probabilityLabel: "P(续写|鲁迅)", product: "0.64×0.58×0.41×0.42≈0.06392", ppl: (Math.pow(0.64 * 0.58 * 0.41 * 0.42, -1 / 4)).toFixed(2), candidates: [] },
      ],
      render(v, s) { window.courseViz.renderLMChain(v, s); },
    },
    workflow: {
      key: "workflow",
      stepLabels: ["直接答", "CoT", "SFT"],
      trace: [
        { title: "直接答", summary: "模型只输出最终答案，无法检查中间是否数错。", reason: "适合简单题；复杂题缺少可诊断过程。", phase: 0, fields: [{ label: "可检查性", value: "低" }] },
        { title: "CoT 提示", summary: "要求先列中间步骤，再给结论，便于检查计算。", reason: "提示改变本次作答方式，不更新参数；生成的步骤仍需核对。", phase: 1, fields: [{ label: "参数更新", value: "无" }] },
        { title: "SFT 监督微调", summary: "用输入与示范回答组成训练集，通过损失和反向传播更新模型参数。", reason: "模型学习任务行为与指令遵循；只看到一种回答格式，不能判断模型是否经过 SFT。", phase: 2, fields: [{ label: "参数更新", value: "有（训练时）" }] },
      ],
      render(v, s) { window.courseViz.renderWorkflow(v, s); },
    },
  },
  tables: {
    "ch9-compare": `<div class="table-wrap compact"><table class="run-table compact comparison-table"><thead><tr><th>阶段</th><th>算法</th><th>架构/产出</th></tr></thead><tbody>
      <tr><td>分词</td><td>BPE</td><td>子词词表</td></tr><tr><td>向量</td><td>Skip-gram</td><td>词向量</td></tr>
      <tr><td>上下文</td><td>自注意力</td><td>Transformer 块</td></tr><tr><td>生成</td><td>语言模型</td><td>下一词分布</td></tr></tbody></table></div>`,
  },
  labAlgos: [
    { key: "bpe", label: "BPE", demo: "bpe", desc: "预设合并：日+记→日记，狂+人→狂人，鲁+迅→鲁迅。" },
    { key: "w2v", label: "Word2Vec", demo: "w2v", desc: "向量空间中拉近共现词、推远负样本。" },
    { key: "selfattn", label: "自注意力", demo: "selfattn", desc: "同一句内 Q 查 K，再加权 V 得新表示。" },
    { key: "lm", label: "语言模型", demo: "lm", desc: "自回归接龙与条件概率。" },
    { key: "workflow", label: "CoT/SFT", demo: "workflow", desc: "错题计数：直接作答、CoT 提示与 SFT 参数训练。" },
  ],
};

courseShared.bootstrapChapter(
  {
    chapterNum: 9,
    pageTitle: "语言模型 · 分步理解",
    eyebrow: "《AI思维》第9章 · 语言智能",
    title: "语言模型 · 分词到序列生成",
    readingMeta: "约 30 分钟 · 5 种算法", sections: [{ id: "hero", label: "开篇" }, { id: "m0", label: "概览" }, { id: "m1", label: "分词向量" }, { id: "m2", label: "注意力" }, { id: "m3", label: "生成" }, { id: "m4", label: "对比" }, { id: "lab", label: "实验室" }],
  },
  ch9Config,
);
