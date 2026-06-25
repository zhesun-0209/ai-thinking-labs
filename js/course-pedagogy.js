"use strict";

/**
 * 导师设计层 · 第 6–12 章
 * 原则：学生带走「判断力」和「心智模型」，不是公式和名词。
 */

const MENTOR_PRINCIPLES = [
  "同一案例贯穿全章（像第5章校园图），便于对比",
  "先建立直觉，再看步进动画，最后才碰公式",
  "每算法必须回答：何时用、何时不用、常见误区",
  "能预测「下一步发生什么」比背定义更重要",
];

const chapters = {
  5: {
    wish: "搜索 = 在状态空间里按规则找路径；重点判断启发式是否存在、路径代价是否相同，以及问题属于找路还是博弈。",
    pillars: [
      { label: "待探索结构", desc: "栈 / 队列 / 优先队列决定「下一步选谁」" },
      { label: "信息来源", desc: "无信息 vs 累计 g vs 估计 h vs g+h" },
      { label: "问题类型", desc: "单智能体找路 vs 双方博弈 MiniMax" },
    ],
    case: "同一张校园图 x→c1，六种算法逐步对比",
  },
  6: {
    wish: "推理 = 在既定表征下，把隐含结论显式化；重点判断应从事实前推、从目标后推，还是在缺边时转向软排序。",
    pillars: [
      { label: "驱动方向", desc: "前向链数据驱动 vs 后向链目标驱动" },
      { label: "图谱思维", desc: "三元组 + 关系类型约束的多跳查询" },
      { label: "不完备信息", desc: "软自洽：多条证据路径计票排序" },
    ],
    case: "苏格拉底三段论 + 鲁迅/莫言文学图谱",
  },
  7: {
    wish: "学习 = 压缩数据；重点分辨不同算法压缩出的结构、内层损失与外层指标的差异，以及过拟合出现的条件。",
    pillars: [
      { label: "压缩物", desc: "树 / 直线 / 超平面 / 簇中心各压缩什么" },
      { label: "两层优化", desc: "内层拟合训练信号，外层 P/R/F1 评泛化" },
      { label: "可解释性", desc: "决策树可读；线性模型可解释权重" },
    ],
    case: "50 道错题 + 房价散点 + 成绩聚类",
  },
  8: {
    wish: "连接 = 可微分的函数组合 + 离散符号的向量化；重点建立流水线、责任分配和软查询三种心智模型。",
    pillars: [
      { label: "计算图", desc: "前向算值，反向分梯度" },
      { label: "嵌入", desc: "TransE：关系是向量空间里的平移" },
      { label: "对齐", desc: "注意力：按相关性加权取信息" },
    ],
    case: "血糖 MLP + 鲁迅三元组 + 翻译对齐",
  },
  9: {
    wish: "语言 = 分词→向量→上下文→生成；重点把各算法放进同一条流水线，而不是孤立记忆术语。",
    pillars: [
      { label: "流水线", desc: "BPE → 向量 → 自注意力 → 语言模型" },
      { label: "分布式语义", desc: "共现塑造向量空间" },
      { label: "生成", desc: "自回归 = 链式条件概率" },
    ],
    case: "短句：鲁迅写了狂人日记",
  },
  10: {
    wish: "感知 = 从像素到语义；重点比较不同架构的归纳偏置，以及自监督如何提供训练信号。",
    pillars: [
      { label: "归纳偏置", desc: "局部性与全局注意力" },
      { label: "自监督", desc: "MAE 遮罩重构、CLIP 对比对齐" },
      { label: "统一积木", desc: "ViT 与语言模型共享 Transformer" },
    ],
    case: "4×4 小图标",
  },
  11: {
    wish: "行动 = 在不确定环境里试错学习；重点理解智能体-环境环、探索与利用、TD 自举，以及策略与价值的分工。",
    pillars: [
      { label: "交互环", desc: "s → a → r,s′ 循环" },
      { label: "长期回报", desc: "γ 折扣未来奖励" },
      { label: "探索", desc: "ε-贪心：不能只利用已知最优" },
    ],
    case: "订机票四状态 MDP",
  },
  12: {
    wish: "创造 = 在巨大空间里找新解；重点区分搜索、对抗生成、迭代去噪和换表征优化各自解决的瓶颈。",
    pillars: [
      { label: "搜索", desc: "MCTS 采样估计，不必展开全树" },
      { label: "对抗", desc: "GAN 两玩家零和" },
      { label: "去噪", desc: "扩散学逆过程" },
    ],
    case: "表征搜索 + 迷你围棋 + 图像生成",
  },
};

