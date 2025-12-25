# N-Queens Course Project: CP vs QUBO

This repository accompanies a university-style project that compares three N-Queens models built with course material only: two MiniZinc encodings (classic `alldifferent` over integers and a Boolean pseudo-Boolean variant) and a quadratic unconstrained binary optimization (QUBO) solved with the Fixstars Amplify annealing engine. The code is structured for reproducible experiments and lightweight reporting rather than marketing polish.

## What we compare / what we measure
- **Models**: classic CP with `alldifferent`, Boolean PB with row/column/diagonal counts, and a grid-based QUBO sent to Amplify.
- **Metrics**: runtime, success rate (especially for the stochastic QUBO), and sensitivity to penalty weights in the QUBO formulation.
- **Stochastic note**: QUBO runs are repeated per setting to capture variability.

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
config.py               Centralized parameters
sanity_checks.py        Quick correctness checks
```

## Setup
1. Install MiniZinc and ensure `minizinc` is on your PATH.
2. (Optional for QUBO) Obtain a Fixstars Amplify token and export it as `AMPLIFY_TOKEN`.
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running experiments
### Constraint Programming (MiniZinc)
```
python -m src.experiments.experiment_cp
```
This records one row per run in `results/raw/cp_results.csv` (model, N, timeout, status, validity).

### QUBO with Amplify
```
python -m src.experiments.experiment_qubo
```
Requires `AMPLIFY_TOKEN`. Outputs long-format rows to `results/raw/qubo_results.csv`, including penalty settings, energies, and validity for repeated runs.

### Aggregation and plotting
After generating raw CSVs, create aggregated tables and figures:
```
python -m src.analysis.aggregate_results
python -m src.analysis.plot_results
```
Aggregates are written to `results/aggregated/` and plots to `results/figures/` (CP runtime vs N, QUBO success rate vs N, and QUBO penalty sensitivity).

### Sanity checks
Run small checks for `N=4` and `N=8` to confirm the pipeline:
```
python sanity_checks.py
```
The script exercises both CP models, the validator (including a negative case), and runs a small QUBO test only if a token is available.

## Reproducibility notes
- Experiment parameters (board sizes, timeouts, penalty weights, number of runs) live in `config.py`. Profiles let you switch between quick debugging and fuller benchmarks.
- MiniZinc runs enforce per-call timeouts; QUBO runs respect Amplify timeouts and sample counts.
- QUBO solutions are validated just like CP solutions; success rates summarize how often the annealer finds a legal placement.
