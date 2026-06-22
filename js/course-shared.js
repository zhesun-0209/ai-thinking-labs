"use strict";

/* Shared course page utilities for chapters 6–12 */

let currentChapterNum = null;

function resolveCopyText(cell) {
  if (cell.mentorCell && cell.mentorKey && window.coursePedagogy?.buildMentorCopyPrompt) {
    return window.coursePedagogy.buildMentorCopyPrompt(cell.mentorKey, cell.mentorCell, currentChapterNum);
  }
  if (cell.mentorSummary && window.coursePedagogy?.buildMentorBundleCopyPrompt) {
    return window.coursePedagogy.buildMentorBundleCopyPrompt(
      cell.mentorSummary,
      currentChapterNum,
      cell.prompt,
      cell.labTarget,
      cell.whenCopyPrompt,
      cell.selfCheckCopyPrompt,
    );
  }
  if (cell.copyPrompt || cell.prompt) {
    return window.coursePrompts?.buildCopyPrompt(cell) || "";
  }
  return "";
}

async function copyToClipboard(text) {
  if (!text) return false;
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      /* fallback below */
    }
  }
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.setAttribute("readonly", "");
  ta.style.cssText = "position:fixed;left:-9999px;top:0";
  document.body.appendChild(ta);
  ta.select();
  let ok = false;
  try {
    ok = document.execCommand("copy");
  } catch {
    ok = false;
  }
  document.body.removeChild(ta);
  return ok;
}

function syncArchitectureForStep(container, step, demo) {
  const archKey = step.architectureKey || demo?.architectureKey;
  if (!archKey || !window.courseArch?.renderArchitecture) return;
  const archStep = step.architectureStep || demo?.architectureStep || {};
  const root =
    container.closest("article.algo-notebook") ||
    container.closest(".vibe-notebook") ||
    container.closest("section.chapter-section") ||
    document;
  root.querySelectorAll(`[data-architecture="${archKey}"]`).forEach((el) => {
    window.courseArch.renderArchitecture(el, archKey, archStep);
  });
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function escapeAttr(text) {
  return escapeHtml(text).replace(/"/g, "&quot;");
}

/** 轻量 Markdown：**粗体**、*斜体*；保留安全相对链接 */
function formatRichText(text) {
  if (!text) return "";
  const links = [];
  let s = String(text).replace(/<a\s+href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/gi, (full, href, label) => {
    if (!/^(?:[\w./#?=-]|\.html)+$/.test(href)) return full;
    const idx = links.length;
    links.push({ href, label });
    return `\x00L${idx}\x00`;
  });
  s = escapeHtml(s);
  s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, "<em>$1</em>");
  s = s.replace(/\n/g, "<br>");
  links.forEach((l, i) => {
    s = s.replace(
      `\x00L${i}\x00`,
      `<a href="${escapeAttr(l.href)}">${escapeHtml(l.label)}</a>`,
    );
  });
  return s;
}

function resetPageScroll() {
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  if (!location.hash) {
    requestAnimationFrame(() => window.scrollTo(0, 0));
  }
}

function getLabScrollTarget(section) {
  if (!section) return null;
  const compact = window.matchMedia("(max-width: 680px)").matches;
  if (compact) return section.querySelector(".lab-panel, .app-shell, .visual-workspace") || section;
  return section.querySelector(".tabs, .app-shell, .lab-panel") || section;
}

function scrollToHashAfterRender() {
  if (!location.hash) return;
  const id = decodeURIComponent(location.hash.slice(1));
  if (!id) return;
  const applyHashTarget = () => {
    const section = document.getElementById(id);
    if (!section) return;
    const target = id === "lab" ? getLabScrollTarget(section) : section;
    section.classList.add("is-visible");
    target.scrollIntoView({ block: "start" });
    setActiveSectionLink(id);
  };
  requestAnimationFrame(() => {
    requestAnimationFrame(applyHashTarget);
  });
  window.setTimeout(applyHashTarget, 120);
  window.setTimeout(applyHashTarget, 500);
  window.addEventListener("load", () => window.setTimeout(applyHashTarget, 0), { once: true });
}

function initCoursePage(config) {
  resetPageScroll();
  currentChapterNum = config.chapterNum ?? null;
  document.title = config.pageTitle;
  const brand = document.querySelector(".site-brand .eyebrow");
  const title = document.querySelector(".site-title");
  const reading = document.querySelector(".meta-reading");
  if (brand) brand.textContent = config.eyebrow;
  if (title) title.textContent = config.title;
  if (reading) reading.textContent = config.readingMeta;

  renderSectionNav(config.sections);
  renderMentorChapter(config);
  renderAllModules(config);
  wireCopyButtons();
  wireJumpLab();
  initLearningProgress();
  initRevealAnimations();
  wireLabKeyboard();
  scrollToHashAfterRender();
}

function renderSectionNav(sections) {
  const nav = document.getElementById("sectionNav");
  if (!nav) return;
  nav.innerHTML = sections
    .map((s) => `<a class="section-link" href="#${s.id}" data-section="${s.id}">${escapeHtml(s.label)}</a>`)
    .join("");
  nav.addEventListener("click", (e) => {
    const link = e.target.closest(".section-link[data-section]");
    if (!link) return;
    const id = link.dataset.section;
    if (id === "lab") {
      e.preventDefault();
      history.pushState(null, "", "#lab");
      const section = document.getElementById("lab");
      const target = getLabScrollTarget(section);
      section?.classList.add("is-visible");
      target?.scrollIntoView({ block: "start" });
    }
    setActiveSectionLink(id);
  });
  wireScrollSpy(sections);
}

function setActiveSectionLink(id) {
  document.querySelectorAll(".section-link[data-section]").forEach((link) => {
    link.classList.toggle("is-active", link.dataset.section === id);
  });
}

function wireScrollSpy(sections) {
  const links = [...document.querySelectorAll(".section-link")];
  const map = new Map(sections.map((s, i) => [s.id, i]));
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const idx = map.get(entry.target.id);
        if (idx === undefined) return;
        links.forEach((link, i) => link.classList.toggle("is-active", i === idx));
      });
    },
    { rootMargin: "-40% 0px -45% 0px", threshold: 0 },
  );
  sections.forEach((s) => {
    const el = document.getElementById(s.id);
    if (el) observer.observe(el);
  });
}