const notebooks = {
  "ch5-dfs": {
    wish: "深度优先 = 栈 + 一条路走到底再回溯。",
    mentalModel: "迷宫里选一条道走到黑，死路就回到最近岔口。",
    mustSee: ["栈顶是谁", "何时回溯", "路径是否最短"],
    misconception: "误区：DFS 一定最快——它只保证找得到路，不保证步数或代价最少。",
    selfCheck: "本图中 DFS 4 步、BFS 2 步——差别来自待探索结构还是启发式？",
    whenToUse: "深树有限、存储紧张、只需任意可行解时。",
  },
  "ch5-bfs": {
    wish: "广度优先 = 队列 + 层序扩散，等权图上保证最少步数。",
    mentalModel: "水波从起点一圈圈向外，先碰到的目标步数最少。",
    mustSee: ["队头是谁", "第一层有哪些邻居", "为何 2 步即到 c1"],
    misconception: "误区：BFS 永远最优——只在每条边代价相同时保证最少步数；代价不同要用 UCS。",
    selfCheck: "第一步 x 的三个邻居各是什么？第二步为何从队头取 s1 就结束？",
    whenToUse: "无权或等权图、需要最少步数、层次遍历类问题。",
  },
  "ch5-ucs": {
    wish: "一致代价搜索 = 优先展开累计花费 g 最小的地点。",
    mentalModel: "谁从起点走过来更便宜，谁先被展开——像按总价排队。",
    mustSee: ["每步 g 如何累加", "为何本例路径 x→s1→t→c1 代价 7", "发现目标 vs 取出目标"],
    misconception: "误区：UCS 与 BFS 一样——BFS 数步数，UCS 看累计代价；本图 BFS 2 步但花费 8。",
    selfCheck: "本例 BFS 与 UCS 路径各是什么？步数少是否一定花费少？",
    whenToUse: "边权不同、需要最低总代价路径时。",
  },
  "ch5-greedy": {
    wish: "贪婪搜索 = 只看估计距离 h，谁看起来离目标最近谁先走。",
    mentalModel: "只凭直觉选「离操场最近」的地点，不管已经走了多远。",
    mustSee: ["第一步为何必展开超市", "超市为何是死胡同", "回溯后路径代价 8"],
    misconception: "误区：h 小就一定走对——h 是估计不是实际，且未考虑已走代价 g。",
    selfCheck: "第一步展开超市后为何必须回溯？A* 第一步为何不选超市？",
    whenToUse: "需要快速近似、可接受非最优、或作为 A* 的直觉对照。",
  },
  "ch5-astar": {
    wish: "A* = 综合 g+h，既看已走代价也看剩余估计。",
    mentalModel: "导航同时显示「已走公里数 + 预计剩余」——比只看其一更稳。",
    mustSee: ["第一步 g+h 对比：超市 8 vs 食堂 5", "与 UCS 同得最优代价 7", "与贪婪路径对比"],
    misconception: "误区：A* 永远比 UCS 快——h 合理且可采纳时才更有效剪枝；h 差时可能退化。",
    selfCheck: "从 x 出发时，超市 g=7、h=1，为何 A* 不先选它？",
    whenToUse: "有可靠启发式、需要最优或近最优路径的经典规划。",
  },
  "ch5-minimax": {
    wish: "MiniMax = 我方取 max、假设对手取 min，在博弈树上选最优走法。",
    mentalModel: "下棋时既想自己最好，又必须按对手最坏应对来规划。",
    mustSee: ["MAX/MIN 层交替", "叶节点分数如何回传", "Alpha-Beta 剪掉哪些分支"],
    misconception: "误区：MiniMax 就是图搜索——它是博弈树评估，不是 campus 找路；对手会主动选对你最差的应对。",
    selfCheck: "极小层为何取 min？若对手不理性，MiniMax 结论还成立吗？",
    whenToUse: "双人对弈、零和博弈、可枚举的决策树。",
  },
  "ch6-forward": {
    wish: "前向链像「撒网」：从已知事实出发，能推则推。",
    mentalModel: "事实池 + 规则扫描器；新事实入池，直到推不动。",
    mustSee: ["哪条规则被触发（✓）", "工作记忆何时出现新事实", "何时停止（推不出新结论）"],
    misconception: "误区：前向链一定比后向链「更正确」——其实都依赖规则完备性，只是搜索方向不同。",
    selfCheck: "若只有目标、事实很少，你会选前向还是后向？为什么？",
    whenToUse: "事实多、目标未知或需全盘推导时。",
  },
  "ch6-backward": {
    wish: "后向链像「倒推计划」：只碰与目标相关的规则。",
    mentalModel: "目标栈；匹配规则 → 产生子目标 → 直到命中事实。",
    mustSee: ["目标如何分解", "子目标何时命中事实库", "与同一例前向链步数对比"],
    misconception: "误区：后向链永远更快——若分支因子大，仍可能爆炸。",
    selfCheck: "证明「终有一死(苏格拉底)」时，第一个子目标是什么？",
    whenToUse: "目标明确、只需证一条结论时。",
  },
  "ch6-multihop": {
    wish: "多跳查询 = 在图谱上走满足关系类型约束的路径，不是裸 BFS。",
    mentalModel: "模板 (鲁迅,创作,?X) 且 (?X,发表于,?Y) 像 SQL JOIN，每跳过滤边类型。",
    mustSee: ["当前激活的节点/边", "关系类型是否匹配模板", "答案集合如何累积"],
    misconception: "误区：图谱推理就是图搜索——忽略关系语义会连出「鲁迅→发表于→桌子」这类荒谬路径。",
    selfCheck: "若去掉「发表于」约束，会多出哪些错误答案？",
    whenToUse: "结构化知识库问答、链接预测、合规路径查询。",
  },
  "ch6-pathrank": {
    wish: "软自洽 = 缺边时用多条间接路径计票，硬约束仍守关系类型。",
    mentalModel: "侦探拼图：没有直接证据时，看哪几条线索链最一致、权重最高。",
    mustSee: ["路径 A/B/C 各贡献多少票", "硬约束边是否被违反", "最终排序与直觉是否一致"],
    misconception: "误区：路径越多越可信——要看路径质量与权重，噪声边会误导投票。",
    selfCheck: "「莫言→获得→诺奖→代表→红高粱」这条链，哪一段是软推断？",
    whenToUse: "图谱不完备、需证据聚合的开放域问答。",
  },
  "ch8-forward": {
    wish: "前向传播 = 数据沿架构图从左流到右；每层输出是下一层输入。",
    mentalModel: "流水线工厂：每站加工一次，产品逐站变「抽象」。",
    mustSee: ["哪一层被点亮", "ReLU 后负值是否变 0", "ŷ=0.82 的含义（概率）"],
    misconception: "误区：以为前向只算一次——推理时算一遍，训练时每批样本都要重算并保存 a 供反向用。",
    selfCheck: "不看动画，你能说出从 x 到 ŷ 经过几步运算吗？",
    whenToUse: "任何神经网络推理、训练的第一步。",
  },
  "ch8-backward": {
    wish: "反向传播 = 把最终误差「分责任」给各层权重。",
    mentalModel: "快递溯源：从收件问题倒查每一环谁该负责。",
    mustSee: ["δ 从输出层出现", "ReLU′ 在 z≤0 处截断梯度", "为何需要保存前向时的 a"],
    misconception: "误区：反向传播是「反向执行网络」——其实是链式法则对 W 求偏导，方向沿计算图回溯。",
    selfCheck: "若隐藏层 ReLU 输出全为 0，这一层还能收到梯度吗？",
    whenToUse: "训练任何可微模型；与优化器配合更新 W。",
  },
  "ch8-attention": {
    wish: "注意力 = 按需求从编码器里「软查询」信息，解决对齐与长依赖。",
    mentalModel: "图书馆检索：Q 是你的问题，K 是索引，V 是内容，权重是相关性。",
    mustSee: ["编码器-解码器桥的位置", "「日记」行对「写」列权重最高", "Softmax 后权重和为 1"],
    misconception: "误区：注意力是 RNN 的简单替代——它并行看全句，但 O(n²) 且需位置信息。",
    selfCheck: "解码「日记」时，Q 来自解码器还是编码器？",
    whenToUse: "序列对齐、长上下文聚合、Transformer 核心。",
  },
  "ch8-transe": {
    wish: "TransE = 把三元组变成几何：头实体 + 关系向量 ≈ 尾实体。",
    mentalModel: "向量空间里的平移：从「鲁迅」沿「创作」方向走，应到「呐喊」附近。",
    mustSee: ["h+r≈t 正例距离缩小", "负采样推远错误尾实体", "嵌入维度 d 的作用"],
    misconception: "误区：嵌入能替代逻辑推理——它擅长相似度与补全，复杂推理仍需规则或 GNN。",
    selfCheck: "若 h+r 与 t 距离仍大，损失如何驱动更新？",
    whenToUse: "图谱很大、有噪声、需链接预测或相似度检索时。",
  },
  "ch7-tree": {
    wish: "决策树 = 用一串问题压缩数据；信息增益选「问哪个问题最划算」。",
    mentalModel: "二十问游戏：每个问题把人群分成更纯的两堆。",
    mustSee: ["根节点熵 H(S)", "为何先选「含分数」", "左子树为何纯为计算错误"],
    misconception: "误区：树越深越好——深树记忆训练集，泛化差；需剪枝。",
    selfCheck: "若「含分数=是」已全为计算错误，还要再分吗？",
    whenToUse: "需要可解释规则、特征离散、中小规模表格数据。",
  },
  "ch7-gd": {
    wish: "梯度下降 = 沿损失下降最快的方向小步更新参数。",
    mentalModel: "蒙眼下山：摸局部坡度，朝最陡的下坡方向挪一步。",
    mustSee: ["拟合直线如何贴近散点", "MSE 是否单调下降", "η 过大时是否震荡"],
    misconception: "误区：梯度下降一定找到全局最优——非凸损失会困在局部极小。",
    selfCheck: "若 η 增大 10 倍，演示中的直线会怎样？",
    whenToUse: "可微损失 + 连续参数（回归、神经网络训练）。",
  },
  "ch7-perceptron": {
    wish: "感知机 = 线性分类器，只在分错时更新边界。",
    mentalModel: "旋转门：错分样本把决策边界往「能分对」的方向推一把。",
    mustSee: ["哪一点被错分触发更新", "w 变化如何影响边界斜率", "何时停止（全对）"],
    misconception: "误区：感知机可解 XOR——线性不可分时永远学不会，需多层网络。",
    selfCheck: "若两类点线性可分，感知机步数有限吗？（感知机收敛定理）",
    whenToUse: "简单线性可分、教学入门、在线学习场景。",
  },
  "ch7-kmeans": {
    wish: "K-均值 = 无标签数据找 K 个簇中心，交替分配与更新。",
    mentalModel: "画 K 个磁铁：点被最近磁铁吸住，磁铁再移到簇内平均位置。",
    mustSee: ["E 步谁归哪簇", "M 步中心移动方向", "分配是否稳定"],
    misconception: "误区：K 已知且最优——K 需人工选或肘部法；初值不同结果可能不同。",
    selfCheck: "若 K=3 但真实只有 2 簇，会发生什么？",
    whenToUse: "聚类、向量量化、无监督预处理。",
  },
  "ch7-metrics": {
    wish: "P/R/F1 评「外层」泛化：同一模型，阈值不同指标不同。",
    mentalModel: "抓逃犯：严门槛少误抓（P↑）但漏抓多（R↓）；宽门槛相反。",
    mustSee: ["τ 变化时 TP/FP/FN 如何变", "P 与 R 的此消彼长", "F1 何时比准确率更合理"],
    misconception: "误区：准确率够用了——类别不平衡时准确率会骗人。",
    selfCheck: "漏诊重病（FN）代价高时，应调高还是调低 τ？",
    whenToUse: "分类部署前选阈值、不平衡数据、医疗/风控等代价不对称场景。",
  },
  "ch9-selfattn": {
    wish: "自注意力让每个词「看见」全句，并行聚合上下文。",
    mentalModel: "开班会：每人根据与发言者的相关度决定听谁。",
    mustSee: ["Q/K/V 各从哪来", "Softmax 后权重和为 1", "「写」这一行如何关注「鲁」"],
    misconception: "误区：注意力自带位置感——需额外加位置编码。",
    selfCheck: "自注意力与编码器-解码器注意力的 Q 来源有何不同？",
    whenToUse: "需要长距离依赖、并行训练的现代 LM/CV。",
  },
  "ch9-bpe": {
    wish: "BPE 让模型在「字」与「词」之间找粒度，平衡词表大小与覆盖率。",
    mentalModel: "合并最高频相邻对，像拼乐高：常用片段先固定成块。",
    mustSee: ["哪两个符号被合并", "合并后序列如何变短", "最终子词能否覆盖生僻组合"],
    misconception: "误区：BPE 懂语义——它只看频率，不懂意思。",
    selfCheck: "「狂人」与「日记」哪个先合并，取决于什么？",
    whenToUse: "开放词表、多语言、GPT 类模型分词。",
  },
  "ch9-w2v": {
    wish: "Word2Vec = 用共现统计把词变成向量，相似语境的词靠近。",
    mentalModel: "物以类聚：共现多的词在空间里被拉近距离。",
    mustSee: ["中心词与正例距离缩小", "负采样推远无关词", "向量维度 d 的作用"],
    misconception: "误区：词向量等于词典定义——它是统计共现，会有偏见与时代局限。",
    selfCheck: "「国王−男人+女人≈女王」为何有时成立有时不成立？",
    whenToUse: "词级语义、冷启动向量表示、理解注意力之前的表示层。",
  },
  "ch9-lm": {
    wish: "语言模型 = 自回归链式概率，训练学 P(w_i | 上文)。",
    mentalModel: "接龙游戏：给定前缀，预测下一个最合理的词元。",
    mustSee: ["前缀如何逐步扩展", "每步条件概率", "整句概率 = 连乘"],
    misconception: "误区：LM 理解语言——它建模统计共现，可幻觉、可偏见。",
    selfCheck: "困惑度 Perplexity 越低说明什么？与交叉熵有何关系？",
    whenToUse: "文本生成、语音识别、任何需要序列概率的任务。",
  },
  "ch10-cnn": {
    wish: "CNN 利用局部性：相邻像素相关，同一模式可出现在不同位置。",
    mentalModel: "用小模板（卷积核）在图上滑动扫描，参数共享。",
    mustSee: ["卷积核高亮框如何移动", "特征图尺寸为何变小", "池化保留什么（max）"],
    misconception: "误区：卷积「理解」物体——它只是提取局部模式，深层才组合成语义。",
    selfCheck: "步幅为 1、3×3 卷积核时，4×4 输入会输出几×几？",
    whenToUse: "图像、语音等局部结构明显的信号。",
  },
  "ch10-vit": {
    wish: "ViT = 把图像当句子：图块是词元，Transformer 看全局。",
    mentalModel: "切蛋糕成块，每块当一个词，用自注意力看全图。",
    mustSee: ["图块如何切分与展平", "位置编码为何必要", "编码器与语言模型同构"],
    misconception: "误区：ViT 完全取代 CNN——小数据上 CNN 仍常更强；ViT 需大数据预训练。",
    selfCheck: "没有位置编码，图块顺序丢失会怎样？",
    whenToUse: "大规模预训练、需长程依赖的图像任务。",
  },
  "ch10-mae": {
    wish: "MAE = 遮大部分图块，编码器学压缩表示，解码器学重构。",
    mentalModel: "完形填空：只看 25% 词猜全文，逼模型学语义而非死记。",
    mustSee: ["75% 图块被遮", "编码器输入仅可见图块", "重构像素作为自监督信号"],
    misconception: "误区：MAE 在做分类——预训练阶段无标签，下游才微调分类头。",
    selfCheck: "为何遮 75% 而不是 50%？（更高遮罩比例 → 更难任务）",
    whenToUse: "视觉自监督预训练、标注稀缺场景。",
  },
  "ch10-clip": {
    wish: "CLIP = 图文双塔对比学习，对齐图像与文本向量表示。",
    mentalModel: "相亲配对：配对的图文靠近，不配对的推远。",
    mustSee: ["图像/文本编码器各输出向量", "同一批样本内正负样本", "余弦相似度如何训练"],
    misconception: "误区：CLIP 生成图像——它学联合向量表示，生成需另接扩散等模型。",
    selfCheck: "零样本分类如何用「a photo of a {class}」文本提示？",
    whenToUse: "图文检索、零样本分类、多模态对齐。",
  },
  "ch11-mdp": {
    wish: "MDP 把「与环境互动」说清：状态、动作、奖励、下一状态。",
    mentalModel: "订机票 App：每步操作改变订单状态，完成给大奖励。",
    mustSee: ["智能体→环境→r,s′ 环", "累积回报 G 如何算", "γ 为何小于 1"],
    misconception: "误区：奖励只看眼前——没有 γ 折扣，智能体会短视。",
    selfCheck: "「已确认」后还有动作吗？终止状态有何特点？",
    whenToUse: "序贯决策、游戏、机器人、推荐。",
  },
  "ch11-actor": {
    wish: "Actor-Critic = 策略网络出动作，价值网络评状态，优势指导更新。",
    mentalModel: "Actor 是球员，Critic 是教练：A>0 说明这步比预期好，多练。",
    mustSee: ["π(a|s) 分布", "V(s) 基线", "A = R + γV(s′) − V(s)"],
    misconception: "误区：Critic 替 Actor 做决策——部署时通常只用 Actor 的 π。",
    selfCheck: "A<0 时 Actor 应提高还是降低该动作概率？",
    whenToUse: "连续/离散动作、需低方差策略梯度的 RL。",
  },
  "ch11-td": {
    wish: "TD 学习 = 用下一状态价值自举，不必等回合结束。",
    mentalModel: "边走边修正地图：每走一步就用「眼前奖励+下一步估值」更新当前估值。",
    mustSee: ["TD 目标 r + γV(s′)", "TD 误差 δ", "V(s) 如何逐步收敛"],
    misconception: "误区：TD 比蒙特卡洛更准——TD 有偏（用估计估估计）但方差小、在线。",
    selfCheck: "若 γ=0，TD 更新退化成什么？",
    whenToUse: "在线 RL、大状态空间、需 bootstrapping 的场景。",
  },
  "ch11-epsilon": {
    wish: "ε-贪心 = 训练时故意随机试差动作，避免只利用已知最优而陷入次优。",
    mentalModel: "八成选已知最好餐馆，两成随机探新店——否则永远不知道有没有更好的。",
    mustSee: ["探索/利用比例条", "ε 随训练衰减", "部署时 ε→0"],
    misconception: "误区：探索越多越好——过多探索浪费样本，收敛慢。",
    selfCheck: "多臂老虎机里，一直 greedy 会卡在次优臂吗？",
    whenToUse: "表格 Q-learning、简单 bandit、RL 训练初期。",
  },
  "ch12-diffusion": {
    wish: "扩散 = 学一个去噪器，把简单分布（噪声）逐步变回数据分布。",
    mentalModel: "雕塑逆过程：从一团泥（噪声）一点点修出形状（图像）。",
    mustSee: ["架构图 x₀→x_T→U-Net→x̂₀", "前向加噪 vs 反向去噪方向", "U-Net 输入含时间步 t"],
    misconception: "误区：扩散 = GAN——GAN 对抗训练；扩散是似然/分数匹配的迭代采样。",
    selfCheck: "训练时网络预测的是 x₀ 还是噪声 ε？",
    whenToUse: "高质量图像/音频生成，训练较稳定但采样慢。",
  },
  "ch12-mcts": {
    wish: "MCTS 用模拟估计哪步更好，适合分支巨大的博弈/规划。",
    mentalModel: "先试走几步棋，记胜率，再偏走 historically 赢多的分支（UCT）。",
    mustSee: ["选择沿 UCT 下降", "扩展添加新叶", "回传更新 Q/N"],
    misconception: "误区：MCTS 等于 MiniMax——MiniMax 要展开（或剪枝）完整树；MCTS 采样估计。",
    selfCheck: "Q/N 高但 N 很小，UCT 会倾向探索还是利用？",
    whenToUse: "围棋、规划、与策略/价值网络结合（AlphaGo）。",
  },
  "ch12-gan": {
    wish: "GAN = 生成器与判别器对抗，G 骗 D、D 辨真假。",
    mentalModel: "造假币者 vs 验钞机：双方交替变强，达到纳什均衡。",
    mustSee: ["z→G→x̂ 与真样本 x 进 D", "D(x̂) 随训练变化", "min-max 博弈直觉"],
    misconception: "误区：GAN 训练稳定——模式崩溃、梯度消失是常见坑；扩散往往更稳。",
    selfCheck: "D 太强时 G 的梯度会怎样？（G 学不动）",
    whenToUse: "图像生成、数据增强、域适应（需调参技巧）。",
  },
  "ch12-repr": {
    wish: "表征搜索 = 换问题坐标系，让优化地形更平滑。",
    mentalModel: "同一座山，代数坐标崎岖，几何坐标有缓坡——换表征再搜。",
    mustSee: ["代数表征损失卡住", "退火允许差解", "换几何后损失下降"],
    misconception: "误区：退火保证全局最优——它提高跳出局部的概率，不保证最优。",
    selfCheck: "模拟退火温度 T 高时，接受差解的概率大还是小？",
    whenToUse: "组合优化、定理证明搜索、非凸景观。",
  },
};

