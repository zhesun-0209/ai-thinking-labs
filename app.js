"use strict";

/* ========== Campus graph (book ch.5) ========== */

const GOAL_ID = "c1";
const START_ID = "x";

const CAMPUS_NODES = {
  x: { id: "x", name: "校门口", label: "x", x: 88, y: 248, h: 7 },
  c2: { id: "c2", name: "超市", label: "c2", x: 88, y: 72, h: 1 },
  j: { id: "j", name: "教学楼", label: "j", x: 248, y: 72, h: 4 },
  s2: { id: "s2", name: "实验楼", label: "s2", x: 408, y: 72, h: 4 },
  s1: { id: "s1", name: "食堂", label: "s1", x: 248, y: 248, h: 3 },
  t: { id: "t", name: "图书馆", label: "t", x: 408, y: 248, h: 2 },
  c1: { id: "c1", name: "操场", label: "c1", x: 558, y: 158, h: 0 },
};

const NODE_RADIUS = 22;
const SVG_VIEWBOX = "0 0 640 320";

const CAMPUS_EDGES = [
  { from: "x", to: "c2", cost: 7 },
  { from: "x", to: "j", cost: 2 },
  { from: "x", to: "s1", cost: 2 },
  { from: "j", to: "s2", cost: 4 },
  { from: "s2", to: "s1", cost: 1 },
  { from: "s1", to: "t", cost: 3 },
  { from: "s1", to: "c1", cost: 6 },
  { from: "t", to: "c1", cost: 2 },
];

const adjacency = buildAdjacency(CAMPUS_EDGES);

function buildAdjacency(edges) {
  const map = {};
  edges.forEach(({ from, to, cost }) => {
    (map[from] ||= []).push({ id: to, cost });
    (map[to] ||= []).push({ id: from, cost });
  });
  Object.values(map).forEach((list) => list.sort((a, b) => a.id.localeCompare(b.id)));
  return map;
}

function getNeighbors(nodeId) {
  return adjacency[nodeId] || [];
}

function heuristic(nodeId) {
  return CAMPUS_NODES[nodeId]?.h ?? 0;
}

function edgeCost(from, to) {
  return getNeighbors(from).find((n) => n.id === to)?.cost ?? 0;
}

function pathCost(path) {
  let total = 0;
  for (let i = 0; i < path.length - 1; i += 1) {
    total += edgeCost(path[i], path[i + 1]);
  }
  return total;
}

/* ========== Algorithm metadata ========== */

const algorithms = {
  dfs: {
    tab: "DFS",
    section: "5.2",
    title: "DFS 深度优先搜索",
    tagline: "一条路走到黑",
    strategy: "栈（后进先出）",
    summary:
      "深度优先搜索用栈管理待探索列表：总是从栈顶取地点展开，新发现的邻居压入栈顶。能系统地走遍整张图，但不保证找到最短或最便宜的路径。",
    narrative:
      "从校门口 x 出发：先沿一条路尽量走到底，走不通再回头，直到到达操场 c1。",
    pseudocode: `function dfs(start, goal):
  frontier = stack([start])
  visited = empty set
  parent = empty map

  while frontier is not empty:
    current = frontier.pop()
    if current in visited: continue
    mark visited
    if current is goal: return path(parent)

    for neighbor in neighbors(current) by 字母序:
      if neighbor not visited and not in frontier:
        parent[neighbor] = current
        frontier.push(neighbor)`,
    advancedSteps: [
      "先把起点放入待探索栈",
      "从栈顶取出一个状态",
      "检查它是不是目标",
      "若不是，把所有没去过且不在栈中的邻居压入栈顶",
      "重复 2-4，直到找到目标或栈为空",
    ],
    prompt: [
      "请用校园图实现 DFS。节点有 x、c2、j、s1、s2、t、c1，目标是操场 c1。",
      "frontier 使用栈；邻居按字母顺序处理，压栈时反向以保证先尝试字母序靠前节点。",
      "记录每一步 current、frontier、visited、parent。",
    ],
  },
  bfs: {
    tab: "BFS",
    section: "5.2",
    title: "BFS 广度优先搜索",
    tagline: "层层推进",
    strategy: "队列（先进先出）",
    summary:
      "广度优先搜索用队列管理待探索列表：从队头取出地点，新邻居加到队尾，像水波一样一层层向外扩散。在每条路代价相同的情况下，能保证找到步数最少的路径。",
    narrative:
      "从校门口逐层向外扩展：先处理离起点一步远的地点，再处理两步远的，直到到达 c1。",
    pseudocode: `function bfs(start, goal):
  frontier = queue([start])
  visited = empty set
  parent = empty map

  while frontier is not empty:
    current = frontier.dequeue()
    mark visited
    if current is goal: return path(parent)

    for neighbor in neighbors(current) by 字母序:
      if neighbor not visited and not in frontier:
        parent[neighbor] = current
        frontier.enqueue(neighbor)`,
    advancedSteps: [
      "先把起点放进待探索队列",
      "从队列最前面取出一个状态",
      "检查它是不是目标",
      "若不是，把所有没去过且不在队列中的邻居放到队尾",
      "重复 2-4，直到找到目标或队列为空",
    ],
    prompt: [
      "请把 DFS 改成 BFS。frontier 改为队列：队头出、队尾进。",
      "在校园图上从 x 搜索到 c1，说明 BFS 保证无权图最少步数。",
    ],
  },
  ucs: {
    tab: "UCS",
    section: "5.2",
    title: "UCS 一致代价搜索",
    tagline: "谁更便宜先走谁",
    strategy: "按累计代价最小",
    summary:
      "一致代价搜索每次取出「从起点走到这里花费最少」的地点展开，保证找到总代价最低的路径。",
    narrative:
      "比较从起点到各地点的累计代价，优先展开代价最小的，最终得到最便宜的路径。",
    pseudocode: `function ucs(start, goal):
  frontier = priority_queue(key = g)
  best_g[start] = 0

  while frontier is not empty:
    current = pop_min_g(frontier)
    if current is goal: return path

    for neighbor in neighbors(current):
      new_g = best_g[current] + cost(current, neighbor)
      if new_g < best_g[neighbor]:
        update parent and push frontier`,
    advancedSteps: [
      "把起点以 g=0 放入优先队列",
      "取出 g 最小的节点",
      "若是目标则停止（取出时停止，不是发现时）",
      "松弛邻居：若 new_g 更低则更新 parent 和队列",
      "重复直到队列为空",
    ],
    prompt: [
      "请实现 UCS。frontier 按累计成本 g(n) 排序。",
      "若发现到同一节点有更便宜路线，更新 parent。目标在取出 frontier 时停止。",
    ],
  },
  greedy: {
    tab: "Greedy",
    section: "5.3",
    title: "贪婪最佳优先搜索",
    tagline: "只跟着感觉走",
    strategy: "按估计距离最小",
    summary:
      "贪婪搜索每次取出「看起来离目标最近」的地点，不考虑已经走了多远，因此不保证找到最优路径。",
    narrative:
      "谁看起来离操场 c1 最近，就先展开谁——像只凭直觉选路，可能绕远。",
    pseudocode: `function greedy(start, goal):
  frontier = priority_queue(key = h)
  visited = empty set

  while frontier is not empty:
    current = pop_min_h(frontier)
    mark visited
    if current is goal: return path

    for neighbor in neighbors(current):
      if neighbor not visited:
        frontier.push(neighbor)`,
    advancedSteps: [
      "把起点放入按 h(n) 排序的优先队列",
      "取出 h 最小的节点",
      "检查是否为目标",
      "将未访问邻居加入队列",
      "重复直到找到目标",
    ],
    prompt: [
      "请实现贪婪搜索。h(n) 使用书中给定的到操场直线距离估计。",
      "frontier 按 h 排序，g 只记录不参与选择。说明为何不保证最低成本。",
    ],
  },
  astar: {
    tab: "A*",
    section: "5.3",
    title: "A* 搜索",
    tagline: "理性与直觉的握手",
    strategy: "按综合代价最小",
    summary:
      "A* 同时考虑已走代价 g 和估计剩余距离 h，取 g+h 最小的地点展开。在估计值合理时，能保证找到最优路径。",
    narrative:
      "既看已经走了多远，也看离目标还有多远，取两者之和最小的地点展开，通常比单纯贪婪更可靠。",
    pseudocode: `function astar(start, goal):
  frontier = priority_queue(key = g + h)
  best_g[start] = 0

  while frontier is not empty:
    current = pop_min_f(frontier)
    if current is goal: return path

    for neighbor in neighbors(current):
      new_g = best_g[current] + cost
      if new_g < best_g[neighbor]:
        update parent; push with f = new_g + h(neighbor)`,
    advancedSteps: [
      "起点入队，f = g + h",
      "取出 f 最小的节点",
      "若是目标则停止",
      "松弛邻居并更新 f 值",
      "重复直到队列为空",
    ],
    prompt: [
      "请在 UCS 基础上实现 A*。f(n)=g(n)+h(n)。",
      "解释为何第一步不选超市，以及为何经图书馆到操场更划算。",
    ],
  },
  minimax: {
    tab: "Minimax",
    section: "5.4",
    title: "MiniMax 博弈搜索",
    tagline: "考虑最坏情况",
    strategy: "我方取最大、对手取最小",
    summary:
      "MiniMax 用于双方对弈：轮到我时选得分最高的走法，轮到对手时假设他会选让我得分最低的应对。",
    narrative:
      "不能只算自己怎么走最好，还要假设对手会怎么为难你——在最坏情况下仍选相对最好的那一步。",
    pseudocode: `function minimax(state, depth, maximizing):
  if terminal or depth == 0:
    return evaluate(state)

  if maximizing:
  return max(minimax(child, depth-1, false))
  else:
  return min(minimax(child, depth-1, true))`,
    advancedSteps: [
      "轮到我方：选择评估值最大的走法（MAX）",
      "轮到对手：假设对手选让我方最差的走法（MIN）",
      "递归展开博弈树直到终局或限定深度",
      "叶节点用评估函数打分",
      "Alpha-Beta 剪枝：已有更好选择时跳过无望分支",
    ],
    prompt: [
      "请实现简化 MiniMax 博弈树可视化，展示 MAX/MIN 层交替。",
      "加入 Alpha-Beta 剪枝演示，说明为何可以跳过部分分支。",
    ],
  },
};

/* ========== Search trace engine ========== */

function makeEntry(nodeId, g, parent) {
  const h = heuristic(nodeId);
  return { id: nodeId, name: CAMPUS_NODES[nodeId].name, g, h, f: g + h, parent };
}

function runSearch(algorithmKey) {
  if (algorithmKey === "minimax") return [];

  const config = algorithms[algorithmKey];
  const frontier = [makeEntry(START_ID, 0, null)];
  const visited = new Set();
  const inFrontier = new Set([START_ID]);
  const parents = {};
  const gScores = { [START_ID]: 0 };
  const steps = [];

  steps.push(
    snapshot({
      algorithmKey,
      title: "初始化",
      explanation: `把起点 ${START_ID}（校门口）放入待探索列表。下一步按「${config.strategy}」取出候选地点。`,
      narrative: "初始化：校门口 x 加入待探索列表，准备取出第一个要展开的地点。",
      current: null,
      frontier: frontierForSnapshot(frontier, algorithmKey),
      visited,
      parents,
      gScores,
      path: [],
    }),
  );

  while (frontier.length > 0) {
    sortFrontierForSelection(frontier, algorithmKey);
    const current = takeCurrent(frontier, algorithmKey);
    inFrontier.delete(current.id);

    if (visited.has(current.id)) continue;

    visited.add(current.id);
    gScores[current.id] = current.g;

    const pathToCurrent = buildPath(parents, current.id);
    const added = [];
    const skipped = [];
    const foundGoal = current.id === GOAL_ID;

    if (!foundGoal) {
      const neighbors = getNeighbors(current.id);
      const ordered =
        algorithmKey === "dfs" ? [...neighbors].reverse() : neighbors;

      ordered.forEach((neighbor) => {
        const nb = neighbor.id;
        const inClosed = visited.has(nb);

        if (inClosed) {
          skipped.push(`${nb} 已访问`);
          return;
        }

        const nextG = current.g + neighbor.cost;
        const nextEntry = makeEntry(nb, nextG, current.id);

        if (algorithmKey === "ucs" || algorithmKey === "astar") {
          const prev = gScores[nb];
          if (prev === undefined || nextG < prev) {
            parents[nb] = current.id;
            gScores[nb] = nextG;
            const idx = frontier.findIndex((e) => e.id === nb);
            if (idx >= 0) frontier.splice(idx, 1);
            frontier.push(nextEntry);
            inFrontier.add(nb);
            added.push(nextEntry);
          } else {
            skipped.push(`${nb} 已有更低 g=${prev}`);
          }
          return;
        }

        if (algorithmKey === "dfs") {
          if (inFrontier.has(nb)) {
            if (!visited.has(nb)) parents[nb] = current.id;
            skipped.push(`${nb} 已在栈中，更新 parent`);
            return;
          }
          parents[nb] = current.id;
          gScores[nb] = nextG;
          frontier.push(nextEntry);
          inFrontier.add(nb);
          added.push(nextEntry);
          return;
        }

        if (algorithmKey === "bfs" || algorithmKey === "greedy") {
          if (inFrontier.has(nb)) {
            skipped.push(`${nb} 已在待探索列表中`);
            return;
          }
          parents[nb] = current.id;
          gScores[nb] = nextG;
          frontier.push(nextEntry);
          inFrontier.add(nb);
          added.push(nextEntry);
        }
      });
    }

    const finalPath = foundGoal ? pathToCurrent : pathToCurrent;

    steps.push(
      snapshot({
        algorithmKey,
        title: foundGoal ? `到达操场 ${current.id}` : `展开 ${CAMPUS_NODES[current.id].name}(${current.id})`,
        explanation: explainStep({ algorithmKey, current, added, skipped, foundGoal, path: finalPath }),
        narrative: narrativeForStep(algorithmKey, current, foundGoal, added, skipped),
        selectionReason: selectionReasonFor(algorithmKey, current),
        current,
        frontier: frontierForSnapshot(frontier, algorithmKey),
        visited,
        parents,
        gScores,
        path: finalPath,
        foundGoal,
      }),
    );

    if (foundGoal) break;
  }

  return steps;
}

