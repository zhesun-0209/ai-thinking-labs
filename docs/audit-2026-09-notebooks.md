# Notebook 阅读与章节实验列表审计

日期：2026-09-16

状态：阅读外壳修复及 24 本仅导出完成。以下保全数据记录该阶段的结果；最终集成时另行修复并执行了 MCTS 一册，其余 23 本 `.ipynb` 与原 HEAD 字节一致。MCTS 的代码、输出及回归证据见 [课程报告](audit-2026-09-content.md#集成审计聚焦修复mcts-notebook)。本报告的“未执行”和“24 本不变”均限于阅读外壳子任务，不代表后续集成没有执行 MCTS。

## 范围与结论

本任务仅修改 notebooks/notebooks.css、notebooks/chapter.html、notebooks/view.html、notebooks/index.html、js/notebooks-catalog.js、scripts/render_notebooks.py、24 个 notebooks/rendered/*.html 及本报告。没有修改 .ipynb、教学算法或主站全局文件。工作树中的其他改动由并行任务产生，本任务未处理。

阅读页继续使用 nbconvert 的 cell、Markdown 和 MIME 输出结构；只替换阅读外壳、共享样式及交互。白底、墨黑正文、#176b62 主色、中文系统 sans 字体、字间距 0、圆角不超过 6px；无大标题、渐变或嵌套卡片。原输出图中的颜色完全保留。

章节列表最终为“标题 + 简介 + 独立知识点行 + 阅读/下载动作”。知识点来自原有 result 字段，按顿号/逗号拆分，以“ · ”连接；不显示 scope、tier、核心/拓展标签或估算分钟。

## 证据与修复

| 优先级 | 原实现证据 | 修复 |
| --- | --- | --- |
| P1 | 无效 ch 参数 trim 后直接拼入 innerHTML，可注入标签 | 不回显原始参数；章节及范围按已存在章节校验，数据文案 HTML 转义 |
| P1 | view.html 同时 meta refresh 到目录及按任意 nb 字符串重定向 | 移除竞争重定向，按 24 个已知文件白名单解析；无效值保留错误页与返回入口 |
| P1 | 41 张输出图使用相同泛化 alt，缺少尺寸与原图入口 | 按绘图代码补具体 alt，41 张均有 width/height、lazy、async；原图 dialog 保留原分辨率 |
| P1 | 原命令默认执行并原地写回 .ipynb | 默认仅导出；--export-only / --skip-execute 明确禁止执行；重算必须显式 --execute |
| P2 | 每页内联约 26 万字符的 nbconvert/JupyterLab 样式及阅读 CSS | 保留官方 cell 渲染，替换为共享 notebooks.css；不再附带 JupyterLab 应用样式 |
| P2 | 章节标题在页头、概览、章节块重复，含预渲染说明及大块留白 | 单章保留一个页标题；多章使用章节小标题；删除工程说明、固定大卡片高度 |
| P2 | 阅读页正文重复“章节网页”链接，顶部导航冗余，无代码复制 | 顶部保留实验列表、章节正文、下载；删除仅含同一章节链接的段落；保留教学导言 |
| P2 | 移动端代码被限制高度、强制表格最小 640px、反复显示滚动说明 | 代码不缩字、不强制折行或截断高度；代码/表格有局部滚动与键盘焦点；删除滚动说明 |

代码复制使用 Clipboard API，并有本地/权限受限时的回退；成功/失败反馈使用 live status。原图 dialog 支持关闭、Escape 与焦点返回；禁用 JS 时不产生无效复制按钮，Markdown、代码、图表仍可阅读。

## 外部依赖与 LaTeX

- 修复前已有 24 个导出页不请求外网字体、RequireJS、MathJax 或 Mermaid。不能将本次改动描述为“修复了实际存在的 CDN 加载故障”。
- 全部 Notebook 的 Markdown 公式标记计数为 0，输出中的 text/latex MIME 为 0；最终 Markdown/HTML 正文中的原始美元符号数量也为 0。
- 因此当前没有需要排版的 LaTeX，不能声称“已验证公式渲染”。本次没有加入数学 vendor，也没有仅删 MathJax 后留下公式源码。
- 新模板直接省去不需要的外部脚本。未来若加入 $...$、$$...$$、\\(...\\)、\\[...\\]、LaTeX 环境或 text/latex 输出，导出会明确报错，要求先接入带来源/许可记录的本地数学渲染器；不会默默发布裸公式。
- 上述五种 Markdown 公式格式的阻断用例已通过；代码及行内代码中的美元符号不误判。原始 Markdown 的反斜杠 LaTeX 检查采取保守拒绝策略，包括含此类分隔符的示例，后续新增此类内容时需要审视此边界。
- 新模板拒绝需要脚本的交互输出、远端 src/link 资源及输出 CSS 中的依赖引用。当前最终 24 页外部渲染依赖为 0，每页只有一个内联阅读增强脚本。

## 输出保全

以本任务开始时的 Git HEAD 为基准，最终重新比较全部 24 页：

| 项目 | 修复前 | 修复后 | 验证方式 |
| --- | ---: | ---: | --- |
| .ipynb | 24 | 24 | 每个文件与 HEAD 逐字节一致，SHA-256 不变 |
| 可见代码 cell | 96 | 96 | 数量及高亮 pre 的纯代码文本逐项一致 |
| Markdown cell | 78 | 78 | 数量、cell 结构保留，仅移除重复导航段落 |
| 输出 PNG | 41 | 41 | Base64 解码后每张图片的 SHA-256 一致 |
| 数据表格 | 109 | 109 | 数量及每张表格的文本内容逐项一致 |
| 文本输出块 | 12 | 12 | 数量及文本逐项一致 |
| 已隐藏 bootstrap cell | 30 | 30 | 保留原 ai-labs-bootstrap 过滤逻辑，这 30 个 cell 的存储输出总数为 0 |

bootstrap 中包括 import、显示/字体设置等，后续可见代码可能依赖它们；只复制网页单个 cell 不保证可以独立执行。按主 agent 确认的既有边界，继续隐藏这些初始化 cell，不新增页面说明，不改变下载版。下载的 24 本保留全部 cell 和既有执行结果。

24 个文件按文件名排序形成“文件名:SHA-256 + 换行”的清单，其整体 SHA-256 为：

```text
7573f72d42a305ea912310b7724ea115dcd2a53f634aca5cbdaf86f876a7497e
```

## 体积与图像尺寸

- 24 个 HTML 合计：15,070,293 -> 8,719,469 字节，减少 6,350,824 字节，下降 42.14%。
- 新共享 notebooks.css：10,887 字节；以上 HTML 总数未计共享 CSS。共享文件可跨页缓存，具体缓存头由部署配置决定。
- 单页 HTML：最小 115,251 字节，中位数 201,776.5 字节，最大 1,295,984 字节。
- 41 张原始 PNG：宽度范围 516-1770px，高度范围 402-875px；这是各维度范围，不代表同一张图。未裁切、重编码或缩减像素。
- 正文图像按容器等比缩放，dialog 按原始宽度展示并允许横纵滚动。lazy/async 仅减少不必要的解码与绘制工作；因为图像仍内嵌 Base64，不会减少初次 HTML 图像字节。
- 仍有两张扩散实验页超过 1.2MB，主要来自原有图像。为保全输出，本次没有压缩或拆分这些图片；未测量 LCP/INP/CLS，不将字节减少等同于实测加载提速。

| 文件 | 原 HTML KiB | 新 HTML KiB | 图片 | 表格 |
| --- | ---: | ---: | ---: | ---: |
| ch05_campus_search.html | 1254.9 | 997.9 | 6 | 8 |
| ch06_forward_backward_chain.html | 377.5 | 119.1 | 1 | 4 |
| ch06_graph_reasoning.html | 394.7 | 136.3 | 1 | 4 |
| ch07_decision_tree_kmeans.html | 872.4 | 614.9 | 4 | 12 |
| ch07_perceptron_gd.html | 507.0 | 248.8 | 2 | 6 |
| ch08_mlp_backprop.html | 374.4 | 116.0 | 1 | 6 |
| ch08_transe_attention.html | 500.8 | 242.4 | 2 | 5 |
| ch09_attention_lm.html | 417.6 | 158.9 | 1 | 3 |
| ch09_bpe.html | 417.5 | 158.8 | 1 | 2 |
| ch09_word2vec_analogy.html | 371.0 | 112.5 | 1 | 5 |
| ch10_clip_infonce.html | 442.6 | 183.7 | 1 | 1 |
| ch10_conv2d_numpy.html | 423.1 | 164.5 | 1 | 4 |
| ch10_mae_masking.html | 1030.4 | 771.7 | 1 | 3 |
| ch10_vit_patchify.html | 580.9 | 322.0 | 1 | 1 |
| ch11_epsilon_greedy.html | 462.8 | 204.5 | 3 | 6 |
| ch11_mdp_value_iteration.html | 424.8 | 166.7 | 2 | 7 |
| ch11_td_learning.html | 447.8 | 189.6 | 3 | 5 |
| ch12_alphafold_concepts.html | 394.3 | 135.7 | 1 | 5 |
| ch12_image_denoising.html | 519.7 | 260.9 | 1 | 2 |
| ch12_image_denoising_diffusion.html | 1524.1 | 1265.6 | 1 | 5 |
| ch12_image_diffusion.html | 1483.6 | 1224.6 | 1 | 1 |
| ch12_image_patch_gan.html | 597.0 | 338.2 | 1 | 2 |
| ch12_iris_parameter_search.html | 429.8 | 171.1 | 1 | 4 |
| ch12_mcts.html | 468.5 | 210.5 | 3 | 8 |

## 导出与验证

仓库根目录运行：

```bash
python3 -B scripts/render_notebooks.py --export-only
```

当前默认无参数执行也仅导出；旧 --skip-execute 参数兼容。仅导出路径显式关闭 ExecutePreprocessor，复用已有结果。先生成并验证全部页面，再写入结果，缺失/越界文件名及不支持的数学/交互依赖会在发布前报错。源 Notebook 中的 bootstrap 安装代码不会运行。

原 SOP 中无 --execute 的命令现在只导出，不重算；确需重算时必须显式追加 --execute。本任务按权限未修改该 SOP。

已完成：

- 全量 24 本仅导出，无内核/模型执行。
- 24 本源文件、96 个代码块、41 张图像、109 张表格、12 个文本块保全比较。
- 全部渲染页本地链接/片段锚点解析、唯一 h1/导航、图片 alt/尺寸/加载属性检查。
- 24 个目录目标、单章、完整范围、倒序范围、非法范围、HTML 注入参数和旧阅读入口文件白名单测试。
- 24 条目录知识点及“无分类/无时间”断言。
- 默认、--export-only、--skip-execute 三种路径的禁止执行测试。
- 数学守卫、错误文件名与目录穿越拒绝测试。
- Node 检查目录脚本、24 页内联阅读脚本及入口内联脚本语法。
- tinycss2 样式解析；无外部字体、渐变、非零字间距；限定文件 git diff --check 通过。

浏览器边界：

- 本任务没有打开或操作用户浏览器。
- 主 agent 已反馈验收通过：MCTS 手机页、原图 dialog 打开、Escape 关闭后焦点返回、复制代码成功。
- 目录知识点修改发生在该次反馈后，已完成静态断言；目录最终视觉、其余 Notebook 的移动/桌面抽检、剪贴板拒绝回退、打印及浏览器性能指标由主 agent 统一验收，未在此冒称完成。

## Singer 构建交接

没有新增 notebooks/assets/ 文件或第三方 vendor。无需新增前端资产路径。

需保留已有路径：

- notebooks/notebooks.css：现在也是所有 rendered HTML 的样式依赖，引用为 ../notebooks.css?v=20260916。
- js/notebooks-catalog.js：chapter.html 与旧版 view.html 均引用，版本参数为 v=20260916。
- notebooks/rendered/*.html：24 个输出。
- notebooks/*.ipynb：24 个原下载文件，不变。
- notebooks/chapter.html、notebooks/view.html、notebooks/index.html 和原 favicon.svg、章节正文/目录链接目标。

新增报告路径为 docs/audit-2026-09-notebooks.md，不是运行时资源。全局构建 allowlist 由 Singer 维护，本任务没有修改构建脚本。
