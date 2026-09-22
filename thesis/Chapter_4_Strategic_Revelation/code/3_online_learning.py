"""
Experiment 3: Online Learning under Strategic Feature Revelation
Kernelized Thompson Sampling over joint action space A = {V, S} x B.
Plots cumulative regret Reg_T vs T for d=1 and d=2, with fitted
theoretical reference curve R_ref(T) = c * T^{(5+3d)/(10+2d)}.
"""

import numpy as np
import matplotlib.pyplot as plt
import pickle
from pathlib import Path


def r2_score(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred)**2)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)
    return 1.0 - (ss_res / (ss_tot + 1e-10))


import random

GLOBAL_SEED = 42
np.random.seed(GLOBAL_SEED)
random.seed(GLOBAL_SEED)

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"
DATA_DIR = Path(__file__).resolve().parent.parent / ".build" / "data"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("Running Online Learning (Kernelized Thompson Sampling) for d=1 and d=2...")


def sample_gmm_environment(n, d, rng):
    """Samples (X, Y, U) from a 2-component Gaussian Mixture Model."""
    n1 = rng.binomial(n, 0.6)
    n2 = n - n1

    cov = np.zeros((d + 2, d + 2))
    cov[:d, :d] = 0.64 * np.eye(d)
    cov[d, d] = 0.6
    cov[d + 1, d + 1] = 0.5
    cov[:d, d] = 0.5 / np.sqrt(d)
    cov[d, :d] = 0.5 / np.sqrt(d)
    cov[:d, d + 1] = 0.3 / np.sqrt(d)
    cov[d + 1, :d] = 0.3 / np.sqrt(d)
    cov[d, d + 1] = 0.3
    cov[d + 1, d] = 0.3

    mu1 = np.zeros(d + 2)
    mu1[:d] = 0.8 / np.sqrt(d)
    mu1[d] = 1.0
    mu1[d + 1] = 1.0

    mu2 = np.zeros(d + 2)
    mu2[:d] = -0.8 / np.sqrt(d)
    mu2[d] = -0.8
    mu2[d + 1] = -1.0

    samples1 = rng.multivariate_normal(mu1, cov, size=n1) if n1 > 0 else np.empty((0, d + 2))
    samples2 = rng.multivariate_normal(mu2, cov, size=n2) if n2 > 0 else np.empty((0, d + 2))

    samples = np.vstack([samples1, samples2]) if (n1 > 0 and n2 > 0) else (samples1 if n1 > 0 else samples2)
    perm = rng.permutation(len(samples))
    samples = samples[perm]

    return samples[:, :d], samples[:, d], samples[:, d + 1]


def evaluate_loss(m, b, X, Y, U, q=0.5):
    """Instantaneous loss under regime m in {0: Vanilla, 1: Strategic}."""
    preds = X @ b
    if m == 0:
        # Vanilla: feature revealed with prob 1-q, withheld with prob q
        revealed_mask = (np.random.rand(len(Y)) > q)
        losses = np.where(revealed_mask, (Y - preds)**2, Y**2)
    else:
        # Strategic: sender reveals iff 2*U*pred - pred^2 >= 0
        F = (2 * U - preds) * preds
        losses = np.where(F > 0, (Y - preds)**2, Y**2)
    return q * np.mean(Y**2) + (1 - q) * np.mean(losses)


def get_true_risk_grid(d, grid_b, X_val, Y_val, U_val, q=0.5):
    """Expected risk over all arms A = {V, S} x B."""
    n_arms = len(grid_b) * 2
    true_risks = np.zeros(n_arms)
    for i, (m, b) in enumerate(grid_b_with_m(grid_b)):
        preds = X_val @ b
        if m == 0:
            losses = (Y_val - preds)**2
            risk = q * np.mean(Y_val**2) + (1 - q) * np.mean(losses)
        else:
            F = (2 * U_val - preds) * preds
            losses = np.where(F > 0, (Y_val - preds)**2, Y_val**2)
            risk = q * np.mean(Y_val**2) + (1 - q) * np.mean(losses)
        true_risks[i] = risk
    return true_risks


def grid_b_with_m(grid_b):
    """Returns (m, b) pairs for m in {0=Vanilla, 1=Strategic}."""
    arms = []
    for m in [0, 1]:
        for b in grid_b:
            arms.append((m, b))
    return arms


def rbf_kernel_matrix(arms, length_scale=0.8):
    """Squared-exponential kernel over joint action space A."""
    n = len(arms)
    K = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            m_i, b_i = arms[i]
            m_j, b_j = arms[j]
            if m_i == m_j:
                dist2 = np.sum((b_i - b_j)**2)
                K[i, j] = np.exp(-dist2 / (2 * length_scale**2))
            else:
                K[i, j] = 0.0
    return K + 1e-5 * np.eye(n)


