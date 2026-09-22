"""
Experiment 2: Regression Learning Problem
Generalization gap |Delta(E) - Delta_hat(D_n)| vs sample size n
for feature dimensions d=2 and d=5, with least-squares reference
fit C * sqrt(d/n), under a fat-tailed Student-t Mixture Model (nu=5).
"""

import numpy as np
import matplotlib.pyplot as plt
import pickle
from pathlib import Path
from scipy.optimize import minimize
from scipy.interpolate import make_interp_spline
from scipy.ndimage import gaussian_filter1d

import random

GLOBAL_SEED = 42
np.random.seed(GLOBAL_SEED)
random.seed(GLOBAL_SEED)

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"
DATA_DIR = Path(__file__).resolve().parent.parent / ".build" / "data"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("Running Regression Learning Curves for Generalization Gap...")

n_sizes = np.unique(np.int32(np.geomspace(50, 3000, 65)))
M_repeats = 15
dimensions = [2, 5]
q = 0.5
test_size = 10000
NU_DOF = 5  # Degrees of freedom for fat-tailed Student-t mixture


def sample_tmm_environment(n, d, rng, nu=NU_DOF):
    """Samples (X, Y, U) from a fat-tailed 2-component Student-t Mixture Model."""
    n1 = rng.binomial(n, 0.6)
    n2 = n - n1

    cov = np.zeros((d + 2, d + 2))
    cov[:d, :d] = 0.64 * np.eye(d)
    cov[d, d] = 0.6
    cov[d + 1, d + 1] = 0.5
    cov[:d, d] = 0.4
    cov[d, :d] = 0.4
    cov[:d, d + 1] = 0.25
    cov[d + 1, :d] = 0.25
    cov[d, d + 1] = 0.3
    cov[d + 1, d] = 0.3

    min_eig = np.min(np.linalg.eigvalsh(cov))
    if min_eig <= 0:
        cov += (abs(min_eig) + 0.05) * np.eye(d + 2)

    mu1 = np.zeros(d + 2)
    mu1[:d] = 0.6
    mu1[d] = 1.0
    mu1[d + 1] = 1.0

    mu2 = np.zeros(d + 2)
    mu2[:d] = -0.6
    mu2[d] = -0.8
    mu2[d + 1] = -1.0

    w1 = rng.chisquare(nu, size=(n1, 1)) / nu
    z1 = rng.multivariate_normal(np.zeros(d + 2), cov, size=n1) if n1 > 0 else np.empty((0, d + 2))
    s1 = mu1 + z1 / np.sqrt(w1) if n1 > 0 else np.empty((0, d + 2))

    w2 = rng.chisquare(nu, size=(n2, 1)) / nu
    z2 = rng.multivariate_normal(np.zeros(d + 2), cov, size=n2) if n2 > 0 else np.empty((0, d + 2))
    s2 = mu2 + z2 / np.sqrt(w2) if n2 > 0 else np.empty((0, d + 2))

    samples = np.vstack([s1, s2]) if (n1 > 0 and n2 > 0) else (s1 if n1 > 0 else s2)
    perm = rng.permutation(len(samples))
    samples = samples[perm]

    return samples[:, :d], samples[:, d], samples[:, d + 1]


results_data = {}
cache_file = DATA_DIR / "regression_learning_data.pkl"

if cache_file.exists():
    print("Loading cached regression learning simulation data...")
    with open(cache_file, 'rb') as f:
        results_data = pickle.load(f)