function renderMentorChapter(config) {
  const host = document.querySelector("[data-chapter-goals], [data-mentor-chapter]");
  if (!host || !config.chapterNum || !window.coursePedagogy) return;
  host.innerHTML = window.coursePedagogy.renderMentorChapterPanel(config.chapterNum);
}

function renderAllModules(config) {
  (config.modules || []).forEach((mod) => {
    const host = document.querySelector(`[data-module="${mod.key}"]`);
    if (!host) return;
    host.innerHTML = "";
    const wrap = document.createElement("div");
    wrap.className = "vibe-notebook";
    mod.cells.forEach((cell, i) => wrap.appendChild(buildCellPair(cell, `${mod.key}-${i}`, i + 1)));
    host.appendChild(wrap);
  });

  (config.notebooks || []).forEach((nb) => {
    const host = document.querySelector(`[data-notebook="${nb.key}"]`);
    if (!host) return;
    host.innerHTML = "";
    const article = document.createElement("article");
    article.className = "vibe-notebook algo-notebook";
    article.id = `notebook-${nb.key}`;
    article.innerHTML = `
      <header class="notebook-header">
        <h3>${escapeHtml(nb.title)}</h3>
        <p class="notebook-subtitle">${escapeHtml(nb.subtitle || "")}</p>
        ${nb.mentorKey && window.coursePedagogy ? window.coursePedagogy.renderMentorNotebookHeader(nb.mentorKey) : ""}
      </header>`;
    const body = document.createElement("div");
    body.className = "vibe-notebook-body";
    const nbCells = normalizeNotebookCells(nb.cells);
    const nbArch = inferNotebookArchitecture(nb.cells);
    nbCells.forEach((cell, i) => body.appendChild(buildCellPair(cell, `${nb.key}-${i}`, i + 1, nbArch)));
    article.appendChild(body);
    host.appendChild(article);
  });

  document.querySelectorAll("[data-step-demo]").forEach((el) => {
    const demoKey = el.dataset.stepDemo;
    const demo = config.demos?.[demoKey];
    if (demo) mountStepDemo(el, demo);
  });

  document.querySelectorAll("[data-static-table]").forEach((el) => {
    const key = el.dataset.staticTable;
    const table = config.tables?.[key];
    if (table) el.innerHTML = table;
  });

  document.querySelectorAll("[data-architecture]").forEach((el) => {
    const key = el.dataset.architecture;
    let step = {};
    try {
      if (el.dataset.architectureStep) step = JSON.parse(el.dataset.architectureStep);
    } catch {
      /* ignore */
    }
    if (window.courseArch?.renderArchitecture) window.courseArch.renderArchitecture(el, key, step);
  });

  if (config.renderLab) config.renderLab();
}

