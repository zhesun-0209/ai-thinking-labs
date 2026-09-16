#!/usr/bin/env python3
"""Export stored Notebook outputs without execution; opt in with --execute."""

from __future__ import annotations

import argparse
import base64
import re
import struct
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

import nbformat
from bs4 import BeautifulSoup
from nbconvert import HTMLExporter
from traitlets.config import Config

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = ROOT / "notebooks"
RENDERED_DIR = NOTEBOOKS_DIR / "rendered"
CSS_VERSION = "20260916"

# Retain nbconvert's cell and MIME renderers, not the JupyterLab application CSS.
READER_TEMPLATE = r"""
{% extends 'index.html.j2' %}
{% block html_head %}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ resources.reader_title | e }} · AI思维 Notebook</title>
<meta name="description" content="{{ resources.reader_title | e }}，AI思维配套代码实验。">
<link rel="icon" href="../../favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../notebooks.css?v={{ resources.css_version }}">
{% endblock html_head %}
"""

READER_SCRIPT = r"""
(() => {
  const status = document.getElementById("ai-labs-status");
  let statusTimer;
  const announce = (message) => {
    clearTimeout(statusTimer);
    status.textContent = message;
    statusTimer = setTimeout(() => { status.textContent = ""; }, 4000);
  };
  const iconButton = (symbol, label, className = "") => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "nb-icon-button " + className;
    button.textContent = symbol;
    button.title = label;
    button.setAttribute("aria-label", label);
    return button;
  };
  const fallbackCopy = (text) => {
    const active = document.activeElement;
    const buffer = document.createElement("textarea");
    buffer.className = "nb-copy-buffer";
    buffer.value = text;
    buffer.setAttribute("aria-label", "待复制代码");
    document.body.append(buffer);
    buffer.select();
    let copied = false;
    try { copied = document.execCommand("copy"); }
    finally {
      buffer.remove();
      active?.focus({ preventScroll: true });
    }
    return copied;
  };
  document.querySelectorAll(".jp-CodeCell .jp-InputArea-editor pre").forEach((pre, index) => {
    const tools = document.createElement("div");
    tools.className = "nb-code-tools";
    const label = "复制代码单元 " + (index + 1);
    const button = iconButton("⧉", label, "nb-copy");
    let resetTimer;
    button.addEventListener("click", async () => {
      let copied = false;
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(pre.textContent);
          copied = true;
        }
      } catch (_) { /* Clipboard permissions can be denied on a static host. */ }
      if (!copied) {
        try { copied = fallbackCopy(pre.textContent); } catch (_) { copied = false; }
      }
      clearTimeout(resetTimer);
      button.dataset.state = copied ? "copied" : "failed";
      button.textContent = copied ? "✓" : "⧉";
      button.title = copied ? "已复制" : "复制失败";
      button.setAttribute("aria-label", button.title);
      announce(copied ? "代码已复制" : "复制失败，请选中代码后复制。");
      resetTimer = setTimeout(() => {
        button.textContent = "⧉";
        button.title = label;
        button.setAttribute("aria-label", label);
        delete button.dataset.state;
      }, 2200);
    });
    tools.append(button);
    pre.closest(".jp-Cell-inputWrapper").prepend(tools);
  });

  const dialog = document.createElement("dialog");
  dialog.className = "nb-image-dialog";
  dialog.setAttribute("aria-labelledby", "nb-image-title");
  const header = document.createElement("header");
  const title = document.createElement("h2");
  title.id = "nb-image-title";
  title.textContent = "输出图";
  const closeButton = iconButton("×", "关闭原图");
  header.append(title, closeButton);
  const detail = document.createElement("div");
  detail.className = "nb-image-detail";
  detail.tabIndex = 0;
  detail.setAttribute("role", "region");
  detail.setAttribute("aria-label", "原始尺寸图像");
  const fullImage = document.createElement("img");
  detail.append(fullImage);
  dialog.append(header, detail);
  document.body.append(dialog);
  closeButton.addEventListener("click", () => dialog.close());
  let imageTrigger;
  dialog.addEventListener("close", () => {
    document.body.classList.remove("nb-dialog-open");
    fullImage.removeAttribute("src");
    imageTrigger?.focus({ preventScroll: true });
  });
  if (typeof dialog.showModal === "function") {
    document.querySelectorAll(".nb-figure img").forEach((img) => {
      const toolbar = document.createElement("div");
      toolbar.className = "nb-figure-tools";
      const button = iconButton("⤢", "查看原图：" + img.alt);
      button.setAttribute("aria-haspopup", "dialog");
      const open = () => {
        imageTrigger = button;
        title.textContent = img.alt;
        fullImage.alt = img.alt;
        fullImage.src = img.currentSrc || img.src;
        fullImage.width = img.naturalWidth || Number(img.getAttribute("width"));
        dialog.showModal();
        document.body.classList.add("nb-dialog-open");
        detail.scrollTo(0, 0);
      };
      button.addEventListener("click", open);
      img.addEventListener("click", open);
      img.dataset.zoomable = "true";
      toolbar.append(button);
      img.before(toolbar);
    });
  }

  const top = document.getElementById("ai-labs-top");
  let pending = false;
  const updateTop = () => { top.hidden = window.scrollY < 520; pending = false; };
  document.addEventListener("scroll", () => {
    if (!pending) { pending = true; requestAnimationFrame(updateTop); }
  }, { passive: true });
  top.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    document.getElementById("nb-content").focus({ preventScroll: true });
  });
  updateTop();
})();
"""

