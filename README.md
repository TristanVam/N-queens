# N-Queens: CP vs QUBO (course project)

This repository is a compact programming project comparing three encodings of the N-Queens problem that stay within the course syllabus: two MiniZinc constraint models (integer + `alldifferent`, Boolean + pseudo-Boolean) and a quadratic unconstrained binary optimization (QUBO) model solved with the Fixstars Amplify Annealing Engine. Everything is scripted so results are reproducible and ready for analysis.

## What we compare / what we measure

- **Models**
  - Classic CP: one integer column variable per row, `alldifferent` on columns and diagonals (optional symmetry break toggle).
  - PB Boolean CP: grid of Booleans with pseudo-Boolean row/column/diagonal constraints.
  - QUBO: binary grid with quadratic penalties, solved via Amplify Annealing Engine.
- **Metrics**
  - Runtime per instance (CP).
  - Success rate across runs (QUBO).
  - Penalty sensitivity (QUBO) by varying weights.
- **Stochastic note**
  - QUBO sampling is stochastic; each configuration is run multiple times.

## Repository structure

```
models/                 MiniZinc models (classic integer + alldifferent, pseudo-Boolean)
src/minizinc/           MiniZinc runners and output parser
src/qubo/               QUBO builders and Amplify runner
src/validation/         Solution validator
src/experiments/        Experiment drivers for CP and QUBO
src/analysis/           Aggregation and plotting utilities
src/utils/              Logging helpers
results/                Default output folders
config.py               Centralized parameters and profiles
sanity_checks.py        Quick correctness checks
```

## Setup

1. Install MiniZinc (make sure `minizinc` is on your `PATH`).
2. (Optional for QUBO) export a Fixstars Amplify token as `AMPLIFY_TOKEN`.
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running experiments

### Constraint Programming (MiniZinc)
```
python -m src.experiments.experiment_cp
```
Stores one CSV row per run in `results/raw/cp_results.csv`.

### QUBO with Amplify
Ensure `AMPLIFY_TOKEN` is set:
```
python -m src.experiments.experiment_qubo
```
Stores one CSV row per run in `results/raw/qubo_results.csv`.

### Aggregation and plotting
```
python -m src.analysis.aggregate_results
python -m src.analysis.plot_results
```
Aggregates are written to `results/aggregated/`, plots to `results/figures/`.

### Sanity checks
```
python sanity_checks.py
```
Runs small N checks, validation tests, and (if a token exists) a QUBO sample.

## Reproducibility notes

- All experiment parameters live in `config.py`, with fast-debug and full-benchmark profiles.
- MiniZinc runs are wrapped with timeouts and keep stdout/stderr for inspection.
- QUBO runs record candidate counts, energies, and validation status for later analysis.
