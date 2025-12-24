"""Run Fixstars Amplify Annealing Engine on the N-Queens QUBO."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

from amplify import Solver
from amplify.client import FixstarsClient

from config import AMPLIFY_TOKEN_ENV, AMPLIFY_NUM_SAMPLES
from src.qubo.qubo_builders import PenaltyConfig, build_qubo
from src.validation.validate_solution import validate_solution
from src.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


class MissingTokenError(EnvironmentError):
    """Raised when the Amplify token is unavailable."""


@dataclass
class AmplifyResult:
    status: str
    energy: float
    positions: List[Tuple[int, int]]
    valid: bool
    runtime: float
    penalties: PenaltyConfig
    num_candidates: int
    best_valid_found: bool
    reason_summary: str
    message: str = ""


class AmplifyRunner:
    """Wrapper around the Amplify annealing workflow."""

    def __init__(self, token_env: str = AMPLIFY_TOKEN_ENV):
        token = os.getenv(token_env)
        if not token:
            raise MissingTokenError(
                f"Amplify token not found in environment variable {token_env}."
            )
        client = FixstarsClient()
        client.token = token
        client.parameters.outputs.duplicate = True
        self.client = client
        self.solver = Solver(client)

    def solve(self, n: int, penalties: PenaltyConfig, timeout: float | None = None) -> AmplifyResult:
        bqm, idx_to_coord, variables = build_qubo(n, penalties)
        if timeout is not None:
            self.client.parameters.timeout = int(timeout * 1000)
        self.client.parameters.num_outputs = AMPLIFY_NUM_SAMPLES

        start = time.perf_counter()
        try:
            result = self.solver.solve(bqm)
        except Exception as exc:  # Amplify SDK specific exceptions are broad
            runtime = time.perf_counter() - start
            logger.error("Amplify solver error: %s", exc)
            return AmplifyResult(
                status="ERROR",
                energy=float("inf"),
                positions=[],
                valid=False,
                runtime=runtime,
                penalties=penalties,
                num_candidates=0,
                best_valid_found=False,
                reason_summary="format_error",
                message=str(exc),
            )
        runtime = time.perf_counter() - start

        num_candidates = len(result)
        if num_candidates == 0:
            logger.warning("Amplify returned no solutions")
            return AmplifyResult(
                status="NO_CANDIDATE",
                energy=float("inf"),
                positions=[],
                valid=False,
                runtime=runtime,
                penalties=penalties,
                num_candidates=0,
                best_valid_found=False,
                reason_summary="format_error",
                message="No candidates returned",
            )

        best = result[0]
        energy = best.energy
        values: Dict = best.values
        chosen: List[Tuple[int, int]] = []
        for idx, coord in enumerate(idx_to_coord):
            if values.get(variables[idx], 0) == 1:
                chosen.append(coord)

        validation = validate_solution(chosen, n)
        best_valid_found = bool(validation["valid"])
        logger.info(
            "Amplify candidates=%d best_energy=%.4f valid=%s",
            num_candidates,
            energy,
            best_valid_found,
        )

        return AmplifyResult(
            status="OK",
            energy=energy,
            positions=chosen,
            valid=best_valid_found,
            runtime=runtime,
            penalties=penalties,
            num_candidates=num_candidates,
            best_valid_found=best_valid_found,
            reason_summary=str(validation["reason_summary"]),
            message="",
        )


__all__ = ["AmplifyRunner", "AmplifyResult", "MissingTokenError"]