function narrativeForStep(algorithmKey, current, foundGoal, added, skipped) {
  if (foundGoal) {
    return `到达目标 ${current.id}（${CAMPUS_NODES[current.id].name}），搜索结束。`;
  }
  const name = CAMPUS_NODES[current.id].name;
  const addedText = added.length
    ? `新加入待探索：${added.map((e) => e.id).join("、")}。`
    : "本步没有新邻居加入待探索。";
  if (algorithmKey === "dfs") return `展开 ${current.id}（${name}）。${addedText}下一个由栈顶决定。`;
  if (algorithmKey === "bfs") return `展开 ${current.id}（${name}）。${addedText}下一个由队头决定。`;
  if (algorithmKey === "ucs") return `展开 ${current.id}，累计代价 ${current.g}。${addedText}`;
  if (algorithmKey === "greedy") return `展开 ${current.id}，估计距离 ${current.h}。${addedText}`;
  return `展开 ${current.id}，综合值 ${current.f}（已走 ${current.g} + 估计 ${current.h}）。${addedText}`;
}

function selectionReasonFor(algorithmKey, current) {
  if (algorithmKey === "dfs") return `${current.id} 位于栈顶，所以被取出展开。`;
  if (algorithmKey === "bfs") return `${current.id} 位于队头，所以被取出展开。`;
  if (algorithmKey === "ucs") return `${current.id} 的累计代价 ${current.g} 是当前待探索列表中最小的。`;
  if (algorithmKey === "greedy") return `${current.id} 的估计距离 ${current.h} 看起来离操场最近。`;
  return `${current.id} 的综合值 ${current.f}（已走 ${current.g} + 估计 ${current.h}）最小。`;
}

function takeCurrent(frontier, algorithmKey) {
  if (algorithmKey === "dfs") return frontier.pop();
  return frontier.shift();
}

function sortFrontierForSelection(frontier, algorithmKey) {
  if (algorithmKey === "ucs") {
    frontier.sort((a, b) => a.g - b.g || a.id.localeCompare(b.id));
  } else if (algorithmKey === "greedy") {
    frontier.sort((a, b) => a.h - b.h || a.id.localeCompare(b.id));
  } else if (algorithmKey === "astar") {
    frontier.sort((a, b) => a.f - b.f || a.h - b.h || a.g - b.g || a.id.localeCompare(b.id));
  }
}

function frontierForSnapshot(frontier, algorithmKey) {
  const copy = frontier.map((e) => ({ ...e }));
  if (algorithmKey === "dfs") return copy.reverse();
  sortFrontierForSelection(copy, algorithmKey);
  return copy;
}

function snapshot(data) {
  return {
    algorithmKey: data.algorithmKey,
    title: data.title,
    explanation: data.explanation,
    narrative: data.narrative || "",
    selectionReason: data.selectionReason || "",
    current: data.current ? { ...data.current } : null,
    frontier: data.frontier.map((e) => ({ ...e })),
    visited: Array.from(data.visited),
    parents: { ...data.parents },
    gScores: { ...data.gScores },
    path: [...data.path],
    foundGoal: Boolean(data.foundGoal),
  };
}

function buildPath(parents, targetId) {
  const path = [];
  let cursor = targetId;
  while (cursor) {
    path.unshift(cursor);
    cursor = parents[cursor];
  }
  return path;
}

function explainStep({ algorithmKey, current, added, skipped, foundGoal, path }) {
  const config = algorithms[algorithmKey];
  if (foundGoal) {
    return `按「${config.strategy}」取出 ${current.id}，它就是目标操场。路径 ${path.map((id) => CAMPUS_NODES[id].name).join(" → ")}，累计成本 ${current.g}。`;
  }
  const scoreText = scoreForAlgorithm(algorithmKey, current);
  const addedText = added.length
    ? `新加入待探索：${added.map((e) => formatEntry(e, algorithmKey)).join("，")}。`
    : "没有新邻居。";
  const skippedText = skipped.length ? `跳过：${skipped.join("，")}。` : "";
  return `按「${config.strategy}」选择 ${current.id}${scoreText}。${addedText}${skippedText}`;
}

function scoreForAlgorithm(algorithmKey, entry) {
  if (algorithmKey === "dfs") return "（栈顶）";
  if (algorithmKey === "bfs") return "（队头）";
  if (algorithmKey === "ucs") return `，g=${entry.g} 最小`;
  if (algorithmKey === "greedy") return `，h=${entry.h} 最小`;
  return `，f=${entry.f} 最小`;
}

function formatEntry(entry, algorithmKey) {
  if (algorithmKey === "ucs") return `${entry.id}(代价${entry.g})`;
  if (algorithmKey === "greedy") return `${entry.id}(估计${entry.h})`;
  if (algorithmKey === "astar") return `${entry.id}(综合${entry.f})`;
  return `${entry.id}`;
}

/* ========== Minimax game tree ========== */

const MINIMAX_TREE = {
  id: "root",
  label: "开局",
  depth: 0,
  isMax: true,
  children: [
    {
      id: "eat",
      label: "吃炮",
      move: "吃炮（看似赚）",
      children: [
        {
          id: "opp-check",
          label: "对手将军",
          isMax: false,
          score: -100,
          terminal: true,
          pruned: false,
        },
      ],
    },
    {
      id: "defend",
      label: "防守",
      move: "防守一步",
      children: [
        {
          id: "opp-normal",
          label: "对手普通应",
          isMax: false,
          score: 5,
          terminal: true,
        },
        {
          id: "opp-attack",
          label: "对手进攻",
          isMax: false,
          score: -10,
          terminal: true,
          pruned: true,
        },
      ],
    },
    {
      id: "develop",
      label: "发展",
      move: "平稳发展",
      children: [
        {
          id: "opp-trade",
          label: "对手兑子",
          isMax: false,
          score: 8,
          terminal: true,
          pruned: true,
        },
      ],
    },
  ],
};

const MINIMAX_STEPS = buildMinimaxSteps();

function buildMinimaxSteps() {
  const steps = [
    {
      title: "博弈树介绍",
      narrative: "博弈搜索中双方轮流落子：不能只算己方最优，必须假设对手选让我方最糟的应对。",
      explanation: "与路径搜索不同：状态由双方交替推动，需展开博弈树而非单纯遍历图。",
      highlighted: ["root"],
      pruned: [],
      chosen: null,
      scores: {},
    },
    {
      title: "展开我方选择（MAX）",
      narrative: "轮到我走：吃炮、防守、发展，三条路都要比较。",
      explanation: "极大化层：我方尽量选择评估分更高的走法。",
      highlighted: ["root", "eat", "defend", "develop"],
      pruned: [],
      chosen: null,
      scores: {},
    },
    {
      title: "假设对手反击（MIN）",
      narrative: "如果吃炮，对手会将军——局面评估 -100。",
      explanation: "极小化层：假设对手选让我方最糟的应对。吃炮分支下限是 -100。",
      highlighted: ["eat", "opp-check"],
      pruned: [],
      chosen: "eat",
      scores: { eat: -100 },
    },
    {
      title: "Alpha-Beta 剪枝",
      narrative: "防守分支对手最多 -10；发展分支在展开前已被剪枝——已有防守保底 5 分。",
      explanation: "剪枝：若某分支上限不如已知最佳选择，就不必继续算下去（类比招聘：25万岗位不必继续面）。",
      highlighted: ["defend", "opp-normal"],
      pruned: ["opp-attack", "opp-trade", "develop"],
      chosen: "defend",
      scores: { eat: -100, defend: 5, develop: 8 },
    },
    {
      title: "选择防守",
      narrative: "不吃炮，先防守。博弈搜索比较的是最坏情况下的相对最好。",
      explanation: "MiniMax 结论：防守（最坏 -10 优于吃炮的 -100）。不要幻想最好上限，要看最糟下限。",
      highlighted: ["defend", "opp-normal"],
      pruned: ["opp-attack", "opp-trade", "eat", "opp-check"],
      chosen: "defend",
      scores: { eat: -100, defend: 5 },
    },
  ];
  return steps;
}

/* ========== Worked runs (book-aligned summaries) ========== */

const workedRuns = {
  dfs: {
    label: "深度优先",
    rule: "看栈顶",
    finalPath: ["x", "j", "s2", "s1", "c1"],
    note: "路径 x→j→s2→s1→c1，共 4 步；不保证最短。",
    narrative: "深度优先：先沿教学楼方向走到底，再回溯，最终到达操场。路径较长，共 4 步。",
  },
  bfs: {
    label: "广度优先",
    rule: "看队头",
    finalPath: ["x", "s1", "c1"],
    note: "路径 x→s1→c1，2 步；无权图保证最少步数。",
    narrative: "广度优先：一层层向外扩散，第二步就从食堂直达操场。",
  },
  ucs: {
    label: "一致代价",
    rule: "取 g 最小",
    finalPath: ["x", "s1", "t", "c1"],
    cost: 7,
    note: "路径 x→s1→t→c1，总成本 7（最优）。",
    narrative: "每次选累计代价最小的地点，经图书馆到达操场，总代价最低。",
  },
  greedy: {
    label: "贪婪搜索",
    rule: "取 h 最小",
    finalPath: ["x", "s1", "c1"],
    cost: 8,
    note: "路径 x→s1→c1，成本 8；h 陷阱导致非最优。",
    narrative: "第一步会被超市（h=1）诱惑并展开，发现死胡同后回溯，最终走食堂直达，总代价 8，不是最优 7。",
  },
  astar: {
    label: "A*",
    rule: "取 f 最小",
    finalPath: ["x", "s1", "t", "c1"],
    cost: 7,
    note: "路径 x→s1→t→c1，成本 7；与 UCS 同得最优。",
    narrative: "既考虑已走距离也考虑剩余估计，第一步不会只选看起来最近的超市。",
  },
};

const workedRunMeta = {
  dfs: { structure: "stack", structureName: "栈", selector: "栈顶", choiceRule: "后进先出，一条路走到底。", optimal: "不保证" },
  bfs: { structure: "queue", structureName: "队列", selector: "队头", choiceRule: "先进先出，一层层扩散。", optimal: "等权图最少步数" },
  ucs: { structure: "priority", structureName: "优先队列", selector: "代价最小", choiceRule: "累计代价最低者优先。", optimal: "保证最低代价" },
  greedy: { structure: "priority", structureName: "优先队列", selector: "估计最近", choiceRule: "看起来离目标最近者优先。", optimal: "不保证" },
  astar: { structure: "priority", structureName: "优先队列", selector: "综合最小", choiceRule: "已走代价加估计距离最小者优先。", optimal: "估计合理时最优" },
};

function tracesToWorkedSteps(trace) {
  return trace.map((step, index) => ({
    step: index,
    current: step.current?.id || "-",
    frontier: formatFrontierString(step.frontier, step.algorithmKey),
    visited: `[${step.visited.join(", ")}]`,
    note: step.narrative || step.explanation.slice(0, 60),
    narrative: step.narrative,
    selectionReason: step.selectionReason,
  }));
}

