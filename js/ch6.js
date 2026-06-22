"use strict";

/* Chapter 6 · 推理智能 */

const C = window.courseCopyPrompts?.ch6 || {};

const CH6_KG = {
  width: 640,
  height: 300,
  nodes: {
    luxun: { id: "luxun", name: "鲁迅", short: "鲁迅", x: 90, y: 150 },
    kr: { id: "kr", name: "狂人日记", short: "狂人", x: 280, y: 80 },
    hn: { id: "hn", name: "呐喊", short: "呐喊", x: 280, y: 220 },
    club: { id: "club", name: "文学周报社", short: "周报", x: 480, y: 150 },
    md: { id: "md", name: "茅盾文学奖", short: "茅奖", x: 520, y: 80 },
  },
  edges: [
    { from: "luxun", to: "kr", rel: "创作" },
    { from: "luxun", to: "hn", rel: "创作" },
    { from: "kr", to: "club", rel: "发表于" },
    { from: "hn", to: "club", rel: "发表于" },
    { from: "kr", to: "md", rel: "获得" },
  ],
};

const CH6_KG_MOYAN = {
  width: 640,
  height: 320,
  nodes: {
    my: { id: "my", name: "莫言", short: "莫言", x: 80, y: 160 },
    wa: { id: "wa", name: "《蛙》", short: "蛙", x: 240, y: 80 },
    hlg: { id: "hlg", name: "《红高粱》", short: "红高粱", x: 240, y: 220 },
    md: { id: "md", name: "茅盾文学奖", short: "茅奖", x: 420, y: 60 },
    canon: { id: "canon", name: "新中国长篇小说典藏", short: "典藏", x: 420, y: 160 },
    film: { id: "film", name: "电影《红高粱》", short: "电影", x: 420, y: 260 },
    bear: { id: "bear", name: "柏林金熊奖", short: "金熊", x: 560, y: 260 },
  },
  edges: [
    { from: "my", to: "wa", rel: "作品" },
    { from: "my", to: "hlg", rel: "作品" },
    { from: "wa", to: "md", rel: "获得" },
    { from: "hlg", to: "canon", rel: "入选" },
    { from: "hlg", to: "film", rel: "改编" },
    { from: "film", to: "bear", rel: "获得" },
  ],
};

const forwardTrace = [
  {
    title: "初始化",
    summary: "把已知事实放入工作记忆。",
    reason: "前向链从事实出发：先把「苏格拉底是人」放进待推理集合。",
    facts: [{ text: "人(苏格拉底)", new: true }],
    rules: [
      { text: "R1: 若 人(X) 则 会死(X)", fired: false },
      { text: "R2: 若 会死(X) 则 终有一死(X)", fired: false },
    ],
    fields: [
      { label: "策略", value: "前向链 · 数据驱动" },
      { label: "工作记忆", value: "人(苏格拉底)" },
    ],
  },
  {
    title: "匹配 R1",
    summary: "找到前提满足的规则并触发。",
    reason: "事实「人(苏格拉底)」满足 R1 的前提，推导出「会死(苏格拉底)」。",
    facts: [
      { text: "人(苏格拉底)" },
      { text: "会死(苏格拉底)", new: true },
    ],
    rules: [
      { text: "R1: 若 人(X) 则 会死(X) ✓", fired: true },
      { text: "R2: 若 会死(X) 则 终有一死(X)", fired: false },
    ],
    fields: [
      { label: "触发规则", value: "R1" },
      { label: "新事实", value: "会死(苏格拉底)" },
    ],
  },
  {
    title: "匹配 R2",
    summary: "继续扫描，直到无新事实。",
    reason: "「会死(苏格拉底)」触发 R2，得到目标结论「终有一死(苏格拉底)」。",
    facts: [
      { text: "人(苏格拉底)" },
      { text: "会死(苏格拉底)" },
      { text: "终有一死(苏格拉底)", new: true },
    ],
    rules: [
      { text: "R1 ✓", fired: true },
      { text: "R2: 若 会死(X) 则 终有一死(X) ✓", fired: true },
    ],
    fields: [
      { label: "触发规则", value: "R2" },
      { label: "结论", value: "终有一死(苏格拉底) — 证明完成" },
    ],
  },
];

