from copy import copy, deepcopy

from pixel_font_builder.opentype import CircleDotOutlinesPainter


def test_copy():
    painter_1 = CircleDotOutlinesPainter(radius=1)
    painter_2 = copy(painter_1)
    painter_3 = deepcopy(painter_1)

    assert painter_1 == painter_2
    assert painter_1 == painter_3
    assert painter_1 is not painter_2
    assert painter_1 is not painter_3


def test_eq():
    painter_1 = CircleDotOutlinesPainter(radius=1)
    painter_2 = CircleDotOutlinesPainter(radius=1)
    assert painter_1 == painter_2
