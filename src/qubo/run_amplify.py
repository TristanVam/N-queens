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


@dataclass
class AmplifyResult:
    energy: float
    positions: List[Tuple[int, int]]
    valid: bool
    runtime: float
    penalties: PenaltyConfig


class AmplifyRunner:
    """Wrapper around the Amplify annealing workflow."""

    def __init__(self, token_env: str = AMPLIFY_TOKEN_ENV):
        token = os.getenv(token_env)
        if not token:
            raise EnvironmentError(
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
        result = self.solver.solve(bqm)
        runtime = time.perf_counter() - start

        if len(result) == 0:
            logger.warning("Amplify returned no solutions")
            return AmplifyResult(
                energy=float("inf"), positions=[], valid=False, runtime=runtime, penalties=penalties
            )

        # Take the best solution
        best = result[0]
        energy = best.energy
        values: Dict = best.values
        chosen: List[Tuple[int, int]] = []
        for idx, coord in enumerate(idx_to_coord):
            if values.get(variables[idx], 0) == 1:
                chosen.append(coord)

        validation = validate_solution(chosen, n)
        return AmplifyResult(
            energy=energy,
            positions=chosen,
            valid=bool(validation["valid"]),
            runtime=runtime,
            penalties=penalties,
        )


__all__ = ["AmplifyRunner", "AmplifyResult"]