function formatFrontierString(frontier, algorithmKey) {
  if (!frontier.length) return "[]";
  return `[${frontier.map((e) => formatEntry(e, algorithmKey)).join(", ")}]`;
}

const traces = Object.fromEntries(
  Object.keys(algorithms)
    .filter((k) => k !== "minimax")
    .map((key) => [key, runSearch(key)]),
);

Object.keys(workedRuns).forEach((key) => {
  const goalStep = traces[key].find((s) => s.foundGoal);
  if (goalStep) {
    workedRuns[key].finalPath = goalStep.path;
    workedRuns[key].cost = goalStep.current?.g ?? pathCost(goalStep.path);
  }
  workedRuns[key].steps = tracesToWorkedSteps(traces[key]);
});

const workedState = {};
const workedPlayState = {};
const workedTimers = {};
const ONBOARDING_KEY = "search-vibe-notebook-v1";

/* ========== Vibe Coding notebooks ========== */

const CAMPUS_GRAPH_SPEC = `地点：x(校门口), c2(超市,距操场估计1), j(教学楼,估计4), s1(食堂,估计3), s2(实验楼,估计4), t(图书馆,估计2), c1(操场,目标)
路径与代价：x-c2=7, x-j=2, x-s1=2, j-s2=4, s2-s1=1, s1-t=3, s1-c1=6, t-c1=2
起点 x，目标 c1，同一地点的多个邻居按字母顺序处理`;

const C5 = window.courseCopyPrompts?.ch5 || {};

function buildCopyPrompt(cell) {
  const raw = (cell.copyPrompt || cell.prompt || "").trim();
  if (!raw) return "";
  return raw.replace(/<[^>]+>/g, "").replace(/\*\*/g, "").trim();
}

function stepNavLabel(traceStep, stepIndex) {
  if (stepIndex === 0) return "起点";
  const id = traceStep.current?.id;
  if (!id || id === "-") return "—";
  return CAMPUS_NODES[id]?.name || id;
}

function renderVisitedTags(visited) {
  if (!visited?.length) return '<span class="detail-tag empty">暂无</span>';
  return visited
    .map((id) => `<span class="detail-tag muted">${escapeHtml(id)}<em>${escapeHtml(CAMPUS_NODES[id]?.name || "")}</em></span>`)
    .join("");
}

function renderFrontierTags(frontier, algorithmKey) {
  if (!frontier?.length) return '<span class="detail-tag empty">暂无</span>';
  const meta = workedRunMeta[algorithmKey];
  return frontier
    .map((entry, i) => {
      const next = i === 0 ? `<i class="detail-tag-badge">${meta?.selector || "下一个"}</i>` : "";
      return `<span class="detail-tag ${i === 0 ? "is-next" : ""}">${next}${escapeHtml(formatEntry(entry, algorithmKey))}</span>`;
    })
    .join("");
}

function renderWorkedStepDetail(run, key, instanceKey, index, step, trace) {
  const strip = trace
    .map((t, i) => {
      const short = stepNavLabel(t, i);
      return `<button type="button" class="step-nav-btn ${i === index ? "is-active" : ""} ${i < index ? "is-done" : ""}" data-step="${i}" ${i === index ? 'aria-current="step"' : ""} title="步骤 ${i}：${escapeAttr(short)}"><span class="step-nav-num">${i}</span><span class="step-nav-label">${escapeHtml(short)}</span></button>`;
    })
    .join("");

  const currentLabel = step.current
    ? `<strong>${escapeHtml(step.current.id)}</strong> <span>${escapeHtml(CAMPUS_NODES[step.current.id]?.name || "")}</span>`
    : "—";

  return `
    <section class="worked-step-panel" aria-label="步骤明细">
      <div class="step-nav-strip" data-step-nav="${instanceKey}" role="tablist" aria-label="全部步骤">
        ${strip}
      </div>
      <div class="step-detail-card" role="tabpanel">
        <div class="step-detail-head">
          <h4 class="step-detail-title">${escapeHtml(step.title || `步骤 ${index}`)}</h4>
          <span class="step-detail-index">第 ${index} / ${trace.length - 1} 步</span>
        </div>
        <dl class="step-detail-grid">
          <div class="detail-field"><dt>当前地点</dt><dd>${currentLabel}</dd></div>
          <div class="detail-field detail-wide"><dt>待探索</dt><dd class="detail-tags">${renderFrontierTags(step.frontier, key)}</dd></div>
          <div class="detail-field detail-wide"><dt>已访问</dt><dd class="detail-tags">${renderVisitedTags(step.visited)}</dd></div>
        </dl>
        <p class="step-detail-reason"><strong>本步说明：</strong>${escapeHtml(step.selectionReason || step.narrative || "初始化：准备开始搜索。")}</p>
      </div>
    </section>`;
}

const vibeModules = {
  graph: {
    cells: [
      {
        prompt: `把校园路线画成一张搜索图：圆圈代表地点，连线代表可走的路（线上数字是代价），目标是到达操场 c1。\n\n请理解下面五个概念——\n· 待探索：还没展开、但已在候选名单里的地点\n· 已访问：已经展开过的地点\n· 路径来源：记录「这个地点是从哪里来的」，方便回溯整条路\n\n${CAMPUS_GRAPH_SPEC}`,
        copyPrompt: C5.graphIntro,
        vibeTip: "先认准地图上的七个地点和连线，再记五个概念。不必背英文术语。",
        output: { type: "graph-static" },
      },
      {
        prompt: "三种无信息搜索（深度优先、广度优先、一致代价）的差别，只在于「待探索列表」用什么结构、按什么规则取下一个地点。下面表格概括了这一点。",
        copyPrompt: C5.graphCompare,
        vibeTip: "学每种算法时，重点看「下一步选谁」——其他部分（已访问、路径来源）大同小异。",
        output: { type: "term-table" },
      },
    ],
  },
  compare: {
    cells: [
      {
        prompt: `在同一张校园图上，六种搜索策略各会走出怎样的路径？下表比较它们的选点规则、路径结果和能否保证最优。\n\n${CAMPUS_GRAPH_SPEC}`,
        copyPrompt: C5.compareTable,
        vibeTip: "点击表格中的某一行，可跳转到实验室查看该算法的完整步进过程。",
        output: { type: "compare-table" },
      },
      {
        prompt: "建议按下面顺序学习：先理解搜索图，再学深度优先和广度优先，然后加入路径代价和估计距离，最后了解博弈搜索。",
        copyPrompt: C5.learningPath,
        vibeTip: "每学完一种，在实验室里切换算法对比，印象会更深。",
        output: { type: "learning-path" },
      },
    ],
  },
};

