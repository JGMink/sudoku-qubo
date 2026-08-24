"""
Generate QPU result figures from sudoku_summary.csv.

Produces:
  figures/fig5_comparison_table.png  — replaces old hybrid vs SA table
  figures/fig6_valid_rate.png        — bar chart: QPU vs SA by difficulty

Run from repo root:
    python figures/plot_qpu_results.py
"""

import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict
from pathlib import Path

HERE     = Path(__file__).parent
CSV_PATH = HERE.parent / "qpu_experiments" / "sudoku_summary.csv"

# Qubit counts observed during solve (from console output)
QUBIT_RANGES = {"easy": "16–17", "medium": "46–47", "hard": "99–117"}

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

rows = []
with open(CSV_PATH) as f:
    for r in csv.DictReader(f):
        diff = r["puzzle"].split("_")[1]   # easy | medium | hard
        rows.append({
            "puzzle":          r["puzzle"],
            "difficulty":      diff,
            "n_givens":        int(r["n_givens"]),
            "n_free_vars":     int(r["n_free_vars"]),
            "sa_valid_pct":    float(r["sa_valid_pct"]),
            "qpu_valid_pct":   float(r["qpu_valid_pct"]),
            "chain_break_pct": float(r["chain_break_pct"]),
        })

by_diff = defaultdict(list)
for r in rows:
    by_diff[r["difficulty"]].append(r)

DIFFS = ["easy", "medium", "hard"]

# ---------------------------------------------------------------------------
# Fig 5 — results table (replaces old hybrid vs SA table)
# ---------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 3.4))
ax.axis("off")
fig.patch.set_facecolor("white")

col_labels = ["Difficulty", "Givens", "Free Vars", "Qubits",
              "SA Opt %", "QPU Opt %", "QPU ±Std"]

table_data = []
for diff in DIFFS:
    group    = by_diff[diff]
    givens   = group[0]["n_givens"]
    free     = group[0]["n_free_vars"]
    sa_avg   = np.mean([r["sa_valid_pct"]  for r in group])
    qpu_vals = [r["qpu_valid_pct"] for r in group]
    qpu_avg  = np.mean(qpu_vals)
    qpu_std  = np.std(qpu_vals)
    table_data.append([
        diff.capitalize(),
        str(givens),
        str(free),
        QUBIT_RANGES[diff],
        f"{sa_avg:.1f}%",
        f"{qpu_avg:.1f}%",
        f"±{qpu_std:.1f}%",
    ])

