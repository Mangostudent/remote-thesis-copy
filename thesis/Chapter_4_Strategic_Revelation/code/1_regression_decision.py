"""
Experiment 1: Regression Decision Problem
Two-panel parameter sweep heatmap of strategic advantage Delta*(q)
for q=0.15 vs q=0.85, with Theorem 1 (sufficiency) and Theorem 2
(necessity) boundary contour overlays.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
from scipy.ndimage import gaussian_filter
from pathlib import Path
from matplotlib.lines import Line2D

import random

GLOBAL_SEED = 42
np.random.seed(GLOBAL_SEED)
random.seed(GLOBAL_SEED)

local_figures = Path(__file__).resolve().parent.parent / "figures"
local_figures.mkdir(parents=True, exist_ok=True)
out_paths = [local_figures / "regression_decision_sweep.png", local_figures / "regression_decision_sweep.pdf"]

print("Running 2-Panel Regression Decision Sweep (q=0.15 vs q=0.85)...")


class GaussianDistribution:
    """Joint Gaussian distribution of (X, U, Y)."""
    def __init__(self, var_x=1.0, var_u=1.0, var_y=1.0, cov_xu=0.1, cov_xy=0.0, cov_uy=0.0):
        self.var_x = var_x
        self.var_u = var_u
        self.var_y = var_y
        self.cov_xu = cov_xu
        self.cov_xy = cov_xy
        self.cov_uy = cov_uy
        self.sigma = np.array([
            [self.var_y, self.cov_xy, self.cov_uy],
            [self.cov_xy, self.var_x, self.cov_xu],
            [self.cov_uy, self.cov_xu, self.var_u]
        ])

    def is_valid(self):
        """Checks positive semi-definiteness of the covariance matrix."""
        try:
            return np.min(np.linalg.eigvalsh(self.sigma)) > 1e-8
        except np.linalg.LinAlgError:
            return False


class RegressionGame:
    """Disclosure game logic for the regression decision problem."""
    def __init__(self, distribution, q, Z_samples):
        self.dist = distribution
        self.q = q
        self.Z_samples = Z_samples
        self._cached_rv = None
        self._cached_rs = None

    def calculate_vanilla_risk(self):
        """R_V* = Var(Y) - (1-q) * Var(b_V * X)."""
        b_y = self.dist.cov_xy / self.dist.var_x
        var_by_x = (b_y**2) * self.dist.var_x
        self._cached_rv = self.dist.var_y - (1.0 - self.q) * var_by_x
        return self._cached_rv

    def calculate_strategic_risk(self):
        """R_S* via scalar optimization over b using common random numbers."""
        samples = self.Z_samples @ np.linalg.cholesky(self.dist.sigma).T
        Y, X, U = samples[:, 0], samples[:, 1], samples[:, 2]

        def objective(b):
            f = (2.0 * U - b * X) * (b * X)
            g = (2.0 * Y - b * X) * (b * X)
            return self.dist.var_y - (1.0 - self.q) * np.mean(g * (f > 0))

        res = minimize_scalar(objective, bounds=(-5.0, 5.0), method='bounded')
        self._cached_rs = res.fun
        return self._cached_rs

    @property
    def strategic_advantage(self):
        rv = self._cached_rv if self._cached_rv is not None else self.calculate_vanilla_risk()
        rs = self._cached_rs if self._cached_rs is not None else self.calculate_strategic_risk()
        return rv - rs

    def calculate_theoretical_margins(self):
        """
        Returns (suff_margin, nec_margin):
        - suff_margin: Theorem 1 sufficiency (positive => condition holds)
        - nec_margin:  Theorem 2 necessity (positive => condition holds)
        """
        samples = self.Z_samples @ np.linalg.cholesky(self.dist.sigma).T
        Y, X, U = samples[:, 0], samples[:, 1], samples[:, 2]

        b_y = self.dist.cov_xy / self.dist.var_x
        var_by_x = (b_y**2) * self.dist.var_x
        lhs = np.sqrt(max(0.0, self.dist.var_u + self.dist.var_y - 2.0 * self.dist.cov_uy))

        if abs(b_y) < 1e-4:
            return -lhs, -1.0

        b_cands = np.linspace(-5.0, 5.0, 101)
        bX = np.outer(X, b_cands)
        G = (2.0 * Y[:, None] - bX) * bX
        v_diff = ((b_cands - b_y)**2) * self.dist.var_x
        num = np.mean(np.abs(G), axis=0) - var_by_x - v_diff

        nec_margin = np.max(num)

        # Scalar denominator for the dashed sufficiency contour
        den = 4.0 * np.sqrt(var_by_x + 1e-9)
        rhs_vals = num / den
        max_rhs = np.max(rhs_vals)
        suff_margin = max_rhs - lhs

        return suff_margin, nec_margin


grid_size = 40
uy_range = np.linspace(-1.0, 1.0, grid_size)
xy_range = np.linspace(-1.0, 1.0, grid_size)
cov_xu = 0.1
q_values = [0.15, 0.85]
n_samples = 100000

Z = np.random.normal(0, 1, (n_samples, 3))
X_grid, Y_grid = np.meshgrid(uy_range, xy_range)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for idx, q_val in enumerate(q_values):
    ax = axes[idx]
    delta_map = np.zeros((grid_size, grid_size))
    suff_map = np.zeros((grid_size, grid_size))
    nec_map = np.zeros((grid_size, grid_size))
    valid_mask = np.zeros((grid_size, grid_size), dtype=bool)

    for i, c_xy in enumerate(xy_range):
        for j, c_uy in enumerate(uy_range):
            dist = GaussianDistribution(cov_xu=cov_xu, cov_xy=c_xy, cov_uy=c_uy)
            if not dist.is_valid():
                continue

            valid_mask[i, j] = True
            game = RegressionGame(dist, q_val, Z)
            delta_map[i, j] = game.strategic_advantage
            s_m, n_m = game.calculate_theoretical_margins()
            suff_map[i, j] = s_m
            nec_map[i, j] = n_m

    delta_masked = np.ma.masked_where(~valid_mask, delta_map)
    limit = max(0.15, np.abs(delta_masked).max())

    im = ax.imshow(delta_masked, extent=[uy_range[0], uy_range[-1], xy_range[0], xy_range[-1]],
                   origin='lower', cmap='RdBu_r', vmin=-limit, vmax=limit,
                   interpolation='bilinear')

    cb = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label(fr'Strategic Advantage $\Delta^\star({q_val})$', fontsize=11)

    ax.contour(X_grid, Y_grid, valid_mask.astype(float), [0.5],
               colors='#cccccc', linewidths=1.2)

    if np.nanmin(np.where(valid_mask, nec_map, np.nan)) > 0:
        ax.contour(X_grid, Y_grid, valid_mask.astype(float), [0.5], colors='black',
                   linestyles='-', linewidths=2.2, alpha=0.9)
    else:
        try:
            smoothed_nec = gaussian_filter(nec_map, sigma=2.0)
            smoothed_nec[~valid_mask] = np.nan
            ax.contour(X_grid, Y_grid, smoothed_nec, levels=[0.0], colors='black',
                       linestyles='-', linewidths=2.2, alpha=0.9)
        except Exception:
            pass

    if np.any(suff_map > 0):
        try:
            smoothed_suff = gaussian_filter(suff_map, sigma=2.0)
            smoothed_suff[~valid_mask] = np.nan
            ax.contour(X_grid, Y_grid, smoothed_suff, levels=[0.0], colors='black',
                       linestyles='--', linewidths=2.5, alpha=0.9)
        except Exception:
            pass

    custom_lines = [
        Line2D([0], [0], color='black', lw=2.2, linestyle='-'),
        Line2D([0], [0], color='black', lw=2.5, linestyle='--')
    ]
    ax.legend(custom_lines, ['Theoretical Necessity (Thm. 2)', 'Theoretical Sufficiency (Thm. 1)'],
              loc='upper right', framealpha=0.9, fontsize=9.0)

    ax.set_xlabel(r'Cov$(U,Y)$', fontsize=12)
    ax.set_ylabel(r'Cov$(X,Y)$', fontsize=12)
    ax.set_title(fr'Strategic Advantage at Noise $q = {q_val}$ ($\mathrm{{Cov}}(X,U)={cov_xu}$)', fontsize=13, pad=12)

plt.suptitle(r'Regression Strategic Advantage $\Delta^\star(q)$ Heatmaps under Channel Noise Comparison', fontsize=15, y=0.98)
plt.tight_layout()

for path in out_paths:
    plt.savefig(path, dpi=300, bbox_inches='tight')
    print(f"Saved 2-panel upgraded plot to {path}")

plt.close()
print("Regression Decision 2-panel sweep complete!")

# Applied Fix: Corrected sufficient-condition denominator to 4*sqrt(Var(bX)).
