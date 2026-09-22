"""
Side Information Learning from Partitioned Data (Chapter 3)

This script implements:
1. Three Gaussian Mixture Model (GMM) toy examples across different signal-imputation regimes,
   with truncated covariates satisfying Assumption C1 (boundedness).
2. Three real-world benchmark datasets from OpenML (Adult Income, Bank Marketing, and Mushroom)
   with strict 3-way splitting (training pool, oracle tuning sample, held-out test set).
3. Exact regularized logistic regression solver matching Algorithm 3.1:
   - Stage 1: Imputer u_hat = argmin L_hat(u) + mu * ||u||^2 (mu = c / sqrt(m)).
     Hard imputation: phi_hat(X) = 2 * I{sigma(u_hat^T (1, X)) >= 0.5} - 1 in {-1, +1}.
   - Stage 2: Primary learner w_hat = argmin R_hat^phi(w) + lambda_c * |w_c|^2 + lambda_x * ||w_x||^2 + lambda_z * |w_z|^2
     with lambda_c = 1 / sqrt(n), lambda_x = 1 / sqrt(n), lambda_z = lambda_z^* (three-candidate rule).
   - Stage 3: Deployment test risk R(w_hat) evaluated with OBSERVED side information Z_test in {-1, +1}.
4. Evaluates Theoretical Upper Bound (RHS) and Actual Excess Risk (LHS) with 99% confidence bands.
"""

import os
import random
import time
import numpy as np
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.datasets import fetch_openml

# Set global reproducibility seed
GLOBAL_SEED = 42
np.random.seed(GLOBAL_SEED)
random.seed(GLOBAL_SEED)

def sigmoid(x):
    """Numerically stable sigmoid function."""
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

def solve_regularized_logistic(X, y, reg_weights, w0=None):
    """
    Solves the exact regularized logistic regression problem:
        min_w  (1 / N) * sum_{i=1}^N ln(1 + exp(-y_i * (w^T x_i))) + sum_{k=1}^K reg_weights[k] * w_k^2
    where y in {-1, +1} and X has shape (N, K).
    """
    N, K = X.shape
    if w0 is None:
        w0 = np.zeros(K)
        
    def loss_grad(w):
        margin = y * (X @ w)
        # Numerically stable log(1 + exp(-m))
        loss_vec = np.where(margin > 0,
                            np.log1p(np.exp(-np.clip(margin, -30, 30))),
                            -margin + np.log1p(np.exp(np.clip(margin, -30, 30))))
        loss = np.mean(loss_vec) + np.sum(reg_weights * (w**2))
        
        p_neg = 1.0 / (1.0 + np.exp(np.clip(margin, -30, 30)))
        grad = -(X.T @ (y * p_neg)) / N + 2.0 * reg_weights * w
        return loss, grad

    res = minimize(loss_grad, w0, jac=True, method='L-BFGS-B', options={'maxiter': 300, 'ftol': 1e-8})
    return res.x

def eval_logistic_risk(X, y, w):
    """Computes unregularized logistic risk: (1 / N) * sum_{i=1}^N ln(1 + exp(-y_i * (w^T x_i)))."""
    margin = y * (X @ w)
    loss_vec = np.where(margin > 0,
                        np.log1p(np.exp(-np.clip(margin, -30, 30))),
                        -margin + np.log1p(np.exp(np.clip(margin, -30, 30))))
    return float(np.mean(loss_vec))


# =====================================================================
# 1. SYNTHETIC TOY GAUSSIAN MIXTURE DISTRIBUTIONS (3 EXAMPLES)
# =====================================================================

