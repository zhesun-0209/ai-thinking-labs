"use strict";

(function () {

let vizMarkerSeq = 0;

function entropy(counts) {
  const total = counts.reduce((a, b) => a + b, 0);
  if (total <= 0) return 0;
  return -counts
    .filter((c) => c > 0)
    .reduce((h, c) => {
      const p = c / total;
      return h + p * Math.log2(p);
    }, 0);
}

function infoGain(parentCounts, splits) {
  const parentH = entropy(parentCounts);
  const total = parentCounts.reduce((a, b) => a + b, 0);
  const rem =
    splits.reduce((acc, split) => {
      const w = split.counts.reduce((a, b) => a + b, 0) / total;
      return acc + w * entropy(split.counts);
    }, 0) || 0;
  return parentH - rem;
}

function fmt(n, d = 2) {
  return Number(n).toFixed(d);
}

let transeMarkerUid = 0;

function renderFormula(container, keyOrLatex) {
  if (window.courseMath?.mountMath && window.courseMath.formulas[keyOrLatex]) {
    window.courseMath.mountMath(container, keyOrLatex);
    return;
  }
  container.innerHTML = `<div class="formula-card"><code>${keyOrLatex}</code></div>`;
}

function renderLegend(container, items) {
  container.insertAdjacentHTML(
    "beforeend",
    `<div class="viz-legend">${items.map((it) => `<span class="viz-legend-item"><i style="background:${it.color}"></i>${it.label}</span>`).join("")}</div>`,
  );
}

function renderDecisionTree(container, tree, highlight = []) {
  const hi = new Set(highlight);
  function node(n, depth = 0) {
    if (n.leaf) {
      return `<li class="dt-leaf ${hi.has(n.id) ? "is-active" : ""}"><span class="dt-label">${n.label}</span><span class="dt-meta">${n.count ?? ""} 样本 → ${n.prediction}</span></li>`;
    }
    return `<li class="dt-node ${hi.has(n.id) ? "is-active" : ""}">
      <div class="dt-split"><span class="dt-q">${n.question}</span>${n.gain != null ? `<span class="dt-gain">增益 ${fmt(n.gain)}</span>` : ""}${n.entropy != null ? `<span class="dt-entropy">H=${fmt(n.entropy)}</span>` : ""}</div>
      <ul class="dt-children"><li class="dt-branch"><span class="dt-branch-label">是</span>${node(n.yes, depth + 1)}</li><li class="dt-branch"><span class="dt-branch-label">否</span>${node(n.no, depth + 1)}</li></ul>
    </li>`;
  }
  container.innerHTML = `<ul class="decision-tree">${node(tree)}</ul>`;
}

function renderConfusionMatrix(container, { tp, fp, fn, tn, thr }) {
  const total = tp + fp + fn + tn;
  const acc = total ? (tp + tn) / total : 0;
  const p = tp + fp ? tp / (tp + fp) : 0;
  const r = tp + fn ? tp / (tp + fn) : 0;
  const f1 = p + r ? (2 * p * r) / (p + r) : 0;
  container.innerHTML = `
    <div class="confusion-wrap">
      <div class="confusion-grid" role="img" aria-label="混淆矩阵">
        <div></div><div class="cg-head">预测正</div><div class="cg-head">预测负</div>
        <div class="cg-head">实际正</div><div class="cg-cell tp">${tp}<span>TP</span></div><div class="cg-cell fn">${fn}<span>FN</span></div>
        <div class="cg-head">实际负</div><div class="cg-cell fp">${fp}<span>FP</span></div><div class="cg-cell tn">${tn}<span>TN</span></div>
      </div>
      <div class="metric-bars">
        <div class="metric-bar-row"><span>精确率 P</span><div class="metric-bar"><i style="width:${p * 100}%"></i></div><em>${fmt(p)}</em></div>
        <div class="metric-bar-row"><span>召回率 R</span><div class="metric-bar"><i style="width:${r * 100}%"></i></div><em>${fmt(r)}</em></div>
        <div class="metric-bar-row"><span>F1</span><div class="metric-bar accent"><i style="width:${f1 * 100}%"></i></div><em>${fmt(f1)}</em></div>
        <div class="metric-bar-row"><span>准确率</span><div class="metric-bar"><i style="width:${acc * 100}%"></i></div><em>${fmt(acc)}</em></div>
      </div>
      ${thr != null ? `<p class="output-caption">分类阈值 τ = ${thr}</p>` : ""}
    </div>`;
}

function renderMLP(container, step) {
  const layers = step.layers || [
    { name: "输入", nodes: ["x₁", "x₂"], values: [6.2, 0.8] },
    { name: "隐藏 ReLU", nodes: ["h₁", "h₂"], values: [0.71, 0.45] },
    { name: "输出 σ", nodes: ["ŷ"], values: [0.82] },
  ];
  const active = step.activeLayer ?? 0;
  const xFor = (li) => 70 + li * 180;
  const yFor = (ns, ni) => 112 + (ni - (ns - 1) / 2) * 78;
  const edgeMarkup = layers
    .slice(0, -1)
    .map((layer, li) => {
      const x0 = xFor(li);
      const x1 = xFor(li + 1);
      const n0 = layer.nodes.length;
      const n1 = layers[li + 1].nodes.length;
      let edges = "";
      for (let a = 0; a < n0; a++)
        for (let b = 0; b < n1; b++) {
          const y0 = yFor(n0, a);
          const y1 = yFor(n1, b);
          edges += `<line class="mlp-edge ${li < active ? "is-on" : ""}" x1="${x0 + 24}" y1="${y0}" x2="${x1 - 24}" y2="${y1}"></line>`;
        }
      return edges;
    })
    .join("");
  const nodeMarkup = layers
    .map((layer, li) => {
      const x = xFor(li);
      const ns = layer.nodes.length;
      return layer.nodes
        .map((n, ni) => {
          const y = yFor(ns, ni);
          const on = li <= active;
          const cur = li === active;
          return `<g class="mlp-node ${on ? "is-on" : ""} ${cur ? "is-current" : ""}" transform="translate(${x},${y})">
            <circle r="22"></circle><text dy="4">${n}</text>
            ${layer.values?.[ni] != null ? `<text class="mlp-val" y="38">${layer.values[ni]}</text>` : ""}
          </g>`;
        })
        .join("");
    })
    .join("");
  container.innerHTML = `
    <svg class="mlp-svg" viewBox="0 0 520 230" role="img" aria-label="MLP 结构">
      ${edgeMarkup}
      ${nodeMarkup}
      ${layers.map((layer, li) => `<text class="mlp-layer-label" x="${xFor(li)}" y="28" text-anchor="middle">${layer.name}</text>`).join("")}
    </svg>`;
}

function renderHeatmapLabeled(container, matrix, rowLabels, colLabels, opts = {}) {
  const max = Math.max(...matrix.flat(), 0.001);
  const title = opts.title ? `<p class="heat-title">${opts.title}</p>` : "";
  const rows = matrix
    .map(
      (row, i) =>
        `<div class="heat-row"><span class="heat-row-label">${rowLabels[i] || i}</span>${row
          .map((v, j) => {
            const t = v / max;
            return `<div class="heat-cell" style="background:rgba(13,107,98,${0.1 + t * 0.78})" title="${rowLabels[i]}→${colLabels[j]}: ${fmt(v)}">${fmt(v)}</div>`;
          })
          .join("")}</div>`,
    )
    .join("");
  container.innerHTML = `${title}<div class="heat-labeled"><div class="heat-col-labels"><span></span>${colLabels.map((c) => `<span>${c}</span>`).join("")}</div>${rows}</div>`;
}

function renderAttentionFlow(container, step) {
  const sourceTokens = step.sourceTokens || ["鲁迅", "写", "日记"];
  const queryToken = step.queryToken || "日记";
  const scores = step.scores || [0.4, 2.1, 0.3];
  const weights = step.weights || [0.05, 0.8, 0.15];
  const phase = step.phase || "score";
  const mode = step.mode || "cross";
  const focus = step.focusIndex ?? weights.reduce((best, v, i, arr) => (v > arr[best] ? i : best), 0);
  const queryIndex = Math.max(0, sourceTokens.indexOf(queryToken));
  const W = 780;
  const H = mode === "self" ? 420 : 388;
  const n = sourceTokens.length;
  const normalizedScore = (v) => {
    const min = Math.min(...scores);
    const max = Math.max(...scores);
    return max === min ? 0.5 : (v - min) / (max - min);
  };
  const showWeights = phase !== "score";
  const showContext = phase === "context";
  const title =
    mode === "self"
      ? `Self-Attention：Q(${queryToken}) 查询同一句所有 K`
      : `Cross-Attention：Decoder 的 Q(${queryToken}) 查询 Encoder 的 K/V`;
  const querySub = mode === "self" ? "Q/K/V 同句" : "Q 来自 Decoder";
  const memorySub = mode === "self" ? "同一句 token（K,V）" : "Encoder 序列（K,V）";
  const resultLabel = mode === "self" ? `新表示：${queryToken}′` : `输出倾向：${sourceTokens[focus]}`;

  const encGap = n > 1 ? Math.min(118, (mode === "cross" ? 400 : W - 120) / (n - 1)) : 0;
  const encStart = mode === "cross" ? 72 : (W - encGap * (n - 1)) / 2;
  const encY = mode === "self" ? 162 : 136;
  const queryPos =
    mode === "cross"
      ? { x: W - 108, y: 236 }
      : { x: encStart + queryIndex * encGap, y: encY };

  const lineMetric = showWeights ? weights : scores.map(normalizedScore);
  const lineMarkup = sourceTokens
    .map((tok, i) => {
      if (mode === "self" && i === queryIndex) return "";
      const x = encStart + i * encGap;
      const y = encY;
      const width = 1.2 + lineMetric[i] * 4.5;
      const opacity = 0.2 + lineMetric[i] * 0.72;
      const cls = i === focus ? "is-focus" : "";
      const qx = queryPos.x;
      const qy = mode === "cross" ? queryPos.y - 28 : queryPos.y;
      const tx = x;
      const ty = y;
      const midY =
        mode === "self"
          ? Math.min(qy, ty) - 64 - Math.abs(i - queryIndex) * 7
          : (qy + ty) / 2 - 20;
      const path =
        mode === "self"
          ? `M ${qx} ${qy - 26} Q ${(qx + tx) / 2} ${midY} ${tx} ${ty - 26}`
          : `M ${qx - 36} ${qy} L ${tx + 34} ${ty}`;
      return `<path class="attention-link ${cls}" d="${path}" fill="none" style="stroke-width:${width};opacity:${opacity}"></path>`;
    })
    .join("");

  const sourceMarkup = sourceTokens
    .map((tok, i) => {
      const x = encStart + i * encGap;
      const y = encY;
      const weight = weights[i] ?? 0;
      const score = scores[i] ?? 0;
      const isQuery = mode === "self" && i === queryIndex;
      const cls = [i === focus ? "is-focus" : "", isQuery ? "is-query" : ""].filter(Boolean).join(" ");
      const metric = showWeights ? `α=${fmt(weight, 2)}` : `score=${fmt(score, 1)}`;
      return `<g class="attention-token ${cls}" transform="translate(${x},${y})">
        <rect x="-34" y="-26" width="68" height="52" rx="10"></rect>
        <text class="attention-token-main" y="-2" text-anchor="middle">${tok}</text>
        <text class="attention-token-sub" y="14" text-anchor="middle">${isQuery ? "Q+K,V" : "Kᵢ,Vᵢ"}</text>
        ${showWeights || phase === "score" ? `<rect class="attention-weight-track" x="-30" y="32" width="60" height="7" rx="3"></rect>
        <rect class="attention-weight-fill" x="-30" y="32" width="${Math.max(3, 60 * (showWeights ? weight : normalizedScore(score)))}" height="7" rx="3"></rect>
        <text class="attention-score-label" y="52" text-anchor="middle">${metric}</text>` : ""}
        ${isQuery ? `<text class="attention-query-badge" x="28" y="-18">Q</text>` : ""}
      </g>`;
    })
    .join("");

  const contextY = mode === "self" ? 292 : 286;
  const contextBars = sourceTokens
    .map((tok, i) => {
      const x = 100 + i * Math.min(76, (W - 200) / Math.max(n - 1, 1));
      const h = Math.max(8, weights[i] * 44);
      const cls = i === focus ? "is-focus" : "";
      return `<g class="attention-contrib ${cls}" transform="translate(${x},0)">
        <rect x="-16" y="${contextY - h}" width="32" height="${h}" rx="6"></rect>
        <text x="0" y="${contextY + 16}" text-anchor="middle">${tok}</text>
      </g>`;
    })
    .join("");

  const stageY = mode === "self" ? 362 : 338;
  const stage = (x, label, active) => `<g class="attention-stage ${active ? "is-active" : ""}" transform="translate(${x},${stageY})">
    <rect x="-58" y="-14" width="116" height="24" rx="12"></rect>
    <text y="2" text-anchor="middle">${label}</text>
  </g>`;

  const crossQueryMarkup =
    mode === "cross"
      ? `<g class="attention-query" transform="translate(${queryPos.x},${queryPos.y})">
          <rect x="-42" y="-28" width="84" height="56" rx="12"></rect>
          <text class="attention-query-main" y="-4" text-anchor="middle">Q</text>
          <text class="attention-query-sub" y="16" text-anchor="middle">${queryToken}</text>
          <text class="attention-query-hint" y="38" text-anchor="middle">${querySub}</text>
        </g>
        <text class="attention-section-label" x="${queryPos.x}" y="${queryPos.y - 44}" text-anchor="middle">Decoder</text>`
      : `<text class="attention-self-hint" x="36" y="98">高亮 token 同时充当 Q，向全句 K 发查询</text>`;

  container.innerHTML = `
    <div class="attention-flow-wrap">
      <svg class="attention-flow-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="${mode === "self" ? "Self-Attention 步进图" : "Encoder-Decoder Attention 步进图"}">
        <rect class="attention-bg" x="10" y="10" width="760" height="${H - 20}" rx="16"></rect>
        <text class="attention-title" x="28" y="34">${title}</text>
        <text class="attention-caption" x="28" y="54">${phase === "score" ? "第 1 步：用 Q 与每个 K 做点积，得到相似度分数。" : phase === "softmax" ? "第 2 步：Softmax 把分数变成权重，权重和为 1。" : "第 3 步：按权重加权 V，得到当前步需要的上下文信息。"}</text>
        <text class="attention-section-label" x="36" y="78">${memorySub}</text>
        ${mode === "cross" ? `<text class="attention-section-label" x="36" y="${encY - 44}">Encoder</text>` : ""}
        ${lineMarkup}
        ${sourceMarkup}
        ${crossQueryMarkup}
        ${showContext ? `<g class="attention-context">
          <text class="attention-section-label" x="36" y="${contextY - 62}">context = Σ αᵢVᵢ</text>
          ${contextBars}
          <g class="attention-output" transform="translate(318, ${contextY + 34})">
            <rect width="144" height="48" rx="10"></rect>
            <text x="72" y="20" text-anchor="middle">上下文向量 c</text>
            <text x="72" y="38" text-anchor="middle">${resultLabel}</text>
          </g>
        </g>` : ""}
        ${stage(168, "Q·Kᵀ 打分", phase === "score")}
        ${stage(390, "Softmax 权重", phase === "softmax")}
        ${stage(612, "加权 V 输出", phase === "context")}
      </svg>
    </div>`;
}

function drawChartAxes(ctx, w, h, pad, xLabel, yLabel, opts = {}) {
  const gridX = opts.gridX ?? 4;
  const gridY = opts.gridY ?? 4;
  const plotW = w - pad.l - pad.r;
  const plotH = h - pad.t - pad.b;
  ctx.strokeStyle = "#eef2f6";
  ctx.lineWidth = 1;
  for (let i = 1; i < gridX; i++) {
    const x = pad.l + (i / gridX) * plotW;
    ctx.beginPath();
    ctx.moveTo(x, pad.t);
    ctx.lineTo(x, h - pad.b);
    ctx.stroke();
  }
  for (let i = 1; i < gridY; i++) {
    const y = pad.t + (i / gridY) * plotH;
    ctx.beginPath();
    ctx.moveTo(pad.l, y);
    ctx.lineTo(w - pad.r, y);
    ctx.stroke();
  }
  ctx.strokeStyle = "#94a3b8";
  ctx.lineWidth = 1.25;
  ctx.beginPath();
  ctx.moveTo(pad.l, pad.t);
  ctx.lineTo(pad.l, h - pad.b);
  ctx.lineTo(w - pad.r, h - pad.b);
  ctx.stroke();
  ctx.fillStyle = "#64748b";
  ctx.font = "12px ui-sans-serif, system-ui, -apple-system, sans-serif";
  if (xLabel) ctx.fillText(xLabel, w / 2 - 20, h - 8);
  if (yLabel) {
    ctx.save();
    ctx.translate(14, h / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText(yLabel, 0, 0);
    ctx.restore();
  }
}

function drawScatterRegression(ctx, w, h, points, line, opts = {}) {
  const hasParamBox = opts.w != null;
  const paramBoxW = hasParamBox ? Math.min(136, Math.max(118, Math.round(w * 0.3))) : 0;
  const pad = { l: 48, r: hasParamBox ? paramBoxW + 24 : 16, t: 16, b: 36 };
  ctx.fillStyle = "#f8fafc";
  ctx.fillRect(0, 0, w, h);
  drawChartAxes(ctx, w, h, pad, opts.xLabel || "x", opts.yLabel || "y");
  const xs = points.map((p) => p[0]);
  const ys = points.map((p) => p[1]);
  const minX = Math.min(...xs, 0);
  const maxX = Math.max(...xs, 1);
  const minY = Math.min(...ys, 0);
  const maxY = Math.max(...ys, 1);
  const sx = (x) => pad.l + ((x - minX) / (maxX - minX || 1)) * (w - pad.l - pad.r);
  const sy = (y) => h - pad.b - ((y - minY) / (maxY - minY || 1)) * (h - pad.t - pad.b);
  points.forEach(([x, y]) => {
    ctx.fillStyle = "#0d6b62";
    ctx.beginPath();
    ctx.arc(sx(x), sy(y), 5, 0, 7);
    ctx.fill();
  });
  if (line) {
    const [w0, b0, w1, b1] = line;
    ctx.strokeStyle = "#c2410c";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(sx(w0), sy(b0));
    ctx.lineTo(sx(w1), sy(b1));
    ctx.stroke();
    if (opts.loss != null) {
      ctx.fillStyle = "#334155";
      ctx.font = "12px sans-serif";
      ctx.fillText(`MSE ≈ ${fmt(opts.loss)}`, pad.l + 8, pad.t + 16);
    }
    if (hasParamBox) {
      const boxX = w - paramBoxW - 8;
      ctx.fillStyle = "#fff";
      ctx.fillRect(boxX, pad.t, paramBoxW, 72);
      ctx.strokeStyle = "#e2e8f0";
      ctx.strokeRect(boxX, pad.t, paramBoxW, 72);
      ctx.fillStyle = "#334155";
      ctx.font = "11px sans-serif";
      ctx.fillText(`w = ${fmt(opts.w, 3)}`, boxX + 10, pad.t + 18);
      ctx.fillText(`b = ${fmt(opts.b, 1)}`, boxX + 10, pad.t + 34);
      if (opts.eta != null) ctx.fillText(`η = ${opts.eta}`, boxX + 10, pad.t + 50);
      if (opts.step != null) ctx.fillText(`迭代 t = ${opts.step}`, boxX + 10, pad.t + 66);
    }
  }
}

function drawKMeans(ctx, w, h, points, centers, assign, opts = {}) {
  const pad = { l: 48, r: 18, t: 46, b: 38 };
  const colors = ["#0d6b62", "#c2410c"];
  const allCenters = [...centers, ...(opts.prevCenters || [])];
  const xs = [...points.map((p) => p[0]), ...allCenters.map((c) => c[0])];
  const ys = [...points.map((p) => p[1]), ...allCenters.map((c) => c[1])];
  const xGap = Math.max(6, (Math.max(...xs) - Math.min(...xs)) * 0.1);
  const yGap = Math.max(6, (Math.max(...ys) - Math.min(...ys)) * 0.1);
  const xMin = Math.max(0, Math.min(...xs) - xGap);
  const xMax = Math.min(100, Math.max(...xs) + xGap);
  const yMin = Math.max(0, Math.min(...ys) - yGap);
  const yMax = Math.min(100, Math.max(...ys) + yGap);
  const plotW = w - pad.l - pad.r;
  const plotH = h - pad.t - pad.b;
  const plotL = pad.l;
  const plotR = w - pad.r;
  const plotT = pad.t;
  const plotB = h - pad.b;
  const sx = (x) => pad.l + ((x - xMin) / (xMax - xMin || 1)) * plotW;
  const sy = (y) => h - pad.b - ((y - yMin) / (yMax - yMin || 1)) * plotH;
  const dx = (px) => xMin + ((px - pad.l) / (plotW || 1)) * (xMax - xMin);
  const dy = (py) => yMax - ((py - pad.t) / (plotH || 1)) * (yMax - yMin);
  const nearest = (x, y) =>
    centers
      .map(([cx, cy]) => (x - cx) ** 2 + (y - cy) ** 2)
      .reduce((best, d, i, arr) => (d < arr[best] ? i : best), 0);
  const changed = new Set(
    assign && opts.prevAssign ? assign.flatMap((c, i) => (opts.prevAssign[i] !== c ? [i] : [])) : [],
  );

  const drawArrow = (x0, y0, x1, y1, color) => {
    const a = Math.atan2(y1 - y0, x1 - x0);
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x1 - 7 * Math.cos(a - Math.PI / 6), y1 - 7 * Math.sin(a - Math.PI / 6));
    ctx.lineTo(x1 - 7 * Math.cos(a + Math.PI / 6), y1 - 7 * Math.sin(a + Math.PI / 6));
    ctx.closePath();
    ctx.fill();
  };

  const boundarySegment = () => {
    if (centers.length < 2) return null;
    const [a, b] = centers;
    const A = 2 * (b[0] - a[0]);
    const B = 2 * (b[1] - a[1]);
    const C = a[0] ** 2 + a[1] ** 2 - b[0] ** 2 - b[1] ** 2;
    const candidates = [];
    const add = (x, y) => {
      if (x < xMin - 1e-6 || x > xMax + 1e-6 || y < yMin - 1e-6 || y > yMax + 1e-6) return;
      if (candidates.some((p) => Math.hypot(p[0] - x, p[1] - y) < 1e-6)) return;
      candidates.push([x, y]);
    };
    if (Math.abs(B) > 1e-6) {
      add(xMin, -(A * xMin + C) / B);
      add(xMax, -(A * xMax + C) / B);
    }
    if (Math.abs(A) > 1e-6) {
      add(-(B * yMin + C) / A, yMin);
      add(-(B * yMax + C) / A, yMax);
    }
    if (candidates.length < 2) return null;
    return candidates.slice(0, 2);
  };

  ctx.fillStyle = "#f8fafc";
  ctx.fillRect(0, 0, w, h);

  ctx.save();
  ctx.rect(plotL, plotT, plotW, plotH);
  ctx.clip();
  for (let py = plotT; py < plotB; py += 8) {
    for (let px = plotL; px < plotR; px += 8) {
      const c = nearest(dx(px + 4), dy(py + 4));
      ctx.fillStyle = c === 0 ? "rgba(13,107,98,0.055)" : "rgba(194,65,12,0.05)";
      ctx.fillRect(px, py, 8.5, 8.5);
    }
  }
  ctx.restore();

  drawChartAxes(ctx, w, h, pad, "语文分", "数学分");

  const seg = boundarySegment();
  if (seg) {
    ctx.save();
    ctx.rect(plotL, plotT, plotW, plotH);
    ctx.clip();
    ctx.strokeStyle = "#94a3b8";
    ctx.lineWidth = 1.2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(sx(seg[0][0]), sy(seg[0][1]));
    ctx.lineTo(sx(seg[1][0]), sy(seg[1][1]));
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();
  }

  if (assign) {
    points.forEach(([x, y], i) => {
      const c = assign[i];
      ctx.strokeStyle = c === 0 ? "rgba(13,107,98,0.22)" : "rgba(194,65,12,0.22)";
      ctx.lineWidth = changed.has(i) ? 1.5 : 0.9;
      ctx.beginPath();
      ctx.moveTo(sx(x), sy(y));
      ctx.lineTo(sx(centers[c][0]), sy(centers[c][1]));
      ctx.stroke();
    });
  }

  if (opts.prevCenters) {
    centers.forEach(([x, y], i) => {
      const p = opts.prevCenters[i];
      if (!p) return;
      drawArrow(sx(p[0]), sy(p[1]), sx(x), sy(y), colors[i]);
    });
  }

  points.forEach(([x, y], i) => {
    const c = assign ? assign[i] : -1;
    ctx.fillStyle = c < 0 ? "#64748b" : colors[c];
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.arc(sx(x), sy(y), 4.3, 0, 7);
    ctx.fill();
    ctx.stroke();
    if (changed.has(i)) {
      ctx.strokeStyle = "#2563eb";
      ctx.lineWidth = 2.1;
      ctx.beginPath();
      ctx.arc(sx(x), sy(y), 8.2, 0, 7);
      ctx.stroke();
    }
  });

  centers.forEach(([x, y], i) => {
    const px = sx(x);
    const py = sy(y);
    ctx.fillStyle = "#fff";
    ctx.strokeStyle = colors[i];
    ctx.lineWidth = 2.4;
    ctx.beginPath();
    ctx.arc(px, py, 10.5, 0, 7);
    ctx.fill();
    ctx.stroke();
    ctx.strokeStyle = colors[i];
    ctx.lineWidth = 1.7;
    ctx.beginPath();
    ctx.moveTo(px - 6, py);
    ctx.lineTo(px + 6, py);
    ctx.moveTo(px, py - 6);
    ctx.lineTo(px, py + 6);
    ctx.stroke();
    ctx.fillStyle = colors[i];
    ctx.font = "bold 11px ui-sans-serif, system-ui, -apple-system, sans-serif";
    ctx.fillText(`C${i + 1}`, Math.min(plotR - 22, px + 12), Math.max(plotT + 12, py - 8));
  });

  const counts = assign ? [assign.filter((c) => c === 0).length, assign.filter((c) => c === 1).length] : [0, 0];
  const boxW = Math.min(w - 24, 360);
  ctx.fillStyle = "rgba(255,255,255,0.94)";
  ctx.strokeStyle = "#e2e8f0";
  ctx.lineWidth = 1;
  ctx.fillRect(12, 8, boxW, 30);
  ctx.strokeRect(12, 8, boxW, 30);
  ctx.font = "11px ui-sans-serif, system-ui, -apple-system, sans-serif";
  ctx.fillStyle = "#334155";
  const text =
    assign == null
      ? "初始化：灰点未分配，随机选择 C1 / C2"
      : `C1=${counts[0]} · C2=${counts[1]}${changed.size ? ` · 换簇 ${changed.size} 点` : ""}`;
  ctx.fillText(text, 24, 27);
}

function drawPerceptron(ctx, w, h, points, modelOrAngle, highlightWrong, opts = {}) {
  const statusH = 42;
  const pad = { l: 48, r: 22, t: statusH + 14, b: 36 };
  const xs = points.map((p) => p[0]);
  const ys = points.map((p) => p[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const xGap = Math.max(12, (maxX - minX) * 0.12);
  const yGap = Math.max(12, (maxY - minY) * 0.12);
  const xMin = Math.min(0, minX - xGap);
  const xMax = maxX + xGap;
  const yMin = Math.min(0, minY - yGap);
  const yMax = maxY + yGap;
  const plotW = w - pad.l - pad.r;
  const plotH = h - pad.t - pad.b;
  const sx = (x) => pad.l + ((x - xMin) / (xMax - xMin || 1)) * (w - pad.l - pad.r);
  const sy = (y) => h - pad.b - ((y - yMin) / (yMax - yMin || 1)) * (h - pad.t - pad.b);
  const dx = (px) => xMin + ((px - pad.l) / (plotW || 1)) * (xMax - xMin);
  const dy = (py) => yMax - ((py - pad.t) / (plotH || 1)) * (yMax - yMin);
  const dataMidX = (minX + maxX) / 2;
  const dataMidY = (minY + maxY) / 2;
  const model =
    modelOrAngle && typeof modelOrAngle === "object"
      ? modelOrAngle
      : (() => {
          const angle = Number(modelOrAngle) || 0;
          const wx = Math.cos(angle + Math.PI / 2);
          const wy = -Math.sin(angle + Math.PI / 2);
          return { wx, wy, b: -(wx * dataMidX + wy * dataMidY) };
        })();
  const score = ([x, y]) => model.wx * x + model.wy * y + model.b;
  const wrongSet = new Set(points.flatMap((p, i) => (p[2] * score(p) <= 0 ? [i] : [])));
  const wrongCount = wrongSet.size;
  const plotL = pad.l;
  const plotR = w - pad.r;
  const plotT = pad.t;
  const plotB = h - pad.b;

  const boundarySegment = (m) => {
    const candidates = [];
    const add = (x, y) => {
      if (x < xMin - 1e-6 || x > xMax + 1e-6 || y < yMin - 1e-6 || y > yMax + 1e-6) return;
      if (candidates.some((p) => Math.hypot(p[0] - x, p[1] - y) < 1e-6)) return;
      candidates.push([x, y]);
    };
    if (Math.abs(m.wy) > 1e-6) {
      add(xMin, -(m.wx * xMin + m.b) / m.wy);
      add(xMax, -(m.wx * xMax + m.b) / m.wy);
    }
    if (Math.abs(m.wx) > 1e-6) {
      add(-(m.wy * yMin + m.b) / m.wx, yMin);
      add(-(m.wy * yMax + m.b) / m.wx, yMax);
    }
    if (candidates.length < 2) return null;
    let best = [candidates[0], candidates[1]];
    let bestD = -1;
    for (let i = 0; i < candidates.length; i++) {
      for (let j = i + 1; j < candidates.length; j++) {
        const d = Math.hypot(sx(candidates[i][0]) - sx(candidates[j][0]), sy(candidates[i][1]) - sy(candidates[j][1]));
        if (d > bestD) {
          bestD = d;
          best = [candidates[i], candidates[j]];
        }
      }
    }
    return best;
  };

  const drawLine = (m, color, width, dash = []) => {
    const seg = boundarySegment(m);
    if (!seg) return null;
    ctx.save();
    ctx.rect(plotL, plotT, plotW, plotH);
    ctx.clip();
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.setLineDash(dash);
    ctx.beginPath();
    ctx.moveTo(sx(seg[0][0]), sy(seg[0][1]));
    ctx.lineTo(sx(seg[1][0]), sy(seg[1][1]));
    ctx.stroke();
    ctx.restore();
    ctx.setLineDash([]);
    return seg;
  };

  const drawArrow = (x0, y0, x1, y1, color) => {
    const angle = Math.atan2(y1 - y0, x1 - x0);
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 1.7;
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x1 - 8 * Math.cos(angle - Math.PI / 6), y1 - 8 * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(x1 - 8 * Math.cos(angle + Math.PI / 6), y1 - 8 * Math.sin(angle + Math.PI / 6));
    ctx.closePath();
    ctx.fill();
  };

  ctx.fillStyle = "#f8fafc";
  ctx.fillRect(0, 0, w, h);

  ctx.save();
  ctx.rect(plotL, plotT, plotW, plotH);
  ctx.clip();
  const cell = 8;
  for (let py = plotT; py < plotB; py += cell) {
    for (let px = plotL; px < plotR; px += cell) {
      const s = model.wx * dx(px + cell / 2) + model.wy * dy(py + cell / 2) + model.b;
      ctx.fillStyle = s >= 0 ? "rgba(13, 107, 98, 0.055)" : "rgba(194, 65, 12, 0.05)";
      ctx.fillRect(px, py, cell + 0.5, cell + 0.5);
    }
  }
  ctx.restore();

  drawChartAxes(ctx, w, h, pad, opts.xLabel || "语文分", opts.yLabel || "数学分");

  if (opts.prevModel) drawLine(opts.prevModel, "#94a3b8", 1.4, [5, 5]);
  const currentSeg = drawLine(model, "#1d4ed8", 2.6);

  points.forEach(([x, y, label], i) => {
    const px = sx(x);
    const py = sy(y);
    const wrong = wrongSet.size ? wrongSet.has(i) : highlightWrong === label;
    ctx.fillStyle = label > 0 ? "#0d6b62" : "#c2410c";
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(px, py, 4.6, 0, 7);
    ctx.fill();
    ctx.stroke();
    if (wrong) {
      ctx.strokeStyle = "#2563eb";
      ctx.lineWidth = 2.1;
      ctx.beginPath();
      ctx.arc(px, py, 8.4, 0, 7);
      ctx.stroke();
    }
  });

  if (currentSeg) {
    const m0 = currentSeg[0];
    const m1 = currentSeg[1];
    const mx = (m0[0] + m1[0]) / 2;
    const my = (m0[1] + m1[1]) / 2;
    const norm = Math.hypot(model.wx, model.wy) || 1;
    const arrowScale = Math.min(xMax - xMin, yMax - yMin) * 0.16;
    const ax0 = sx(mx);
    const ay0 = sy(my);
    const ax1 = sx(mx + (model.wx / norm) * arrowScale);
    const ay1 = sy(my + (model.wy / norm) * arrowScale);
    drawArrow(ax0, ay0, ax1, ay1, "#334155");
    ctx.fillStyle = "#334155";
    ctx.font = "bold 11px ui-sans-serif, system-ui, -apple-system, sans-serif";
    ctx.fillText("w", ax1 + 5, ay1 - 4);
    ctx.save();
    ctx.translate(sx(mx) + 8, sy(my) - 7);
    ctx.fillStyle = "rgba(255,255,255,0.86)";
    ctx.fillRect(-4, -12, 64, 16);
    ctx.fillStyle = "#1d4ed8";
    ctx.font = "10px ui-sans-serif, system-ui, -apple-system, sans-serif";
    ctx.fillText("w·x+b=0", 0, 0);
    ctx.restore();
  }

  const norm = Math.hypot(model.wx, model.wy) || 1;
  const nx = model.wx / norm;
  const ny = model.wy / norm;
  const slope = Math.abs(model.wy) > 1e-6 ? -model.wx / model.wy : null;
  const intercept = Math.abs(model.wy) > 1e-6 ? -model.b / model.wy : null;

  ctx.fillStyle = "#fff";
  ctx.strokeStyle = "#e2e8f0";
  ctx.lineWidth = 1;
  const boxW = Math.min(322, w - 36);
  ctx.fillRect(18, 8, boxW, statusH);
  ctx.strokeRect(18, 8, boxW, statusH);
  ctx.fillStyle = "#334155";
  ctx.font = "11px ui-sans-serif, system-ui, -apple-system, sans-serif";
  ctx.textBaseline = "top";
  const boundaryText = slope == null ? `x = ${fmt(-model.b / model.wx, 1)}` : `y = ${fmt(slope, 2)}x + ${fmt(intercept, 1)}`;
  ctx.fillText(`${boundaryText} · w≈[${fmt(nx, 2)}, ${fmt(ny, 2)}]`, 30, 15);
  if (opts.converged || wrongCount === 0) ctx.fillText("全部分对 · 收敛", 30, 32);
  else ctx.fillText(`错分 ${wrongCount} 点 → 触发更新`, 30, 32);

  if (w > 520) {
    const lx = boxW - 68;
    ctx.fillStyle = "#0d6b62";
    ctx.beginPath();
    ctx.arc(lx, 35, 4, 0, 7);
    ctx.fill();
    ctx.fillStyle = "#334155";
    ctx.fillText("+1", lx + 8, 29);
    ctx.fillStyle = "#c2410c";
    ctx.beginPath();
    ctx.arc(lx + 42, 35, 4, 0, 7);
    ctx.fill();
    ctx.fillStyle = "#334155";
    ctx.fillText("-1", lx + 50, 29);
  }
  ctx.textBaseline = "alphabetic";
}

const CONV_KERNEL_3 = [
  [1, 0.5, 0],
  [0.5, 1, 0.5],
  [0, 0.5, 1],
];

function convOutputAt(input, kr, kc) {
  let sum = 0;
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      sum += input[kr + i][kc + j] * CONV_KERNEL_3[i][j];
    }
  }
  return Math.max(0, sum * 0.35);
}

function convProgressFromKPos(kPos) {
  if (!kPos) return 0;
  const map = { "0,0": 1, "0,1": 2, "1,0": 3, "1,1": 4 };
  return map[`${kPos[0]},${kPos[1]}`] ?? 0;
}

function drawConvGrid(ctx, w, h, gridSize, kernelSize, kPos, phase) {
  ctx.fillStyle = "#f8fafc";
  ctx.fillRect(0, 0, w, h);

  const convProgress = phase === "conv" ? convProgressFromKPos(kPos) : phase === "pool" ? 4 : 0;
  const showFeature = convProgress > 0 || phase === "pool";
  const showPool = phase === "pool";
  const cell = Math.max(18, Math.min(72, (h - 82) / gridSize, (w - 160) / (gridSize + 3.8)));
  const fcell = cell * 0.92;
  const poolCell = cell * 1.08;
  const gap = Math.max(30, Math.min(64, cell * 0.88));
  const contentBottom = h - 58;
  const inputSize = gridSize * cell;
  const featSize = 2 * fcell;
  const totalW = inputSize + gap + featSize + gap + poolCell;
  const ox = Math.max(24, (w - totalW) / 2);
  const oy = Math.max(20, Math.min((contentBottom - inputSize) / 2, contentBottom - inputSize - 8));
  const featOx = ox + inputSize + gap;
  const featOy = oy + (inputSize - featSize) / 2;
  const poolOx = featOx + featSize + gap;
  const poolOy = oy + (inputSize - poolCell) / 2;

  const drawArrow = (x1, y, x2, active) => {
    const color = active ? "#0d6b62" : "#cbd5e1";
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x1, y);
    ctx.lineTo(x2, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x2, y);
    ctx.lineTo(x2 - 7, y - 4);
    ctx.lineTo(x2 - 7, y + 4);
    ctx.closePath();
    ctx.fill();
  };

  const drawGrid = (x, y, size, values, color, title, caption = "") => {
    ctx.fillStyle = "#64748b";
    ctx.font = "12px ui-sans-serif, system-ui, sans-serif";
    ctx.fillText(title, x, y - 10);
    values.forEach((row, i) => {
      row.forEach((v, j) => {
        ctx.fillStyle = color(v);
        ctx.fillRect(x + j * size, y + i * size, size - 3, size - 3);
        ctx.strokeStyle = "rgba(15,23,42,0.08)";
        ctx.strokeRect(x + j * size, y + i * size, size - 3, size - 3);
        if (size >= 24) {
          ctx.fillStyle = "#334155";
          ctx.font = `${Math.max(9, Math.min(12, size * 0.26))}px ui-monospace, monospace`;
          ctx.fillText(v.toFixed(2), x + j * size + size * 0.15, y + i * size + size * 0.58);
        }
      });
    });
    if (caption) {
      ctx.fillStyle = "#94a3b8";
      ctx.font = "10px ui-sans-serif, system-ui, sans-serif";
      ctx.fillText(caption, x, y + values.length * size + 14);
    }
  };

  const drawGhostGrid = (x, y, size, rows, cols, title, caption = "") => {
    ctx.fillStyle = "#94a3b8";
    ctx.font = "12px ui-sans-serif, system-ui, sans-serif";
    ctx.fillText(title, x, y - 10);
    ctx.save();
    ctx.setLineDash([5, 4]);
    for (let i = 0; i < rows; i++) {
      for (let j = 0; j < cols; j++) {
        ctx.fillStyle = "#f1f5f9";
        ctx.fillRect(x + j * size, y + i * size, size - 3, size - 3);
        ctx.strokeStyle = "#cbd5e1";
        ctx.strokeRect(x + j * size, y + i * size, size - 3, size - 3);
      }
    }
    ctx.restore();
    if (caption) {
      ctx.fillStyle = "#94a3b8";
      ctx.font = "10px ui-sans-serif, system-ui, sans-serif";
      ctx.fillText(caption, x, y + rows * size + 14);
    }
  };

  const inputValues = Array.from({ length: gridSize }, (_, i) =>
    Array.from({ length: gridSize }, (_, j) => 0.15 + (i + j) / (gridSize * 2)),
  );

  const featOrder = [
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1],
  ];
  const featValues = featOrder.map(([r, c]) => convOutputAt(inputValues, r, c));

  drawGrid(
    ox,
    oy,
    cell,
    inputValues,
    (v) => `rgba(13,107,98,${0.14 + v * 0.58})`,
    `${gridSize}×${gridSize} 输入`,
    phase === "in" ? "原始像素" : "",
  );

  if (phase === "conv" && kPos) {
    ctx.strokeStyle = "#c2410c";
    ctx.lineWidth = 3;
    ctx.strokeRect(ox + kPos[1] * cell, oy + kPos[0] * cell, kernelSize * cell - 3, kernelSize * cell - 3);
  }

  if (showFeature) {
    drawArrow(ox + inputSize + 8, oy + inputSize / 2, featOx - 10, true);
    ctx.fillStyle = "#64748b";
    ctx.font = "12px ui-sans-serif, system-ui, sans-serif";
    ctx.fillText("2×2 特征图", featOx, featOy - 10);
    for (let fi = 0; fi < 4; fi++) {
      const fr = Math.floor(fi / 2);
      const fc = fi % 2;
      const filled = convProgress >= fi + 1;
      const fx = featOx + fc * fcell;
      const fy = featOy + fr * fcell;
      if (filled) {
        const v = featValues[fi];
        ctx.fillStyle = `rgba(37,99,235,${0.2 + v * 0.65})`;
        ctx.fillRect(fx, fy, fcell - 3, fcell - 3);
        ctx.strokeStyle = fi + 1 === convProgress && phase === "conv" ? "#c2410c" : "rgba(15,23,42,0.08)";
        ctx.lineWidth = fi + 1 === convProgress && phase === "conv" ? 2.5 : 1;
        ctx.strokeRect(fx, fy, fcell - 3, fcell - 3);
        ctx.fillStyle = "#334155";
        ctx.font = `${Math.max(9, Math.min(12, fcell * 0.26))}px ui-monospace, monospace`;
        ctx.fillText(v.toFixed(2), fx + fcell * 0.15, fy + fcell * 0.58);
      } else {
        ctx.save();
        ctx.setLineDash([5, 4]);
        ctx.fillStyle = "#f1f5f9";
        ctx.fillRect(fx, fy, fcell - 3, fcell - 3);
        ctx.strokeStyle = "#cbd5e1";
        ctx.strokeRect(fx, fy, fcell - 3, fcell - 3);
        ctx.restore();
      }
    }
  } else {
    drawArrow(ox + inputSize + 8, oy + inputSize / 2, featOx - 10, phase === "conv");
    drawGhostGrid(featOx, featOy, fcell, 2, 2, "2×2 特征图", "");
  }

  if (showPool) {
    drawArrow(featOx + featSize + 8, oy + inputSize / 2, poolOx - 10, true);
    const poolVal = Math.max(...featValues);
    drawGrid(
      poolOx,
      poolOy,
      poolCell,
      [[poolVal]],
      (v) => `rgba(37,99,235,${0.24 + v * 0.65})`,
      "1×1 池化后",
      "",
    );
  } else {
    drawArrow(featOx + featSize + 8, oy + inputSize / 2, poolOx - 10, false);
    drawGhostGrid(poolOx, poolOy, poolCell, 1, 1, "1×1 池化后", "");
  }

  ctx.fillStyle = "#f1f5f9";
  ctx.fillRect(0, contentBottom, w, h - contentBottom);
  ctx.strokeStyle = "#e2e8f0";
  ctx.beginPath();
  ctx.moveTo(0, contentBottom);
  ctx.lineTo(w, contentBottom);
  ctx.stroke();
  ctx.fillStyle = "#334155";
  ctx.font = "11px ui-sans-serif, system-ui, sans-serif";
  let status = "";
  if (phase === "in") status = "准备：3×3 卷积核从左到右、从上到下扫描";
  else if (phase === "conv" && kPos) {
    const curIdx = convProgress;
    const fr = Math.floor((curIdx - 1) / 2);
    const fc = (curIdx - 1) % 2;
    status = `kernel(${kPos[0]},${kPos[1]}) → 特征图[${fr},${fc}] = ${featValues[curIdx - 1].toFixed(2)} · 已填 ${convProgress}/4`;
  } else if (phase === "pool") {
    status = `MaxPool 2×2 → 1×1，max = ${Math.max(...featValues).toFixed(2)}`;
  }
  if (status) {
    const maxW = w - ox - 16;
    if (ctx.measureText(status).width <= maxW) {
      ctx.fillText(status, ox, h - 22);
    } else {
      const line2 = phase === "conv" ? `已填 ${convProgress}/4 格` : "";
      const line1 = line2 ? status.replace(` · ${line2}`, "") : status;
      ctx.fillText(line1, ox, h - 36);
      if (line2) ctx.fillText(line2, ox, h - 20);
    }
  }
}

