"""Quick sanity checks for the N-Queens project."""
from __future__ import annotations

import sys

from src.minizinc.run_minizinc import run_minizinc
from src.minizinc.parse_minizinc_output import parse_positions
from src.validation.validate_solution import validate_solution
from src.qubo.run_amplify import AmplifyRunner, MissingTokenError
from config import CP_MODELS


def check_cp_models() -> bool:
    ok = True
    for model_name, model_path in CP_MODELS.items():
        for n in (4, 8):
            result = run_minizinc(str(model_path), {"N": n}, timeout=5)
            positions = parse_positions(result.stdout) if result.status == "SAT" else []
            validity = validate_solution(positions, n)
            success = result.status == "SAT" and validity["valid"]
            print(f"CP {model_name} N={n}: status={result.status} valid={validity['valid']}")
            ok = ok and success
    return ok


def check_validator() -> bool:
    invalid = [(1, 1), (1, 2), (2, 2), (3, 3)]
    validity = validate_solution(invalid, 4)
    print("Validator detects conflicts:", validity["violations"])
    return not validity["valid"]


def check_qubo_behavior() -> bool:
    try:
        runner = AmplifyRunner()
    except MissingTokenError as exc:
        print("QUBO skipped (AMPLIFY_TOKEN missing):", exc)
        return True
    weak_penalties = {"row": 0.5, "col": 0.5, "diag": 0.5}
    outcome = runner.solve(4, weak_penalties, timeout=1.0)
    print(
        "QUBO run energy=", outcome.energy,
        "valid=", outcome.valid,
        "queens=", len(outcome.positions),
        "candidates=", outcome.num_candidates,
    )
    return True


def main() -> None:
    status_cp = check_cp_models()
    status_validator = check_validator()
    status_qubo = check_qubo_behavior()
    if not (status_cp and status_validator and status_qubo):
        sys.exit(1)


if __name__ == "__main__":
    main()