const vibeNotebooks = {
  dfs: {
    title: "深度优先搜索（DFS）",
    subtitle: "待探索列表用栈——总是先处理最近加入的地点",
    cells: [
      {
        prompt: `从校门口 x 出发，尽量沿一条路走到底，走不通再回头——这就是深度优先搜索。\n\n请观看下方动画：注意当前展开的地点（高亮）、已访问过的地点，以及待探索列表里下一个要去哪里。\n\n${CAMPUS_GRAPH_SPEC}`,
        copyPrompt: C5.dfsIntro,
        vibeTip: "先跟着动画走一遍，不必纠结细节。重点感受「走到底再回头」的节奏。",
        labAlgo: "dfs",
        output: { type: "worked-map", algo: "dfs", withPseudo: true },
      },
      {
        prompt: "深度优先用栈存放待探索地点：新发现的邻居总是加在栈顶，下一步也从栈顶取。动画里「栈顶」高亮的就是即将展开的那个。",
        copyPrompt: C5.dfsStack,
        vibeTip: "只要记住：栈 = 后进先出 = 最近加入的最先被处理。",
        labAlgo: "dfs",
        output: { type: "frontier-focus", algo: "dfs" },
      },
      {
        prompt: "本例中深度优先走了 x→教学楼→实验楼→食堂→操场，共 4 步。广度优先只要 2 步。深度优先能保证找到路，但不保证步数最少。",
        copyPrompt: C5.dfsVsBfs,
        vibeTip: "对比两种算法时，固定同一张图、同一个起点和终点，差异一目了然。",
        output: { type: "compare-pair", algos: ["dfs", "bfs"] },
      },
      { mentorCell: "misconception", mentorKey: "ch5-dfs" },
      { mentorCell: "selfCheck", mentorKey: "ch5-dfs" },
      {
        mentorCell: "when",
        mentorKey: "ch5-dfs",
        prompt: "在实验室中可以切换算法、逐步或自动播放，反复观察深度优先的完整过程。",
        copyPrompt: C5.dfsLab,
        vibeTip: "遇到看不懂的步骤，点「技术细节」展开查看更完整的说明。",
        labAlgo: "dfs",
      },
    ],
  },
  bfs: {
    title: "广度优先搜索（BFS）",
    subtitle: "待探索列表用队列——先加入的先处理，像水波扩散",
    cells: [
      {
        prompt: `广度优先与深度优先的唯一核心差别：待探索列表改用队列。新邻居加到队尾，下一步从队头取——先发现的地点先被展开。\n\n${CAMPUS_GRAPH_SPEC}`,
        copyPrompt: C5.bfsIntro,
        vibeTip: "对比上一节的深度优先动画，只看「待探索」的取法有何不同。",
        labAlgo: "bfs",
        output: { type: "worked-map", algo: "bfs", withPseudo: true },
      },
      {
        prompt: "本例中，第一步展开校门口的三个邻居；第二步从队头取出食堂，发现它连着操场——搜索结束。总共 2 步，这是等权图上的最少步数。",
        copyPrompt: C5.bfsLayers,
        vibeTip: "广度优先像同心圆扩散：离起点近的先处理，所以第一次碰到目标时步数最少。",
        labAlgo: "bfs",
        output: { type: "insight", html: "<strong>层序展开</strong>：第一步处理校门口的所有邻居（超市、教学楼、食堂）；第二步从队头取出食堂，发现它直接连着操场。在每条路代价相同的情况下，广度优先保证步数最少。" },
      },
      {
        prompt: "深度优先与广度优先：待探索结构不同、本图路径不同、步数不同。深度优先适合「找任意一条路」，广度优先适合「找最少步数」。",
        copyPrompt: C5.bfsVsDfs,
        vibeTip: "两种算法都不考虑路径代价数字；遇到带权路径时，需要用一致代价搜索处理总花费。",
        output: { type: "compare-pair", algos: ["dfs", "bfs"] },
      },
      { mentorCell: "misconception", mentorKey: "ch5-bfs" },
      { mentorCell: "selfCheck", mentorKey: "ch5-bfs" },
      {
        mentorCell: "when",
        mentorKey: "ch5-bfs",
        prompt: "在实验室切换 BFS，对照层序展开与 2 步最短路径。",
        copyPrompt: C5.bfsIntro,
        labAlgo: "bfs",
      },
    ],
  },
  ucs: {
    title: "一致代价搜索（UCS）",
    subtitle: "待探索列表按累计代价排序——谁更便宜先走谁",
    cells: [
      {
        prompt: `当每条路的代价不同时，就不能只看步数了。一致代价搜索每次取出「从起点走到这里花费最少」的地点展开。\n\n${CAMPUS_GRAPH_SPEC}`,
        copyPrompt: C5.ucsIntro,
        vibeTip: "累计代价就是「从校门口走到当前地点一共花了多少」。",
        labAlgo: "ucs",
        output: { type: "worked-map", algo: "ucs", withPseudo: true },
      },
      {
        prompt: "本例最终路径是 x→食堂→图书馆→操场，总代价 7。动画里可看到每步为何选累计代价最小的那个地点。",
        copyPrompt: C5.ucsPath,
        vibeTip: "注意：到达目标后，要等「取出」目标时才停止，而不是刚「发现」目标就停。",
        labAlgo: "ucs",
        output: { type: "frontier-focus", algo: "ucs" },
      },
      {
        prompt: "广度优先只数步数，一致代价搜索看总花费。当所有路的代价都是 1 时，两者结果相近；本图各路代价不同，结果就不同了。",
        copyPrompt: C5.ucsVsBfs,
        vibeTip: "本例广度优先 2 步但代价 8，一致代价搜索 3 步但代价 7——步数少不等于花费少。",
        output: { type: "insight", html: "<strong>广度优先 vs 一致代价</strong>：广度优先按<strong>步数</strong>一层层扩展，适合每条路代价相同的情况；一致代价搜索按<strong>累计花费</strong>扩展，适合代价不同的情况。本图中广度优先 2 步但花费 8，一致代价搜索 3 步但花费 7。" },
      },
      { mentorCell: "misconception", mentorKey: "ch5-ucs" },
      { mentorCell: "selfCheck", mentorKey: "ch5-ucs" },
      {
        mentorCell: "when",
        mentorKey: "ch5-ucs",
        prompt: "在实验室播放 UCS，逐步对照累计代价 g 与最终路径 x→s1→t→c1。",
        copyPrompt: C5.ucsPath,
        labAlgo: "ucs",
      },
    ],
  },
  greedy: {
    title: "贪婪最佳优先搜索",
    subtitle: "待探索列表按估计距离排序——谁看起来离目标最近",
    cells: [
      {
        prompt: `给每个地点一个「到操场的估计距离」h。贪婪搜索每次取出 h 最小的地点——像只凭直觉选看起来最近的路。\n\n${CAMPUS_GRAPH_SPEC}`,
        copyPrompt: C5.greedyIntro,
        vibeTip: "h 是估计值，不是实际距离。本页已给出每个地点的 h，直接对照地图理解即可。",
        labAlgo: "greedy",
        output: { type: "worked-map", algo: "greedy", withPseudo: true },
      },
      {
        prompt: "动画第一步会展开超市（h 最小），但超市是死胡同。回溯后最终走 x→食堂→操场，花费 8，不如一致代价或 A* 的 7。",
        copyPrompt: C5.greedyTrap,
        vibeTip: "陷阱在「第一步」：只看 h 不看 g，且未验证是否有出路。",
        output: { type: "insight", html: "<strong>贪婪的陷阱</strong>：第一步必展开超市（h=1 最小），但 x→超市 就要 7 且无出路到操场。回溯后走 x→食堂→操场，花费 8；一致代价 / A* 经图书馆只需 7。" },
      },
      {
        prompt: "贪婪搜索只看估计距离 h；一致代价搜索只看累计花费 g。两者各走极端，也各有可能错过最优路径。",
        copyPrompt: C5.greedyVsUcs,
        vibeTip: "记住这个对比：A* 把已走代价 g 和估计距离 h 结合起来排序。",
        output: { type: "compare-pair", algos: ["greedy", "ucs"] },
      },
      { mentorCell: "misconception", mentorKey: "ch5-greedy" },
      { mentorCell: "selfCheck", mentorKey: "ch5-greedy" },
      {
        mentorCell: "when",
        mentorKey: "ch5-greedy",
        prompt: "在实验室播放贪婪搜索，重点看第一步展开超市与回溯过程。",
        copyPrompt: C5.greedyTrap,
        labAlgo: "greedy",
      },
    ],
  },
  astar: {
    title: "A* 搜索",
    subtitle: "待探索列表按「已走+估计」排序——既看已走距离，也看剩余估计",
    cells: [
      {
        prompt: `A* 把累计花费 g 和估计距离 h 加在一起比较：谁的总分 g+h 最小，谁先展开。这样既不会只看直觉（贪婪），也不会完全忽略方向（一致代价）。\n\n${CAMPUS_GRAPH_SPEC}`,
        copyPrompt: C5.astarIntro,
        vibeTip: "第一步为什么不先选超市？因为已走代价 7 太大，合计 8，不如其他选择。",
        labAlgo: "astar",
        output: { type: "worked-map", algo: "astar", withPseudo: true },
      },
      {
        prompt: "从校门口出发时：超市 g=7、h=1、合计 8；教学楼 g=2、h=4、合计 6；食堂 g=2、h=3、合计 5。A* 选合计最小的食堂方向，不会只看 h 选超市。",
        copyPrompt: C5.astarFirst,
        vibeTip: "对照数字看动画，比背公式更容易理解。",
        output: { type: "insight", html: "<strong>第一步怎么选</strong>（从校门口出发）：超市 已走7 + 估计1 = 8；教学楼 2+4=6；食堂 2+3=5。A* 取合计最小者，不会只因超市估计最近就选它。" },
      },
      {
        prompt: "本例中 A* 与一致代价搜索都找到花费 7 的最优路径，而贪婪搜索花了 8。A* 在估计合理时兼顾方向与代价。",
        copyPrompt: C5.astarCompare,
        vibeTip: "三种算法同图对比，是理解「只看花费」「只看估计」「两者兼顾」各自作用的好办法。",
        output: { type: "compare-pair", algos: ["astar", "greedy", "ucs"] },
      },
      { mentorCell: "misconception", mentorKey: "ch5-astar" },
      { mentorCell: "selfCheck", mentorKey: "ch5-astar" },
      {
        mentorCell: "when",
        mentorKey: "ch5-astar",
        prompt: "在实验室播放 A*，对照每步 g、h 与 g+h 的选点理由。",
        copyPrompt: C5.astarFirst,
        labAlgo: "astar",
      },
    ],
  },
  minimax: {
    title: "MiniMax 博弈搜索",
    subtitle: "双方轮流下棋，我方选最好、假设对手选最坏",
    cells: [
      {
        prompt: "路径搜索只有你在走；博弈搜索则双方轮流落子。MiniMax 的做法是：轮到我时选对我最有利的走法，轮到对手时假设他会选对我最不利的应对。",
        copyPrompt: C5.minimaxIntro,
        vibeTip: "先理解树的结构：每一层要么轮到我方选，要么轮到对手选。",
        labAlgo: "minimax",
        output: { type: "minimax-tree", step: 0 },
      },
      {
        prompt: "为什么极小层要假设对手选让我方得分最低的分支？因为理性对手不会配合你——你必须按最坏情况来规划。",
        copyPrompt: C5.minimaxMin,
        vibeTip: "看动画里的具体数字，比记定义更直观。",
        labAlgo: "minimax",
        output: { type: "minimax-tree", step: 2 },
      },
      {
        prompt: "Alpha-Beta 剪枝：如果某条分支已经不可能比现有选择更好，就不用再往下算了。动画里被划掉的分支就是剪掉的。",
        copyPrompt: C5.minimaxPrune,
        vibeTip: "剪枝不改变最终结论，只是少做无用计算。",
        labAlgo: "minimax",
        output: { type: "minimax-tree", step: 3 },
      },
      {
        prompt: "路径搜索在图上找路，比较的是花费或距离；博弈搜索在树上选走法，比较的是双方轮流下的局面评估值。",
        copyPrompt: C5.minimaxVsPath,
        vibeTip: "这是两类不同的「搜索」问题，不要混为一谈。",
        output: { type: "game-compare-table" },
      },
      { mentorCell: "misconception", mentorKey: "ch5-minimax" },
      { mentorCell: "selfCheck", mentorKey: "ch5-minimax" },
      {
        mentorCell: "when",
        mentorKey: "ch5-minimax",
        prompt: "在实验室步进 MiniMax 树，对照 MAX/MIN 层与 Alpha-Beta 剪枝。",
        copyPrompt: C5.minimaxPrune,
        labAlgo: "minimax",
      },
    ],
  },
};

const LEARNING_PATH = [
  { step: 1, topic: "搜索图与基本概念", prompt: "把校园路线画成图，理解待探索、已访问、路径来源" },
  { step: 2, topic: "深度优先搜索", prompt: "一条路走到底，再回溯" },
  { step: 3, topic: "广度优先搜索", prompt: "一层层扩散，保证最少步数" },
  { step: 4, topic: "一致代价搜索", prompt: "加入路径代价，找花费最少的路" },
  { step: 5, topic: "贪婪搜索", prompt: "按估计距离选路，可能绕远" },
  { step: 6, topic: "A* 搜索", prompt: "已走代价 + 估计距离，兼顾方向与花费" },
  { step: 7, topic: "MiniMax 博弈搜索", prompt: "双方轮流，按最坏情况选最优" },
  { step: 8, topic: "互动实验室", prompt: "自由切换六种算法，反复步进加深理解" },
];

/* ========== App state & DOM ========== */

const state = {
  algorithmKey: "dfs",
  stepIndex: 0,
  timer: null,
  minimaxStep: 0,
  minimaxTimer: null,
};

const dom = {};

function cacheDom() {
  const ids = [
    "algorithmTabs", "algorithmTitle", "algorithmSummary", "algorithmTagline",
    "stepIndex", "stepTotal", "campusMap", "prevStep", "nextStep", "resetStep",
    "playPause", "playIcon", "playText", "stepRange", "stepTitle", "stepExplanation",
    "stepNarrative", "currentNode", "currentG", "currentH", "currentF",
    "structureTitle", "structureMode", "processingNode", "processingReason",
    "nextCandidate", "nextReason", "frontierStructure", "frontierList",
    "visitedList", "parentList", "frontierStrategy", "pseudocode",
    "minimaxLabPrev", "minimaxLabNext", "minimaxLabRange", "minimaxLabStepTitle", "minimaxLabNarrative",
    "sectionNav",
  ];
  ids.forEach((id) => {
    const el = document.getElementById(id);
    dom[toCamel(id)] = el;
  });
}

function toCamel(id) {
  return id.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
}

function init() {
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  if (!location.hash) {
    requestAnimationFrame(() => window.scrollTo(0, 0));
  }
  cacheDom();
  renderTabs();
  renderSectionNav();
  renderMentorChapter();
  renderAllNotebooks();
  wireEvents();
  wireScrollSpy();
  initLearningProgress();
  initRevealAnimations();
  initOnboarding();
  render();
  scrollToHashAfterRender();
  window.searchLab = { CAMPUS_NODES, CAMPUS_EDGES, algorithms, traces, workedRuns, vibeNotebooks };
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

function getLabScrollTarget(section, algoKey = state.algorithmKey) {
  if (!section) return null;
  const compact = window.matchMedia("(max-width: 680px)").matches;
  if (compact && algoKey === "minimax") return document.getElementById("minimaxLabPanel") || section;
  if (compact) return section.querySelector(".visual-workspace, .app-shell, .lab-panel") || section;
  return section.querySelector(".tabs, .app-shell, .lab-panel") || section;
}

/* ========== Campus SVG rendering ========== */

const EDGE_LABEL_FLIP = {
  "x-s1": -1,
  "x-j": 1,
  "j-s2": -1,
  "s1-t": 1,
  "s1-c1": -1,
  "t-c1": 1,
};

function edgeEndpoints(x1, y1, x2, y2, radius = NODE_RADIUS) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.hypot(dx, dy) || 1;
  const ux = dx / len;
  const uy = dy / len;
  return {
    x1: x1 + ux * radius,
    y1: y1 + uy * radius,
    x2: x2 - ux * (radius + 5),
    y2: y2 - uy * (radius + 5),
  };
}

function edgeLabelPos(x1, y1, x2, y2, flip = 1) {
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.hypot(dx, dy) || 1;
  const offset = 18;
  return {
    x: mx - (dy / len) * offset * flip,
    y: my + (dx / len) * offset * flip,
  };
}

function nodeNamePlacement(node) {
  if (node.id === "c1") return { dx: 36, dy: 6, anchor: "start" };
  if (node.y < 160) return { dx: 0, dy: -46, anchor: "middle" };
  return { dx: 0, dy: 44, anchor: "middle" };
}

function metricPlacement(node) {
  if (node.id === "c1") return { x: 36, y: -28, anchor: "start" };
  if (node.y < 160) return { x: 0, y: 38, anchor: "middle" };
  return { x: 0, y: -48, anchor: "middle" };
}

function metricLabelSvg(metric, pos) {
  if (!metric) return "";
  return `<text class="node-metric" x="${pos.x}" y="${pos.y}" text-anchor="${pos.anchor || "middle"}">${metric}</text>`;
}

function formatResultMetric(key, run) {
  if (key === "dfs" || key === "bfs") {
    return `${Math.max(0, run.finalPath.length - 1)} 步`;
  }
  return `成本 ${run.cost}`;
}

function isOptimalRun(key, run) {
  return key === "ucs" || key === "astar" ? run.cost === 7 : false;
}