const backwardTrace = [
  {
    title: "设定目标",
    summary: "从要证明的结论倒推。",
    reason: "后向链从目标「终有一死(苏格拉底)」出发，查找能推出它的规则。",
    goals: [{ text: "终有一死(苏格拉底)", active: true }],
    rules: [{ text: "R2: 若 会死(X) 则 终有一死(X)", fired: false }],
    fields: [
      { label: "策略", value: "后向链 · 目标驱动" },
      { label: "当前目标", value: "终有一死(苏格拉底)" },
    ],
  },
  {
    title: "分解子目标",
    summary: "匹配 R2，产生新子目标。",
    reason: "R2 的结论正是目标，于是需要证明子目标「会死(苏格拉底)」。",
    goals: [
      { text: "终有一死(苏格拉底)" },
      { text: "会死(苏格拉底)", active: true },
    ],
    rules: [{ text: "R2 ✓ 匹配", fired: true }],
    fields: [
      { label: "匹配规则", value: "R2" },
      { label: "新子目标", value: "会死(苏格拉底)" },
    ],
  },
  {
    title: "继续分解",
    summary: "再匹配 R1。",
    reason: "为证明「会死(苏格拉底)」，匹配 R1，子目标变为「人(苏格拉底)」。",
    goals: [
      { text: "终有一死(苏格拉底)" },
      { text: "会死(苏格拉底)" },
      { text: "人(苏格拉底)", active: true },
    ],
    rules: [
      { text: "R1: 若 人(X) 则 会死(X)", fired: false },
    ],
    fields: [
      { label: "匹配规则", value: "R1" },
      { label: "新子目标", value: "人(苏格拉底)" },
    ],
  },
  {
    title: "命中事实",
    summary: "子目标与事实库一致，证明完成。",
    reason: "事实库已有「人(苏格拉底)」，所有子目标得证，后向链结束。",
    facts: [{ text: "人(苏格拉底)", new: true }],
    goals: [{ text: "全部子目标已证 ✓" }],
    fields: [
      { label: "命中事实", value: "人(苏格拉底)" },
      { label: "结论", value: "终有一死(苏格拉底) — 证明完成" },
    ],
  },
];

const multihopTrace = [
  {
    title: "解析查询",
    summary: "把自然语言变成关系约束。",
    reason: "问题「鲁迅发表过哪些作品？」→ 在图上找 (鲁迅, 创作, ?作品) 并继续约束。",
    fields: [
      { label: "查询模板", value: "(鲁迅, 创作, ?X) ∧ (?X, 发表于, ?Y)" },
      { label: "策略", value: "后向链式图查询" },
    ],
    activeNodes: ["luxun"],
    activeEdges: [],
  },
  {
    title: "第一跳",
    summary: "沿「创作」边展开。",
    reason: "从鲁迅出发，找到创作关系连到《狂人日记》和《呐喊》。",
    activeNodes: ["luxun", "kr", "hn"],
    activeEdges: ["luxun-创作-kr", "luxun-创作-hn"],
    pathEdges: ["luxun-创作-kr", "luxun-创作-hn"],
  },
  {
    title: "第二跳",
    summary: "继续满足「发表于」约束。",
    reason: "两部作品都连到「文学周报社」，查询约束全部满足。",
    activeNodes: ["luxun", "kr", "hn", "club"],
    activeEdges: ["luxun-创作-kr", "luxun-创作-hn", "kr-发表于-club", "hn-发表于-club"],
    pathEdges: ["luxun-创作-kr", "kr-发表于-club", "luxun-创作-hn", "hn-发表于-club"],
    fields: [{ label: "答案", value: "《狂人日记》《呐喊》（均发表于文学周报社）" }],
  },
];

