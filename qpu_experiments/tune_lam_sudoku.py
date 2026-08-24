"""
LAM penalty weight sweep for 4x4 Sudoku QUBO.

Sweeps LAM values across all 12 puzzles using SimulatedAnnealingSampler to find
the optimal QUBO penalty weight before QPU runs.

Output: qpu_experiments/lam_tuning/lam_sweep.csv + lam_summary.json

Self-contained: no imports from other files in this repo.

Usage:
    python qpu_experiments/tune_lam_sudoku.py
"""

import csv
import json
import time
from collections import defaultdict
from pathlib import Path

import dimod
from dimod import BinaryQuadraticModel

try:
    from dwave.samplers import SimulatedAnnealingSampler
except ImportError:
    try:
        from neal import SimulatedAnnealingSampler
    except ImportError:
        from dimod.reference.samplers import SimulatedAnnealingSampler

# ---------------------------------------------------------------------------
# Puzzle definitions (same as compute_gs_sudoku.py)
# ---------------------------------------------------------------------------

PUZZLES_4x4 = {
    # EASY — 12 givens, 4 blank cells
    "easy_1": [
        [3, 2, 1, 0],
        [4, 1, 2, 0],
        [2, 4, 0, 1],
        [0, 3, 4, 2],
    ],
    "easy_2": [
        [1, 2, 3, 0],
        [3, 4, 0, 2],
        [2, 0, 4, 3],
        [0, 3, 2, 1],
    ],
    "easy_3": [
        [2, 3, 4, 0],
        [4, 1, 0, 3],
        [3, 0, 1, 2],
        [0, 2, 3, 4],
    ],
    "easy_4": [
        [4, 1, 2, 0],
        [2, 3, 0, 1],
        [1, 0, 3, 2],
        [0, 2, 1, 4],
    ],
    # MEDIUM — 8 givens, 8 blank cells
    "medium_1": [
        [3, 2, 0, 0],
        [4, 0, 0, 3],
        [2, 0, 3, 0],
        [0, 0, 4, 2],
    ],
    "medium_2": [
        [1, 0, 0, 4],
        [0, 4, 1, 0],
        [2, 0, 0, 3],
        [0, 3, 2, 0],
    ],
    "medium_3": [
        [2, 0, 0, 1],
        [0, 1, 2, 0],
        [3, 0, 0, 2],
        [0, 2, 3, 0],
    ],
    "medium_4": [
        [4, 0, 0, 3],
        [0, 3, 4, 0],
        [1, 0, 0, 2],
        [0, 2, 1, 0],
    ],
    # HARD — 4 givens, 12 blank cells
    "hard_1": [
        [0, 2, 0, 0],
        [0, 0, 0, 3],
        [2, 0, 0, 0],
        [0, 0, 4, 0],
    ],
    "hard_2": [
        [1, 0, 0, 0],
        [0, 0, 0, 2],
        [0, 0, 4, 0],
        [0, 3, 0, 0],
    ],
    "hard_3": [
        [2, 3, 0, 0],
        [0, 0, 0, 0],
        [3, 0, 0, 0],
        [0, 0, 0, 4],
    ],
    "hard_4": [
        [0, 1, 0, 0],
        [0, 0, 4, 0],
        [0, 0, 0, 2],
        [3, 0, 0, 0],
    ],
}

