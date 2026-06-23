"""Chapter 12 creation demos — pedagogical API."""

from __future__ import annotations

import math
import random

import matplotlib.pyplot as plt
import numpy as np


def annealing_demo() -> None:
    losses = [12.4, 8.1, 3.2, 2.3]
    reprs = ["代数", "代数+退火", "几何", "几何"]
    print("| 步骤 | 表征 | loss |")
    for i, (r, l) in enumerate(zip(reprs, losses)):
        print(f"| {i} | {r} | {l} |")


def plot_annealing() -> None:
    losses = [12.4, 8.1, 3.2, 2.3]
    fig, ax = plt.subplots()
    ax.plot(range(len(losses)), losses, marker="o", color="#0d6b62", linewidth=2)
    ax.set_xlabel("search step")
    ax.set_ylabel("loss")
    ax.set_title("Annealing search")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def mcts_uct(q: float, n: int, N: int, c: float = 1.4) -> float:
    if n == 0:
        return float("inf")
    return q / n + c * math.sqrt(math.log(N + 1) / n)


def mcts_demo() -> None:
    stats = {"a": (2, 5), "b": (3, 4)}
    N = sum(n for _, n in stats.values())
    print("UCT = Q/N + c·√(ln N / n):")
    for k, (q, n) in stats.items():
        print(f"  走法 {k}: Q={q}, n={n} → UCT={mcts_uct(q, n, N):.3f}")


def plot_uct() -> None:
    stats = {"a": (2, 5), "b": (3, 4), "c": (0, 0)}
    N = sum(n for _, n in stats.values())
    keys = list(stats.keys())
    scores = [mcts_uct(q, n, N) for q, n in stats.values()]
    fig, ax = plt.subplots()
    ax.bar(keys, scores, color="#0d6b62")
    ax.set_title("MCTS UCT scores")
    plt.tight_layout()
    plt.show()


def diffusion_1d() -> list[float]:
    xs = diffusion_1d_values()
    print("前向加噪 x:", [round(v, 3) for v in xs])
    return xs


def diffusion_1d_values(steps: int = 5, seed: int = 0, sigma: float = 0.3) -> list[float]:
    random.seed(0)
    if seed != 0:
        random.seed(seed)
    x0 = 1.0
    xs = [x0]
    x = x0
    for _ in range(steps):
        x += random.gauss(0, sigma)
        xs.append(x)
    return xs


def diffusion_1d_table(steps: int = 5, seed: int = 0, sigma: float = 0.3) -> None:
    import pandas as pd
    from IPython.display import display

    xs = diffusion_1d_values(steps=steps, seed=seed, sigma=sigma)
    display(pd.DataFrame({"t": list(range(len(xs))), "x_t": [round(v, 3) for v in xs]}))


def codelens_diffusion_1d(steps: int = 5) -> list:
    from common.codelens import Frame

    random.seed(0)
    x = 1.0
    frames = [Frame(0, "x = x0", "初始", {"x": round(x, 3)})]
    for i in range(1, steps + 1):
        x += random.gauss(0, 0.3)
        frames.append(Frame(i, "x += noise", f"第 {i} 步加噪", {"x": round(x, 3)}))
    return frames


def animate_diffusion_1d() -> None:
    from common.viz_anim import animate_bar_values

    frames = codelens_diffusion_1d()
    snaps = [{"step": f.step, "values": {"x": f.state["x"]}, "action": f.narrative} for f in frames]
    animate_bar_values(snaps, title="1D diffusion x", ylabel="x", fps=0.8)


def plot_diffusion_1d(xs: list[float] | None = None) -> None:
    if xs is None:
        random.seed(0)
        xs = [1.0]
        x = 1.0
        for _ in range(5):
            x += random.gauss(0, 0.3)
            xs.append(x)
    fig, ax = plt.subplots()
    ax.plot(range(len(xs)), xs, marker="o", color="#3498db", label="forward noise")
    ax.plot(range(len(xs)-1, -1, -1), xs[::-1], marker="x", color="#0d6b62", label="reverse denoise")
    ax.set_title("1D diffusion toy")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def _digits_sample(digit: int = 3) -> tuple[np.ndarray, np.ndarray, int]:
    from sklearn.datasets import load_digits

    digits = load_digits()
    images = digits.images.astype(float) / 16.0
    labels = digits.target
    idx = int(np.where(labels == digit)[0][3])
    prototype = images[labels == digit].mean(axis=0)
    return images[idx], prototype, int(labels[idx])


def _diffusion_schedule(steps: int = 6) -> tuple[np.ndarray, np.ndarray]:
    betas = np.linspace(0.06, 0.24, steps)
    alpha_bar = np.cumprod(1.0 - betas)
    return betas, alpha_bar