const pathRankTrace = [
  {
    title: "问题：代表作？",
    summary: "图谱中没有「代表作」这条边。",
    reason: "「代表作」不是简单事实，需要综合多条间接证据。",
    fields: [{ label: "缺失边", value: "无 (莫言, 代表作, ?)" }],
    activeNodes: ["my"],
  },
  {
    title: "路径 A",
    summary: "作品 → 获得茅盾文学奖",
    reason: "路径 A：《蛙》获得茅盾文学奖 — 权重高（权威奖项）。",
    activeNodes: ["my", "wa", "md"],
    activeEdges: ["my-作品-wa", "wa-获得-md"],
    pathEdges: ["my-作品-wa", "wa-获得-md"],
    fields: [{ label: "路径 A 得分", value: "3 分（茅盾文学奖）" }],
  },
  {
    title: "路径 B",
    summary: "作品 → 入选典藏",
    reason: "路径 B：《红高粱》入选新中国长篇小说典藏。",
    activeNodes: ["my", "hlg", "canon"],
    activeEdges: ["my-作品-hlg", "hlg-入选-canon"],
    pathEdges: ["my-作品-hlg", "hlg-入选-canon"],
    fields: [{ label: "路径 B 得分", value: "2 分（文学典藏）" }],
  },
  {
    title: "路径 C + 排序",
    summary: "多条路径计票，给出排序。",
    reason: "路径 C：《红高粱》→ 电影 → 金熊奖。汇总：《蛙》3 分、《红高粱》2+1 分 — 软自洽排序。",
    activeNodes: ["my", "wa", "hlg", "md", "canon", "film", "bear"],
    activeEdges: ["my-作品-wa", "wa-获得-md", "my-作品-hlg", "hlg-入选-canon", "hlg-改编-film", "film-获得-bear"],
    fields: [
      { label: "候选排序", value: "1.《蛙》3分 2.《红高粱》3分（并列，路径数多者优先）" },
      { label: "tie-break", value: "同分→路径条数多者胜；《红高粱》2条路径" },
      { label: "方法", value: "路径证据投票（软自洽）" },
    ],
  },
];

