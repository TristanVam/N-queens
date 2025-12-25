"""Automated experiments for QUBO annealing using Fixstars Amplify."""
from __future__ import annotations

from datetime import datetime

import pandas as pd

import config
from src.qubo.run_amplify import AmplifyRunner, AmplifyTokenMissing
from src.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


def run_qubo_experiments() -> None:
    config.RAW_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        runner = AmplifyRunner()
    except AmplifyTokenMissing as exc:
        logger.error("Cannot run Amplify experiments: %s", exc)
        return

    results = []
    run_counter = 0
    for n in config.QUBO_NS:
        for penalty_idx, penalty_cfg in enumerate(config.QUBO_PENALTIES):
            penalty_name = f"penalty_set_{penalty_idx}"
            for timeout in config.QUBO_TIMEOUTS:
                for run_id in range(config.QUBO_RUNS_PER_CONFIG):
                    logger.info(
                        "QUBO run N=%d timeout=%.2fs penalties=%s run=%d",
                        n,
                        timeout,
                        penalty_cfg,
                        run_id,
                    )
                    outcome = runner.solve(n, penalty_cfg, timeout=timeout)
                    results.append(
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "solver_name": "amplify_ae",
                            "model_name": "qubo",
                            "run_id": run_counter,
                            "N": n,
                            "timeout_s": timeout,
                            "status": outcome.status,
                            "runtime_s": outcome.runtime,
                            "is_valid": outcome.valid,
                            "reason_summary": outcome.reason_summary,
                            "penalty_set_name": penalty_name,
                            "penalty_values": str(penalty_cfg),
                            "energy": outcome.energy,
                            "num_candidates": outcome.num_candidates,
                            "best_valid_found": outcome.best_valid_found,
                            "run_repeat": run_id,
                        }
                    )
                    run_counter += 1

    df = pd.DataFrame(results)
    df.to_csv(config.QUBO_RESULTS_CSV, index=False)
    logger.info("Saved QUBO results to %s", config.QUBO_RESULTS_CSV)


if __name__ == "__main__":
    run_qubo_experiments()
