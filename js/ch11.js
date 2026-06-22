"use strict";

/* Chapter 11 · 行动智能 — 对齐第5章 + MDP 架构图 */

const C = window.courseCopyPrompts?.ch11 || {};
const { renderStateFlow } = window.courseViz;

const ch11Config = {
  modules: {
    intro: {
      key: "intro",
      cells: [{
        prompt: "行动智能 = 智能体与环境循环交互。订机票案例：待搜索→已比价(+1)→已下单(+2)→已确认(+10)，折扣 γ=0.9。请先认准 **MDP 交互环架构图**：Agent 输出动作 a → 环境返回 r,s′ → 更新状态。",
        architectureKey: "mdp",
        vibeTip: "π(a|s) 是策略；V(s) 是状态价值；γ 折扣未来奖励。",
        copyPrompt: C.intro,
      }],
    },
    bellman: {
      key: "bellman",
      cells: [{
        prompt: "理解 TD 与 Actor-Critic 之前，先建立 **Bellman 方程**心智模型：状态价值如何由「即时奖励 + 未来价值」递归定义。",
        demoKey: "bellman",
        interactive: true,
        vibeTip: "教科书路径：回报 G → Bellman 期望 → 最优 Bellman → TD 采样近似。",
        copyPrompt: C.bellmanConcept,
      }],
    },
    hierarchy: {
      key: "hierarchy",
      cells: [{
        prompt: "11.3–11.4：大脑规划子目标（端杯→抓取→平移→放置），小脑做轨迹控制；模仿学习 + 域随机化增强鲁棒性。",
        demoKey: "hierarchy",
        interactive: true,
        vibeTip: "分层 = 不同时间尺度的决策；高层慢、低层快。",
        copyPrompt: C.hierarchy,
      }],
    },
    compare: {
      key: "compare",
      cells: [{
        prompt: "行动智能四块：**MDP** 形式化环境、**Actor-Critic** 学策略、**TD** 学价值、**ε-贪心** 平衡探索。请对照下表理解各自角色。",
        tableKey: "ch11-compare",
        outputLabel: "对比表",
        copyPrompt: C.compare,
      }],
    },
  },
  notebooks: {
    mdp: {
      key: "mdp",
      mentorKey: "ch11-mdp",
      title: "MDP 智能体环", subtitle: "观测 → 动作 → 奖励",
      cells: [
        {
          prompt: "订机票：待搜索 → 已比价(+1) → 已下单(+2) → 已确认(+10)。**Agent–Env 环**：每步 s → a → (r, s′)。",
          architectureKey: "mdp",
          vibeTip: "G = Σ γᵗ r_t；γ<1 才能看长远。",
          copyPrompt: C.mdpConcept,
        },
        {
          prompt: "对照下方**状态转移图**步进：每一步写清 s、a、r、s′。与第5章搜索一样，先把「状态空间」画清楚再谈算法。",
          demoKey: "mdp", labTarget: "mdp", interactive: true,
          copyPrompt: C.mdpDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch11-mdp" },
        { mentorCell: "selfCheck", mentorKey: "ch11-mdp" },
        { mentorCell: "when", mentorKey: "ch11-mdp", labTarget: "mdp" },
      ],
    },
    actor: {
      key: "actor",
      mentorKey: "ch11-actor",
      title: "Actor-Critic", subtitle: "策略 + 价值",
      cells: [
        {
          prompt: "对照 **Actor-Critic 架构图**：Actor 输出 π(a|s)，Critic 估计 V(s)，优势 A=R+γV(s′)−V(s) 指导更新。",
          architectureKey: "actor-critic",
          vibeTip: "A>0：这步比预期好，提高该动作概率。",
          copyPrompt: C.actorConcept,
        },
        {
          prompt: "观看步进：π、V、A 如何联动？",
          demoKey: "actor", labTarget: "actor", interactive: true,
          copyPrompt: C.actorDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch11-actor" },
        { mentorCell: "selfCheck", mentorKey: "ch11-actor" },
        { mentorCell: "when", mentorKey: "ch11-actor" },
      ],
    },
    td: {
      key: "td",
      mentorKey: "ch11-td",
      title: "TD(0) 学习", subtitle: "Bellman 自举",
      cells: [
        {
          prompt: "V(s) ← V(s) + α[r + γV(s′) − V(s)]。**不必等回合结束**，用下一状态价值自举。δ = r + γV(s′) − V(s) 是「惊喜程度」。",
          vibeTip: "TD 有偏但方差小；蒙特卡洛等到终局更准但慢。",
          copyPrompt: C.tdConcept,
        },
        {
          prompt: "观看步进：V(s) 如何从 2.00 更新到 2.52？",
          demoKey: "td", labTarget: "td", interactive: true,
          copyPrompt: C.tdDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch11-td" },
        { mentorCell: "selfCheck", mentorKey: "ch11-td" },
        { mentorCell: "when", mentorKey: "ch11-td" },
      ],
    },
    epsilon: {
      key: "epsilon",
      mentorKey: "ch11-epsilon",
      title: "ε-贪心", subtitle: "探索 vs 利用",
      cells: [
        {
          prompt: "以 ε 随机探索、1−ε 选当前最优。训练初期 ε 大，后期 ε→0。**探索不足会卡在次优**。",
          vibeTip: "八成选最好餐馆，两成随机探新店。",
          copyPrompt: C.epsilonConcept,
        },
        {
          prompt: "观看比例条步进：ε=0.4 → 0.15 → 0.02 各适合什么阶段？",
          demoKey: "epsilon", labTarget: "epsilon", interactive: true,
          copyPrompt: C.epsilonDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch11-epsilon" },
        { mentorCell: "selfCheck", mentorKey: "ch11-epsilon" },
        { mentorCell: "when", mentorKey: "ch11-epsilon" },
      ],
    },
  },
  demos: {
    bellman: {
      key: "bellman",
      stepLabels: ["回报 G", "Bellman", "最优", "TD"],
      trace: [
        { part: "define", title: "折扣回报 G", summary: "从当前步起，未来奖励按 γ 折扣求和。", reason: "γ<1 让智能体既看眼前也看长远。", fields: [{ label: "例", value: "0+0.9+1.62+…" }] },
        { part: "expect", title: "Bellman 期望方程", summary: "V(s) 等于走一步的期望回报。", reason: "把「长期」拆成「一步 + 未来」— 递归结构。", fields: [{ label: "核心", value: "r + γV(s′)" }] },
        { part: "optimal", title: "最优 Bellman", summary: "最优策略下选 max_a 的动作。", reason: "动态规划可解，但大状态空间需采样近似。", fields: [{ label: "符号", value: "V*(s)" }] },
        { part: "td", title: "TD(0) 自举", summary: "用一步样本 r+γV(s′) 更新 V(s)。", reason: "TD 是 Bellman 方程的随机近似。", fields: [{ label: "更新", value: "V←V+αδ" }] },
      ],
      render(v, s) { window.courseViz.renderBellmanExplainer(v, s); },
    },
    hierarchy: {
      key: "hierarchy",
      stepLabels: ["规划", "抓取", "平移", "放置"],
      trace: [
        { title: "高层规划", summary: "高层先把“端杯”拆成抓取、平移、放置三个子目标。", reason: "分层控制把长任务变成短时间尺度动作。", fields: [{ label: "高层输出", value: "子目标序列" }], phase: 0, labels: ["端杯", "抓取", "平移", "放置"] },
        { title: "低层执行·抓取", summary: "低层控制手部轨迹接近杯柄并闭合。", reason: "低层策略处理连续动作，不需要重新规划全局目标。", fields: [{ label: "控制量", value: "关节/速度" }], phase: 1, labels: ["端杯", "抓取", "平移", "放置"] },
        { title: "低层执行·平移", summary: "保持杯子稳定，把它移动到目标位置上方。", reason: "轨迹控制关注平滑和避障，而不是重新决定任务顺序。", fields: [{ label: "约束", value: "稳定 + 避障" }], phase: 2, labels: ["端杯", "抓取", "平移", "放置"] },
        { title: "完成放置", summary: "放置成功后，高层目标完成。", reason: "域随机化让低层在不同杯子、光照、摩擦条件下仍能执行。", fields: [{ label: "鲁棒性", value: "域随机化" }], phase: 3, labels: ["端杯", "抓取", "平移", "放置"] },
      ],
      render(v, s) {
        const labels = s.labels || ["端杯", "抓取", "平移", "放置"];
        renderStateFlow(v, labels, s.phase ?? 0);
        v.innerHTML += `<p class="output-caption">${s.phase === 0 ? "高层慢规划" : "低层快控制 · 模仿学习"}</p>`;
      },
    },
    mdp: {
      key: "mdp",
      architectureKey: "mdp",
      stepLabels: ["s₀ 待搜索", "s₁ 已比价", "s₂ 已下单", "s₃ 已确认"],
      trace: [
        { title: "s₀ 待搜索", summary: "用户打开订票 App，环境处于「待搜索」。Agent 必须选动作「搜索航班」。", reason: "MDP 五元组 (S,A,P,R,γ) 中，这是初始状态 s₀∈S。", state: 0, action: "搜索航班", reward: 0, fields: [{ label: "s", value: "待搜索" }, { label: "a", value: "搜索航班" }, { label: "r", value: "0" }] },
        { title: "s₁ 已比价", summary: "环境返回航班列表，状态变为「已比价」，即时奖励 +1。", reason: "P(s₁|s₀,搜索)=1；有进展但任务未完成。", state: 1, action: "选择航班", reward: 1, fields: [{ label: "s′", value: "已比价" }, { label: "r", value: "+1" }] },
        { title: "s₂ 已下单", summary: "用户选定航班并下单，奖励 +2（比比价更接近目标）。", reason: "越接近「已确认」，中间奖励可设计得越大。", state: 2, action: "支付", reward: 2, fields: [{ label: "s′", value: "已下单" }, { label: "r", value: "+2" }] },
        { title: "s₃ 已确认", summary: "支付成功、出票确认 — 终止状态，奖励 +10。", reason: "终止后无后续动作；G 会把 +10 折扣传回前面各状态。", state: 3, action: "—", reward: 10, fields: [{ label: "终止", value: "是" }, { label: "G", value: "≈9.8" }] },
      ],
      render(v, s) { window.courseViz.renderMDPBooking(v, s); },
    },
    actor: {
      key: "actor",
      architectureKey: "actor-critic",
      stepLabels: ["π", "V", "A", "更新"],
      trace: [
        { title: "Actor 输出策略", summary: "当前状态下，Actor 给「搜索」0.70、「等待」0.30。", reason: "π(a|s) 是动作概率分布，不是价值估计。", fields: [{ label: "π(搜索)", value: "0.70" }], actions: [{ name: "搜索", p: 0.7 }, { name: "等待", p: 0.3 }] },
        { title: "Critic 估价值", summary: "Critic 估计当前状态长期回报 V(s)=4.2。", reason: "V(s) 用来判断刚才动作是否比预期更好。", fields: [{ label: "V(s)", value: "4.2" }], v: 4.2, actions: [{ name: "搜索", p: 0.7 }, { name: "等待", p: 0.3 }] },
        { title: "计算优势 A", summary: "实际回报比预期高 1.8，说明「搜索」这步值得加强。", reason: "A=R+γV(s′)−V(s)，A>0 提高该动作概率。", fields: [{ label: "A", value: "+1.8" }], v: 4.2, advantage: 1.8, actions: [{ name: "搜索", p: 0.7 }, { name: "等待", p: 0.3 }] },
        { title: "更新策略", summary: "把「搜索」概率从 0.70 提高到 0.78。", reason: "Actor 按 Critic 给出的优势方向更新。", fields: [{ label: "π(搜索)", value: "0.70→0.78" }], v: 4.2, advantage: 1.8, actions: [{ name: "搜索", p: 0.78 }, { name: "等待", p: 0.22 }] },
      ],
      render(v, s) { window.courseViz.renderActorCritic(v, s); },
    },
    td: {
      key: "td",
      stepLabels: ["V旧", "转移", "目标", "V新"],
      trace: [
        { title: "旧估计 V(s)", summary: "当前把状态 s 的价值估为 2.00。", reason: "TD 更新从旧价值出发，不需要等整局结束。", fields: [{ label: "V(s)", value: "2.00" }], vOld: 2.0 },
        { title: "观察转移", summary: "执行动作后得到即时奖励 r=1，并到达 s′。", reason: "下一状态已有价值估计 V(s′)=4.00。", fields: [{ label: "r", value: "+1" }, { label: "V(s′)", value: "4.00" }], vOld: 2.0, r: 1, vNext: 4.0, target: 4.6 },
        { title: "TD 目标", summary: "用 r+γV(s′)=1+0.9×4=4.60 当作学习目标。", reason: "这就是 Bellman 自举：用下一状态估计补足未来回报。", fields: [{ label: "target", value: "4.60" }], vOld: 2.0, r: 1, vNext: 4.0, target: 4.6 },
        { title: "更新 V(s)", summary: "按 α=0.2 向目标靠近：2.00→2.52。", reason: "δ=4.60−2.00=2.60，只走一小步避免震荡。", fields: [{ label: "δ", value: "+2.60" }, { label: "V新", value: "2.52" }], vOld: 2.0, vNew: 2.52, r: 1, vNext: 4.0, target: 4.6 },
      ],
      render(v, s) { window.courseViz.renderTDUpdate(v, s); },
    },
    epsilon: {
      key: "epsilon", stepLabels: ["ε=0.4", "ε=0.15", "ε=0.02"],
      trace: [
        { title: "初期 · 多探索", eps: 0.4, summary: "40% 随机试新店，60% 选已知最优。", reason: "早期 Q 估计不可靠，需要主动收集信息。", fields: [{ label: "随机探索", value: "40%" }], pick: { mode: "explore", arm: 2 } },
        { title: "中期 · 平衡", eps: 0.15, summary: "主要利用当前最好选择，但仍保留少量探索。", reason: "继续检查是否有被低估的选项。", fields: [{ label: "随机探索", value: "15%" }], pick: { mode: "exploit", arm: 0 } },
        { title: "后期 · 近纯贪心", eps: 0.02, summary: "几乎总选 Q 最高的餐馆 A。", reason: "当估计稳定后，应把更多机会给高回报动作。", fields: [{ label: "随机探索", value: "2%" }], pick: { mode: "exploit", arm: 0 } },
      ],
      render(v, s) { window.courseViz.renderEpsilonBandit(v, s); },
    },
  },
  tables: {
    "ch11-compare": `<div class="table-wrap compact"><table class="run-table compact comparison-table"><thead><tr><th>概念</th><th>架构/公式</th><th>作用</th></tr></thead><tbody>
      <tr><td>MDP</td><td>Agent–Env 环</td><td>形式化</td></tr><tr><td>Actor-Critic</td><td>π + V</td><td>策略梯度</td></tr>
      <tr><td>TD(0)</td><td>V←V+αδ</td><td>价值学习</td></tr><tr><td>ε-greedy</td><td>随机/最优</td><td>探索</td></tr></tbody></table></div>`,
  },
  labAlgos: [
    { key: "bellman", label: "Bellman", demo: "bellman", desc: "回报 → Bellman 期望 → 最优 → TD 自举。" },
    { key: "mdp", label: "MDP", demo: "mdp", desc: "订机票状态图：s、a、r、G 逐步展开。" },
    { key: "actor", label: "Actor-Critic", demo: "actor", desc: "π 与 V 分工，优势 A 指导更新。" },
    { key: "td", label: "TD", demo: "td", desc: "Bellman 自举更新 V(s)。" },
    { key: "epsilon", label: "ε-贪心", demo: "epsilon", desc: "训练各阶段探索/利用比例。" },
  ],
};

courseShared.bootstrapChapter(
  {
    chapterNum: 11,
    pageTitle: "强化学习 · 分步理解", eyebrow: "《AI思维》第11章 · 行动智能", title: "智能体如何行动，订票案例讲清楚", readingMeta: "约 35 分钟 · Bellman + 4 种方法", sections: [{ id: "hero", label: "开篇" }, { id: "m0", label: "概览" }, { id: "m0b", label: "Bellman" }, { id: "m1", label: "MDP" }, { id: "m2", label: "学习" }, { id: "m3", label: "探索" }, { id: "m4", label: "对比" }, { id: "lab", label: "实验室" }],
  },
  ch11Config,
);
