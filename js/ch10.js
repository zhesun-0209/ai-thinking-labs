"use strict";

/* Chapter 10 · 感知智能 — 对齐第5章 + CNN/ViT/MAE/CLIP 架构图 */

const C = window.courseCopyPrompts?.ch10 || {};

const ch10Config = {
  modules: {
    intro: {
      key: "intro",
      cells: [{
        prompt: "感知智能从像素到语义。本章用 4×4 灰度小图演示卷积→池化流水线，四条主线对应四种架构——请先浏览下方 **CNN 流水线图**，建立整体印象。",
        architectureKey: "cnn",
        vibeTip: "CNN 的归纳偏置：局部连接 + 权值共享。",
        copyPrompt: C.intro,
      }],
    },
    compare: {
      key: "compare",
      cells: [{
        prompt: "四种感知架构一览：**CNN** 局部卷积、**ViT** 全局注意力、**MAE** 遮罩重构、**CLIP** 图文对比。请对照下表理解结构关键词与训练信号的差异。",
        tableKey: "ch10-compare",
        outputLabel: "对比表",
        copyPrompt: C.compare,
      }],
    },
  },
  notebooks: {
    cnn: {
      key: "cnn",
      mentorKey: "ch10-cnn",
      title: "视觉模型 · 卷积到 Transformer", subtitle: "局部特征提取",
      cells: [
        {
          prompt: "CNN 的归纳偏置：**局部连接 + 权值共享**。同一卷积核扫全图，提取可复用的局部模式。",
          architectureKey: "cnn",
          architectureStep: { highlight: "conv" },
          vibeTip: "用小模板在图上滑动扫描。",
          copyPrompt: C.cnnConcept,
        },
        {
          prompt: "3×3 卷积核在 4×4 输入上滑动 → 2×2 特征图 → max-pool → 1×1。注意 **卷积核高亮框** 如何移动。",
          demoKey: "cnn", labTarget: "cnn", interactive: true,
          copyPrompt: C.cnnDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch10-cnn" },
        { mentorCell: "selfCheck", mentorKey: "ch10-cnn" },
        { mentorCell: "when", mentorKey: "ch10-cnn", labTarget: "cnn" },
      ],
    },
    patch: {
      key: "patch",
      mentorKey: "ch10-vit",
      title: "ViT · Patch 词元化", subtitle: "图像当句子",
      cells: [
        {
          prompt: "ViT 把 4×4 图切成 2×2 的 4 个 patch，加位置编码后送入 **Transformer Encoder**（与第9章同构）。",
          architectureKey: "vit",
          architectureStep: { highlight: ["patch", "enc"] },
          vibeTip: "Patch = 图像版的 token。",
          copyPrompt: C.vitConcept,
        },
        { prompt: "步进：patch 切分 → 展平 → +位置编码 → 送入 Encoder。", demoKey: "patch", labTarget: "patch", interactive: true, outputLabel: "Patch 动画", copyPrompt: C.vitDemo },
        { mentorCell: "misconception", mentorKey: "ch10-vit" },
        { mentorCell: "selfCheck", mentorKey: "ch10-vit" },
        { mentorCell: "when", mentorKey: "ch10-vit" },
      ],
    },
    mae: {
      key: "mae",
      mentorKey: "ch10-mae",
      title: "MAE 掩码自编码", subtitle: "遮 75% 再重构",
      cells: [
        {
          prompt: "MAE 随机遮 75% patch，**Encoder 只看 25%**，Decoder 重构全部像素——自监督预训练。",
          architectureKey: "mae",
          architectureStep: { phase: 1 },
          vibeTip: "完形填空：只看 25% 逼模型学语义。",
          copyPrompt: C.maeConcept,
        },
        { prompt: "观看步进：遮罩 → Encoder → Decoder 重构。", demoKey: "mae", labTarget: "mae", interactive: true, copyPrompt: C.maeDemo },
        { mentorCell: "misconception", mentorKey: "ch10-mae" },
        { mentorCell: "selfCheck", mentorKey: "ch10-mae" },
        { mentorCell: "when", mentorKey: "ch10-mae" },
      ],
    },
    clip: {
      key: "clip",
      mentorKey: "ch10-clip",
      title: "CLIP 对比学习", subtitle: "图文双塔",
      cells: [
        {
          prompt: "CLIP 用 **两个 Encoder** 分别编码图像和文本，对比损失拉近匹配对、推远非匹配。",
          architectureKey: "clip",
          vibeTip: "一批样本内 N 对正样本，N²−N 个负样本。",
          copyPrompt: C.clipConcept,
        },
        { prompt: "步进：双塔编码 → 正例拉近 → 负例推远 → InfoNCE 损失。", demoKey: "clip", labTarget: "clip", interactive: true, copyPrompt: C.clipDemo },
        { mentorCell: "misconception", mentorKey: "ch10-clip" },
        { mentorCell: "selfCheck", mentorKey: "ch10-clip" },
        { mentorCell: "when", mentorKey: "ch10-clip" },
      ],
    },
  },
  demos: {
    cnn: {
      key: "cnn",
      architectureKey: "cnn",
      stepLabels: ["输入", "卷积①", "卷积②", "卷积③", "卷积④", "池化"],
      trace: [
        { phase: "in", kPos: null, title: "4×4 输入", summary: "每个格子是一块局部像素强度。", reason: "卷积不先看整图，而是从小窗口开始找局部模式。", architectureStep: { highlight: "in" } },
        { phase: "conv", kPos: [0, 0], title: "卷积核扫 (0,0)", summary: "3×3 窗口覆盖左上角，计算第 1 个特征值。", reason: "权值共享：同一卷积核将在 4 个位置各算一次。", fields: [{ label: "进度", value: "1/4" }], architectureStep: { highlight: "conv" } },
        { phase: "conv", kPos: [0, 1], title: "卷积核扫 (0,1)", summary: "窗口右移一列，填充特征图第 2 格。", reason: "从左到右扫描完第一行。", fields: [{ label: "进度", value: "2/4" }], architectureStep: { highlight: "conv" } },
        { phase: "conv", kPos: [1, 0], title: "卷积核扫 (1,0)", summary: "换到第二行左侧，第 3 格写入特征图。", reason: "自上而下、从左到右 — 与教材图示一致。", fields: [{ label: "进度", value: "3/4" }], architectureStep: { highlight: "conv" } },
        { phase: "conv", kPos: [1, 1], title: "卷积核扫 (1,1)", summary: "最后一个窗口 → 2×2 特征图填满。", reason: "4 个窗口各产生 1 个数，步幅为 1。", fields: [{ label: "输出", value: "2×2" }], architectureStep: { highlight: "feat" } },
        { phase: "pool", kPos: null, title: "Max Pool", summary: "取 2×2 特征图中的最大响应，压成 1×1。", reason: "池化保留最强证据，同时降低位置敏感性。", fields: [{ label: "保留", value: "max" }], architectureStep: { highlight: "pool" } },
      ],
      render(v, s) {
        courseShared.renderCanvasDemo(v, { ...s, canvasAspect: 340 / 560 }, (ctx, w, h) =>
          window.courseViz.drawConvGrid(ctx, w, h, 4, 3, s.kPos, s.phase),
        );
      },
    },
    patch: {
      key: "patch",
      architectureKey: "vit",
      stepLabels: ["原图", "Patch", "投影", "位置", "Encoder", "Head"],
      trace: [
        { vitPhase: 0, title: "原图", summary: "4×4 灰度图，尚未切分。", reason: "ViT 第一步与 CNN 不同：先切成 patch 而非卷积核扫描。", architectureStep: { highlight: ["img"] } },
        { vitPhase: 1, patches: 4, title: "Patchify", summary: "切成 4 个 2×2 patch，每个 patch 是一个视觉 token。", reason: "类比 NLP：patch ≈ 单词。", architectureStep: { highlight: ["patch"] } },
        { vitPhase: 2, patches: 4, flat: true, title: "Linear 投影", summary: "每个 patch 展平后经线性层映射到 d 维 embedding。", reason: "把像素块变成 Transformer 能处理的向量序列。", fields: [{ label: "token", value: "P1…P4" }], architectureStep: { highlight: ["patch"] } },
        { vitPhase: 3, patches: 4, pos: true, title: "+位置编码", summary: "加上可学习的位置编码，保留空间顺序信息。", reason: "Self-Attention 本身不感知上下左右。", fields: [{ label: "输入", value: "emb + pos" }], architectureStep: { highlight: ["patch", "pos"] } },
        { vitPhase: 4, patches: 4, pos: true, enc: true, title: "Transformer Encoder", summary: "L 层 Self-Attention + FFN，全局混合 patch 信息。", reason: "每个 patch 可直接 attend 全图任意 patch。", architectureStep: { highlight: ["patch", "enc"] } },
        { vitPhase: 5, patches: 4, pos: true, enc: true, head: true, title: "分类 Head", summary: "池化 token 表示 → MLP → 类别概率。", reason: "预训练后可接下游分类头微调。", fields: [{ label: "预测", value: "猫 0.87" }], architectureStep: { highlight: ["head"] } },
      ],
      render(v, s) { window.courseViz.renderViTPatches(v, s); },
    },
    mae: {
      key: "mae",
      architectureKey: "mae",
      stepLabels: ["切分", "遮罩", "Encoder", "Decoder"],
      trace: [
        { maePhase: 1, mask: 0, title: "切 patch", summary: "原图切成 4 个 patch token。", reason: "与 ViT 相同的前处理。", architectureStep: { phase: 0 } },
        { maePhase: 2, mask: 3, title: "随机遮 75%", summary: "移除 P2–P4，仅保留 P1 送入 Encoder。", reason: "He et al. MAE：高比例遮罩逼模型学语义。", fields: [{ label: "可见", value: "25%" }], architectureStep: { phase: 1 } },
        { maePhase: 3, mask: 3, encode: true, title: "Encoder", summary: "ViT Encoder 只处理可见 patch，计算高效。", reason: "不见被遮 patch，节省算力。", fields: [{ label: "输入", value: "P1" }], architectureStep: { phase: 2 } },
        { maePhase: 4, mask: 0, recon: true, title: "Decoder 重构", summary: "轻量 Decoder 用掩码 token + Encoder 输出，还原全部像素。", reason: "损失仅在被遮区域计算 MSE。", fields: [{ label: "监督", value: "像素 MSE" }], architectureStep: { phase: 3 } },
      ],
      render(v, s) { window.courseViz.renderMAEFlow(v, s); },
    },
    clip: {
      key: "clip",
      architectureKey: "clip",
      stepLabels: ["双塔", "正例", "负例", "损失"],
      trace: [
        { clipPhase: 0, sim: null, title: "双塔编码", summary: "图像和文本分别进不同 Encoder，得到 v_I、v_T。", reason: "CLIP 先把两种模态投到同一个向量空间。", fields: [{ label: "图像", value: "v_I" }, { label: "文本", value: "v_T" }], architectureStep: { phase: "both" } },
        { clipPhase: 1, sim: 0.91, pos: true, title: "正例拉近", summary: "同一语义的图文向量夹角变小，cos=0.91。", reason: "匹配图文应该在共享空间里靠近。", fields: [{ label: "正例", value: "猫图 ↔ 猫文本" }, { label: "目标", value: "cos ↑" }] },
        { clipPhase: 2, sim: 0.08, pos: false, title: "负例推远", summary: "猫图配车辆文本是负例，cos=0.08。", reason: "同一批样本里的其它文本都是干扰项，模型要把它们推远。", fields: [{ label: "负例", value: "猫图 ↔ 车文本" }, { label: "目标", value: "cos ↓" }] },
        { clipPhase: 3, title: "InfoNCE", summary: "正例分数进分子，同一批样本内所有负例进分母。", reason: "损失降低时，正例相似度上升，负例下降。", fields: [{ label: "损失", value: "InfoNCE" }], sim: 0.91, pos: true, loss: true },
      ],
      render(v, s) { window.courseViz.renderCLIPPair(v, s); },
    },
  },
  tables: {
    "ch10-compare": `<div class="table-wrap compact"><table class="run-table compact comparison-table"><thead><tr><th>架构</th><th>架构图关键词</th><th>训练信号</th></tr></thead><tbody>
      <tr><td>CNN</td><td>Conv→Pool→FC</td><td>标签</td></tr><tr><td>ViT</td><td>Patch→Transformer</td><td>标签</td></tr>
      <tr><td>MAE</td><td>Mask→Enc→Dec</td><td>重构</td></tr><tr><td>CLIP</td><td>双塔+对比</td><td>图文对</td></tr></tbody></table></div>`,
  },
  labAlgos: [
    { key: "cnn", label: "CNN", demo: "cnn", desc: "对照 CNN 架构图看卷积核滑动。" },
    { key: "patch", label: "ViT", demo: "patch", desc: "Patch 词元化 → 位置编码 → Encoder。" },
    { key: "mae", label: "MAE", demo: "mae", desc: "对照 MAE 架构图看 75% 遮罩与重构。" },
    { key: "clip", label: "CLIP", demo: "clip", desc: "双塔架构 + 匹配/非匹配 cosine。" },
  ],
};

courseShared.bootstrapChapter(
  {
    chapterNum: 10,
    pageTitle: "视觉模型 · 分步理解", eyebrow: "《AI思维》第10章 · 感知智能", title: "视觉模型 · 卷积到 Transformer", readingMeta: "约 30 分钟 · 4 种架构", sections: [{ id: "hero", label: "开篇" }, { id: "m0", label: "概览" }, { id: "m1", label: "CNN" }, { id: "m2", label: "ViT" }, { id: "m3", label: "自监督" }, { id: "m4", label: "对比" }, { id: "lab", label: "实验室" }],
  },
  ch10Config,
);
