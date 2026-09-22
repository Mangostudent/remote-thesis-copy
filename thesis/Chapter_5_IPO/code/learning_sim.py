"""
GP-TS learning simulation (Chapter 5).
Average regret R_t/t under low (sigma=0.05) and high (sigma=0.25) noise.
"""

import random
import numpy as np
import matplotlib.pyplot as plt
import os
import warnings

# Global reproducibility seed
GLOBAL_SEED = 42
np.random.seed(GLOBAL_SEED)
random.seed(GLOBAL_SEED)

warnings.filterwarnings("ignore")

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel as C

N1, N2, N = 50, 50, 100


def firm_br_linear(x, eps, beta=3.0):
    """Firm best response under linear valuation V_j(z) = max(0, 1 +/- beta*z)."""
    y_grid = np.linspace(x - eps, x + eps, 201)
    v1 = np.maximum(0.0, 1 + beta * y_grid)
    v2 = np.maximum(0.0, 1 - beta * y_grid)
    rev = np.stack([100 * np.minimum(v1, v2), 50 * v1, 50 * v2])
    strat = int(np.argmax(np.max(rev, axis=1)))
    idx = int(np.argmax(rev[strat]))
    y = y_grid[idx]
    if strat == 0:
        return y, min(1 + beta * y, 1 - beta * y), 100
    if strat == 1:
        return y, 1 + beta * y, 50
    return y, 1 - beta * y, 50


def precompute_welfare(eps_grid, num_x=2000, seed=0):
    """Precomputes true expected welfare f(eps) over the eps grid."""
    rng = np.random.default_rng(seed)
    X = rng.uniform(-1 / 3, 1 / 3, num_x)
    types = rng.choice([1, 2], size=num_x)
    W = []
    for eps in eps_grid:
        vals = []
        for x, j in zip(X, types):
            _, _, q = firm_br_linear(x, eps)
            y_true = max(0.0, 1 + 3 * x) if j == 1 else max(0.0, 1 - 3 * x)
            vals.append(q * y_true / N)
        W.append(np.mean(vals))
    return np.asarray(W)


def run_gpts(noise, W_true, eps_grid, T=1000, seed=1):
    """Runs one trial of GP-Thompson Sampling on the welfare function."""
    rng = np.random.default_rng(seed)
    opt = float(np.max(W_true))
    kernel = C(1.0, (1e-2, 1e2)) * Matern(length_scale=0.3, nu=2.5)
    gp = GaussianProcessRegressor(kernel=kernel, alpha=noise**2, normalize_y=True,
                                  n_restarts_optimizer=2)
    X_train, y_train = [], []
    cum = []
    regret_sum = 0.0

    idx = int(rng.integers(0, len(eps_grid)))
    true_w = W_true[idx]
    y_obs = true_w + rng.normal(0.0, noise)
    X_train.append([eps_grid[idx]])
    y_train.append(y_obs)
    gp.fit(np.asarray(X_train), np.asarray(y_train))
    regret_sum += opt - true_w
    cum.append(regret_sum)

    for t in range(1, T):
        # Thompson sample: draw one posterior path on the grid
        mean, cov = gp.predict(eps_grid.reshape(-1, 1), return_cov=True)
        cov = cov + 1e-8 * np.eye(len(eps_grid))
        sample = rng.multivariate_normal(mean, cov)
        action = int(np.argmax(sample))
        true_w = W_true[action]
        y_obs = true_w + rng.normal(0.0, noise)
        X_train.append([eps_grid[action]])
        y_train.append(y_obs)
        # Refit GP periodically for speed
        if t % 5 == 0 or t < 20:
            gp.fit(np.asarray(X_train), np.asarray(y_train))
        regret_sum += opt - true_w
        cum.append(regret_sum)

    return np.asarray(cum)


def main():
    eps_grid = np.linspace(0.0, 1.2, 61)
    print("Precomputing true welfare...")
    W_true = precompute_welfare(eps_grid)

    T = 500
    n_trials = 40
    noises = [
        {"label": r"Low noise ($\sigma=0.05$)", "sigma": 0.05, "color": "#1f77b4"},
        {"label": r"High noise ($\sigma=0.25$)", "sigma": 0.25, "color": "#d62728"}
    ]

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    t_arr = np.arange(1, T + 1)
    phi = t_arr ** (2.0 / 3.0)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "figures")
    data_dir = os.path.join(os.path.dirname(__file__), "..", ".build", "data")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    cache_path = os.path.join(data_dir, "learning_sim_data.pkl")

    all_data = {}
    if os.path.exists(cache_path):
        import pickle
        print("Loading cached GP-TS simulation data...")
        with open(cache_path, "rb") as f:
            all_data = pickle.load(f)
    else:
        for cfg in noises:
            sigma = cfg["sigma"]
            label = cfg["label"]
            print(f"Running GP-TS ({label}) over {n_trials} trials...")
            curves = []
            for s in range(n_trials):
                curves.append(run_gpts(sigma, W_true, eps_grid, T=T, seed=100 + s))
            curves = np.stack(curves)
            all_data[sigma] = curves
        import pickle
        with open(cache_path, "wb") as f:
            pickle.dump(all_data, f)

    for cfg in noises:
        sigma = cfg["sigma"]
        color = cfg["color"]
        label = cfg["label"]
        curves = all_data[sigma]
        mean_r = curves.mean(axis=0)
        std_r = curves.std(axis=0, ddof=1)
        sem = std_r / np.sqrt(n_trials)

        ax.plot(t_arr, mean_r, color=color, lw=2.2, label=rf"Empirical $R_T$ ({label})")
        ax.fill_between(t_arr, np.maximum(0, mean_r - sem), mean_r + sem, color=color, alpha=0.18, label=rf"Mean $\pm$ 1 SE ({label})")

    ax.set_title(r"GP-TS Cumulative Regret $R_T$ vs. Episodes $T$", fontsize=12, pad=10)
    ax.set_xlabel(r"Episode $t$", fontsize=11)
    ax.set_ylabel(r"Cumulative Regret $R_T$", fontsize=11)
    ax.legend(fontsize=8.5, loc="upper left", framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    out_pdf = os.path.join(out_dir, "learning_results.pdf")
    out_png = os.path.join(out_dir, "learning_results.png")
    plt.savefig(out_pdf, format="pdf", bbox_inches="tight")
    plt.savefig(out_png, format="png", dpi=300, bbox_inches="tight")
    print(f"Saved {out_pdf} and {out_png}")


if __name__ == "__main__":
    main()
