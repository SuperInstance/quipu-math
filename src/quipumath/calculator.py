"""Quipu arithmetic — add, subtract, and multiply quipu values.

Operations work on CordTree objects, producing new trees with the results.
"""

from __future__ import annotations

from quipumath.cord import Cord, CordTree
from quipumath.knot import encode_number


def _result_tree(value: int, color: str = "green") -> CordTree:
    """Build a single-pendant tree encoding a result value."""
    tree = CordTree()
    tree.add_pendant(Cord(color=color, knots=encode_number(value)))
    return tree


def add_quipus(tree_a: CordTree, tree_b: CordTree) -> CordTree:
    """Add two quipu trees element-wise (pendant by pendant).

    If the trees have different numbers of pendants, the shorter is
    zero-padded. The result has one pendant per position whose value
    is the sum of the corresponding pendants.

    Args:
        tree_a: First quipu tree.
        tree_b: Second quipu tree.

    Returns:
        A new CordTree with element-wise sums.
    """
    max_len = max(len(tree_a.pendant_cords), len(tree_b.pendant_cords))
    result = CordTree()
    for i in range(max_len):
        va = tree_a.pendant_cords[i].value if i < len(tree_a.pendant_cords) else 0
        vb = tree_b.pendant_cords[i].value if i < len(tree_b.pendant_cords) else 0
        result.add_pendant(Cord(color="green", knots=encode_number(va + vb)))
    return result


def subtract_quipus(tree_a: CordTree, tree_b: CordTree) -> CordTree:
    """Subtract tree_b from tree_a element-wise.

    Raises ValueError if any result would be negative.

    Args:
        tree_a: Minuend quipu tree.
        tree_b: Subtrahend quipu tree.

    Returns:
        A new CordTree with element-wise differences.
    """
    max_len = max(len(tree_a.pendant_cords), len(tree_b.pendant_cords))
    result = CordTree()
    for i in range(max_len):
        va = tree_a.pendant_cords[i].value if i < len(tree_a.pendant_cords) else 0
        vb = tree_b.pendant_cords[i].value if i < len(tree_b.pendant_cords) else 0
        diff = va - vb
        if diff < 0:
            raise ValueError(
                f"Negative result at position {i}: {va} - {vb} = {diff}"
            )
        result.add_pendant(Cord(color="blue", knots=encode_number(diff)))
    return result


def multiply_quipus(tree_a: CordTree, tree_b: CordTree) -> CordTree:
    """Multiply two quipu trees element-wise.

    If the trees have different numbers of pendants, the shorter is
    zero-padded.

    Args:
        tree_a: First quipu tree.
        tree_b: Second quipu tree.

    Returns:
        A new CordTree with element-wise products.
    """
    max_len = max(len(tree_a.pendant_cords), len(tree_b.pendant_cords))
    result = CordTree()
    for i in range(max_len):
        va = tree_a.pendant_cords[i].value if i < len(tree_a.pendant_cords) else 0
        vb = tree_b.pendant_cords[i].value if i < len(tree_b.pendant_cords) else 0
        result.add_pendant(Cord(color="yellow", knots=encode_number(va * vb)))
    return result
