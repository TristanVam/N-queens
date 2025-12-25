"""Build the grid-style QUBO for N-Queens.

Rows and columns use equality; ``<= 1`` per column is equivalent by pigeonhole,
and we stick with ``= 1`` to keep the penalties clear and stable in practice.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from amplify import BinaryQuadraticModel, BinaryQuadraticModelBuilder, gen_symbols


PenaltyConfig = Dict[str, float]


def generate_mapping(n: int) -> Tuple[List[Tuple[int, int]], Dict[Tuple[int, int], int]]:
    """Create index-to-coordinate and coordinate-to-index mappings."""
    idx_to_coord: List[Tuple[int, int]] = []
    coord_to_idx: Dict[Tuple[int, int], int] = {}
    for r in range(n):
        for c in range(n):
            idx = r * n + c
            idx_to_coord.append((r + 1, c + 1))
            coord_to_idx[(r + 1, c + 1)] = idx
    return idx_to_coord, coord_to_idx


def build_qubo(
    n: int, penalties: PenaltyConfig
) -> Tuple[BinaryQuadraticModel, List[Tuple[int, int]], list]:
    """Create the N-Queens BinaryQuadraticModel with penalty scaling."""
    idx_to_coord, coord_to_idx = generate_mapping(n)
    x = gen_symbols(BinaryQuadraticModelBuilder, n * n)
    bqm = BinaryQuadraticModel()

    # Row constraints: (sum - 1)^2 to enforce exactly one queen per row
    row_penalty = penalties.get("row", 1.0)
    for r in range(n):
        row_indices = [coord_to_idx[(r + 1, c + 1)] for c in range(n)]
        _add_equality_penalty(bqm, x, row_indices, row_penalty)

    # Column constraints: equality is equivalent to <= 1 because total queens = N
    col_penalty = penalties.get("col", 1.0)
    for c in range(n):
        col_indices = [coord_to_idx[(r + 1, c + 1)] for r in range(n)]
        _add_equality_penalty(bqm, x, col_indices, col_penalty, target=1)

    # Diagonal constraints: pairwise conflicts only (at most one)
    diag_penalty = penalties.get("diag", 1.0)
    diagonals = _collect_diagonals(n)
    for indices in diagonals:
        _add_at_most_one_penalty(bqm, x, indices, diag_penalty)

    # Offset is not essential but kept for clarity
    bqm.normalize()
    return bqm, idx_to_coord, x


def _add_equality_penalty(
    bqm: BinaryQuadraticModel,
    vars_builder,
    indices: List[int],
    penalty: float,
    target: int = 1,
) -> None:
    """Add quadratic penalty (sum xi - target)^2 scaled by penalty."""
    if not indices:
        return
    for idx in indices:
        bqm.add_bias(vars_builder[idx], penalty * (1 - 2 * target))
    for i, idx_i in enumerate(indices):
        for idx_j in indices[i + 1 :]:
            bqm.add_quadratic(vars_builder[idx_i], vars_builder[idx_j], 2 * penalty)
    bqm.add_offset(penalty * target * target)


def _add_at_most_one_penalty(
    bqm: BinaryQuadraticModel,
    vars_builder,
    indices: List[int],
    penalty: float,
) -> None:
    """Penalize any pair of active variables in the provided index set."""
    for i, idx_i in enumerate(indices):
        for idx_j in indices[i + 1 :]:
            bqm.add_quadratic(vars_builder[idx_i], vars_builder[idx_j], penalty)


def _collect_diagonals(n: int) -> List[List[int]]:
    idx_to_coord, _ = generate_mapping(n)
    diag_map: Dict[int, List[int]] = {}
    anti_diag_map: Dict[int, List[int]] = {}
    for idx, (r, c) in enumerate(idx_to_coord):
        diag = r - c
        anti = r + c
        diag_map.setdefault(diag, []).append(idx)
        anti_diag_map.setdefault(anti, []).append(idx)
    return list(diag_map.values()) + list(anti_diag_map.values())
