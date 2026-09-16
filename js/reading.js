"use strict";

(() => {
  const storageKey = "ai-thinking:last-reading";
  const chapterMatch = location.pathname.match(/\/ch(5|6|7|8|9|10|11|12)\.html$/);
  const header = document.querySelector(".site-header");
  if (header && typeof ResizeObserver !== "undefined") {
    const observer = new ResizeObserver(() => {
      document.documentElement.style.setProperty("--header-height", `${Math.ceil(header.getBoundingClientRect().height)}px`);
    });
    observer.observe(header);
  }

  if (chapterMatch) {
    const chapter = Number(chapterMatch[1]);
    const save = (section) => {
      try {
        localStorage.setItem(storageKey, JSON.stringify({ chapter, section, title: document.querySelector(".site-brand .eyebrow")?.textContent || `第 ${chapter} 章` }));
      } catch { /* Reading remains available when storage is disabled. */ }
    };
    save(location.hash.slice(1));
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (visible.length) save(visible[0].target.id);
    }, { rootMargin: "-25% 0px -55% 0px", threshold: 0 });
    document.querySelectorAll("main > section[id]").forEach((section) => observer.observe(section));
  }

  const continuation = document.getElementById("continueReading");
  if (continuation) {
    try {
      const last = JSON.parse(localStorage.getItem(storageKey));
      if (Number.isInteger(last?.chapter) && last.chapter >= 5 && last.chapter <= 12) {
        const section = /^(hero|m[0-9]+|lab)$/.test(last.section) ? `#${last.section}` : "";
        continuation.href = `ch${last.chapter}.html${section}`;
        continuation.textContent = `继续阅读：${typeof last.title === "string" ? last.title.replace("《AI思维》", "").trim() : `第 ${last.chapter} 章`} →`;
        continuation.hidden = false;
      }
    } catch { /* A missing or outdated reading record is not an error. */ }
  }

  const search = document.getElementById("chapterSearch");
  if (search) {
    const cards = [...document.querySelectorAll(".hub-card")];
    const normalize = (value) => value.toLocaleLowerCase().replace(/[\s\-·]/g, "");
    const filter = () => {
      const query = normalize(search.value);
      let count = 0;
      cards.forEach((card) => {
        card.hidden = !normalize(`${card.textContent} ${card.dataset.search}`).includes(query);
        if (!card.hidden) count += 1;
      });
      document.getElementById("chapterCount").textContent = `${count} 个章节`;
      document.getElementById("searchEmpty").hidden = count > 0;
    };
    search.addEventListener("input", filter);
    search.addEventListener("search", filter);
    search.addEventListener("keydown", (event) => {
      if (event.key === "Escape") { search.value = ""; filter(); }
    });
  }
})();
