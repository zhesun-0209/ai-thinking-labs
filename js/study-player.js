"use strict";

/* Selected Lucide icons, ISC License, copyright (c) 2026 Lucide Icons and Contributors.
 * Permission to use, copy, modify, and/or distribute this software for any purpose
 * with or without fee is hereby granted, provided that the above copyright notice
 * and this permission notice appear in all copies. THE SOFTWARE IS PROVIDED "AS IS"
 * AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR
 * BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
 * CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
 * WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 * Arrow icons derived from Feather, MIT License, copyright (c) 2013-present Cole Bemis.
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in the
 * Software without restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
 * Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions: The above copyright notice and this
 * permission notice shall be included in all copies or substantial portions of the
 * Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
const studyIcons = {
  prev: '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
  next: '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
  play: '<path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"/>',
  pause: '<rect x="14" y="3" width="5" height="18" rx="1"/><rect x="5" y="3" width="5" height="18" rx="1"/>',
  reset: '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/>',
  zoom: '<path d="M15 3h6v6"/><path d="m21 3-7 7"/><path d="m3 21 7-7"/><path d="M9 21H3v-6"/>',
};
function studyIcon(name) {
  return `<svg class="study-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${studyIcons[name]}</svg>`;
}

// Keep controls mounted while the diagram and current explanation change.
window.studyPlayer = {
  mount(host, config) {
    const root = document.createElement("div");
    root.className = `worked-player study-player study-player--${config.kind || "default"}`;
    if (config.id) root.id = config.id;
    root.setAttribute("role", "group");
    root.setAttribute("aria-label", `${config.title}分步演示`);
    root.tabIndex = 0;
    const labels = config.labels;
    root.innerHTML = `
      <div class="study-toolbar">
        <strong class="study-title"></strong>
        <div class="study-actions">
          <button type="button" data-action="prev" aria-label="上一步" title="上一步">${studyIcon("prev")}</button>
          <button type="button" data-action="play" class="study-play" aria-label="播放" title="播放">${studyIcon("play")}</button>
          <button type="button" data-action="next" aria-label="下一步" title="下一步">${studyIcon("next")}</button>
          <button type="button" data-action="reset" aria-label="重新开始" title="重新开始">${studyIcon("reset")}</button>
          <button type="button" data-action="zoom" aria-label="放大图示" title="放大图示">${studyIcon("zoom")}</button>
        </div>
      </div>
      <div class="study-body">
        <div class="study-visual"></div>
        <div class="study-detail"></div>
      </div>
      <div class="study-progress">
        <label><span class="study-position" role="status" aria-live="polite"></span>
          <input type="range" min="0" max="${labels.length - 1}" value="0" aria-label="步骤进度" /></label>
        <div class="study-stops" role="group" aria-label="选择步骤"></div>
      </div>`;
    host.append(root);
    root.querySelector(".study-title").textContent = config.title;
    const stops = root.querySelector(".study-stops");
    labels.forEach((label, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.index = String(index);
      button.textContent = `${index + 1}. ${label}`;
      stops.append(button);
    });
    const visual = root.querySelector(".study-visual");
    const detail = root.querySelector(".study-detail");
    const range = root.querySelector("input");
    range.setAttribute("aria-label", `${config.title}步骤进度`);
    const play = root.querySelector('[data-action="play"]');
    let index = 0;
    let timer = null;
    let disposed = false;
    let dialog = null;
    const measure = () => {
      if (!config.measure || disposed || !root.isConnected) return;
      root.style.removeProperty("--study-detail-height");
      root.style.removeProperty("--study-diagram-height");
      let diagramHeight = 0;
      let detailHeight = 0;
      // Reserve the largest state at this width before the reader starts playback.
      labels.forEach((_, i) => {
        config.renderVisual(visual, i);
        config.renderDetail(detail, i);
        const content = visual.querySelector(".study-viz-content");
        diagramHeight = Math.max(diagramHeight, content?.getBoundingClientRect().height || 0);
        const explanation = detail.querySelector(".study-lesson-detail, .study-clip-detail");
        detailHeight = Math.max(detailHeight, explanation?.getBoundingClientRect().height || 0);
      });
      root.style.setProperty("--study-diagram-height", `${Math.ceil(diagramHeight)}px`);
      root.style.setProperty("--study-detail-height", `${Math.ceil(detailHeight)}px`);
    };
    const stop = () => {
      clearInterval(timer);
      timer = null;
      play.innerHTML = studyIcon("play");
      play.setAttribute("aria-label", "播放");
      play.title = "播放";
      play.setAttribute("aria-pressed", "false");
    };
    const paint = () => {
      config.renderVisual(visual, index);
      config.renderDetail(detail, index);
      config.onChange?.(index);
      range.value = String(index);
      range.setAttribute("aria-valuetext", `第 ${index + 1} 步，共 ${labels.length} 步：${labels[index]}`);
      root.querySelector(".study-position").textContent = `${index + 1} / ${labels.length}`;
      root.querySelector('[data-action="prev"]').disabled = index === 0;
      root.querySelector('[data-action="next"]').disabled = index === labels.length - 1;
      stops.querySelectorAll("button").forEach((button, i) => {
        button.classList.toggle("is-current", i === index);
        button.classList.toggle("is-done", i < index);
        if (i === index) button.setAttribute("aria-current", "step");
        else button.removeAttribute("aria-current");
      });
    };
    const go = (next) => {
      if (!Number.isFinite(next) || disposed) return;
      stop();
      index = Math.max(0, Math.min(labels.length - 1, next));
      paint();
    };
    const zoom = () => {
      stop();
      dialog = document.createElement("dialog");
      dialog.className = "study-zoom";
      dialog.setAttribute("aria-label", `${config.title}图示`);
      dialog.innerHTML = '<div class="study-zoom-head"><strong></strong><button type="button" autofocus>关闭</button></div><div class="study-zoom-visual"></div>';
      dialog.querySelector("strong").textContent = `${config.title} · ${labels[index]}`;
      root.append(dialog);
      dialog.showModal();
      config.renderVisual(dialog.querySelector(".study-zoom-visual"), index);
      dialog.querySelector("button").addEventListener("click", () => dialog.close());
      dialog.addEventListener("close", () => {
        dialog.remove();
        dialog = null;
        root.querySelector('[data-action="zoom"]').focus({ preventScroll: true });
      }, { once: true });
    };
    root.addEventListener("click", (event) => {
      const button = event.target.closest("button");
      if (!button || !root.contains(button)) return;
      if (button.dataset.index != null) go(Number(button.dataset.index));
      switch (button.dataset.action) {
        case "prev": go(index - 1); break;
        case "next": go(index + 1); break;
        case "reset": go(0); break;
        case "zoom": zoom(); break;
        case "play":
          if (timer) { stop(); break; }
          if (index === labels.length - 1) index = 0;
          paint();
          play.innerHTML = studyIcon("pause");
          play.setAttribute("aria-label", "暂停");
          play.title = "暂停";
          play.setAttribute("aria-pressed", "true");
          timer = setInterval(() => {
            if (!root.isConnected || document.hidden) { stop(); return; }
            index += 1;
            if (index >= labels.length - 1) { index = labels.length - 1; stop(); }
            paint();
          }, config.interval || 1600);
          break;
      }
    });
    range.addEventListener("input", () => go(Number(range.value)));
    root.addEventListener("course:pause", stop);
    root.addEventListener("course:layout", event => {
      stop();
      if (!event.target.closest("dialog")) { measure(); paint(); }
    });
    const onVisibility = () => { if (document.hidden) stop(); };
    document.addEventListener("visibilitychange", onVisibility);
    let width = 0;
    const observer = new ResizeObserver(([entry]) => {
      const nextWidth = Math.round(entry.contentRect.width);
      if (disposed || nextWidth === width) return;
      width = nextWidth;
      measure();
      paint();
    });
    observer.observe(visual);
    root.addEventListener("course:demo-dispose", () => {
      disposed = true;
      stop();
      observer.disconnect();
      document.removeEventListener("visibilitychange", onVisibility);
      dialog?.close();
    }, { once: true });
    stop();
    measure();
    paint();
    document.fonts?.ready.then(() => {
      if (!disposed && config.measure) { measure(); paint(); }
    });
    return { go, root };
  },
};

window.studyPlayer.refinePage = () => {
  if (!document.body.classList.contains("study-pilot")) return;
  const chapter = location.pathname.match(/ch(\d+)\.html$/)?.[1];
  if (chapter) {
    document.querySelectorAll(".chapter-section > .section-header").forEach((header, index) => {
      const heading = header.querySelector("h2");
      if (!heading || heading.querySelector(".study-section-number")) return;
      const number = document.createElement("span");
      number.className = "study-section-number";
      number.textContent = `${chapter}.${index + 1}`;
      heading.prepend(number);
      const eyebrow = header.querySelector(".eyebrow");
      if (eyebrow) eyebrow.hidden = true;
    });
  }
  // Keep optional practice next to its lesson without interrupting the explanation.
  document.querySelectorAll(".vibe-cell-pair").forEach(pair => {
    if (pair.querySelector(":scope > .study-resources")) return;
    pair.querySelectorAll(".cell-header").forEach(header => {
      if (["要点", "演示"].includes(header.querySelector(".cell-label")?.textContent.trim())) header.hidden = true;
    });
    const actions = pair.querySelector(".prompt-actions");
    if (!actions?.querySelector("button, a")) return;
    const resources = document.createElement("details");
    resources.className = "study-resources";
    const summary = document.createElement("summary");
    summary.textContent = "延伸练习";
    resources.append(summary, actions);
    pair.append(resources);
  });
};
document.addEventListener("DOMContentLoaded", window.studyPlayer.refinePage);