function renderStateFlow(container, states, current, rewards = []) {
  container.innerHTML = `<div class="state-flow">${states
    .map((s, i) => {
      const cls = i === current ? "is-current" : i < current ? "is-done" : "";
      const r = rewards[i] != null ? `<span class="state-reward">+${rewards[i]}</span>` : "";
      return `<div class="state-node ${cls}"><span class="state-num">${i}</span><span class="state-label">${s}</span>${r}</div>${i < states.length - 1 ? '<span class="state-arrow">→</span>' : ""}`;
    })
    .join("")}</div>`;
}

function renderMCTSTree(container, step) {
  const phase = step.phase;
  const base = [
    { id: "root", label: "根", n: 10, q: 5, x: 260, y: 28 },
    { id: "a", label: "a", n: 6, q: 3, parent: "root", x: 120, y: 96 },
    { id: "b", label: "b", n: 4, q: 2, parent: "root", x: 400, y: 96 },
    { id: "c", label: "c", n: 0, q: 0, parent: "b", isNew: true, x: 400, y: 168 },
  ];
  const nodes =
    phase === "backup"
      ? [
          { id: "root", label: "根", n: 11, q: 5.62, x: 260, y: 28 },
          { id: "a", label: "a", n: 6, q: 3, parent: "root", x: 120, y: 96 },
          { id: "b", label: "b", n: 5, q: 2.62, parent: "root", x: 400, y: 96, delta: "+1N +0.62Q" },
          { id: "c", label: "c", n: 1, q: 0.62, parent: "b", x: 400, y: 168, delta: "新叶 +1N" },
        ]
      : base.map((n) => ({ ...n }));
  const active = step.active || "root";
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
  const edges = nodes
    .filter((n) => n.parent && byId[n.parent])
    .map((n) => {
      const p = byId[n.parent];
      return `<line class="mcts-edge ${n.id === active || p.id === active ? "is-active" : ""}" x1="${p.x}" y1="${p.y + 18}" x2="${n.x}" y2="${n.y - 18}"/>`;
    })
    .join("");
  const nodeSvg = nodes
    .map((n) => {
      const wr = n.n ? fmt(n.q / n.n, 2) : "—";
      const cls = [n.id === active ? "is-active" : "", n.isNew ? "is-new" : ""].filter(Boolean).join(" ");
      return `<g class="mcts-node-svg ${cls}" transform="translate(${n.x},${n.y})">
        <rect class="mcts-node-box" x="-56" y="-22" width="112" height="44" rx="8"/>
        <text class="mcts-node-label" y="-6">${n.label}</text>
        <text class="mcts-node-meta" y="9">N=${n.n}  Q/N=${wr}</text>
        ${n.delta ? `<text class="mcts-node-delta" y="23">${n.delta}</text>` : ""}
      </g>`;
    })
    .join("");
  container.innerHTML = `
    <svg class="mcts-svg" viewBox="0 0 520 200" role="img" aria-label="MCTS 搜索树">
      ${edges}${nodeSvg}
    </svg>`;
}

