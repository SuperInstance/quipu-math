"""Knot types and number encoding/decoding for quipu mathematics.

Incan quipu encode decimal numbers using knot sequences on cords.
Each position represents a decimal place (ones, tens, hundreds…).
- Long knots (multiple turns) encode the digit value (2–9 turns).
- A figure-eight knot encodes the digit 1.
- A single knot encodes 1 in non-units positions (simplified convention).
- Absence of knots at a position encodes 0.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass


class KnotType(enum.Enum):
    """Types of knots used in quipu encoding."""

    single = 1
    figure_eight = 1  # represents digit 1 in the units position
    long = 0  # placeholder; actual value set via `turns`

    @classmethod
    def long_with_turns(cls, turns: int) -> "KnotNode":
        """Create a long knot with a specific number of turns (2–9)."""
        if not 2 <= turns <= 9:
            raise ValueError(f"Long knot turns must be 2–9, got {turns}")
        return KnotNode(knot=cls.long, turns=turns)


@dataclass(frozen=True)
class KnotNode:
    """A single knot on a cord.

    Attributes:
        knot: The type of knot.
        turns: Number of turns (meaningful only for long knots).
        position: Decimal position (0=units, 1=tens, 2=hundreds…).
    """

    knot: KnotType
    turns: int = 0
    position: int = 0

    @property
    def digit_value(self) -> int:
        """The decimal digit this knot represents."""
        if self.knot == KnotType.figure_eight:
            return 1
        if self.knot == KnotType.single:
            return 1
        if self.knot == KnotType.long:
            return self.turns
        return 0


def encode_number(n: int) -> list[KnotNode]:
    """Encode a non-negative integer as a sequence of quipu knots.

    Each digit is encoded with its decimal position preserved.
    The convention uses KnotNode.position to track which decimal place
    each knot occupies.

    Each digit maps to:
      - 0 → no knot at that position
      - 1 → figure_eight (units, position 0) or single (position > 0)
      - 2–9 → long knot with that many turns

    Args:
        n: Non-negative integer to encode.

    Returns:
        List of KnotNode with position information.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError(f"Cannot encode negative number: {n}")
    if n == 0:
        return []

    digits: list[int] = []
    while n > 0:
        digits.append(n % 10)
        n //= 10

    knots: list[KnotNode] = []
    for position, digit in enumerate(digits):
        if digit == 0:
            continue
        elif digit == 1:
            if position == 0:
                knots.append(KnotNode(knot=KnotType.figure_eight, position=position))
            else:
                knots.append(KnotNode(knot=KnotType.single, position=position))
        else:
            knots.append(KnotNode(knot=KnotType.long, turns=digit, position=position))
    return knots


def decode_knots(knots: list[KnotNode]) -> int:
    """Decode a knot sequence back to an integer.

    Each knot carries its position (decimal place). The digit value
    contributes 10^position to the total.

    Args:
        knots: Sequence of KnotNode objects with position info.

    Returns:
        The decoded integer value.
    """
    if not knots:
        return 0

    total = 0
    for node in knots:
        total += node.digit_value * (10 ** node.position)
    return total


def checksum(knots: list[KnotNode]) -> int:
    """Compute a simple checksum (sum of digit values) for a knot sequence.

    Args:
        knots: Sequence of KnotNode objects.

    Returns:
        Sum of all digit values in the sequence.
    """
    return sum(node.digit_value for node in knots)
