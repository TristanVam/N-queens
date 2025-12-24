"""Automated experiments for QUBO annealing using Fixstars Amplify."""
from __future__ import annotations

from datetime import datetime, timezone
import pandas as pd

import config
from src.qubo.run_amplify import AmplifyRunner, MissingTokenError
from src.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


def run_qubo_experiments() -> None:
    config.RAW_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        runner = AmplifyRunner()
    except MissingTokenError as exc:
        logger.error("Cannot run Amplify experiments: %s", exc)
        return

    results = []
    for penalty_idx, penalty_cfg in enumerate(config.QUBO_PENALTIES):
        penalty_name = f"penalty_set_{penalty_idx}"
        for n in config.QUBO_NS:
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
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "solver_name": "amplify_ae",
                            "model_name": "qubo",
                            "run_id": run_id,
                            "penalty_set_name": penalty_name,
                            "penalty_values": str(penalty_cfg),
                            "N": n,
                            "timeout_s": timeout,
                            "status": outcome.status,
                            "runtime_s": outcome.runtime,
                            "energy": outcome.energy,
                            "is_valid": outcome.valid,
                            "reason_summary": outcome.reason_summary,
                            "num_candidates": outcome.num_candidates,
                            "best_valid_found": outcome.best_valid_found,
                            "penalty_row": penalty_cfg.get("row"),
                            "penalty_col": penalty_cfg.get("col"),
                            "penalty_diag": penalty_cfg.get("diag"),
                            "num_queens": len(outcome.positions),
                        }
                    )

    df = pd.DataFrame(results)
    df.to_csv(config.QUBO_RESULTS_CSV, index=False)
    logger.info("Saved QUBO results to %s", config.QUBO_RESULTS_CSV)


if __name__ == "__main__":
    run_qubo_experiments()
