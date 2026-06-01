"""Cord and CordTree data structures for quipu mathematics.

A Cord holds a color, a sequence of knots, and optional child cords
(subsidiaries). A CordTree represents a full quipu: one main cord with
zero or more pendant cords hanging from it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from quipumath.knot import KnotNode, decode_knots, encode_number


@dataclass
class Cord:
    """A single cord on a quipu.

    Attributes:
        color: Color identifier for the cord (e.g. "red", "white").
        knots: Sequence of knots encoding a number.
        position: Position along the main cord (0-indexed).
        children: Subsidiary cords attached to this cord.
    """

    color: str = "white"
    knots: list[KnotNode] = field(default_factory=list)
    position: int = 0
    children: list["Cord"] = field(default_factory=list)

    @property
    def value(self) -> int:
        """The numeric value encoded in this cord's knots."""
        return decode_knots(self.knots)

    def add_child(self, child: "Cord") -> None:
        """Attach a subsidiary cord."""
        self.children.append(child)

    def to_dict(self) -> dict[str, Any]:
        """Serialize this cord (and children) to a dict."""
        return {
            "color": self.color,
            "knots": [
                {"knot": k.knot.name, "turns": k.turns, "position": k.position} for k in self.knots
            ],
            "position": self.position,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Cord":
        """Deserialize a cord from a dict."""
        from quipumath.knot import KnotType

        knots = [
            KnotNode(
                knot=KnotType[d["knot"]],
                turns=d.get("turns", 0),
                position=d.get("position", 0),
            )
            for d in data.get("knots", [])
        ]
        children = [cls.from_dict(c) for c in data.get("children", [])]
        return cls(
            color=data.get("color", "white"),
            knots=knots,
            position=data.get("position", 0),
            children=children,
        )


@dataclass
class CordTree:
    """A full quipu: main cord with pendant cords.

    Attributes:
        main_cord: The primary top-level cord.
        pendant_cords: Cords hanging from the main cord.
    """

    main_cord: Cord = field(default_factory=lambda: Cord(color="main"))
    pendant_cords: list[Cord] = field(default_factory=list)

    def add_pendant(self, cord: Cord) -> None:
        """Add a pendant cord, auto-assigning position if default."""
        cord.position = len(self.pendant_cords)
        self.pendant_cords.append(cord)

    def total_value(self) -> int:
        """Sum of all pendant cord values."""
        return sum(c.value for c in self.pendant_cords)

    def serialize(self) -> str:
        """Serialize the tree to a JSON string."""
        data = {
            "main_cord": self.main_cord.to_dict(),
            "pendant_cords": [c.to_dict() for c in self.pendant_cords],
        }
        return json.dumps(data, indent=2)

    @classmethod
    def deserialize(cls, json_str: str) -> "CordTree":
        """Deserialize a tree from a JSON string."""
        data = json.loads(json_str)
        main = Cord.from_dict(data["main_cord"])
        pendants = [Cord.from_dict(d) for d in data.get("pendant_cords", [])]
        return cls(main_cord=main, pendant_cords=pendants)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CordTree):
            return NotImplemented
        return self.serialize() == other.serialize()
