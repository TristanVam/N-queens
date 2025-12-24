"""QUBO model builders for the N-Queens problem using Fixstars Amplify.

Modeling choices (within the course material):
- Binary variables x[r, c] arranged on the N x N grid (1-based when decoded).
- Constraint-to-penalty approach with only quadratic terms.
- Rows are enforced as exactly one queen; columns use (sum - 1)^2 as well.
  Because every row enforces exactly one queen (N queens total), requiring
  each column to sum to 1 is equivalent to the standard "at most one" plus
  pigeonhole reasoning and keeps penalties symmetric with the PB grid model.
- Diagonals are enforced with pairwise quadratic penalties (at most one).
The index mapping is kept stable for encoding/decoding solutions.
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
    """Construct a BinaryQuadraticModel for the N-Queens problem.

    Penalties use the standard quadratic formulation for equality and at-most-one
    constraints.
    """
    idx_to_coord, coord_to_idx = generate_mapping(n)
    x = gen_symbols(BinaryQuadraticModelBuilder, n * n)
    bqm = BinaryQuadraticModel()

    # Row constraints: (sum - 1)^2
    row_penalty = penalties.get("row", 1.0)
    for r in range(n):
        row_indices = [coord_to_idx[(r + 1, c + 1)] for c in range(n)]
        _add_equality_penalty(bqm, x, row_indices, row_penalty)

    # Column constraints
    col_penalty = penalties.get("col", 1.0)
    for c in range(n):
        col_indices = [coord_to_idx[(r + 1, c + 1)] for r in range(n)]
        _add_equality_penalty(bqm, x, col_indices, col_penalty, target=1)

    # Diagonal constraints: pairwise conflicts only (at most one)
    diag_penalty = penalties.get("diag", 1.0)
    diagonals = _collect_diagonals(n)
    for indices in diagonals:
        # Pairwise penalties enforce at most one queen per diagonal
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


__all__ = ["build_qubo", "generate_mapping", "PenaltyConfig"]
