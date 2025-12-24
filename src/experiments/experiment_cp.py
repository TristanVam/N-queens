"""Automated experiments for the MiniZinc CP models."""
from __future__ import annotations

from datetime import datetime, timezone
import pandas as pd

import config
from src.minizinc.parse_minizinc_output import parse_positions
from src.minizinc.run_minizinc import run_minizinc
from src.utils.logging_utils import setup_logging
from src.validation.validate_solution import validate_solution

logger = setup_logging(__name__)


def run_cp_experiments() -> None:
    results = []
    config.RAW_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    run_counter = 0

    for model_name, model_path in config.CP_MODELS.items():
        for n in config.CP_NS:
            for timeout in config.CP_TIMEOUTS:
                logger.info("Running %s with N=%d timeout=%ss", model_name, n, timeout)
                run_id = run_counter
                run_counter += 1
                result = run_minizinc(str(model_path), {"N": n}, timeout=timeout)
                try:
                    positions = parse_positions(result.stdout) if result.status == "SAT" else []
                except ValueError as exc:
                    logger.error("Parsing failed: %s", exc)
                    positions = []

                validity = validate_solution(positions, n)
                results.append(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "solver_name": "minizinc",
                        "model_name": model_name,
                        "run_id": run_id,
                        "N": n,
                        "timeout_s": timeout,
                        "status": result.status,
                        "runtime_s": result.runtime,
                        "is_valid": validity["valid"],
                        "reason_summary": validity["reason_summary"],
                        "num_queens": len(positions),
                        "violations": ";".join(validity["violations"]),
                    }
                )

    df = pd.DataFrame(results)
    df.to_csv(config.CP_RESULTS_CSV, index=False)
    logger.info("Saved CP results to %s", config.CP_RESULTS_CSV)


if __name__ == "__main__":
    run_cp_experiments()
