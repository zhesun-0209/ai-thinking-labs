"use strict";

/* Chapter 9 · 语言智能 — 对齐第5章 + Transformer 架构图 */

const C = window.courseCopyPrompts?.ch9 || {};

const ch9Config = {
  modules: {
    intro: {
      key: "intro",
      cells: [{
        prompt: "语言模型 pipeline：分词 → 向量 → 上下文建模 → 生成。固定短句「鲁迅 写 了 狂人 日记」贯穿本章。请先认准 **Transformer Encoder Block** 架构图——现代 LM 的核心积木。",
        architectureKey: "transformer",
        architectureStep: { highlight: ["attn", "ffn"] },
        vibeTip: "Self-Attention 在 Encoder 里让每个词「看见」全句；GPT 类 LM 用 Decoder-only 变体（见 LM 模块）。",
        copyPrompt: C.intro,
      }],
    },
    workflow: {
      key: "workflow",
      cells: [{
        prompt: "CoT 先写推理链再作答；SFT 对齐 instruction 输出格式。请步进对比三种回答方式。",
        demoKey: "workflow",
        interactive: true,
        vibeTip: "CoT/SFT 不改变模型结构，改变的是「输出格式与推理习惯」。",
        copyPrompt: C.workflow,
      }],
    },
    compare: {
      key: "compare",
      cells: [{
        prompt: "NLP 流水线四阶段：**BPE** 子词切分 → **Skip-gram** 词向量 → **Self-Attention** 上下文建模 → **语言模型** 自回归生成。请对照下表理解各阶段产出。",
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
      title: "语言模型 · 分词到序列生成", subtitle: "字节对合并",
      cells: [
        {
          prompt: "BPE 从字符开始，反复合并**最高频相邻对**，在字与词之间找粒度。合并顺序取决于语料统计，不是人工规则。",
          vibeTip: "像拼乐高：常用片段先固定成块。",
          copyPrompt: C.bpeConcept,
        },
        {
          prompt: "请观看步进：句子「鲁迅 写 了 狂人 日记」上注意哪两个符号被合并、词表如何变短。",
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
          prompt: "Skip-gram：用中心词「鲁迅」预测上下文「写」。共现多的词向量靠近——**统计共现，不是词典定义**。",
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
          prompt: "Self-Attention：句「鲁迅 写 了 狂人 日记」中每个词用 Q 查询全句 K，Softmax 得权重，加权 V。**需位置编码**才有顺序感。",
          architectureKey: "transformer",
          architectureStep: { highlight: ["attn"] },
          vibeTip: "热力图一行 = 一个词「看向」全句哪些位置。",
          copyPrompt: C.selfattnConcept,
        },
        {
          prompt: "对照 Transformer Block 架构图，再看热力图步进。",
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
          prompt: "语言模型：P(w₁…w_n)=Π P(w_i|w_{<i})。前缀「鲁迅」→「写」→「了」… **GPT = 仅 Decoder Block 堆叠**（因果掩码自注意力），自回归接龙生成下一 token。",
          architectureKey: "decoder-only",
          vibeTip: "整句概率 = 各步条件概率连乘。Self-Attn 节用的是 Encoder 积木；LM 节用 Decoder-only。",
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
        { tokens: ["鲁","迅","写","了","狂","人","日","记"], pair: ["日","记"], count: 12, title: "字符级输入", summary: "句子先被拆成最小字符 token。", reason: "BPE 从细粒度开始，反复统计相邻 token 对的出现频率。", fields: [{ label: "高频对", value: "日+记" }] },
        { tokens: ["鲁","迅","写","了","狂","人","日记"], highlight: ["日记"], title: "合并日记", summary: "把最高频相邻对「日+记」合成一个 token。", reason: "常一起出现的片段应作为更稳定的子词单位。", fields: [{ label: "新 token", value: "日记" }] },
        { tokens: ["鲁","迅","写","了","狂人","日记"], highlight: ["狂人","日记"], title: "合并狂人", summary: "继续把「狂+人」合成「狂人」。", reason: "每次合并都会减少序列长度，但仍保留可拆分能力。", fields: [{ label: "长度", value: "7→6" }] },
        { tokens: ["鲁迅","写","了","狂人","日记"], highlight: ["鲁迅","狂人","日记"], title: "形成子词表", summary: "得到「鲁迅 / 写 / 了 / 狂人 / 日记」这些子词 token。", reason: "语言模型后续预测的是 token，不是原始汉字或完整词典词。", fields: [{ label: "输出", value: "子词序列" }] },
      ],
      render(v, s) {
        courseShared.renderTokenStrip(v, s.tokens, s.highlight || []);
        if (s.pair) v.innerHTML += `<p class="output-caption">最高频对：${s.pair.join("+")}（${s.count} 次）</p>`;
      },
    },
    w2v: {
      key: "w2v",
      architectureKey: "skipgram",
      stepLabels: ["窗口", "正例", "负例", "完成"],
      trace: [
        { title: "取上下文窗口", summary: "中心词是「鲁迅」，窗口里出现上下文词「写」。", reason: "Skip-gram 用中心词预测上下文词。", phase: 0, caption: "中心词预测上下文「写」。", fields: [{ label: "正例对", value: "鲁迅→写" }] },
        { title: "正例拉近", summary: "提高 v_鲁迅 与 v_写 的点积相似度。", reason: "真实共现的词应在向量空间中更接近。", phase: 1, caption: "相似度 0.42 → 0.68", fields: [{ label: "相似度", value: "0.42→0.68" }] },
        { title: "负采样推远", summary: "随机采到不相关词「桌子」，把它从「鲁迅」附近推开。", reason: "负样本让模型不只会拉近，还会学会区分。", phase: 2, caption: "相似度 0.15 → −0.22", fields: [{ label: "相似度", value: "0.15→−0.22" }] },
        { title: "更新向量空间", summary: "共现词靠近，不相关词远离，语义结构逐步形成。", reason: "大量窗口重复训练后，词向量会编码统计语义。", phase: 3, caption: "共现词在空间中靠近。", fields: [{ label: "效果", value: "共现词靠近" }] },
      ],
      render(v, s) { window.courseViz.renderWord2Vec(v, s); },
    },
    selfattn: {
      key: "selfattn",
      architectureKey: "transformer",
      stepLabels: ["Q 查询 K", "Softmax", "加权 V"],
      trace: [
        {
          title: "Q(写) 查询全句 K",
          summary: "「写」这个位置生成 Q，去看同一句每个 token 的 K。",
          reason: "Self-Attention 的 Q/K/V 都来自同一句；这里最高分指向主语「鲁迅」。",
          fields: [{ label: "最高分", value: "鲁迅：1.2" }],
          mode: "self",
          phase: "score",
          queryToken: "写",
          sourceTokens: ["鲁迅", "写", "了", "狂人", "日记"],
          scores: [1.2, 0.7, 0.1, 0.6, 0.3],
          weights: [0.35, 0.22, 0.08, 0.2, 0.15],
          focusIndex: 0,
          architectureStep: { highlight: ["attn"] },
        },
        {
          title: "Softmax 变权重",
          summary: "权重显示「写」主要看向「鲁迅」，也保留自身和宾语线索。",
          reason: "这些权重不是人工规则，是 QK 分数归一化后的软分配。",
          fields: [{ label: "α(鲁迅)", value: "0.35" }, { label: "权重和", value: "1.00" }],
          mode: "self",
          phase: "softmax",
          queryToken: "写",
          sourceTokens: ["鲁迅", "写", "了", "狂人", "日记"],
          scores: [1.2, 0.7, 0.1, 0.6, 0.3],
          weights: [0.35, 0.22, 0.08, 0.2, 0.15],
          focusIndex: 0,
          architectureStep: { highlight: ["attn"] },
        },
        {
          title: "加权 V 得新表示",
          summary: "「写」的新向量混入主语和宾语信息，不再只是孤立词向量。",
          reason: "输出是 ΣαᵢVᵢ，再送入后续 FFN；位置编码负责保留词序。",
          fields: [{ label: "输出", value: "写′" }, { label: "最大贡献", value: "鲁迅 0.35" }],
          mode: "self",
          phase: "context",
          queryToken: "写",
          sourceTokens: ["鲁迅", "写", "了", "狂人", "日记"],
          scores: [1.2, 0.7, 0.1, 0.6, 0.3],
          weights: [0.35, 0.22, 0.08, 0.2, 0.15],
          focusIndex: 0,
          architectureStep: { highlight: ["attn", "ffn"] },
        },
      ],
      render(v, s) { window.courseViz.renderAttentionFlow(v, s); },
    },
    lm: {
      key: "lm",
      architectureKey: "decoder-only",
      stepLabels: ["P(写｜鲁迅)", "P(了｜鲁迅 写)", "P(狂人｜鲁迅 写 了)", "句概率"],
      trace: [
        { title: "第一步", summary: "首词预测：「鲁迅」后最可能是「写」。", prefix: ["鲁迅"], candidates: [{ w: "写", p: 0.64 }, { w: "是", p: 0.12 }, { w: "的", p: 0.08 }] },
        { title: "第二步", summary: "链式扩展：P(了|鲁迅 写)。", prefix: ["鲁迅", "写"], candidates: [{ w: "了", p: 0.58 }, { w: "过", p: 0.21 }, { w: "的", p: 0.09 }] },
        { title: "第三步", summary: "子词预测：BPE 切分后的下一 token。", prefix: ["鲁迅", "写", "了"], candidates: [{ w: "狂人", p: 0.41 }, { w: "《", p: 0.18 }, { w: "一", p: 0.11 }] },
        { title: "整句", summary: "概率连乘 → 困惑度。", prefix: ["鲁迅", "写", "了", "狂人", "日记"], product: "0.64×0.58×0.41×…≈0.064", ppl: "8.2", candidates: [{ w: "（完成）", p: 1.0 }] },
      ],
      render(v, s) { window.courseViz.renderLMChain(v, s); },
    },
    workflow: {
      key: "workflow",
      stepLabels: ["直接答", "CoT", "SFT"],
      trace: [
        { title: "直接答", summary: "模型只输出最终答案，无法检查中间是否数错。", reason: "适合简单题；复杂题缺少可诊断过程。", phase: 0, fields: [{ label: "可检查性", value: "低" }] },
        { title: "CoT", summary: "先列中间步骤，再给结论，错误位置更容易被发现。", reason: "推理链把隐式计算外显出来。", phase: 1, fields: [{ label: "可检查性", value: "高" }] },
        { title: "SFT", summary: "用固定 instruction/response 格式训练模型按要求作答。", reason: "SFT 不是让模型自动变聪明，而是让输出更符合任务格式。", phase: 2, fields: [{ label: "目标", value: "格式对齐" }] },
      ],
      render(v, s) { window.courseViz.renderWorkflow(v, s); },
    },
  },
  tables: {
    "ch9-compare": `<div class="table-wrap compact"><table class="run-table compact comparison-table"><thead><tr><th>阶段</th><th>算法</th><th>架构/产出</th></tr></thead><tbody>
      <tr><td>分词</td><td>BPE</td><td>子词词表</td></tr><tr><td>向量</td><td>Skip-gram</td><td>词向量</td></tr>
      <tr><td>上下文</td><td>Self-Attention</td><td>Transformer Block</td></tr><tr><td>生成</td><td>LM</td><td>下一词分布</td></tr></tbody></table></div>`,
  },
  labAlgos: [
    { key: "bpe", label: "BPE", demo: "bpe", desc: "子词合并：人+记→日记→狂人→鲁迅。" },
    { key: "w2v", label: "Word2Vec", demo: "w2v", desc: "向量空间中拉近共现词、推远负样本。" },
    { key: "selfattn", label: "自注意力", demo: "selfattn", desc: "同一句内 Q 查 K，再加权 V 得新表示。" },
    { key: "lm", label: "语言模型", demo: "lm", desc: "自回归接龙与条件概率。" },
    { key: "workflow", label: "CoT/SFT", demo: "workflow", desc: "同一错题计数题：直接答 vs 推理链 vs 模板格式。" },
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
