"""Quick sanity checks for the N-Queens project."""
from __future__ import annotations

import os
import sys

from config import CP_MODELS
from src.minizinc.run_minizinc import run_minizinc
from src.minizinc.parse_minizinc_output import parse_positions
from src.validation.validate_solution import validate_solution
from src.qubo.run_amplify import AmplifyRunner, AmplifyTokenMissing


def check_cp_models() -> bool:
    ok = True
    for model_name, model_path in CP_MODELS.items():
        for n in (4, 8):
            result = run_minizinc(str(model_path), {"N": n}, timeout=5)
            try:
                positions = parse_positions(result.stdout) if result.status == "SAT" else []
            except ValueError:
                positions = []
            validity = validate_solution(positions, n)
            success = result.status == "SAT" and validity["valid"]
            print(
                f"CP {model_name} N={n} status={result.status} valid={validity['valid']} "
                f"reason={validity['reason_summary']}"
            )
            ok = ok and success
    return ok


def check_validator() -> bool:
    invalid = [(1, 1), (1, 2), (2, 2), (3, 3)]
    validity = validate_solution(invalid, 4)
    detected = not validity["valid"] and validity["reason_summary"] != "ok"
    print("Validator negative test reason=", validity["reason_summary"], "violations=", validity["violations"])
    return detected


def check_qubo_behavior() -> bool:
    token = os.getenv("AMPLIFY_TOKEN")
    if not token:
        print("QUBO skipped (AMPLIFY_TOKEN missing)")
        return True
    try:
        runner = AmplifyRunner()
    except AmplifyTokenMissing as exc:
        print("QUBO skipped (AMPLIFY_TOKEN missing)", exc)
        return True
    weak_penalties = {"row": 0.5, "col": 0.5, "diag": 0.5}
    outcome = runner.solve(4, weak_penalties, timeout=1.0)
    print(
        "QUBO run energy=", outcome.energy,
        "valid=", outcome.valid,
        "best_valid_found=", outcome.best_valid_found,
        "candidates=", outcome.num_candidates,
        "reason=", outcome.reason_summary,
    )
    return outcome.num_candidates >= 0  # only fail on solver crash


def main() -> None:
    cp_ok = check_cp_models()
    validator_ok = check_validator()
    qubo_ok = check_qubo_behavior()

    all_ok = cp_ok and validator_ok and qubo_ok
    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
