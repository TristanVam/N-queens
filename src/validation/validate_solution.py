"""Validate N-Queens placements and summarize reasons."""
from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Tuple


class ValidationError(Exception):
    """Raised when a validation precondition fails."""



def _has_duplicates(values: Iterable[int]) -> bool:
    counter = Counter(values)
    return any(count > 1 for count in counter.values())


def _summary_from_flags(
    wrong_count: bool, out_of_bounds: bool, row_dup: bool, col_dup: bool, diag_dup: bool
) -> str:
    if wrong_count:
        return "wrong_count"
    if out_of_bounds:
        return "format_error"
    if row_dup:
        return "row_conflict"
    if col_dup:
        return "col_conflict"
    if diag_dup:
        return "diag_conflict"
    return "ok"


def validate_solution(positions: List[Tuple[int, int]], n: int) -> Dict[str, object]:
    """Check board bounds, conflicts, and produce a concise summary."""
    if n <= 0:
        raise ValidationError("Board size must be positive")

    violations: List[str] = []
    rows = [r for r, _ in positions]
    cols = [c for _, c in positions]
    diag1 = [r + c for r, c in positions]
    diag2 = [r - c for r, c in positions]

    wrong_count = len(positions) != n
    out_of_bounds = any(r < 1 or r > n or c < 1 or c > n for r, c in positions)
    row_dup = _has_duplicates(rows)
    col_dup = _has_duplicates(cols)
    diag_dup = _has_duplicates(diag1) or _has_duplicates(diag2)

    if wrong_count:
        violations.append(f"Expected {n} queens, found {len(positions)}")

    if out_of_bounds:
        violations.append("Coordinates out of bounds")

    if row_dup:
        violations.append("Row conflict detected")
    if col_dup:
        violations.append("Column conflict detected")
    if _has_duplicates(diag1):
        violations.append("Positive diagonal conflict detected")
    if _has_duplicates(diag2):
        violations.append("Negative diagonal conflict detected")

    valid = len(violations) == 0
    reason_summary = _summary_from_flags(wrong_count, out_of_bounds, row_dup, col_dup, diag_dup)
    return {
        "valid": valid,
        "violations": violations,
        "counts": {
            "rows": Counter(rows),
            "cols": Counter(cols),
            "diag1": Counter(diag1),
            "diag2": Counter(diag2),
        },
        "reason_summary": reason_summary,
    }