const ch6Config = {
  pageTitle: "推理算法 · 图谱分步理解",
  eyebrow: "《AI思维》第6章 · 推理智能",
  title: "四种推理策略，一张文学图谱讲清楚",
  readingMeta: "约 18 分钟 · 4 种策略 + 图谱实验",
  sections: [
    { id: "hero", label: "开篇" },
    { id: "m0", label: "表征" },
    { id: "m1", label: "演绎" },
    { id: "m2", label: "图谱" },
    { id: "m3", label: "图推理" },
    { id: "m4", label: "对比" },
    { id: "lab", label: "实验室" },
  ],
  modules: {
    logic: {
      key: "logic",
      cells: [
        {
          prompt:
            "命题逻辑用真/假描述世界；一阶逻辑把句子拆成对象和关系，能写「所有人…」「存在…」。推理 = 在既定表征下，按规则把隐含结论显式推出来。",
          tip: "不必背符号全称，先理解「事实 + 规则 → 结论」。",
          demoKey: "logic",
          interactive: true,
          copyPrompt: C.logic,
        },
      ],
    },
    kg: {
      key: "kg",
      cells: [
        {
          prompt:
            "知识图谱用三元组（主体, 关系, 客体）表示事实，如 (鲁迅, 创作, 《狂人日记》)。同一套结构也能表示本体约束。",
          tip: "三元组让知识可复用：换一个问题，往往只需换查询模板。",
          demoKey: "kg-static",
          interactive: true,
          copyPrompt: C.kg,
        },
      ],
    },
    compare: {
      key: "compare",
      cells: [
        {
          prompt: "四种推理策略对比：前向链撒网、后向链按需、多跳图查询、软自洽路径排序。",
          tableKey: "ch6-compare",
          copyPrompt: C.compare,
        },
        {
          prompt: "第 6 章图谱推理与第 5 章搜索的关系：都是在图上找路，但推理还有关系类型约束与证据排序。",
          html: `<p class="output-caption">→ 回顾 <a href="ch5.html#hero">第5章 搜索智能</a> 中的 BFS / A* 步进演示。</p>`,
          copyPrompt: C.compareSearch,
        },
      ],
    },
  },
  notebooks: {
    forward: {
      key: "forward",
      mentorKey: "ch6-forward",
      title: "前向链推理",
      subtitle: "从事实出发，能推则推，数据驱动",
      cells: [
        {
          prompt: "**前向链像撒网**：事实入工作记忆，扫描规则，能触发就加入新事实。与后向链的差别在**驱动方向**——数据驱动 vs 目标驱动。",
          vibeTip: "把事实池想成待扫描的集合：新事实入池，直到推不出新结论。",
          copyPrompt: C.forwardConcept,
        },
        {
          prompt: "请观看步进演示：注意事实库如何增长、哪条规则被触发（✓）。案例：事实 人(苏格拉底)，规则 R1/R2 推导「终有一死(苏格拉底)」。",
          demoKey: "forward",
          labTarget: "forward",
          interactive: true,
          copyPrompt: C.forwardDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch6-forward" },
        { mentorCell: "selfCheck", mentorKey: "ch6-forward" },
        {
          mentorCell: "when",
          mentorKey: "ch6-forward",
          prompt: "在实验室反复播放，直到你能**预测下一步哪条规则被触发**。",
          labTarget: "forward",
          copyPrompt: C.forwardLab,
        },
      ],
    },
    backward: {
      key: "backward",
      mentorKey: "ch6-backward",
      title: "后向链推理",
      subtitle: "从目标倒推，只走相关规则，目标驱动",
      cells: [
        {
          prompt: "**后向链像倒推计划**：从要证的目标出发，匹配规则产生子目标，直到命中事实库。目标明确时只碰相关规则。",
          vibeTip: "盯住目标栈：子目标如何一层层分解。",
          copyPrompt: C.backwardConcept,
        },
        {
          prompt: "观看步进：同一苏格拉底例子，对比前向链的步数与触发顺序。",
          demoKey: "backward",
          labTarget: "backward",
          interactive: true,
          copyPrompt: C.backwardDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch6-backward" },
        { mentorCell: "selfCheck", mentorKey: "ch6-backward" },
        { mentorCell: "when", mentorKey: "ch6-backward" },
      ],
    },
    multihop: {
      key: "multihop",
      mentorKey: "ch6-multihop",
      title: "多跳图谱推理",
      subtitle: "在图上找满足关系约束的路径",
      cells: [
        {
          prompt: "查询「鲁迅发表过哪些作品？」→ 模板 (鲁迅,创作,?X) 且 (?X,发表于,?Y)。**每一跳都要检查关系类型**——这是与裸图搜索的差别。",
          vibeTip: "像 SQL JOIN：关系类型是硬约束。",
          copyPrompt: C.multihopConcept,
        },
        {
          prompt: "观看步进：在文学图谱上逐跳匹配，看答案集合如何累积。",
          demoKey: "multihop",
          labTarget: "multihop",
          interactive: true,
          copyPrompt: C.multihopDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch6-multihop" },
        { mentorCell: "selfCheck", mentorKey: "ch6-multihop" },
        { mentorCell: "when", mentorKey: "ch6-multihop" },
      ],
    },
    pathrank: {
      key: "pathrank",
      mentorKey: "ch6-pathrank",
      title: "路径证据排序（软自洽）",
      subtitle: "信息不完整时，用多条路径投票排序",
      cells: [
        {
          prompt: "问「莫言的代表作？」图谱没有「代表作」边。收集路径 A/B/C 的证据，按权重计票给出排序。**硬约束仍要守**——关系类型不能乱连。",
          vibeTip: "软的是对「缺边」的容忍，不是对语义的放弃。",
          copyPrompt: C.pathrankConcept,
        },
        {
          prompt: "观看步进：哪条路径贡献最多票？最终排序是否符合你的直觉？",
          demoKey: "pathrank",
          labTarget: "pathrank",
          interactive: true,
          copyPrompt: C.pathrankDemo,
        },
        { mentorCell: "misconception", mentorKey: "ch6-pathrank" },
        { mentorCell: "selfCheck", mentorKey: "ch6-pathrank" },
        { mentorCell: "when", mentorKey: "ch6-pathrank" },
      ],
    },
  },
  demos: {
    logic: {
      key: "logic",
      stepLabels: ["命题", "一阶", "产生式"],
      trace: [
        {
          title: "命题逻辑",
          summary: "原子命题 + 连接词，用 ∧ 组合事实。",
          layer: 0,
          rows: [["命题逻辑", "「苏格拉底是人」∧「人终有一死」"]],
        },
        {
          title: "一阶逻辑",
          summary: "量词 + 谓词，可代入个体常量。",
          layer: 1,
          rows: [
            ["命题逻辑", "…"],
            ["一阶逻辑", "∀X 人(X)→会死(X)，X=苏格拉底"],
          ],
        },
        {
          title: "产生式规则",
          summary: "规则与事实库分离，便于推理引擎扫描触发。",
          layer: 2,
          facts: ["人(苏格拉底)", "会死(苏格拉底) ✓"],
          rows: [
            ["一阶逻辑", "…"],
            ["产生式", "IF 人(X) THEN 会死(X) · 事实库独立"],
          ],
        },
      ],
      render(visual, step) {
        window.courseViz.renderLogicLayers(visual, step);
      },
    },
    "kg-static": {
      key: "kg-static",
      stepLabels: ["作者", "作品", "发表"],
      trace: [
        {
          title: "中心实体",
          summary: "从作者「鲁迅」出发，作为查询锚点。",
          activeNodes: ["luxun"],
          activeEdges: [],
          legend: [{ cls: "path", label: "当前节点" }],
        },
        {
          title: "创作关系",
          summary: "鲁迅创作了《狂人日记》《呐喊》。",
          activeNodes: ["luxun", "kr", "hn"],
          activeEdges: ["luxun-创作-kr", "luxun-创作-hn"],
          highlightEdges: ["luxun-创作-kr", "luxun-创作-hn"],
          legend: [{ cls: "final", label: "本步新增关系" }, { cls: "path", label: "已激活" }],
        },
        {
          title: "发表关系",
          summary: "两部作品均发表于文学周报社。",
          activeNodes: ["luxun", "kr", "hn", "club"],
          activeEdges: ["luxun-创作-kr", "luxun-创作-hn", "kr-发表于-club", "hn-发表于-club"],
          highlightEdges: ["kr-发表于-club", "hn-发表于-club"],
          legend: [{ cls: "final", label: "本步新增" }, { cls: "path", label: "创作链" }],
        },
      ],
      render(visual, step) {
        visual.className = "demo-visual demo-visual--rich kg-canvas";
        courseShared.renderKnowledgeGraph(visual, CH6_KG, step);
      },
    },
    forward: {
      key: "forward",
      trace: forwardTrace,
      stepLabels: ["起点", "R1", "R2"],
      render(visual, step) {
        courseShared.renderRulePanel(visual, step);
      },
    },
    backward: {
      key: "backward",
      trace: backwardTrace,
      stepLabels: ["目标", "R2", "R1", "事实"],
      render(visual, step) {
        courseShared.renderRulePanel(visual, step);
      },
    },
    multihop: {
      key: "multihop",
      trace: multihopTrace.map((s) => ({
        ...s,
        legend: [
          { cls: "path", label: "当前路径" },
          { cls: "final", label: "满足约束的边" },
        ],
      })),
      stepLabels: ["查询", "1跳", "2跳"],
      render(visual, step) {
        visual.className = "demo-visual demo-visual--rich kg-canvas";
        courseShared.renderKnowledgeGraph(visual, CH6_KG, step);
      },
    },
    pathrank: {
      key: "pathrank",
      trace: pathRankTrace.map((s) => ({
        ...s,
        legend: [
          { cls: "path", label: "证据路径" },
          { cls: "final", label: "当前聚焦" },
        ],
      })),
      stepLabels: ["问题", "路径A", "路径B", "排序"],
      render(visual, step) {
        visual.className = "demo-visual demo-visual--rich kg-canvas";
        courseShared.renderKnowledgeGraph(visual, CH6_KG_MOYAN, step);
      },
    },
  },
  tables: {
    "ch6-compare": `<div class="table-wrap compact"><table class="run-table compact comparison-table">
      <thead><tr><th>策略</th><th>驱动</th><th>本页案例</th><th>特点</th></tr></thead>
      <tbody>
        <tr><td>前向链</td><td>事实</td><td>苏格拉底三段论</td><td>全面，可能组合爆炸</td></tr>
        <tr><td>后向链</td><td>目标</td><td>同上</td><td>目标明确时更高效</td></tr>
        <tr><td>多跳推理</td><td>查询模板</td><td>鲁迅作品查询</td><td>关系类型约束</td></tr>
        <tr><td>软自洽</td><td>证据路径</td><td>莫言代表作</td><td>缺边时给排序+理由</td></tr>
      </tbody></table></div>`,
  },
  renderLab() {
    const tabs = document.getElementById("labTabs");
    const panel = document.getElementById("labPanel");
    if (!tabs || !panel) return;
    courseShared.buildLabSwitcher(tabs, panel, [
      { key: "forward", label: "前向链", demo: "forward", desc: "苏格拉底三段论：从事实出发，R1→R2 逐步触发。" },
      { key: "backward", label: "后向链", demo: "backward", desc: "同一例子从目标倒推，分解子目标直到命中事实。" },
      { key: "multihop", label: "多跳", demo: "multihop", desc: "鲁迅文学图谱：(创作)→(发表) 两跳查询。" },
      { key: "pathrank", label: "路径排序", demo: "pathrank", desc: "莫言代表作：多条证据路径计票排序。" },
      { key: "kg-static", label: "文学图谱", demo: "kg-static", desc: "鲁迅作品三元组静态图谱。" },
    ], ch6Config.demos);
  },
};

function initCh6() {
  courseShared.initCoursePage({
    ...ch6Config,
    chapterNum: 6,
    modules: Object.values(ch6Config.modules),
    notebooks: Object.values(ch6Config.notebooks),
  });
}

document.addEventListener("DOMContentLoaded", initCh6);
