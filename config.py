"""Central configuration for N-Queens experiments.

Profiles allow switching between quick debugging runs and fuller benchmarks
without editing multiple files. This keeps experimental protocols explicit
and reproducible.
"""
from pathlib import Path

ROOT = Path(__file__).parent
RESULTS_DIR = ROOT / "results"
RAW_RESULTS_DIR = RESULTS_DIR / "raw"
AGG_RESULTS_DIR = RESULTS_DIR / "aggregated"
FIGURES_DIR = RESULTS_DIR / "figures"

# Select a profile to populate all experiment parameters.
# FAST_DEBUG keeps runs short for interactive debugging.
# FULL_BENCH scales until timeouts and success rates begin to degrade.
PROFILE = "FULL_BENCH"

PROFILE_SETTINGS = {
    "FAST_DEBUG": {
        "CP_NS": [4, 8],
        "CP_TIMEOUTS": [3],
        "QUBO_NS": [4],
        "QUBO_TIMEOUTS": [1.0],
        "QUBO_RUNS_PER_CONFIG": 1,
        "QUBO_PENALTIES": [
            {"row": 2.0, "col": 2.0, "diag": 2.0},
        ],
    },
    "FULL_BENCH": {
        "CP_NS": [4, 8, 12, 16],
        "CP_TIMEOUTS": [5, 15],
        "QUBO_NS": [4, 8, 12],
        "QUBO_TIMEOUTS": [1.0, 3.0],
        "QUBO_RUNS_PER_CONFIG": 3,
        "QUBO_PENALTIES": [
            {"row": 4.0, "col": 4.0, "diag": 4.0},
            {"row": 2.0, "col": 2.0, "diag": 4.0},
            {"row": 1.0, "col": 1.0, "diag": 2.0},
        ],
    },
}

_profile = PROFILE_SETTINGS[PROFILE]

# Constraint Programming settings
CP_NS = _profile["CP_NS"]
CP_TIMEOUTS = _profile["CP_TIMEOUTS"]  # seconds
CP_MODELS = {
    "classic": ROOT / "models" / "queens_classic.mzn",
    "pb": ROOT / "models" / "queens_pb.mzn",
}

# QUBO settings
QUBO_NS = _profile["QUBO_NS"]
QUBO_TIMEOUTS = _profile["QUBO_TIMEOUTS"]  # seconds per annealing run if supported
QUBO_RUNS_PER_CONFIG = _profile["QUBO_RUNS_PER_CONFIG"]
# Penalty configurations: (row, column, diag)
QUBO_PENALTIES = _profile["QUBO_PENALTIES"]

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