# Known solutions for GS rate computation
SOLUTIONS_4x4 = {
    "easy_1":   [[3, 2, 1, 4], [4, 1, 2, 3], [2, 4, 3, 1], [1, 3, 4, 2]],
    "easy_2":   [[1, 2, 3, 4], [3, 4, 1, 2], [2, 1, 4, 3], [4, 3, 2, 1]],
    "easy_3":   [[2, 3, 4, 1], [4, 1, 2, 3], [3, 4, 1, 2], [1, 2, 3, 4]],
    "easy_4":   [[4, 1, 2, 3], [2, 3, 4, 1], [1, 4, 3, 2], [3, 2, 1, 4]],
    "medium_1": [[3, 2, 1, 4], [4, 1, 2, 3], [2, 4, 3, 1], [1, 3, 4, 2]],
    "medium_2": [[1, 2, 3, 4], [3, 4, 1, 2], [2, 1, 4, 3], [4, 3, 2, 1]],
    "medium_3": [[2, 3, 4, 1], [4, 1, 2, 3], [3, 4, 1, 2], [1, 2, 3, 4]],
    "medium_4": [[4, 1, 2, 3], [2, 3, 4, 1], [1, 4, 3, 2], [3, 2, 1, 4]],
    "hard_1":   [[3, 2, 1, 4], [4, 1, 2, 3], [2, 4, 3, 1], [1, 3, 4, 2]],
    "hard_2":   [[1, 2, 3, 4], [3, 4, 1, 2], [2, 1, 4, 3], [4, 3, 2, 1]],
    "hard_3":   [[2, 3, 4, 1], [4, 1, 2, 3], [3, 4, 1, 2], [1, 2, 3, 4]],
    "hard_4":   [[4, 1, 2, 3], [2, 3, 4, 1], [1, 4, 3, 2], [3, 2, 1, 4]],
}

# ---------------------------------------------------------------------------
# Variable indexing
# ---------------------------------------------------------------------------

def var_idx(i: int, j: int, k: int, N: int) -> int:
    """Linear index for QUBO variable x_{i,j,k}.

    i = row (0-indexed), j = col (0-indexed), k = digit index (0-indexed)
    N = grid size
    """
    return i * N * N + j * N + k


# ---------------------------------------------------------------------------
# BQM construction
# ---------------------------------------------------------------------------

def build_sudoku_bqm(puzzle: list, lam: float) -> BinaryQuadraticModel:
    """
    Build a reduced BQM for the Sudoku puzzle with given cells fixed via fix_variable().

    Penalty weight lam is applied to all four constraint types.
    """
    N = len(puzzle)
    box = int(round(N ** 0.5))
    linear: dict = defaultdict(float)
    quadratic: dict = defaultdict(float)
    offset = 0.0

    def add_one_hot(group: list) -> None:
        nonlocal offset
        for v in group:
            linear[v] += -lam
        for a in range(len(group)):
            for b in range(a + 1, len(group)):
                key = (min(group[a], group[b]), max(group[a], group[b]))
                quadratic[key] += 2 * lam
        offset += lam

    # E1: one digit per cell
    for i in range(N):
        for j in range(N):
            add_one_hot([var_idx(i, j, k, N) for k in range(N)])

    # E2: each digit once per row
    for i in range(N):
        for k in range(N):
            add_one_hot([var_idx(i, j, k, N) for j in range(N)])

    # E3: each digit once per column
    for j in range(N):
        for k in range(N):
            add_one_hot([var_idx(i, j, k, N) for i in range(N)])

    # E4: each digit once per box
    for br in range(box):
        for bc in range(box):
            cells = [(br * box + r, bc * box + c)
                     for r in range(box) for c in range(box)]
            for k in range(N):
                add_one_hot([var_idx(i, j, k, N) for (i, j) in cells])

    bqm = BinaryQuadraticModel(dict(linear), dict(quadratic), offset,
                               vartype="BINARY")

    # Fix given cells
    for i in range(N):
        for j in range(N):
            if puzzle[i][j] != 0:
                digit = puzzle[i][j] - 1  # 0-indexed
                for k in range(N):
                    bqm.fix_variable(var_idx(i, j, k, N), 1 if k == digit else 0)

    return bqm


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_sudoku(sample: dict, puzzle: list) -> tuple:
    """
    Check if a sample (dict of {var_idx: 0|1} for free vars) is a valid solution.

    Returns (is_valid, breakdown) where breakdown has per-constraint violation counts.
    """
    N = len(puzzle)
    box = int(round(N ** 0.5))

    # Reconstruct full grid
    grid = [row[:] for row in puzzle]
    for i in range(N):
        for j in range(N):
            if puzzle[i][j] == 0:
                for k in range(N):
                    v = var_idx(i, j, k, N)
                    if sample.get(v, 0) == 1:
                        grid[i][j] = k + 1
                        break

    # E1: cell one-hot
    e1 = 0
    for i in range(N):
        for j in range(N):
            if puzzle[i][j] == 0:
                count = sum(
                    sample.get(var_idx(i, j, k, N), 0) for k in range(N)
                )
                if count != 1:
                    e1 += 1

    # Row violations
    e2 = 0
    for i in range(N):
        digits = [grid[i][j] for j in range(N) if grid[i][j] != 0]
        if len(digits) != N or len(set(digits)) != N:
            e2 += 1

    # Column violations
    e3 = 0
    for j in range(N):
        digits = [grid[i][j] for i in range(N) if grid[i][j] != 0]
        if len(digits) != N or len(set(digits)) != N:
            e3 += 1

    # Box violations
    e4 = 0
    for br in range(box):
        for bc in range(box):
            digits = []
            for r in range(box):
                for c in range(box):
                    v = grid[br * box + r][bc * box + c]
                    if v != 0:
                        digits.append(v)
            if len(digits) != N or len(set(digits)) != N:
                e4 += 1

    is_valid = (e1 == 0 and e2 == 0 and e3 == 0 and e4 == 0)
    return is_valid, {"e1_cell": e1, "e2_row": e2, "e3_col": e3, "e4_box": e4}


