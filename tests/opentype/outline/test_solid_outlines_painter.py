from copy import copy, deepcopy

from pixel_font_builder.opentype import SolidOutlinesPainter


def _normalize_pixel_outline(outline: list[tuple[int, int]]) -> list[tuple[int, int]]:
    start = min(range(len(outline)), key=lambda index: (outline[index][1], outline[index][0]))
    return outline[start:] + outline[:start]


def _normalize_pixel_outlines(outlines: list[list[tuple[int, int]]]) -> list[list[tuple[int, int]]]:
    outlines = [_normalize_pixel_outline(outline) for outline in outlines]
    outlines.sort(key=lambda outline: outline[0])
    return outlines


def test_create_pixel_outlines():
    assert _normalize_pixel_outlines(SolidOutlinesPainter.create_pixel_outlines([])) == []
    assert _normalize_pixel_outlines(SolidOutlinesPainter.create_pixel_outlines([
        [1],
    ])) == [
        [(0, 0), (1, 0), (1, 1), (0, 1)],
    ]
    assert _normalize_pixel_outlines(SolidOutlinesPainter.create_pixel_outlines([
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ])) == [
        [(0, 0), (7, 0), (7, 7), (0, 7)],
    ]
    assert _normalize_pixel_outlines(SolidOutlinesPainter.create_pixel_outlines([
        [1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ])) == [
        [(0, 0), (7, 0), (7, 7), (0, 7)],
        [(1, 1), (1, 6), (6, 6), (6, 1)],
        [(2, 2), (5, 2), (5, 5), (2, 5)],
        [(3, 3), (3, 4), (4, 4), (4, 3)],
    ]
    assert _normalize_pixel_outlines(SolidOutlinesPainter.create_pixel_outlines([
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
    ])) == [
        [(3, 0), (4, 0), (4, 3), (7, 3), (7, 4), (4, 4), (4, 7), (3, 7), (3, 4), (0, 4), (0, 3), (3, 3)],
    ]
    assert _normalize_pixel_outlines(SolidOutlinesPainter.create_pixel_outlines([
        [1, 1, 1, 0, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 1],
    ])) == [
        [(0, 0), (3, 0), (3, 3), (0, 3)],
        [(0, 4), (3, 4), (3, 7), (0, 7)],
        [(4, 0), (7, 0), (7, 3), (4, 3)],
        [(4, 4), (7, 4), (7, 7), (4, 7)],
    ]
    assert _normalize_pixel_outlines(SolidOutlinesPainter.create_pixel_outlines([
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ])) == [
        [(1, 7), (2, 7), (2, 9), (6, 9), (6, 7), (7, 7), (7, 14), (6, 14), (6, 10), (2, 10), (2, 14), (1, 14)],
        [(2, 5), (3, 5), (3, 7), (2, 7)],
        [(3, 4), (5, 4), (5, 5), (3, 5)],
        [(5, 5), (6, 5), (6, 7), (5, 7)],
    ]


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
