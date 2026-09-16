"use strict";

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
          <button type="button" data-action="prev" aria-label="上一步" title="上一步">←</button>
          <button type="button" data-action="play" class="study-play">播放</button>
          <button type="button" data-action="next" aria-label="下一步" title="下一步">→</button>
          <button type="button" data-action="reset" aria-label="重新开始" title="重新开始">↺</button>
          <button type="button" data-action="zoom" aria-label="放大图示" title="放大图示">放大</button>
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
      const slots = ["title", "summary", "fields", "reason"];
      slots.forEach(key => root.style.removeProperty(`--study-${key}-height`));
      root.style.removeProperty("--study-diagram-height");
      const heights = {};
      let diagramHeight = 0;
      // Reserve the largest state at this width before the reader starts playback.
      labels.forEach((_, i) => {
        config.renderVisual(visual, i);
        config.renderDetail(detail, i);
        const content = visual.querySelector(".study-viz-content");
        diagramHeight = Math.max(diagramHeight, content?.getBoundingClientRect().height || 0);
        detail.querySelectorAll("[data-study-slot]").forEach(node => {
          const key = node.dataset.studySlot;
          heights[key] = Math.max(heights[key] || 0, node.getBoundingClientRect().height);
        });
      });
      root.style.setProperty("--study-diagram-height", `${Math.ceil(diagramHeight)}px`);
      Object.entries(heights).forEach(([key, value]) => root.style.setProperty(`--study-${key}-height`, `${Math.ceil(value)}px`));
    };
    const stop = () => {
      clearInterval(timer);
      timer = null;
      play.textContent = "播放";
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
          play.textContent = "暂停";
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