tbl = ax.table(
    cellText=[col_labels] + table_data,
    loc="center",
    cellLoc="center",
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(11)
tbl.scale(1, 2.0)

# Style header row
for col in range(len(col_labels)):
    cell = tbl[0, col]
    cell.set_facecolor("#1a1a2e")
    cell.set_text_props(color="white", fontweight="bold")

# Style data rows
row_colors = {"Easy": "#f0f9f0", "Medium": "#fff9f0", "Hard": "#fff0f0"}
qpu_good   = "#c8e6c9"   # green  ≥ 95%
qpu_warn   = "#fff9c4"   # yellow 80–95%
qpu_bad    = "#ffcdd2"   # red    < 80%

for i, diff in enumerate(DIFFS):
    data_row = i + 1
    group     = by_diff[diff]
    qpu_avg   = np.mean([r["qpu_valid_pct"] for r in group])
    base_col  = row_colors[diff.capitalize()]

    for col in range(len(col_labels)):
        cell = tbl[data_row, col]
        cell.set_facecolor(base_col)
        cell.set_edgecolor("#cccccc")

    # Color the QPU Valid % cell
    qpu_col = 5
    if qpu_avg >= 95:
        tbl[data_row, qpu_col].set_facecolor(qpu_good)
    elif qpu_avg >= 80:
        tbl[data_row, qpu_col].set_facecolor(qpu_warn)
    else:
        tbl[data_row, qpu_col].set_facecolor(qpu_bad)

ax.set_title(
    "D-Wave Advantage2 QPU vs. Simulated Annealing  —  4×4 Sudoku\n"
    "Forward Annealing  •  1,000 reads  •  200 µs  •  4 puzzles per difficulty",
    fontsize=12, fontweight="bold", pad=14,
)

out5     = HERE / "fig5_comparison_table.png"
out5_pdf = HERE / "fig5_comparison_table.pdf"
plt.savefig(out5,     dpi=300, bbox_inches="tight", facecolor="white")
plt.savefig(out5_pdf, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Saved {out5}")
print(f"Saved {out5_pdf}")

# ---------------------------------------------------------------------------
# Fig 6 — bar chart: QPU valid rate by difficulty, SA baseline
# ---------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

x      = np.arange(len(DIFFS))
width  = 0.32

sa_means  = [np.mean([r["sa_valid_pct"]  for r in by_diff[d]]) for d in DIFFS]
qpu_means = [np.mean([r["qpu_valid_pct"] for r in by_diff[d]]) for d in DIFFS]
qpu_stds  = [np.std( [r["qpu_valid_pct"] for r in by_diff[d]]) for d in DIFFS]
sa_stds   = [np.std( [r["sa_valid_pct"]  for r in by_diff[d]]) for d in DIFFS]

QPU_BLUE = "#0082CA"
SA_GRAY  = "#9E9E9E"

bars_sa  = ax.bar(x - width/2, sa_means,  width, yerr=sa_stds,
                  color=SA_GRAY,  alpha=0.85, capsize=5,
                  error_kw={"elinewidth": 1.5}, label="Simulated Annealing")
bars_qpu = ax.bar(x + width/2, qpu_means, width, yerr=qpu_stds,
                  color=QPU_BLUE, alpha=0.90, capsize=5,
                  error_kw={"elinewidth": 1.5}, label="QPU (Advantage2)")

# Value labels on QPU bars
for bar, mean, std in zip(bars_qpu, qpu_means, qpu_stds):
    label = f"{mean:.1f}%"
    ypos  = bar.get_height() + (std if std > 0 else 0) + 1.5
    ax.text(bar.get_x() + bar.get_width() / 2, ypos,
            label, ha="center", va="bottom", fontsize=10, fontweight="bold",
            color=QPU_BLUE)

# Per-puzzle scatter dots on QPU bars
for i, diff in enumerate(DIFFS):
    vals = [r["qpu_valid_pct"] for r in by_diff[diff]]
    ax.scatter([x[i] + width/2] * len(vals), vals,
               color="white", edgecolors=QPU_BLUE, s=30, zorder=5, linewidths=1.2)

ax.axhline(100, color="#444444", linewidth=0.8, linestyle="--", alpha=0.5)

ax.set_xticks(x)
ax.set_xticklabels([d.capitalize() for d in DIFFS], fontsize=13)
ax.set_xlabel("Puzzle Difficulty", fontsize=12)
ax.set_ylabel("Optimal Solution Rate (%)", fontsize=12)
ax.set_ylim(0, 115)
ax.set_yticks(range(0, 101, 20))
ax.tick_params(axis="both", labelsize=11)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.legend(fontsize=11, framealpha=0.9,
          loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)

ax.set_title(
    "QPU Valid Solution Rate vs. Puzzle Difficulty\n"
    "D-Wave Advantage2  •  4×4 Sudoku  •  Forward Annealing  •  1,000 reads",
    fontsize=12, fontweight="bold",
)

# Annotate qubit counts below x tick labels
tick_labels = [f"{d.capitalize()}\n({QUBIT_RANGES[d]} qubits)" for d in DIFFS]
ax.set_xticklabels(tick_labels, fontsize=11)

out6 = HERE / "fig6_valid_rate.png"
plt.savefig(out6, dpi=150, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Saved {out6}")
