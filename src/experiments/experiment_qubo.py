"""Automated experiments for QUBO annealing using Fixstars Amplify."""
from __future__ import annotations

import config
from src.qubo.run_amplify import AmplifyRunner
from src.utils.logging_utils import setup_logging
import pandas as pd

logger = setup_logging(__name__)


def run_qubo_experiments() -> None:
    config.RAW_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        runner = AmplifyRunner()
    except EnvironmentError as exc:
        logger.error("Cannot run Amplify experiments: %s", exc)
        return

    results = []
    for n in config.QUBO_NS:
        for penalty_cfg in config.QUBO_PENALTIES:
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
                            "N": n,
                            "timeout": timeout,
                            "run": run_id,
                            "energy": outcome.energy,
                            "valid": outcome.valid,
                            "runtime": outcome.runtime,
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
