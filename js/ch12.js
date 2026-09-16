"use strict";

/* Chapter 12 · 创造智能 — 对齐第5章 + Diffusion/GAN/MCTS 架构图 */

const C = window.courseCopyPrompts?.ch12 || {};

const ch12Config = {
  modules: {
    intro: {
      key: "intro",
      cells: [{
        prompt: "创造智能在巨大搜索空间找新解。第5章已有 <a href=\"ch5.html#hero\">MiniMax</a>；本章重点：**扩散模型架构**、GAN 对抗、MCTS 树搜索。\n\n请先认准下方 **扩散模型流水线图**（x₀→加噪→U-Net 去噪→x̂₀）。",
        architectureKey: "diffusion",
        vibeTip: "扩散 = 学一个「去噪器」U-Net，而不是直接学生成器 G(z)。",
        copyPrompt: C.intro,
      }],
    },
    alphafold: {
      key: "alphafold",
      cells: [{
        prompt: "**AlphaFold 2**：序列 + 多序列比对（MSA）→ Evoformer → 结构模块 → 3D 结构与 pLDDT 局部置信度。步进查看这一代模型的数据流。",
        demoKey: "alphafold",
        interactive: true,
        vibeTip: "结构预测不同于模拟完整折叠过程；这里介绍 AlphaFold 2，并非所有 AlphaFold 版本。",
        copyPrompt: C.alphafold,
      }],
    },
    compare: {
      key: "compare",
      cells: [{
        prompt: "创造智能四范式：**表征搜索+退火** 换坐标系、**MCTS** 增量搜索、**GAN** 对抗生成、**扩散** 逐步去噪。请对照下表理解与第5章搜索的联系。",
        tableKey: "ch12-compare",
        outputLabel: "对比表",
        copyPrompt: C.compare,
      }],
    },
  },
  notebooks: {
    repr: {
      key: "repr",
      mentorKey: "ch12-repr",
      title: "表征搜索与模拟退火", subtitle: "优化地形的教学示意",
      cells: [
        {
          prompt: "换表征可能改变搜索的难度；模拟退火以一定概率接受较差候选，帮助跳出局部低谷。下图是优化直觉的示意，**不是 AlphaProof 的算法流程**。",
          vibeTip: "代数坐标崎岖，几何坐标可能有缓坡。",
          copyPrompt: C.reprConcept,
        },
        {
          prompt: "请观看损失变化：12.4 → 13.2 → 3.2 → 2.3。注意退火那一步暂时接受了更大的损失。",
          demoKey: "repr", labTarget: "repr", interactive: true,
          copyPrompt: C.reprDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch12-repr" },
        { mentorCell: "selfCheck", mentorKey: "ch12-repr" },
        { mentorCell: "when", mentorKey: "ch12-repr" },
      ],
    },
    mcts: {
      key: "mcts",
      mentorKey: "ch12-mcts",
      title: "MCTS 四步", subtitle: "用模拟结果分配搜索次数",
      cells: [
        {
          prompt: "MCTS：选择（UCT）→ 扩展 → 模拟 → 回传。**用采样估计胜率**，不必展开全部子树——与 MiniMax 本质不同。",
          vibeTip: "UCT = Q子/N子 + c√(ln N父/N子)，c>0；未访问子节点优先尝试。",
          copyPrompt: C.mctsConcept,
        },
        {
          prompt: "观看步进：哪条边被选中？Q/N 如何回传？",
          demoKey: "mcts", labTarget: "mcts", interactive: true,
          copyPrompt: C.mctsDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch12-mcts" },
        { mentorCell: "selfCheck", mentorKey: "ch12-mcts" },
        { mentorCell: "when", mentorKey: "ch12-mcts", labTarget: "mcts" },
      ],
    },
    gan: {
      key: "gan",
      mentorKey: "ch12-gan",
      title: "GAN 对抗训练", subtitle: "G 与 D 零和博弈",
      cells: [
        {
          prompt: "GAN：**生成器**造假样本，**判别器**判真假，二者交替训练。生成器希望 D(x̂)→1；判别器希望辨真辨假。",
          architectureKey: "gan",
          architectureStep: { phase: "both" },
          vibeTip: "生成器与判别器交替优化；理想均衡不代表实际训练一定能达到。",
          copyPrompt: C.ganConcept,
        },
        { prompt: "步进：观察 D(x̂) 随对抗训练变化。", demoKey: "gan", labTarget: "gan", interactive: true, outputLabel: "对抗训练", copyPrompt: C.ganDemo },
        { mentorCell: "misconception", mentorKey: "ch12-gan" },
        { mentorCell: "selfCheck", mentorKey: "ch12-gan" },
        { mentorCell: "when", mentorKey: "ch12-gan" },
      ],
    },
    diffusion: {
      key: "diffusion",
      mentorKey: "ch12-diffusion",
      title: "扩散去噪", subtitle: "前向加噪 · 反向 U-Net",
      cells: [
        {
          prompt: "扩散：**前向**逐步加噪至 x_T≈N(0,I)；**反向**用 U-Net ε_θ(x_t,t) 逐步去噪。训练学预测噪声 ε。",
          architectureKey: "diffusion",
          vibeTip: "雕塑逆过程：从噪声一点点修出形状。",
          copyPrompt: C.diffusionConcept,
        },
        {
          prompt: "对照扩散架构图与步进动画：清晰→噪声→去噪→清晰。",
          demoKey: "diffusion", labTarget: "diffusion", interactive: true,
          copyPrompt: C.diffusionDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch12-diffusion" },
        { mentorCell: "selfCheck", mentorKey: "ch12-diffusion" },
        { mentorCell: "when", mentorKey: "ch12-diffusion", labTarget: "diffusion" },
      ],
    },
  },
  demos: {
    repr: {
      key: "repr",
      stepLabels: ["代数", "退火", "几何", "收敛"],
      trace: [
        { loss: 12.4, repr: "代数", annealStep: 0, history: [{ t: 0.28, y: 0.62 }], title: "代数搜索", summary: "直接在代数表达式空间搜索，损失卡在局部低谷 12.4。", reason: "表征选择会改变优化地形；同一问题在某种坐标下更难。", fields: [{ label: "损失", value: "12.4" }] },
        { loss: 13.2, repr: "代数", temp: 2.0, acceptBad: true, annealStep: 1, history: [{ t: 0.28, y: 0.62 }, { t: 0.38, y: 0.70 }], title: "模拟退火", summary: "温度 T=2.0，损失从 12.4 升到 13.2，接受概率 exp(−0.8/2)≈0.67。", reason: "本步示意一次被接受的较差候选；接受差解不保证下一步就找到更优解。", fields: [{ label: "T", value: "2.0" }, { label: "损失", value: "13.2" }] },
        { loss: 3.2, repr: "几何", annealStep: 2, history: [{ t: 0.55, y: 0.35 }], title: "换几何表征", summary: "改用几何表征后，相邻候选更平滑，沿缓坡下降到 3.2。", reason: "好的表征把难搜索问题变成更容易优化的问题。", fields: [{ label: "损失", value: "3.2" }] },
        { loss: 2.3, repr: "几何", annealStep: 3, history: [{ t: 0.68, y: 0.28 }], title: "继续收敛", summary: "在平滑地形上继续下降，得到更好候选解 2.3。", reason: "表征和搜索策略共同决定能否找到高质量解。", fields: [{ label: "损失", value: "2.3" }] },
      ],
      render(v, s) { window.courseViz.renderReprLandscape(v, s); },
    },
    mcts: {
      key: "mcts", stepLabels: ["选择", "扩展", "模拟", "回传"],
      trace: [
        { phase: "select", active: "b", title: "UCT 选择", summary: "从根节点选 UCT 最大的分支 b。", reason: "UCT 同时看胜率 Q/N 和探索项，避免只盯旧高分。", fields: [{ label: "选择", value: "b" }] },
        { phase: "expand", active: "c", title: "扩展新节点", summary: "在 b 下面添加还没试过的叶节点 c。", reason: "MCTS 不一次展开全树，只在被选中的路径上增长。", fields: [{ label: "新增", value: "c" }] },
        { phase: "sim", active: "c", title: "随机模拟", summary: "从 c 模拟到终局，本次根节点一方获胜，记回报 1。", reason: "一次模拟给出一个样本，累计多次才能估计胜率；本图统一按根节点一方记分。", fields: [{ label: "本次回报", value: "1（获胜）" }] },
        { phase: "backup", active: "b", win: 1, title: "回传统计", summary: "沿 c→b→根更新 N 与累计回报 Q。b 从 N=4,Q=2 变为 N=5,Q=3。", reason: "b 的新平均胜率为 3/5=0.60，不是本次模拟回报 1。", fields: [{ label: "b 胜率", value: "0.60" }] },
      ],
      render(v, s) {
        window.courseViz.renderMCTSTree(v, s);
        v.innerHTML += `<p class="output-caption">${{ select: "选择：UCT 最高的边", expand: "扩展：添加新子节点", sim: "模拟：快速对局", backup: "回传：更新 Q/N" }[s.phase]}</p>`;
      },
    },
    gan: {
      key: "gan",
      architectureKey: "gan",
      stepLabels: ["G", "D", "G", "均衡"],
      trace: [
        { title: "生成器造样本", summary: "噪声 z 经过生成器生成假样本 x̂。", reason: "刚开始假样本很粗糙，判别器只给 D(x̂)=0.18。", fields: [{ label: "D(x̂)", value: "0.18" }], architectureStep: { phase: "g" } },
        { title: "判别器训练", summary: "判别器同时看真样本 x 和假样本 x̂。", reason: "判别器的目标是 D(x真)→1、D(x̂)→0。", fields: [{ label: "D(x真)", value: "0.92" }, { label: "D(x̂)", value: "0.08" }], architectureStep: { phase: "d" } },
        { title: "生成器对抗", summary: "冻结判别器，更新生成器，让假样本更像真样本。", reason: "生成器的目标是骗过判别器，因此希望 D(x̂) 升高。", fields: [{ label: "D(x̂)", value: "0.74" }], architectureStep: { phase: "g" } },
        { title: "理想均衡", summary: "理想情况下，生成分布与真实分布相同，最优判别器输出 0.50。", reason: "反过来，单看 D(x̂)≈0.50 不能证明生成质量好，也可能是判别器尚未学会区分。", fields: [{ label: "D(x̂)，理想情况", value: "≈0.50" }], architectureStep: { phase: "both" } },
      ],
      render(v, s) {
        const phase = s.architectureStep?.phase ?? (s.title.includes("判别器") ? "d" : "g");
        const stepIdx = ["生成器造样本", "判别器训练", "生成器对抗", "理想均衡"].indexOf(s.title);
        v.innerHTML = `<div class="gan-demo-stack"><div class="gan-arch-slot"></div><div class="gan-metrics-slot"></div><div class="gan-formula-slot"></div><div class="gan-canvas-slot"></div><div class="gan-curve-slot"></div></div>`;
        window.courseArch.renderGAN(v.querySelector(".gan-arch-slot"), { phase });
        const metrics = v.querySelector(".gan-metrics-slot");
        metrics.innerHTML = `<div class="repr-table four-elements">${(s.fields || []).map((f) => `<div class="repr-row"><strong>${f.label}</strong><span>${f.value}</span></div>`).join("")}</div>`;
        const formulaSlot = v.querySelector(".gan-formula-slot");
        if (formulaSlot && window.courseMath?.mountMath) {
          const key = stepIdx === 1 ? "gan_d" : stepIdx >= 0 ? "gan_g" : "gan_g";
          formulaSlot.innerHTML = `<div data-math="${key}"></div>`;
          window.courseMath.mountMath(formulaSlot.firstElementChild, key);
        }
        const canvasSlot = v.querySelector(".gan-canvas-slot");
        window.courseViz.renderGanSamples(canvasSlot, stepIdx >= 0 ? stepIdx : 0);
        const curveSlot = v.querySelector(".gan-curve-slot");
        courseShared.renderCanvasDemo(curveSlot, { ...s, _curve: true, canvasAspect: 300 / 560 }, (ctx, w, h) => {
          window.courseViz.drawGanTrainingCurve(ctx, w, h, stepIdx >= 0 ? stepIdx : 0);
        });
        const note = document.createElement("p");
        note.className = "output-caption gan-curve-note";
        note.textContent = window.courseViz.ganCurveCaption(stepIdx >= 0 ? stepIdx : 0);
        curveSlot.appendChild(note);
      },
    },
    alphafold: {
      key: "alphafold",
      stepLabels: ["序列", "MSA", "Evoformer", "结构"],
      trace: [
        { title: "输入序列", summary: "把氨基酸单链编码成模型可处理的词元。", reason: "序列只给出一维顺序，还没有空间距离信息。", phase: 0, fields: [{ label: "输入", value: "氨基酸" }] },
        { title: "MSA 比对", summary: "收集同源序列，观察哪些位置会共同变化。", reason: "共变位置常提示空间上接近或功能相关。", phase: 1, fields: [{ label: "信号", value: "进化共变" }] },
        { title: "Evoformer", summary: "MSA 表示和位置对表示反复交换信息。", reason: "模型在这里同时更新“残基是什么”和“残基两两关系”。", phase: 2, fields: [{ label: "表示", value: "MSA + 位置对" }] },
        { title: "3D 结构", summary: "输出残基坐标，并给每段结构 pLDDT 置信度。", reason: "pLDDT 低的位置说明模型对局部结构不确定。", phase: 3, fields: [{ label: "输出", value: "坐标 + pLDDT" }] },
      ],
      render(v, s) { window.courseViz.renderAlphaFoldFlow(v, s); },
    },
    diffusion: {
      key: "diffusion",
      architectureKey: "diffusion",
      stepLabels: ["x₀", "x_T", "去噪", "x̂₀"],
      trace: [
        { phase: 0, noise: 0.02, t: 0, title: "x₀ 清晰样本", summary: "训练从真实清晰图像 x₀ 开始。", reason: "模型要学的是如何从被加噪版本恢复出 x₀。", fields: [{ label: "t", value: "0" }], architectureStep: { phase: 0 } },
        { phase: 1, noise: 0.95, t: 1000, title: "前向加噪", summary: "逐步加入高斯噪声，最终 x_T 接近纯噪声。", reason: "前向过程是固定的，不需要训练。", fields: [{ label: "t", value: "1000" }], architectureStep: { phase: 1 } },
        { phase: 2, noise: 0.45, t: 500, title: "U-Net 预测噪声", summary: "U-Net 输入 x_t 和时间 t，预测其中的噪声 ε。", reason: "减去预测噪声，就能向更清晰的 x_{t-1} 前进一步。", fields: [{ label: "目标", value: "ε_θ(x_t,t)" }], architectureStep: { phase: 2 } },
        { phase: 3, noise: 0.05, t: 0, title: "得到 x̂₀", summary: "多次反向去噪后得到生成图像 x̂₀。", reason: "生成时从随机噪声出发，反复调用同一个去噪器。", fields: [{ label: "输出", value: "x̂₀" }], architectureStep: { phase: 3 } },
      ],
      render(v, s) {
        v.innerHTML = `<div class="diffusion-stack"><div class="diff-arch-slot"></div><div class="diff-canvas-slot"></div></div>`;
        window.courseArch.renderDiffusion(v.querySelector(".diff-arch-slot"), { phase: s.phase });
        const slot = v.querySelector(".diff-canvas-slot");
        window.courseViz.renderDiffusionStep(slot, s);
      },
    },
  },
  tables: {
    "ch12-compare": `<div class="table-wrap compact"><table class="run-table compact comparison-table"><thead><tr><th>方法</th><th>核心机制</th><th>与第5章搜索</th></tr></thead><tbody>
      <tr><td>表征+退火</td><td>改变表征、以一定概率接受差解</td><td>可能改变搜索空间及邻接关系</td></tr><tr><td>MCTS</td><td>选择/扩展/模拟/回传，UCT 平衡探索</td><td>按采样统计分配搜索预算，不是 MiniMax 的增量版</td></tr>
      <tr><td>GAN</td><td>G 与 D 交替优化，0.5 不是质量证明</td><td>—</td></tr><tr><td>扩散</td><td>前向加噪 + U-Net 逐步去噪</td><td>—</td></tr></tbody></table></div>`,
  },
  labAlgos: [
    { key: "repr", label: "表征搜索", demo: "repr", desc: "代数与几何表征 · 退火跳出局部最优。" },
    { key: "mcts", label: "MCTS", demo: "mcts", desc: "四步循环与 Q/N 回传。" },
    { key: "gan", label: "GAN", demo: "gan", desc: "对照 GAN 架构图看 D(x̂) 变化。" },
    { key: "diffusion", label: "扩散", demo: "diffusion", desc: "对照架构图：前向加噪与 U-Net 反向去噪。" },
    { key: "alphafold", label: "AlphaFold 案例", demo: "alphafold", desc: "案例补充：序列→MSA→Evoformer→3D 结构与 pLDDT。" },
  ],
};

courseShared.bootstrapChapter(
  {
    chapterNum: 12,
    pageTitle: "创造算法 · 分步理解", eyebrow: "《AI思维》第12章 · 创造智能", title: "创造智能 · 搜索、生成与结构设计", readingMeta: "约 32 分钟 · 4 类方法 + AlphaFold 案例", sections: [{ id: "hero", label: "开篇" }, { id: "m0", label: "概览" }, { id: "m1", label: "搜索" }, { id: "m2", label: "MCTS" }, { id: "m3", label: "生成" }, { id: "m4", label: "对比" }, { id: "lab", label: "实验室" }] },
  ch12Config,
);
