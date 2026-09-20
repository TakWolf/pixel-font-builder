from copy import copy, deepcopy

from pixel_font_builder.opentype import SquareDotOutlinePainter


def test_copy() -> None:
    painter_1 = SquareDotOutlinePainter(size=1)
    painter_2 = copy(painter_1)
    painter_3 = deepcopy(painter_1)

    assert painter_1 == painter_2
    assert painter_1 == painter_3
    assert painter_1 is not painter_2
    assert painter_1 is not painter_3


def test_eq() -> None:
    painter_1 = SquareDotOutlinePainter(size=1)
    painter_2 = SquareDotOutlinePainter(size=1)
    assert painter_1 == painter_2
