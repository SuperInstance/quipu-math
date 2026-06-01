"""Comprehensive tests for quipu-math — 40+ pytest tests."""

import pytest

from quipumath.knot import KnotType, KnotNode, encode_number, decode_knots, checksum
from quipumath.cord import Cord, CordTree
from quipumath.weave import weave, unweave, is_associative
from quipumath.checksum import parity_knots, cross_sums, detect_corruption
from quipumath.visualize import to_svg, annotate
from quipumath.calculator import add_quipus, subtract_quipus, multiply_quipus


# ── Knot encoding / decoding ──────────────────────────────────────────

class TestKnotType:
    def test_single_value(self):
        assert KnotType.single.value == 1

    def test_figure_eight_value(self):
        assert KnotType.figure_eight.value == 1

    def test_knot_node_digit_figure_eight(self):
        kn = KnotNode(knot=KnotType.figure_eight)
        assert kn.digit_value == 1

    def test_knot_node_digit_long(self):
        kn = KnotNode(knot=KnotType.long, turns=7)
        assert kn.digit_value == 7

    def test_knot_node_digit_single(self):
        kn = KnotNode(knot=KnotType.single)
        assert kn.digit_value == 1

    def test_long_with_turns_valid(self):
        kn = KnotType.long_with_turns(5)
        assert kn.turns == 5
        assert kn.knot == KnotType.long

    def test_long_with_turns_invalid(self):
        with pytest.raises(ValueError):
            KnotType.long_with_turns(10)
        with pytest.raises(ValueError):
            KnotType.long_with_turns(1)


class TestEncodeDecode:
    def test_encode_zero(self):
        assert encode_number(0) == []

    def test_encode_one(self):
        knots = encode_number(1)
        assert len(knots) == 1
        assert knots[0].knot == KnotType.figure_eight

    def test_encode_nine(self):
        knots = encode_number(9)
        assert len(knots) == 1
        assert knots[0].knot == KnotType.long
        assert knots[0].turns == 9

    def test_encode_ten(self):
        knots = encode_number(10)
        assert len(knots) == 1
        assert knots[0].knot == KnotType.single

    def test_encode_247(self):
        knots = encode_number(247)
        # digits: 7 (units=0), 4 (tens=1), 2 (hundreds=2)
        assert len(knots) == 3
        by_pos = {k.position: k for k in knots}
        assert by_pos[0].knot == KnotType.long and by_pos[0].turns == 7
        assert by_pos[1].knot == KnotType.long and by_pos[1].turns == 4
        assert by_pos[2].knot == KnotType.long and by_pos[2].turns == 2

    def test_encode_negative_raises(self):
        with pytest.raises(ValueError):
            encode_number(-1)

    def test_decode_empty(self):
        assert decode_knots([]) == 0

    def test_roundtrip_single_digit(self):
        for n in range(1, 10):
            assert decode_knots(encode_number(n)) == n

    def test_roundtrip_large(self):
        for n in [0, 1, 10, 42, 100, 247, 1000, 9999]:
            assert decode_knots(encode_number(n)) == n

    def test_checksum_empty(self):
        assert checksum([]) == 0

    def test_checksum_value(self):
        # encode_number(247) → digits 7, 4, 2 → sum = 13
        knots = encode_number(247)
        assert checksum(knots) == 13


# ── Cord and CordTree ─────────────────────────────────────────────────

class TestCord:
    def test_cord_value(self):
        cord = Cord(knots=encode_number(42))
        assert cord.value == 42

    def test_cord_default_color(self):
        cord = Cord()
        assert cord.color == "white"

    def test_cord_add_child(self):
        parent = Cord(color="red", knots=encode_number(10))
        child = Cord(color="blue", knots=encode_number(3))
        parent.add_child(child)
        assert len(parent.children) == 1
        assert parent.children[0].color == "blue"

    def test_cord_serialization_roundtrip(self):
        cord = Cord(color="red", knots=encode_number(55), position=2)
        cord.add_child(Cord(color="green", knots=encode_number(3)))
        d = cord.to_dict()
        restored = Cord.from_dict(d)
        assert restored.color == "red"
        assert restored.value == 55
        assert len(restored.children) == 1
        assert restored.children[0].value == 3