def reconstruct_grid(sample: dict, puzzle: list) -> list:
    """Reconstruct full NxN grid from sample (free vars) and puzzle (givens)."""
    N = len(puzzle)
    grid = [row[:] for row in puzzle]
    for i in range(N):
        for j in range(N):
            if puzzle[i][j] == 0:
                for k in range(N):
                    v = var_idx(i, j, k, N)
                    if sample.get(v, 0) == 1:
                        grid[i][j] = k + 1
                        break
    return grid


# ---------------------------------------------------------------------------
# LAM evaluation
# ---------------------------------------------------------------------------

def evaluate_lam(lam: float, puzzle_key: str, puzzle: list, solution: list,
                 reads: int = 200, sweeps: int = 10_000) -> dict:
    """
    Run SA on the BQM with the given lam and return performance metrics.

    Returns a dict with:
        valid_rate, gs_rate, e1_viol_rate, e2_viol_rate, e3_viol_rate, e4_viol_rate
    """
    bqm = build_sudoku_bqm(puzzle, lam)
    sampler = SimulatedAnnealingSampler()
    response = sampler.sample(bqm, num_reads=reads, num_sweeps=sweeps,
                              beta_range=(0.1, 10.0))

    n_valid = 0
    n_gs = 0
    e1_viols = 0
    e2_viols = 0
    e3_viols = 0
    e4_viols = 0
    n_total = 0

    for datum in response.data():
        n_occ = datum.num_occurrences
        n_total += n_occ
        is_valid, breakdown = validate_sudoku(datum.sample, puzzle)
        if is_valid:
            n_valid += n_occ
            # Check ground state
            grid = reconstruct_grid(datum.sample, puzzle)
            if grid == solution:
                n_gs += n_occ
        e1_viols += breakdown["e1_cell"] * n_occ
        e2_viols += breakdown["e2_row"] * n_occ
        e3_viols += breakdown["e3_col"] * n_occ
        e4_viols += breakdown["e4_box"] * n_occ

    valid_rate = round(100.0 * n_valid / n_total, 2) if n_total else 0.0
    gs_rate    = round(100.0 * n_gs / n_total, 2) if n_total else 0.0

    return {
        "puzzle_key":    puzzle_key,
        "lam":           lam,
        "valid_rate":    valid_rate,
        "gs_rate":       gs_rate,
        "e1_viol_rate":  round(e1_viols / n_total, 4) if n_total else 0.0,
        "e2_viol_rate":  round(e2_viols / n_total, 4) if n_total else 0.0,
        "e3_viol_rate":  round(e3_viols / n_total, 4) if n_total else 0.0,
        "e4_viol_rate":  round(e4_viols / n_total, 4) if n_total else 0.0,
        "n_reads":       n_total,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

LAM_VALUES = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0]
SA_READS   = 200
SA_SWEEPS  = 10_000

