"""Utility to invoke MiniZinc models from Python."""
from __future__ import annotations

import shlex
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

from config import MINIZINC_BINARY
from src.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


@dataclass
class MiniZincResult:
    """Container for MiniZinc run results."""

    status: str
    runtime: float
    stdout: str
    stderr: str

    def as_tuple(self) -> Tuple[str, float, str, str]:
        return self.status, self.runtime, self.stdout, self.stderr


def _format_params(params: Dict[str, int]) -> List[str]:
    cmd_params: List[str] = []
    for key, val in params.items():
        literal = f"{key}={val}"
        cmd_params.extend(["-D", literal])
    return cmd_params


def run_minizinc(model_path: str, params: Dict[str, int], timeout: int = 10) -> MiniZincResult:
    """Run a MiniZinc model via the command line interface.

    Parameters
    ----------
    model_path:
        Path to the `.mzn` model file.
    params:
        Dictionary of MiniZinc parameters (currently expects integers only).
    timeout:
        Wall-clock timeout in seconds.
    """
    cmd = [MINIZINC_BINARY, model_path]
    cmd.extend(_format_params(params))
    logger.debug("Executing MiniZinc: %s", " ".join(shlex.quote(x) for x in cmd))

    start = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        runtime = time.perf_counter() - start
    except subprocess.TimeoutExpired as exc:
        runtime = time.perf_counter() - start
        logger.warning("MiniZinc timeout after %.3fs", runtime)
        return MiniZincResult(status="TIMEOUT", runtime=runtime, stdout=exc.stdout or "", stderr=exc.stderr or "")
    except FileNotFoundError as exc:
        runtime = time.perf_counter() - start
        message = f"MiniZinc binary not found: {exc}"
        logger.error(message)
        return MiniZincResult(status="ERROR", runtime=runtime, stdout="", stderr=message)

    if proc.returncode == 0:
        status = "SAT"
    else:
        status = "ERROR"
        logger.error("MiniZinc returned non-zero exit code %s", proc.returncode)

    return MiniZincResult(status=status, runtime=runtime, stdout=proc.stdout, stderr=proc.stderr)


__all__ = ["MiniZincResult", "run_minizinc"]
