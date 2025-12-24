"""Aggregate raw CSV experiment results."""
from __future__ import annotations

import pandas as pd

import config
from src.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


def aggregate_cp(df: pd.DataFrame) -> pd.DataFrame:
    df_success = df[df["is_valid"]]
    grouped = df.groupby(["model_name", "N"])
    agg = grouped["is_valid"].mean().reset_index(name="success_rate")

    runtime_med = df_success.groupby(["model_name", "N"])["runtime_s"].median().reset_index(name="runtime_median_success")
    runtime_mean = df_success.groupby(["model_name", "N"])["runtime_s"].mean().reset_index(name="runtime_mean_success")
    agg = agg.merge(runtime_med, on=["model_name", "N"], how="left")
    agg = agg.merge(runtime_mean, on=["model_name", "N"], how="left")

    max_rows = []
    for model, group in agg.groupby("model_name"):
        solved = group[group["success_rate"] >= 1.0]
        max_n = solved["N"].max() if not solved.empty else None
        max_rows.append({"model_name": model, "N_max_at_100pct_success": max_n})
    max_df = pd.DataFrame(max_rows)
    agg = agg.merge(max_df, on=["model_name"], how="left")
    return agg


def aggregate_qubo(df: pd.DataFrame) -> pd.DataFrame:
    df_success = df[df["is_valid"]]
    grouped = df.groupby(["N", "penalty_set_name"])
    agg = grouped["is_valid"].mean().reset_index(name="success_rate")

    energy_median = df_success.groupby(["N", "penalty_set_name"])["energy"].median().reset_index(name="energy_median_success")
    runtime_median = df_success.groupby(["N", "penalty_set_name"])["runtime_s"].median().reset_index(name="runtime_median_success")
    agg = agg.merge(energy_median, on=["N", "penalty_set_name"], how="left")
    agg = agg.merge(runtime_median, on=["N", "penalty_set_name"], how="left")

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