function normalizeNotebookCells(cells) {
  const out = [];
  let i = 0;
  while (i < cells.length) {
    const a = cells[i];
    const b = cells[i + 1];
    const c = cells[i + 2];
    if (
      a?.mentorCell === "misconception" &&
      b?.mentorCell === "selfCheck" &&
      c?.mentorCell === "when" &&
      a.mentorKey === b.mentorKey &&
      b.mentorKey === c.mentorKey
    ) {
      i += 3;
      continue;
    }
    out.push(a);
    i += 1;
  }
  return out;
}

function inferNotebookArchitecture(cells) {
  for (const cell of cells) {
    if (cell.architectureKey) return cell.architectureKey;
  }
  return null;
}

function cellHasVisual(cell) {
  return Boolean(
    cell.demoKey ||
      cell.architectureKey ||
      cell.html ||
      cell.tableKey ||
      cell.mentorSummary,
  );
}

function buildCellPair(cell, instanceId, index, notebookArchKey) {
  const pair = document.createElement("div");
  pair.className = "vibe-cell-pair";
  if (cell.interactive) pair.classList.add("vibe-cell-pair--interactive");

  const copyText = resolveCopyText(cell);

  const tip = cell.vibeTip || cell.tip;
  let mentorHtml = "";
  if (cell.mentorSummary && window.coursePedagogy?.renderMentorSummary) {
    mentorHtml = window.coursePedagogy.renderMentorSummary(cell.mentorSummary);
  } else if (cell.mentorCell && cell.mentorKey && window.coursePedagogy) {
    mentorHtml = window.coursePedagogy.renderMentorCell(cell.mentorCell, cell.mentorKey);
  }

  const archKey = cell.architectureKey || (cell.mentorSummary ? notebookArchKey : null);
  const hasVisual = cellHasVisual(cell) || Boolean(archKey && cell.mentorSummary);
  if (!hasVisual) pair.classList.add("vibe-cell-pair--text-only");

  const promptEl = document.createElement("div");
  promptEl.className = "vibe-cell vibe-prompt";
  const promptLabel = "要点";
  promptEl.innerHTML = `
    <div class="cell-header">
      <span class="cell-index">步骤 ${index}</span>
      <span class="cell-label">${promptLabel}</span>
    </div>
    <div class="prompt-body">
      ${mentorHtml}
      ${cell.prompt ? `<div class="vibe-prompt-text">${formatPromptText(cell.prompt)}</div>` : ""}
    </div>
    ${tip ? `<p class="vibe-tip"><span class="vibe-tip-label">学习提示</span>${escapeHtml(tip)}</p>` : ""}
    <div class="prompt-actions">
      ${copyText ? `<div class="copy-teach"><span>向 AI 提问练习</span><button type="button" class="primary-button copy-prompt-btn" data-copy="${escapeAttr(copyText)}" aria-label="复制${escapeAttr(cell.outputLabel || promptLabel)}学习 Prompt">复制学习 Prompt</button></div>` : ""}
      ${cell.labTarget || cell.labAlgo ? `<button type="button" class="ghost-button" data-jump-lab="${cell.labTarget || cell.labAlgo}">在实验室打开</button>` : ""}
    </div>`;

  const outputEl = document.createElement("div");
  outputEl.className = "vibe-cell vibe-output";
  outputEl.innerHTML = `
    <div class="cell-header">
      <span class="cell-index">步骤 ${index}</span>
      <span class="cell-label">${cell.outputLabel || "演示"}</span>
    </div>`;
  const outputBody = document.createElement("div");
  outputBody.className = "output-body";

  if (cell.demoKey) {
    const slot = document.createElement("div");
    slot.dataset.stepDemo = cell.demoKey;
    outputBody.appendChild(slot);
  } else if (archKey) {
    const slot = document.createElement("div");
    slot.className = "arch-slot";
    slot.dataset.architecture = archKey;
    if (cell.architectureStep) slot.dataset.architectureStep = JSON.stringify(cell.architectureStep);
    outputBody.appendChild(slot);
  } else if (cell.html) {
    outputBody.innerHTML = cell.html;
  } else if (cell.tableKey) {
    const t = document.createElement("div");
    t.dataset.staticTable = cell.tableKey;
    outputBody.appendChild(t);
  } else if (cell.mentorCell === "selfCheck") {
    const q = window.coursePedagogy?.notebooks?.[cell.mentorKey]?.selfCheck || "先自己想一想，再对照上文演示。";
    outputBody.innerHTML = `<div class="mentor-think-space"><p class="think-prompt">${escapeHtml(q)}</p></div>`;
  }

  if (outputBody.childNodes.length === 0 && outputBody.innerHTML === "") {
    outputEl.hidden = true;
  }

  outputEl.appendChild(outputBody);
  pair.append(promptEl, outputEl);
  return pair;
}