class TestCordTree:
    def test_empty_tree(self):
        tree = CordTree()
        assert len(tree.pendant_cords) == 0

    def test_add_pendant(self):
        tree = CordTree()
        tree.add_pendant(Cord(color="red", knots=encode_number(10)))
        tree.add_pendant(Cord(color="blue", knots=encode_number(20)))
        assert len(tree.pendant_cords) == 2
        assert tree.pendant_cords[0].position == 0
        assert tree.pendant_cords[1].position == 1

    def test_total_value(self):
        tree = CordTree()
        tree.add_pendant(Cord(knots=encode_number(100)))
        tree.add_pendant(Cord(knots=encode_number(47)))
        assert tree.total_value() == 147

    def test_serialize_deserialize(self):
        tree = CordTree()
        tree.add_pendant(Cord(color="red", knots=encode_number(30)))
        tree.add_pendant(Cord(color="blue", knots=encode_number(12)))
        json_str = tree.serialize()
        restored = CordTree.deserialize(json_str)
        assert len(restored.pendant_cords) == 2
        assert restored.pendant_cords[0].value == 30
        assert restored.pendant_cords[1].value == 12

    def test_tree_equality(self):
        tree1 = CordTree()
        tree1.add_pendant(Cord(color="red", knots=encode_number(5)))
        tree2 = CordTree()
        tree2.add_pendant(Cord(color="red", knots=encode_number(5)))
        assert tree1 == tree2


# ── Weave / Unweave ───────────────────────────────────────────────────

class TestWeave:
    def test_weave_values(self):
        c1 = Cord(color="red", knots=encode_number(3))
        c2 = Cord(color="blue", knots=encode_number(7))
        woven = weave(c1, c2)
        assert woven.value == 3 * 10000 + 7

    def test_unweave_roundtrip(self):
        c1 = Cord(color="red", knots=encode_number(42))
        c2 = Cord(color="blue", knots=encode_number(13))
        woven = weave(c1, c2)
        r1, r2 = unweave(woven)
        assert r1.value == 42
        assert r2.value == 13

    def test_unweave_preserves_colors(self):
        c1 = Cord(color="red", knots=encode_number(5))
        c2 = Cord(color="green", knots=encode_number(8))
        woven = weave(c1, c2)
        r1, r2 = unweave(woven)
        assert r1.color == "red"
        assert r2.color == "green"

    def test_associativity(self):
        # weave is NOT strictly associative with this encoding,
        # so is_associative should return False for these values.
        a = Cord(color="a", knots=encode_number(2))
        b = Cord(color="b", knots=encode_number(3))
        c = Cord(color="c", knots=encode_number(4))
        assert not is_associative(a, b, c)

    def test_associativity_trivial(self):
        # With zeros, associativity holds trivially
        a = Cord(color="a", knots=encode_number(0))
        b = Cord(color="b", knots=encode_number(0))
        c = Cord(color="c", knots=encode_number(0))
        assert is_associative(a, b, c)


# ── Checksum / Error detection ────────────────────────────────────────

class TestChecksum:
    def test_parity_knots(self):
        cord = Cord(knots=encode_number(247))  # digits 7, 4, 2 → sum=13 → 13%10=3
        assert parity_knots(cord) == 3

    def test_parity_zero(self):
        cord = Cord(knots=[])  # value 0
        assert parity_knots(cord) == 0

    def test_cross_sums(self):
        tree = CordTree()
        tree.add_pendant(Cord(color="red", knots=encode_number(10)))   # digit 1, parity=1
        tree.add_pendant(Cord(color="blue", knots=encode_number(20)))  # digit 2, parity=2
        cs = cross_sums(tree)
        assert cs["total"] == 30
        assert cs["count"] == 2
        assert cs["parity"] == 3

    def test_detect_no_corruption(self):
        tree1 = CordTree()
        tree1.add_pendant(Cord(color="red", knots=encode_number(10)))
        tree2 = CordTree()
        tree2.add_pendant(Cord(color="red", knots=encode_number(10)))
        errors = detect_corruption(tree1, tree2)
        assert errors == []

    def test_detect_value_corruption(self):
        tree1 = CordTree()
        tree1.add_pendant(Cord(color="red", knots=encode_number(10)))
        tree2 = CordTree()
        tree2.add_pendant(Cord(color="red", knots=encode_number(20)))
        errors = detect_corruption(tree1, tree2)
        assert any("Value mismatch" in e for e in errors)

    def test_detect_count_corruption(self):
        tree1 = CordTree()
        tree1.add_pendant(Cord(color="red", knots=encode_number(10)))
        tree2 = CordTree()
        tree2.add_pendant(Cord(color="red", knots=encode_number(10)))
        tree2.add_pendant(Cord(color="blue", knots=encode_number(5)))
        errors = detect_corruption(tree1, tree2)
        assert any("count" in e.lower() for e in errors)

    def test_detect_color_corruption(self):
        tree1 = CordTree()
        tree1.add_pendant(Cord(color="red", knots=encode_number(10)))
        tree2 = CordTree()
        tree2.add_pendant(Cord(color="blue", knots=encode_number(10)))
        errors = detect_corruption(tree1, tree2)
        assert any("Color mismatch" in e for e in errors)


