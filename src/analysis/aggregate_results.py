"""Aggregate raw CSV experiment results."""
from __future__ import annotations

import pandas as pd

import config
from src.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


def aggregate_cp(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grouped = df.groupby(["model_name", "N"], dropna=False)
    for (model, n), group in grouped:
        successes = group[group["is_valid"]]
        success_rate = len(successes) / len(group)
        runtime_median_success = successes["runtime_s"].median() if not successes.empty else None
        runtime_mean_success = successes["runtime_s"].mean() if not successes.empty else None
        rows.append(
            {
                "model_name": model,
                "N": n,
                "success_rate": success_rate,
                "runtime_median_success": runtime_median_success,
                "runtime_mean_success": runtime_mean_success,
            }
        )
    agg = pd.DataFrame(rows)

    max_rows = []
    for model, group in agg.groupby("model_name"):
        solved = group[group["success_rate"] >= 1.0]
        max_n = solved["N"].max() if not solved.empty else None
        max_rows.append({"model_name": model, "N_max_at_100pct_success": max_n})
    max_df = pd.DataFrame(max_rows)
    return agg.merge(max_df, on="model_name", how="left")


def aggregate_qubo(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grouped = df.groupby(["N", "penalty_set_name", "penalty_values"], dropna=False)
    for (n, penalty_name, penalty_values), group in grouped:
        successes = group[group["is_valid"]]
        success_rate = len(successes) / len(group)
        runtime_median_success = successes["runtime_s"].median() if not successes.empty else None
        runtime_mean_success = successes["runtime_s"].mean() if not successes.empty else None
        energy_median = successes["energy"].median() if not successes.empty else None
        rows.append(
            {
                "N": n,
                "penalty_set_name": penalty_name,
                "penalty_values": penalty_values,
                "success_rate": success_rate,
                "runtime_median_success": runtime_median_success,
                "runtime_mean_success": runtime_mean_success,
                "energy_median_success": energy_median,
            }
        )
    agg = pd.DataFrame(rows)
    solved = agg[agg["success_rate"] >= 1.0]
    max_n = solved["N"].max() if not solved.empty else None
    agg["N_max_at_100pct_success"] = max_n
    return agg


def run() -> None:
    config.AGG_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        cp_df = pd.read_csv(config.CP_RESULTS_CSV)
        cp_agg = aggregate_cp(cp_df)
        cp_agg.to_csv(config.AGG_CP_CSV, index=False)
        logger.info("Saved CP aggregation to %s", config.AGG_CP_CSV)
    except FileNotFoundError:
        logger.warning("CP results file not found at %s", config.CP_RESULTS_CSV)

    try:
        qubo_df = pd.read_csv(config.QUBO_RESULTS_CSV)
        qubo_agg = aggregate_qubo(qubo_df)
        qubo_agg.to_csv(config.AGG_QUBO_CSV, index=False)
        logger.info("Saved QUBO aggregation to %s", config.AGG_QUBO_CSV)
    except FileNotFoundError:
        logger.warning("QUBO results file not found at %s", config.QUBO_RESULTS_CSV)


if __name__ == "__main__":
    run()