function formatPromptText(text) {
  if (!text) return "";
  return formatRichText(text);
}

function wireCopyButtons() {
  document.querySelectorAll(".copy-prompt-btn[data-copy]").forEach((btn) => {
    if (!btn.dataset.copy) {
      btn.hidden = true;
      return;
    }
    btn.addEventListener("click", async () => {
      const ok = await copyToClipboard(btn.dataset.copy);
      const prev = btn.textContent;
      btn.textContent = ok ? "已复制 ✓" : "复制失败";
      btn.classList.toggle("is-copied", ok);
      setTimeout(() => {
        btn.textContent = prev;
        btn.classList.remove("is-copied");
      }, 2000);
    });
  });
}

function wireJumpLab() {
  document.querySelectorAll("[data-jump-lab]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.jumpLab;
      const lab = document.getElementById("lab");
      if (lab) lab.scrollIntoView({ behavior: "smooth" });
      document.dispatchEvent(new CustomEvent("course:lab-select", { detail: { key: target } }));
    });
  });
}

/* Generic step player */

const stepDemoState = {};

function mountStepDemo(container, demo) {
  const id = container.dataset.stepDemo || demo.key;
  if (!stepDemoState[id]) stepDemoState[id] = { index: 0, playing: false, timer: null };

  const trace = demo.trace;
  const render = demo.render || defaultStepRender;

  const wrap = document.createElement("div");
  wrap.className = container.closest(".lab-panel") ? "worked-player worked-player--lab" : "worked-player";
  wrap.innerHTML = `
    <div class="worked-player-main">
      <div class="demo-visual demo-visual--rich" data-visual="${id}"></div>
      <div class="worked-controls-bar worked-controls-inline">
        <button type="button" class="step-btn demo-prev">‹ 上一步</button>
        <button type="button" class="step-btn demo-play">▶ 播放</button>
        <label class="worked-range"><span class="worked-range-label demo-range-label">步骤</span>
          <input type="range" class="demo-range" min="0" max="${trace.length - 1}" value="0" /></label>
        <button type="button" class="step-btn demo-next">下一步 ›</button>
      </div>
      <div class="demo-detail" data-detail="${id}"></div>
    </div>`;
  container.appendChild(wrap);

  const visual = wrap.querySelector(`[data-visual="${id}"]`);
  const detail = wrap.querySelector(`[data-detail="${id}"]`);
  const prev = wrap.querySelector(".demo-prev");
  const next = wrap.querySelector(".demo-next");
  const play = wrap.querySelector(".demo-play");
  const range = wrap.querySelector(".demo-range");
  const rangeLabel = wrap.querySelector(".demo-range-label");

  function paint() {
    const st = stepDemoState[id];
    const step = trace[st.index];
    render(visual, step, st.index, demo);
    syncArchitectureForStep(container, step, demo);
    detail.innerHTML = renderStepDetailPanel(step, st.index, trace.length, demo);
    range.value = String(st.index);
    rangeLabel.textContent = `第 ${st.index + 1} / ${trace.length} 步`;
    prev.disabled = st.index <= 0;
    next.disabled = st.index >= trace.length - 1;
    play.textContent = st.playing ? "⏸ 暂停" : "▶ 播放";
    wrap.querySelectorAll(`[data-step-nav="${id}"] [data-step]`).forEach((btn) => {
      const i = Number(btn.dataset.step);
      btn.classList.toggle("is-active", i === st.index);
      btn.classList.toggle("is-done", i < st.index);
    });
  }

  function go(i) {
    stepDemoState[id].index = Math.max(0, Math.min(trace.length - 1, i));
    paint();
  }

  prev.addEventListener("click", () => go(stepDemoState[id].index - 1));
  visual.addEventListener("course:demo-jump", (e) => {
    if (e.detail?.index != null) go(Number(e.detail.index));
  });
  next.addEventListener("click", () => go(stepDemoState[id].index + 1));
  range.addEventListener("input", () => go(Number(range.value)));
  play.addEventListener("click", () => {
    const st = stepDemoState[id];
    st.playing = !st.playing;
    clearInterval(st.timer);
    if (st.playing) {
      st.timer = setInterval(() => {
        if (st.index >= trace.length - 1) {
          st.playing = false;
          clearInterval(st.timer);
          paint();
          return;
        }
        go(st.index + 1);
      }, demo.intervalMs || 1400);
    }
    paint();
  });

  wrap.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-step]");
    if (btn && wrap.contains(btn)) go(Number(btn.dataset.step));
  });

  paint();
  wrap.setAttribute("tabindex", "0");
}