# ── Visualization ─────────────────────────────────────────────────────

class TestVisualize:
    def test_svg_contains_svg_tag(self):
        tree = CordTree()
        result = to_svg(tree)
        assert "<svg" in result
        assert "</svg>" in result

    def test_svg_with_pendants(self):
        tree = CordTree()
        tree.add_pendant(Cord(color="red", knots=encode_number(42)))
        tree.add_pendant(Cord(color="blue", knots=encode_number(7)))
        svg = to_svg(tree)
        assert "circle" in svg
        assert "line" in svg

    def test_annotate_output(self):
        cord = Cord(color="red", knots=encode_number(42), position=0)
        text = annotate(cord)
        assert "red" in text
        assert "42" in text

    def test_annotate_with_values(self):
        cord = Cord(color="blue", knots=encode_number(7))
        text = annotate(cord, values=[7])
        assert "digit=7" in text

    def test_annotate_with_children(self):
        parent = Cord(color="red", knots=encode_number(10))
        parent.add_child(Cord(color="green", knots=encode_number(3)))
        text = annotate(parent)
        assert "Children: 1" in text


# ── Calculator ─────────────────────────────────────────────────────────

class TestCalculator:
    def test_add_quipus(self):
        a = CordTree()
        a.add_pendant(Cord(knots=encode_number(10)))
        b = CordTree()
        b.add_pendant(Cord(knots=encode_number(25)))
        result = add_quipus(a, b)
        assert result.pendant_cords[0].value == 35

    def test_add_quipus_multiple(self):
        a = CordTree()
        a.add_pendant(Cord(knots=encode_number(10)))
        a.add_pendant(Cord(knots=encode_number(20)))
        b = CordTree()
        b.add_pendant(Cord(knots=encode_number(5)))
        b.add_pendant(Cord(knots=encode_number(15)))
        result = add_quipus(a, b)
        assert result.pendant_cords[0].value == 15
        assert result.pendant_cords[1].value == 35

    def test_subtract_quipus(self):
        a = CordTree()
        a.add_pendant(Cord(knots=encode_number(50)))
        b = CordTree()
        b.add_pendant(Cord(knots=encode_number(20)))
        result = subtract_quipus(a, b)
        assert result.pendant_cords[0].value == 30

    def test_subtract_negative_raises(self):
        a = CordTree()
        a.add_pendant(Cord(knots=encode_number(5)))
        b = CordTree()
        b.add_pendant(Cord(knots=encode_number(10)))
        with pytest.raises(ValueError, match="Negative result"):
            subtract_quipus(a, b)

    def test_multiply_quipus(self):
        a = CordTree()
        a.add_pendant(Cord(knots=encode_number(6)))
        b = CordTree()
        b.add_pendant(Cord(knots=encode_number(7)))
        result = multiply_quipus(a, b)
        assert result.pendant_cords[0].value == 42

    def test_multiply_by_zero(self):
        a = CordTree()
        a.add_pendant(Cord(knots=encode_number(42)))
        b = CordTree()
        b.add_pendant(Cord(knots=[]))  # value 0
        result = multiply_quipus(a, b)
        assert result.pendant_cords[0].value == 0

    def test_add_different_lengths(self):
        a = CordTree()
        a.add_pendant(Cord(knots=encode_number(10)))
        a.add_pendant(Cord(knots=encode_number(20)))
        b = CordTree()
        b.add_pendant(Cord(knots=encode_number(5)))
        result = add_quipus(a, b)
        assert len(result.pendant_cords) == 2
        assert result.pendant_cords[0].value == 15
        assert result.pendant_cords[1].value == 20