# Descriptions identify the plotted data, not unverified numerical conclusions.
IMAGE_DESCRIPTIONS = {
    "ch05_campus_search": [
        "罗马尼亚城市路线图，标出 Arad 起点、Bucharest 终点、道路距离和启发式距离",
        "DFS 搜索的节点展开顺序与最终路线",
        "BFS 搜索的节点展开顺序与最终路线",
        "UCS 搜索的累计代价与最终路线",
        "贪心搜索按启发式距离展开的节点与最终路线",
        "A* 搜索按 g+h 展开的节点与最终路线",
    ],
    "ch06_forward_backward_chain": ["动物分类专家系统的事实、触发规则与前向推理路径"],
    "ch06_graph_reasoning": ["人物知识图谱中 Marie Curie 到诺贝尔奖的多跳路径"],
    "ch07_decision_tree_kmeans": [
        "Wine 分类决策树的特征分裂与叶节点",
        "Wine 决策树的重要性前八项特征",
        "Iris 鸢尾花数据的聚类分组与聚类中心",
        "不同 k 值的簇内平方和与轮廓系数",
    ],
    "ch07_perceptron_gd": [
        "疾病指标回归的拟合直线与梯度下降 MSE 曲线",
        "鸢尾花二分类样本与感知机线性决策边界",
    ],
    "ch08_mlp_backprop": ["乳腺癌 MLP 的训练损失、混淆矩阵与样本预测置信度"],
    "ch08_transe_attention": [
        "国家与首都的 TransE 向量几何关系、正负例训练距离",
        "词语注意力权重矩阵与每个查询词的最高关注关系",
    ],
    "ch09_attention_lm": ["句子的因果注意力矩阵、可见上下文与最高关注词关系"],
    "ch09_bpe": ["BPE 合并的符号对频次、词元数量变化与合并过程"],
    "ch09_word2vec_analogy": ["Skip-gram 训练损失及词向量二维投影中的类比关系"],
    "ch10_clip_infonce": ["真实图片与候选文本提示的 CLIP 匹配概率矩阵"],
    "ch10_conv2d_numpy": ["花朵原图、Sobel 卷积窗口、边缘特征图与最大池化结果"],
    "ch10_mae_masking": ["原图、掩码可见输入、ViT-MAE 预测图块、重建结果与误差图"],
    "ch10_vit_patchify": ["建筑照片的图块网格、展平向量与选定局部图块"],
    "ch11_epsilon_greedy": [
        "悬崖行走环境中的起点、终点和危险区域",
        "探索率 0.10 训练后的完成路线",
        "不同探索率的训练回报与探索率 0.10 的策略图",
    ],
    "ch11_mdp_value_iteration": [
        "冰湖导航初始状态与选定动作后的下一格",
        "冰湖价值迭代的状态价值、策略箭头与 Bellman 误差收敛曲线",
    ],
    "ch11_td_learning": [
        "出租车任务的初始位置、乘客与目的地",
        "训练后出租车接送乘客的执行路线",
        "Q-learning 训练回报曲线与起始状态各动作的 Q 值",
    ],
    "ch12_alphafold_concepts": ["蛋白序列对齐、位置保守性、位置对表征与候选接触热力图"],
    "ch12_image_denoising": ["建筑原图、带噪输入、去噪输出与重建误差"],
    "ch12_image_denoising_diffusion": ["花朵图片前向加噪序列与预训练 DDPM 的反向采样轨迹"],
    "ch12_image_diffusion": ["花朵照片在不同时间步的前向加噪序列"],
    "ch12_image_patch_gan": ["GAN 训练损失、判别器输出、真实手写数字与生成数字的对比"],
    "ch12_iris_parameter_search": ["鸢尾花分类的参数搜索轨迹及 C、gamma 参数空间得分"],
    "ch12_mcts": [
        "冰湖 MCTS 的起点环境与规划目标",
        "MCTS 每步重新规划后的实际抽样路线，以及下一状态各动作的后续回报与访问次数",
        "起点动作的平均回报与仅用于探索的 UCT，以及剩余 16 步节点中最多访问动作的平均回报",
    ],
}