function renderCampusMap(step, options = {}) {
  const container = options.container || dom.campusMap;
  if (!container) return;
  container.classList.add("map-canvas");

  const visited = new Set(step?.visited || []);
  const frontier = new Set((step?.frontier || []).map((e) => e.id));
  const path = new Set(step?.path || []);
  const currentId = step?.current?.id;
  const finalPath = options.finalPath || [];
  const markerId = options.markerId || "campus-arrow";
  const metricMode = options.metricMode || null;
  const gScores = step?.gScores || {};
  const frontierEntries = step?.frontier || [];

  const metricForNode = (nodeId) => {
    if (!metricMode) return "";
    if (currentId === nodeId && step?.current) {
      if (metricMode === "g") return `g=${step.current.g}`;
      if (metricMode === "h") return `h=${step.current.h}`;
      if (metricMode === "f") return `f=${step.current.f}`;
    }
    const inFrontier = frontierEntries.find((e) => e.id === nodeId);
    if (inFrontier) {
      if (metricMode === "g") return `g=${inFrontier.g}`;
      if (metricMode === "h") return `h=${inFrontier.h}`;
      if (metricMode === "f") return `f=${inFrontier.f}`;
    }
    if (gScores[nodeId] !== undefined && metricMode === "g") return `g=${gScores[nodeId]}`;
    if (options.showH && !metricMode) return `h=${CAMPUS_NODES[nodeId]?.h ?? 0}`;
    return "";
  };

  const edgeMarkup = CAMPUS_EDGES.map(({ from, to, cost }) => {
    const a = CAMPUS_NODES[from];
    const b = CAMPUS_NODES[to];
    const inFinal =
      finalPath.length > 0 &&
      finalPath.some((n, i) => n === from && finalPath[i + 1] === to);
    const inPath = path.has(from) && path.has(to) && !inFinal;
    const cls = ["graph-edge", inFinal ? "in-final" : "", inPath ? "in-path" : ""]
      .filter(Boolean)
      .join(" ");
    const line = edgeEndpoints(a.x, a.y, b.x, b.y);
    const flip = EDGE_LABEL_FLIP[`${from}-${to}`] ?? EDGE_LABEL_FLIP[`${to}-${from}`] ?? 1;
    const label = edgeLabelPos(a.x, a.y, b.x, b.y, flip);
    return `
      <line class="${cls}" x1="${line.x1}" y1="${line.y1}" x2="${line.x2}" y2="${line.y2}" marker-end="url(#${markerId})"></line>
      <text class="graph-weight ${inFinal ? "in-final" : ""}" x="${label.x}" y="${label.y}">${cost}</text>
    `;
  }).join("");

  const nodeMarkup = Object.values(CAMPUS_NODES)
    .map((node) => {
      const cls = [
        "graph-node",
        node.id === START_ID ? "is-start" : "",
        node.id === GOAL_ID ? "is-goal" : "",
        finalPath.includes(node.id) ? "is-final" : "",
        visited.has(node.id) ? "is-visited" : "",
        frontier.has(node.id) ? "is-frontier" : "",
        currentId === node.id ? "is-current" : "",
      ]
        .filter(Boolean)
        .join(" ");
      const metric = metricForNode(node.id);
      const namePos = nodeNamePlacement(node);
      const metricPos = metricPlacement(node);
      return `
        <g class="${cls}" transform="translate(${node.x} ${node.y})">
          <title>${node.name} (${node.label})${metric ? ` · ${metric}` : ""}</title>
          <circle r="${NODE_RADIUS}"></circle>
          ${metricLabelSvg(metric, metricPos)}
          <text class="node-id">${node.label}</text>
          <text class="node-name" x="${namePos.dx}" y="${namePos.dy}" text-anchor="${namePos.anchor}">${node.name}</text>
        </g>
      `;
    })
    .join("");

  container.innerHTML = `
    <svg class="campus-svg" viewBox="${SVG_VIEWBOX}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="校园搜索图">
      <defs>
        <marker id="${markerId}" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z"></path>
        </marker>
      </defs>
      ${edgeMarkup}
      ${nodeMarkup}
    </svg>
  `;
}

function renderRepresentation() {
  const el = document.getElementById("reprCampusMap");
  if (el) renderCampusMap({ visited: [], frontier: [], path: [] }, { container: el, showH: false, markerId: "repr-arrow" });
}

/* ========== Tabs & navigation ========== */

function renderTabs() {
  if (!dom.algorithmTabs) return;
  dom.algorithmTabs.setAttribute("role", "tablist");
  dom.algorithmTabs.innerHTML = "";
  Object.entries(algorithms).forEach(([key, algo]) => {
    const btn = document.createElement("button");
    btn.className = `tab ${key === state.algorithmKey ? "is-active" : ""}`;
    btn.type = "button";
    btn.dataset.algorithm = key;
    btn.textContent = algo.tab;
    btn.setAttribute("role", "tab");
    btn.setAttribute("aria-selected", String(key === state.algorithmKey));
    btn.addEventListener("click", () => jumpToLab(key));
    dom.algorithmTabs.appendChild(btn);
  });
}

function metricModeForAlgorithm(key) {
  if (key === "ucs") return "g";
  if (key === "greedy") return "h";
  if (key === "astar") return "f";
  return null;
}

function renderSectionNav() {
  if (!dom.sectionNav) return;
  const sections = [
    { id: "hero", label: "开篇" },
    { id: "m0", label: "搜索图" },
    { id: "m1", label: "无信息" },
    { id: "m2", label: "有信息" },
    { id: "m3", label: "博弈" },
    { id: "m4", label: "对比" },
    { id: "lab", label: "实验室" },
  ];
  dom.sectionNav.innerHTML = sections
    .map((s) => `<a href="#${s.id}" class="section-link" data-section="${s.id}">${s.label}</a>`)
    .join("");
  dom.sectionNav.addEventListener("click", (e) => {
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
}

function setActiveSectionLink(id) {
  document.querySelectorAll(".section-link[data-section]").forEach((link) => {
    link.classList.toggle("is-active", link.dataset.section === id);
  });
}

function wireScrollSpy() {
  const links = Array.from(document.querySelectorAll(".section-link[data-section]"));
  if (!links.length) return;

  const sectionIds = links.map((l) => l.dataset.section);
  const visitedSections = new Set();
  const syncActiveSection = () => {
    const anchorY = Math.min(window.innerHeight * 0.25, 160);
    let activeId = sectionIds[0];
    sectionIds.forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      if (el.getBoundingClientRect().top <= anchorY) activeId = id;
    });
    setActiveSectionLink(activeId);
  };

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && entry.intersectionRatio > 0.15) {
          visitedSections.add(entry.target.id);
          const link = links.find((l) => l.dataset.section === entry.target.id);
          link?.classList.add("is-visited");
        }
      });

      syncActiveSection();
    },
    { rootMargin: "-20% 0px -65% 0px", threshold: [0, 0.15, 0.35, 0.5] },
  );

  sectionIds.forEach((id) => {
    const el = document.getElementById(id);
    if (el) observer.observe(el);
  });
  window.addEventListener("scroll", () => requestAnimationFrame(syncActiveSection), { passive: true });
}

function initLearningProgress() {
  const bar = document.getElementById("learningProgressBar");
  const label = document.getElementById("learningProgressText");
  const progressEl = document.querySelector(".learning-progress");
  if (!bar) return;

  const update = () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const pct = docHeight > 0 ? Math.min(100, Math.round((scrollTop / docHeight) * 100)) : 0;
    bar.style.width = `${pct}%`;
    if (label) label.textContent = `${pct}%`;
    if (progressEl) progressEl.setAttribute("aria-valuenow", String(pct));
  };

  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update, { passive: true });
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
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) reveal(entry.target, observer);
      });
    },
    { threshold: 0, rootMargin: "0px 0px -32px 0px" },
  );

  sections.forEach((el) => {
    observer.observe(el);
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight * 0.98 && rect.bottom > 0) {
      reveal(el, observer);
    }
  });
}

function chapterGroupForAlgo(_key) {
  return null;
}

function setChapterAlgoTab(_group, _key) {}

function initChapterTabs() {}

function initMinimaxAdvancedTabs() {}

/* ========== Vibe notebook rendering ========== */