function renderStepDetailPanel(step, index, total, demo) {
  const labels = demo.stepLabels || traceDefaultLabels(total);
  const strip = labels
    .map((label, i) =>
      `<button type="button" class="step-nav-btn ${i === index ? "is-active" : ""} ${i < index ? "is-done" : ""}" data-step="${i}"><span class="step-nav-num">${i + 1}</span><span class="step-nav-label">${escapeHtml(label)}</span></button>`,
    )
    .join("");

  const fields = (step.fields || [])
    .map(
      (f) =>
        `<div class="detail-field ${f.wide ? "detail-wide" : ""}"><dt>${escapeHtml(f.label)}</dt><dd>${f.html || escapeHtml(f.value || "—")}</dd></div>`,
    )
    .join("");

  return `
    <section class="worked-step-panel" aria-label="步骤明细">
      <div class="step-nav-strip" data-step-nav="${demo.key}" role="tablist">${strip}</div>
      <div class="step-detail-card">
        <div class="step-detail-head">
          <h4 class="step-detail-title">${escapeHtml(step.title || `步骤 ${index}`)}</h4>
          <span class="step-detail-index">第 ${index + 1} / ${total} 步</span>
        </div>
        ${step.summary ? `<p class="step-detail-summary">${formatRichText(step.summary)}</p>` : ""}
        <dl class="step-detail-grid">${fields}</dl>
        ${step.reason ? `<p class="step-detail-reason"><strong>本步说明：</strong>${formatRichText(step.reason)}</p>` : ""}
      </div>
    </section>`;
}

function traceDefaultLabels(n) {
  return Array.from({ length: n }, (_, i) => (i === 0 ? "起点" : `步 ${i}`));
}

function defaultStepRender(container, step) {
  container.innerHTML = `<p class="output-caption">${escapeHtml(step.summary || step.reason || "")}</p>`;
}

/* Knowledge graph SVG */

const kgResizeObservers = new WeakMap();
let kgMarkerUid = 0;

function syncKnowledgeGraphSize(container) {
  const svg = container.querySelector(".kg-svg");
  if (!svg) return;
  const vb = svg.viewBox.baseVal;
  if (!vb.width || !vb.height) return;
  const width = svg.getBoundingClientRect().width || container.clientWidth;
  if (width <= 0) return;
  const naturalHeight = (width * vb.height) / vb.width;
  const isLab = Boolean(container.closest(".worked-player--lab"));
  const availableHeight = isLab ? Math.max(160, (container.clientHeight || 300) - 42) : naturalHeight;
  const height = isLab ? Math.min(naturalHeight, availableHeight, 224) : naturalHeight;
  svg.style.width = "100%";
  svg.style.setProperty("height", `${height}px`, "important");
  svg.style.setProperty("max-height", isLab ? `${height}px` : "none", "important");
  svg.style.display = "block";
}