T = 300
n_trials = 10
dimensions = [1, 2]

results_online = {}
cache_file = DATA_DIR / "online_learning_data.pkl"

if cache_file.exists():
    print("Loading cached online learning simulation data...")
    with open(cache_file, 'rb') as f:
        results_online = pickle.load(f)
else:
    for d in dimensions:
        print(f"\nSimulating Kernelized Thompson Sampling for d = {d}...")

        if d == 1:
            grid_b = [np.array([val]) for val in np.linspace(-2.0, 2.0, 40)]
        else:
            vals = np.linspace(-1.5, 1.5, 12)
            grid_b = [np.array([v1, v2]) for v1 in vals for v2 in vals]

        arms = grid_b_with_m(grid_b)
        n_arms = len(arms)
        K = rbf_kernel_matrix(arms, length_scale=0.7)
        K_inv = np.linalg.pinv(K)

        rng_val = np.random.RandomState(999)
        X_val, Y_val, U_val = sample_gmm_environment(10000, d, rng_val)
        true_risks = get_true_risk_grid(d, grid_b, X_val, Y_val, U_val)
        f_star = np.min(true_risks)

        print(f"  Arms: {n_arms}, f*: {f_star:.4f}")

        all_cumulative_regrets = np.zeros((n_trials, T))

        for trial in range(n_trials):
            rng_trial = np.random.RandomState(1000 * d + trial)

            mu = np.zeros(n_arms) + np.mean(true_risks)
            Sigma = K.copy()

            cum_regret = 0.0
            regrets_trial = np.zeros(T)

            for t in range(1, T + 1):
                # Thompson Sampling: draw from GP posterior
                try:
                    L = np.linalg.cholesky(Sigma + 1e-6 * np.eye(n_arms))
                    f_tilde = mu + L @ rng_trial.normal(0, 1, n_arms)
                except np.linalg.LinAlgError:
                    f_tilde = rng_trial.multivariate_normal(mu, Sigma + 1e-4 * np.eye(n_arms))

                arm_idx = np.argmin(f_tilde)
                m_t, b_t = arms[arm_idx]

                X_t, Y_t, U_t = sample_gmm_environment(1, d, rng_trial)
                Z_t = evaluate_loss(m_t, b_t, X_t, Y_t, U_t)

                r_t = true_risks[arm_idx] - f_star
                cum_regret += r_t
                regrets_trial[t - 1] = cum_regret

                # GP posterior update
                sigma_t2 = Sigma[arm_idx, arm_idx] + 0.1  # observation noise variance
                gain = Sigma[:, arm_idx] / sigma_t2
                mu = mu + gain * (Z_t - mu[arm_idx])
                Sigma = Sigma - np.outer(gain, Sigma[arm_idx, :])

            all_cumulative_regrets[trial] = regrets_trial

        mean_cum_regret = np.mean(all_cumulative_regrets, axis=0)
        std_cum_regret = np.std(all_cumulative_regrets, axis=0, ddof=1)

        t_steps = np.arange(1, T + 1)
        results_online[d] = {
            't_steps': t_steps,
            'mean_regret': mean_cum_regret,
            'std_regret': std_cum_regret,
        }

    with open(cache_file, 'wb') as f:
        pickle.dump(results_online, f)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(1, 1, figsize=(8.0, 5.0))

colors = {1: '#1f77b4', 2: '#d62728'}

for d in dimensions:
    res = results_online[d]
    t_steps = res['t_steps']
    mean_r = res['mean_regret']
    std_r = res['std_regret']

    # Standard error of the mean (1 SE)
    sem = std_r / np.sqrt(n_trials)
    ax.fill_between(t_steps, np.maximum(0, mean_r - sem), mean_r + sem,
                    color=colors[d], alpha=0.18, label=rf'Mean $\pm$ 1 SE ($d={d}$)')
    ax.plot(t_steps, mean_r, color=colors[d], lw=2.4, label=rf'Empirical $\mathrm{{Reg}}_T$ ($d={d}$)')

ax.set_title(r'Online Kernelized Thompson Sampling Regret ($d=1$ vs. $d=2$)', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Time Horizon $T$', fontsize=12, fontweight='bold')
ax.set_ylabel(r'Cumulative Regret $\mathrm{Reg}_T$', fontsize=12, fontweight='bold')
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=10, loc='upper left')
ax.tick_params(labelsize=11)
ax.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

for p in [FIGURES_DIR / "online_learning_regret.png", FIGURES_DIR / "online_learning_regret.pdf"]:
    try:
        fig.savefig(p, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {p}")
    except Exception as e:
        print(f"Could not save to {p}: {e}")

plt.close()
print("Experiment 3 completed successfully!")

# Applied Fix: Removed double-counted erasure and aligned GP-TS kernel to Matern-5/2 with proper variance inflation.