function normalizeVibeNotebookCells(cells) {
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

function resolveCh5CopyText(cell) {
  if (cell.mentorSummary && window.coursePedagogy?.buildMentorBundleCopyPrompt) {
    return window.coursePedagogy.buildMentorBundleCopyPrompt(
      cell.mentorSummary,
      5,
      cell.prompt,
      cell.labAlgo,
      cell.whenCopyPrompt,
      cell.selfCheckCopyPrompt,
    );
  }
  if (cell.mentorCell && cell.mentorKey && window.coursePedagogy?.buildMentorCopyPrompt) {
    return window.coursePedagogy.buildMentorCopyPrompt(cell.mentorKey, cell.mentorCell, 5);
  }
  return buildCopyPrompt(cell);
}

function renderMentorChapter() {
  const host = document.querySelector("[data-chapter-goals]");
  if (!host || !window.coursePedagogy) return;
  host.innerHTML = window.coursePedagogy.renderMentorChapterPanel(5);
}

function renderAllNotebooks() {
  document.querySelectorAll("[data-vibe-module]").forEach((host) => {
    renderVibeModule(host.dataset.vibeModule, host);
  });
  document.querySelectorAll("[data-vibe-notebook]").forEach((host) => {
    renderNotebook(host.dataset.vibeNotebook, host);
  });
  renderWorkedRuns();
}

function renderVibeModule(moduleKey, host) {
  const mod = vibeModules[moduleKey];
  if (!mod || !host) return;
  host.innerHTML = "";
  const wrap = document.createElement("div");
  wrap.className = "vibe-notebook";
  mod.cells.forEach((cell, i) => {
    wrap.appendChild(buildVibeCellPair(cell, `${moduleKey}-${i}`, i + 1));
  });
  host.appendChild(wrap);
}

function renderNotebook(notebookKey, host) {
  const nb = vibeNotebooks[notebookKey];
  if (!nb || !host) return;
  host.innerHTML = "";
  const article = document.createElement("article");
  article.className = "vibe-notebook algo-notebook";
  article.id = `notebook-${notebookKey}`;
  article.innerHTML = `
    <header class="notebook-header">
      <h3>${nb.title}</h3>
      <p class="notebook-subtitle">${nb.subtitle || ""}</p>
    </header>`;
  const body = document.createElement("div");
  body.className = "vibe-notebook-body";
  const nbCells = normalizeVibeNotebookCells(nb.cells);
  nbCells.forEach((cell, i) => {
    body.appendChild(buildVibeCellPair(cell, `${notebookKey}-${i}`, i + 1, notebookKey));
  });
  article.appendChild(body);
  host.appendChild(article);
}

function formatPromptHtml(prompt) {
  const spec = CAMPUS_GRAPH_SPEC.trim();
  const rich = window.courseShared?.formatRichText || ((t) => escapeHtml(t).replace(/\n/g, "<br>"));
  if (!prompt.includes(spec)) {
    return `<div class="vibe-prompt-text">${rich(prompt)}</div>`;
  }
  const specIndex = prompt.indexOf(spec);
  const lead = prompt.slice(0, specIndex).trim();
  const tail = prompt.slice(specIndex + spec.length).trim();
  return `
    ${lead ? `<div class="vibe-prompt-text">${rich(lead)}</div>` : ""}
    <div class="vibe-prompt-spec">
      <span class="vibe-prompt-spec-label">图数据说明</span>
      <pre class="vibe-prompt-spec-body">${escapeHtml(spec)}</pre>
    </div>
    ${tail ? `<div class="vibe-prompt-text">${rich(tail)}</div>` : ""}`;
}

function buildVibeCellPair(cell, instanceId, index, notebookKey = "") {
  const pair = document.createElement("div");
  pair.className = "vibe-cell-pair";
  pair.dataset.cellInstance = instanceId;

  let mentorHtml = "";
  if (cell.mentorSummary && window.coursePedagogy?.renderMentorSummary) {
    mentorHtml = window.coursePedagogy.renderMentorSummary(cell.mentorSummary);
  } else if (cell.mentorCell && cell.mentorKey && window.coursePedagogy) {
    mentorHtml = window.coursePedagogy.renderMentorCell(cell.mentorCell, cell.mentorKey);
  }

  const hasOutput = Boolean(cell.output);
  if (!hasOutput && (cell.mentorSummary || cell.mentorCell)) {
    pair.classList.add("vibe-cell-pair--text-only");
  }

  const promptEl = document.createElement("div");
  promptEl.className = "vibe-cell vibe-prompt";
  const promptLabel = "要点";
  const copyText = resolveCh5CopyText(cell);
  promptEl.innerHTML = `
    <div class="cell-header">
      <span class="cell-index">步骤 ${index}</span>
      <span class="cell-label">${promptLabel}</span>
    </div>
    <div class="prompt-body">
      ${mentorHtml}
      ${cell.prompt ? formatPromptHtml(cell.prompt) : ""}
    </div>
      ${cell.vibeTip ? `<p class="vibe-tip"><span class="vibe-tip-label">学习提示</span>${escapeHtml(cell.vibeTip)}</p>` : ""}
    <div class="prompt-actions">
      ${copyText ? `<div class="copy-teach"><span>向 AI 提问练习</span><button type="button" class="primary-button copy-prompt-btn" data-copy="${escapeAttr(copyText)}" aria-label="复制${escapeAttr(promptLabel)}学习 Prompt">复制学习 Prompt</button></div>` : `<button type="button" class="primary-button copy-prompt-btn">复制学习 Prompt</button>`}
      ${cell.labAlgo ? `<button type="button" class="ghost-button" data-jump-algo="${cell.labAlgo}">在实验室打开</button>` : ""}
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
  if (hasOutput) {
    mountOutputCell(outputBody, cell.output, instanceId, notebookKey);
    outputEl.appendChild(outputBody);
  } else if (cell.mentorCell === "selfCheck") {
    const q =
      window.coursePedagogy?.notebooks?.[cell.mentorKey]?.selfCheck ||
      "先自己想一想，再对照上文演示。";
    outputBody.innerHTML = `<div class="mentor-think-space"><p class="think-prompt">${escapeHtml(q)}</p></div>`;
    outputEl.appendChild(outputBody);
  } else {
    outputEl.hidden = true;
  }

  pair.append(promptEl, outputEl);

  const interactiveTypes = new Set(["worked-map", "frontier-focus"]);
  if (interactiveTypes.has(cell.output?.type)) {
    pair.classList.add("vibe-cell-pair--interactive");
  }

  promptEl.querySelector(".copy-prompt-btn")?.addEventListener("click", (e) => {
    copyPromptText(copyText || buildCopyPrompt(cell), e.currentTarget);
  });

  return pair;
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

async function copyPromptText(text, btn) {
  let ok = false;
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      ok = true;
    } catch {
      ok = false;
    }
  }
  if (!ok) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.cssText = "position:fixed;left:-9999px";
    document.body.appendChild(ta);
    ta.select();
    try {
      ok = document.execCommand("copy");
    } catch {
      ok = false;
    }
    document.body.removeChild(ta);
  }
  const prev = btn.textContent;
  btn.textContent = ok ? "已复制 ✓" : "复制失败";
  btn.classList.toggle("is-copied", ok);
  setTimeout(() => {
    btn.textContent = prev;
    btn.classList.remove("is-copied");
  }, 2000);
}

function mountOutputCell(container, output, instanceId, notebookKey) {
  if (!output) return;
  switch (output.type) {
    case "graph-static": {
      const mapEl = document.createElement("div");
      mapEl.id = "reprCampusMap";
      mapEl.className = "campus-map-static";
      mapEl.setAttribute("aria-label", "校园搜索图");
      const table = document.createElement("div");
      table.className = "repr-table four-elements";
      table.innerHTML = `
        <div class="repr-row header"><span>概念</span><span>在本图搜索中</span></div>
        <div class="repr-row"><strong>地点（节点）</strong><span>图上的位置（x, s1, c1…）</span></div>
        <div class="repr-row"><strong>路径（边）</strong><span>相邻地点间的移动，带代价</span></div>
        <div class="repr-row"><strong>目标</strong><span>操场 c1</span></div>
        <div class="repr-row"><strong>待探索</strong><span>还没展开、但在候选名单里的地点</span></div>
        <div class="repr-row"><strong>已访问</strong><span>已经展开过的地点</span></div>
        <div class="repr-row"><strong>路径来源</strong><span>记录每个地点是从哪里来的</span></div>`;
      container.append(mapEl, table);
      renderCampusMap({ visited: [], frontier: [], path: [] }, { container: mapEl, showH: false, markerId: "repr-arrow" });
      break;
    }
    case "term-table": {
      container.innerHTML = `
        <div class="table-wrap compact">
          <table class="run-table compact">
            <thead><tr><th>算法</th><th>待探索结构</th><th>取下一个的规则</th><th>还需记录</th></tr></thead>
            <tbody>
              <tr><td>深度优先</td><td>栈</td><td>从栈顶取（后进先出）</td><td>已访问、路径来源</td></tr>
              <tr><td>广度优先</td><td>队列</td><td>从队头取（先进先出）</td><td>已访问、路径来源</td></tr>
              <tr><td>一致代价</td><td>优先队列</td><td>累计代价最小</td><td>累计代价、路径来源</td></tr>
              <tr><td>贪婪搜索</td><td>优先队列</td><td>估计距离最小</td><td>估计距离、路径来源</td></tr>
              <tr><td>A*</td><td>优先队列</td><td>已走+估计 最小</td><td>累计代价、估计距离、路径来源</td></tr>
            </tbody>
          </table>
        </div>`;
      break;
    }
    case "worked-map": {
      if (output.withPseudo) {
        const pre = document.createElement("pre");
        pre.className = "pseudo-compact notebook-pseudo";
        pre.innerHTML = `<code>${escapeHtml(algorithms[output.algo]?.pseudocode || "")}</code>`;
        container.appendChild(pre);
      }
      const slot = document.createElement("div");
      slot.className = "worked-visual notebook-worked";
      slot.dataset.workedRun = output.algo;
      slot.dataset.workedInstance = instanceId;
      container.appendChild(slot);
      break;
    }
    case "frontier-focus": {
      const slot = document.createElement("div");
      slot.className = "worked-visual notebook-worked frontier-focus-host";
      slot.dataset.workedRun = output.algo;
      slot.dataset.workedInstance = `${instanceId}-focus`;
      slot.dataset.frontierFocus = "1";
      container.appendChild(slot);
      break;
    }
    case "compare-pair": {
      const table = buildComparePairTable(output.algos);
      container.appendChild(table);
      wireJumpAlgoButtons(container);
      break;
    }
    case "compare-table": {
      const target = document.createElement("div");
      target.dataset.workedComparison = "1";
      container.appendChild(target);
      renderWorkedComparisonInto(target);
      break;
    }
    case "learning-path": {
      const ol = document.createElement("ol");
      ol.className = "learning-path-list";
      ol.innerHTML = LEARNING_PATH.map(
        (item) => `<li><strong>${item.step}. ${item.topic}</strong><span>${escapeHtml(item.prompt)}</span></li>`,
      ).join("");
      container.appendChild(ol);
      break;
    }
    case "insight": {
      const box = document.createElement("div");
      box.className = "insight-callout notebook-insight";
      box.innerHTML = output.html;
      container.appendChild(box);
      break;
    }
    case "lab-cta": {
      container.innerHTML = `
        <p class="lab-cta-copy">下方实验室可步进或自动播放该算法的完整过程，并查看待探索列表的变化。</p>
        <button type="button" class="primary-button lab-cta" data-jump-algo="${output.algo}">打开实验室 · ${algorithms[output.algo]?.title || output.algo}</button>`;
      break;
    }
    case "minimax-tree": {
      const wrap = document.createElement("div");
      wrap.className = "minimax-notebook-wrap";
      wrap.dataset.minimaxNotebook = instanceId;
      wrap.dataset.minimaxStep = String(output.step ?? 0);
      wrap.innerHTML = `
        <div class="minimax-tree-host" data-minimax-host="${instanceId}"></div>
        <p class="step-narrative minimax-nb-narrative"></p>
        <div class="worked-controls-inline">
          <button type="button" class="minimax-nb-prev" aria-label="上一步">‹</button>
          <strong class="minimax-nb-title"></strong>
          <button type="button" class="minimax-nb-next" aria-label="下一步">›</button>
        </div>`;
      container.appendChild(wrap);
      initNotebookMinimax(wrap, output.step ?? 0);
      break;
    }
    case "game-compare-table": {
      container.innerHTML = `
        <div class="table-wrap compact">
          <table class="run-table compact minimax-compare-table">
            <thead><tr><th></th><th>路径搜索</th><th>博弈搜索</th></tr></thead>
            <tbody>
              <tr><td>状态转移</td><td>单方推动</td><td>双方交替</td></tr>
              <tr><td>比较什么</td><td>花费或距离</td><td>局面评估分数</td></tr>
              <tr><td>优化目标</td><td>最优路径</td><td>最坏情况下最好</td></tr>
              <tr><td>典型结构</td><td>图 + 待探索列表</td><td>博弈树</td></tr>
            </tbody>
          </table>
        </div>`;
      break;
    }
    default:
      break;
  }
}

function buildComparePairTable(algoKeys) {
  const wrap = document.createElement("div");
  wrap.className = "table-wrap compact";
  const rows = algoKeys
    .map((key) => {
      const run = workedRuns[key];
      const meta = workedRunMeta[key];
      if (!run) return "";
      const metric = key === "dfs" || key === "bfs"
        ? `${Math.max(0, run.finalPath.length - 1)} 步`
        : `成本 ${run.cost}`;
      return `<tr class="comparison-row ${isOptimalRun(key, run) ? "is-low-cost" : ""}" data-jump-algo="${key}" tabindex="0" role="button">
        <td>${run.label}</td><td>${meta.structureName}</td><td>${meta.selector}</td>
        <td>${run.finalPath.join("→")}</td><td>${metric}</td><td>${meta.optimal}</td></tr>`;
    })
    .join("");
  wrap.innerHTML = `
    <table class="run-table compact comparison-table">
      <thead><tr><th>算法</th><th>结构</th><th>规则</th><th>路径</th><th>指标</th><th>保证</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
  return wrap;
}

const notebookMinimaxState = {};

function initNotebookMinimax(wrap, initialStep) {
  const id = wrap.dataset.minimaxNotebook;
  if (notebookMinimaxState[id] === undefined) notebookMinimaxState[id] = initialStep;
  renderNotebookMinimax(wrap, notebookMinimaxState[id]);

  wrap.querySelector(".minimax-nb-prev")?.addEventListener("click", () => {
    notebookMinimaxState[id] = Math.max(0, notebookMinimaxState[id] - 1);
    renderNotebookMinimax(wrap, notebookMinimaxState[id]);
  });
  wrap.querySelector(".minimax-nb-next")?.addEventListener("click", () => {
    notebookMinimaxState[id] = Math.min(MINIMAX_STEPS.length - 1, notebookMinimaxState[id] + 1);
    renderNotebookMinimax(wrap, notebookMinimaxState[id]);
  });
}

function renderNotebookMinimax(wrap, stepIndex) {
  const step = MINIMAX_STEPS[stepIndex];
  if (!step) return;
  const host = wrap.querySelector("[data-minimax-host]");
  if (host) host.innerHTML = buildGameTreeSvg(step);
  const title = wrap.querySelector(".minimax-nb-title");
  const narrative = wrap.querySelector(".minimax-nb-narrative");
  if (title) title.textContent = step.title;
  if (narrative) narrative.textContent = step.narrative;
  wrap.querySelector(".minimax-nb-prev")?.toggleAttribute("disabled", stepIndex <= 0);
  wrap.querySelector(".minimax-nb-next")?.toggleAttribute("disabled", stepIndex >= MINIMAX_STEPS.length - 1);
}

function workedContainerSelector(key, instance) {
  if (instance) return `[data-worked-run="${key}"][data-worked-instance="${instance}"]`;
  return `[data-worked-run="${key}"]`;
}

function getWorkedInstanceKey(container) {
  const algo = container.dataset.workedRun;
  const inst = container.dataset.workedInstance || algo;
  return `${algo}::${inst}`;
}

/* ========== Worked examples ========== */

function initOnboarding() {
  const el = document.getElementById("onboarding");
  if (!el) return;
  if (location.hash) {
    el.hidden = true;
    return;
  }

  const dismiss = (scrollToStart = false) => {
    localStorage.setItem(ONBOARDING_KEY, "1");
    el.hidden = true;
    if (scrollToStart) {
      document.getElementById("m0")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  if (localStorage.getItem(ONBOARDING_KEY)) {
    el.hidden = true;
    return;
  }

  el.hidden = false;
  document.getElementById("onboardingStart")?.addEventListener("click", () => dismiss(true));
  document.getElementById("onboardingSkip")?.addEventListener("click", () => dismiss(false));
  el.querySelector(".onboarding-backdrop")?.addEventListener("click", () => dismiss(false));
}

/* ========== Worked examples ========== */

function renderWorkedRuns() {
  document.querySelectorAll("[data-worked-run]").forEach((container) => {
    const key = container.dataset.workedRun;
    if (!workedRuns[key]) return;
    const instanceKey = getWorkedInstanceKey(container);
    if (workedState[instanceKey] === undefined) workedState[instanceKey] = 0;
    renderWorkedRun(container, key, instanceKey);
  });
  document.querySelectorAll("[data-worked-comparison]").forEach((target) => {
    renderWorkedComparisonInto(target);
  });
}

function renderFrontierChip(key, step) {
  const meta = workedRunMeta[key];
  const items = step.frontier?.slice(0, 4) || [];
  if (!items.length) return '<p class="frontier-chip-empty">待探索列表为空</p>';
  const labels = items.map((entry, i) => {
    const badge = i === 0 ? meta.selector : "";
    return `<span class="frontier-chip ${i === 0 ? "is-next" : ""}">${badge ? `<em>${badge}</em> ` : ""}${formatEntry(entry, key)}</span>`;
  });
  return `<div class="frontier-chip-row">${labels.join("")}</div>`;
}

function renderWorkedRun(container, key, instanceKey) {
  const run = workedRuns[key];
  const trace = traces[key];
  const index = Math.max(0, Math.min(workedState[instanceKey] ?? 0, trace.length - 1));
  workedState[instanceKey] = index;
  const step = trace[index];
  const pathLabel = run.finalPath.map((id) => CAMPUS_NODES[id].name).join(" → ");
  const isFocus = container.dataset.frontierFocus === "1";
  const meta = workedRunMeta[key];
  const rangeId = `worked-range-${instanceKey.replace(/[^a-z0-9-]/gi, "-")}`;

  container.innerHTML = "";
  const layout = document.createElement("div");
  layout.className = isFocus ? "notebook-focus-layout worked-player" : "worked-player";

  const mainline = document.createElement("div");
  mainline.className = "worked-player-main";

  if (isFocus) {
    mainline.innerHTML = `
      <p class="focus-label"><strong>${meta.structureName}</strong> · ${meta.choiceRule}</p>
      <div class="worked-map-slot" data-worked-map="${instanceKey}"></div>
      <div class="frontier-focus-slot" data-frontier-focus="${instanceKey}"></div>
      <div class="worked-controls-inline worked-controls-bar">
        <button type="button" class="step-btn" data-worked-action="prev" ${index === 0 ? "disabled" : ""} aria-label="上一步">‹ 上一步</button>
        <label class="range-label worked-range" for="${rangeId}">
          <span class="worked-range-label">步骤 ${index} / ${trace.length - 1}</span>
          <input id="${rangeId}" type="range" min="0" max="${trace.length - 1}" value="${index}" />
        </label>
        <button type="button" class="step-btn" data-worked-action="next" ${index === trace.length - 1 ? "disabled" : ""} aria-label="下一步">下一步 ›</button>
      </div>
      <p class="step-narrative">${step.narrative || ""}</p>
      ${renderFrontierChip(key, step)}`;
  } else {
    mainline.innerHTML = `
      <div class="worked-result-badge ${isOptimalRun(key, run) ? "is-optimal" : ""}">
        <span class="badge-label">最终结果</span>
        <strong>${pathLabel}</strong>
        <em>${formatResultMetric(key, run)}</em>
      </div>
      <div class="worked-map-slot" data-worked-map="${instanceKey}"></div>
      <div class="worked-controls-inline worked-controls-bar">
        <button type="button" class="step-btn" data-worked-action="prev" ${index === 0 ? "disabled" : ""} aria-label="上一步">‹ 上一步</button>
        <button type="button" class="ghost-button" data-worked-action="play">${workedPlayState[instanceKey] ? "⏸ 暂停" : "▶ 播放"}</button>
        <label class="range-label worked-range" for="${rangeId}">
          <span class="worked-range-label">步骤 ${index} / ${trace.length - 1}</span>
          <input id="${rangeId}" type="range" min="0" max="${trace.length - 1}" value="${index}" />
        </label>
        <button type="button" class="step-btn" data-worked-action="next" ${index === trace.length - 1 ? "disabled" : ""} aria-label="下一步">下一步 ›</button>
      </div>
      <p class="step-narrative">${step.narrative || ""}</p>
      ${renderFrontierChip(key, step)}
      ${renderWorkedStepDetail(run, key, instanceKey, index, step, trace)}`;
  }

  layout.append(mainline);
  container.append(layout);

  const mapSlot = container.querySelector(`[data-worked-map="${instanceKey}"]`);
  renderCampusMap(step, {
    container: mapSlot,
    finalPath: run.finalPath,
    markerId: `worked-${instanceKey.replace(/[^a-z0-9-]/gi, "-")}`,
    metricMode: metricModeForAlgorithm(key),
    showH: key === "greedy" || key === "astar",
  });

  if (isFocus) {
    const focusSlot = container.querySelector(`[data-frontier-focus="${instanceKey}"]`);
    if (focusSlot) renderFrontierFocusInto(focusSlot, step, key);
  }

  container.querySelectorAll("[data-worked-action]").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (btn.dataset.workedAction === "prev") setWorkedStep(container, key, instanceKey, index - 1);
      if (btn.dataset.workedAction === "next") setWorkedStep(container, key, instanceKey, index + 1);
      if (btn.dataset.workedAction === "play") toggleWorkedPlay(container, key, instanceKey);
    });
  });

  const range = container.querySelector(`#${rangeId}`);
  range?.addEventListener("input", (e) => setWorkedStep(container, key, instanceKey, Number(e.target.value)));

  container.querySelectorAll(`[data-step-nav="${instanceKey}"] .step-nav-btn`).forEach((btn) => {
    btn.addEventListener("click", () => setWorkedStep(container, key, instanceKey, Number(btn.dataset.step)));
  });

  scrollActiveStepNav(container, instanceKey);
}

