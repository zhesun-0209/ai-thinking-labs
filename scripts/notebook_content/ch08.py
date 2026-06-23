"""第 8–12 章 notebook — 与 ch5 同密度的逐步演示。"""

from __future__ import annotations

from notebook_content import runestone as rs
from notebook_content.runestone import boot, flatten


def notebooks() -> dict[str, list]:
    out: dict[str, list] = {}
    out.update(_ch08())
    out.update(_ch09())
    out.update(_ch10())
    out.update(_ch11())
    out.update(_ch12())
    return out


def _ch08() -> dict[str, list]:
    B = boot("ch08", "from neural import *")
    return {
        "ch08_mlp_backprop.ipynb": flatten([
            rs.chapter_link(
                "第 8 章 · MLP 前向与反向",
                "血糖+运动→风险：逐层打印 z、h、ŷ 与 δ。",
                ["前向 trace 表", "反向 δ 链式法则", "ReLU 截断梯度"],
                "../ch8.html",
            ),
            rs.section("1", "网络结构"),
            rs.reading("两层 MLP：输入 x → 隐藏 h=ReLU(W1x+b1) → 输出 ŷ=σ(W2h+b2)。"),
            rs.listing("MLP", "z1=W1x+b1; h=ReLU(z1); y=sigmoid(W2h+b2)"),
            *rs.stepcode(B, "display(forward_trace())", "forward_demo()"),
            *rs.stepcode("plot_mlp_flow()"),
            rs.self_check("隐藏层维度？", answer="2，对应 h1、h2。"),
            rs.section("2", "反向传播"),
            rs.subsection("2.1", "δ 回传", "δ_out 从输出层产生，链式法则乘回隐藏层；ReLU′=0 处梯度截断。"),
            rs.listing("Backprop", "delta_out = dL/dy * dy/dz\n delta_h = W2^T delta_out * ReLU'(z1)"),
            *rs.stepcode("backward_demo()"),
            rs.self_check("ReLU 全 0 时 δ_h？", answer="全 0，无梯度回传。"),
            rs.section("3", "与网页对照"),
            rs.reading("ŷ≈0.82、δ_out≈0.036 与 ch8 网页一致。"),
            rs.summary("前向存激活；反向分梯度。对照 [ch8.html](../ch8.html)。"),
            rs.exercises("若输出层换 softmax，δ_out 形式？", "b1 梯度如何计算？"),
        ]),
        "ch08_transe_attention.ipynb": flatten([
            rs.chapter_link(
                "第 8 章 · TransE 与 Attention",
                "向量平移嵌入 + 解码端软对齐。",
                ["TransE 距离与 margin", "Attention softmax 权重"],
                "../ch8.html",
            ),
            rs.section("1", "TransE 嵌入"),
            rs.reading("希望 **h + r ≈ t**；正例距离小，负例 tail 替换后距离大。"),
            rs.listing("TransE", "d = ||h + r - t||\nloss = max(0, d+ + margin - d-)"),
            *rs.stepcode(B, "transe_demo()", "plot_transe()"),
            rs.self_check("正例 d+ 约多少？", answer="0.31，小于负例 2.08。"),
            rs.section("2", "Cross-Attention"),
            rs.reading("解码端 query「写」对 encoder 各 token 算 score，softmax 得权重 α。"),
            rs.listing("Attention", "scores = QK^T\nalpha = softmax(scores)"),
            *rs.stepcode("attention_demo()", "plot_attention()"),
            rs.self_check("「写」的 α 最大？", answer="约 0.80，t1 对应「写」。"),
            rs.summary("TransE=几何平移；Attention=软查询。对照 [ch8.html](../ch8.html)。"),
            rs.exercises("margin 增大对 loss 影响？", "α 和为 1 保证什么？"),
        ]),
    }


