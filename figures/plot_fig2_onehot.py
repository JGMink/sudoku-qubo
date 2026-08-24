"""
Recreate fig2_onehot_matrix.png — One-Hot Encoding visualization.

Run from repo root:
    python figures/plot_fig2_onehot.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import ConnectionPatch
from pathlib import Path

OUT_PNG = Path(__file__).parent / "fig2_onehot_matrix.png"
OUT_PDF = Path(__file__).parent / "fig2_onehot_matrix.pdf"

# hard_1 puzzle (0 = blank)
PUZZLE = np.array([
    [0, 2, 0, 0],
    [0, 0, 0, 3],
    [2, 0, 0, 0],
    [0, 0, 4, 0],
])
N = 4

# Build encoding matrix (16 rows × 4 cols)
# 0 = free, -1 = eliminated, 1 = fixed
enc = np.zeros((N * N, N), dtype=int)
for i in range(N):
    for j in range(N):
        g = PUZZLE[i, j]
        if g != 0:
            for k in range(N):
                enc[i * N + j, k] = 1 if k == g - 1 else -1

FREE_C  = "#AED6F1"
ELIM_C  = "#D5D8DC"
FIXED_C = "#1A5276"

n_free  = int(np.sum(enc == 0))
n_elim  = int(np.sum(enc == -1))
n_fixed = int(np.sum(enc == 1))

# ---------------------------------------------------------------------------
# Figure layout — both axes share the same vertical span
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(14, 6.5))
fig.patch.set_facecolor("white")

ax_p = fig.add_axes([0.04, 0.10, 0.26, 0.80])
ax_p.set_xlim(0, N)
ax_p.set_ylim(0, N)
ax_p.set_aspect("equal")
ax_p.axis("off")
ax_p.set_title("4×4 Puzzle", fontsize=12, fontweight="bold", pad=10)

ax_m = fig.add_axes([0.37, 0.10, 0.53, 0.80])
ax_m.set_xlim(-0.5, N + 1.2)
ax_m.set_ylim(-0.5, N * N - 0.5)
ax_m.axis("off")
fig.text(0.56, 0.91, "16×4 Encoding Matrix  (64 binary variables)",
         ha="center", fontsize=11, fontweight="bold")

# ---------------------------------------------------------------------------
# Draw puzzle grid
# ---------------------------------------------------------------------------
for i in range(N):
    for j in range(N):
        val = PUZZLE[i, j]
        ry  = N - 1 - i
        fc  = "#F9E79F" if val != 0 else "white"
        ax_p.add_patch(plt.Rectangle([j, ry], 1, 1,
                       facecolor=fc, edgecolor="#888888", linewidth=1.2))
        if val != 0:
            ax_p.text(j + 0.5, ry + 0.5, str(val),
                      ha="center", va="center", fontsize=18,
                      fontweight="bold", color="#333333")
        else:
            ax_p.text(j + 0.5, ry + 0.5, "?",
                      ha="center", va="center", fontsize=12, color="#aaaaaa")

for br in range(2):
    for bc in range(2):
        ax_p.add_patch(plt.Rectangle([bc * 2, br * 2], 2, 2,
                       fill=False, edgecolor="#333333", linewidth=2.2))

ax_p.legend(
    handles=[
        mpatches.Patch(facecolor="#F9E79F", edgecolor="#888888", label="Given clue"),
        mpatches.Patch(facecolor="white",   edgecolor="#888888", label="Free cell"),
    ],
    loc="lower center", bbox_to_anchor=(0.5, -0.10),
    fontsize=9, ncol=2, framealpha=0.9,
)

# ---------------------------------------------------------------------------
# Draw encoding matrix
# ---------------------------------------------------------------------------
for row_idx in range(N * N):
    mat_y = N * N - 1 - row_idx

    for k in range(N):
        v  = enc[row_idx, k]
        fc = FREE_C if v == 0 else (FIXED_C if v == 1 else ELIM_C)
        ax_m.add_patch(plt.Rectangle(
            [k - 0.5, mat_y - 0.5], 1, 1,
            facecolor=fc, edgecolor="white", linewidth=0.8,
        ))

    cell_r = row_idx // N
    cell_c = row_idx % N
    ax_m.text(N - 0.5 + 0.25, mat_y,
              f"({cell_r+1},{cell_c+1})",
              ha="left", va="center", fontsize=8.5, color="#444444")

for k in range(N):
    ax_m.text(k, -0.5 - 0.45, f"d={k+1}",
              ha="center", va="top", fontsize=10, fontweight="bold")

# ---------------------------------------------------------------------------
# Connecting lines
# ---------------------------------------------------------------------------
for i in range(N):
    for j in range(N):
        row_idx = i * N + j
        mat_y   = N * N - 1 - row_idx
        puz_y   = N - 1 - i + 0.5

        fig.add_artist(ConnectionPatch(
            xyA=(j + 1.0, puz_y), xyB=(-0.5, mat_y),
            coordsA="data", coordsB="data",
            axesA=ax_p, axesB=ax_m,
            color="#BBBBBB", linewidth=0.5, alpha=0.6,
        ))

# ---------------------------------------------------------------------------
# Title + bottom legend
# ---------------------------------------------------------------------------
fig.suptitle("One-Hot Encoding: Each Sudoku Cell Becomes N Binary Variables",
             fontsize=13, fontweight="bold", x=0.47, y=0.98)

fig.legend(
    handles=[
        mpatches.Patch(facecolor=FREE_C,  edgecolor="#888888",
                       label=f"Free variable  ({n_free} vars)"),
        mpatches.Patch(facecolor=ELIM_C,  edgecolor="#888888",
                       label=f"Eliminated  ({n_elim} vars, given ≠ digit)"),
        mpatches.Patch(facecolor=FIXED_C, edgecolor="#888888",
                       label=f"Fixed = 1  ({n_fixed} vars, given = digit)"),
    ],
    loc="lower center", bbox_to_anchor=(0.58, 0.0),
    fontsize=9, ncol=3, framealpha=0.9,
)

plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight", facecolor="white")
plt.savefig(OUT_PDF, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Saved {OUT_PNG}")
print(f"Saved {OUT_PDF}")
