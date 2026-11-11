from copy import copy, deepcopy

from pixel_font_builder import ColorRaster


def test_copy() -> None:
    raster_1 = ColorRaster(
        horizontal_offset=(1, 2),
        vertical_offset=(3, 4),
        bitmap=[[(255, 0, 0, 255), (0, 0, 0, 0), (0, 255, 0, 128), (0, 0, 255, 255)]],
    )
    raster_2 = copy(raster_1)

    assert raster_1 == raster_2
    assert raster_1 is not raster_2
    assert raster_1.bitmap is raster_2.bitmap


def test_deepcopy() -> None:
    raster_1 = ColorRaster(
        horizontal_offset=(1, 2),
        vertical_offset=(3, 4),
        bitmap=[[(255, 0, 0, 255), (0, 0, 0, 0), (0, 255, 0, 128), (0, 0, 255, 255)]],
    )
    raster_2 = deepcopy(raster_1)

    assert raster_1 == raster_2
    assert raster_1 is not raster_2
    assert raster_1.bitmap is not raster_2.bitmap

    for bitmap_row_1, bitmap_row_2 in zip(raster_1.bitmap, raster_2.bitmap):
        assert bitmap_row_1 is not bitmap_row_2


def test_eq() -> None:
    raster_1 = ColorRaster(
        horizontal_offset=(1, 2),
        vertical_offset=(3, 4),
        bitmap=[[(255, 0, 0, 255), (0, 0, 0, 0), (0, 255, 0, 128), (0, 0, 255, 255)]],
    )
    raster_2 = ColorRaster(
        horizontal_offset=(1, 2),
        vertical_offset=(3, 4),
        bitmap=[[(255, 0, 0, 255), (0, 0, 0, 0), (0, 255, 0, 128), (0, 0, 255, 255)]],
    )
    assert raster_1 == raster_2
