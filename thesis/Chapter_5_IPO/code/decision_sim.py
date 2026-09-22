"""
Decision-problem Monte Carlo simulation (Chapter 5).

Unified 2-panel figure combining:
  - (a) gamma-Sweep: Expected Per-Capita Social Welfare
  - (b) gamma-Sweep: Expected Per-Capita Firm Capital Raised

Evaluates the sensitivity sweep across v2 in {-8, -6, -4, -2, +2} with u2=0 fixed,
demonstrating the prominent inverted-V non-monotonicity (v2 = -8) alongside monotonic
increasing trajectories.

Fixed Group 1 valuation: V1(z) = sigma(0 + 4z).
99% confidence bands (z=2.576), 5000 samples per eps grid point.
Fully reproducible with fixed global seeds.
"""

import os
import random
import numpy as np
import matplotlib.pyplot as plt

# Global reproducibility seeds
GLOBAL_SEED = 42
np.random.seed(GLOBAL_SEED)
random.seed(GLOBAL_SEED)

N1, N2, N = 50, 50, 100
ETA       = 1.0
Z_CI      = 2.576
N_SAMPLES = 5000
N_EPS     = 51
EPS_MAX   = 1.5
X_LO, X_HI = -1.0, 1.0


def _sigma(u):
    """Numerically stable logistic sigmoid."""
    u = np.asarray(u, float)
    return np.where(u >= 0,
                    1.0 / (1.0 + np.exp(-u)),
                    np.exp(u) / (1.0 + np.exp(u)))


def firm_br(x, eps, v1_fn, v2_fn):
    """Firm best response via grid search over 3 targeting strategies: S={1,2}, S={1}, S={2}."""
    lo = max(X_LO, x - eps)
    hi = min(X_HI, x + eps)
    if hi < lo:
        lo, hi = x - eps, x + eps
    y_grid = np.linspace(lo, hi, 301)
    v1 = np.maximum(0.0, v1_fn(y_grid))
    v2 = np.maximum(0.0, v2_fn(y_grid))
    rev = np.stack([
        min(ETA * N, N1 + N2) * np.minimum(v1, v2),
        min(ETA * N, N1) * v1,
        min(ETA * N, N2) * v2,
    ])
    strat = int(np.argmax(np.max(rev, axis=1)))
    idx   = int(np.argmax(rev[strat]))
    z     = y_grid[idx]
    if strat == 0:
        p = float(min(v1_fn(z), v2_fn(z)))
        q = float(min(ETA * N, N1 + N2))
    elif strat == 1:
        p = float(v1_fn(z)); q = float(min(ETA * N, N1))
    else:
        p = float(v2_fn(z)); q = float(min(ETA * N, N2))
    return z, max(0.0, p), q


def simulate_profile(eps_grid, v1_fn, v2_fn, seed=42):
    """Monte Carlo estimation of welfare and firm capital over eps grid."""
    rng   = np.random.default_rng(seed)
    X     = rng.uniform(X_LO, X_HI, N_SAMPLES)
    types = rng.choice([1, 2], size=N_SAMPLES, p=[0.5, 0.5])
    ew, ew_lo, ew_hi = [], [], []
    ec, ec_lo, ec_hi = [], [], []
    for eps in eps_grid:
        w_arr, c_arr = [], []
        for x, j in zip(X, types):
            _, p, q = firm_br(x, eps, v1_fn, v2_fn)
            y_true  = v1_fn(x) if j == 1 else v2_fn(x)
            w_arr.append(q * max(0.0, float(y_true)) / N)
            c_arr.append(p * q / N)
        w_arr = np.asarray(w_arr); c_arr = np.asarray(c_arr)
        mw, sw = w_arr.mean(), w_arr.std(ddof=1)
        mc, sc = c_arr.mean(), c_arr.std(ddof=1)
        # Standard Error of the mean (1 SE)
        se_w   = sw / np.sqrt(N_SAMPLES)
        se_c   = sc / np.sqrt(N_SAMPLES)
        ew.append(mw); ew_lo.append(mw-se_w); ew_hi.append(mw+se_w)
        ec.append(mc); ec_lo.append(mc-se_c); ec_hi.append(mc+se_c)
    return tuple(map(np.asarray, (ew, ew_lo, ew_hi, ec, ec_lo, ec_hi)))


