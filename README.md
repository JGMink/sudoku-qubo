# Sudoku QUBO: Quantum Optimization Framework

**A complete framework for formulating Sudoku puzzles
as Quadratic Unconstrained Binary Optimization (QUBO) problems,
with variable elimination techniques for quantum and classical optimization.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Contributions](#contributions)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Mathematical Formulation](#mathematical-formulation)
- [Usage Examples](#usage-examples)
- [Matrix Reduction](#matrix-reduction)
- [Performance Metrics](#performance-metrics)
- [Testing](#testing)
- [Documentation](#documentation)
- [QPU Experiments](#qpu-experiments)
- [Citation](#citation)
- [License](#license)
- [Resources](#resources)

---

## Overview

This project provides a complete implementation of Sudoku puzzle formulation
as QUBO problems, suitable for solving on:

- **Quantum annealers** (D-Wave systems)
- **Gate-based quantum computers** (variational algorithms)
- **Classical optimization** (simulated annealing, tabu search, etc.)

The framework includes **variable elimination techniques** that reduce problem size
by 50-75% when given cells (clues) are present,
making larger puzzles tractable on current quantum hardware.

Originally developed as a research project for CMSC 410 (Intro to Quantum
Computing) at Virginia Commonwealth University, advised by Prof. Thang Dinh.

### What is QUBO?

Quadratic Unconstrained Binary Optimization (QUBO)
expresses combinatorial optimization problems as:

```text
minimize: E(x) = x^T Q x
```

where `x` is a binary vector and `Q` is the QUBO matrix.
This formulation is native to quantum annealers
and can be efficiently mapped to quantum circuits.

---

## Contributions

The QUBO formulation, all implementation (QUBO construction, variable
elimination, simulated annealing, D-Wave QPU/hybrid experiments), and
experiment design in this repository are the work of **Jonah Minkoff**.

The formulation was inspired by the grid-based QUBO encoding in Irbäck,
Knuthson & Mohanty, *"Folding lattice proteins confined on minimal grids
using a quantum-inspired encoding,"* Phys. Rev. E (2025)
([arXiv:2510.01890](https://arxiv.org/abs/2510.01890)) — see
[references.md](references.md).

The QAOA comparison in the notebook (`notebooks/sudoku_qubo.ipynb`,
Section 9) was implemented by **Siri Reddy**, a partner on the course
project this repo grew out of. **Derek Chiou**, another course partner,
contributed to repository setup (dependency management, `.gitignore`) and
to the written report. Everything else — including the accompanying
written report and its two other co-authors — is not reproduced here; this
repo covers the code and the solely-authored poster/notes only.

---

## Key Features

### Core Functionality

- ✅ **Full QUBO Construction** - Build complete QUBO matrices for any N×N Sudoku
- ✅ **Variable Elimination** - Reduce matrix size by removing givens
- ✅ **Two Reduction Methods** - Pedagogical (extraction) and efficient (direct) approaches
- ✅ **Energy Evaluation** - Direct calculation and QUBO-based evaluation
- ✅ **Solution Validation** - Verify constraint satisfaction
- ✅ **Solution Reconstruction** - Convert reduced solutions back to full format

### Technical Highlights

- **One-hot encoding** for natural constraint formulation
- **Constraint adjustment** accounting for given cells
- **Optimized matrix operations** with NumPy
- **Index remapping** for efficient reduced representations
- **Comprehensive test suite** with 4 major test cases

### Scalability

- 4×4 Sudoku: 64 variables → 32 with 8 givens
- 9×9 Sudoku: 729 variables → ~450 with 30 givens
- Extensible to larger puzzle sizes

---

## Project Structure

```text
sudoku-qubo/
├── problem_formation_and_evaluation/
│   ├── energy_calc/
│   │   └── calc_mods.py              # Direct energy calculation functions
│   └── qubo_construction/
│       ├── qubo_generation.py        # Full QUBO matrix construction
│       ├── matrix_reduction.py       # Variable elimination & reduction
│       └── construction_test.py      # Comprehensive test suite
│
├── notebooks/
│   └── sudoku_qubo.ipynb             # Interactive tutorial & demonstrations
│
├── qpu_experiments/                  # D-Wave QPU benchmark suite (see below)
│
├── figures/                          # Poster/report figures + generation scripts
│
├── poster/
│   ├── quantum_sudoku_poster.pdf     # Final conference poster
│   ├── quantum_sudoku_poster.pptx    # Poster source (PptxGenJS)
│   └── make_poster.js                # Build script
│
├── papers/
│   └── Simulated_and_Hybrid_Annealing_Algorithms...pdf  # Solo writeup on SA/hybrid annealing
│
├── references.md                     # Annotated bibliography
├── LICENSE                            # MIT License
├── README.md                          # This file
└── requirements.txt                   # Python dependencies
```

### Module Descriptions

#### `qubo_generation.py`

Full QUBO matrix construction for Sudoku puzzles.
Builds complete N³×N³ matrices including all variables (free and fixed).

**Key Functions:**

- `build_sudoku_qubo()` - Complete QUBO with all four constraints
- `build_E1()` through `build_E4()` - Individual constraint components
- `evaluate_qubo()` - Energy calculation from bitstrings

#### `matrix_reduction.py`

Variable elimination techniques to reduce QUBO size by removing fixed variables.

**Key Functions:**

- `build_reduced_qubo()` - Extract reduced matrix (pedagogical approach)
- `build_reduced_qubo_direct()` - Build reduced matrix directly (efficient)
- `evaluate_reduced_qubo()` - Energy evaluation on reduced matrices
- `reconstruct_full_solution()` - Convert reduced to full solutions

#### `calc_mods.py`

Direct energy calculation from Sudoku grids without QUBO matrices.

**Key Functions:**

- `total_energy()` - Calculate constraint violations directly
- `is_valid_solution()` - Check if solution satisfies all constraints
- `tensor_to_grid()` - Convert binary tensors to Sudoku grids

#### `construction_test.py`

Comprehensive test suite validating all functionality.

**Tests:**

1. Blank 4×4 Sudoku (64 variables)
2. Partial 4×4 Sudoku (32 variables with 8 givens)
3. 9×9 Sudoku construction (729 variables)
4. Reduced QUBO validation (matrix equivalence)

---

## Installation

### Prerequisites

- Python 3.8 or higher
- NumPy (only requirement for the core QUBO/reduction code + tests)
- Jupyter, Matplotlib, Seaborn, pandas — for the notebook (`requirements.txt`)
- D-Wave Ocean SDK — only for `qpu_experiments/*.py` and notebook §8 (`requirements-dwave.txt`)
- Qiskit — only for the QAOA comparison, notebook §9 (`requirements-qaoa.txt`)

### Setup

```bash
# Clone the repository
git clone https://github.com/JGMink/sudoku-qubo.git
cd sudoku-qubo

# Core + notebook dependencies
pip install -r requirements.txt

# Optional: only if you'll run qpu_experiments/*.py or notebook §8 (SA/D-Wave)
pip install -r requirements-dwave.txt

# Optional: only if you'll run notebook §9 (QAOA)
pip install -r requirements-qaoa.txt

# Run tests to verify installation (core deps only, no extras needed)
cd problem_formation_and_evaluation/qubo_construction
python construction_test.py
```

Expected output: `✓ ALL TESTS PASSED`

Using `uv` instead: `uv sync` installs core deps; add extras with
`uv sync --extra dwave --extra qaoa`.

---

## Quick Start

### Example 1: Build Full QUBO

```python
from problem_formation_and_evaluation.qubo_construction.qubo_generation import build_sudoku_qubo

# Define a 4×4 puzzle with givens
givens = {
    (0, 0): 2, (0, 2): 4,
    (1, 1): 3, (1, 3): 1,
    (2, 0): 1, (2, 2): 3,
    (3, 1): 4, (3, 3): 2
}

# Build full 64×64 QUBO matrix
Q, var_to_idx, idx_to_var, offset = build_sudoku_qubo(
    N=4,
    box_size=2,
    givens=givens
)

print(f"QUBO size: {Q.shape[0]}×{Q.shape[1]}")
# Output: QUBO size: 64×64
```

### Example 2: Build Reduced QUBO

```python
from problem_formation_and_evaluation.qubo_construction.matrix_reduction import build_reduced_qubo_direct

# Build reduced 32×32 QUBO (eliminates given cells)
Q_reduced, var_to_idx, idx_to_var, offset, info = build_reduced_qubo_direct(
    N=4,
    box_size=2,
    givens=givens
)

print(f"Reduced QUBO size: {Q_reduced.shape[0]}×{Q_reduced.shape[1]}")
print(f"Variable reduction: {info['reduction_pct']:.1f}%")
# Output: Reduced QUBO size: 32×32
#         Variable reduction: 50.0%
```

### Example 3: Evaluate Solution

```python
from problem_formation_and_evaluation.qubo_construction.qubo_generation import evaluate_qubo

# Valid solution for the puzzle
solution_bitstring = (
    "0100" + "1000" + "0001" + "0010" +  # Row 0: 2,1,4,3
    "0001" + "0010" + "0100" + "1000" +  # Row 1: 4,3,2,1
    "1000" + "0100" + "0010" + "0001" +  # Row 2: 1,2,3,4
    "0010" + "0001" + "1000" + "0100"    # Row 3: 3,4,1,2
)

energy = evaluate_qubo(Q, solution_bitstring, offset)
print(f"Energy: {energy}")
# Output: Energy: 0.0  (valid solution!)
```

---

## Mathematical Formulation

### Binary Variables

We use **one-hot encoding**:

```text
x_{i,j,k} = 1  if digit (k+1) is in cell (i,j)
          = 0  otherwise
```

- `i ∈ {0,1,...,N-1}` is the row index
- `j ∈ {0,1,...,N-1}` is the column index  
- `k ∈ {0,1,...,N-1}` is the digit index (k=0 represents digit 1)

**Total variables:** N³ (e.g., 64 for 4×4, 729 for 9×9)

### Energy Function

The objective function minimizes constraint violations:

```text
E = E₁ + E₂ + E₃ + E₄
```

where:

#### E₁: Each cell has exactly one digit

```text
E₁ = Σ_{i,j} [Σ_k x_{i,j,k} - 1]²
```

#### E₂: Each row has each digit exactly once

```text
E₂ = Σ_{i,k} [Σ_j x_{i,j,k} - 1]²
```

#### E₃: Each column has each digit exactly once

```text
E₃ = Σ_{j,k} [Σ_i x_{i,j,k} - 1]²
```

#### E₄: Each box has each digit exactly once

```text
E₄ = Σ_{box,k} [Σ_{(i,j)∈box} x_{i,j,k} - 1]²
```

**Valid solutions have E = 0** (all constraints satisfied).

### QUBO Matrix Form

Expanding the squared penalties gives:

```text
E = x^T Q x + constant
```

where Q is the QUBO matrix with:

- **Diagonal terms:** Linear coefficients from constraint expansion
- **Off-diagonal terms:** Quadratic interaction coefficients
- **Constant offset:** Terms independent of x

---

## Usage Examples

### Working with Givens (Clues)

```python
# Define a partially filled puzzle
givens = {
    (0, 0): 2,  # Cell (0,0) contains digit 2
    (0, 2): 4,  # Cell (0,2) contains digit 4
    # ... more givens
}

# The QUBO automatically accounts for givens:
# - Constraints are adjusted
# - Fixed contributions move to constant offset
# - Can optionally eliminate variables entirely
```

### Lagrange Multipliers

Control constraint importance with Lagrange multipliers:

```python
Q, var_to_idx, idx_to_var, offset = build_sudoku_qubo(
    N=4,
    box_size=2,
    givens=givens,
    L1=1.0,  # Cell constraint weight
    L2=1.0,  # Row constraint weight
    L3=1.0,  # Column constraint weight
    L4=1.0   # Box constraint weight
)

# Adjust weights to emphasize certain constraints
# Higher values → stronger penalty for violations
```

### Solution Validation

```python
from problem_formation_and_evaluation.energy_calc.calc_mods import total_energy, is_valid_solution

# total_energy returns (total, (E1, E2, E3, E4)); is_valid_solution checks the breakdown
total, breakdown = total_energy(solution_bitstring, N=4, box_size=2)
valid = is_valid_solution(breakdown)
print(f"Valid solution: {valid}")  # True iff E1 == E2 == E3 == E4 == 0
```

---

## Matrix Reduction

### The Problem with Givens

When a Sudoku puzzle has given cells (clues), many variables are **fixed**:

- Cell (0,0) = 2 means: x(0,0,1)=1, x(0,0,0)=0, x(0,0,2)=0, x(0,0,3)=0
- These 4 variables are **known** → no need to optimize them!

### Solution: Variable Elimination

**Idea:** Build a smaller QUBO using only the **free variables**.

For 4×4 with 8 givens:

- **Full QUBO:** 64 variables, 64×64 matrix (4,096 entries)
- **Reduced QUBO:** 32 variables, 32×32 matrix (1,024 entries)
- **Savings:** 50% fewer variables, 75% smaller matrix

### Two Approaches

#### 1. Extraction Method (Pedagogical)

```python
Q_reduced, var_to_idx, idx_to_var, offset, info = build_reduced_qubo(
    N, box_size, givens
)
```

**Process:**

1. Build full 64×64 QUBO
2. Identify free variables
3. Extract 32×32 submatrix
4. Return reduced representation

**Advantage:** Clear demonstration of the reduction process

#### 2. Direct Method (Efficient)

```python
Q_reduced, var_to_idx, idx_to_var, offset, info = build_reduced_qubo_direct(
    N, box_size, givens
)
```

**Process:**

1. Identify free variables upfront
2. Build 32×32 QUBO directly
3. Never allocate space for eliminated variables

**Advantage:** More memory efficient, faster for large problems

### Equivalence Guarantee

Both methods produce **identical** results:

- Same QUBO matrix ✓
- Same constant offset ✓
- Same energy for any solution ✓

### Index Remapping

The reduced QUBO uses **new indices** for free variables:

```python
# Old indexing (full QUBO)
x(0,1,0) → index 4
x(0,1,1) → index 5
x(0,1,2) → index 6
x(0,1,3) → index 7

# New indexing (reduced QUBO)
x(0,1,0) → index 0
x(0,1,1) → index 1
x(0,1,2) → index 2
x(0,1,3) → index 3
```

The `var_to_idx` and `idx_to_var` dictionaries handle this mapping automatically.

### Solution Reconstruction

After solving the reduced QUBO, reconstruct the full solution:

```python
from problem_formation_and_evaluation.qubo_construction.matrix_reduction import reconstruct_full_solution

# Solve reduced QUBO → get 32-bit solution
reduced_solution = "01001000001001000010010000100100"

# Reconstruct to 64-bit solution
full_solution = reconstruct_full_solution(
    reduced_solution,
    var_to_idx,
    idx_to_var,
    givens,
    N=4
)

# Now has all 64 bits (including given cells)
```

---

## Performance Metrics

### Variable Reduction

| Puzzle | Givens | Total Vars | Free Vars | Reduction |
|--------|--------|------------|-----------|-----------|
| 4×4 | 0 | 64 | 64 | 0% |
| 4×4 | 8 | 64 | 32 | 50% |
| 9×9 | 0 | 729 | 729 | 0% |
| 9×9 | 30 | 729 | 459 | 37% |
| 9×9 | 40 | 729 | 369 | 49% |

### Matrix Size Reduction

| Puzzle | Full Matrix | Reduced Matrix | Savings |
|--------|-------------|----------------|---------|
| 4×4, 8 givens | 64×64 (4,096) | 32×32 (1,024) | 75% |
| 9×9, 30 givens | 729×729 (531K) | 459×459 (211K) | 60% |

### Quantum Hardware Requirements

| Puzzle | Full Qubits | Reduced Qubits | Feasible On |
|--------|-------------|----------------|-------------|
| 4×4 (blank) | 64 | 64 | Any quantum device |
| 4×4 (8 givens) | 64 | 32 | Any quantum device |
| 9×9 (blank) | 729 | 729 | Large systems only |
| 9×9 (30 givens) | 729 | ~450 | D-Wave, large gate-based |

---

## Testing

### Run All Tests

```bash
cd problem_formation_and_evaluation/qubo_construction
python construction_test.py
```

### Test Coverage

#### Test 1: Blank 4×4 Sudoku

- No givens (all 64 variables free)
- Validates basic QUBO construction
- Tests all four constraint types
- Expected energy: 0.0 for valid solutions

#### Test 2: Partial 4×4 Sudoku

- 8 givens (32 free variables)
- Tests constraint adjustment for givens
- Validates reduced variable handling
- Expected energy: 0.0 for valid solutions

#### Test 3: 9×9 Sudoku Construction

- Validates scalability to full Sudoku
- Matrix size: 729×729
- Construction only (no evaluation)

#### Test 4: Reduced QUBO Validation

- Compares extraction vs direct methods
- Verifies matrix equivalence
- Tests energy preservation
- Validates solution reconstruction

### Expected Output

```text
================================================================================
SUDOKU QUBO TEST SUITE
================================================================================

TEST: Test 1: Blank 4×4 (Valid Solution)
E1: 0.0 (expected 0.0) ✓
E2: 0.0 (expected 0.0) ✓
E3: 0.0 (expected 0.0) ✓
E4: 0.0 (expected 0.0) ✓
Status: ✓ PASS

TEST: Test 2: Partial 4×4 (Valid Solution)
E1: 0.0 (expected 0.0) ✓
E2: 0.0 (expected 0.0) ✓
E3: 0.0 (expected 0.0) ✓
E4: 0.0 (expected 0.0) ✓
Status: ✓ PASS

TEST: Test 3: 9×9 Construction
Matrix size: 729×729 = 531,441 entries
✓ Construction successful

TEST: Test 4: Reduced QUBO
Matrices identical: True ✓
Offsets identical: True ✓
Energy match (correct): ✓
Energy match (incorrect): ✓

================================================================================
SUMMARY
================================================================================
✓ ALL TESTS PASSED
```

---

## Documentation

### Jupyter Notebook

Interactive tutorial covering (see [Contributions](#contributions) for
per-section authorship):

- Problem definition and mathematical formulation
- Step-by-step QUBO construction
- Individual constraint components (E1-E4)
- Full QUBO assembly
- Solution validation
- Variable elimination / matrix reduction (theory, two-method comparison,
  energy validation, solution reconstruction)
- Scaling to 9×9
- Classical baseline: simulated annealing
- QAOA comparison (gate-based, contributed by Siri Reddy)
- Method comparison & conclusions

**Launch:**

```bash
jupyter notebook notebooks/sudoku_qubo.ipynb
```

### Module Organization

```python
# Full QUBO construction
from problem_formation_and_evaluation.qubo_construction.qubo_generation import (
    build_sudoku_qubo,
    build_E1, build_E2, build_E3, build_E4,
    evaluate_qubo
)

# Matrix reduction
from problem_formation_and_evaluation.qubo_construction.matrix_reduction import (
    build_reduced_qubo,
    build_reduced_qubo_direct,
    evaluate_reduced_qubo,
    reconstruct_full_solution,
    print_reduction_stats
)

# Direct energy calculation
from problem_formation_and_evaluation.energy_calc.calc_mods import (
    total_energy,
    is_valid_solution,
    tensor_to_grid,
    print_grid
)
```

---

## QPU Experiments

Hardware experiments on D-Wave Advantage2 (Zephyr topology, ~7,000 qubits)
benchmarking the Sudoku QUBO across difficulty levels and annealing modes.

### Scripts (`qpu_experiments/`)

| Script | Purpose |
|--------|---------|
| `compute_gs_sudoku.py` | Backtracking solver that finds ground-truth solutions for all 14 puzzles and saves them to `ground_truths_sudoku.json` |
| `tune_lam_sudoku.py` | SA-based sweep over LAM ∈ {0.5…4.0} × 12 puzzles to find optimal QUBO penalty weight before QPU runs |
| `run_qpu_sudoku.py` | Forward and reverse annealing on D-Wave QPU; three phases: embed, solve, analyze |

### Test Instances

12 tasks: 4×4 puzzles across 3 difficulty levels (givens chosen so 17 = the
minimum for a unique solution):

| Difficulty | Givens | Free Vars | Qubits (approx) |
|------------|--------|-----------|-----------------|
| Easy       | 12     | 16        | ~17             |
| Medium     | 8      | 32        | ~47             |
| Hard       | 4      | 48        | ~99             |

### Three-Run Workflow

**Run 1 — LAM Tuning (local, free)**
```bash
python qpu_experiments/tune_lam_sudoku.py
```
Sweeps LAM values across all 12 puzzles using SA (108 runs, ~5 min). Output: `qpu_experiments/lam_tuning/lam_sweep.csv` + `lam_summary.json`. **QPU time: 0s.**

**Run 2 — Forward Annealing (QPU)**
```bash
python qpu_experiments/run_qpu_sudoku.py --mode forward --phase embed
python qpu_experiments/run_qpu_sudoku.py --mode forward --phase solve
python qpu_experiments/run_qpu_sudoku.py --phase analyze
```
12 tasks × 1,000 reads × 200 µs ≈ 2.4 s QPU time.

**Run 3 — Reverse Annealing (QPU)**
```bash
python qpu_experiments/run_qpu_sudoku.py --mode reverse --phase embed
python qpu_experiments/run_qpu_sudoku.py --mode reverse --phase solve
python qpu_experiments/run_qpu_sudoku.py --phase analyze
```
SA finds a valid initial state per puzzle; QPU reverse-anneals from that
state using schedule (0µs, s=1) → (10µs, s=0.45) → (110µs, s=0.45) →
(120µs, s=1). **Hypothesis:** starting from the valid manifold increases
valid rate vs. forward annealing, especially on hard puzzles.
12 tasks × 1,000 reads × 120 µs ≈ 1.4 s QPU time.

### Metrics

- **Valid rate** — % reads decoding to a valid Sudoku solution
- **GS rate** — % reads matching the known unique solution
- **Chain break fraction** — mean fraction of chains broken per read
- **SA baseline** — SA valid rate at same read count (free comparison)

Requires a D-Wave Leap account; set `DWAVE_API_TOKEN` in your environment
(never commit it — see `.gitignore`).

---

## Citation

If you use this code in your research, please cite:

```bibtex
@misc{sudoku-qubo-2026,
  title={Sudoku QUBO: Quantum Optimization Framework with Variable Elimination},
  author={Jonah Minkoff},
  year={2026},
  publisher={GitHub},
  url={https://github.com/JGMink/sudoku-qubo}
}
```

See [references.md](references.md) for the full annotated bibliography,
including the Irbäck et al. paper that inspired this project's formulation.

---

## License

This project is licensed under the MIT License
-- see the [LICENSE](LICENSE) file for details.

---

## Resources

### Quantum Computing

- [D-Wave Ocean SDK](https://docs.ocean.dwavesys.com/)
- [Qiskit Optimization](https://qiskit.org/documentation/optimization/)
- [Amazon Braket](https://aws.amazon.com/braket/)

### QUBO Formulation

- Lucas, A. (2014). "Ising formulations of many NP problems"
- Glover, F. et al. (2019).
"Quantum Bridge Analytics I: a tutorial on formulating and using QUBO models"

### Sudoku & Constraint Satisfaction

- Sudoku as a CSP: Russell & Norvig, "Artificial Intelligence: A Modern Approach"
- Quantum approaches: Various papers on quantum constraint satisfaction
