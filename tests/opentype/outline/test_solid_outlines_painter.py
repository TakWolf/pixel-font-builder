from copy import copy, deepcopy

from pixel_font_builder.opentype import SolidOutlinesPainter


def test_copy():
    painter_1 = SolidOutlinesPainter()
    painter_2 = copy(painter_1)
    painter_3 = deepcopy(painter_1)

    assert painter_1 == painter_2
    assert painter_1 == painter_3
    assert painter_1 is painter_2
    assert painter_1 is painter_3


def test_eq():
    painter_1 = SolidOutlinesPainter()
    painter_2 = SolidOutlinesPainter()
    assert painter_1 == painter_2