def _ch09() -> dict[str, list]:
    B = boot(
        "ch09",
        "from bpe import *",
    )
    Bl = boot("ch09", "from language import *")
    return {
        "ch09_bpe.ipynb": flatten([
            rs.chapter_link(
                "第 9 章 · BPE",
                "「鲁迅写了狂人日记」：逐次合并最高频 byte pair。",
                ["统计 pair 频次", "逐步 merge", "GIF 看 token 序列变化"],
                "../ch9.html",
            ),
            rs.section("1", "初始 token"),
            rs.reading("语料先切成字符级 token；统计相邻 pair 出现次数。"),
            *rs.stepcode(B, "display(first_merge_table())"),
            rs.section("2", "逐步合并"),
            rs.listing("BPE", "while vocab large:\n  pair = argmax count(a,b)\n  merge pair -> new token"),
            *rs.stepcode(
                "bpe_frames = codelens_bpe_merges()",
                "animate_bpe_merges()",
                "display(steps_table())",
            ),
            rs.self_check("第一次合并哪一对？", answer="见 demo_first_merge 最高频 pair。"),
            rs.section("3", "与网页验证"),
            rs.reading("每步 `与网页一致` 字段应为 True。"),
            rs.summary("BPE 由高频 pair 迭代合并子词。对照 [ch9.html](../ch9.html)。"),
            rs.exercises("为何先合并高频 pair？", "中文 BPE 与英文有何不同？"),
        ]),
        "ch09_skipgram_toy.ipynb": flatten([
            rs.chapter_link(
                "第 9 章 · Skip-gram",
                "中心词「鲁迅」与上下文「写」向量靠近。",
                ["共现对", "cos 相似度变化"],
                "../ch9.html",
            ),
            rs.section("1", "词向量训练"),
            rs.reading("Skip-gram 用中心词预测上下文；共现词向量在空间中靠近。"),
            rs.listing("Skip-gram", "maximize P(context | center)"),
            *rs.stepcode(Bl, "skipgram_demo()", "plot_skipgram_sim()"),
            rs.self_check("训练后 cos 变化方向？", answer="「鲁迅-写」相似度上升。"),
            rs.summary("共现塑造向量空间。对照 [ch9.html](../ch9.html)。"),
            rs.exercises("窗口 size=1 vs 5 有何影响？", "负采样作用？"),
        ]),
        "ch09_attention_lm.ipynb": flatten([
            rs.chapter_link(
                "第 9 章 · Self-Attention 与 LM",
                "Q=「写」对全句权重 + 字符 bigram。",
                ["α 分布", "下一字符预测"],
                "../ch9.html",
            ),
            rs.section("1", "Self-Attention"),
            rs.reading("每个 token 作 query 对所有 key 算 attention，得到上下文加权表示。"),
            *rs.stepcode(Bl, "display(self_attention_matrix())", "plot_attention_heatmap()"),
            rs.section("2", "字符语言模型"),
            rs.reading("bigram 统计 P(c_t | c_{t-1})，逐步预测下一字符。"),
            rs.listing("Char LM", "P(next | prev) from counts"),
            *rs.stepcode("char_lm_demo()"),
            rs.self_check("「写」后最可能字符？", answer="见 char_lm_demo 输出。"),
            rs.summary("Attention 软对齐；LM 预测下一 token。对照 [ch9.html](../ch9.html)。"),
            rs.exercises("Self-attn 与 RNN 优劣？", "bigram 局限？"),
        ]),
    }