function scrollActiveStepNav(container, instanceKey) {
  const active = container.querySelector(`[data-step-nav="${instanceKey}"] .step-nav-btn.is-active`);
  active?.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
}

function renderFrontierFocusInto(slot, step, algorithmKey) {
  slot.innerHTML = "";
  slot.className = `frontier-structure frontier-focus-inline ${algorithmKey}-structure`;
  if (!step.frontier?.length) {
    slot.innerHTML = '<div class="frontier-empty">待探索列表为空</div>';
    return;
  }
  if (algorithmKey === "dfs") renderStackStructure(step.frontier, algorithmKey, slot);
  else if (algorithmKey === "bfs") renderQueueStructure(step.frontier, algorithmKey, slot);
  else renderPriorityStructure(step.frontier, algorithmKey, slot);
}

function setWorkedStep(container, key, instanceKey, next) {
  const trace = traces[key];
  if (!trace) return;
  workedState[instanceKey] = Math.max(0, Math.min(next, trace.length - 1));
  if (container) renderWorkedRun(container, key, instanceKey);
}

function toggleWorkedPlay(container, key, instanceKey) {
  if (workedTimers[instanceKey]) {
    window.clearInterval(workedTimers[instanceKey]);
    workedTimers[instanceKey] = null;
    workedPlayState[instanceKey] = false;
    if (container) renderWorkedRun(container, key, instanceKey);
    return;
  }

  const trace = traces[key];
  if ((workedState[instanceKey] ?? 0) >= trace.length - 1) workedState[instanceKey] = 0;

  workedPlayState[instanceKey] = true;
  if (container) renderWorkedRun(container, key, instanceKey);

  workedTimers[instanceKey] = window.setInterval(() => {
    const idx = workedState[instanceKey] ?? 0;
    const c = document.querySelector(`[data-worked-instance="${container.dataset.workedInstance}"]`);
    if (idx >= trace.length - 1) {
      window.clearInterval(workedTimers[instanceKey]);
      workedTimers[instanceKey] = null;
      workedPlayState[instanceKey] = false;
    } else {
      workedState[instanceKey] = idx + 1;
    }
    if (c) renderWorkedRun(c, key, instanceKey);
  }, 850);
}

function stopAllWorkedPlay() {
  Object.keys(workedTimers).forEach((key) => {
    if (workedTimers[key]) {
      window.clearInterval(workedTimers[key]);
      workedTimers[key] = null;
      workedPlayState[key] = false;
    }
  });
}

function renderWorkedComparisonInto(target) {
  if (!target) return;
  const rows = Object.entries(workedRuns)
    .map(([key, run]) => {
      const meta = workedRunMeta[key];
      const metric = key === "dfs" || key === "bfs"
        ? `${Math.max(0, run.finalPath.length - 1)} 步`
        : String(run.cost);
      return `<tr class="comparison-row ${isOptimalRun(key, run) ? "is-low-cost" : ""}" data-jump-algo="${key}" tabindex="0" role="button" aria-label="在实验室播放 ${run.label}">
        <td>${run.label}</td><td>${meta.structureName}</td><td>${meta.selector}</td>
        <td>${run.finalPath.join("→")}</td>
        <td>${metric}</td><td>${meta.optimal}</td></tr>`;
    })
    .join("");
  target.innerHTML = `
    <div class="comparison-card">
      <p class="comparison-hint">绿色高亮为代价 7 的较优路径（一致代价与 A*）。<strong>点击任意行</strong>可在实验室查看完整过程。</p>
      <div class="table-wrap"><table class="run-table comparison-table">
        <thead><tr><th>算法</th><th>结构</th><th>规则</th><th>路径</th><th>步数/成本</th><th>保证</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </div>`;

  wireJumpAlgoButtons(target);
}

function wireJumpAlgoButtons(root = document) {
  root.querySelectorAll("[data-jump-algo]").forEach((btn) => {
    if (btn.dataset.jumpWired) return;
    btn.dataset.jumpWired = "1";
    btn.addEventListener("click", () => jumpToLab(btn.dataset.jumpAlgo));
    if (btn.classList.contains("comparison-row")) {
      btn.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          jumpToLab(btn.dataset.jumpAlgo);
        }
      });
    }
  });
}

/* ========== Minimax ========== */

function renderMinimaxStep(index) {
  const step = MINIMAX_STEPS[index];
  if (!step) return;

  if (dom.minimaxLabStepTitle) dom.minimaxLabStepTitle.textContent = step.title;
  if (dom.minimaxLabNarrative) dom.minimaxLabNarrative.textContent = step.narrative;
  if (dom.minimaxLabRange) {
    dom.minimaxLabRange.max = String(MINIMAX_STEPS.length - 1);
    dom.minimaxLabRange.value = String(index);
  }
  const labTree = document.getElementById("minimaxTreeLab");
  if (labTree) labTree.innerHTML = buildGameTreeSvg(step);
  updateMinimaxStepButtons(index, MINIMAX_STEPS.length - 1);
}

function buildGameTreeSvg(step) {
  const nodes = [
    { id: "root", x: 280, y: 30, label: "我方走", layer: "max" },
    { id: "eat", x: 100, y: 100, label: "吃炮", layer: "max" },
    { id: "defend", x: 280, y: 100, label: "防守", layer: "max" },
    { id: "develop", x: 460, y: 100, label: "发展", layer: "max" },
    { id: "opp-check", x: 100, y: 180, label: "将军 -100", layer: "min" },
    { id: "opp-normal", x: 220, y: 180, label: "普通 +5", layer: "min" },
    { id: "opp-attack", x: 340, y: 180, label: "进攻 -10", layer: "min" },
    { id: "opp-trade", x: 460, y: 180, label: "兑子 +8", layer: "min" },
  ];
  const edges = [
    ["root", "eat"], ["root", "defend"], ["root", "develop"],
    ["eat", "opp-check"], ["defend", "opp-normal"], ["defend", "opp-attack"], ["develop", "opp-trade"],
  ];

  const edgeSvg = edges
    .map(([a, b]) => {
      const na = nodes.find((n) => n.id === a);
      const nb = nodes.find((n) => n.id === b);
      const pruned = step.pruned.includes(b) || step.pruned.includes(a);
      return `<line class="tree-edge ${pruned ? "is-pruned" : ""}" x1="${na.x}" y1="${na.y + 18}" x2="${nb.x}" y2="${nb.y - 18}"></line>`;
    })
    .join("");

  const nodeSvg = nodes
    .map((n) => {
      const hi = step.highlighted.includes(n.id);
      const pruned = step.pruned.includes(n.id);
      const chosen = step.chosen === n.id;
      return `
        <g class="tree-node ${n.layer} ${hi ? "is-highlighted" : ""} ${pruned ? "is-pruned" : ""} ${chosen ? "is-chosen" : ""}" transform="translate(${n.x} ${n.y})">
          <rect x="-42" y="-18" width="84" height="36" rx="8"></rect>
          <text>${n.label}</text>
        </g>`;
    })
    .join("");

  return `<svg class="game-tree-svg" viewBox="0 0 560 220" preserveAspectRatio="xMidYMid meet" role="img">${edgeSvg}${nodeSvg}</svg>`;
}

/* ========== Main lab render ========== */

