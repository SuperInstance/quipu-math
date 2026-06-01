"""Incan-style error detection for quipu data.

Provides parity knots, cross-sums across a cord tree, and corruption detection
by comparing two trees (or cords) and listing discrepancies.
"""

from __future__ import annotations

from quipumath.cord import Cord, CordTree
from quipumath.knot import KnotNode, checksum


def parity_knots(cord: Cord) -> int:
    """Compute a parity value for a cord's knot sequence.

    The parity is the sum of all digit values modulo 10.

    Args:
        cord: The cord to compute parity for.

    Returns:
        Parity value (0–9).
    """
    return checksum(cord.knots) % 10


def cross_sums(tree: CordTree) -> dict[str, int]:
    """Compute cross-check sums across a cord tree.

    Returns a dict with:
      - "total": sum of all pendant values
      - "parity": sum of all individual parities mod 10
      - "count": number of pendant cords
      - per-pendant parity under "pendant_N" keys

    Args:
        tree: The cord tree to analyze.

    Returns:
        Dictionary of cross-check sums.
    """
    result: dict[str, int] = {}
    total = 0
    parity_sum = 0
    for i, cord in enumerate(tree.pendant_cords):
        p = parity_knots(cord)
        total += cord.value
        parity_sum += p
        result[f"pendant_{i}"] = p
    result["total"] = total
    result["parity"] = parity_sum % 10
    result["count"] = len(tree.pendant_cords)
    return result


def detect_corruption(
    original: CordTree, corrupted: CordTree
) -> list[str]:
    """Compare two cord trees and list detected errors.

    Checks for:
      - Different number of pendant cords
      - Value mismatches at each position
      - Color mismatches
      - Checksum (parity) mismatches

    Args:
        original: The known-good cord tree.
        corrupted: The potentially corrupted cord tree.

    Returns:
        List of human-readable error descriptions.
    """
    errors: list[str] = []

    if len(original.pendant_cords) != len(corrupted.pendant_cords):
        errors.append(
            f"Pendant count mismatch: original has "
            f"{len(original.pendant_cords)}, corrupted has "
            f"{len(corrupted.pendant_cords)}"
        )
        # Only compare up to the shorter list
        min_len = min(
            len(original.pendant_cords), len(corrupted.pendant_cords)
        )
    else:
        min_len = len(original.pendant_cords)

    for i in range(min_len):
        orig_cord = original.pendant_cords[i]
        corr_cord = corrupted.pendant_cords[i]

        if orig_cord.value != corr_cord.value:
            errors.append(
                f"Value mismatch at pendant {i}: "
                f"{orig_cord.value} vs {corr_cord.value}"
            )

        if orig_cord.color != corr_cord.color:
            errors.append(
                f"Color mismatch at pendant {i}: "
                f"{orig_cord.color!r} vs {corr_cord.color!r}"
            )

        orig_parity = parity_knots(orig_cord)
        corr_parity = parity_knots(corr_cord)
        if orig_parity != corr_parity:
            errors.append(
                f"Parity mismatch at pendant {i}: "
                f"{orig_parity} vs {corr_parity}"
            )

    return errors