def _ch10() -> dict[str, list]:
    B = boot(
        "ch10",
        "from vision import *",
    )
    return {
        "ch10_conv2d_numpy.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · 卷积",
                "4×4 输入 → 2×2 卷积 → MaxPool。",
                ["卷积核滑动逐步", "GIF 高亮窗口", "池化"],
                "../ch10.html",
            ),
            rs.section("1", "卷积定义"),
            rs.reading("输出每个位置 = 输入 patch 与 kernel 元素积之和（valid 卷积）。"),
            rs.listing("conv2d", "out[i,j] = sum(input[i:i+k, j:j+k] * kernel)"),
            *rs.stepcode(
                B,
                "conv_frames = codelens_conv()",
                "animate_conv_slide()",
                "display(conv_output_table())",
            ),
            *rs.stepcode("plot_conv()"),
            rs.self_check("2×2 输出有几个值？", answer="4 个，对应 4 个滑动位置。"),
            rs.summary("局部连接+权值共享。对照 [ch10.html](../ch10.html)。"),
            rs.exercises("padding=1 输出尺寸？", "stride=2 呢？"),
        ]),
        "ch10_vit_patchify.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · ViT Patchify",
                "4×4 → 4 个 2×2 patch token。",
                ["patch 切分", "token 序列"],
                "../ch10.html",
            ),
            rs.section("1", "Patch 切分"),
            rs.reading("图像分块展平为 token，加位置编码后送 Transformer。"),
            *rs.stepcode(boot("ch10", "from vision import *"), "vit_patchify()", "plot_patches()"),
            rs.self_check("几个 patch？", answer="4 个 2×2。"),
            rs.summary("ViT 把图像当 token 序列。对照 [ch10.html](../ch10.html)。"),
            rs.exercises("patch 更大时 token 数？", "与 CNN 感受野对比？"),
        ]),
        "ch10_mae_masking.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · MAE",
                "75% patch 掩码，Encoder 只看 25%。",
                ["随机掩码", "Encoder/Decoder 分工"],
                "../ch10.html",
            ),
            rs.section("1", "掩码策略"),
            rs.reading("随机遮盖大部分 patch；Encoder 只看可见 token；Decoder 重构全图。"),
            *rs.stepcode(boot("ch10", "from vision import *"), "mae_demo()", "plot_mae_mask()"),
            rs.self_check("可见比例？", answer="25%，1/4 patch。"),
            rs.summary("MAE 自监督学表示。对照 [ch10.html](../ch10.html)。"),
            rs.exercises("掩码比例 50% 影响？", "与 BERT MLM 异同？"),
        ]),
        "ch10_clip_infonce.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · CLIP",
                "图文正例 cos 高、负例 cos 低。",
                ["对比学习", "InfoNCE"],
                "../ch10.html",
            ),
            rs.section("1", "对比损失"),
            rs.reading("同一 batch 内配对图文为正例，错配为负例；拉近正例、推远负例。"),
            *rs.stepcode(boot("ch10", "from vision import *"), "clip_infonce()", "plot_clip_cos()"),
            rs.self_check("正例 cos 约？", answer="0.91，负例约 0.08。"),
            rs.summary("CLIP 学跨模态对齐。对照 [ch10.html](../ch10.html)。"),
            rs.exercises("batch 增大影响？", "hard negative 作用？"),
        ]),
    }


def _ch11() -> dict[str, list]:
    B = boot(
        "ch11",
        "from rl import *",
    )
    return {
        "ch11_mdp_value_iteration.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · MDP 与价值迭代",
                "订机票四状态：奖励、γ、Bellman 备份。",
                ["MDP 链", "价值迭代逐步", "V 收敛 GIF"],
                "../ch11.html",
            ),
            rs.section("1", "MDP 定义"),
            rs.reading("状态序列 S0→S1→S2→S3，每步即时奖励 R(s)，折扣 γ 权衡远期回报。"),
            rs.listing("Return", "G = R0 + gamma R1 + gamma^2 R2 + ..."),
            *rs.stepcode(B, "mdp_demo()", "plot_mdp_chain()"),
            rs.section("2", "价值迭代"),
            rs.subsection("2.1", "Bellman 备份", "V(s) ← R(s) + γ V(s')，从后向前同步更新。"),
            rs.listing("Bellman", "V(s) <- R(s) + gamma * V(s')"),
            *rs.stepcode(
                "vi_frames = codelens_value_iteration()",
                "animate_value_iteration()",
                "display(value_iteration_table())",
            ),
            *rs.stepcode("plot_value_iteration()"),
            rs.self_check("V(S0) 收敛约？", answer="约 9.8，见输出。"),
            rs.summary("长期回报用 γ 折扣；迭代至 V 稳定。对照 [ch11.html](../ch11.html)。"),
            rs.exercises("γ=0 时策略？", "γ→1 时？"),
        ]),
        "ch11_td_learning.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · TD(0)",
                "bootstrap：用 V(s') 更新 V(s)。",
                ["TD target", "一步更新"],
                "../ch11.html",
            ),
            rs.section("1", "TD 更新"),
            rs.reading("不需等 episode 结束：用 r + γV(s') 作 target，逐步修正 V(s)。"),
            rs.listing("TD(0)", "V(s) <- V(s) + alpha * (r + gamma V(s') - V(s))"),
            *rs.stepcode(boot("ch11", "from rl import *"), "td_demo()"),
            rs.self_check("target 约多少？", answer="r + γV(s') = 1 + 0.9×4 = 4.6。"),
            rs.summary("TD 在线 bootstrap。对照 [ch11.html](../ch11.html)。"),
            rs.exercises("α 过大？", "与 MC 区别？"),
        ]),
        "ch11_epsilon_greedy.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · ε-贪心",
                "1000 次模拟：ε 与探索比例。",
                ["探索 vs 利用", "ε 影响"],
                "../ch11.html",
            ),
            rs.section("1", "多臂 bandit"),
            rs.reading("以概率 ε 随机探索，1-ε 选当前最优臂。"),
            rs.listing("ε-greedy", "if rand() < eps: random arm\nelse: argmax Q"),
            *rs.stepcode(boot("ch11", "from rl import *"), "bandit_demo()", "plot_epsilon_greedy()"),
            rs.self_check("ε=0.4 探索约？", answer="约 40%。"),
            rs.summary("ε 大探索多；ε 小利用多。对照 [ch11.html](../ch11.html)。"),
            rs.exercises("ε 衰减 schedule？", "UCB 与 ε-greedy？"),
        ]),
    }


