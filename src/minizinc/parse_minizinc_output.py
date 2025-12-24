"""Parser for MiniZinc output produced by the N-Queens models."""
from __future__ import annotations

import re
from typing import List, Tuple


POSITION_PATTERN = re.compile(r"positions=\[(?P<body>[^\]]*)\]")
PAIR_PATTERN = re.compile(r"\(\s*(?P<row>\d+)\s*,\s*(?P<col>\d+)\s*\)")


def parse_positions(raw_output: str) -> List[Tuple[int, int]]:
    """Extract a list of ``(row, col)`` tuples from MiniZinc output."""
    match = POSITION_PATTERN.search(raw_output)
    if not match:
        raise ValueError("Could not find positions array in MiniZinc output")

    body = match.group("body").strip()
    if not body:
        return []

    positions: List[Tuple[int, int]] = []
    for pair_match in PAIR_PATTERN.finditer(body):
        row = int(pair_match.group("row"))
        col = int(pair_match.group("col"))
        positions.append((row, col))
    if not positions:
        raise ValueError("No coordinate pairs parsed from MiniZinc output")
    return positions


__all__ = ["parse_positions"]
