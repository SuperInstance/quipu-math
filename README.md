# quipu-math

Mathematics of Incan knotted cord (quipu) data structures.

Quipu are Incan knotted cord recording devices. This package implements the
**mathematics** of knotted data structures: encoding numbers as knot sequences,
building cord hierarchies, arithmetic on quipus, error detection via parity
knots, and SVG visualization.

## Installation

```bash
pip install quipu-math
```

## Quick Start

```python
from quipumath import encode_number, decode_knots, Cord, CordTree

# Encode a number as a knot sequence
knots = encode_number(247)   # [KnotType.long, KnotType.figure_eight, KnotType.long]

# Decode back
n = decode_knots(knots)      # 247

# Build a cord tree
tree = CordTree()
tree.add_pendant(Cord(color="red", knots=encode_number(100)))
tree.add_pendant(Cord(color="blue", knots=encode_number(47)))
```

## Modules

- **knot** — Knot types and number encoding/decoding
- **cord** — Cord and CordTree data structures with serialization
- **weave** — Categorical product of cords (weave/unweave)
- **checksum** — Incan-style error detection
- **visualize** — SVG rendering of cord trees
- **calculator** — Quipu arithmetic (add, subtract, multiply)

## License

MIT
