"""
Generate fig3_compression.png — 3D mini-cube visualization of QUBO variable reduction.

Left  (large): 9×9×9 voxel grid, 3 colors:
               free vars (blue), given/fixed digit (gold), eliminated wrong-digit (gray)
Right (small): proportionally-scaled solid cube of mini-cubes, all free-var blue

Run from repo root:
    python figures/plot_fig3_compression.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pathlib import Path
from PIL import Image

OUT = Path(__file__).parent / "fig3_compression.png"
OUT_PDF = Path(__file__).parent / "fig3_compression.pdf"

# 9×9 easy puzzle (30 givens)
PUZZLE = np.array([
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
N = 9

N_BEFORE = N ** 3
N_GIVEN  = int(np.sum(PUZZLE != 0))
N_FREE   = int(np.sum(PUZZLE == 0)) * N
N_FIXED  = N_GIVEN
N_ELIM   = N_GIVEN * (N - 1)
N_AFTER  = N_FREE

FREE_RGBA  = np.array([0.00, 0.51, 0.79, 0.88])
FIXED_RGBA = np.array([0.91, 0.66, 0.22, 0.95])
ELIM_RGBA  = np.array([0.55, 0.65, 0.75, 0.45])

FREE_HEX  = "#0082CA"
FIXED_HEX = "#E8A938"
ELIM_HEX  = "#8EABC9"

# Small cube dimensions
S_SMALL = N * (N_AFTER / N_BEFORE) ** (1 / 3)
GAP     = 2.5
N_DIV   = 8   # mini-cube divisions for small cube

# ---------------------------------------------------------------------------
# Build voxel arrays for large cube
# ---------------------------------------------------------------------------
filled     = np.ones((N, N, N), dtype=bool)
facecolors = np.zeros((N, N, N, 4))

for i in range(N):
    for j in range(N):
        g = PUZZLE[i, j]
        if g == 0:
            facecolors[i, j, :] = FREE_RGBA
        else:
            for k in range(N):
                facecolors[i, j, k] = FIXED_RGBA if k == g - 1 else ELIM_RGBA

# ---------------------------------------------------------------------------
# Small cube: draw as N_DIV × N_DIV × N_DIV exterior mini-cube faces
# ---------------------------------------------------------------------------
x0 = N + GAP
y0 = (N - S_SMALL) / 2
z0 = (N - S_SMALL) / 2
unit = S_SMALL / N_DIV


def mini_cube_exterior_faces(ox, oy, oz, sz, n):
    """Return all exterior face polygons for an n×n×n grid of mini-cubes."""
    u = sz / n
    faces = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                cx, cy, cz = ox + i*u, oy + j*u, oz + k*u
                v = [
                    [cx,   cy,   cz  ], [cx+u, cy,   cz  ],
                    [cx+u, cy+u, cz  ], [cx,   cy+u, cz  ],
                    [cx,   cy,   cz+u], [cx+u, cy,   cz+u],
                    [cx+u, cy+u, cz+u], [cx,   cy+u, cz+u],
                ]
                if i == 0:   faces.append([v[0], v[3], v[7], v[4]])
                if i == n-1: faces.append([v[1], v[2], v[6], v[5]])
                if j == 0:   faces.append([v[0], v[1], v[5], v[4]])
                if j == n-1: faces.append([v[2], v[3], v[7], v[6]])
                if k == 0:   faces.append([v[0], v[1], v[2], v[3]])
                if k == n-1: faces.append([v[4], v[5], v[6], v[7]])
    return faces

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(20, 10))
fig.patch.set_facecolor("white")

ax = fig.add_axes([-0.05, -0.12, 1.10, 1.10], projection="3d")
ax.set_facecolor("white")

# Large cube — voxels
ax.voxels(filled, facecolors=facecolors, edgecolor="white", linewidth=0.15)

# Small cube — mini-cube exterior faces
small_faces = mini_cube_exterior_faces(x0, y0, z0, S_SMALL, N_DIV)
ax.add_collection3d(Poly3DCollection(
    small_faces,
    facecolor=FREE_HEX, edgecolor="white",
    linewidth=0.35, alpha=0.88,
))

# Axis limits — tight around geometry so cubes fill the frame
pad = 0.15
ax.set_xlim(-pad, x0 + S_SMALL + pad)
ax.set_ylim(-pad, N + pad)
ax.set_zlim(-pad, N + pad)
ax.set_box_aspect([x0 + S_SMALL + 2*pad, N + 2*pad, N + 2*pad])
ax.set_axis_off()
ax.dist = 4.8   # zoom in (default ~10)

# Legend
fig.legend(
    handles=[
        mpatches.Patch(facecolor=FREE_HEX,  edgecolor="#aaa", label=f"Free variable  ({N_FREE})"),
        mpatches.Patch(facecolor=FIXED_HEX, edgecolor="#aaa", label=f"Given — correct digit  ({N_FIXED})"),
        mpatches.Patch(facecolor=ELIM_HEX,  edgecolor="#aaa", label=f"Eliminated — wrong digit  ({N_ELIM})"),
    ],
    loc="lower center", bbox_to_anchor=(0.5, 0.01),
    ncol=3, fontsize=16, framealpha=0.9,
)

ax.view_init(elev=18, azim=-48)

fig.suptitle(
    "QUBO Variable Reduction via Given-Cell Elimination\n"
    f"9×9 Easy Sudoku  •  {N_GIVEN} givens fixed  •  "
    f"{N_ELIM + N_FIXED} of {N_BEFORE} variables eliminated",
    fontsize=20, fontweight="bold", x=0.5, y=0.94,
)

plt.savefig(OUT, dpi=300, bbox_inches="tight", facecolor="white")
plt.savefig(OUT_PDF, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Saved {OUT_PDF}")

# Auto-crop internal 3D-axes whitespace down to actual content
img  = Image.open(OUT).convert("RGB")
arr  = np.array(img)
mask = arr.mean(axis=2) < 253          # non-white pixels
rows = np.where(mask.any(axis=1))[0]
cols = np.where(mask.any(axis=0))[0]
pad  = 18                               # px breathing room
r0, r1 = max(rows[0]  - pad, 0), min(rows[-1]  + pad, arr.shape[0])
c0, c1 = max(cols[0]  - pad, 0), min(cols[-1]  + pad, arr.shape[1])
Image.fromarray(arr[r0:r1, c0:c1]).save(OUT)

print(f"Saved {OUT}")
