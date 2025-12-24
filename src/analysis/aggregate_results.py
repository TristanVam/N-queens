"""Aggregate raw CSV experiment results."""
from __future__ import annotations

import pandas as pd

import config
from src.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


def aggregate_cp(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby(["model", "N"])
    agg = grouped.agg(success_rate=("valid", "mean"), median_runtime=("runtime", "median")).reset_index()
    max_rows = []
    for model, group in agg.groupby("model"):
        solved = group[group["success_rate"] >= 1.0]
        max_n = solved["N"].max() if not solved.empty else None
        max_rows.append({"model": model, "max_solved_N": max_n})
    max_df = pd.DataFrame(max_rows)
    agg = agg.merge(max_df, on="model", how="left")
    return agg


def aggregate_qubo(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby(["N", "penalty_row", "penalty_col", "penalty_diag"])
    agg = grouped.agg(success_rate=("valid", "mean"), median_energy=("energy", "median"), median_runtime=("runtime", "median")).reset_index()
    solved = agg[agg["success_rate"] >= 1.0]
    max_n = solved["N"].max() if not solved.empty else None
    agg["max_solved_N"] = max_n
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