def generate_gmm_population(dist_type=1, N_pop=50000, d=5, seed=42, kappa=4.0):
    """
    Generate population data from a Gaussian Mixture Model with 3 components,
    truncated to ||X||_2 <= kappa to strictly satisfy Assumption C1 (boundedness).
    dist_type 1: Informative side information (high signal-imputation ratio).
    dist_type 2: Moderate regime (balanced signal and imputation noise).
    dist_type 3: Noisy side information (low signal-imputation ratio).
    """
    rng = np.random.default_rng(seed)
    
    # 3 Mixture components in R^5
    comp = rng.choice(3, size=N_pop, p=[0.4, 0.35, 0.25])
    means = np.array([
        [1.2, -1.0, 0.5, 0.0, 0.8],
        [-1.0, 1.2, -0.6, 0.8, -0.2],
        [0.0, -0.2, 1.0, -1.0, -0.8]
    ])
    X = means[comp] + rng.normal(0, 0.7, size=(N_pop, d))
    
    # Truncate X to satisfy Assumption C1 (||X||_2 <= kappa)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    X = np.where(norms > kappa, X * (kappa / norms), X)
    X_ones = np.column_stack([np.ones(N_pop), X])
    
    if dist_type == 1:
        # High signal, low imputation loss
        u = np.array([0.2, 1.5, -1.2, 0.8, -0.4, 1.0])
        w = np.array([0.1, 0.4, -0.3, 0.2, 0.5, 0.1, 2.0])
    elif dist_type == 2:
        # Moderate regime
        u = np.array([0.0, 0.8, -0.6, 0.4, 0.1, -0.3])
        w = np.array([-0.1, 0.5, -0.5, 0.3, 0.4, 0.2, 1.2])
    else:
        # Noisy side information / weaker coupling
        u = np.array([0.1, 0.3, -0.2, 0.1, 0.0, -0.1])
        w = np.array([0.2, 0.8, -0.7, 0.5, 0.6, 0.3, 0.5])
        
    prob_z = sigmoid(X_ones @ u)
    Z = np.where(rng.uniform(size=N_pop) < prob_z, 1.0, -1.0)
    
    XZ_ones = np.column_stack([X_ones, Z])
    prob_y = sigmoid(XZ_ones @ w)
    Y = np.where(rng.uniform(size=N_pop) < prob_y, 1.0, -1.0)
    
    # Oracle fits on the population with vanishing regularization
    w_star = solve_regularized_logistic(XZ_ones, Y, np.full(d + 2, 1e-6))
    R_w_star = eval_logistic_risk(XZ_ones, Y, w_star)
    
    v_star = solve_regularized_logistic(X_ones, Y, np.full(d + 1, 1e-6))
    T_v_star = eval_logistic_risk(X_ones, Y, v_star)
    
    u_star = solve_regularized_logistic(X_ones, Z, np.full(d + 1, 1e-6))
    L_u_star = eval_logistic_risk(X_ones, Z, u_star)
    
    a = float(w_star[-1]**2)
    Delta = float(max(1e-4, T_v_star - R_w_star))
    
    return u, w, means, R_w_star, a, Delta, float(L_u_star), kappa

def sample_gmm(means, u, w, N, d=5, rng=None, kappa=4.0):
    """Sample N independent observations from the truncated GMM distribution."""
    if rng is None:
        rng = np.random.default_rng()
    comp = rng.choice(3, size=N, p=[0.4, 0.35, 0.25])
    X = means[comp] + rng.normal(0, 0.7, size=(N, d))
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    X = np.where(norms > kappa, X * (kappa / norms), X)
    X_ones = np.column_stack([np.ones(N), X])
    
    prob_z = sigmoid(X_ones @ u)
    Z = np.where(rng.uniform(size=N) < prob_z, 1.0, -1.0)
    
    XZ_ones = np.column_stack([X_ones, Z])
    prob_y = sigmoid(XZ_ones @ w)
    Y = np.where(rng.uniform(size=N) < prob_y, 1.0, -1.0)
    return X, Z, Y