else:
    for d in dimensions:
        print(f"Computing generalization gap curves for d = {d}...")

        def get_vanilla_risk(b, X_data, Y_data):
            return (1 - q) * np.mean((Y_data - X_data @ b)**2) + q * np.mean(Y_data**2)

        def get_strategic_risk(b, X_data, Y_data, U_data):
            preds = X_data @ b
            # Sender reveals if 2*U*pred - pred^2 >= 0
            F = (2 * U_data - preds) * preds
            losses = np.where(F > 0, (Y_data - preds)**2, Y_data**2)
            return q * np.mean(Y_data**2) + (1 - q) * np.mean(losses)

        mean_gaps = []
        std_gaps = []
        all_runs_gaps = []

        for n in n_sizes:
            gaps = []
            for run in range(M_repeats):
                seed_val = int(d * 100000 + n * 100 + run)
                rng_tr = np.random.RandomState(seed_val)

                X_tr, Y_tr, U_tr = sample_tmm_environment(n, d, rng_tr, nu=NU_DOF)
                X_test, Y_test, U_test = sample_tmm_environment(test_size, d, rng_tr, nu=NU_DOF)

                # Vanilla ERM: b_V = (X^T X)^{-1} X^T Y
                b_v = np.linalg.pinv(X_tr) @ Y_tr

                # Strategic ERM
                if d == 1:
                    b_cands = np.linspace(-3.0, 3.0, 200)
                    train_risks = [get_strategic_risk(np.array([b_val]), X_tr, Y_tr, U_tr) for b_val in b_cands]
                    b_s = np.array([b_cands[np.argmin(train_risks)]])
                else:
                    res = minimize(get_strategic_risk, b_v, args=(X_tr, Y_tr, U_tr), method='Powell', options={'maxiter': 500})
                    b_s = res.x

                # Delta_hat(D_n) = R_V(b_V; D_n) - R_S(b_S; D_n)
                rv_train = get_vanilla_risk(b_v, X_tr, Y_tr)
                rs_train = get_strategic_risk(b_s, X_tr, Y_tr, U_tr)
                delta_hat_train = rv_train - rs_train

                # Delta(E) = R_V(b_V; E) - R_S(b_S; E)
                rv_test = get_vanilla_risk(b_v, X_test, Y_test)
                rs_test = get_strategic_risk(b_s, X_test, Y_test, U_test)
                delta_population = rv_test - rs_test

                # Generalization gap |Delta(E) - Delta_hat(D_n)|
                gaps.append(abs(delta_population - delta_hat_train))

            mean_gaps.append(np.mean(gaps))
            std_gaps.append(np.std(gaps, ddof=1))
            all_runs_gaps.append(gaps)

        results_data[d] = {
            'n_sizes': np.array(n_sizes),
            'mean_gaps': np.array(mean_gaps),
            'std_gaps': np.array(std_gaps),
            'all_gaps': np.array(all_runs_gaps)
        }

    with open(cache_file, 'wb') as f:
        pickle.dump(results_data, f)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(1, 1, figsize=(8.0, 5.0))

colors = {2: '#d95f02', 5: '#7570b3'}

for d in dimensions:
    data = results_data[d]
    ns = data['n_sizes']
    means = data['mean_gaps']
    stds = data['std_gaps']

    # Standard error of the mean (1 SE)
    sem = stds / np.sqrt(M_repeats)

    means_smooth_pts = gaussian_filter1d(means, sigma=1.8)
    sem_smooth_pts = gaussian_filter1d(sem, sigma=1.8)

    ns_smooth = np.linspace(ns.min(), ns.max(), 300)
    spl_mean = make_interp_spline(ns, means_smooth_pts, k=3)(ns_smooth)
    spl_upper = make_interp_spline(ns, means_smooth_pts + sem_smooth_pts, k=3)(ns_smooth)
    spl_lower = make_interp_spline(ns, np.maximum(0, means_smooth_pts - sem_smooth_pts), k=3)(ns_smooth)

    ax.plot(ns_smooth, spl_mean, color=colors[d], linewidth=2.4, zorder=4,
            label=rf'Mean Gap ($d={d}$)')
    ax.fill_between(ns_smooth, np.maximum(0, spl_lower), spl_upper, color=colors[d], alpha=0.18, zorder=3,
                    label=rf'Mean $\pm$ 1 SE ($d={d}$)')

ax.set_xscale('log')
ax.set_xlabel(r'Training Sample Size $n$', fontsize=12)
ax.set_ylabel(r'Strategic Advantage Gap $|\Delta(\mathcal{E}) - \widehat{\Delta}(D_n)|$', fontsize=12)
ax.set_title(r'Strategic Advantage Generalization Gap vs. Sample Size ($q=0.5$)', fontsize=13, pad=12)
ax.grid(True, which="both", linestyle='--', alpha=0.5)
ax.legend(loc='upper right', frameon=True, framealpha=0.9, fontsize=10)
plt.tight_layout()

for fname in ["regression_learning_gaps.png", "regression_learning_gaps.pdf"]:
    out_p = FIGURES_DIR / fname
    plt.savefig(out_p, dpi=300, bbox_inches='tight')
    print(f"Saved figure to {out_p}")

plt.close()
print("Regression Learning execution complete!")