function wireEvents() {
  dom.prevStep?.addEventListener("click", () => setStep(state.stepIndex - 1));
  dom.nextStep?.addEventListener("click", () => setStep(state.stepIndex + 1));
  dom.resetStep?.addEventListener("click", () => { stopPlayback(); setStep(0); });
  const onStepRange = (e) => setStep(Number(e.target.value));
  dom.stepRange?.addEventListener("input", onStepRange);
  dom.stepRange?.addEventListener("change", onStepRange);
  dom.playPause?.addEventListener("click", () => (state.timer ? stopPlayback() : startPlayback()));

  const onMinimaxRange = (e) => setMinimaxStep(Number(e.target.value));
  dom.minimaxPrev?.addEventListener("click", () => setMinimaxStep(state.minimaxStep - 1));
  dom.minimaxNext?.addEventListener("click", () => setMinimaxStep(state.minimaxStep + 1));
  dom.minimaxRange?.addEventListener("input", onMinimaxRange);
  dom.minimaxRange?.addEventListener("change", onMinimaxRange);
  dom.minimaxLabPrev?.addEventListener("click", () => setMinimaxStep(state.minimaxStep - 1));
  dom.minimaxLabNext?.addEventListener("click", () => setMinimaxStep(state.minimaxStep + 1));
  dom.minimaxLabRange?.addEventListener("input", onMinimaxRange);
  dom.minimaxLabRange?.addEventListener("change", onMinimaxRange);

  wireJumpAlgoButtons(document);

  document.addEventListener("keydown", (e) => {
    if (!isLabFocused()) return;
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      if (state.algorithmKey === "minimax") setMinimaxStep(state.minimaxStep - 1);
      else setStep(state.stepIndex - 1);
    }
    if (e.key === "ArrowRight") {
      e.preventDefault();
      if (state.algorithmKey === "minimax") setMinimaxStep(state.minimaxStep + 1);
      else setStep(state.stepIndex + 1);
    }
    if (e.key === " ") {
      const tag = document.activeElement?.tagName;
      if (tag === "INPUT" || tag === "BUTTON" || tag === "A") return;
      e.preventDefault();
      if (state.algorithmKey === "minimax") return;
      if (state.timer) stopPlayback();
      else startPlayback();
    }
  });
}

function isLabFocused() {
  const lab = document.getElementById("lab");
  if (!lab) return false;
  const rect = lab.getBoundingClientRect();
  return rect.top < window.innerHeight * 0.6 && rect.bottom > window.innerHeight * 0.2;
}

function jumpToLab(algoKey) {
  stopPlayback();
  stopAllWorkedPlay();
  state.algorithmKey = algoKey;
  state.stepIndex = 0;
  if (algoKey === "minimax") state.minimaxStep = 0;
  render();
  const lab = document.getElementById("lab");
  const target = getLabScrollTarget(lab, algoKey);
  target?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function setMinimaxStep(i) {
  state.minimaxStep = Math.max(0, Math.min(i, MINIMAX_STEPS.length - 1));
  renderMinimaxStep(state.minimaxStep);
}

function startPlayback() {
  if (state.algorithmKey === "minimax") return;
  const steps = traces[state.algorithmKey];
  if (state.stepIndex >= steps.length - 1) { state.stepIndex = 0; render(); }
  state.timer = window.setInterval(() => {
    if (state.stepIndex >= traces[state.algorithmKey].length - 1) { stopPlayback(); return; }
    setStep(state.stepIndex + 1);
  }, 900);
  renderPlaybackState();
}

function stopPlayback() {
  if (state.timer) { window.clearInterval(state.timer); state.timer = null; }
  renderPlaybackState();
}

function setStep(i) {
  if (state.algorithmKey === "minimax") return;
  const steps = traces[state.algorithmKey];
  state.stepIndex = Math.max(0, Math.min(i, steps.length - 1));
  render();
}

function updateLabStepButtons(index, maxIndex) {
  if (dom.prevStep) dom.prevStep.disabled = index <= 0;
  if (dom.nextStep) dom.nextStep.disabled = index >= maxIndex;
}

function updateMinimaxStepButtons(index, maxIndex) {
  if (dom.minimaxLabPrev) dom.minimaxLabPrev.disabled = index <= 0;
  if (dom.minimaxLabNext) dom.minimaxLabNext.disabled = index >= maxIndex;
}

function render() {
  const key = state.algorithmKey;
  const algo = algorithms[key];

  document.querySelectorAll(".tab").forEach((tab) => {
    const isCurrent = tab.dataset.algorithm === key;
    tab.classList.toggle("is-active", isCurrent);
    tab.setAttribute("aria-selected", String(isCurrent));
  });

  if (key === "minimax") {
    renderMinimaxLab(algo);
    return;
  }

  const steps = traces[key];
  const step = steps[state.stepIndex];

  if (dom.algorithmTitle) dom.algorithmTitle.textContent = algo.title;
  if (dom.algorithmSummary) dom.algorithmSummary.textContent = algo.summary;
  if (dom.algorithmTagline) dom.algorithmTagline.textContent = algo.tagline;
  if (dom.stepIndex) dom.stepIndex.textContent = String(state.stepIndex);
  if (dom.stepTotal) dom.stepTotal.textContent = String(steps.length - 1);
  if (dom.stepRange) {
    dom.stepRange.max = String(steps.length - 1);
    dom.stepRange.value = String(state.stepIndex);
  }
  updateLabStepButtons(state.stepIndex, steps.length - 1);
  if (dom.stepTitle) dom.stepTitle.textContent = step.title;
  if (dom.stepExplanation) dom.stepExplanation.textContent = step.explanation;
  if (dom.stepNarrative) dom.stepNarrative.textContent = step.narrative;
  if (dom.frontierStrategy) dom.frontierStrategy.textContent = algo.strategy;
  if (dom.pseudocode) dom.pseudocode.textContent = algo.pseudocode;

  renderCampusMap(step, {
    finalPath: workedRuns[key]?.finalPath || step.path,
    markerId: "lab-arrow",
    metricMode: metricModeForAlgorithm(key),
    showH: key === "greedy" || key === "astar",
  });
  renderMetrics(step);
  renderFrontierStructure(step, key);
  renderSet(dom.frontierList, step.frontier, key, true);
  renderSet(dom.visitedList, step.visited, key, false, step.gScores);
  renderParents(step.parents);
  renderPlaybackState();
  toggleLabPanels();

  const labInspector = document.getElementById("pathInspector");
  const gameInspector = document.getElementById("gameInspector");
  if (labInspector) labInspector.hidden = false;
  if (gameInspector) gameInspector.hidden = true;
}

function renderMinimaxLab(algo) {
  if (dom.algorithmTitle) dom.algorithmTitle.textContent = algo.title;
  if (dom.algorithmSummary) dom.algorithmSummary.textContent = algo.summary;
  if (dom.algorithmTagline) dom.algorithmTagline.textContent = algo.tagline;
  if (dom.stepIndex) dom.stepIndex.textContent = String(state.minimaxStep + 1);
  if (dom.stepTotal) dom.stepTotal.textContent = String(MINIMAX_STEPS.length);
  if (dom.pseudocode) dom.pseudocode.textContent = algo.pseudocode;
  renderMinimaxStep(state.minimaxStep);
  toggleLabPanels();

  const labInspector = document.getElementById("pathInspector");
  const gameInspector = document.getElementById("gameInspector");
  if (labInspector) labInspector.hidden = true;
  if (gameInspector) gameInspector.hidden = false;
}

function renderMetrics(step) {
  if (!step.current) {
    ["currentNode", "currentG", "currentH", "currentF"].forEach((k) => { if (dom[k]) dom[k].textContent = "-"; });
    return;
  }
  if (dom.currentNode) dom.currentNode.textContent = `${CAMPUS_NODES[step.current.id].name}(${step.current.id})`;
  if (dom.currentG) dom.currentG.textContent = String(step.current.g);
  if (dom.currentH) dom.currentH.textContent = String(step.current.h);
  if (dom.currentF) dom.currentF.textContent = String(step.current.f);
}

function renderFrontierStructure(step, algorithmKey) {
  const algo = algorithms[algorithmKey];
  const next = step.frontier[0];
  if (dom.structureTitle) dom.structureTitle.textContent = structureTitleFor(algorithmKey);
  if (dom.structureMode) dom.structureMode.textContent = algo.strategy;
  if (dom.processingNode) dom.processingNode.textContent = step.current ? `${step.current.id}` : "-";
  if (dom.processingReason) dom.processingReason.textContent = step.current ? step.selectionReason : "初始化：尚未取出地点。";
  if (dom.nextCandidate) dom.nextCandidate.textContent = next?.id || "-";
  if (dom.nextReason) dom.nextReason.textContent = next ? `下一个：${formatEntry(next, algorithmKey)}` : "待探索列表为空。";
  if (!dom.frontierStructure) return;
  dom.frontierStructure.innerHTML = "";
  dom.frontierStructure.className = `frontier-structure ${algorithmKey}-structure`;
  if (!step.frontier.length) {
    dom.frontierStructure.innerHTML = '<div class="frontier-empty">待探索列表为空</div>';
    return;
  }
  if (algorithmKey === "dfs") renderStackStructure(step.frontier, algorithmKey);
  else if (algorithmKey === "bfs") renderQueueStructure(step.frontier, algorithmKey);
  else renderPriorityStructure(step.frontier, algorithmKey);
}

function structureTitleFor(key) {
  const m = { dfs: "栈", bfs: "队列", ucs: "按累计代价", greedy: "按估计距离", astar: "按综合值" };
  return `待探索：${m[key] || ""}`;
}

function renderStackStructure(frontier, key, container = dom.frontierStructure) {
  if (!container) return;
  const stack = document.createElement("div");
  stack.className = "stack-visual";
  const bracket = document.createElement("div");
  bracket.className = "stack-bracket";
  frontier.forEach((entry, i) => {
    const item = document.createElement("div");
    item.className = `stack-item ${i === 0 ? "is-next" : ""}`;
    item.innerHTML = `<span class="structure-rank">${i === 0 ? "栈顶" : i + 1}</span><span class="structure-node">${formatEntry(entry, key)}</span>`;
    bracket.appendChild(item);
  });
  stack.appendChild(bracket);
  container.appendChild(stack);
}

function renderQueueStructure(frontier, key, container = dom.frontierStructure) {
  if (!container) return;
  const track = document.createElement("div");
  track.className = "queue-track";
  const items = document.createElement("div");
  items.className = "queue-items";
  frontier.forEach((entry, i) => {
    const item = document.createElement("div");
    item.className = `queue-item ${i === 0 ? "is-next" : ""}`;
    item.innerHTML = `<span class="structure-rank">${i === 0 ? "队头" : i + 1}</span><span class="structure-node">${formatEntry(entry, key)}</span>`;
    items.appendChild(item);
  });
  track.appendChild(items);
  container.appendChild(track);
}

function renderPriorityStructure(frontier, key, container = dom.frontierStructure) {
  if (!container) return;
  const list = document.createElement("div");
  list.className = "priority-list";
  frontier.forEach((entry, i) => {
    const item = document.createElement("div");
    item.className = `priority-item ${i === 0 ? "is-next" : ""}`;
    item.innerHTML = `<span class="structure-rank">${i === 0 ? "最小" : i + 1}</span><span class="structure-node">${formatEntry(entry, key)}</span>`;
    list.appendChild(item);
  });
  container.appendChild(list);
}

function renderSet(container, values, algorithmKey, isFrontier, gScores = {}) {
  if (!container) return;
  container.innerHTML = "";
  if (!values.length) {
    container.innerHTML = '<span class="pill muted">空</span>';
    return;
  }
  values.forEach((value, index) => {
    const entry = typeof value === "string" ? { id: value, g: gScores[value] } : value;
    const pill = document.createElement("span");
    pill.className = `pill ${isFrontier && index === 0 ? "current" : ""}`;
    pill.textContent = isFrontier ? formatEntry(entry, algorithmKey) : `${entry.id}(g=${entry.g ?? "-"})`;
    container.appendChild(pill);
  });
}

function renderParents(parents) {
  if (!dom.parentList) return;
  dom.parentList.innerHTML = "";
  const entries = Object.entries(parents);
  if (!entries.length) {
    dom.parentList.innerHTML = '<span class="parent-edge empty-state">暂无</span>';
    return;
  }
  entries.forEach(([child, parent]) => {
    const edge = document.createElement("span");
    edge.className = "parent-edge";
    edge.textContent = `${CAMPUS_NODES[child]?.name || child} ← ${CAMPUS_NODES[parent]?.name || parent}`;
    dom.parentList.appendChild(edge);
  });
}

function renderPrompt(lines) {
  if (!dom.promptText) return;
  dom.promptText.innerHTML = lines.map((l, i) => `<p>${i + 1}. ${l}</p>`).join("");
}

function renderPlaybackState() {
  if (!dom.playIcon) return;
  const playing = Boolean(state.timer);
  dom.playIcon.textContent = playing ? "⏸" : "▶";
  dom.playText.textContent = playing ? "暂停" : "播放";
}

function toggleLabPanels() {
  const key = state.algorithmKey;
  const campusFrame = document.getElementById("campusFrame");
  const minimaxPanel = document.getElementById("minimaxLabPanel");
  const playback = document.querySelector(".playback");
  if (key === "minimax") {
    if (campusFrame) campusFrame.hidden = true;
    if (minimaxPanel) minimaxPanel.hidden = false;
    if (playback) playback.hidden = true;
  } else {
    if (campusFrame) campusFrame.hidden = false;
    if (minimaxPanel) minimaxPanel.hidden = true;
    if (playback) playback.hidden = false;
  }
}

init();
