"""Central configuration for N-Queens experiments."""
from pathlib import Path

ROOT = Path(__file__).parent
RESULTS_DIR = ROOT / "results"
RAW_RESULTS_DIR = RESULTS_DIR / "raw"
AGG_RESULTS_DIR = RESULTS_DIR / "aggregated"
FIGURES_DIR = RESULTS_DIR / "figures"

# Constraint Programming settings
CP_NS = [4, 8, 12, 16]
CP_TIMEOUTS = [5, 15]  # seconds
CP_MODELS = {
    "classic": ROOT / "models" / "queens_classic.mzn",
    "pb": ROOT / "models" / "queens_pb.mzn",
}

# QUBO settings
QUBO_NS = [4, 8, 12]
QUBO_TIMEOUTS = [1.0, 3.0]  # seconds per annealing run if supported
QUBO_RUNS_PER_CONFIG = 3
# Penalty configurations: (row, column, diag)
QUBO_PENALTIES = [
    {"row": 4.0, "col": 4.0, "diag": 4.0},
    {"row": 2.0, "col": 2.0, "diag": 4.0},
    {"row": 1.0, "col": 1.0, "diag": 2.0},
]

# Amplify / annealing settings
AMPLIFY_NUM_SAMPLES = 20
AMPLIFY_TOKEN_ENV = "AMPLIFY_TOKEN"

# Paths for binaries
MINIZINC_BINARY = "minizinc"

# Random seeds used for experiments where applicable
DEFAULT_SEED = 1234

# CSV schema
CP_RESULTS_CSV = RAW_RESULTS_DIR / "cp_results.csv"
QUBO_RESULTS_CSV = RAW_RESULTS_DIR / "qubo_results.csv"
AGG_CP_CSV = AGG_RESULTS_DIR / "cp_aggregated.csv"
AGG_QUBO_CSV = AGG_RESULTS_DIR / "qubo_aggregated.csv"
