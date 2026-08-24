"""
Generate fig1_sudoku_puzzles.png/.pdf — Sudoku Test Puzzles panel.

Run from repo root:
    python figures/plot_fig1_puzzles.py
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

OUT_PNG = Path(__file__).parent / "fig1_sudoku_puzzles.png"
OUT_PDF = Path(__file__).parent / "fig1_sudoku_puzzles.pdf"

# ---------------------------------------------------------------------------
# Puzzles
# ---------------------------------------------------------------------------

# hard_1 from QPU experiments — 4 givens, 12 free cells → 48 free vars
PUZZLE_4x4 = np.array([
    [0, 2, 0, 0],
    [0, 0, 0, 3],
    [2, 0, 0, 0],
    [0, 0, 4, 0],
])

# Classic 9×9 easy — 30 givens → 459 free vars
PUZZLE_9x9_EASY = np.array([
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
])

# Gordon Royle 17-clue puzzle — 17 givens → 576 free vars
PUZZLE_9x9_HARD = np.array([
    [0, 0, 0, 0, 0, 0, 0, 1, 0],
    [4, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 5, 0, 4, 0, 7],
    [0, 0, 8, 0, 0, 0, 3, 0, 0],
    [0, 0, 1, 0, 9, 0, 0, 0, 0],
    [3, 0, 0, 4, 0, 0, 2, 0, 0],
    [0, 5, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 8, 0, 6, 0, 0, 0],
])

GIVEN_COLOR = "#AED6F1"
FREE_COLOR  = "white"
BOX_EDGE    = "#222222"
CELL_EDGE   = "#999999"
NUM_COLOR   = "#1a3a5c"

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def draw_puzzle(ax, puzzle, box_size, title, caption, num_size=16):
    N = puzzle.shape[0]
    ax.set_xlim(0, N)
    ax.set_ylim(-1.0, N)
    ax.set_aspect("equal")
    ax.axis("off")

    for i in range(N):
        for j in range(N):
            val = puzzle[i, j]
            ry  = N - 1 - i
            fc  = GIVEN_COLOR if val != 0 else FREE_COLOR
            ax.add_patch(plt.Rectangle(
                [j, ry], 1, 1,
                facecolor=fc, edgecolor=CELL_EDGE, linewidth=0.7,
            ))
            if val != 0:
                ax.text(j + 0.5, ry + 0.5, str(val),
                        ha="center", va="center",
                        fontsize=num_size, fontweight="bold", color=NUM_COLOR)

    boxes = N // box_size
    for br in range(boxes):
        for bc in range(boxes):
            ax.add_patch(plt.Rectangle(
                [bc * box_size, br * box_size], box_size, box_size,
                fill=False, edgecolor=BOX_EDGE, linewidth=2.2, zorder=2,
            ))

    ax.set_title(title, fontsize=11, fontweight="bold", pad=8, linespacing=1.5)
    ax.text(N / 2, -0.55, caption,
            ha="center", va="top", fontsize=9, color="#555555", style="italic")

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------

fig, axes = plt.subplots(
    1, 3, figsize=(14, 6),
    gridspec_kw={"width_ratios": [4, 9, 9]},
)
fig.patch.set_facecolor("white")

n4  = int(np.sum(PUZZLE_4x4       != 0))
n9e = int(np.sum(PUZZLE_9x9_EASY  != 0))
n9h = int(np.sum(PUZZLE_9x9_HARD  != 0))

draw_puzzle(axes[0], PUZZLE_4x4, 2,
            "4×4 Puzzle\n(Baseline — 64 vars)",
            f"{n4} givens  →  {(4*4 - n4)*4} free variables",
            num_size=20)

draw_puzzle(axes[1], PUZZLE_9x9_EASY, 3,
            f"9×9 Easy  ({n9e} givens)\n{(81 - n9e)*9} free variables",
            f"{n9e} givens  →  {(81 - n9e)*9} free variables",
            num_size=13)

draw_puzzle(axes[2], PUZZLE_9x9_HARD, 3,
            f"9×9 Hard  ({n9h} givens)\n{(81 - n9h)*9} free variables",
            f"{n9h} givens  →  {(81 - n9h)*9} free variables",
            num_size=13)

fig.suptitle("Sudoku Test Puzzles Used in Experiments",
             fontsize=14, fontweight="bold", y=1.01)

plt.tight_layout(pad=1.5)
plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight", facecolor="white")
plt.savefig(OUT_PDF, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Saved {OUT_PNG}")
print(f"Saved {OUT_PDF}")
