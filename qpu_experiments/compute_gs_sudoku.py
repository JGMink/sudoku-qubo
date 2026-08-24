"""
Backtracking Sudoku solver for 4x4 and 9x9 puzzles.

Finds ALL solutions (stops after 2 for uniqueness check), verifies each solution
against the full QUBO energy, and saves results to ground_truths_sudoku.json.

Self-contained: no imports from other files in this repo.
"""

import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Puzzle definitions
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

# Known solutions for all 4x4 puzzles
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

PUZZLES_9x9 = {
    "9x9_easy": [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ],
    "9x9_hard": [
        [8, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 6, 0, 0, 0, 0, 0],
        [0, 7, 0, 0, 9, 0, 2, 0, 0],
        [0, 5, 0, 0, 0, 7, 0, 0, 0],
        [0, 0, 0, 0, 4, 5, 7, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 3, 0],
        [0, 0, 1, 0, 0, 0, 0, 6, 8],
        [0, 0, 8, 5, 0, 0, 0, 1, 0],
        [0, 9, 0, 0, 0, 0, 4, 0, 0],
    ],
}

# ---------------------------------------------------------------------------
# Variable indexing (matches run_qpu_sudoku.py)
# ---------------------------------------------------------------------------

def var_idx(i: int, j: int, k: int, N: int) -> int:
    """Linear index for QUBO variable x_{i,j,k}.

    i = row (0-indexed)
    j = col (0-indexed)
    k = digit index (0-indexed, so digit k+1)
    N = grid size (4 or 9)
    """
    return i * N * N + j * N + k


# ---------------------------------------------------------------------------
# Backtracking solver
# ---------------------------------------------------------------------------

