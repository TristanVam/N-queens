"""Quick sanity checks for the N-Queens project."""
from __future__ import annotations

from src.minizinc.run_minizinc import run_minizinc
from src.minizinc.parse_minizinc_output import parse_positions
from src.validation.validate_solution import validate_solution
from src.qubo.run_amplify import AmplifyRunner
from config import CP_MODELS


def check_cp_models() -> None:
    for model_name, model_path in CP_MODELS.items():
        for n in (4, 8):
            result = run_minizinc(str(model_path), {"N": n}, timeout=5)
            positions = parse_positions(result.stdout)
            validity = validate_solution(positions, n)
            print(f"CP {model_name} N={n} status={result.status} valid={validity['valid']}")


def check_validator() -> None:
    invalid = [(1, 1), (1, 2), (2, 2), (3, 3)]
    validity = validate_solution(invalid, 4)
    print("Validator detects conflicts:", validity["violations"])


def check_qubo_behavior() -> None:
    try:
        runner = AmplifyRunner()
    except EnvironmentError as exc:
        print("Skipping QUBO check (token missing):", exc)
        return
    weak_penalties = {"row": 0.5, "col": 0.5, "diag": 0.5}
    outcome = runner.solve(4, weak_penalties, timeout=1.0)
    print(
        "QUBO run energy=", outcome.energy,
        "valid=", outcome.valid,
        "queens=", len(outcome.positions),
    )


def main() -> None:
    check_cp_models()
    check_validator()
    check_qubo_behavior()


if __name__ == "__main__":
    main()
