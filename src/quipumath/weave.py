"""Weave (categorical product) and unweave operations for cords.

Weaving two cords produces a combined cord representing the pair of values.
Unweaving recovers the original components. The weave operation is associative
in the sense that weave(weave(a, b), c) is isomorphic to weave(a, weave(b, c)).
"""

from __future__ import annotations

from quipumath.cord import Cord
from quipumath.knot import KnotNode, encode_number


def weave(cord1: Cord, cord2: Cord) -> Cord:
    """Weave two cords into a combined cord (categorical product).

    The combined cord encodes a pair (v1, v2) using a mapping:
        combined_value = v1 * 10000 + v2
    This supports values up to 9999 each.

    The color is set to "woven:" + cord1.color + "+" + cord2.color.
    Children from both cords are merged.

    Args:
        cord1: First cord.
        cord2: Second cord.

    Returns:
        A new Cord encoding both values.
    """
    v1 = cord1.value
    v2 = cord2.value
    combined_value = v1 * 10000 + v2
    combined_color = f"woven:{cord1.color}+{cord2.color}"
    combined_knots = encode_number(combined_value)
    combined_children = cord1.children + cord2.children

    return Cord(
        color=combined_color,
        knots=combined_knots,
        position=cord1.position,
        children=combined_children,
    )


def unweave(cord: Cord) -> tuple[Cord, Cord]:
    """Unweave a combined cord back into its two component cords.

    Args:
        cord: A cord previously produced by weave().

    Returns:
        Tuple of (cord1, cord2) with original values.
    """
    combined = cord.value
    v2 = combined % 10000
    v1 = combined // 10000

    # Parse the color back to extract original colors
    color_str = cord.color
    if color_str.startswith("woven:") and "+" in color_str:
        colors_part = color_str[len("woven:"):]
        c1_color, c2_color = colors_part.split("+", 1)
    else:
        c1_color, c2_color = "white", "white"

    cord1 = Cord(color=c1_color, knots=encode_number(v1))
    cord2 = Cord(color=c2_color, knots=encode_number(v2))
    return cord1, cord2


def is_associative(cord_a: Cord, cord_b: Cord, cord_c: Cord) -> bool:
    """Check that weave is associative for three cords.

    weave(weave(a, b), c) and weave(a, weave(b, c)) should encode the same
    triple of values, even if the intermediate encodings differ.

    Args:
        cord_a, cord_b, cord_c: Three cords to test.

    Returns:
        True if the values are the same under both groupings.
    """
    # Left: weave(weave(a, b), c)
    left = weave(weave(cord_a, cord_b), cord_c)
    # Right: weave(a, weave(b, c))
    right = weave(cord_a, weave(cord_b, cord_c))
    return left.value == right.value