def _is_valid_placement(grid, row, col, num, N):
    """Check if placing num at (row, col) is consistent."""
    box = int(round(N ** 0.5))

    # Row check
    if num in grid[row]:
        return False

    # Column check
    if num in [grid[r][col] for r in range(N)]:
        return False

    # Box check
    br = (row // box) * box
    bc = (col // box) * box
    for r in range(br, br + box):
        for c in range(bc, bc + box):
            if grid[r][c] == num:
                return False

    return True


def _find_empty(grid, N):
    """Return (row, col) of the first empty cell, or None if full."""
    for i in range(N):
        for j in range(N):
            if grid[i][j] == 0:
                return (i, j)
    return None


def find_all_solutions(puzzle, max_solutions=2):
    """
    Backtracking solver that finds all solutions, stopping after max_solutions.

    Returns a list of solutions (each solution is an NxN list of ints).
    """
    N = len(puzzle)
    grid = [row[:] for row in puzzle]  # deep copy
    solutions = []

    def backtrack():
        if len(solutions) >= max_solutions:
            return
        cell = _find_empty(grid, N)
        if cell is None:
            # Board is full — record solution
            solutions.append([row[:] for row in grid])
            return
        row, col = cell
        for num in range(1, N + 1):
            if _is_valid_placement(grid, row, col, num, N):
                grid[row][col] = num
                backtrack()
                grid[row][col] = 0
                if len(solutions) >= max_solutions:
                    return

    backtrack()
    return solutions


# ---------------------------------------------------------------------------
# QUBO energy verification (4x4 only)
# ---------------------------------------------------------------------------

def verify_qubo_energy(puzzle, solution, lam=1.0):
    """
    Build the full 4x4 Sudoku QUBO and evaluate energy for the given solution.

    For a valid solution with all constraints satisfied, energy should be 0.0.

    QUBO penalty for a one-hot group of size N:
        lam * (sum(x) - 1)^2
      = lam * (sum(x_i^2) - 2*sum(x_i) + 2*sum_{i<j}(x_i*x_j) + 1)

    Since x_i in {0,1}, x_i^2 = x_i, so:
        = lam * (-sum(x_i) + 2*sum_{i<j}(x_i*x_j) + 1)

    We evaluate this directly from the binary assignment.
    """
    N = len(puzzle)
    box = int(round(N ** 0.5))

    # Build binary assignment from solution
    x = {}
    for i in range(N):
        for j in range(N):
            for k in range(N):
                idx = var_idx(i, j, k, N)
                x[idx] = 1 if solution[i][j] == (k + 1) else 0

    def one_hot_penalty(group_indices):
        """Evaluate lam*(sum(x_i) - 1)^2 for the given group."""
        s = sum(x[idx] for idx in group_indices)
        return lam * (s - 1) ** 2

    total_energy = 0.0

    # E1: one digit per cell
    for i in range(N):
        for j in range(N):
            group = [var_idx(i, j, k, N) for k in range(N)]
            total_energy += one_hot_penalty(group)

    # E2: each digit once per row
    for i in range(N):
        for k in range(N):
            group = [var_idx(i, j, k, N) for j in range(N)]
            total_energy += one_hot_penalty(group)

    # E3: each digit once per column
    for j in range(N):
        for k in range(N):
            group = [var_idx(i, j, k, N) for i in range(N)]
            total_energy += one_hot_penalty(group)

    # E4: each digit once per 2x2 box
    for br in range(box):
        for bc in range(box):
            cells = [(br * box + r, bc * box + c)
                     for r in range(box) for c in range(box)]
            for k in range(N):
                group = [var_idx(i, j, k, N) for (i, j) in cells]
                total_energy += one_hot_penalty(group)

    return total_energy


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def is_valid_solution(solution, puzzle):
    """Check that solution is consistent with puzzle givens and all constraints."""
    N = len(solution)
    box = int(round(N ** 0.5))

    # Check givens
    for i in range(N):
        for j in range(N):
            if puzzle[i][j] != 0 and solution[i][j] != puzzle[i][j]:
                return False

    digits = set(range(1, N + 1))

    # Rows
    for i in range(N):
        if set(solution[i]) != digits:
            return False

    # Columns
    for j in range(N):
        if set(solution[i][j] for i in range(N)) != digits:
            return False

    # Boxes
    for br in range(box):
        for bc in range(box):
            vals = set()
            for r in range(box):
                for c in range(box):
                    vals.add(solution[br * box + r][bc * box + c])
            if vals != digits:
                return False

    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    HERE = Path(__file__).parent
    output_path = HERE / "ground_truths_sudoku.json"

    results = {}
    all_passed = True

    print("=" * 60)
    print("4x4 Puzzles")
    print("=" * 60)

    for key, puzzle in PUZZLES_4x4.items():
        print(f"\n[{key}]")
        solutions = find_all_solutions(puzzle, max_solutions=2)

        if len(solutions) == 0:
            print(f"  ERROR: No solution found!")
            all_passed = False
            results[key] = {"error": "no_solution"}
            continue

        if len(solutions) > 1:
            print(f"  WARNING: Multiple solutions found (not unique)!")

        sol = solutions[0]
        unique = (len(solutions) == 1)

        # Verify against known solution
        known = SOLUTIONS_4x4.get(key)
        matches_known = (sol == known) if known else None

        # Verify constraints
        valid = is_valid_solution(sol, puzzle)

        # Verify QUBO energy (4x4 only)
        energy = verify_qubo_energy(puzzle, sol, lam=1.0)

        status_parts = []
        if valid:
            status_parts.append("valid")
        else:
            status_parts.append("INVALID")
            all_passed = False

        if energy == 0.0:
            status_parts.append(f"energy={energy:.1f} (correct)")
        else:
            status_parts.append(f"energy={energy:.4f} (WRONG)")
            all_passed = False

        if unique:
            status_parts.append("unique")
        else:
            status_parts.append("NOT-UNIQUE")

        if matches_known is not None:
            if matches_known:
                status_parts.append("matches-known")
            else:
                status_parts.append("DIFFERS-FROM-KNOWN")
                print(f"  Solver found:  {sol}")
                print(f"  Known sol:     {known}")
                all_passed = False

        print(f"  {', '.join(status_parts)}")
        print(f"  Solution: {sol}")

        results[key] = {
            "puzzle":   puzzle,
            "solution": sol,
            "unique":   unique,
            "valid":    valid,
            "qubo_energy_lam1": energy,
            "n_givens": sum(1 for row in puzzle for v in row if v != 0),
            "n_free":   sum(1 for row in puzzle for v in row if v == 0),
        }

    print("\n" + "=" * 60)
    print("9x9 Puzzles (no QUBO energy check)")
    print("=" * 60)

    for key, puzzle in PUZZLES_9x9.items():
        print(f"\n[{key}]")
        solutions = find_all_solutions(puzzle, max_solutions=2)

        if len(solutions) == 0:
            print(f"  ERROR: No solution found!")
            all_passed = False
            results[key] = {"error": "no_solution"}
            continue

        if len(solutions) > 1:
            print(f"  WARNING: Multiple solutions found (not unique)!")

        sol = solutions[0]
        unique = (len(solutions) == 1)
        valid = is_valid_solution(sol, puzzle)

        status_parts = []
        if valid:
            status_parts.append("valid")
        else:
            status_parts.append("INVALID")
            all_passed = False
        if unique:
            status_parts.append("unique")
        else:
            status_parts.append("NOT-UNIQUE")

        print(f"  {', '.join(status_parts)}")
        print(f"  Solution row 0: {sol[0]}")

        results[key] = {
            "puzzle":   puzzle,
            "solution": sol,
            "unique":   unique,
            "valid":    valid,
            "qubo_energy_lam1": None,  # skipped for 9x9
            "n_givens": sum(1 for row in puzzle for v in row if v != 0),
            "n_free":   sum(1 for row in puzzle for v in row if v == 0),
        }

    # Save results
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 60}")
    if all_passed:
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED — see output above")
    print(f"Results saved -> {output_path}")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    import sys
    ok = main()
    sys.exit(0 if ok else 1)