function activationPath(fn, toX, toY, samples = 160) {
  const pts = [];
  for (let i = 0; i <= samples; i++) {
    const t = i / samples;
    const x = -4 + t * 8;
    pts.push(`${toX(x).toFixed(1)},${toY(fn(x)).toFixed(1)}`);
  }
  return `M ${pts.join(" L ")}`;
}

function renderActivationCurves(container, highlight = null) {
  const fns = [
    { name: "Sigmoid", fn: (x) => 1 / (1 + Math.exp(-x)), color: "#0d6b62", id: "sigmoid" },
    { name: "ReLU", fn: (x) => Math.max(0, x), color: "#c2410c", id: "relu" },
    { name: "Tanh", fn: (x) => Math.tanh(x), color: "#2563eb", id: "tanh" },
  ];
  const W = 560;
  const H = 280;
  const pad = { l: 48, r: 24, t: 32, b: 40 };
  const plotW = W - pad.l - pad.r;
  const plotH = H - pad.t - pad.b;
  const xMin = -4;
  const xMax = 4;
  const yMin = -1.2;
  const yMax = 1.2;
  const toX = (x) => pad.l + ((x - xMin) / (xMax - xMin)) * plotW;
  const toY = (y) => pad.t + (1 - (y - yMin) / (yMax - yMin)) * plotH;
  const show = highlight ? fns.filter((f) => f.id === highlight) : fns;
  const grid = [];
  for (let x = -4; x <= 4; x += 2) {
    grid.push(`<line x1="${toX(x)}" y1="${pad.t}" x2="${toX(x)}" y2="${H - pad.b}" class="act-grid"/>`);
    grid.push(`<text x="${toX(x)}" y="${H - 14}" text-anchor="middle" class="act-tick">${x}</text>`);
  }
  for (let y = -1; y <= 1; y += 1) {
    grid.push(`<line x1="${pad.l}" y1="${toY(y)}" x2="${W - pad.r}" y2="${toY(y)}" class="act-grid"/>`);
    grid.push(`<text x="${pad.l - 8}" y="${toY(y) + 4}" text-anchor="end" class="act-tick">${y}</text>`);
  }
  const curves = show
    .map(({ name, fn, color, id }) => {
      const active = highlight === id;
      return `<path class="act-curve ${active ? "is-active" : ""}" d="${activationPath(fn, toX, toY)}" stroke="${color}" stroke-width="${active ? 3 : 2.25}" fill="none"/>`;
    })
    .join("");
  const legend = show
    .map(({ name, color, id }, i) => {
      const active = highlight === id;
      return `<g transform="translate(${W - 128}, ${40 + i * 24})"><rect width="16" height="4" y="-2" fill="${color}" rx="2"/><text class="act-legend ${active ? "is-active" : ""}" x="22" y="4">${name}${active ? " ← 本步" : ""}</text></g>`;
    })
    .join("");
  container.innerHTML = `
    <div class="activation-chart-wrap">
      <svg class="activation-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="激活函数曲线">
        <rect width="${W}" height="${H}" fill="#f8fafc"/>
        ${grid.join("")}
        <line x1="${pad.l}" y1="${toY(0)}" x2="${W - pad.r}" y2="${toY(0)}" class="act-axis"/>
        <line x1="${toX(0)}" y1="${pad.t}" x2="${toX(0)}" y2="${H - pad.b}" class="act-axis"/>
        ${curves}
        ${legend}
        <text x="${W / 2}" y="${H - 2}" text-anchor="middle" class="act-axis-label">x</text>
        <text x="14" y="${H / 2}" text-anchor="middle" class="act-axis-label" transform="rotate(-90 14 ${H / 2})">f(x)</text>
      </svg>
    </div>`;
}