def list_notebooks(names: list[str] | None = None) -> list[Path]:
    if not names:
        return sorted(NOTEBOOKS_DIR.glob("ch*.ipynb"))
    paths = []
    for name in names:
        if not re.fullmatch(r"ch\d{2}_[a-z0-9_]+\.ipynb", name):
            raise ValueError(f"expected an ipynb filename under notebooks/: {name}")
        path = NOTEBOOKS_DIR / name
        if not path.is_file():
            raise ValueError(f"notebook not found: {name}")
        if path not in paths:
            paths.append(path)
    return paths


def execute_inplace(path: Path) -> None:
    cmd = [
        sys.executable, "-m", "jupyter", "nbconvert",
        "--Application.log_level=ERROR", "--to", "notebook", "--execute", "--inplace",
        "--ExecutePreprocessor.timeout=120", str(path.relative_to(ROOT)),
    ]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(ROOT), check=True)


def notebook_title(nb, path: Path) -> str:
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            for line in cell.source.splitlines():
                if line.startswith("# "):
                    return line[2:].strip()
    return path.stem


def validate_static_output(soup: BeautifulSoup, path: Path) -> None:
    # Never silently ship raw formulae or missing interactive dependencies.
    for block in soup.select(".jp-RenderedMarkdown, .jp-RenderedLatex, .jp-RenderedHTML"):
        fragment = BeautifulSoup(str(block), "html.parser")
        for code in fragment.select("pre, code"):
            code.decompose()
        if block.get("data-mime-type") == "text/latex" or fragment.select(".math") or re.search(r"\\[([]|\\begin\{|(?<!\\)\$[^$]+\$", fragment.get_text()):
            raise ValueError(f"{path.name}: math requires a local, licensed renderer before export")
    if soup.select("script, iframe, object, embed"):
        raise ValueError(f"{path.name}: interactive output needs an explicit local renderer")
    for node in soup.select("[src], link[href]"):
        value = node.get("src", node.get("href", ""))
        if urlsplit(value).scheme in ("http", "https") or value.startswith("//"):
            raise ValueError(f"{path.name}: external rendering dependency: {value}")
    for style in soup.select("style"):
        if re.search(r"@import|url\s*\(", style.get_text(), re.IGNORECASE):
            raise ValueError(f"{path.name}: output CSS contains a rendering dependency")


