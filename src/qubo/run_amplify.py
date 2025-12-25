"""Run Fixstars Amplify Annealing Engine on the N-Queens QUBO."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from amplify import Solver
from amplify.client import FixstarsClient

from config import AMPLIFY_TOKEN_ENV, AMPLIFY_NUM_SAMPLES
from src.qubo.qubo_builders import PenaltyConfig, build_qubo
from src.validation.validate_solution import validate_solution
from src.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


class AmplifyTokenMissing(EnvironmentError):
    """Raised when the Amplify token is not available."""


@dataclass
class AmplifyResult:
    energy: float
    positions: List[Tuple[int, int]]
    valid: bool
    runtime: float
    penalties: PenaltyConfig
    num_candidates: int
    best_valid_found: bool
    reason_summary: str
    status: str = "OK"
    message: Optional[str] = None


class AmplifyRunner:
    """Wrapper around the Amplify annealing workflow."""

    def __init__(self, token_env: str = AMPLIFY_TOKEN_ENV):
        token = os.getenv(token_env)
        if not token:
            raise AmplifyTokenMissing(
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
        except Exception as exc:  # Amplify exceptions are varied
            runtime = time.perf_counter() - start
            message = f"Amplify solver error: {exc}"
            logger.error(message)
            return AmplifyResult(
                energy=float("inf"),
                positions=[],
                valid=False,
                runtime=runtime,
                penalties=penalties,
                num_candidates=0,
                best_valid_found=False,
                reason_summary="format_error",
                status="ERROR",
                message=message,
            )

        runtime = time.perf_counter() - start
        num_candidates = len(result)
        if num_candidates == 0:
            logger.warning("Amplify returned no solutions")
            return AmplifyResult(
                energy=float("inf"),
                positions=[],
                valid=False,
                runtime=runtime,
                penalties=penalties,
                num_candidates=0,
                best_valid_found=False,
                reason_summary="wrong_count",
                status="NO_CANDIDATES",
                message="No candidates returned",
            )

        best_energy = float("inf")
        best_positions: List[Tuple[int, int]] = []
        best_reason = "wrong_count"
        best_valid_found = False
        best_valid_energy = float("inf")
        best_valid_positions: List[Tuple[int, int]] = []
        best_valid_reason = "wrong_count"

        for candidate in result:
            energy = candidate.energy
            values: Dict = candidate.values
            positions: List[Tuple[int, int]] = []
            for idx, coord in enumerate(idx_to_coord):
                if values.get(variables[idx], 0) == 1:
                    positions.append(coord)
            validation = validate_solution(positions, n)

            if energy < best_energy:
                best_energy = energy
                best_positions = positions
                best_reason = str(validation.get("reason_summary", "wrong_count"))

            if validation["valid"] and energy < best_valid_energy:
                best_valid_found = True
                best_valid_energy = energy
                best_valid_positions = positions
                best_valid_reason = str(validation.get("reason_summary", "ok"))

        logger.info(
            "Amplify returned %d candidates; best energy %.3f; any valid=%s",
            num_candidates,
            best_energy,
            best_valid_found,
        )

        if best_valid_found:
            return AmplifyResult(
                energy=best_valid_energy,
                positions=best_valid_positions,
                valid=True,
                runtime=runtime,
                penalties=penalties,
                num_candidates=num_candidates,
                best_valid_found=True,
                reason_summary=best_valid_reason,
            )

        return AmplifyResult(
            energy=best_energy,
            positions=best_positions,
            valid=False,
            runtime=runtime,
            penalties=penalties,
            num_candidates=num_candidates,
            best_valid_found=False,
            reason_summary=best_reason,
        )