function renderXorDemo(container) {
  const pts = [[0, 0, -1], [0, 1, 1], [1, 0, 1], [1, 1, -1]];
  const panel = (title, mode, ox) => {
    const pw = 264;
    const ph = 230;
    const plotX = ox + 46;
    const plotY = 82;
    const plotW = 178;
    const plotH = 112;
    const pointInset = 15;
    const edgeX = (x) => plotX + x * plotW;
    const edgeY = (y) => plotY + (1 - y) * plotH;
    const sx = (x) => plotX + pointInset + x * (plotW - pointInset * 2);
    const sy = (y) => plotY + pointInset + (1 - y) * (plotH - pointInset * 2);
    const pointLabel = (x, y, label) => {
      const anchor = x === 0 ? "start" : "end";
      const dx = x === 0 ? 13 : -13;
      const dy = 4;
      return `<text x="${sx(x) + dx}" y="${sy(y) + dy}" text-anchor="${anchor}" class="xor-point-label">(${x},${y}) y=${label > 0 ? 1 : 0}</text>`;
    };
    const dots = pts
      .map(([x, y, label]) => {
        const fill = label > 0 ? "#0d6b62" : "#c2410c";
        return `${pointLabel(x, y, label)}<circle cx="${sx(x)}" cy="${sy(y)}" r="6" fill="${fill}" class="xor-dot"/>`;
      })
      .join("");
    const grid = `
      <rect x="${plotX}" y="${plotY}" width="${plotW}" height="${plotH}" class="xor-plot"/>
      <line x1="${edgeX(0.5)}" y1="${plotY}" x2="${edgeX(0.5)}" y2="${plotY + plotH}" class="xor-grid"/>
      <line x1="${plotX}" y1="${edgeY(0.5)}" x2="${plotX + plotW}" y2="${edgeY(0.5)}" class="xor-grid"/>
      <line x1="${plotX}" y1="${plotY + plotH}" x2="${plotX + plotW + 10}" y2="${plotY + plotH}" class="xor-axis"/>
      <line x1="${plotX}" y1="${plotY + plotH}" x2="${plotX}" y2="${plotY - 10}" class="xor-axis"/>
      <text x="${plotX + plotW + 14}" y="${plotY + plotH + 4}" class="xor-axis-text">x₁</text>
      <text x="${plotX - 14}" y="${plotY + 6}" text-anchor="end" class="xor-axis-text">x₂</text>`;
    const boundary =
      mode === "linear"
        ? `<line x1="${edgeX(0)}" y1="${edgeY(0.76)}" x2="${edgeX(1)}" y2="${edgeY(0.24)}" class="xor-boundary xor-fail" stroke-dasharray="6 4"/>
           <text x="${edgeX(0.55)}" y="${edgeY(0.74)}" text-anchor="middle" class="xor-boundary-label is-fail">单条边界失败</text>`
        : `<polygon points="${edgeX(0)},${edgeY(0.55)} ${edgeX(0)},${edgeY(1)} ${edgeX(0.45)},${edgeY(1)} ${edgeX(1)},${edgeY(0.45)} ${edgeX(1)},${edgeY(0)} ${edgeX(0.55)},${edgeY(0)}" class="xor-band"/>
           <line x1="${edgeX(0)}" y1="${edgeY(0.55)}" x2="${edgeX(0.55)}" y2="${edgeY(0)}" class="xor-boundary xor-ok"/>
           <line x1="${edgeX(0.45)}" y1="${edgeY(1)}" x2="${edgeX(1)}" y2="${edgeY(0.45)}" class="xor-boundary xor-ok"/>
           <text x="${edgeX(0.5)}" y="${edgeY(0.52)}" text-anchor="middle" class="xor-boundary-label is-ok">两条边界组合</text>`;
    const subtitle = mode === "linear" ? "只有一个半平面，无法隔开交错标签" : "隐藏层组合多个半平面，得到非线性区域";
    const verdict = mode === "linear" ? "结论：单层线性模型不够" : "结论：加入激活后可分";
    return `<g>
      <rect x="${ox}" y="20" width="${pw}" height="${ph}" rx="10" class="xor-panel"/>
      <text x="${ox + 14}" y="42" class="xor-title">${title}</text>
      <text x="${ox + 14}" y="60" class="xor-subtitle">${subtitle}</text>
      ${grid}${boundary}${dots}
      <rect x="${ox + 12}" y="${20 + ph - 30}" width="${pw - 24}" height="22" rx="11" class="xor-footer ${mode === "linear" ? "is-fail" : "is-ok"}"/>
      <text x="${ox + 24}" y="${20 + ph - 15}" class="xor-verdict ${mode === "linear" ? "is-fail" : "is-ok"}">${verdict}</text>
    </g>`;
  };
  container.innerHTML = `
    <div class="xor-demo-wrap">
      <svg class="xor-svg" viewBox="0 0 560 270" role="img" aria-label="XOR 线性 vs 非线性">
        ${panel("单层线性", "linear", 12)}
        ${panel("含 ReLU 隐藏层", "mlp", 284)}
      </svg>
    </div>`;
}

function drawActivationCurves(ctx, w, h, highlight = null) {
  const fns = [
    { name: "Sigmoid", fn: (x) => 1 / (1 + Math.exp(-x)), color: "#0d6b62", id: "sigmoid" },
    { name: "ReLU", fn: (x) => Math.max(0, x), color: "#c2410c", id: "relu" },
    { name: "Tanh", fn: (x) => Math.tanh(x), color: "#2563eb", id: "tanh" },
  ];
  ctx.fillStyle = "#f8fafc";
  ctx.fillRect(0, 0, w, h);
  drawChartAxes(ctx, w, h, { l: 40, r: 16, t: 16, b: 36 }, "x", "σ(x)");
  fns.forEach(({ name, fn, color, id }) => {
    const dim = highlight && highlight !== id;
    ctx.strokeStyle = color;
    ctx.globalAlpha = dim ? 0.25 : 1;
    ctx.lineWidth = highlight === id ? 3 : 2;
    ctx.beginPath();
    for (let px = 0; px <= w - 56; px++) {
      const x = (px / (w - 56)) * 8 - 4;
      const y = fn(x);
      const cx = 40 + px;
      const cy = h - 36 - ((y + 0.2) / 2.2) * (h - 60);
      if (px === 0) ctx.moveTo(cx, cy);
      else ctx.lineTo(cx, cy);
    }
    ctx.stroke();
    ctx.globalAlpha = 1;
    ctx.fillStyle = color;
    ctx.fillText(name + (highlight === id ? " ← 本步" : ""), w - 120, 24 + fns.findIndex((f) => f.id === id) * 16);
  });
}

function renderMLPBackward(container, step) {
  const phase = step.phase ?? 0;
  const layers = [
    { name: "输入", nodes: ["x₁", "x₂"], values: ["6.2", "0.8"] },
    { name: "隐藏 ReLU", nodes: ["h₁", "h₂"], values: ["0.71", "0.45"] },
    { name: "输出 σ", nodes: ["ŷ"], values: ["0.82"] },
  ];
  const gradOn = phase >= 0 ? [2] : [];
  const gradMid = phase >= 1 ? [1] : [];
  const xFor = (li) => 70 + li * 180;
  const yFor = (ns, ni) => 112 + (ni - (ns - 1) / 2) * 78;
  const nodeMarkup = layers.map((layer, li) => {
    const x = xFor(li);
    const ns = layer.nodes.length;
    return layer.nodes.map((n, ni) => {
      const y = yFor(ns, ni);
      const hasGrad = (gradOn.includes(li) || gradMid.includes(li)) && phase < 2;
      const cur = (phase === 0 && li === 2) || (phase === 1 && li === 1) || phase === 2;
      return `<g class="mlp-node is-on ${cur ? "is-current" : ""} ${hasGrad ? "has-grad" : ""}" transform="translate(${x},${y})">
        <circle r="22"></circle><text dy="4">${n}</text>
        <text class="mlp-val" y="38">${layer.values[ni]}</text>
        ${hasGrad ? `<text class="mlp-grad" y="-30">δ</text>` : ""}
      </g>`;
    }).join("");
  }).join("");
  container.innerHTML = `
    <svg class="mlp-svg mlp-backward" viewBox="0 0 520 240" role="img" aria-label="反向传播">
      ${phase < 2 ? `<path class="grad-flow" d="M 410 92 C 356 34, 302 34, 254 52" marker-end="url(#grad-arrow)"></path>` : ""}
      ${nodeMarkup}
      ${phase === 2 ? `<text x="260" y="216" text-anchor="middle" class="mlp-layer-label">W_h ← W_h − 0.01·δ_h·aᵀ · W_out ← W_out − 0.01·δ_out·hᵀ</text>` : ""}
      <defs><marker id="grad-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#c2410c"></path></marker></defs>
    </svg>`;
}

function renderTransE(container, step) {
  const hLabel = step.hLabel || "鲁迅";
  const rLabel = step.rLabel || "创作";
  const tLabel = step.tLabel || "呐喊";
  const negLabel = step.negLabel || "红楼梦";
  const kind = step.kind || "init";
  const uid = `transe-${++transeMarkerUid}`;
  const phaseLines = {
    init: ["向量平移假设", "h + r 应靠近正确尾实体 t"],
    pos: ["正例训练", "把预测点 h+r 拉向 t"],
    neg: ["负例训练", "把错误尾实体 t′ 推离 h+r"],
    update: ["Margin 更新", "让 d⁺ 比 d⁻ 至少小 margin"],
  };
  const [titleLine1, titleLine2] = phaseLines[kind] || phaseLines.init;
  const states = {
    init: { pred: [188, 192], tail: [282, 192], neg: [318, 244], dPos: 0.84, dNeg: 1.36, loss: 0.48 },
    pos: { pred: [248, 192], tail: [282, 192], neg: [318, 244], dPos: 0.31, dNeg: 1.62, loss: 0 },
    neg: { pred: [248, 192], tail: [282, 192], neg: [318, 244], dPos: 0.31, dNeg: 2.08, loss: 0 },
    update: { pred: [254, 192], tail: [282, 192], neg: [322, 246], dPos: 0.28, dNeg: 2.08, loss: 0 },
  };
  const state = states[kind] || states.init;
  const head = [82, 192];
  const relEnd = state.pred;
  const axisY = 240;
  const distY = 258;
  const dist = step.dist ?? (kind === "neg" ? state.dNeg : kind === "init" ? null : state.dPos);
  const lossValue = fmt(Math.max(0, 1 + state.dPos - state.dNeg), 2);
  const stepNum = { init: "1", pos: "2", neg: "3", update: "4" }[kind] || "1";

  const chip = (x, y, w, label, value, cls = "") => `
    <g class="transe-chip ${cls}" transform="translate(${x},${y})">
      <rect width="${w}" height="34" rx="8"></rect>
      <text class="transe-chip-label" x="10" y="13">${label}</text>
      <text class="transe-chip-value" x="10" y="27">${value}</text>
    </g>`;
  const point = (x, y, label, cls, sub = "", subSide = "right") => {
    const subX = subSide === "right" ? 22 : -22;
    const anchor = subSide === "right" ? "start" : "end";
    return `
    <g class="transe-point ${cls}" transform="translate(${x},${y})">
      <circle r="16"></circle>
      <text class="transe-point-label" y="4" text-anchor="middle">${label}</text>
      ${sub ? `<text class="transe-point-sub" x="${subX}" y="4" text-anchor="${anchor}">${sub}</text>` : ""}
    </g>`;
  };
  const metricRow = (y, label, value, cls = "") => `
    <g class="transe-metric ${cls}" transform="translate(32,${y})">
      <text class="transe-metric-label" x="0" y="0">${label}</text>
      <text class="transe-metric-value" x="126" y="0">${value}</text>
    </g>`;
  const bracket = (x1, x2, y, label, cls) => {
    const mid = (x1 + x2) / 2;
    return `
      <line class="transe-bracket ${cls}" x1="${x1}" y1="${y - 10}" x2="${x1}" y2="${y}"></line>
      <line class="transe-bracket ${cls}" x1="${x2}" y1="${y - 10}" x2="${x2}" y2="${y}"></line>
      <line class="transe-distance ${cls}" x1="${x1}" y1="${y}" x2="${x2}" y2="${y}"></line>
      <text class="transe-distance-label ${cls}" x="${mid}" y="${y + 16}" text-anchor="middle">${label}</text>`;
  };

  const posDistanceLine =
    kind === "init" || kind === "pos" || kind === "update"
      ? `${bracket(state.pred[0], state.tail[0], distY, `d⁺=${fmt(state.dPos, 2)}`, "is-pos")}
         <line class="transe-drop" x1="${state.pred[0]}" y1="${state.pred[1] + 18}" x2="${state.pred[0]}" y2="${distY - 10}"></line>
         <line class="transe-drop" x1="${state.tail[0]}" y1="${state.tail[1] + 18}" x2="${state.tail[0]}" y2="${distY - 10}"></line>`
      : "";
  const negDistanceLine =
    kind === "neg" || kind === "update"
      ? `${bracket(state.pred[0], state.neg[0], distY + 18, `d⁻=${fmt(state.dNeg, 2)}`, "is-neg")}
         <line class="transe-drop is-neg" x1="${state.pred[0]}" y1="${state.pred[1] + 18}" x2="${state.pred[0]}" y2="${distY + 8}"></line>
         <line class="transe-drop is-neg" x1="${state.neg[0]}" y1="${state.neg[1] + 18}" x2="${state.neg[0]}" y2="${distY + 8}"></line>`
      : "";
  const pullArrow =
    kind === "pos"
      ? `<line class="transe-action is-pos" x1="${state.tail[0] + 28}" y1="${state.tail[1] - 30}" x2="${state.tail[0] + 6}" y2="${state.tail[1] - 8}" marker-end="url(#${uid}-pos)"></line>
         <text class="transe-action-label is-pos" x="${state.tail[0] + 34}" y="${state.tail[1] - 34}">拉近 t</text>`
      : "";
  const pushArrow =
    kind === "neg"
      ? `<line class="transe-action is-neg" x1="${state.neg[0] - 30}" y1="${state.neg[1] + 10}" x2="${state.neg[0] - 8}" y2="${state.neg[1] - 4}" marker-end="url(#${uid}-neg)"></line>
         <text class="transe-action-label is-neg" x="${state.neg[0] - 88}" y="${state.neg[1] + 22}">推远 t′</text>`
      : "";

  container.innerHTML = `
    <svg class="transe-svg" viewBox="0 0 640 330" role="img" aria-label="TransE 嵌入训练步骤">
      <defs>
        <marker id="${uid}-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#0d6b62"></path></marker>
        <marker id="${uid}-pos" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#0d6b62"></path></marker>
        <marker id="${uid}-neg" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#c2410c"></path></marker>
      </defs>
      <rect class="transe-card" x="14" y="14" width="612" height="302" rx="14"></rect>
      <text class="transe-step-kicker" x="34" y="38">步骤 ${stepNum}</text>
      <text class="transe-title" x="96" y="38">${titleLine1}</text>
      <text class="transe-title-sub" x="96" y="54">${titleLine2}</text>
      ${chip(34, 68, 114, "头实体 h", hLabel, "is-head")}
      ${chip(158, 68, 114, "关系 r", rLabel, "is-relation")}
      ${chip(282, 68, 114, "正确尾 t", tLabel, "is-tail")}
      ${chip(406, 68, 126, "负例 t′", negLabel, kind === "neg" || kind === "update" ? "is-neg" : "")}

      <rect class="transe-plane" x="34" y="108" width="368" height="178" rx="10"></rect>
      <line class="transe-axis" x1="54" y1="${axisY}" x2="382" y2="${axisY}"></line>
      <line class="transe-axis" x1="54" y1="${axisY}" x2="54" y2="132"></line>
      <line class="transe-vector" x1="${head[0] + 18}" y1="${head[1]}" x2="${relEnd[0] - 18}" y2="${relEnd[1]}" marker-end="url(#${uid}-arrow)"></line>
      <text class="transe-vector-label" x="${(head[0] + relEnd[0]) / 2}" y="${head[1] - 22}" text-anchor="middle">+ r(${rLabel})</text>
      ${point(head[0], head[1], "h", "is-head")}
      ${point(state.pred[0], state.pred[1], "h+r", "is-pred")}
      ${point(state.tail[0], state.tail[1], "t", "is-tail")}
      ${kind === "neg" || kind === "update" ? point(state.neg[0], state.neg[1], "t′", "is-neg") : ""}
      ${posDistanceLine}
      ${negDistanceLine}
      ${pullArrow}
      ${pushArrow}

      <g class="transe-score-card" transform="translate(418,118)">
        <rect width="172" height="118" rx="12"></rect>
        <text class="transe-score-title" x="18" y="24">训练目标</text>
        ${metricRow(48, "正例距离 d⁺", fmt(state.dPos, 2), "is-pos")}
        ${metricRow(74, "负例距离 d⁻", fmt(state.dNeg, 2), "is-neg")}
        <text class="transe-loss" x="18" y="102">margin=1.0 · loss=${lossValue}</text>
      </g>
      ${dist != null ? `<text class="transe-current" x="218" y="312" text-anchor="middle">当前：${kind === "neg" ? "||h+r−t′||" : "||h+r−t||"} = ${fmt(dist, 2)}</text>` : ""}
    </svg>`;
}