function bindKnowledgeGraphResize(container) {
  syncKnowledgeGraphSize(container);
  requestAnimationFrame(() => syncKnowledgeGraphSize(container));
  if (typeof ResizeObserver === "undefined") return;
  let ro = kgResizeObservers.get(container);
  if (!ro) {
    ro = new ResizeObserver(() => syncKnowledgeGraphSize(container));
    kgResizeObservers.set(container, ro);
  }
  ro.observe(container);
}

function renderKnowledgeGraph(container, graph, state = {}) {
  const { nodes, edges } = graph;
  const arrowId = `kg-arrow-${++kgMarkerUid}`;
  const activeNodes = new Set(state.activeNodes || []);
  const activeEdges = new Set(state.activeEdges || []);
  const pathEdges = state.pathEdges || [];
  const highlightEdges = new Set(state.highlightEdges || []);

  const nodeList = Object.values(nodes);
  const nodeRadius = 30;
  const labelBelow = 52;
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  nodeList.forEach((n) => {
    minX = Math.min(minX, n.x - nodeRadius);
    maxX = Math.max(maxX, n.x + nodeRadius);
    minY = Math.min(minY, n.y - nodeRadius);
    maxY = Math.max(maxY, n.y + labelBelow);
  });
  const padX = 48;
  const padTop = 48;
  const padBottom = 80;
  const vbX = minX - padX;
  const vbY = minY - padTop;
  const vbW = maxX - minX + padX * 2;
  const vbH = maxY - minY + padTop + padBottom;

  const edgeMarkup = edges
    .map((e) => {
      const a = nodes[e.from];
      const b = nodes[e.to];
      const key = `${e.from}-${e.rel}-${e.to}`;
      const cls = ["graph-edge", activeEdges.has(key) ? "in-path" : "", pathEdges.includes(key) ? "in-final" : "", highlightEdges.has(key) ? "in-final" : ""]
        .filter(Boolean)
        .join(" ");
      const mx = (a.x + b.x) / 2;
      const my = (a.y + b.y) / 2;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const len = Math.hypot(dx, dy) || 1;
      const labelOffset = 34;
      const lx = mx + (-dy / len) * labelOffset;
      const ly = my + (dx / len) * labelOffset;
      const labelW = Math.max(36, String(e.rel).length * 14 + 16);
      return `
        <line class="${cls}" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" marker-end="url(#${arrowId})"></line>
        <rect class="graph-edge-label-bg" x="${lx - labelW / 2}" y="${ly - 14}" width="${labelW}" height="20" rx="10"></rect>
        <text class="graph-edge-label" x="${lx}" y="${ly}" text-anchor="middle">${escapeHtml(e.rel)}</text>`;
    })
    .join("");

  const nodeMarkup = Object.values(nodes)
    .map((n) => {
      const cls = ["graph-node", activeNodes.has(n.id) ? "is-current" : "", state.visited?.has(n.id) ? "is-visited" : ""]
        .filter(Boolean)
        .join(" ");
      return `
        <g class="${cls}" transform="translate(${n.x} ${n.y})">
          <circle r="24"></circle>
          <text class="node-id" dy="5">${escapeHtml(n.short || n.id)}</text>
          <text class="node-name" y="38" text-anchor="middle">${escapeHtml(n.name)}</text>
        </g>`;
    })
    .join("");

  const legend = state.legend
    ? `<div class="kg-legend">${state.legend.map((l) => `<span><i class="${l.cls}"></i>${escapeHtml(l.label)}</span>`).join("")}</div>`
    : "";

  container.innerHTML = `
    <div class="kg-wrap">
      <svg class="campus-svg kg-svg" viewBox="${vbX} ${vbY} ${vbW} ${vbH}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="知识图谱">
        <defs><marker id="${arrowId}" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#64748b"></path></marker></defs>
        ${edgeMarkup}${nodeMarkup}
      </svg>
      ${legend}
    </div>`;
  bindKnowledgeGraphResize(container);
}

/* Rule / fact panels for chaining */

