"""Validation utilities for N-Queens solutions."""
from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Tuple


class ValidationError(Exception):
    """Raised when a validation precondition fails."""



def _has_duplicates(values: Iterable[int]) -> bool:
    counter = Counter(values)
    return any(count > 1 for count in counter.values())


def validate_solution(positions: List[Tuple[int, int]], n: int) -> Dict[str, object]:
    """Validate an N-Queens placement.

    Returns a dictionary with:
    - ``valid``: boolean
    - ``violations``: list of strings describing conflicts
    - ``counts``: diagnostic counters
    """
    if n <= 0:
        raise ValidationError("Board size must be positive")

    violations: List[str] = []
    rows = [r for r, _ in positions]
    cols = [c for _, c in positions]
    diag1 = [r + c for r, c in positions]
    diag2 = [r - c for r, c in positions]

    if len(positions) != n:
        violations.append(f"Expected {n} queens, found {len(positions)}")

    if any(r < 1 or r > n or c < 1 or c > n for r, c in positions):
        violations.append("Coordinates out of bounds")

    if _has_duplicates(rows):
        violations.append("Row conflict detected")
    if _has_duplicates(cols):
        violations.append("Column conflict detected")
    if _has_duplicates(diag1):
        violations.append("Positive diagonal conflict detected")
    if _has_duplicates(diag2):
        violations.append("Negative diagonal conflict detected")

    valid = len(violations) == 0
    return {
        "valid": valid,
        "violations": violations,
        "counts": {
            "rows": Counter(rows),
            "cols": Counter(cols),
            "diag1": Counter(diag1),
            "diag2": Counter(diag2),
        },
    }


__all__ = ["validate_solution", "ValidationError"]
