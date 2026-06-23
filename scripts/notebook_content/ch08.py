"""Chapters 8-12 executable notebooks."""

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
    b = boot("ch08", "from neural import *")
    return {
        "ch08_mlp_backprop.ipynb": flatten([
            rs.chapter_link(
                "第 8 章 · MLPClassifier",
                ["调用 sklearn MLPClassifier", "输出预测概率", "绘制网络结构"],
                "../ch8.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 用 sklearn Pipeline 标准化特征，并训练 MLPClassifier。\nfrom sklearn.pipeline import make_pipeline\nfrom sklearn.preprocessing import StandardScaler\nX_mlp, y_mlp = mlp_dataset()\nmlp = make_pipeline(\n    StandardScaler(),\n    MLPClassifier(hidden_layer_sizes=(2,), activation='relu', solver='lbfgs', random_state=0, max_iter=1000),\n)\nmlp.fit(X_mlp, y_mlp)",
                "# 查看 sklearn MLPClassifier 的预测概率。\ndisplay(mlp_result_table(mlp, X_mlp, y_mlp))",
                "# 绘制这个小 MLP 的输入-隐藏层-输出结构。\nplot_mlp_flow()",
            ),
        ]),
        "ch08_transe_attention.ipynb": flatten([
            rs.chapter_link(
                "第 8 章 · TransE 与 Attention",
                ["运行 TransE 距离计算", "运行 attention 权重计算", "绘制结果图"],
                "../ch8.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# TransE 这里用 numpy 最小示例计算正负三元组距离。\ntranse_demo()",
                "# 绘制 h + r 接近 t 的几何关系。\nplot_transe()",
            ),
            rs.section("1", "Attention"),
            *rs.stepcode(
                "# Attention 这里用 numpy softmax 计算权重。\nattention_demo()",
                "# 绘制 attention 权重分布。\nplot_attention()",
            ),
        ]),
    }


def _ch09() -> dict[str, list]:
    b_bpe = boot("ch09", "from bpe import *")
    b_lm = boot("ch09", "from language import *")
    return {
        "ch09_bpe.ipynb": flatten([
            rs.chapter_link(
                "第 9 章 · BPE",
                ["加载 BPE 数据", "运行合并步骤", "输出合并表"],
                "../ch9.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b_bpe,
                "# 加载固定的 BPE 示例数据。\nspec = load_bpe_spec()",
                "# 显示第一次 merge 的 pair 统计。\ndisplay(first_merge_table())",
            ),
            rs.section("1", "运行 BPE"),
            *rs.stepcode(
                "# 运行预设 merge 序列，得到每一步 token 历史。\nhistory = run_from_spec()",
                "# 输出每一轮 merge 之后的 token 表。\ndisplay(steps_table())",
                "# 打印第一次 merge 的复现实验输出。\ndemo_first_merge()",
            ),
        ]),
        "ch09_skipgram_toy.ipynb": flatten([
            rs.chapter_link(
                "第 9 章 · Skip-gram",
                ["运行词向量玩具训练", "绘制相似度变化"],
                "../ch9.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b_lm,
                "# 运行一个 numpy 版 Skip-gram 玩具训练。\nskipgram_demo()",
                "# 绘制中心词和上下文词的相似度变化。\nplot_skipgram_sim()",
            ),
        ]),
        "ch09_attention_lm.ipynb": flatten([
            rs.chapter_link(
                "第 9 章 · Self-Attention 与字符 LM",
                ["输出 attention 矩阵", "运行字符 bigram 预测"],
                "../ch9.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b_lm,
                "# 输出 self-attention 的小矩阵。\ndisplay(self_attention_matrix())",
                "# 绘制 attention heatmap。\nplot_attention_heatmap()",
            ),
            rs.section("1", "字符语言模型"),
            *rs.stepcode("# 运行字符 bigram 统计并输出下一字符预测。\nchar_lm_demo()"),
        ]),
    }


def _ch10() -> dict[str, list]:
    b = boot("ch10", "from vision import *")
    return {
        "ch10_conv2d_numpy.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · 卷积",
                ["运行 2D 卷积", "输出卷积表", "绘制特征图"],
                "../ch10.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 直接调用 scipy.signal.correlate2d 计算 valid 卷积。\nfrom scipy.signal import correlate2d\nfeature = correlate2d(IMG, KERNEL, mode='valid')\nprint(feature.astype(int))",
                "# 输出每个窗口位置的卷积值表。\ndisplay(conv_output_table())",
                "# 绘制输入、卷积输出和 MaxPool 结果。\nplot_conv()",
            ),
        ]),
        "ch10_vit_patchify.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · ViT Patchify",
                ["运行 patch 切分", "绘制 patch 图"],
                "../ch10.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 用 numpy reshape/transpose 把图像切成 patch token。\nvit_patchify()",
                "# 绘制原图和 2x2 patch。\nplot_patches()",
            ),
        ]),
        "ch10_mae_masking.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · MAE",
                ["运行 mask 示例", "绘制可见 patch"],
                "../ch10.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 运行 MAE mask 示例，输出可见 patch 索引。\nmae_demo()",
                "# 绘制被 mask 后的可见 patch。\nplot_mae_mask()",
            ),
        ]),
        "ch10_clip_infonce.ipynb": flatten([
            rs.chapter_link(
                "第 10 章 · CLIP",
                ["运行图文相似度计算", "绘制对比结果"],
                "../ch10.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 用 numpy 向量计算正负图文对 cosine similarity。\nclip_infonce()",
                "# 绘制正负样本的相似度对比。\nplot_clip_cos()",
            ),
        ]),
    }