function renderMentorChapterPanel(ch) {
  const meta = chapters[ch];
  if (!meta) return "";
  return `
    <div class="mentor-chapter-panel">
      <p class="mentor-voice">本章导学</p>
      <p class="mentor-wish">${esc(meta.wish)}</p>
      <ul class="hero-goals" aria-label="学习目标">
        ${meta.pillars.map((p) => `<li><strong>${esc(p.label)}</strong>${esc(p.desc)}</li>`).join("")}
      </ul>
    </div>`;
}

function renderMentorSummary(mentorKey) {
  const m = notebooks[mentorKey];
  if (!m) return "";
  const misconception = m.misconception.replace(/^误区[：:]\s*/, "");
  return `
    <div class="algo-summary-stack">
      <div class="mentor-callout mentor-callout--warn"><h4>常见误区</h4><p>${esc(misconception)}</p></div>
      <div class="mentor-callout mentor-callout--quiz"><h4>检验一下</h4><p>${esc(m.selfCheck)}</p></div>
      <div class="mentor-callout mentor-callout--use"><h4>适用场景</h4><p>${esc(m.whenToUse)}</p></div>
    </div>`;
}

function renderMentorNotebookHeader(_key) {
  return "";
}

function renderMentorCell(kind, key) {
  const m = notebooks[key];
  if (!m) return "";
  if (kind === "misconception") {
    const text = m.misconception.replace(/^误区[：:]\s*/, "");
    return `<div class="mentor-callout mentor-callout--warn"><h4>常见误区</h4><p>${esc(text)}</p></div>`;
  }
  if (kind === "selfCheck") {
    return `<div class="mentor-callout mentor-callout--quiz"><h4>检验一下</h4><p>${esc(m.selfCheck)}</p></div>`;
  }
  if (kind === "when") {
    return `<div class="mentor-callout mentor-callout--use"><h4>适用场景</h4><p>${esc(m.whenToUse)}</p></div>`;
  }
  return "";
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function mentorChapterNum(key) {
  const m = String(key).match(/^ch(\d+)-/);
  return m ? Number(m[1]) : null;
}

function buildMentorCopyPrompt(mentorKey, kind, chapterNum) {
  const m = notebooks[mentorKey];
  if (!m) return "";
  const algo = mentorKey.replace(/^ch\d+-/, "");
  const caseBlock = window.courseCopyPrompts?.mentorCase?.(mentorKey) || "";
  const M = window.courseCopyPrompts?.mentor;
  if (!M) return "";

  if (kind === "misconception") {
    return M.misconception(0, algo, m.misconception.replace(/^误区[：:]\s*/, ""), caseBlock);
  }
  if (kind === "selfCheck") {
    return M.selfCheck(0, algo, m.selfCheck, caseBlock);
  }
  if (kind === "when") {
    return M.when(0, algo, m.whenToUse, caseBlock);
  }
  return "";
}

/** 笔记本练习合并格：误区 + 自测 + 适用 + 实验练习 */
function buildMentorBundleCopyPrompt(mentorKey, chapterNum, practicePrompt, labTarget, whenCopyPrompt, selfCheckCopyPrompt) {
  const m = notebooks[mentorKey];
  if (!m) return "";
  const algo = mentorKey.replace(/^ch\d+-/, "");
  const caseBlock = window.courseCopyPrompts?.mentorCase?.(mentorKey) || "";
  const M = window.courseCopyPrompts?.mentor;
  if (!M) return "";

  let out = M.bundle(
    0,
    algo,
    m.misconception.replace(/^误区[：:]\s*/, ""),
    m.selfCheck,
    caseBlock,
  );
  if (selfCheckCopyPrompt && selfCheckCopyPrompt !== out) out += `\n\n---\n\n${selfCheckCopyPrompt}`;
  if (whenCopyPrompt && whenCopyPrompt !== selfCheckCopyPrompt) out += `\n\n---\n\n${whenCopyPrompt}`;
  return out;
}

/** 导师标准 cell 序列模板（可复用在各章 refactor） */
const CELL_FLOW = {
  intuition: "intuition",
  model: "model",
  demo: "demo",
  pitfall: "pitfall",
  quiz: "quiz",
};

window.coursePedagogy = {
  MENTOR_PRINCIPLES,
  chapters,
  notebooks,
  CELL_FLOW,
  renderMentorChapterPanel,
  renderMentorNotebookHeader,
  renderMentorCell,
  renderMentorSummary,
  buildMentorCopyPrompt,
  buildMentorBundleCopyPrompt,
  mentorChapterNum,
};