def _ch12() -> dict[str, list]:
    B = boot("ch12", "from create import *")
    return {
        "ch12_repr_search_annealing.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 表征搜索与退火",
                "换表征跳出局部最优，loss 逐步下降。",
                ["表征切换", "loss 轨迹"],
                "../ch12.html",
            ),
            rs.section("1", "搜索过程"),
            rs.reading("同一任务换代数/几何表征；模拟退火允许暂时升 loss 跳出局部最优。"),
            *rs.stepcode(B, "annealing_demo()", "plot_annealing()"),
            rs.self_check("最低 loss？", answer="2.3，几何表征。"),
            rs.summary("表征+搜索策略影响最终 loss。对照 [ch12.html](../ch12.html)。"),
            rs.exercises("退火温度 schedule？", "何时换表征？"),
        ]),
        "ch12_mcts.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · MCTS / UCT",
                "Q/N + 探索项；未访问节点优先。",
                ["UCT 公式", "选择分数"],
                "../ch12.html",
            ),
            rs.section("1", "UCT 选择"),
            rs.reading("平衡利用 Q/N 与探索 c√(ln N/n)；n=0 时优先访问。"),
            rs.listing("UCT", "score = Q/N + c * sqrt(ln N / n)"),
            *rs.stepcode(B, "mcts_demo()", "plot_uct()"),
            rs.self_check("未访问走法 c 的 UCT？", answer="+∞，优先扩展。"),
            rs.summary("MCTS 四步：选择-扩展-模拟-回传。对照 [ch12.html](../ch12.html)。"),
            rs.exercises("c 增大影响？", "与 UCB1 关系？"),
        ]),
        "ch12_diffusion_1d.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 1D 扩散",
                "前向加噪逐步 x 序列。",
                ["噪声步", "x 轨迹", "GIF 逐步"],
                "../ch12.html",
            ),
            rs.section("1", "前向过程"),
            rs.reading("每步 x ← x + ε，ε~N(0,σ²)，数据逐渐变为噪声。"),
            rs.listing("Forward", "x_{t+1} = x_t + epsilon,  epsilon ~ N(0, sigma^2)"),
            *rs.stepcode(
                boot("ch12", "from create import *"),
                "diff_frames = codelens_diffusion_1d()",
                "animate_diffusion_1d()",
                "diffusion_1d_table()",
            ),
            *rs.stepcode("xs = diffusion_1d_values()", "plot_diffusion_1d(xs)"),
            rs.self_check("步数？", answer="5 步加噪 + 初始点。"),
            rs.summary("扩散前向逐步破坏结构。对照 [ch12.html](../ch12.html)。"),
            rs.exercises("σ 增大？", "与 DDPM 关系？"),
        ]),
        "ch12_diffusion_digits.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 小图像 Diffusion 经典缩影",
                "用 sklearn digits 的 8×8 手写数字展示 DDPM 的前向加噪、反向去噪和采样轨迹。",
                ["真实小图像案例", "DDPM 加噪公式", "从噪声逐步回到数字形状", "对比 toy 与经典图像生成"],
                "../ch12.html",
            ),
            rs.section("1", "为什么要换成小图像"),
            rs.reading(
                "1D toy 适合讲公式，但读者很难把它和「生成图像」联系起来。这里用经典 `sklearn.datasets.load_digits`：每张图只有 8×8，足够快，也能看清数字结构如何被噪声破坏。",
                "这个 notebook 不训练大模型；它用同类数字的平均图像作为教学版 denoiser，展示 diffusion 的过程缩影。",
            ),
            rs.section("2", "前向扩散：清晰数字如何变成噪声"),
            rs.listing("DDPM forward", "x_t = sqrt(alpha_bar_t) * x0 + sqrt(1-alpha_bar_t) * epsilon"),
            *rs.stepcode(B, "digits_diffusion_table()", "plot_digits_forward(seed=7, digit=3)"),
            rs.self_check("t 越大，signal_scale 和 noise_scale 如何变化？", answer="signal_scale 下降，noise_scale 上升，图像越来越像噪声。"),
            rs.section("3", "反向去噪：模型到底学什么"),
            rs.reading(
                "真实 diffusion 模型会学习预测噪声或 score。这里用「同类数字原型」模拟一个已经学到数字结构的 denoiser：每一步都把噪声图往数字原型拉近一点。",
                "这不是生产模型，但能清楚展示为什么 reverse process 是一串小步修复，而不是一次性画图。",
            ),
            *rs.stepcode("plot_digits_reverse(seed=7, digit=3)", "plot_digits_denoiser_comparison(seed=7, digit=3)", "digits_diffusion_summary(seed=7, digit=3)"),
            rs.self_check("denoised 的 MSE 是否应低于 noisy？", answer="应低于 noisy，说明去噪轨迹把图像拉回了数据分布附近。"),
            rs.section("4", "和真实 DDPM 的边界"),
            rs.reading(
                "**相同点**：都有前向加噪、按时间步逐步反推、从纯噪声回到数据分布。",
                "**不同点**：真实 DDPM 的 denoiser 是神经网络，这里用类原型代替，只用于理解过程。",
            ),
            rs.summary("经典图像 diffusion 的核心不是魔法生成，而是学习每个噪声强度下如何做一小步去噪。对照 [ch12.html](../ch12.html)。"),
            rs.exercises("把 digit=3 改成 digit=8，反向轨迹有什么差别？", "如果 denoiser 用错类别原型，会发生什么？"),
        ]),
        "ch12_gan_toy.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · GAN",
                "判别器 D(x̂) 训练轨迹。",
                ["D 输出", "对抗平衡"],
                "../ch12.html",
            ),
            rs.section("1", "判别器训练"),
            rs.reading("G 生成假样本，D 区分真假；理想平衡 D≈0.5。"),
            *rs.stepcode(B, "gan_toy()", "plot_gan_d()"),
            rs.self_check("D 最终约？", answer="0.50，接近理想。"),
            rs.summary("GAN  minimax 博弈。对照 [ch12.html](../ch12.html)。"),
            rs.exercises("模式崩塌？", "WGAN 改进？"),
        ]),
        "ch12_diffusion_toy.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 扩散去噪概念",
                "加噪与去噪逆过程（1D 玩具）。",
                ["前向/反向", "逆过程", "逐步 trace"],
                "../ch12.html",
            ),
            rs.section("1", "双向过程"),
            rs.reading("前向加噪；学习网络逐步去噪，从噪声恢复数据。"),
            rs.listing("Reverse", "x_{t-1} = denoise_net(x_t, t)"),
            *rs.stepcode(
                boot("ch12", "from create import *"),
                "diff_frames = codelens_diffusion_1d()",
                "animate_diffusion_1d()",
                "diffusion_1d_table()",
            ),
            *rs.stepcode("xs = diffusion_1d_values()", "plot_diffusion_1d(xs)"),
            rs.self_check("图中两条线含义？", answer="蓝=前向加噪，绿=概念性反向去噪。"),
            rs.summary("生成 = 学逆扩散。对照 [ch12.html](../ch12.html)。"),
            rs.exercises("去噪步数 T？", "与 score matching？"),
        ]),
        "ch12_alphafold_concepts.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · AlphaFold 流程",
                "序列 → MSA → Evoformer → 3D。",
                ["四阶段 pipeline", "各模块作用"],
                "../ch12.html",
            ),
            rs.section("1", "Pipeline"),
            rs.reading("MSA 提共变；Evoformer 融合序列与结构先验；输出 3D 坐标与 pLDDT 置信度。"),
            *rs.stepcode(B, "alphafold_outline()"),
            rs.self_check("Evoformer 输入？", answer="MSA + 配对表示。"),
            rs.summary("AF2 = 序列→结构端到端。对照 [ch12.html](../ch12.html)。"),
            rs.exercises("pLDDT 含义？", "与 Rosetta 对比？"),
        ]),
    }
