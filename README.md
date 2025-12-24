# N-Queens Comparative Study (CP & QUBO)

This repository implements an experimental pipeline for the N-Queens problem using only the methods covered in the accompanying course: MiniZinc-based constraint programming (integer + `alldifferent`, Boolean + pseudo-Boolean constraints) and a quadratic unconstrained binary optimization (QUBO) formulation solved with the Fixstars Amplify annealing engine. The code is fully reproducible and organized for direct submission as a programming project.

## Project goals

- Provide clean MiniZinc models for two CP encodings.
- Provide a QUBO model with configurable penalties and an annealing-based solver.
- Offer automated experiment scripts, aggregation, and plotting utilities.
- Validate all solutions with a consistent checker.

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

1. Install MiniZinc (binary available on the PATH).
2. Obtain a Fixstars Amplify token and export it as `AMPLIFY_TOKEN` for QUBO experiments.
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running experiments

### Constraint Programming (MiniZinc)

```
python -m src.experiments.experiment_cp
```
Outputs a CSV at `results/raw/cp_results.csv` with status, runtime, and validity information for each run.

### QUBO with Amplify

Ensure `AMPLIFY_TOKEN` is set before running:
```
python -m src.experiments.experiment_qubo
```
Results are stored in `results/raw/qubo_results.csv` and include energy, validity, and penalty configuration.

### Aggregation and plotting

After running experiments, aggregate and generate figures:
```
python -m src.analysis.aggregate_results
python -m src.analysis.plot_results
```
Aggregated tables are placed in `results/aggregated/` and plots in `results/figures/` (runtime vs N for CP, success rate vs N for QUBO, and penalty sensitivity).

### Sanity checks

Run small end-to-end checks for `N=4` and `N=8`:
```
python sanity_checks.py
```
The script exercises both CP models, the validator, and (if a token is available) a QUBO run with weak penalties to illustrate stochastic behavior.

## Reproducibility notes

- All experiment parameters (board sizes, timeouts, penalty weights, number of runs) are centralized in `config.py` for transparency and easy modification.
- The MiniZinc runner enforces per-call timeouts to avoid hanging runs.
- QUBO solutions are sampled multiple times (`AMPLIFY_NUM_SAMPLES`) to capture stochastic performance; exact outcomes may vary per run.

## Warnings

- The QUBO annealing process is inherently stochastic. Success rates and energies may fluctuate across runs, especially with weaker penalties.
- If MiniZinc or Amplify are not installed/configured, the corresponding scripts will log an error and skip execution.