HERE       = Path(__file__).parent
OUTPUT_DIR = HERE / "lam_tuning"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"LAM sweep: {LAM_VALUES}")
    print(f"Puzzles:   {list(PUZZLES_4x4.keys())}")
    print(f"Reads:     {SA_READS}  Sweeps: {SA_SWEEPS}")
    print(f"Total runs: {len(LAM_VALUES) * len(PUZZLES_4x4)}")
    print()

    all_rows = []
    t_start = time.time()

    for lam in LAM_VALUES:
        lam_rows = []
        print(f"LAM={lam:.2f}", end="  ", flush=True)
        for puzzle_key, puzzle in PUZZLES_4x4.items():
            solution = SOLUTIONS_4x4[puzzle_key]
            row = evaluate_lam(lam, puzzle_key, puzzle, solution,
                               reads=SA_READS, sweeps=SA_SWEEPS)
            lam_rows.append(row)
            all_rows.append(row)

        # Aggregate across puzzles for this LAM
        avg_valid = sum(r["valid_rate"] for r in lam_rows) / len(lam_rows)
        avg_gs    = sum(r["gs_rate"] for r in lam_rows) / len(lam_rows)
        print(f"avg_valid={avg_valid:.1f}%  avg_gs={avg_gs:.1f}%", flush=True)

    elapsed = time.time() - t_start
    print(f"\nCompleted in {elapsed:.1f}s")

    # Save CSV
    csv_path = OUTPUT_DIR / "lam_sweep.csv"
    fieldnames = [
        "lam", "puzzle_key", "valid_rate", "gs_rate",
        "e1_viol_rate", "e2_viol_rate", "e3_viol_rate", "e4_viol_rate", "n_reads",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow({k: row[k] for k in fieldnames})
    print(f"CSV saved -> {csv_path}")

    # Build summary: per-LAM aggregated metrics
    summary = {}
    for lam in LAM_VALUES:
        rows = [r for r in all_rows if r["lam"] == lam]
        summary[str(lam)] = {
            "lam":             lam,
            "avg_valid_rate":  round(sum(r["valid_rate"] for r in rows) / len(rows), 2),
            "avg_gs_rate":     round(sum(r["gs_rate"] for r in rows) / len(rows), 2),
            "avg_e1_viol":     round(sum(r["e1_viol_rate"] for r in rows) / len(rows), 4),
            "avg_e2_viol":     round(sum(r["e2_viol_rate"] for r in rows) / len(rows), 4),
            "avg_e3_viol":     round(sum(r["e3_viol_rate"] for r in rows) / len(rows), 4),
            "avg_e4_viol":     round(sum(r["e4_viol_rate"] for r in rows) / len(rows), 4),
            "per_puzzle":      {r["puzzle_key"]: {
                                    "valid_rate": r["valid_rate"],
                                    "gs_rate":    r["gs_rate"],
                                } for r in rows},
        }

    # Find best LAM (highest avg valid rate, break ties by gs rate)
    best_lam = max(LAM_VALUES,
                   key=lambda l: (summary[str(l)]["avg_valid_rate"],
                                  summary[str(l)]["avg_gs_rate"]))
    summary["best_lam"] = best_lam
    summary["sa_reads"]  = SA_READS
    summary["sa_sweeps"] = SA_SWEEPS

    json_path = OUTPUT_DIR / "lam_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved -> {json_path}")

    print(f"\nBest LAM: {best_lam}")
    print("\nFull results by LAM:")
    header = f"{'LAM':>6}  {'valid%':>7}  {'gs%':>7}"
    print(header)
    print("-" * len(header))
    for lam in LAM_VALUES:
        s = summary[str(lam)]
        print(f"{lam:>6.2f}  {s['avg_valid_rate']:>7.1f}  {s['avg_gs_rate']:>7.1f}")


if __name__ == "__main__":
    main()