def digits_diffusion_table(steps: int = 6) -> None:
    import pandas as pd
    from IPython.display import display

    betas, alpha_bar = _diffusion_schedule(steps)
    rows = []
    for t, (beta, abar) in enumerate(zip(betas, alpha_bar), start=1):
        rows.append(
            {
                "t": t,
                "beta_t": round(float(beta), 3),
                "signal_scale sqrt(alpha_bar)": round(float(np.sqrt(abar)), 3),
                "noise_scale sqrt(1-alpha_bar)": round(float(np.sqrt(1 - abar)), 3),
            }
        )
    display(pd.DataFrame(rows))


def make_digits_diffusion(seed: int = 7, digit: int = 3, steps: int = 6) -> dict:
    rng = np.random.default_rng(seed)
    image, prototype, label = _digits_sample(digit)
    betas, alpha_bar = _diffusion_schedule(steps)
    noise = rng.normal(0, 1, size=image.shape)

    forward = [image]
    for abar in alpha_bar:
        xt = np.sqrt(abar) * image + np.sqrt(1 - abar) * noise
        forward.append(np.clip(xt, 0, 1))

    reverse = [forward[-1]]
    x = forward[-1]
    # A tiny teaching denoiser: use the class prototype as a stand-in for a learned score model.
    for t in range(steps, 0, -1):
        blend = 0.18 + 0.09 * (steps - t)
        x = (1 - blend) * x + blend * prototype
        x = np.clip(x, 0, 1)
        reverse.append(x)

    return {
        "label": label,
        "image": image,
        "prototype": prototype,
        "forward": forward,
        "reverse": reverse,
        "betas": betas,
        "alpha_bar": alpha_bar,
    }


def plot_digits_forward(seed: int = 7, digit: int = 3) -> None:
    data = make_digits_diffusion(seed=seed, digit=digit)
    frames = data["forward"]
    fig, axes = plt.subplots(1, len(frames), figsize=(1.55 * len(frames), 1.8))
    for i, (ax, img) in enumerate(zip(axes, frames)):
        ax.imshow(img, cmap="gray", vmin=0, vmax=1)
        ax.set_title("x0" if i == 0 else f"x{i}")
        ax.axis("off")
    fig.suptitle(f"Forward diffusion on sklearn digits: label {data['label']}", y=1.05)
    plt.tight_layout()
    plt.show()


def plot_digits_reverse(seed: int = 7, digit: int = 3) -> None:
    data = make_digits_diffusion(seed=seed, digit=digit)
    frames = data["reverse"]
    fig, axes = plt.subplots(1, len(frames), figsize=(1.55 * len(frames), 1.8))
    for i, (ax, img) in enumerate(zip(axes, frames)):
        ax.imshow(img, cmap="gray", vmin=0, vmax=1)
        ax.set_title("noise" if i == 0 else f"rev {i}")
        ax.axis("off")
    fig.suptitle("Reverse denoising path with a class-prototype denoiser", y=1.05)
    plt.tight_layout()
    plt.show()


def plot_digits_denoiser_comparison(seed: int = 7, digit: int = 3) -> None:
    data = make_digits_diffusion(seed=seed, digit=digit)
    images = [data["image"], data["forward"][-1], data["prototype"], data["reverse"][-1]]
    titles = ["clean x0", "noisy xT", "class prototype", "denoised"]
    fig, axes = plt.subplots(1, 4, figsize=(7.2, 2.1))
    for ax, img, title in zip(axes, images, titles):
        ax.imshow(img, cmap="gray", vmin=0, vmax=1)
        ax.set_title(title)
        ax.axis("off")
    plt.tight_layout()
    plt.show()


def digits_diffusion_summary(seed: int = 7, digit: int = 3) -> None:
    data = make_digits_diffusion(seed=seed, digit=digit)
    clean = data["image"]
    noisy = data["forward"][-1]
    denoised = data["reverse"][-1]
    print(f"digit label: {data['label']}")
    print(f"MSE(noisy, clean)   = {np.mean((noisy - clean) ** 2):.4f}")
    print(f"MSE(denoised, clean)= {np.mean((denoised - clean) ** 2):.4f}")
    print("这个 notebook 用类原型代替真实神经网络，目的是展示经典图像 diffusion 的过程缩影。")


def gan_toy() -> None:
    d_fake = [0.18, 0.08, 0.74, 0.50]
    print("D(生成样本) 概率:", " → ".join(f"{v:.2f}" for v in d_fake))


def plot_gan_d() -> None:
    d_fake = [0.18, 0.08, 0.74, 0.50]
    fig, ax = plt.subplots()
    ax.plot(range(len(d_fake)), d_fake, marker="o", color="#e74c3c", linewidth=2)
    ax.axhline(0.5, color="gray", linestyle="--", label="ideal D=0.5")
    ax.set_title("GAN discriminator D(x)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def alphafold_outline() -> None:
    steps = ["输入氨基酸序列", "MSA 共变", "Evoformer", "3D 坐标 + pLDDT"]
    for i, s in enumerate(steps):
        print(f"{i+1}. {s}")
