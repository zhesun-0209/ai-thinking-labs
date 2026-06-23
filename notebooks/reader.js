"use strict";

(function () {
  const btn = document.getElementById("toggleCode");
  if (!btn) return;

  let hidden = false;

  const sync = () => {
    document.body.classList.toggle("nb-hide-code", hidden);
    btn.textContent = hidden ? "显示代码" : "隐藏代码";
    btn.setAttribute("aria-pressed", hidden ? "true" : "false");
  };

  btn.addEventListener("click", () => {
    hidden = !hidden;
    sync();
  });

  sync();
})();