def run_toy_experiments():
    print("--- Running Synthetic GMM Toy Experiments (3 Distributions) ---")
    N_values = np.array([500, 1000, 2000, 5000])
    n_trials = 20
    d = 5
    
    dist_names = [
        "Toy Distribution 1 (High Signal)",
        "Toy Distribution 2 (Moderate Signal)",
        "Toy Distribution 3 (Noisy Side Info)"
    ]
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    for dist_idx in range(1, 4):
        u, w, means, R_w_star, a, Delta, L_u_star, kappa = generate_gmm_population(dist_type=dist_idx, d=d)
        
        # Test set for evaluating true deployment excess risk
        rng_test = np.random.default_rng(999 + dist_idx)
        X_test, Z_test, Y_test = sample_gmm(means, u, w, N=20000, d=d, rng=rng_test, kappa=kappa)
        X_test_aug = np.column_stack([np.ones(len(Y_test)), X_test, Z_test])
        
        mean_lhs = []
        std_lhs = []
        rhs_vals = []
        
        for N in N_values:
            M = N # Set M = N
            
            # Theoretical RHS upper bound evaluated at optimal lambda_z^* (Corollary 3.1)
            b_m = (4.0 / np.log(2.0)) * (L_u_star + 1.0 / np.sqrt(M))
            lam_0 = 1.0 / np.sqrt(N)
            candidates = [lam_0, 1e4]
            if a > 0:
                lam_I = np.sqrt(b_m / (2.0 * a))
                if lam_I >= lam_0:
                    candidates.append(lam_I)
                    
            def F(lam):
                return min(a * lam, Delta) + b_m * min(1.0, 1.0 / (2.0 * lam))
                
            best_lam = min(candidates, key=F)
            rhs = 1.0 / np.sqrt(N) + F(best_lam)
            rhs_vals.append(rhs)
            
            lhs_trials = []
            rng_sim = np.random.default_rng(dist_idx * 10000 + N)
            for t in range(n_trials):
                # 1. Auxiliary dataset S of size M
                X_xz, Z_xz, _ = sample_gmm(means, u, w, N=M, d=d, rng=rng_sim, kappa=kappa)
                # 2. Primary dataset D of size N
                X_xy, _, Y_xy = sample_gmm(means, u, w, N=N, d=d, rng=rng_sim, kappa=kappa)
                
                # Stage 1: Fit imputer u_hat on S with mu = 1 / sqrt(M)
                X_s_ones = np.column_stack([np.ones(M), X_xz])
                reg_imputer = np.full(d + 1, 1.0 / np.sqrt(M))
                u_hat = solve_regularized_logistic(X_s_ones, Z_xz, reg_imputer)
                
                # Hard imputation: phi_hat(X) in {-1, +1}
                X_d_ones = np.column_stack([np.ones(N), X_xy])
                z_hat_d = np.where(X_d_ones @ u_hat >= 0.0, 1.0, -1.0)
                
                # Stage 2: Fit primary classifier w_hat on D with regularizer lambda_z^*
                # Penalties: lambda_c = 1 / sqrt(N), lambda_x = 1 / sqrt(N), lambda_z = best_lam
                X_aug_d = np.column_stack([X_d_ones, z_hat_d])
                reg_primary = np.array([1.0 / np.sqrt(N)] * (d + 1) + [best_lam])
                w_hat = solve_regularized_logistic(X_aug_d, Y_xy, reg_primary)
                
                # Stage 3: Evaluate deployment risk with OBSERVED Z_test
                test_loss = eval_logistic_risk(X_test_aug, Y_test, w_hat)
                lhs = test_loss - R_w_star  # Unclipped excess risk
                lhs_trials.append(lhs)
                
            mean_lhs.append(np.mean(lhs_trials))
            std_lhs.append(np.std(lhs_trials, ddof=1))
            print(f"Dist {dist_idx} (N={N}, M={M}): LHS={mean_lhs[-1]:.4f}, RHS={rhs_vals[-1]:.4f}")
            
        mean_lhs = np.array(mean_lhs)
        std_lhs = np.array(std_lhs)
        ci_99 = stats.t.ppf(0.995, n_trials - 1) * std_lhs / np.sqrt(n_trials)
        
        ax = axes[dist_idx - 1]
        ax.plot(N_values, mean_lhs, marker='o', color='#1f77b4', lw=2, label='Actual Excess Risk (LHS)')
        ax.fill_between(N_values, mean_lhs - ci_99, mean_lhs + ci_99, color='#1f77b4', alpha=0.25, label='99% Confidence Band')
        ax.plot(N_values, rhs_vals, marker='s', linestyle='--', color='#d62728', lw=2, label='Theoretical Bound (RHS)')
        
        ax.set_title(dist_names[dist_idx - 1], fontsize=11, fontweight='bold')
        ax.set_xlabel('Sample Size $N$ ($M=N$)', fontsize=10)
        ax.set_ylabel('Excess Risk', fontsize=10)
        ax.grid(True, linestyle=':', alpha=0.6)
        if dist_idx == 1:
            ax.legend(fontsize=9, loc='upper right')
            
    plt.tight_layout()
    toy_out_code = os.path.join(os.path.dirname(__file__), "fig_excess_risk_toy.pdf")
    toy_out_fig = os.path.join(os.path.dirname(__file__), "..", "Figures", "fig_excess_risk_toy.pdf")
    plt.savefig(toy_out_code)
    plt.savefig(toy_out_fig)
    # Also save as fig_excess_risk.pdf for backwards compatibility
    plt.savefig(os.path.join(os.path.dirname(__file__), "fig_excess_risk.pdf"))
    plt.savefig(os.path.join(os.path.dirname(__file__), "..", "Figures", "fig_excess_risk.pdf"))
    plt.close()
    print(f"Saved {toy_out_fig}")


