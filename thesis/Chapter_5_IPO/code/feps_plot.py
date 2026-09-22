"""
Analytical f(eps) plot for the closed-form k=2 example.

  f(eps) = 2/3 + eps/2       for 0 <= eps <= 1/6
           1 - (3/2)*eps     for 1/6 < eps <= 1/3
           1/2               for eps > 1/3
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os


def f_eps(eps):
    eps = np.asarray(eps, float)
    out = np.empty_like(eps)
    m1 = eps <= 1/6
    m2 = (eps > 1/6) & (eps <= 1/3)
    m3 = eps > 1/3
    out[m1] = 2/3 + eps[m1] / 2
    out[m2] = 1 - 1.5 * eps[m2]
    out[m3] = 0.5
    return out


def main():
    eps = np.linspace(0, 0.55, 500)
    fw  = f_eps(eps)

    fig, ax = plt.subplots(figsize=(5.2, 3.4))

    ax.axvspan(0,    1/6,  alpha=0.08, color="#2ca02c")
    ax.axvspan(1/6,  1/3,  alpha=0.08, color="#d62728")
    ax.axvspan(1/3,  0.55, alpha=0.08, color="#7f7f7f")

    ax.plot(eps, fw, color="#1f77b4", lw=2.5, zorder=3)

    pts = {
        r"$(0,\; 0.67)$":         (0,   2/3),
        r"$(1/6,\; 0.75)$": (1/6, 3/4),
        r"$(1/3,\; 0.50)$": (1/3, 1/2),
    }
    for label, (ex, fy) in pts.items():
        ax.plot(ex, fy, "o", color="#1f77b4", ms=6, zorder=4)
        offset = (0.01, 0.012)
        if ex == 1/6:
            offset = (-0.005, 0.013)
        ax.annotate(label, xy=(ex, fy),
                    xytext=(ex + offset[0], fy + offset[1]),
                    fontsize=8.5, ha="left")

    ax.axvline(1/6, color="#2ca02c", lw=1.0, ls="--", alpha=0.7)
    ax.axvline(1/3, color="#d62728", lw=1.0, ls="--", alpha=0.7)

    # Slope f' = +1/2 annotation
    ax.annotate("", xy=(0.12, f_eps(0.12)),
                xytext=(0.02, f_eps(0.02)),
                arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=1.5))
    ax.text(0.055, 0.693, r"$f'=+\frac{1}{2}$", fontsize=8,
            color="#2ca02c", ha="center")

    # Slope f' = -3/2 annotation
    ax.annotate("", xy=(0.28, f_eps(0.28)),
                xytext=(0.19, f_eps(0.19)),
                arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5))
    ax.text(0.245, 0.640, r"$f'=-\frac{3}{2}$", fontsize=8,
            color="#d62728", ha="center")

    # Slope f' = 0 annotation
    ax.text(0.43, 0.515, r"$f'=0$", fontsize=8, color="#555555", ha="center")

    p1 = mpatches.Patch(color="#2ca02c", alpha=0.3, label="Regime I: eps in [0, 1/6]")
    p2 = mpatches.Patch(color="#d62728", alpha=0.3, label="Regime II: eps in (1/6, 1/3]")
    p3 = mpatches.Patch(color="#7f7f7f", alpha=0.3, label="Regime III: eps > 1/3")
    ax.legend(handles=[p1, p2, p3], fontsize=7.5, loc="lower left", framealpha=0.85)

    # Optimal eps* = 1/6
    ax.plot(1/6, 3/4, "*", ms=13, color="gold", markeredgecolor="#555",
            markeredgewidth=0.6, zorder=5, label=r"$\varepsilon^*=1/6$")

    ax.set_xlabel(r"Enforcement Budget $\varepsilon$", fontsize=10)
    ax.set_ylabel(r"Expected Social Welfare $f(\varepsilon)$", fontsize=10)
    ax.set_title(
        r"Analytical $f(\varepsilon)$: closed-form $k=2$ example"
        "\n"
        r"($\varepsilon^* = 1/6$, peak welfare $= 3/4$)",
        fontsize=10)
    ax.set_xlim(0, 0.55)
    ax.set_ylim(0.45, 0.82)
    ax.set_xticks([0, 1/6, 1/3, 0.5])
    ax.set_xticklabels([r"$0$", r"$1/6$", r"$1/3$", r"$0.5$"], fontsize=9)
    ax.grid(True, ls="--", alpha=0.4)

    plt.tight_layout()

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "feps_analytical.pdf")
    plt.savefig(out, format="pdf", bbox_inches="tight")
    print(f"Saved -> {out}")


if __name__ == "__main__":
    main()