function renderWord2Vec(container, step) {
  const phase = step.phase ?? 0;
  const pts = [
    { label: "鲁迅", x: 0.35, y: 0.5, role: "center" },
    { label: "写", x: phase >= 1 ? 0.52 : 0.62, y: phase >= 1 ? 0.48 : 0.35, role: "pos" },
    { label: "桌子", x: phase >= 2 ? 0.78 : 0.72, y: phase >= 2 ? 0.72 : 0.65, role: "neg" },
  ];
  container.innerHTML = `
    <div class="w2v-space">
      <svg viewBox="0 0 400 220" class="w2v-svg">
        <rect width="400" height="220" fill="#f8fafc"/>
        ${phase >= 1 ? `<line x1="${pts[0].x * 360 + 20}" y1="${pts[0].y * 180 + 20}" x2="${pts[1].x * 360 + 20}" y2="${pts[1].y * 180 + 20}" stroke="#0d6b62" stroke-width="2" marker-end="url(#w2v-a)"/>` : ""}
        ${phase >= 2 ? `<line x1="${pts[0].x * 360 + 20}" y1="${pts[0].y * 180 + 20}" x2="${pts[2].x * 360 + 20}" y2="${pts[2].y * 180 + 20}" stroke="#c2410c" stroke-dasharray="4"/>` : ""}
        ${pts.map((p) => `<g transform="translate(${p.x * 360 + 20},${p.y * 180 + 20})"><circle r="14" fill="${p.role === "neg" ? "#c2410c" : "#0d6b62"}"/><text dy="4" text-anchor="middle" fill="#fff" font-size="10">${p.label}</text></g>`).join("")}
        <defs><marker id="w2v-a" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#0d6b62"/></marker></defs>
      </svg>
      <p class="output-caption">${step.caption || "共现词在向量空间中靠近，无关词被推远。"}</p>
    </div>`;
}

function renderLMChain(container, step) {
  const prefix = step.prefix || ["鲁迅"];
  const candidates = step.candidates || [{ w: "写", p: 0.64 }];
  const maxP = Math.max(...candidates.map((c) => c.p), 0.01);
  const chainHtml = step.product
    ? `<div class="lm-chain-mul"><span>P(句) =</span><code>${step.product}</code></div>`
    : "";
  container.innerHTML = `
    <div class="lm-chain">
      <div class="token-strip">${prefix.map((t, i) => `<span class="token-chip is-merge">${t}${i < prefix.length - 1 ? "" : ""}</span>`).join('<span class="lm-arrow">→</span>')}</div>
      <p class="output-caption">${step.product ? "各步条件概率连乘" : "P(下一 token | 上文)"}</p>
      <div class="lm-probs">${candidates.map((c) => `
        <div class="lm-prob-row"><span>${c.w}</span><div class="metric-bar"><i style="width:${(c.p / maxP) * 100}%"></i></div><em>${fmt(c.p)}</em></div>`).join("")}</div>
      ${chainHtml}
      ${step.ppl != null ? `<p class="output-caption">困惑度 PPL = exp(−平均 log P) ≈ ${step.ppl}</p>` : ""}
    </div>`;
}

function renderActorCritic(container, step) {
  const actions = step.actions || [
    { name: "搜索", p: 0.7 },
    { name: "等待", p: 0.3 },
  ];
  const v = step.v ?? 4.2;
  const a = step.advantage;
  container.innerHTML = `
    <div class="actor-critic-viz">
      <div class="ac-col"><h5>Actor · π(a|s)</h5>
        ${actions.map((ac) => `<div class="metric-bar-row"><span>${ac.name}</span><div class="metric-bar accent"><i style="width:${ac.p * 100}%"></i></div><em>${fmt(ac.p)}</em></div>`).join("")}
      </div>
      <div class="ac-col"><h5>Critic · V(s)</h5><p class="ac-v">${fmt(v)}</p>
        ${a != null ? `<p class="output-caption">优势 A = ${a > 0 ? "+" : ""}${fmt(a)} → ${a > 0 ? "提高" : "降低"}该动作概率</p>` : ""}
      </div>
    </div>`;
}

function renderTDUpdate(container, step) {
  const vOld = step.vOld ?? 2.0;
  const vNew = step.vNew ?? 2.52;
  const r = step.r ?? 1;
  const vNext = step.vNext ?? 4.0;
  const target = step.target ?? 4.6;
  const delta = target - vOld;
  const uid = `td-${++vizMarkerSeq}`;
  const arr = `${uid}-arr`;
  container.innerHTML = `
    <div class="td-viz">
      <svg viewBox="0 0 520 228" class="td-svg" role="img" aria-label="TD 更新示意">
        <rect width="520" height="228" fill="#f8fafc" rx="8"/>
        <g transform="translate(64,72)">
          <circle r="30" fill="#0d6b62"/>
          <text text-anchor="middle" dy="5" fill="#fff" font-size="14">s</text>
        </g>
        <text x="64" y="128" text-anchor="middle" font-size="12" fill="#334155">待搜索</text>
        <text x="64" y="146" text-anchor="middle" font-size="11" fill="#c2410c">V=${fmt(vOld)}</text>
        <text x="152" y="78" fill="#64748b" font-size="12">动作 a</text>
        <path d="M 124 72 L 176 72" stroke="#64748b" marker-end="url(#${arr})"/>
        <text x="150" y="62" fill="#0d6b62" font-size="11">r=${r}</text>
        <g transform="translate(232,72)">
          <circle r="30" fill="#64748b"/>
          <text text-anchor="middle" dy="5" fill="#fff" font-size="14">s′</text>
        </g>
        <text x="232" y="128" text-anchor="middle" font-size="12" fill="#334155">已比价</text>
        <text x="232" y="146" text-anchor="middle" font-size="11" fill="#334155">V=${fmt(vNext)}</text>
        <rect x="312" y="36" width="188" height="88" rx="8" fill="#fff" stroke="#e2e8f0"/>
        <text x="326" y="58" font-size="11" fill="#64748b">Bellman 目标（一步）</text>
        <text x="326" y="80" font-size="13" fill="#0f172a">r + γV(s′) = ${r} + 0.9×${fmt(vNext)} = ${fmt(target)}</text>
        <text x="326" y="102" font-size="12" fill="#c2410c">δ = ${fmt(delta)} → V 新 ${fmt(vNew)}</text>
        <defs><marker id="${arr}" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#64748b"/></marker></defs>
      </svg>
      <div data-math="td_update" class="td-formula-slot"></div>
    </div>`;
  if (window.courseMath?.mountMath) {
    window.courseMath.mountMath(container.querySelector(".td-formula-slot"), "td_update");
  }
}

let clipArchSeq = 0;

function clipArchSvg(clipPhase) {
  const uid = `clip-${++vizMarkerSeq}`;
  const arr = `${uid}-arr`;
  const arrG = `${uid}-arr-g`;
  const arrR = `${uid}-arr-r`;
  const cx = 280;
  const cy = 92;
  const viX = clipPhase === 1 ? cx - 6 : clipPhase === 2 ? cx - 28 : cx - 12;
  const vtX = clipPhase === 1 ? cx + 6 : clipPhase === 2 ? cx + 28 : cx + 12;
  const viY = clipPhase === 1 ? cy - 10 : clipPhase === 2 ? cy - 22 : cy - 14;
  const vtY = clipPhase === 1 ? cy + 10 : clipPhase === 2 ? cy + 22 : cy + 14;
  const linkOn = clipPhase >= 1;
  const linkColor = clipPhase === 2 ? "#c2410c" : "#0d6b62";
  const phaseLabel =
    clipPhase === 0
      ? "双塔各自编码，投影到同一 ℝᵈ"
      : clipPhase === 1
        ? "正例：匹配图文向量靠近"
        : clipPhase === 2
          ? "负例：非匹配向量推远"
          : "InfoNCE：最大化对角相似度";
  return `
    <svg class="clip-arch-mini" viewBox="0 0 560 188" role="img" aria-label="CLIP 双塔与联合嵌入空间">
      <rect width="560" height="188" fill="#f8fafc" rx="8"/>
      <text x="280" y="18" text-anchor="middle" font-size="11" fill="#64748b">${phaseLabel}</text>
      <rect x="12" y="36" width="56" height="36" rx="6" fill="#e0f2fe" stroke="#0d6b62" stroke-width="1.5"/>
      <text x="40" y="58" text-anchor="middle" font-size="9" fill="#0f172a">Image</text>
      <path d="M 68 54 L 88 54" stroke="#64748b" marker-end="url(#${arr})"/>
      <rect x="88" y="28" width="84" height="52" rx="6" fill="#fff" stroke="#0d6b62" stroke-width="1.5"/>
      <text x="130" y="48" text-anchor="middle" font-size="9" fill="#0d6b62" font-weight="600">Image Enc</text>
      <text x="130" y="62" text-anchor="middle" font-size="8" fill="#64748b">ViT / ResNet</text>
      <path d="M 172 54 L 198 54" stroke="${linkOn ? "#0d6b62" : "#94a3b8"}" stroke-width="2" marker-end="url(#${arrG})"/>
      <text x="185" y="48" font-size="8" fill="#64748b">W_I</text>
      <path d="M 198 54 L ${cx - 78} ${cy - 6}" stroke="${linkOn ? "#0d6b62" : "#94a3b8"}" stroke-width="2" fill="none"/>
      <rect x="12" y="118" width="56" height="36" rx="6" fill="#fff7ed" stroke="#c2410c" stroke-width="1.5"/>
      <text x="40" y="140" text-anchor="middle" font-size="9" fill="#0f172a">Text</text>
      <path d="M 68 136 L 88 136" stroke="#64748b" marker-end="url(#${arr})"/>
      <rect x="88" y="110" width="84" height="52" rx="6" fill="#fff" stroke="#c2410c" stroke-width="1.5"/>
      <text x="130" y="130" text-anchor="middle" font-size="9" fill="#c2410c" font-weight="600">Text Enc</text>
      <text x="130" y="144" text-anchor="middle" font-size="8" fill="#64748b">Transformer</text>
      <path d="M 172 136 L 198 136" stroke="${linkOn ? "#c2410c" : "#94a3b8"}" stroke-width="2" marker-end="url(#${arrR})"/>
      <text x="185" y="130" font-size="8" fill="#64748b">W_T</text>
      <path d="M 198 136 L ${cx - 78} ${cy + 6}" stroke="${linkOn ? "#c2410c" : "#94a3b8"}" stroke-width="2" fill="none"/>
      <ellipse cx="${cx}" cy="${cy}" rx="78" ry="48" fill="#fff" stroke="#0d6b62" stroke-width="2" opacity="${linkOn ? 1 : 0.55}"/>
      <text x="${cx}" y="${cy - 8}" text-anchor="middle" font-size="10" fill="#0d6b62">联合嵌入空间</text>
      <text x="${cx}" y="${cy + 8}" text-anchor="middle" font-size="8" fill="#64748b">L2 归一化 · cos(v_I,v_T)</text>
      ${linkOn ? `<circle cx="${viX}" cy="${viY}" r="10" fill="#ecfdf5" stroke="#0d6b62" stroke-width="2"/><text x="${viX}" y="${viY + 3}" text-anchor="middle" font-size="8" fill="#0d6b62">v_I</text>` : ""}
      ${linkOn ? `<circle cx="${vtX}" cy="${vtY}" r="10" fill="#fff7ed" stroke="#c2410c" stroke-width="2"/><text x="${vtX}" y="${vtY + 3}" text-anchor="middle" font-size="8" fill="#c2410c">v_T</text>` : ""}
      ${linkOn ? `<line x1="${viX}" y1="${viY + 10}" x2="${vtX}" y2="${vtY - 10}" stroke="${linkColor}" stroke-width="2" stroke-dasharray="${clipPhase === 2 ? "4 3" : "0"}"/>` : ""}
      ${clipPhase >= 1 ? `<path d="M ${cx + 78} ${cy} L 408 ${cy}" stroke="#64748b" stroke-width="1.5" marker-end="url(#${arr})"/><rect x="408" y="${cy - 28}" width="72" height="56" rx="6" fill="#fff" stroke="#cbd5e1"/><text x="444" y="${cy - 10}" text-anchor="middle" font-size="8" fill="#64748b">batch</text><text x="444" y="${cy + 6}" text-anchor="middle" font-size="9" fill="#0d6b62">N×N cos</text>` : ""}
      <defs>
        <marker id="${arr}" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#64748b"/></marker>
        <marker id="${arrG}" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#0d6b62"/></marker>
        <marker id="${arrR}" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#c2410c"/></marker>
      </defs>
    </svg>`;
}

function renderCLIPPair(container, step) {
  const clipPhase =
    step.clipPhase ??
    (step.loss ? 3 : step.sim != null && step.pos === false ? 2 : step.sim != null ? 1 : 0);
  const imageLabel = step.imageLabel || "图像：猫在沙发上";
  const positiveText = step.positiveText || "文本：一只猫在沙发上";
  const negativeText = step.negativeText || "文本：一辆车在马路上";
  const activeText = clipPhase === 2 ? negativeText : positiveText;
  const posSim = step.posSim ?? 0.91;
  const negSim = step.negSim ?? 0.08;
  const batchN = 3;
  const simMatrix = [
    [0.91, 0.12, 0.08],
    [0.15, 0.88, 0.11],
    [0.09, 0.14, 0.86],
  ];

  let meterClass = "is-neutral";
  let meterLabel = "编码中";
  let meterHint = "分别得到 v_I、v_T";
  if (clipPhase === 1) {
    meterClass = "is-pos";
    meterLabel = fmt(posSim);
    meterHint = "匹配对拉近 ↑";
  } else if (clipPhase === 2) {
    meterClass = "is-neg";
    meterLabel = fmt(negSim);
    meterHint = "非匹配推远 ↓";
  } else if (clipPhase === 3) {
    meterClass = "is-pos";
    meterLabel = fmt(posSim);
    meterHint = "最大化正例 logit";
  }

  const archSvg = clipArchSvg(clipPhase);

  const matrixHtml =
    clipPhase >= 1
      ? `<div class="clip-sim-matrix ${clipPhase === 0 ? "is-dim" : ""}">
          <h5>Batch 相似度矩阵（对角为正例）</h5>
          <table class="clip-sim-table">
            <thead><tr><th></th>${Array.from({ length: batchN }, (_, i) => `<th>T${i + 1}</th>`).join("")}</tr></thead>
            <tbody>${simMatrix
              .map((row, i) => {
                const rowOn = (clipPhase === 1 || clipPhase === 3) && i === 0;
                return `<tr class="${rowOn ? "is-focus" : ""}"><th>I${i + 1}</th>${row
                  .map((v, j) => {
                    const cellOn = rowOn && i === j;
                    const cellNeg = clipPhase === 2 && i === 0 && j === 2;
                    const cls = cellOn ? "is-pos" : cellNeg ? "is-neg" : "";
                    return `<td class="${cls}">${fmt(v)}</td>`;
                  })
                  .join("")}</tr>`;
              })
              .join("")}</tbody>
          </table>
        </div>`
      : "";

  const batchHtml =
    clipPhase >= 1
      ? `<div class="clip-batch">
          <div class="clip-row is-pos ${clipPhase === 1 || clipPhase === 3 ? "is-focus" : ""}"><strong>正例</strong><span>${positiveText}</span><em>cos=${fmt(posSim)}</em></div>
          <div class="clip-row is-neg ${clipPhase === 2 ? "is-focus" : ""}"><strong>负例</strong><span>${negativeText}</span><em>cos=${fmt(negSim)}</em></div>
        </div>`
      : `<p class="clip-phase-hint">两路 Encoder 各自输出 d 维向量，下一步在共享空间计算相似度。</p>`;

  const mathKey = clipPhase === 3 ? "infonce" : clipPhase >= 1 ? "clip_cosine" : null;
  const formulaSlot = mathKey ? `<div class="clip-formula-slot" data-math="${mathKey}"></div>` : "";

  container.innerHTML = `
    <div class="clip-contrast-viz clip-phase-${clipPhase}">
      ${archSvg}
      <div class="clip-two-tower">
        <div class="clip-tower-card ${clipPhase >= 0 ? "is-on" : ""}">
          <strong>图像塔</strong>
          <span>${imageLabel}</span>
          <code>v_I ∈ ℝᵈ</code>
        </div>
        <div class="clip-meter ${meterClass}"><span>cos(v_I, v_T)</span><strong>${meterLabel}</strong><em>${meterHint}</em></div>
        <div class="clip-tower-card ${clipPhase >= 0 ? "is-on" : ""}">
          <strong>文本塔</strong>
          <span>${activeText}</span>
          <code>v_T ∈ ℝᵈ</code>
        </div>
      </div>
      ${batchHtml}
      ${matrixHtml}
      ${formulaSlot}
    </div>`;

  if (mathKey && window.courseMath?.mountMath) {
    window.courseMath.mountMath(container.querySelector(".clip-formula-slot"), mathKey);
  }
}

function renderViTPatches(container, step) {
  const phase = step.vitPhase ?? (step.head ? 5 : step.enc ? 4 : step.pos ? 3 : step.flat ? 2 : step.patches ? 1 : 0);
  const pixels = [
    ["#0d6b62", "#2563eb", "#93c5fd", "#0d6b62"],
    ["#64748b", "#0d6b62", "#2563eb", "#93c5fd"],
    ["#93c5fd", "#64748b", "#0d6b62", "#2563eb"],
    ["#2563eb", "#93c5fd", "#64748b", "#0d6b62"],
  ];
  const patchCell = (i, extra = "") => {
    const pr = Math.floor(i / 2);
    const pc = i % 2;
    const mini = [];
    for (let r = pr * 2; r < pr * 2 + 2; r++) {
      for (let c = pc * 2; c < pc * 2 + 2; c++) {
        mini.push(`<i style="background:${pixels[r][c]}"></i>`);
      }
    }
    const on = phase >= 1;
    return `<div class="vit-patch-tile ${on ? "is-on" : ""} ${extra}"><div class="patch-mini">${mini.join("")}</div><span>P${i + 1}</span></div>`;
  };
  const encBlocks = [1, 2, 3].map((n) => `<div class="vit-enc-block ${phase >= 4 ? "is-on" : ""}">Self-Attn ${n}</div>`).join("");
  container.innerHTML = `
    <div class="vit-paper-flow">
      <div class="vit-paper-row">
        <div class="vit-paper-panel ${phase >= 0 ? "is-on" : ""}">
          <h5>① 原图 H×W</h5>
          <div class="vit-pixel-grid">${pixels.flat().map((c, i) => `<i style="background:${c}" title="px${i}"></i>`).join("")}</div>
        </div>
        <span class="vit-paper-arrow">→</span>
        <div class="vit-paper-panel ${phase >= 1 ? "is-on" : ""}">
          <h5>② Patchify</h5>
          <div class="vit-patch-grid-2">${[0, 1, 2, 3].map((i) => patchCell(i)).join("")}</div>
          <p class="vit-caption">2×2 patch → 4 个视觉 token</p>
        </div>
        <span class="vit-paper-arrow">→</span>
        <div class="vit-paper-panel ${phase >= 2 ? "is-on" : ""}">
          <h5>③ Linear 投影</h5>
          <div class="vit-embed-bars">
            ${[0, 1, 2, 3].map((i) => `<div class="vit-embed-row"><span>P${i + 1}</span><div class="vit-bar"><i style="width:${55 + i * 8}%"></i></div><em>d 维</em></div>`).join("")}
          </div>
        </div>
      </div>
      <div class="vit-paper-row vit-paper-row--mid">
        <div class="vit-paper-panel ${phase >= 3 ? "is-on" : ""}">
          <h5>④ + 位置编码</h5>
          <div class="vit-pos-grid">${[0, 1, 2, 3].map((i) => `<div class="vit-pos-cell"><span>P${i + 1}</span><em>+ pos${i}</em></div>`).join("")}</div>
        </div>
        <span class="vit-paper-arrow">→</span>
        <div class="vit-paper-panel vit-paper-panel--wide ${phase >= 4 ? "is-on" : ""}">
          <h5>⑤ Transformer Encoder ×L</h5>
          <div class="vit-enc-stack">${encBlocks}</div>
          <svg class="vit-attn-svg" viewBox="0 0 280 80" aria-hidden="true">
            ${phase >= 4 ? [0, 1, 2, 3].map((i) => `<line x1="${40 + i * 60}" y1="20" x2="${40 + ((i + 2) % 4) * 60}" y2="60" stroke="#0d6b62" stroke-width="1.5" opacity="0.45"/>`).join("") : ""}
            ${[0, 1, 2, 3].map((i) => `<circle cx="${40 + i * 60}" cy="${phase >= 4 ? 40 : 40}" r="14" fill="${phase >= 4 ? "#ecfdf5" : "#f1f5f9"}" stroke="#0d6b62"/>`).join("")}
          </svg>
          <p class="vit-caption">每个 patch token 与全图 patch 做 Self-Attention</p>
        </div>
        <span class="vit-paper-arrow">→</span>
        <div class="vit-paper-panel ${phase >= 5 ? "is-on" : ""}">
          <h5>⑥ MLP Head</h5>
          <div class="vit-head-out"><strong>猫</strong><em>0.87</em></div>
          <p class="vit-caption">均值池化 4 个 patch token → 分类</p>
        </div>
      </div>
    </div>`;
}

function renderLogicLayers(container, step) {
  const layer = step.layer ?? 0;
  const layers = [
    { name: "命题逻辑", tag: "P ∧ Q", ex: "P=「苏格拉底是人」 Q=「人终有一死」→ P∧Q" },
    { name: "一阶逻辑", tag: "∀X P(X)→Q(X)", ex: "∀X 人(X)→会死(X)，X=苏格拉底" },
    { name: "产生式规则", tag: "IF … THEN …", ex: "IF 人(X) THEN 会死(X) · 事实库独立" },
  ];
  const facts = step.facts || ["人(苏格拉底)", layer >= 2 ? "会死(苏格拉底) ✓" : "—"];
  container.innerHTML = `
    <div class="logic-layer-demo">
      <svg class="logic-syllogism-svg" viewBox="0 0 220 200" role="img" aria-label="三段论推理链">
        <defs><marker id="logic-arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#64748b"/></marker></defs>
        <g class="logic-node ${layer >= 0 ? "is-on" : ""}"><circle cx="110" cy="28" r="22" fill="#0d6b62"/><text x="110" y="32" text-anchor="middle" fill="#fff" font-size="10">苏格拉底</text></g>
        <line x1="110" y1="50" x2="110" y2="68" stroke="#64748b" marker-end="url(#logic-arr)"/>
        <text x="148" y="62" font-size="11" fill="#64748b">是人</text>
        <g class="logic-node ${layer >= 0 ? "is-on" : ""}"><circle cx="110" cy="88" r="22" fill="#2563eb"/><text x="110" y="92" text-anchor="middle" fill="#fff" font-size="11">人</text></g>
        <line x1="110" y1="110" x2="110" y2="128" stroke="#64748b" marker-end="url(#logic-arr)"/>
        <text x="148" y="122" font-size="11" fill="#64748b">终有一死</text>
        <g class="logic-node ${layer >= 1 ? "is-on" : ""}"><circle cx="110" cy="148" r="22" fill="#c2410c"/><text x="110" y="152" text-anchor="middle" fill="#fff" font-size="11">终有一死</text></g>
        ${layer >= 2 ? `<path d="M 40 28 C 20 90, 20 130, 40 148" fill="none" stroke="#0d6b62" stroke-width="2" stroke-dasharray="4" marker-end="url(#logic-arr)"/><text x="8" y="96" font-size="11" fill="#0d6b62">规则触发</text>` : ""}
      </svg>
      <div class="logic-layer-stack">
        ${layers.map((L, i) => `
          <div class="logic-layer-card ${i === layer ? "is-active" : i < layer ? "is-done" : ""}">
            <h5>${L.name}</h5><code>${L.tag}</code><p>${L.ex}</p>
          </div>`).join("")}
        ${layer >= 2 ? `<div class="logic-fact-box"><strong>事实库</strong>${facts.map((f) => `<span class="detail-tag">${f}</span>`).join("")}</div>` : ""}
      </div>
    </div>`;
}

function drawXorDemo(ctx, w, h) {
  const pts = [[0, 0, -1], [0, 1, 1], [1, 0, 1], [1, 1, -1]];
  ctx.fillStyle = "#f8fafc";
  ctx.fillRect(0, 0, w, h);
  const half = w / 2 - 8;
  [["单层线性", "linear"], ["含 ReLU 隐藏层", "mlp"]].forEach(([title, mode], panel) => {
    const ox = panel * half + (panel ? 12 : 0);
    const pw = half - 16;
    const plotX = ox + 34;
    const plotY = 54;
    const plotW = Math.max(96, pw - 68);
    const plotH = Math.max(78, h - 104);
    const pointInset = Math.min(14, plotW * 0.12, plotH * 0.16);
    const edgeX = (x) => plotX + x * plotW;
    const edgeY = (y) => plotY + (1 - y) * plotH;
    const sx = (x) => plotX + pointInset + x * (plotW - pointInset * 2);
    const sy = (y) => plotY + pointInset + (1 - y) * (plotH - pointInset * 2);
    ctx.fillStyle = "#fff";
    ctx.fillRect(ox, 12, pw, h - 24);
    ctx.strokeStyle = "#e2e8f0";
    ctx.strokeRect(ox, 12, pw, h - 24);
    ctx.fillStyle = "#334155";
    ctx.font = "11px sans-serif";
    ctx.fillText(title, ox + 8, 28);
    ctx.fillStyle = "#64748b";
    ctx.font = "8px sans-serif";
    ctx.fillText(mode === "linear" ? "单个半平面" : "组合多个半平面", ox + 8, 42);
    ctx.fillStyle = "#f8fafc";
    ctx.fillRect(plotX, plotY, plotW, plotH);
    ctx.strokeStyle = "#cbd5e1";
    ctx.strokeRect(plotX, plotY, plotW, plotH);
    ctx.strokeStyle = "#e2e8f0";
    ctx.beginPath();
    ctx.moveTo(sx(0.5), plotY);
    ctx.lineTo(sx(0.5), plotY + plotH);
    ctx.moveTo(plotX, sy(0.5));
    ctx.lineTo(plotX + plotW, sy(0.5));
    ctx.stroke();
    ctx.strokeStyle = mode === "linear" ? "#c2410c" : "#0d6b62";
    ctx.lineWidth = 2;
    ctx.setLineDash(mode === "linear" ? [6, 4] : []);
    ctx.beginPath();
    if (mode === "linear") {
      ctx.moveTo(edgeX(0), edgeY(0.76));
      ctx.lineTo(edgeX(1), edgeY(0.24));
    } else {
      ctx.moveTo(edgeX(0), edgeY(0.55));
      ctx.lineTo(edgeX(0.55), edgeY(0));
      ctx.moveTo(edgeX(0.45), edgeY(1));
      ctx.lineTo(edgeX(1), edgeY(0.45));
    }
    ctx.stroke();
    ctx.setLineDash([]);
    pts.forEach(([x, y, label]) => {
      ctx.fillStyle = label > 0 ? "#0d6b62" : "#c2410c";
      ctx.beginPath();
      ctx.arc(sx(x), sy(y), 5.5, 0, 7);
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 1.2;
      ctx.stroke();
    });
    ctx.fillStyle = mode === "linear" ? "#c2410c" : "#0d6b62";
    ctx.font = "9px sans-serif";
    ctx.fillText(mode === "linear" ? "单层线性不够" : "加入激活后可分", ox + 8, h - 14);
  });
}

function renderWorkflow(container, step) {
  const phase = step.phase ?? 0;
  const modes = [
    {
      name: "直接答",
      user: "50 道错题里，概念混淆和计算错误各多少题？请只给两个数字。",
      bot: "概念混淆 18 题，计算错误 20 题。",
      chain: null,
    },
    {
      name: "CoT 推理链",
      user: "50 道错题里，概念混淆和计算错误各多少题？请只给两个数字。",
      bot: "概念混淆 18 题，计算错误 20 题。",
      chain: ["逐题标注错因标签", "概念混淆计数 → 18", "计算错误计数 → 20", "输出两个数字"],
    },
    {
      name: "SFT 对齐格式",
      user: "50 道错题里，概念混淆和计算错误各多少题？请只给两个数字。",
      bot: "分析：按错因标签统计。\n答案：概念混淆 18，计算错误 20。",
      chain: ["固定「分析：… 答案：…」模板", "便于部署与自动解析"],
    },
  ];
  const m = modes[phase];
  container.innerHTML = `
    <div class="workflow-demo">
      <div class="workflow-tabs">${modes.map((x, i) => `<span class="workflow-tab ${i === phase ? "is-active" : ""}">${x.name}</span>`).join("")}</div>
      <div class="workflow-chat">
        <div class="workflow-bubble user"><strong>用户</strong><p>${m.user}</p></div>
        ${m.chain ? `<div class="workflow-chain">${m.chain.map((c) => `<div class="workflow-step-chip">${c}</div>`).join("")}</div>` : ""}
        <div class="workflow-bubble bot"><strong>模型</strong><p>${m.bot}</p></div>
      </div>
      <p class="output-caption">${phase === 0 ? "缺推理过程，难以纠错。" : phase === 1 ? "CoT：先写中间步骤再答。" : "SFT：固定输出模板，便于部署。"}</p>
    </div>`;
}

function renderMAEFlow(container, step) {
  const MAE_PATCH_PATTERNS = [
    [[0.2, 0.3, 0.5, 0.4], [0.3, 0.8, 0.7, 0.5], [0.4, 0.7, 0.9, 0.6], [0.3, 0.5, 0.6, 0.4]],
    [[0.6, 0.2, 0.3, 0.7], [0.1, 0.4, 0.8, 0.2], [0.5, 0.3, 0.2, 0.6], [0.7, 0.5, 0.4, 0.3]],
    [[0.4, 0.6, 0.2, 0.5], [0.3, 0.2, 0.7, 0.4], [0.8, 0.5, 0.3, 0.6], [0.2, 0.4, 0.5, 0.7]],
    [[0.5, 0.3, 0.6, 0.4], [0.4, 0.7, 0.2, 0.5], [0.3, 0.5, 0.8, 0.3], [0.6, 0.2, 0.4, 0.7]],
  ];
  const maePixelMini = (patchIdx, recon) => {
    const pattern = MAE_PATCH_PATTERNS[patchIdx];
    const cells = pattern.flat().map((v) => {
      const g = recon ? Math.round(v * 180 + 40) : Math.round(v * 200);
      const color = recon ? `rgb(${g},${g + 20},255)` : `rgb(${g - 30},${g + 10},${g - 10})`;
      return `<i style="background:${color}"></i>`;
    }).join("");
    return `<div class="mae-pixel-mini">${cells}</div>`;
  };
  const phase = step.maePhase ?? (step.recon ? 4 : step.encode ? 3 : step.mask > 0 ? 2 : 1);
  const visible = phase >= 3 ? [0] : phase >= 2 ? [0] : [0, 1, 2, 3];
  const masked = [1, 2, 3];
  const patchTile = (i) => {
    const isMask = masked.includes(i) && phase >= 2 && phase < 4;
    const isRecon = masked.includes(i) && phase >= 4;
    const showPx = !isMask || isRecon;
    let inner = "";
    if (isMask && !isRecon) {
      inner = `<div class="mae-mask-block">MASK</div>`;
    } else if (showPx) {
      inner = maePixelMini(i, isRecon);
    }
    const cls = visible.includes(i) && phase >= 3 ? "to-encoder" : isMask ? "is-masked" : isRecon ? "is-recon" : "";
    return `<div class="mae-patch ${cls}"><span>P${i + 1}</span>${inner}</div>`;
  };
  container.innerHTML = `
    <div class="mae-paper-flow">
      <div class="mae-paper-row">
        <div class="mae-panel ${phase >= 1 ? "is-on" : ""}">
          <h5>① 切 patch</h5>
          <div class="mae-grid">${[0, 1, 2, 3].map((i) => patchTile(i)).join("")}</div>
        </div>
        <span class="mae-arrow">→</span>
        <div class="mae-panel ${phase >= 2 ? "is-on" : ""}">
          <h5>② 随机遮 75%</h5>
          <div class="mae-grid">${[0, 1, 2, 3].map((i) => patchTile(i)).join("")}</div>
          <p class="mae-caption">仅 P1 可见，P2–P4 被移除</p>
        </div>
        <span class="mae-arrow">→</span>
        <div class="mae-panel ${phase >= 3 ? "is-on" : ""}">
          <h5>③ Encoder（25%）</h5>
          <div class="mae-enc-box">
            <div class="mae-enc-in">${patchTile(0)}</div>
            <div class="mae-enc-stack"><div>ViT Encoder</div><div>只看可见 token</div></div>
          </div>
        </div>
      </div>
      <div class="mae-paper-row">
        <div class="mae-panel mae-panel--wide ${phase >= 4 ? "is-on" : ""}">
          <h5>④ Decoder + 掩码 token 重构全图</h5>
          <div class="mae-dec-flow">
            <div class="mae-dec-tokens">
              ${[0, 1, 2, 3].map((i) => `<span class="${i === 0 ? "from-enc" : "mask-token"}">${i === 0 ? "z₁" : `[M${i}]`}</span>`).join("")}
            </div>
            <span class="mae-arrow">→</span>
            <div class="mae-grid">${[0, 1, 2, 3].map((i) => patchTile(i)).join("")}</div>
          </div>
          <p class="mae-caption">损失 = 被遮 patch 的像素 MSE（预训练无标签）</p>
        </div>
      </div>
    </div>`;
}

function drawMaePixelGrid(ctx, w, h, step) {
  const cell = 10;
  const patchSize = 4;
  const patchPx = patchSize * cell;
  const ox = 48;
  const oy = 40;
  const patterns = [
    [[0.2, 0.3, 0.5, 0.4], [0.3, 0.8, 0.7, 0.5], [0.4, 0.7, 0.9, 0.6], [0.3, 0.5, 0.6, 0.4]],
    [[0.6, 0.2, 0.3, 0.7], [0.1, 0.4, 0.8, 0.2], [0.5, 0.3, 0.2, 0.6], [0.7, 0.5, 0.4, 0.3]],
    [[0.4, 0.6, 0.2, 0.5], [0.3, 0.2, 0.7, 0.4], [0.8, 0.5, 0.3, 0.6], [0.2, 0.4, 0.5, 0.7]],
    [[0.5, 0.3, 0.6, 0.4], [0.4, 0.7, 0.2, 0.5], [0.3, 0.5, 0.8, 0.3], [0.6, 0.2, 0.4, 0.7]],
  ];
  ctx.fillStyle = "#f8fafc";
  ctx.fillRect(0, 0, w, h);
  for (let p = 0; p < 4; p++) {
    const px = ox + (p % 2) * (patchPx + 16);
    const py = oy + Math.floor(p / 2) * (patchPx + 16);
    const hidden = step.mask > 0 && p > 0 && !step.recon;
    const recon = step.recon && p > 0;
    ctx.strokeStyle = "#94a3b8";
    ctx.lineWidth = 1;
    ctx.strokeRect(px - 2, py - 2, patchPx + 4, patchPx + 4);
    if (hidden) {
      ctx.fillStyle = "#cbd5e1";
      ctx.fillRect(px, py, patchPx, patchPx);
      ctx.fillStyle = "#64748b";
      ctx.font = "bold 14px sans-serif";
      ctx.fillText("?", px + patchPx / 2 - 6, py + patchPx / 2 + 5);
    } else {
      for (let i = 0; i < patchSize; i++) {
        for (let j = 0; j < patchSize; j++) {
          const v = patterns[p][i][j];
          const g = recon ? Math.round(v * 180 + 40) : Math.round(v * 200);
          ctx.fillStyle = recon ? `rgb(${g},${g + 20},255)` : `rgb(${g - 30},${g + 10},${g - 10})`;
          ctx.fillRect(px + j * cell, py + i * cell, cell - 1, cell - 1);
        }
      }
      if (recon) {
        ctx.setLineDash([4, 3]);
        ctx.strokeStyle = "#2563eb";
        ctx.strokeRect(px - 2, py - 2, patchPx + 4, patchPx + 4);
        ctx.setLineDash([]);
      }
    }
    if (p === 0) {
      ctx.fillStyle = "#0d6b62";
      ctx.font = "10px sans-serif";
      ctx.fillText("P1 可见", px, py - 8);
    }
  }
  ctx.fillStyle = "#334155";
  ctx.font = "12px sans-serif";
  const cap = step.recon ? "Decoder 重构被遮 patch（蓝色虚线框）" : step.encode ? "Encoder 仅编码 25% 可见 patch" : step.mask ? "随机遮 75% · 仅左上角可见" : "完整 2×2 patch 输入";
  ctx.fillText(cap, ox, h - 16);
}

function renderEpsilonBandit(container, step) {
  const arms = step.arms || [
    { name: "餐馆 A", q: 0.82 },
    { name: "餐馆 B", q: 0.65 },
    { name: "餐馆 C", q: 0.71 },
    { name: "餐馆 D", q: 0.55 },
  ];
  const eps = step.eps ?? 0.2;
  const pick = step.pick ?? { mode: "exploit", arm: 0 };
  const maxQ = Math.max(...arms.map((a) => a.q));
  container.innerHTML = `
    <div class="epsilon-bandit">
      <div class="epsilon-bar-wrap">
        <div class="epsilon-bar"><i class="explore" style="width:${eps * 100}%"></i><i class="exploit" style="width:${(1 - eps) * 100}%"></i></div>
        <span class="epsilon-bar-label">探索 ${Math.round(eps * 100)}% · 利用 ${Math.round((1 - eps) * 100)}%</span>
      </div>
      <div class="bandit-arms">${arms.map((a, i) => `
        <div class="bandit-arm ${i === pick.arm ? "is-picked" : ""} ${a.q === maxQ ? "is-best" : ""}">
          <span class="bandit-arm-name">${a.name}</span>
          <div class="metric-bar"><i style="width:${a.q * 100}%"></i></div>
          <em>Q=${fmt(a.q)}</em>
          ${i === pick.arm ? `<span class="bandit-pick-tag">${pick.mode === "explore" ? "随机探索" : "贪心选最优"}</span>` : ""}
        </div>`).join("")}</div>
      <p class="output-caption">${pick.mode === "explore" ? `掷骰落在探索区 → 随机试 ${arms[pick.arm].name}` : `落在利用区 → 选当前最高 Q 的 ${arms[pick.arm].name}`}</p>
    </div>`;
}

function renderAlphaFoldFlow(container, step) {
  const phase = step.phase ?? 0;
  const seq = ["M", "K", "T", "A", "Y", "F", "Y"];
  const colors = ["#0d6b62", "#2563eb", "#c2410c", "#eab308", "#0d6b62", "#64748b", "#2563eb"];
  const msaRows = [
    ["M", "M", "M", "M", "M", "M", "M"],
    ["K", "K", "R", "K", "K", "N", "K"],
    ["T", "T", "S", "T", "T", "T", "T"],
    ["A", "A", "A", "V", "A", "A", "A"],
    ["Y", "Y", "F", "Y", "Y", "Y", "H"],
    ["F", "F", "L", "F", "F", "F", "F"],
    ["Y", "Y", "Y", "Y", "W", "Y", "Y"],
  ];
  const msaCell = (aa, ref, x, y) => {
    const conserved = aa === ref;
    return `<rect x="${x}" y="${y}" width="30" height="20" fill="${conserved ? "#ecfdf5" : "#fef3c7"}" stroke="#cbd5e1"/><text x="${x + 15}" y="${y + 14}" text-anchor="middle" font-size="10">${aa}</text>`;
  };
  let mainViz = "";
  if (phase === 0) {
    mainViz = `<svg class="alphafold-detail-svg" viewBox="0 0 480 120" role="img" aria-label="氨基酸序列编码">
      <rect width="480" height="120" fill="#fff" rx="8"/>
      <text x="16" y="24" font-size="12" fill="#64748b">一级序列（7 残基 · 每个字母 = 一种氨基酸）</text>
      ${seq.map((aa, i) => `<g transform="translate(${16 + i * 58}, 36)"><rect width="48" height="48" rx="6" fill="${colors[i]}" opacity="0.85"/><text x="24" y="30" text-anchor="middle" fill="#fff" font-weight="600">${aa}</text><text x="24" y="44" text-anchor="middle" fill="#fff" font-size="9">${i + 1}</text></g>`).join("")}
      <text x="16" y="108" font-size="11" fill="#334155">→ one-hot / embedding → 残基特征向量</text>
    </svg>`;
  } else if (phase === 1) {
    const colW = 34;
    mainViz = `<svg class="alphafold-detail-svg" viewBox="0 0 520 220" role="img" aria-label="多序列比对 MSA">
      <rect width="520" height="220" fill="#fff" rx="8"/>
      <text x="16" y="22" font-size="12" fill="#64748b">MSA：7 条同源序列 × 7 列 · 纵向对齐看共变</text>
      ${seq.map((aa, ci) => `<text x="${16 + ci * colW + 15}" y="38" text-anchor="middle" font-size="9" fill="#64748b">${ci + 1}</text>`).join("")}
      ${msaRows.map((row, ri) => `<g transform="translate(16, ${44 + ri * 22})">${row.map((aa, ci) => msaCell(aa, seq[ci], ci * colW, 0)).join("")}</g>`).join("")}
      <text x="16" y="208" font-size="11" fill="#334155">共变列（如第 4 列 A/V）→ 可能空间上靠近</text>
    </svg>`;
  } else if (phase === 2) {
    mainViz = `<svg class="alphafold-detail-svg" viewBox="0 0 520 170" role="img" aria-label="Evoformer">
      <rect width="520" height="170" fill="#fff" rx="8"/>
      <defs><marker id="evo-arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#0d6b62"/></marker></defs>
      <text x="16" y="22" font-size="12" fill="#64748b">Evoformer：MSA 轨 ↔ Pair 轨 双向更新</text>
      <rect x="24" y="36" width="130" height="44" rx="6" fill="#e0f2fe" stroke="#0d6b62"/><text x="89" y="62" text-anchor="middle" font-size="11">MSA 表示</text>
      <rect x="24" y="92" width="130" height="44" rx="6" fill="#fef3c7" stroke="#c2410c"/><text x="89" y="118" text-anchor="middle" font-size="11">Pair (i,j)</text>
      <path d="M 158 58 L 198 58" fill="none" stroke="#0d6b62" stroke-width="2" marker-end="url(#evo-arr)"/>
      <path d="M 198 114 L 158 114" fill="none" stroke="#c2410c" stroke-width="2" marker-end="url(#evo-arr)"/>
      <text x="178" y="52" text-anchor="middle" font-size="9" fill="#0d6b62">MSA→Pair</text>
      <text x="178" y="128" text-anchor="middle" font-size="9" fill="#c2410c">Pair→MSA</text>
      <rect x="210" y="52" width="96" height="72" rx="6" fill="#ecfdf5" stroke="#0d6b62" stroke-width="2"/><text x="258" y="82" text-anchor="middle" font-size="10">Evoformer</text><text x="258" y="98" text-anchor="middle" font-size="9">× 48 块</text>
      <path d="M 310 88 L 350 88" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#evo-arr)"/>
      <rect x="358" y="68" width="110" height="52" rx="6" fill="#f1f5f9" stroke="#64748b"/><text x="413" y="98" text-anchor="middle" font-size="10">结构模块</text>
    </svg>`;
  } else {
    mainViz = `<svg class="alphafold-struct-svg" viewBox="0 0 400 160" role="img" aria-label="蛋白质三维结构">
      <path d="M 40 120 Q 100 40, 160 80 T 280 60 T 360 100" fill="none" stroke="#0d6b62" stroke-width="3"/>
      <circle cx="40" cy="120" r="6" fill="#22c55e"/><circle cx="160" cy="80" r="6" fill="#eab308"/>
      <circle cx="280" cy="60" r="6" fill="#22c55e"/><circle cx="360" cy="100" r="6" fill="#ef4444"/>
      <text x="200" y="145" text-anchor="middle" font-size="10" fill="#64748b">pLDDT：绿=高置信 · 红=低置信</text>
    </svg>`;
  }
  const blocks = [
    { id: "seq", label: "氨基酸序列", sub: "残基 embedding" },
    { id: "msa", label: "MSA 比对", sub: "进化共变" },
    { id: "evo", label: "Evoformer", sub: "MSA + Pair" },
    { id: "struct", label: "3D 结构", sub: "pLDDT" },
  ];
  container.innerHTML = `
    <div class="alphafold-flow">
      <div class="alphafold-pipeline">${blocks.map((b, i) => `
        <div class="alphafold-block ${i <= phase ? "is-on" : ""} ${i === phase ? "is-current" : ""}">
          <strong>${b.label}</strong><span>${b.sub}</span>
        </div>${i < blocks.length - 1 ? '<span class="alphafold-arrow">→</span>' : ""}`).join("")}</div>
      ${mainViz}
      <div class="repr-table four-elements">
        <div class="repr-row"><strong>输入</strong><span>序列 + MSA + 模板（可选）</span></div>
        <div class="repr-row"><strong>输出</strong><span>原子坐标 + 每残基 pLDDT</span></div>
      </div>
    </div>`;
}

