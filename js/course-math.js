"use strict";

/** 全站统一公式块：HTML + CSS 变量，避免 SVG 内联字号不一致 */
(function () {
  const formulas = {
    infonce: `
      <div class="math-block math-block--stack" role="img" aria-label="InfoNCE 对比损失">
        <div class="math-line math-line--hero">
          <span>L<sub>i</sub> = − log</span>
          <span class="math-frac" aria-hidden="true">
            <span class="math-frac-num">exp(s<sup>+</sup>)</span>
            <span class="math-frac-den">Σ<sub>j</sub> exp(s<sub>j</sub>)</span>
          </span>
        </div>
        <p class="math-note">正例分数在分子，batch 内全部图文对在分母</p>
      </div>`,

    clip_cosine: `
      <div class="math-block math-block--stack" role="img" aria-label="CLIP 余弦相似度">
        <div class="math-line math-line--hero">
          cos(v<sub>I</sub>, v<sub>T</sub>) =
          <span class="math-frac" aria-hidden="true">
            <span class="math-frac-num">v<sub>I</sub> · v<sub>T</sub></span>
            <span class="math-frac-den">‖v<sub>I</sub>‖ ‖v<sub>T</sub>‖</span>
          </span>
        </div>
        <p class="math-note">L2 归一化后 cos 等价于点积，取值范围 [−1, 1]</p>
      </div>`,

    bellman_expect: `
      <div class="math-block math-block--stack" role="img" aria-label="Bellman 期望方程">
        <div class="math-line math-line--hero">V(s) = E[ R + γ V(s′) | s, π ]</div>
        <p class="math-note">当前状态价值 = 即时奖励 + 折扣后的下一状态价值（按策略 π 求期望）</p>
      </div>`,

    bellman_optimal: `
      <div class="math-block math-block--stack" role="img" aria-label="最优 Bellman 方程">
        <div class="math-line math-line--hero">V*(s) = max<sub>a</sub> Σ P(s′|s,a) [ R(s,a) + γ V*(s′) ]</div>
        <p class="math-note">最优价值：选让长期回报最大的动作 a</p>
      </div>`,

    td_update: `
      <div class="math-block math-block--stack" role="img" aria-label="TD 更新">
        <div class="math-line math-line--hero">V(s) ← V(s) + α [ r + γ V(s′) − V(s) ]</div>
        <p class="math-note">δ = r + γV(s′) − V(s) 为 TD 误差；用一步样本近似 Bellman 目标</p>
      </div>`,

    advantage: `
      <div class="math-block" role="img" aria-label="优势函数">
        <div class="math-line math-line--hero">A = R + γ V(s′) − V(s)</div>
      </div>`,

    gan_d: `
      <div class="math-block math-block--stack" role="img" aria-label="判别器损失">
        <div class="math-line math-line--hero">L<sub>D</sub> = −E[log D(x)] − E[log(1 − D(G(z)))]</div>
        <p class="math-note">真样本判 1，假样本判 0</p>
      </div>`,

    gan_g: `
      <div class="math-block" role="img" aria-label="生成器损失">
        <div class="math-line math-line--hero">L<sub>G</sub> = −E[log D(G(z))]</div>
      </div>`,

    return_g: `
      <div class="math-block" role="img" aria-label="折扣回报">
        <div class="math-line math-line--hero">G<sub>t</sub> = r<sub>t</sub> + γ r<sub>t+1</sub> + γ² r<sub>t+2</sub> + …</div>
      </div>`,

    anneal: `
      <div class="math-block math-block--stack" role="img" aria-label="模拟退火接受概率">
        <div class="math-line math-line--hero">P(接受差解) = exp(−ΔE / T)</div>
        <p class="math-note">T 高时易跳出局部最优；T 降低后更贪心</p>
      </div>`,
  };

  function mathHtml(key) {
    return formulas[key] || "";
  }

  function mountMath(container, key) {
    if (!container) return;
    const html = mathHtml(key);
    if (html) container.innerHTML = html;
    else container.innerHTML = `<div class="formula-card"><code>${key}</code></div>`;
  }

  window.courseMath = { formulas, mathHtml, mountMath };
})();
