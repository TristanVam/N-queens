"""Generate plots from aggregated experiment results."""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

import config
from src.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


def _save(fig, name: str) -> None:
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = config.FIGURES_DIR / name
    fig.tight_layout()
    fig.savefig(path)
    logger.info("Saved figure to %s", path)
    plt.close(fig)


def plot_cp_runtime():
    try:
        df = pd.read_csv(config.AGG_CP_CSV)
    except FileNotFoundError:
        logger.warning("Aggregated CP results not found at %s", config.AGG_CP_CSV)
        return
    fig, ax = plt.subplots()
    for model, group in df.groupby("model_name"):
        ax.plot(group["N"], group["runtime_median_success"], marker="o", label=model)
    ax.set_xlabel("Board size N")
    ax.set_ylabel("Median runtime (s)")
    ax.set_title("CP runtime vs N")
    ax.legend()
    _save(fig, "cp_runtime.png")


def plot_qubo_success():
    try:
        df = pd.read_csv(config.AGG_QUBO_CSV)
    except FileNotFoundError:
        logger.warning("Aggregated QUBO results not found at %s", config.AGG_QUBO_CSV)
        return
    fig, ax = plt.subplots()
    avg = df.groupby("N")["success_rate"].mean().reset_index()
    ax.plot(avg["N"], avg["success_rate"], marker="o")
    ax.set_xlabel("Board size N")
    ax.set_ylabel("Mean success rate")
    ax.set_title("QUBO success rate vs N")
    _save(fig, "qubo_success_rate.png")


def plot_penalty_sensitivity():
    try:
        df = pd.read_csv(config.AGG_QUBO_CSV)
    except FileNotFoundError:
        logger.warning("Aggregated QUBO results not found at %s", config.AGG_QUBO_CSV)
        return
    fig, ax = plt.subplots()
    df_sorted = df.sort_values(["N", "success_rate"], ascending=[True, False])
    for penalty_name, group in df_sorted.groupby("penalty_set_name"):
        ax.plot(group["N"], group["success_rate"], marker="o", label=penalty_name)
    ax.set_xlabel("Board size N")
    ax.set_ylabel("Success rate")
    ax.set_title("Penalty sensitivity by N")
    ax.legend()
    _save(fig, "qubo_penalties.png")


def run() -> None:
    plot_cp_runtime()
    plot_qubo_success()
    plot_penalty_sensitivity()


if __name__ == "__main__":
    run()