function drawGanTrainingCurve(ctx, w, h, stepIdx) {
  const pad = { l: 52, r: 44, t: 48, b: 58 };
  const plotH = h - pad.t - pad.b;
  const yMaxLoss = 2.4;
  const sx = (i, n) => pad.l + (i / (n - 1)) * (w - pad.l - pad.r);
  const syLoss = (v) => h - pad.b - (v / yMaxLoss) * plotH;
  const syProb = (v) => h - pad.b - v * plotH;

  const phases = ["G", "D", "G", "D", "G", "D", "G", "D", "G", "D", "G", "D", "G", "D", "G", "≈"];
  const dLoss = [0.69, 0.41, 0.62, 0.38, 0.55, 0.33, 0.49, 0.31, 0.44, 0.29, 0.40, 0.27, 0.37, 0.26, 0.34, 0.32];
  const gLoss = [1.92, 2.08, 1.52, 1.88, 1.22, 1.68, 0.98, 1.48, 0.88, 1.32, 0.78, 1.18, 0.74, 1.08, 0.71, 0.68];
  const dFake = [0.16, 0.07, 0.38, 0.06, 0.55, 0.08, 0.72, 0.10, 0.65, 0.12, 0.58, 0.14, 0.54, 0.16, 0.51, 0.50];
  const n = dLoss.length;
  const demoIdx = [1, 4, 9, 15];
  const cur = demoIdx[Math.min(Math.max(0, stepIdx), demoIdx.length - 1)] ?? 0;

  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, w, h);

  for (let i = 0; i < n - 1; i++) {
    ctx.fillStyle = phases[i] === "G" ? "rgba(37,99,235,0.05)" : phases[i] === "D" ? "rgba(194,65,12,0.05)" : "rgba(13,107,98,0.04)";
    ctx.fillRect(sx(i, n), pad.t, sx(i + 1, n) - sx(i, n), plotH);
  }

  ctx.strokeStyle = "#e2e8f0";
  ctx.lineWidth = 1;
  for (let i = 0; i < 5; i++) {
    const y = syLoss((i / 4) * yMaxLoss);
    ctx.beginPath();
    ctx.moveTo(pad.l, y);
    ctx.lineTo(w - pad.r, y);
    ctx.stroke();
  }

  ctx.strokeStyle = "#334155";
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(pad.l, pad.t);
  ctx.lineTo(pad.l, h - pad.b);
  ctx.lineTo(w - pad.r, h - pad.b);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(w - pad.r, pad.t);
  ctx.lineTo(w - pad.r, h - pad.b);
  ctx.stroke();

  const drawSeries = (data, color, sy, dash) => {
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.setLineDash(dash || []);
    ctx.beginPath();
    data.forEach((v, i) => {
      if (i === 0) ctx.moveTo(sx(i, n), sy(v));
      else ctx.lineTo(sx(i, n), sy(v));
    });
    ctx.stroke();
    ctx.setLineDash([]);
    data.forEach((v, i) => {
      ctx.fillStyle = i === cur ? color : color;
      ctx.beginPath();
      ctx.arc(sx(i, n), sy(v), i === cur ? 5.5 : 3, 0, 7);
      ctx.fill();
      if (i === cur) {
        ctx.strokeStyle = "#0f172a";
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    });
  };

  drawSeries(dLoss, "#c2410c", syLoss);
  drawSeries(gLoss, "#2563eb", syLoss);
  drawSeries(dFake, "#0d6b62", syProb, [6, 4]);

  ctx.strokeStyle = "rgba(13,107,98,0.45)";
  ctx.lineWidth = 1.5;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(sx(cur, n), pad.t);
  ctx.lineTo(sx(cur, n), h - pad.b);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = "#64748b";
  ctx.font = "9px ui-sans-serif, sans-serif";
  ctx.textAlign = "center";
  for (let i = 0; i < n; i += 2) {
    ctx.fillText(phases[i], sx(i, n), pad.t - 6);
  }
  ctx.textAlign = "right";
  [0, 0.6, 1.2, 1.8, 2.4].forEach((v) => ctx.fillText(v.toFixed(1), pad.l - 6, syLoss(v) + 3));
  ctx.textAlign = "left";
  [0, 0.25, 0.5, 0.75, 1.0].forEach((v) => ctx.fillText(v.toFixed(2), w - pad.r + 6, syProb(v) + 3));
  ctx.textAlign = "center";
  ctx.fillText("训练轮次 →", w / 2, h - pad.b + 14);

  ctx.fillStyle = "#64748b";
  ctx.font = "11px ui-sans-serif, sans-serif";
  ctx.save();
  ctx.translate(14, h / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText("Loss", 0, 0);
  ctx.restore();
  ctx.save();
  ctx.translate(w - 10, h / 2);
  ctx.rotate(Math.PI / 2);
  ctx.fillText("D(x̂)", 0, 0);
  ctx.restore();

  const legY = pad.t - 18;
  [
    ["#c2410c", "D loss"],
    ["#2563eb", "G loss"],
    ["#0d6b62", "D(x̂)"],
    ["rgba(37,99,235,0.25)", "G 步"],
    ["rgba(194,65,12,0.25)", "D 步"],
  ].forEach(([c, label], i) => {
    const lx = pad.l + i * 72;
    ctx.fillStyle = c;
    if (i < 3) ctx.fillRect(lx, legY - 8, 14, 3);
    else ctx.fillRect(lx, legY - 10, 14, 10);
    ctx.fillStyle = "#334155";
    ctx.textAlign = "left";
    ctx.font = i < 3 ? "10px ui-sans-serif,sans-serif" : "9px ui-sans-serif,sans-serif";
    ctx.fillText(label, lx + 18, legY);
  });

  const phase = phases[cur];
  const phaseNote =
    phase === "G"
      ? "G 步：生成器占优 → G loss 常反弹，D(x̂)↑（假样本更像真）"
      : phase === "D"
        ? "D 步：判别器占优 → D loss↓，D(x̂)↓（识破假样本）"
        : "均衡：拉锯减弱，D(x̂)→0.5";
  ctx.fillStyle = "#0f172a";
  ctx.font = "bold 10px ui-sans-serif,sans-serif";
  ctx.textAlign = "left";
  ctx.fillText(`当前 ${phase === "≈" ? "均衡" : phase + " 更新"}：D=${dLoss[cur].toFixed(2)} · G=${gLoss[cur].toFixed(2)} · D(x̂)=${dFake[cur].toFixed(2)}`, pad.l, h - 28);
  ctx.fillStyle = "#64748b";
  ctx.font = "10px ui-sans-serif,sans-serif";
  ctx.fillText(`${phaseNote} · 经典 GAN loss 呈震荡拉锯，而非像分类器那样单调下降`, pad.l, h - 12);
}

function ganCurveCaption(stepIdx) {
  const notes = [
    "起步 G 很弱：D(x̂) 低，但 G loss 高；接下来 D/G 会交替更新，曲线开始震荡。",
    "D 刚训练完：D loss 骤降、D(x̂) 被压到很低 — 这是 D 步的典型特征，不代表 G 已收敛。",
    "G 反击成功：D(x̂) 明显回升，G loss 先升后降 — 两条 loss 此消彼长，是零和博弈的正常现象。",
    "长期训练后振幅缩小：D(x̂) 围绕 0.5 波动，表示真假难分；若某一方 loss 持续单边下降，反而要警惕模式崩塌。",
  ];
  return notes[Math.min(Math.max(0, stepIdx), notes.length - 1)] ?? notes[0];
}

function landscapePanel(ox, quality, label, isFake) {
  const w = 220;
  const h = 140;
  const jitter = isFake ? (1 - quality) * 18 : 0;
  const sky = isFake ? `hsl(${200 + (1 - quality) * 40}, ${40 + quality * 20}%, ${78 + quality * 8}%)` : "#bae6fd";
  const mount = isFake ? `hsl(${150 + (1 - quality) * 30}, ${45 + quality * 15}%, ${28 + quality * 12}%)` : "#0d6b62";
  const sunOpacity = isFake ? 0.35 + quality * 0.55 : 1;
  const noise =
    isFake && quality < 0.85
      ? Array.from({ length: 24 }, (_, i) => {
          const nx = 20 + ((i * 37) % 180);
          const ny = 30 + ((i * 53) % 90);
          return `<rect x="${ox + nx}" y="${ny + 36}" width="3" height="3" fill="#94a3b8" opacity="${0.15 + (1 - quality) * 0.35}"/>`;
        }).join("")
      : "";
  return `<g>
    <text x="${ox + w / 2}" y="18" text-anchor="middle" class="gan-panel-label">${label}</text>
    <rect x="${ox}" y="28" width="${w}" height="${h}" rx="10" fill="#fff" stroke="#e2e8f0"/>
    <rect x="${ox}" y="28" width="${w}" height="${h * 0.42}" rx="10" fill="${sky}"/>
    <circle cx="${ox + w * 0.78 + jitter}" cy="${28 + h * 0.18 + jitter * 0.3}" r="${6 + quality * 5}" fill="#fbbf24" opacity="${sunOpacity}"/>
    <path d="M ${ox} ${28 + h * 0.72} L ${ox + w * 0.28 + jitter} ${28 + h * (0.38 - quality * 0.08)} L ${ox + w * 0.52} ${28 + h * 0.58} L ${ox + w * 0.78 - jitter} ${28 + h * (0.42 - quality * 0.05)} L ${ox + w} ${28 + h * 0.68} L ${ox + w} ${28 + h} L ${ox} ${28 + h} Z" fill="${mount}" opacity="${0.55 + quality * 0.4}"/>
    ${noise}
  </g>`;
}

function renderGanSamples(container, stepIdx = 0) {
  const qualities = [0.32, 0.22, 0.74, 0.93];
  const q = qualities[stepIdx] ?? 0.5;
  container.innerHTML = `
    <div class="gan-sample-viz">
      <svg class="gan-sample-svg" viewBox="0 0 520 180" role="img" aria-label="GAN 生成与真实样本对比">
        ${landscapePanel(24, q, "生成样本 x̂", true)}
        ${landscapePanel(276, 1, "真实样本 x", false)}
      </svg>
    </div>`;
}

function renderDiffusionStep(container, step) {
  const noise = step.noise ?? 0;
  const tMax = step.tMax ?? 1000;
  const t = step.t ?? Math.round((1 - noise) * tMax);
  const W = 560;
  const H = 248;
  const cx = W / 2;
  const cy = H / 2 - 28;
  const seed = Math.round(noise * 1000) + t;
  let rnd = seed || 1;
  const rand = () => {
    rnd = (rnd * 16807 + 12345) % 2147483647;
    return rnd / 2147483647;
  };
  const dots = [];
  for (let i = 0; i < 180; i++) {
    const ang = rand() * 6.28;
    const baseR = (1 - noise) * 58;
    const r = baseR + rand() * noise * 72;
    const dx = Math.cos(ang) * r;
    const dy = Math.sin(ang) * r;
    const gray = Math.round(100 + rand() * 80);
    dots.push(`<circle cx="${cx + dx}" cy="${cy + dy}" r="${noise > 0.6 ? 1.6 : 2.2}" fill="${noise > 0.6 ? `rgb(${gray},${gray},${gray})` : "#0d6b62"}" opacity="${0.35 + rand() * 0.55}"/>`);
  }
  const shapeOpacity = Math.max(0, 1 - noise * 1.15);
  const statusLabel = noise > 0.8 ? "高噪声 x_T" : noise < 0.12 ? "清晰 x̂₀" : `去噪中 · t=${t}`;
  const barW = W - 48;
  const barX = 24;
  const barY = H - 52;
  const fillW = Math.max(8, barW * (1 - noise));
  const phaseLabel = noise > 0.75 ? "前向加噪 →" : noise < 0.15 ? "← 反向去噪" : "反向采样 ←";
  container.innerHTML = `
    <div class="diffusion-step-viz">
      <svg class="diffusion-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="扩散去噪过程">
        <rect width="${W}" height="${H}" fill="#f8fafc" rx="8"/>
        <text x="24" y="22" font-size="11" fill="#64748b">训练：前向 q(x_t|x_{t-1}) 加噪 · 推理：反向 p(x_{t-1}|x_t) 去噪</text>
        <text x="${W - 24}" y="22" text-anchor="end" font-size="11" fill="#0d6b62">${statusLabel}</text>
        <g opacity="${shapeOpacity.toFixed(2)}">
          <circle cx="${cx - 28}" cy="${cy - 18}" r="14" fill="#0d6b62"/>
          <circle cx="${cx + 28}" cy="${cy - 18}" r="14" fill="#0d6b62"/>
          <path d="M ${cx - 52} ${cy + 6} Q ${cx} ${cy + 38} ${cx + 52} ${cy + 6} Z" fill="#2563eb"/>
        </g>
        ${dots.join("")}
        <text x="${barX}" y="${barY - 10}" font-size="10" fill="#334155">${phaseLabel} · t=${t} / ${tMax}</text>
        <rect x="${barX}" y="${barY}" width="${barW}" height="10" rx="5" fill="#e2e8f0"/>
        <rect x="${barX}" y="${barY}" width="${fillW.toFixed(1)}" height="10" rx="5" fill="#0d6b62"/>
        <text x="${barX}" y="${barY + 26}" font-size="10" fill="#64748b">x₀ 清晰</text>
        <text x="${barX + barW}" y="${barY + 26}" text-anchor="end" font-size="10" fill="#64748b">x_T 纯噪</text>
      </svg>
    </div>`;
}

function renderReprLandscape(container, step) {
  const repr = step.repr || "代数";
  const loss = step.loss ?? 10;
  const temp = step.temp ?? (step.annealStep ? 2.0 - step.annealStep * 0.5 : null);
  const W = 600;
  const H = 300;
  const particleT = step.annealStep != null ? 0.25 + step.annealStep * 0.18 : repr === "代数" ? 0.32 : 0.68;
  const panel = (title, key, jagged, ox) => {
    const pw = 268;
    const pad = { l: 24, r: 12, t: 44, b: 36 };
    const plotW = pw - pad.l - pad.r;
    const plotH = H - pad.t - pad.b - 52;
    const toX = (t) => ox + pad.l + t * plotW;
    const toY = (v) => pad.t + (1 - v) * plotH;
    const pts = [];
    for (let i = 0; i <= plotW; i++) {
      const t = i / plotW;
      const rough = jagged ? 0.52 + Math.sin(t * 14) * 0.32 + Math.sin(t * 31) * 0.08 : 0.12 + t * 0.35;
      pts.push(`${toX(t).toFixed(1)},${toY(rough).toFixed(1)}`);
    }
    const active = repr === key;
    const terrainY = jagged ? 0.52 + Math.sin(particleT * 14) * 0.32 : 0.12 + particleT * 0.35;
    const bx = toX(particleT);
    const by = toY(Math.min(loss / 14, terrainY));
    const pathHistory = step.history || [];
    const lossTagY = by < pad.t + 28 ? by + 22 : by - 14;
    return `<g>
      <rect x="${ox}" y="16" width="${pw}" height="${H - 48}" rx="10" fill="#fff" stroke="${active ? "#0d6b62" : "#e2e8f0"}" stroke-width="${active ? 2 : 1}"/>
      <text x="${ox + 12}" y="36" class="repr-panel-title">${title}</text>
      <path d="M ${pts.join(" L ")}" fill="none" stroke="${jagged ? "#94a3b8" : "#60a5fa"}" stroke-width="2.5" stroke-linecap="round"/>
      ${pathHistory.map((h, i) => `<circle cx="${toX(h.t)}" cy="${toY(h.y)}" r="4" fill="#cbd5e1" opacity="${0.4 + i * 0.15}"/>`).join("")}
      ${active ? `<circle cx="${bx}" cy="${by}" r="9" fill="#c2410c" stroke="#fff" stroke-width="2"/><text x="${Math.min(bx + 14, ox + pw - 48)}" y="${lossTagY}" class="repr-loss-tag">loss=${loss}</text>` : ""}
      ${active && step.acceptBad ? `<text x="${bx + 12}" y="${by + 18}" font-size="10" fill="#0d6b62">接受差解 ↑</text>` : ""}
    </g>`;
  };
  const tempBar = temp
    ? `<div class="repr-temp-bar"><span>温度 T=${temp.toFixed(1)}</span><div class="repr-temp-track"><i style="width:${Math.max(12, (1 - temp / 2.5) * 100)}%"></i></div><em>高→低 · 允许跳出局部最优</em></div>`
    : "";
  const formula = temp ? `<div data-math="anneal" class="repr-formula-slot"></div>` : "";
  container.innerHTML = `
    <div class="repr-landscape-viz">
      <svg class="repr-landscape-svg" viewBox="0 0 ${W} ${H - 36}" role="img" aria-label="表征搜索与模拟退火">
        <rect width="${W}" height="${H - 36}" fill="#f8fafc"/>
        ${panel("代数坐标 · 崎岖", "代数", true, 12)}
        ${panel("几何坐标 · 平滑", "几何", false, 308)}
      </svg>
      ${tempBar}
      ${formula}
      <p class="output-caption">${repr === "代数" ? "直接搜索卡在局部低谷 loss=12.4" : temp ? "退火允许上坡跳出 · 换几何后地形更平滑" : "换表征后沿缓坡继续下降到 loss=2.3"}</p>
    </div>`;
  if (temp && window.courseMath?.mountMath) {
    window.courseMath.mountMath(container.querySelector(".repr-formula-slot"), "anneal");
  }
}

function renderMDPBooking(container, step) {
  const states = [
    { id: "s0", label: "待搜索", short: "s₀", desc: "用户打开 App，尚未选航班", actions: ["搜索航班"], reward: 0 },
    { id: "s1", label: "已比价", short: "s₁", desc: "已看到候选航班列表", actions: ["选择航班"], reward: 1 },
    { id: "s2", label: "已下单", short: "s₂", desc: "订单已生成，待支付", actions: ["支付"], reward: 2 },
    { id: "s3", label: "已确认", short: "s₃", desc: "出票成功 · 终止状态", actions: ["—"], reward: 10, terminal: true },
  ];
  const cur = step.state ?? 0;
  const gamma = 0.9;
  const rewards = [0, 1, 2, 10];
  const edges = [
    { from: 0, to: 1, action: "搜索航班", r: 0 },
    { from: 1, to: 2, action: "选择航班", r: 1 },
    { from: 2, to: 3, action: "支付", r: 2 },
  ];
  const gTerms = [];
  let g = 0;
  for (let t = 0; t <= cur; t++) {
    g += Math.pow(gamma, t) * rewards[t];
    gTerms.push(`${t ? "+" : ""}${(Math.pow(gamma, t) * rewards[t]).toFixed(1)}`);
  }
  const edgeSvg = edges
    .map((e, i) => {
      const x1 = 60 + e.from * 130;
      const x2 = 60 + e.to * 130;
      const y = 72;
      const active = cur > e.from || (cur === e.from && step.action);
      return `<g class="${active ? "is-done" : ""} ${cur === e.from ? "is-current-edge" : ""}">
        <line x1="${x1 + 44}" y1="${y}" x2="${x2 - 8}" y2="${y}" stroke="${cur === e.from ? "#c2410c" : "#94a3b8"}" stroke-width="2" marker-end="url(#mdp-arr)"/>
        <text x="${(x1 + x2) / 2}" y="${y - 10}" text-anchor="middle" font-size="10" fill="#64748b">${e.action}</text>
        <text x="${(x1 + x2) / 2}" y="${y + 22}" text-anchor="middle" font-size="10" fill="#0d6b62">r=${e.r > 0 ? "+" : ""}${e.r}</text>
      </g>`;
    })
    .join("");
  const nodesSvg = states
    .map((s, i) => {
      const x = 60 + i * 130;
      const cls = i === cur ? "is-current" : i < cur ? "is-done" : "";
      return `<g class="mdp-node ${cls}" transform="translate(${x}, 48)">
        <rect width="88" height="52" rx="8" fill="${i === cur ? "#ecfdf5" : "#fff"}" stroke="${i === cur ? "#0d6b62" : "#cbd5e1"}" stroke-width="${i === cur ? 2.5 : 1}"/>
        <text x="44" y="20" text-anchor="middle" font-size="10" fill="#64748b">${s.short}</text>
        <text x="44" y="36" text-anchor="middle" font-size="11" font-weight="600" fill="#0f172a">${s.label}</text>
        ${s.terminal ? `<text x="44" y="48" text-anchor="middle" font-size="8" fill="#c2410c">终态</text>` : ""}
      </g>`;
    })
    .join("");
  const st = states[cur];
  container.innerHTML = `
    <div class="mdp-booking-viz">
      <svg class="mdp-booking-svg" viewBox="0 0 560 200" role="img" aria-label="订机票 MDP 状态图">
        <defs><marker id="mdp-arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#94a3b8"/></marker></defs>
        <text x="16" y="24" font-size="12" fill="#64748b">Agent（订票 App）↔ 环境（航班系统）· γ=${gamma}</text>
        ${edgeSvg}
        ${nodesSvg}
        <g transform="translate(16, 128)">
          <rect width="528" height="64" rx="8" fill="#fff" stroke="#e2e8f0"/>
          <text x="12" y="22" font-size="11" fill="#334155"><tspan font-weight="600">当前：</tspan>${st.desc}</text>
          <text x="12" y="40" font-size="11" fill="#334155"><tspan font-weight="600">动作 a：</tspan>${step.action || st.actions[0]}</text>
          <text x="12" y="56" font-size="11" fill="#0d6b62"><tspan font-weight="600">即时奖励 r：</tspan>${step.reward ?? st.reward} · <tspan font-weight="600">累积 G≈</tspan>${g.toFixed(1)} = ${gTerms.join("")}</text>
        </g>
      </svg>
      <div data-math="return_g" class="mdp-formula-slot"></div>
    </div>`;
  if (window.courseMath?.mountMath) {
    window.courseMath.mountMath(container.querySelector(".mdp-formula-slot"), "return_g");
  }
}

function bellmanDiagram(part) {
  const mk = (body, h = 148) => `<svg class="bellman-diagram-svg" viewBox="0 0 520 ${h}" role="img" preserveAspectRatio="xMidYMid meet">${body}</svg>`;
  if (part === "define") {
    return mk(`
      <rect width="520" height="148" fill="#f8fafc" rx="8"/>
      <text x="16" y="22" font-size="11" fill="#64748b">折扣回报 G = r₀ + γr₁ + γ²r₂ + …</text>
      <g transform="translate(24,38)"><rect width="72" height="40" rx="6" fill="#ecfdf5" stroke="#0d6b62"/><text x="36" y="25" text-anchor="middle" font-size="11">s₀ 待搜索</text></g>
      <text x="108" y="60" font-size="10" fill="#64748b">→ r=0 →</text>
      <g transform="translate(148,38)"><rect width="72" height="40" rx="6" fill="#fff" stroke="#cbd5e1"/><text x="36" y="25" text-anchor="middle" font-size="11">s₁ 已比价</text></g>
      <text x="232" y="60" font-size="10" fill="#64748b">→ r=1 →</text>
      <g transform="translate(272,38)"><rect width="72" height="40" rx="6" fill="#fff" stroke="#cbd5e1"/><text x="36" y="25" text-anchor="middle" font-size="11">s₂ …</text></g>
      <text x="360" y="60" font-size="10" fill="#0d6b62">γ=0.9 折扣未来奖励</text>
      <text x="16" y="132" font-size="11" fill="#334155">V(s) = 从 s 出发、按策略 π 行动的期望回报</text>`, 148);
  }
  if (part === "expect") {
    return mk(`
      <rect width="520" height="130" fill="#f8fafc" rx="8"/>
      <defs><marker id="bm-arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#0d6b62"/></marker></defs>
      <g transform="translate(40,26)"><rect width="80" height="44" rx="6" fill="#ecfdf5" stroke="#0d6b62" stroke-width="2"/><text x="40" y="28" text-anchor="middle" font-size="11">s</text></g>
      <line x1="120" y1="48" x2="200" y2="48" stroke="#0d6b62" stroke-width="2" marker-end="url(#bm-arr)"/>
      <text x="160" y="40" text-anchor="middle" font-size="10" fill="#c2410c">a, r</text>
      <g transform="translate(200,26)"><rect width="80" height="44" rx="6" fill="#fff" stroke="#cbd5e1"/><text x="40" y="28" text-anchor="middle" font-size="11">s′</text></g>
      <text x="320" y="38" font-size="11" fill="#334155">V(s) = E[r + γ V(s′)]</text>
      <text x="320" y="56" font-size="10" fill="#64748b">对下一状态转移求期望</text>
      <text x="16" y="118" font-size="11" fill="#334155">一步奖励 + 折扣后的下一状态价值</text>`);
  }
  if (part === "optimal") {
    return mk(`
      <rect width="520" height="130" fill="#f8fafc" rx="8"/>
      <text x="16" y="20" font-size="11" fill="#64748b">V*(s) = max_a [ r + γ V*(s′) ]</text>
      <g transform="translate(200,26)"><rect width="72" height="40" rx="6" fill="#ecfdf5" stroke="#0d6b62" stroke-width="2"/><text x="36" y="26" text-anchor="middle" font-size="11">s</text></g>
      <line x1="236" y1="66" x2="120" y2="86" stroke="#2563eb" stroke-width="2"/>
      <line x1="236" y1="66" x2="360" y2="86" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4 3"/>
      <g transform="translate(80,88)"><rect width="80" height="18" rx="4" fill="#dbeafe"/><text x="40" y="13" text-anchor="middle" font-size="9">a₁ → s′₁</text></g>
      <g transform="translate(320,88)"><rect width="80" height="18" rx="4" fill="#f1f5f9"/><text x="40" y="13" text-anchor="middle" font-size="9">a₂ → s′₂</text></g>
      <text x="16" y="118" font-size="11" fill="#334155">选使长期回报最大的动作（实线 = 最优分支）</text>`);
  }
  return mk(`
    <rect width="520" height="130" fill="#f8fafc" rx="8"/>
    <text x="16" y="20" font-size="11" fill="#64748b">TD：用采样目标 r+γV(s′) 更新 V(s)</text>
    <g transform="translate(32,34)"><rect width="88" height="40" rx="6" fill="#ecfdf5" stroke="#0d6b62"/><text x="44" y="25" text-anchor="middle" font-size="10">V(s) 旧值</text></g>
    <text x="140" y="56" font-size="16" fill="#64748b">→</text>
    <g transform="translate(168,34)"><rect width="120" height="40" rx="6" fill="#fff" stroke="#2563eb" stroke-width="2"/><text x="60" y="25" text-anchor="middle" font-size="10">V(s)+α·δ</text></g>
    <text x="310" y="42" font-size="10" fill="#334155">δ = r+γV(s′)−V(s)</text>
    <text x="310" y="60" font-size="10" fill="#64748b">无需等回合结束</text>
    <text x="16" y="118" font-size="11" fill="#334155">订机票：走一步即可用下一状态价值自举</text>`);
}

function renderBellmanExplainer(container, step) {
  const part = step.part ?? "define";
  const tabKeys = ["define", "expect", "optimal", "td"];
  const tabLabels = ["V(s)", "期望", "最优", "TD"];
  const panels = {
    define: { title: "状态价值 V(s)", body: "在策略 π 下，从状态 s 出发能期望获得多少<strong>折扣回报</strong>。", math: "return_g" },
    expect: { title: "Bellman 期望方程", body: "当前价值 = 走一步的即时奖励 + 折扣后的下一状态价值（对转移求期望）。", math: "bellman_expect" },
    optimal: { title: "最优 Bellman 方程", body: "最优策略下，选让长期回报最大的动作。", math: "bellman_optimal" },
    td: { title: "TD 学习：Bellman 的采样版", body: "不必等回合结束，用 r+γV(s′) 当作目标，向 Bellman 方程靠拢。", math: "td_update" },
  };
  const p = panels[part] || panels.define;
  const tabs = tabKeys
    .map((k, i) => `<button type="button" class="bellman-tab ${k === part ? "is-active" : ""}" data-bellman-step="${i}">${tabLabels[i]}</button>`)
    .join("");
  container.innerHTML = `
    <div class="bellman-explainer">
      <div class="bellman-tabs">${tabs}</div>
      ${bellmanDiagram(part)}
      <h4 class="bellman-title">${p.title}</h4>
      <p class="bellman-body">${p.body}</p>
      <div class="bellman-math-slot" data-math="${p.math}"></div>
      ${part === "td" ? `<p class="output-caption">订机票例：从「待搜索」走一步到「已比价」，用 V(已比价) 自举更新 V(待搜索)。</p>` : ""}
    </div>`;
  container.querySelectorAll("[data-bellman-step]").forEach((btn) => {
    btn.addEventListener("click", () => {
      container.dispatchEvent(new CustomEvent("course:demo-jump", { detail: { index: Number(btn.dataset.bellmanStep) } }));
    });
  });
  if (window.courseMath?.mountMath) {
    window.courseMath.mountMath(container.querySelector(".bellman-math-slot"), p.math);
  }
}

window.courseViz = {
  entropy,
  infoGain,
  fmt,
  renderFormula,
  renderLegend,
  renderDecisionTree,
  renderConfusionMatrix,
  renderMLP,
  renderMLPBackward,
  renderHeatmapLabeled,
  renderAttentionFlow,
  renderTransE,
  renderWord2Vec,
  renderLMChain,
  renderActorCritic,
  renderTDUpdate,
  renderCLIPPair,
  renderViTPatches,
  renderMAEFlow,
  renderReprLandscape,
  renderMDPBooking,
  renderBellmanExplainer,
  renderLogicLayers,
  drawXorDemo,
  renderWorkflow,
  drawMaePixelGrid,
  renderEpsilonBandit,
  renderAlphaFoldFlow,
  drawGanTrainingCurve,
  ganCurveCaption,
  drawScatterRegression,
  drawKMeans,
  drawPerceptron,
  drawConvGrid,
  renderStateFlow,
  renderMCTSTree,
  renderActivationCurves,
  renderXorDemo,
  renderGanSamples,
  renderDiffusionStep,
  drawActivationCurves,
  drawXorDemo,
};
})();