def _ch11() -> dict[str, list]:
    b = boot("ch11", "from rl import *")
    return {
        "ch11_mdp_value_iteration.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · MDP 与价值迭代",
                ["运行 MDP 示例", "输出价值迭代表", "绘制价值曲线"],
                "../ch11.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 运行 MDP 链式状态示例，输出折扣回报。\nmdp_demo()",
                "# 绘制状态链和奖励。\nplot_mdp_chain()",
            ),
            rs.section("1", "价值迭代"),
            *rs.stepcode(
                "# 输出 Bellman 价值迭代表。\ndisplay(value_iteration_table())",
                "# 绘制 V(S0) 的收敛曲线。\nplot_value_iteration()",
            ),
        ]),
        "ch11_td_learning.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · TD(0)",
                ["运行 TD(0) 一步更新"],
                "../ch11.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(b, "# 运行 TD(0) 一步 bootstrap 更新。\ntd_demo()"),
        ]),
        "ch11_epsilon_greedy.ipynb": flatten([
            rs.chapter_link(
                "第 11 章 · epsilon-贪心",
                ["运行 bandit 示例", "绘制探索比例"],
                "../ch11.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 运行 epsilon-greedy 多臂老虎机模拟。\nbandit_demo()",
                "# 绘制不同 epsilon 下的探索比例。\nplot_epsilon_greedy()",
            ),
        ]),
    }


def _ch12() -> dict[str, list]:
    b = boot("ch12", "from create import *")
    return {
        "ch12_repr_search_annealing.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 表征搜索与退火",
                ["运行退火搜索", "绘制 loss 曲线"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 运行表征搜索/退火示例，输出候选 loss。\nannealing_demo()",
                "# 绘制搜索过程中的 loss 曲线。\nplot_annealing()",
            ),
        ]),
        "ch12_mcts.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · MCTS / UCT",
                ["运行 UCT 分数计算", "绘制分数图"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 运行 UCT 分数计算示例。\nmcts_demo()",
                "# 绘制各走法的 UCT 分数。\nplot_uct()",
            ),
        ]),
        "ch12_diffusion_1d.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 1D 扩散",
                ["运行 1D 加噪", "绘制扩散轨迹"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 输出 1D 前向加噪数值表。\ndiffusion_1d_table()",
                "# 生成固定随机种子的 1D 扩散轨迹。\nxs = diffusion_1d_values()",
                "# 绘制 1D 前向/反向轨迹。\nplot_diffusion_1d(xs)",
            ),
        ]),
        "ch12_diffusion_digits.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 小图像 Diffusion",
                ["运行噪声调度", "绘制前向加噪", "绘制反向去噪"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 使用 sklearn.datasets.load_digits 的 8x8 手写数字数据。\ndigits_diffusion_table()",
                "# 绘制固定数字的前向加噪序列。\nplot_digits_forward(seed=7, digit=3)",
            ),
            rs.section("1", "反向去噪"),
            *rs.stepcode(
                "# 绘制从噪声逐步回到数字形状的反向轨迹。\nplot_digits_reverse(seed=7, digit=3)",
                "# 对比 clean / noisy / prototype / denoised 四张图。\nplot_digits_denoiser_comparison(seed=7, digit=3)",
                "# 输出 noisy 和 denoised 相对 clean 的 MSE。\ndigits_diffusion_summary(seed=7, digit=3)",
            ),
        ]),
        "ch12_gan_toy.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · GAN",
                ["运行判别器输出示例", "绘制 D(x) 轨迹"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 运行 GAN 判别器输出的玩具轨迹。\ngan_toy()",
                "# 绘制 D(生成样本) 的变化。\nplot_gan_d()",
            ),
        ]),
        "ch12_diffusion_toy.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · 扩散去噪概念",
                ["运行 1D 扩散", "绘制前向/反向轨迹"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(
                b,
                "# 生成固定随机种子的 1D 扩散轨迹。\nxs = diffusion_1d_values()",
                "# 绘制前向加噪和概念性反向去噪曲线。\nplot_diffusion_1d(xs)",
            ),
        ]),
        "ch12_alphafold_concepts.ipynb": flatten([
            rs.chapter_link(
                "第 12 章 · AlphaFold 流程",
                ["运行流程输出"],
                "../ch12.html",
            ),
            rs.section("0", "环境与数据"),
            *rs.stepcode(b, "# 输出 AlphaFold 风格流程模块。\nalphafold_outline()"),
        ]),
    }