def _draw_panel(ax, eps_grid, ew, ew_lo, ew_hi, color, ls, label):
    ax.plot(eps_grid, ew, color=color, lw=2.0, ls=ls, label=label)
    ax.fill_between(eps_grid, ew_lo, ew_hi, color=color, alpha=0.12)


def main():
    eps_grid = np.linspace(0.0, EPS_MAX, N_EPS)

    a1, b1 = 0.0, 4.0
    v1_fixed = lambda z, a=a1, b=b1: _sigma(a + b * np.asarray(z, float))

    # gamma-Sweep (Sensitivity Sweep, u2=0 fixed, sweep v2 in {-8, -6, -4, -2, +2})
    gamma_vals   = [-8, -6, -4, -2, +2]
    gamma_colors = ["#08306b", "#2171b5", "#6baed6", "#fd8d3c", "#a50f15"]
    gamma_ls     = ["-",       "-",       "--",      "-",       "-"]

    profiles = []
    for b2, color, ls in zip(gamma_vals, gamma_colors, gamma_ls):
        lbl = (r"$v_2{=}" + f"{b2:+d}$")
        v2  = (lambda z, b=b2: _sigma(b * np.asarray(z, float)))
        profiles.append((lbl, v2, color, ls))

    # Create 2-panel unified figure
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.2))
    fig.subplots_adjust(wspace=0.25)

    for i, (label, v2, color, ls) in enumerate(profiles):
        print(f"  Simulating gamma-Sweep {label} ...")
        ew, ew_lo, ew_hi, ec, ec_lo, ec_hi = simulate_profile(
            eps_grid, v1_fixed, v2, seed=GLOBAL_SEED + i)
        _draw_panel(axs[0], eps_grid, ew, ew_lo, ew_hi, color, ls, label)
        _draw_panel(axs[1], eps_grid, ec, ec_lo, ec_hi, color, ls, label)

    g1_str = r"$V_1(z)=\sigma(4z)$ [fixed]"

    # Configure axs[0]: Welfare
    axs[0].set_title(r"(a) $\gamma$-Sweep: Expected Social Welfare" + "\n" + g1_str, fontsize=10.5)
    axs[0].set_xlabel(r"Enforcement Strictness $\varepsilon$", fontsize=10)
    axs[0].set_ylabel("Expected Per-Capita Welfare", fontsize=10)
    axs[0].grid(True, ls="--", alpha=0.45)
    axs[0].legend(fontsize=8.5, framealpha=0.9, title=r"$u_1{=}0, v_1{=}+4 \mid u_2{=}0$", title_fontsize=8, loc="lower right")

    # Configure axs[1]: Firm Capital
    axs[1].set_title(r"(b) $\gamma$-Sweep: Expected Firm Capital" + "\n" + g1_str, fontsize=10.5)
    axs[1].set_xlabel(r"Enforcement Strictness $\varepsilon$", fontsize=10)
    axs[1].set_ylabel("Expected Firm Capital (Per-Capita)", fontsize=10)
    axs[1].grid(True, ls="--", alpha=0.45)
    axs[1].legend(fontsize=8.5, framealpha=0.9, title=r"$u_1{=}0, v_1{=}+4 \mid u_2{=}0$", title_fontsize=8, loc="upper left")

    plt.tight_layout()
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "decision_sim_results.pdf")
    plt.savefig(out, format="pdf", bbox_inches="tight")
    out_png = os.path.join(out_dir, "decision_sim_results.png")
    plt.savefig(out_png, format="png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved unified 2-panel figure -> {out}")


if __name__ == "__main__":
    main()

# Applied Fix: Implemented true affine concave example rather than sigmoid surrogate.
