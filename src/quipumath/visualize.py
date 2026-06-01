"""SVG visualization of quipu cord trees.

Generates SVG strings rendering a CordTree as a visual quipu with
horizontal main cord, vertical pendant cords, and knots rendered as
circles sized by digit value.
"""

from __future__ import annotations

from quipumath.cord import Cord, CordTree
from quipumath.knot import KnotNode


def to_svg(cord_tree: CordTree) -> str:
    """Render a CordTree as an SVG string.

    The main cord is drawn horizontally at the top. Pendant cords hang
    vertically below it. Knots are shown as circles whose size reflects
    the digit value. Colors are applied from cord metadata.

    Args:
        cord_tree: The cord tree to visualize.

    Returns:
        SVG string.
    """
    num_pendants = len(cord_tree.pendant_cords)
    spacing = 60
    margin_x = 40
    margin_y = 40
    main_y = margin_y
    cord_length = 120
    knot_spacing = 18
    knot_base_r = 4

    width = margin_x * 2 + max(num_pendants, 1) * spacing
    height = margin_y + cord_length + 60

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#faf8f0"/>',
    ]

    # Main cord
    main_x1 = margin_x
    main_x2 = margin_x + max(num_pendants - 1, 0) * spacing if num_pendants > 1 else margin_x + 40
    parts.append(
        f'<line x1="{main_x1}" y1="{main_y}" x2="{main_x2}" y2="{main_y}" '
        f'stroke="#5c3a1e" stroke-width="4" stroke-linecap="round"/>'
    )

    # Pendant cords
    for i, cord in enumerate(cord_tree.pendant_cords):
        px = margin_x + i * spacing
        py_top = main_y
        py_bottom = main_y + cord_length

        # Vertical cord line
        color = _svg_color(cord.color)
        parts.append(
            f'<line x1="{px}" y1="{py_top}" x2="{px}" y2="{py_bottom}" '
            f'stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>'
        )

        # Knots along the pendant (bottom to top: least significant first)
        for j, knot in enumerate(cord.knots):
            ky = py_bottom - 10 - j * knot_spacing
            r = knot_base_r + knot.digit_value * 1.2
            parts.append(
                f'<circle cx="{px}" cy="{ky}" r="{r:.1f}" '
                f'fill="{color}" opacity="0.85"/>'
            )

        # Value label
        parts.append(
            f'<text x="{px}" y="{py_bottom + 18}" '
            f'text-anchor="middle" font-size="11" fill="#333">'
            f"{cord.value}</text>"
        )

    parts.append("</svg>")
    return "\n".join(parts)


def annotate(cord: Cord, values: list[int] | None = None) -> str:
    """Produce a text annotation of a cord's knot structure.

    Args:
        cord: The cord to annotate.
        values: Optional explicit values to label (defaults to knot digit values).

    Returns:
        Multi-line string annotation.
    """
    lines: list[str] = [f"Cord(color={cord.color!r}, value={cord.value})"]
    lines.append(f"  Position: {cord.position}")
    if values is None:
        values = [k.digit_value for k in cord.knots]

    for i, knot in enumerate(cord.knots):
        v = values[i] if i < len(values) else "?"
        lines.append(
            f"  Knot {i}: type={knot.knot.name}, "
            f"turns={knot.turns}, digit={v}"
        )

    if cord.children:
        lines.append(f"  Children: {len(cord.children)}")
        for child in cord.children:
            lines.append(f"    -> {child.color}, value={child.value}")

    return "\n".join(lines)


def _svg_color(name: str) -> str:
    """Map a cord color name to an SVG-compatible color string."""
    palette = {
        "white": "#ddd",
        "red": "#c0392b",
        "blue": "#2980b9",
        "green": "#27ae60",
        "yellow": "#f1c40f",
        "brown": "#8b5e3c",
        "black": "#2c3e50",
        "main": "#5c3a1e",
    }
    if name.startswith("woven:"):
        return "#7d3c98"
    return palette.get(name.lower(), name)