def decorate_html(text: str, notebook_path: Path) -> str:
    soup = BeautifulSoup(text, "html.parser")
    validate_static_output(soup, notebook_path)
    soup.html["lang"] = "zh-CN"
    main = soup.main
    main["id"] = "nb-content"
    main["tabindex"] = "-1"
    ch = int(re.match(r"ch(\d+)_", notebook_path.stem).group(1))
    chrome = soup.new_tag("nav", id="ai-labs-chrome")
    chrome["aria-label"] = "Notebook 导航"
    for href, label in [
        (f"../chapter.html?ch={ch}", "实验列表"),
        (f"../../ch{ch}.html", "章节正文"),
        (f"../{notebook_path.name}", "下载 .ipynb"),
    ]:
        link = soup.new_tag("a", href=href)
        link.string = label
        if href.endswith(".ipynb"):
            link["download"] = ""
        chrome.append(link)
    skip = soup.new_tag("a", href="#nb-content", attrs={"class": "nb-skip"})
    skip.string = "跳到正文"
    main.insert_before(skip)
    main.insert_before(chrome)

    # Drop only the duplicate chapter link, not the introductory learning content.
    chapter_href = f"../../ch{ch}.html"
    for link in main.select("a[href]"):
        if link["href"] == f"../ch{ch}.html":
            link["href"] = chapter_href
        parent = link.parent
        if link["href"] == chapter_href and parent.name == "p" and parent.get_text(strip=True) == link.get_text(strip=True):
            parent.decompose()
    for heading in main.select("h1[id], h2[id], h3[id], h4[id]"):
        heading["id"] = unquote(heading["id"])
        anchor = heading.select_one(".anchor-link")
        if anchor:
            anchor["href"] = "#" + quote(heading["id"], safe="-_")
            anchor["aria-label"] = "链接到本节"
            anchor["title"] = "链接到本节"
    for wrapper in main.select(".jp-Cell-inputWrapper"):
        wrapper.attrs.pop("tabindex", None)
    for index, editor in enumerate(main.select(".jp-InputArea-editor"), 1):
        editor["tabindex"] = "0"
        editor["role"] = "region"
        editor["aria-label"] = f"代码单元 {index}"
    for table in main.select("table"):
        wrapper = soup.new_tag("div", attrs={"class": "nb-table-scroll", "tabindex": "0", "role": "region", "aria-label": "数据表格"})
        table.wrap(wrapper)
    for index, output in enumerate(main.select(".jp-RenderedText"), 1):
        output["tabindex"] = "0"
        output["role"] = "region"
        output["aria-label"] = f"文本输出 {index}"
    images = main.select(".jp-OutputArea-output img")
    descriptions = IMAGE_DESCRIPTIONS.get(notebook_path.stem, [])
    for index, img in enumerate(images):
        if len(descriptions) == len(images):
            description = descriptions[index]
        else:
            heading = img.find_previous(["h2", "h3"])
            description = f"{heading.get_text(' ', strip=True) if heading else notebook_path.stem}，输出图 {index + 1}"
        img["alt"] = description
        img["loading"] = "lazy"
        img["decoding"] = "async"
        if img.get("src", "").startswith("data:image/png;base64,"):
            data = base64.b64decode(img["src"].split(",", 1)[1])
            if data[:8] == b"\x89PNG\r\n\x1a\n":
                width, height = struct.unpack(">II", data[16:24])
                img["width"], img["height"] = str(width), str(height)
        img.wrap(soup.new_tag("figure", attrs={"class": "nb-figure"}))

    top = soup.new_tag("button", id="ai-labs-top", attrs={"class": "nb-icon-button", "type": "button", "hidden": "", "aria-label": "回到顶部", "title": "回到顶部"})
    top.string = "↑"
    soup.body.append(top)
    status = soup.new_tag("div", id="ai-labs-status", attrs={"role": "status", "aria-live": "polite", "aria-atomic": "true"})
    soup.body.append(status)
    script = soup.new_tag("script", id="ai-labs-reader-script")
    script.string = READER_SCRIPT
    soup.body.append(script)
    return str(soup)


def make_exporter() -> HTMLExporter:
    config = Config()
    config.ExecutePreprocessor.enabled = False
    config.TagRemovePreprocessor.enabled = True
    config.TagRemovePreprocessor.remove_cell_tags = {"ai-labs-bootstrap"}
    return HTMLExporter(template_name="lab", raw_template=READER_TEMPLATE, embed_images=True, config=config)


def export_html(path: Path, exporter: HTMLExporter) -> str:
    nb = nbformat.read(path, as_version=4)
    for cell in nb.cells:
        # Markdown can consume single-backslash LaTeX delimiters before HTML validation.
        if cell.cell_type == "markdown" and re.search(r"\\[([]|\\begin\{", cell.source):
            raise ValueError(f"{path.name}: LaTeX source requires a local, licensed renderer before export")
    resources = {
        "metadata": {"path": str(path.parent), "name": path.stem},
        "language_code": "zh-CN",
        "reader_title": notebook_title(nb, path),
        "css_version": CSS_VERSION,
    }
    text, _ = exporter.from_notebook_node(nb, resources=resources)
    return decorate_html(text, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="*", help="ipynb filenames under notebooks/; default: all")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true", help="explicitly execute and modify source ipynb files")
    mode.add_argument("--export-only", "--skip-execute", dest="execute", action="store_false", help="export stored outputs only (default)")
    parser.set_defaults(execute=False)
    args = parser.parse_args()
    try:
        paths = list_notebooks(args.notebooks or None)
    except ValueError as exc:
        parser.error(str(exc))
    if not paths:
        parser.error("no notebooks found")
    print(f"{len(paths)} notebooks; mode: {'EXECUTE IN PLACE' if args.execute else 'export stored outputs only'}", flush=True)
    exporter = make_exporter()
    rendered = []
    for path in paths:
        if args.execute:
            execute_inplace(path)
        rendered.append((path, export_html(path, exporter)))
        print(f"prepared {path.name}", flush=True)
    # Validate every page before replacing any previously published result.
    RENDERED_DIR.mkdir(parents=True, exist_ok=True)
    for path, text in rendered:
        out = RENDERED_DIR / f"{path.stem}.html"
        out.write_text(text, encoding="utf-8")
        print(f"ok {out.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