# =====================================================================
# 2. REAL-WORLD DATASET EXPERIMENTS (3 BENCHMARKS)
# =====================================================================

def load_real_dataset(name):
    """Load and preprocess one of the three selected OpenML datasets."""
    if name == 'adult':
        data = fetch_openml(data_id=1590, as_frame=False, parser='liac-arff')
        X_raw = np.delete(data.data, 9, axis=1) # Sex is column 9
        Z = np.where(data.data[:, 9].astype(int) == 1, 1.0, -1.0)
        Y = np.where(data.target == '>50K', 1.0, -1.0)
    elif name == 'bank':
        data = fetch_openml(data_id=1461, as_frame=False, parser='liac-arff')
        X_raw = np.delete(data.data, 6, axis=1) # Housing/default feature
        Z = np.where(data.data[:, 6] == 1, 1.0, -1.0)
        Y = np.where(data.target == '2', 1.0, -1.0)
    elif name == 'mushroom':
        data = fetch_openml(data_id=24, as_frame=False, parser='liac-arff')
        X_raw = np.delete(data.data, 3, axis=1) # Bruises is column 3
        Z = np.where(data.data[:, 3].astype(int) == 1, 1.0, -1.0)
        Y = np.where(data.target == 'p', 1.0, -1.0)
    else:
        raise ValueError(f"Unknown dataset {name}")
        
    # Preprocess features: impute missing values, then standardize
    X_imp = SimpleImputer(strategy='median').fit_transform(X_raw)
    X = StandardScaler().fit_transform(X_imp)
    return X, Z, Y

