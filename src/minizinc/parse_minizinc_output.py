"""Parser for MiniZinc output produced by the N-Queens models.

MiniZinc may print multiple solutions separated by "----------" and a final
"==========". The parser keeps the last non-empty solution block by default to
match standard satisfaction search behavior.
"""
from __future__ import annotations

import re
from typing import List, Tuple


POSITION_PATTERN = re.compile(r"positions=\[(?P<body>[^\]]*)\]")
PAIR_PATTERN = re.compile(r"\(\s*(?P<row>\d+)\s*,\s*(?P<col>\d+)\s*\)")
SEPARATOR = "----------"
TERMINATOR = "=========="


def _extract_last_block(raw_output: str) -> str:
    text = raw_output.replace(TERMINATOR, "").strip()
    if SEPARATOR in text:
        candidates = [block.strip() for block in text.split(SEPARATOR) if block.strip()]
        if not candidates:
            raise ValueError("No solution blocks found in MiniZinc output")
        return candidates[-1]
    return text


def parse_positions(raw_output: str) -> List[Tuple[int, int]]:
    """Extract a list of ``(row, col)`` tuples from MiniZinc output.

    The parser targets the last solution block and raises a clear error if the
    expected ``positions=[(r,c), ...]`` pattern is missing.
    """
    block = _extract_last_block(raw_output)
    match = POSITION_PATTERN.search(block)
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
