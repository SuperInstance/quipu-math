# quipu-math

> Incan knotted cord mathematics — encode, decode, compute, and visualize numbers as quipu.

## What This Does

`quipu-math` implements the Incan quipu number system in code. It encodes decimal numbers as sequences of knots (long knots, figure-eight knots, single knots) on colored cords, performs arithmetic on quipu-encoded values, detects corruption, and renders quipu as SVG diagrams. Use it for educational math visualization, as a novel encoding scheme, or to explore non-positional number representations.

## The Cultural Root

Quipu (also khipu) were Incan recording devices made of knotted cords. A primary cord held pendant cords, each encoding a number through knot sequences: long knots (multiple turns) for digits 2–9, figure-eight knots for 1, single knots for 1 in higher positions, and absence of knots for 0. Colors encoded categories. The mathematical insight: **knots are a positional decimal system encoded in a tactile medium** — the same math as Arabic numerals, but expressed through topology rather than ink.

## Install

```bash
pip install quipu-math
```

## Quick Start

```python
from quipumath.knot import encode_number, decode_number, KnotType
from quipumath.cord import Cord, CordTree
from quipumath.calculator import add_quipus, subtract_quipus, multiply_quipus
from quipumath.checksum import checksum, detect_corruption
from quipumath.visualize import to_svg, annotate

# Encode and decode numbers
knots = encode_number(135)
# [KnotNode(LONG, digit=5, pos=0), KnotNode(FIGURE_EIGHT, digit=3, pos=1), ...]
print(decode_number(knots))  # 135

# Build a quipu (cord tree)
tree = CordTree()
tree.add_pendant(Cord(color="red", knots=encode_number(42)))
tree.add_pendant(Cord(color="blue", knots=encode_number(17)))

# Arithmetic on quipu trees
tree2 = CordTree()
tree2.add_pendant(Cord(color="green", knots=encode_number(10)))
result = add_quipus(tree, tree2)
print(result.pendant_cords[0].value)  # 52

# Checksums and corruption detection
cs = checksum(tree.pendant_cords[0].knots)
print(f"Checksum: {cs}")

# Visualize as SVG
svg = to_svg(tree)
with open("quipu.svg", "w") as f:
    f.write(svg)

# Text annotation
print(annotate(tree.pendant_cords[0]))
# Cord(color='red', value=42)
#   Knot 0: type=LONG, turns=2, digit=2
#   Knot 1: type=SINGLE, turns=0, digit=4
```

## API Reference

### `knot` module

#### `KnotType` (enum)
`SINGLE`, `FIGURE_EIGHT`, `LONG`, `EMPTY` — the four knot types.

#### `KnotNode`
```python
@dataclass
class KnotNode:
    knot: KnotType
    digit_value: int    # The decimal digit (0-9)
    position: int       # Decimal position (0=units, 1=tens, 2=hundreds...)
    turns: int          # Number of turns (meaningful for LONG knots)
```

#### `encode_number(n) → list[KnotNode]`
Encode a non-negative integer as a sequence of knots.

#### `decode_number(knots) → int`
Decode a knot sequence back to an integer.

### `cord` module

#### `Cord`
```python
@dataclass
class Cord:
    color: str                    # Color name (red, blue, green, etc.)
    knots: list[KnotNode]         # Knot sequence
    position: int = 0             # Position on main cord
    children: list[Cord] = field(default_factory=list)

    @property
    def value(self) -> int  # Decoded numeric value
```

#### `CordTree`
```python
class CordTree:
    pendant_cords: list[Cord]

    def add_pendant(self, cord: Cord) -> None
    def total_value(self) -> int
    def to_dict(self) -> dict
    @classmethod
    def from_dict(cls, d: dict) -> CordTree
```

### `weave` module

#### `weave(cord1, cord2) → Cord`
Interleave two cords into a woven cord. Values are multiplexed.

#### `unweave(cord) → tuple[Cord, Cord]`
Split a woven cord back into its two original cords.

#### `is_associative(a, b, c) → bool`
Verify that weaving is associative for three cords.

### `calculator` module

#### `add_quipus(tree_a, tree_b) → CordTree`
Element-wise addition of two quipu trees. Shorter tree is zero-padded.

#### `subtract_quipus(tree_a, tree_b) → CordTree`
Element-wise subtraction. Raises `ValueError` if any result is negative.

#### `multiply_quipus(tree_a, tree_b) → CordTree`
Element-wise multiplication.

### `checksum` module

#### `checksum(knots) → int`
Sum of all digit values in the knot sequence.

#### `detect_corruption(original, copy) → CorruptionReport`
Compare two cord trees and report discrepancies.

### `visualize` module

#### `to_svg(cord_tree) → str`
Render a CordTree as an SVG string with horizontal main cord, vertical pendant cords, and circles sized by digit value.

#### `annotate(cord, values=None) → str`
Produce a multi-line text annotation of a cord's knot structure.

## How It Works

**Encoding:** The `encode_number` function decomposes an integer into decimal digits (least significant first). Each digit maps to a knot type: 0 → EMPTY (absent), 1 → FIGURE_EIGHT (units position) or SINGLE (higher positions), 2–9 → LONG with `turns = digit_value`.

**Decoding:** Each `KnotNode` contributes `digit_value × 10^position` to the total. Sum all contributions.

**Arithmetic:** The calculator operates element-wise on pendant cords. It decodes values, performs the operation, and re-encodes the result. Trees of different lengths are zero-padded.

**Weaving:** Two cords are interleaved by alternating their knot sequences, creating a single cord that can be split back apart. This is a multiplexing operation on positional encodings.

**Corruption Detection:** Compares checksums and individual knot sequences between an original and a copy, reporting position, expected, and actual values.

## The Math

**Positional Encoding:** A quipu number N = Σᵢ dᵢ × 10ⁱ where dᵢ is the digit at position i, encoded as a specific knot type.

**Checksum:** C = Σ dᵢ — a simple modular checksum for detecting single-digit corruption.

**Weave Algebra:** Weaving defines a binary operation on cords. The `is_associative` function tests whether (a ⊕ b) ⊕ c = a ⊕ (b ⊕ c) for the multiplexing operation.

**Element-wise Arithmetic:** For trees A = [a₁, a₂, ...] and B = [b₁, b₂, ...]: A + B = [a₁+b₁, a₂+b₂, ...], analogously for subtraction and multiplication.

## License

MIT