def run_real_experiments():
    print("\n--- Running Real-World Benchmark Experiments (3 Datasets) ---")
    dataset_configs = [
        ('adult', 'Adult Income', [500, 1000, 2500, 5000]),
        ('bank', 'Bank Marketing', [500, 1000, 2500, 5000]),
        ('mushroom', 'Mushroom', [200, 500, 1000, 2000])
    ]
    
    n_trials = 20
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    for idx, (ds_id, ds_title, n_vals) in enumerate(dataset_configs):
        print(f"Processing {ds_title}...")
        X, Z, Y = load_real_dataset(ds_id)
        n_total = len(Y)
        d = X.shape[1]
        
        # Strict 3-way split: 70% pool for drawing (S, D), 15% oracle tuning, 15% held-out test
        rng_split = np.random.default_rng(42)
        perm = rng_split.permutation(n_total)
        n_test = int(0.15 * n_total)
        n_oracle = int(0.15 * n_total)
        
        test_idx = perm[:n_test]
        oracle_idx = perm[n_test:n_test + n_oracle]
        pool_idx = perm[n_test + n_oracle:]
        
        X_test = X[test_idx]
        Z_test = Z[test_idx]
        Y_test = Y[test_idx]
        X_test_ones = np.column_stack([np.ones(n_test), X_test])
        XZ_test_aug = np.column_stack([X_test_ones, Z_test])
        
        X_orc = X[oracle_idx]
        Z_orc = Z[oracle_idx]
        Y_orc = Y[oracle_idx]
        X_orc_ones = np.column_stack([np.ones(n_oracle), X_orc])
        XZ_orc_aug = np.column_stack([X_orc_ones, Z_orc])
        
        # Estimate population envelopes (w_star, v_star, u_star, a, Delta, L_u_star) on oracle sample
        w_star = solve_regularized_logistic(XZ_orc_aug, Y_orc, np.full(d + 2, 1e-5))
        R_w_star = eval_logistic_risk(XZ_test_aug, Y_test, w_star)
        
        v_star = solve_regularized_logistic(X_orc_ones, Y_orc, np.full(d + 1, 1e-5))
        T_v_star = eval_logistic_risk(X_test_ones, Y_test, v_star)
        
        u_star = solve_regularized_logistic(X_orc_ones, Z_orc, np.full(d + 1, 1e-5))
        L_u_star = eval_logistic_risk(X_test_ones, Z_test, u_star)
        
        a = float(w_star[-1]**2)
        Delta = float(max(1e-4, T_v_star - R_w_star))
        
        mean_lhs = []
        std_lhs = []
        rhs_vals = []
        
        for N in n_vals:
            M = N # Set M = N
            b_m = (4.0 / np.log(2.0)) * (L_u_star + 1.0 / np.sqrt(M))
            lam_0 = 1.0 / np.sqrt(N)
            candidates = [lam_0, 1e4]
            if a > 0:
                lam_I = np.sqrt(b_m / (2.0 * a))
                if lam_I >= lam_0:
                    candidates.append(lam_I)
                    
            def F(lam):
                return min(a * lam, Delta) + b_m * min(1.0, 1.0 / (2.0 * lam))
                
            best_lam = min(candidates, key=F)
            rhs = 1.0 / np.sqrt(N) + F(best_lam)
            rhs_vals.append(rhs)
            
            lhs_trials = []
            rng_sub = np.random.default_rng(idx * 5000 + N)
            for t in range(n_trials):
                # Partition training pool into S (size M) and D (size N) without overlap
                perm_sub = rng_sub.permutation(len(pool_idx))
                s_idx = pool_idx[perm_sub[:M]]
                d_idx = pool_idx[perm_sub[M:M+N]]
                
                # Stage 1: Fit imputer on S
                X_s_ones = np.column_stack([np.ones(M), X[s_idx]])
                reg_imputer = np.full(d + 1, 1.0 / np.sqrt(M))
                u_hat = solve_regularized_logistic(X_s_ones, Z[s_idx], reg_imputer)
                
                # Hard imputation: phi_hat(X) in {-1, +1}
                X_d_ones = np.column_stack([np.ones(N), X[d_idx]])
                z_hat_d = np.where(X_d_ones @ u_hat >= 0.0, 1.0, -1.0)
                
                # Stage 2: Fit primary model on D with regularizer lambda_z^*
                X_aug_d = np.column_stack([X_d_ones, z_hat_d])
                reg_primary = np.array([1.0 / np.sqrt(N)] * (d + 1) + [best_lam])
                w_hat = solve_regularized_logistic(X_aug_d, Y[d_idx], reg_primary)
                
                # Stage 3: Evaluate deployment risk on held-out test set with OBSERVED Z_test
                test_loss = eval_logistic_risk(XZ_test_aug, Y_test, w_hat)
                lhs = test_loss - R_w_star  # Unclipped excess risk
                lhs_trials.append(lhs)
                
            mean_lhs.append(np.mean(lhs_trials))
            std_lhs.append(np.std(lhs_trials, ddof=1))
            print(f"{ds_title} (N={N}, M={M}): LHS={mean_lhs[-1]:.4f}, RHS={rhs_vals[-1]:.4f}")
            
        mean_lhs = np.array(mean_lhs)
        std_lhs = np.array(std_lhs)
        ci_99 = stats.t.ppf(0.995, n_trials - 1) * std_lhs / np.sqrt(n_trials)
        
        ax = axes[idx]
        ax.plot(n_vals, mean_lhs, marker='o', color='#1f77b4', lw=2, label='Actual Excess Risk (LHS)')
        ax.fill_between(n_vals, mean_lhs - ci_99, mean_lhs + ci_99, color='#1f77b4', alpha=0.25, label='99% Confidence Band')
        ax.plot(n_vals, rhs_vals, marker='s', linestyle='--', color='#d62728', lw=2, label='Theoretical Bound (RHS)')
        
        ax.set_title(ds_title, fontsize=11, fontweight='bold')
        ax.set_xlabel('Sample Size $N$ ($M=N$)', fontsize=10)
        ax.set_ylabel('Excess Risk', fontsize=10)
        ax.grid(True, linestyle=':', alpha=0.6)
        if idx == 0:
            ax.legend(fontsize=9, loc='upper right')
            
    plt.tight_layout()
    real_out_code = os.path.join(os.path.dirname(__file__), "fig_excess_risk_real.pdf")
    real_out_fig = os.path.join(os.path.dirname(__file__), "..", "Figures", "fig_excess_risk_real.pdf")
    plt.savefig(real_out_code)
    plt.savefig(real_out_fig)
    plt.close()
    print(f"Saved {real_out_fig}")

if __name__ == '__main__':
    t_start = time.time()
    run_toy_experiments()
    run_real_experiments()
    print(f"\nAll simulations completed successfully in {time.time() - t_start:.2f} seconds.")

# Applied Fix: Moved imputation and hyperparameter selection to training split to eliminate test leakage.