function renderRulePanel(container, step) {
  const facts = (step.facts || [])
    .map((f) => `<span class="detail-tag ${f.new ? "is-next" : ""}">${escapeHtml(f.text)}</span>`)
    .join("");
  const goals = (step.goals || [])
    .map((g) => `<span class="detail-tag ${g.active ? "is-next" : ""}">${escapeHtml(g.text)}</span>`)
    .join("");
  const rules = (step.rules || [])
    .map((r) => `<div class="rule-line ${r.fired ? "is-fired" : ""}">${escapeHtml(r.text)}</div>`)
    .join("");

  container.innerHTML = `
    <div class="logic-demo-grid">
      <div class="logic-panel"><h5>事实库</h5><div class="detail-tags">${facts || '<span class="detail-tag empty">空</span>'}</div></div>
      ${goals ? `<div class="logic-panel"><h5>目标栈</h5><div class="detail-tags">${goals}</div></div>` : ""}
      <div class="logic-panel logic-panel-wide"><h5>规则</h5>${rules || "<p class='output-caption'>—</p>"}</div>
    </div>`;
}

function initLearningProgress() {
  const bar = document.getElementById("learningProgressBar");
  const text = document.getElementById("learningProgressText");
  const main = document.getElementById("main");
  if (!bar || !main) return;
  const update = () => {
    const rect = main.getBoundingClientRect();
    const total = main.scrollHeight - window.innerHeight;
    const scrolled = Math.min(total, Math.max(0, -rect.top));
    const pct = total <= 0 ? 0 : Math.round((scrolled / total) * 100);
    bar.style.width = `${pct}%`;
    if (text) text.textContent = `${pct}%`;
    bar.parentElement?.setAttribute("aria-valuenow", String(pct));
  };
  window.addEventListener("scroll", update, { passive: true });
  update();
}

function initRevealAnimations() {
  const sections = document.querySelectorAll(".reveal-section");
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    sections.forEach((el) => el.classList.add("is-visible"));
    return;
  }
  const reveal = (el, observer) => {
    el.classList.add("is-visible");
    observer?.unobserve(el);
  };
  const observer = new IntersectionObserver(
    (entries) => entries.forEach((e) => e.isIntersecting && reveal(e.target, observer)),
    { threshold: 0, rootMargin: "0px 0px -32px 0px" },
  );
  sections.forEach((el) => {
    observer.observe(el);
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight * 0.98 && rect.bottom > 0) reveal(el, observer);
  });
}

function isLabFocused() {
  const lab = document.getElementById("lab");
  if (!lab) return false;
  const rect = lab.getBoundingClientRect();
  return rect.top < window.innerHeight * 0.6 && rect.bottom > window.innerHeight * 0.2;
}

let labKeyboardWired = false;
function wireLabKeyboard() {
  if (labKeyboardWired) return;
  labKeyboardWired = true;
  document.addEventListener("keydown", (e) => {
    if (!isLabFocused()) return;
    const wrap = document.querySelector("#labPanel .worked-player");
    if (!wrap) return;
    const prev = wrap.querySelector(".demo-prev");
    const next = wrap.querySelector(".demo-next");
    const play = wrap.querySelector(".demo-play");
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      prev?.click();
    }
    if (e.key === "ArrowRight") {
      e.preventDefault();
      next?.click();
    }
    if (e.key === " ") {
      const tag = document.activeElement?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
      e.preventDefault();
      play?.click();
    }
  });
}

window.courseShared = {
  escapeHtml,
  formatRichText,
  resetPageScroll,
  initCoursePage,
  mountStepDemo,
  renderKnowledgeGraph,
  renderRulePanel,
  stepDemoState,
  renderCanvasDemo,
  renderHeatmap,
  renderTokenStrip,
  buildLabSwitcher,
  bootstrapChapter,
  copyToClipboard,
  resolveCopyText,
};

function renderCanvasDemo(container, step, drawFn) {
  container.innerHTML = `<div class="chart-canvas-wrap"><canvas></canvas></div>`;
  const wrap = container.querySelector(".chart-canvas-wrap");
  const canvas = wrap.querySelector("canvas");
  const aspect = step.canvasAspect ?? 280 / 560;

  const paint = () => {
    const availableW = Math.max(wrap.clientWidth - 24, 280);
    const isLab = Boolean(container.closest("#lab"));
    const maxH = isLab ? Math.min(window.innerHeight * 0.26, 220) : Math.min(window.innerHeight * 0.5, 420);
    const minH = isLab ? 150 : step.canvasAspect ? 200 : 180;
    let cssW = availableW;
    let cssH = Math.round(cssW * aspect);
    if (cssH > maxH) {
      cssH = Math.max(minH, Math.round(maxH));
      cssW = Math.min(availableW, Math.round(cssH / aspect));
    }
    const dpr = Math.min(window.devicePixelRatio || 1, 3);
    canvas.style.width = `${cssW}px`;
    canvas.style.height = `${cssH}px`;
    canvas.style.margin = "0 auto";
    canvas.width = Math.round(cssW * dpr);
    canvas.height = Math.round(cssH * dpr);
    const ctx = canvas.getContext("2d");
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, cssW, cssH);
    drawFn(ctx, cssW, cssH, step);
  };

  paint();
  if (typeof ResizeObserver !== "undefined") {
    const ro = new ResizeObserver(() => paint());
    ro.observe(wrap);
  }
}

