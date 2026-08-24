"""
Generate fig4_qubo_matrix.png/.pdf — 4×4 Sudoku QUBO coefficient heatmap.

Run from repo root:
    python figures/plot_fig4_qubo_matrix.py
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "problem_formation_and_evaluation" / "qubo_construction"))
from qubo_generation import build_sudoku_qubo

OUT_PNG = Path(__file__).parent / "fig4_qubo_matrix.png"
OUT_PDF = Path(__file__).parent / "fig4_qubo_matrix.pdf"

# ---------------------------------------------------------------------------
# Build full 4×4 QUBO (no given reduction — all 64 vars)
# ---------------------------------------------------------------------------

N = 4
Q, _, _, _ = build_sudoku_qubo(N, box_size=2, givens=None)
n_vars = N ** 3   # 64

# Upper-triangular view; zero entries become NaN so they render white
Q_ut = np.triu(Q).astype(float)
Q_vis = Q_ut.copy()
Q_vis[Q_vis == 0] = np.nan

# Sparsity (same formula as print_qubo_stats)
nonzero = np.count_nonzero(np.diag(Q)) + np.count_nonzero(np.triu(Q, k=1))
sparsity = 100.0 * (1.0 - nonzero / n_vars ** 2)

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(7, 6.5))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

vmax = np.nanmax(np.abs(Q_vis))
im = ax.imshow(
    Q_vis, cmap="RdBu_r", vmin=-vmax, vmax=vmax,
    aspect="equal", interpolation="nearest", origin="upper",
)

# Grid lines at 16-var boundaries (one per Sudoku row)
for t in range(0, n_vars + 1, N * N):
    ax.axhline(t - 0.5, color="#444444", linewidth=0.9)
    ax.axvline(t - 0.5, color="#444444", linewidth=0.9)

cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("QUBO Coefficient", fontsize=11)

ticks = list(range(0, n_vars + 1, N * N))
ax.set_xticks(ticks)
ax.set_yticks(ticks)
ax.tick_params(labelsize=10)
ax.set_xlabel("Variable Index", fontsize=12)
ax.set_ylabel("Variable Index", fontsize=12)

ax.set_title(f"Coefficient Heatmap  (Sparsity: {sparsity:.1f}%)",
             fontsize=11, pad=6)
fig.suptitle(f"4×4 Sudoku QUBO Matrix  ({n_vars}×{n_vars})",
             fontsize=13, fontweight="bold")

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight", facecolor="white")
plt.savefig(OUT_PDF, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Saved {OUT_PNG}")
print(f"Saved {OUT_PDF}")
