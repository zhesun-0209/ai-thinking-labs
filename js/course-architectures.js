"use strict";

(function () {

/* Architecture SVG diagrams — static + step-highlightable */

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function box(x, y, w, h, label, sub, cls = "") {
  return `<g class="arch-box ${cls}" transform="translate(${x},${y})">
    <rect width="${w}" height="${h}" rx="8"></rect>
    <text class="arch-label" x="${w / 2}" y="${h / 2 - (sub ? 4 : 0)}">${esc(label)}</text>
    ${sub ? `<text class="arch-sub" x="${w / 2}" y="${h / 2 + 14}">${esc(sub)}</text>` : ""}
  </g>`;
}

function arrow(x1, y1, x2, y2, cls = "") {
  const marker = cls.includes("is-accent") ? "arch-arrow-accent" : "arch-arrow";
  return `<line class="arch-arrow ${cls}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" marker-end="url(#${marker})"></line>`;
}

function defs() {
  return `<defs>
    <marker id="arch-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#64748b"></path></marker>
    <marker id="arch-arrow-accent" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#0d6b62"></path></marker>
  </defs>`;
}

let archMarkerUid = 0;

function mount(container, svgInner, viewBox, label) {
  const uid = `arch-${++archMarkerUid}`;
  const scopedSvg = `${defs()}${svgInner}`
    .replaceAll('id="arch-arrow-accent"', `id="${uid}-arrow-accent"`)
    .replaceAll("url(#arch-arrow-accent)", `url(#${uid}-arrow-accent)`)
    .replaceAll('id="arch-arrow"', `id="${uid}-arrow"`)
    .replaceAll("url(#arch-arrow)", `url(#${uid}-arrow)`);
  container.innerHTML = `<figure class="arch-figure" aria-label="${esc(label)}">
    <svg class="arch-svg" viewBox="${viewBox}" role="img">${scopedSvg}</svg>
    <figcaption class="arch-caption">${esc(label)}</figcaption>
  </figure>`;
}

function renderEncoderDecoder(container, step = {}) {
  const hi = new Set(step.highlight || []);
  const inner = `
    ${box(20, 60, 90, 44, "输入序列", "x₁…xₙ", hi.has("input") ? "is-active" : "")}
    ${arrow(110, 82, 140, 82)}
    ${box(140, 44, 100, 76, "Encoder", "RNN/Transformer", hi.has("enc") ? "is-active" : "")}
    ${arrow(240, 82, 270, 82)}
    ${box(270, 60, 90, 44, "上下文", "c", hi.has("ctx") ? "is-active" : "")}
    ${arrow(360, 82, 390, 82)}
    ${box(390, 44, 100, 76, "Decoder", "自回归生成", hi.has("dec") ? "is-active" : "")}
    ${arrow(490, 82, 520, 82)}
    ${box(520, 60, 90, 44, "输出", "y₁…yₘ", hi.has("out") ? "is-active" : "")}
    ${hi.has("attn") ? `<g class="arch-attn-bridge">
      ${arrow(190, 120, 440, 120, "is-accent")}
      <text x="315" y="138" text-anchor="middle" class="arch-anno">Attention: Q(dec) · K(enc)</text>
    </g>` : ""}`;
  mount(container, inner, "0 0 640 160", "Encoder–Decoder + Attention");
}

function renderTransformerBlock(container, step = {}) {
  const hi = new Set(step.highlight || []);
  const inner = `
    ${box(20, 50, 80, 40, "输入", "X", hi.has("in") ? "is-active" : "")}
    ${arrow(100, 70, 130, 70)}
    ${box(130, 30, 120, 80, "Multi-Head", "Self-Attention", hi.has("attn") ? "is-active" : "")}
    ${arrow(250, 70, 280, 70)}
    ${box(280, 40, 90, 60, "Add+Norm", "", hi.has("norm1") ? "is-active" : "")}
    ${arrow(370, 70, 400, 70)}
    ${box(400, 30, 100, 80, "FFN", "前馈网络", hi.has("ffn") ? "is-active" : "")}
    ${arrow(500, 70, 530, 70)}
    ${box(530, 40, 90, 60, "Add+Norm", "", hi.has("norm2") ? "is-active" : "")}
    ${arrow(620, 70, 650, 70)}
    ${box(650, 50, 80, 40, "输出", "X′", hi.has("out") ? "is-active" : "")}`;
  mount(container, inner, "0 0 740 120", "Transformer Encoder Block");
}

function renderDiffusion(container, step = {}) {
  const t = step.phase ?? 0;
  const phases = ["x₀ 清晰", "加噪 x_t", "去噪中", "x̂₀ 恢复"];
  const inner = `
    ${box(30, 50, 70, 50, "x₀", "数据", t === 0 ? "is-active" : t > 0 ? "is-done" : "")}
    ${arrow(100, 75, 130, 75, t >= 1 ? "is-accent" : "")}
    ${box(130, 40, 90, 70, "Forward", "q(x_t|x₀)", t === 1 ? "is-active" : "")}
    ${arrow(220, 75, 250, 75)}
    ${box(250, 50, 70, 50, "x_T", "≈噪声", t === 1 ? "is-active" : "")}
    ${arrow(320, 75, 350, 75, t >= 2 ? "is-accent" : "")}
    ${box(350, 40, 100, 70, "U-Net", "ε_θ(x_t,t)", t === 2 ? "is-active" : "")}
    ${arrow(450, 75, 480, 75, t >= 3 ? "is-accent" : "")}
    ${box(480, 50, 70, 50, "x̂₀", "生成", t === 3 ? "is-active" : "")}
    <text x="280" y="130" text-anchor="middle" class="arch-anno">${esc(phases[t] || "")}</text>`;
  mount(container, inner, "0 0 560 150", "扩散模型：前向加噪 · 反向去噪");
}

function renderGAN(container, step = {}) {
  const hi = step.phase || "both";
  const inner = `
    ${box(40, 90, 60, 36, "z", "噪声", hi === "g" ? "is-active" : "")}
    ${arrow(100, 108, 130, 108, hi === "g" ? "is-accent" : "")}
    ${box(130, 70, 90, 76, "Generator", "G", hi === "g" ? "is-active" : "")}
    ${arrow(220, 108, 250, 108)}
    ${box(250, 90, 70, 36, "x̂", "假样本", hi === "g" || hi === "d" ? "is-active" : "")}
    ${arrow(320, 108, 350, 108, hi === "d" ? "is-accent" : "")}
    ${box(350, 70, 100, 76, "Discriminator", "D", hi === "d" ? "is-active" : "")}
    ${arrow(450, 108, 480, 108)}
    ${box(480, 90, 60, 36, "0/1", "真假", hi === "d" ? "is-active" : "")}
    ${box(250, 20, 70, 36, "x", "真样本", hi === "d" ? "is-active" : "")}
    ${arrow(285, 56, 400, 70, hi === "d" ? "is-accent" : "")}`;
  mount(container, inner, "0 0 560 160", "GAN：生成器 vs 判别器");
}

function renderCLIP(container) {
  const cx = 320;
  const cy = 100;
  const inner = `
    ${box(24, 28, 72, 44, "Image", "I", "is-active")}
    ${arrow(96, 50, 118, 50)}
    ${box(118, 18, 96, 64, "Image Enc.", "ViT/ResNet", "is-active")}
    ${arrow(214, 50, 248, 50, "is-accent")}
    <text x="232" y="44" class="arch-anno">W_I</text>
    <path d="M 248 50 L ${cx - 72} ${cy - 8}" stroke="#0d6b62" stroke-width="2" fill="none" marker-end="url(#arch-arr)"/>
    ${box(24, 118, 72, 44, "Text", "T", "is-active")}
    ${arrow(96, 140, 118, 140)}
    ${box(118, 108, 96, 64, "Text Enc.", "Transformer", "is-active")}
    ${arrow(214, 140, 248, 140, "is-accent")}
    <text x="232" y="134" class="arch-anno">W_T</text>
    <path d="M 248 140 L ${cx - 72} ${cy + 8}" stroke="#c2410c" stroke-width="2" fill="none" marker-end="url(#arch-arr)"/>
    <ellipse cx="${cx}" cy="${cy}" rx="72" ry="46" fill="#ecfdf5" stroke="#0d6b62" stroke-width="2"/>
    <text x="${cx}" y="${cy - 6}" text-anchor="middle" class="arch-label">联合嵌入空间</text>
    <text x="${cx}" y="${cy + 12}" text-anchor="middle" class="arch-anno">L2 归一化 · ℝᵈ</text>
    ${arrow(cx + 72, cy, 408, cy, "is-accent")}
    ${box(408, 72, 88, 56, "相似度", "N×N", "is-active")}
    <text x="280" y="14" class="arch-anno">CLIP：双塔 → 同一嵌入空间 → 批内对比学习（Radford et al.）</text>`;
  mount(container, inner, "0 0 520 200", "CLIP 双塔架构");
}

function renderCNN(container, step = {}) {
  const hi = step.highlight || "conv";
  const inner = `
    ${box(20, 50, 70, 60, "输入", "H×W", hi === "in" ? "is-active" : "")}
    ${arrow(90, 80, 120, 80)}
    ${box(120, 40, 90, 80, "Conv", "3×3·ReLU", hi === "conv" ? "is-active" : "")}
    ${arrow(210, 80, 240, 80)}
    ${box(240, 50, 70, 60, "特征图", "H′×W′", hi === "feat" ? "is-active" : "")}
    ${arrow(310, 80, 340, 80)}
    ${box(340, 40, 90, 80, "Pool", "Max 2×2", hi === "pool" ? "is-active" : "")}
    ${arrow(430, 80, 460, 80)}
    ${box(460, 50, 80, 60, "FC", "分类", hi === "fc" ? "is-active" : "")}`;
  mount(container, inner, "0 0 560 140", "CNN：卷积 → 池化 → 全连接");
}

function renderViT(container, step = {}) {
  const hi = new Set(step.highlight || []);
  const inner = `
    ${box(20, 55, 80, 50, "图像", "H×W×C", hi.has("img") ? "is-active" : "")}
    ${arrow(100, 80, 130, 80)}
    ${box(130, 45, 100, 70, "Patchify", "P×P 切块", hi.has("patch") ? "is-active" : "")}
    ${arrow(230, 80, 260, 80)}
    ${box(260, 45, 110, 70, "Linear+Pos", "token 序列", hi.has("pos") ? "is-active" : "")}
    ${arrow(370, 80, 400, 80)}
    ${box(400, 30, 130, 100, "Transformer", "Encoder×L", hi.has("enc") ? "is-active" : "")}
    ${arrow(530, 80, 560, 80)}
    ${box(560, 55, 80, 50, "Head", "分类", hi.has("head") ? "is-active" : "")}`;
  mount(container, inner, "0 0 660 140", "Vision Transformer (ViT)");
}

function renderMAE(container, step = {}) {
  const hi = step.phase ?? 0;
  const inner = `
    ${box(20, 50, 80, 50, "Patches", "100%", hi === 0 ? "is-active" : "is-done")}
    ${arrow(100, 75, 130, 75)}
    ${box(130, 35, 100, 80, "Mask", "75% 遮", hi === 1 ? "is-active" : "")}
    ${arrow(230, 75, 260, 75)}
    ${box(260, 40, 110, 70, "Encoder", "只看 25%", hi === 2 ? "is-active" : "")}
    ${arrow(370, 75, 400, 75)}
    ${box(400, 40, 110, 70, "Decoder", "+mask token", hi === 3 ? "is-active" : "")}
    ${arrow(510, 75, 540, 75)}
    ${box(540, 50, 80, 50, "重构", "像素", hi === 3 ? "is-active" : "")}`;
  mount(container, inner, "0 0 640 130", "MAE：掩码自编码预训练");
}

function renderSkipGram(container, step = {}) {
  const inner = `
    ${box(240, 30, 80, 40, "中心词", "鲁迅", "is-active")}
    ${arrow(280, 70, 280, 100, "is-accent")}
    ${box(220, 100, 120, 50, "Softmax", "P(ctx|中心)", step.phase === "softmax" ? "is-active" : "")}
    ${arrow(200, 125, 120, 125)}
    ${box(60, 100, 60, 50, "写", "正例", "is-active")}
    ${arrow(360, 125, 440, 125)}
    ${box(440, 100, 60, 50, "了", "正例", "is-active")}
    ${arrow(280, 150, 280, 180, "is-accent")}
    ${box(200, 180, 160, 40, "负采样", "桌子、天气…", step.phase === "neg" ? "is-active" : "")}`;
  mount(container, inner, "0 0 560 230", "Word2Vec Skip-gram + 负采样");
}

function renderMDPLoop(container) {
  const inner = `
    ${box(240, 20, 100, 44, "Agent", "π(a|s)", "is-active")}
    ${arrow(290, 64, 290, 90, "is-accent")}
    ${box(220, 90, 140, 44, "环境 Env", "s, r, s′", "is-active")}
    ${arrow(220, 112, 120, 112)}
    ${box(40, 90, 100, 44, "状态 s", "", "is-active")}
    ${arrow(360, 112, 460, 112)}
    ${box(460, 90, 100, 44, "动作 a", "", "is-active")}
    ${arrow(290, 134, 290, 160, "is-accent")}
    ${box(220, 160, 140, 44, "奖励 r", "+折扣 γ", "is-active")}`;
  mount(container, inner, "0 0 580 220", "MDP 智能体–环境交互环");
}

function renderTransE(container) {
  const inner = `
    ${box(40, 60, 80, 50, "h", "鲁迅", "is-active")}
    ${arrow(120, 85, 160, 85, "is-accent")}
    ${box(160, 60, 80, 50, "r", "创作", "is-active")}
    ${arrow(240, 85, 280, 85, "is-accent")}
    ${box(280, 60, 80, 50, "t", "呐喊", "is-active")}
    <text x="200" y="130" text-anchor="middle" class="arch-anno">h + r ≈ t（平移假设）</text>
    ${box(400, 55, 140, 60, "负采样 t′", "红楼梦", "")}`;
  mount(container, inner, "0 0 560 150", "TransE 图谱嵌入");
}

function renderMLPStack(container, step = {}) {
  const hi = new Set(Array.isArray(step.highlight) ? step.highlight : step.highlight ? [step.highlight] : ["in", "hid", "out", "lin1", "lin2"]);
  const on = (k) => hi.has(k);
  const inner = `
    ${box(30, 55, 70, 40, "x", "[6.2,0.8]", on("in") ? "is-active" : "")}
    ${arrow(100, 75, 130, 75)}
    ${box(130, 35, 90, 80, "Linear", "W₁x+b₁", on("lin1") || on("hid") ? "is-active" : "")}
    ${arrow(220, 75, 250, 75)}
    ${box(250, 45, 80, 60, "ReLU", "max(0,·)", on("hid") ? "is-active" : "")}
    ${arrow(330, 75, 360, 75)}
    ${box(360, 35, 90, 80, "Linear", "W₂h+b₂", on("lin2") || on("out") ? "is-active" : "")}
    ${arrow(450, 75, 480, 75)}
    ${box(480, 55, 70, 40, "σ", "ŷ=0.82", on("out") ? "is-active" : "")}`;
  mount(container, inner, "0 0 570 130", "小 MLP：血糖预测");
}

function renderDecisionTreeArch(container) {
  const inner = `
    <g class="arch-tree">
      <rect x="250" y="10" width="120" height="36" rx="6" class="arch-tree-node is-active"/>
      <text x="310" y="33" text-anchor="middle">含分数?</text>
      <line x1="280" y1="46" x2="160" y2="80" class="arch-arrow"/>
      <line x1="340" y1="46" x2="460" y2="80" class="arch-arrow"/>
      <text x="200" y="70" class="arch-anno">是</text>
      <text x="400" y="70" class="arch-anno">否</text>
      <rect x="100" y="80" width="120" height="36" rx="6" class="arch-tree-node"/>
      <text x="160" y="103" text-anchor="middle">计算错误</text>
      <rect x="400" y="80" width="120" height="36" rx="6" class="arch-tree-node"/>
      <text x="460" y="103" text-anchor="middle">概念题?</text>
      <line x1="430" y1="116" x2="360" y2="150" class="arch-arrow"/>
      <line x1="490" y1="116" x2="560" y2="150" class="arch-arrow"/>
      <rect x="300" y="150" width="120" height="36" rx="6" class="arch-tree-node"/>
      <text x="360" y="173" text-anchor="middle">概念混淆</text>
      <rect x="500" y="150" width="120" height="36" rx="6" class="arch-tree-node"/>
      <text x="560" y="173" text-anchor="middle">粗心</text>
    </g>`;
  mount(container, inner, "0 0 640 200", "决策树结构（错题分类）");
}

function renderActorCriticArch(container, step = {}) {
  const hi = new Set(step.highlight || []);
  const inner = `
    ${box(40, 70, 90, 44, "状态 s", "", hi.has("s") ? "is-active" : "")}
    ${arrow(130, 92, 170, 92)}
    ${box(170, 50, 110, 84, "Actor", "π(a|s)", hi.has("actor") ? "is-active" : "")}
    ${arrow(280, 92, 320, 92)}
    ${box(320, 70, 80, 44, "动作 a", "", hi.has("a") ? "is-active" : "")}
    ${arrow(170, 134, 170, 160, hi.has("critic") ? "is-accent" : "")}
    ${box(130, 160, 110, 70, "Critic", "V(s), A", hi.has("critic") ? "is-active" : "")}
    ${arrow(400, 92, 440, 92)}
    ${box(440, 70, 90, 44, "环境", "r, s′", hi.has("env") ? "is-active" : "")}`;
  mount(container, inner, "0 0 560 240", "Actor-Critic 双网络");
}

function renderDecoderBlock(container, step = {}) {
  const hi = new Set(step.highlight || []);
  const inner = `
    ${box(20, 50, 90, 40, "前缀", "tokens", hi.has("in") ? "is-active" : "")}
    ${arrow(110, 70, 140, 70)}
    ${box(140, 28, 140, 84, "Masked MHA", "因果掩码", hi.has("attn") ? "is-active" : "")}
    ${arrow(280, 70, 310, 70)}
    ${box(310, 40, 90, 60, "Add+Norm", "", hi.has("norm1") ? "is-active" : "")}
    ${arrow(400, 70, 430, 70)}
    ${box(430, 28, 100, 84, "FFN", "", hi.has("ffn") ? "is-active" : "")}
    ${arrow(530, 70, 560, 70)}
    ${box(560, 50, 100, 44, "Softmax", "P(下一token)", hi.has("out") ? "is-active" : "")}
    <text x="340" y="130" text-anchor="middle" class="arch-anno">GPT = Decoder Block × L（无 Encoder）</text>`;
  mount(container, inner, "0 0 680 140", "GPT Decoder Block（因果自注意力）");
}

function renderArchitecture(container, key, step) {
  const map = {
    "encoder-decoder": renderEncoderDecoder,
    transformer: renderTransformerBlock,
    "decoder-only": renderDecoderBlock,
    gpt: renderDecoderBlock,
    diffusion: renderDiffusion,
    gan: renderGAN,
    clip: renderCLIP,
    cnn: renderCNN,
    vit: renderViT,
    mae: renderMAE,
    skipgram: renderSkipGram,
    mdp: renderMDPLoop,
    "actor-critic": renderActorCriticArch,
    transe: renderTransE,
    mlp: renderMLPStack,
    "decision-tree": renderDecisionTreeArch,
  };
  (map[key] || renderMLPStack)(container, step || {});
}

window.courseArch = {
  renderArchitecture,
  renderEncoderDecoder,
  renderTransformerBlock,
  renderDecoderBlock,
  renderDiffusion,
  renderGAN,
  renderCLIP,
  renderCNN,
  renderViT,
  renderMAE,
  renderSkipGram,
  renderMDPLoop,
  renderTransE,
  renderMLPStack,
  renderDecisionTreeArch,
};
})();