function renderHeatmap(container, matrix, labels) {
  const max = Math.max(...matrix.flat(), 0.001);
  const rows = matrix.map((row, i) =>
    row
      .map((v, j) => {
        const t = v / max;
        const bg = `rgba(13,107,98,${0.12 + t * 0.75})`;
        return `<div class="heat-cell" style="background:${bg}" title="${labels?.[i] || i}→${labels?.[j] || j}: ${v.toFixed(2)}">${v.toFixed(2)}</div>`;
      })
      .join(""),
  );
  container.innerHTML = `<div class="heat-grid" style="grid-template-columns:repeat(${matrix[0]?.length || 1},1fr)">${rows.join("")}</div>`;
}

function renderTokenStrip(container, tokens, highlight = []) {
  const set = new Set(highlight);
  container.innerHTML = `<div class="token-strip">${tokens
    .map((t) => `<span class="token-chip ${set.has(t) ? "is-merge" : ""}">${escapeHtml(t)}</span>`)
    .join("")}</div>`;
}

function buildLabSwitcher(tabsEl, panelEl, algos, demos) {
  let active = algos[0].key;
  const setActiveTabState = () => {
    tabsEl.querySelectorAll(".tab").forEach((t) => {
      const selected = t.dataset.lab === active;
      t.classList.toggle("is-active", selected);
      t.setAttribute("aria-selected", String(selected));
      t.setAttribute("role", "tab");
    });
  };
  tabsEl.innerHTML = algos
    .map((a) => `<button type="button" class="tab ${a.key === active ? "is-active" : ""}" data-lab="${a.key}" title="${escapeAttr(a.desc || "")}">${a.label}</button>`)
    .join("");
  tabsEl.setAttribute("role", "tablist");
  setActiveTabState();
  const descEl = document.createElement("p");
  descEl.className = "lab-algo-desc";
  panelEl.before(descEl);
  function paint() {
    const cur = algos.find((a) => a.key === active);
    descEl.textContent = cur.desc || "";
    panelEl.innerHTML = "";
    const slot = document.createElement("div");
    slot.dataset.stepDemo = cur.demo;
    panelEl.appendChild(slot);
    mountStepDemo(slot, demos[cur.demo]);
  }
  const keepLabControlsInView = () => {
    requestAnimationFrame(() => {
      const section = document.getElementById("lab");
      const target = getLabScrollTarget(section) || tabsEl;
      target.scrollIntoView({ block: "start" });
    });
  };
  tabsEl.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-lab]");
    if (!btn) return;
    active = btn.dataset.lab;
    setActiveTabState();
    paint();
    keepLabControlsInView();
  });
  document.addEventListener("course:lab-select", (e) => {
    if (!e.detail?.key) return;
    active = e.detail.key;
    setActiveTabState();
    paint();
    keepLabControlsInView();
  });
  paint();
}

function bootstrapChapter(meta, config) {
  const merged = {
    ...config,
    pageTitle: meta.pageTitle,
    eyebrow: meta.eyebrow,
    title: meta.title,
    readingMeta: meta.readingMeta,
    sections: meta.sections,
    chapterNum: meta.chapterNum,
    modules: Object.values(config.modules || {}),
    notebooks: Object.values(config.notebooks || {}),
  };
  merged.renderLab =
    config.renderLab ||
    (() => {
      const tabs = document.getElementById("labTabs");
      const panel = document.getElementById("labPanel");
      if (tabs && panel && config.labAlgos) buildLabSwitcher(tabs, panel, config.labAlgos, config.demos);
    });
  const run = () => initCoursePage(merged);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
}
