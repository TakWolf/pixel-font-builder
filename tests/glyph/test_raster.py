from pixel_font_builder import Raster


def test_raster_1() -> None:
    raster = Raster(
        horizontal_offset=(1, 2),
        vertical_offset=(3, 4),
        bitmap=[
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ],
    )
    assert raster.horizontal_offset_x == 1
    assert raster.horizontal_offset_y == 2
    assert raster.horizontal_offset == (1, 2)
    assert raster.vertical_offset_x == 3
    assert raster.vertical_offset_y == 4
    assert raster.vertical_offset == (3, 4)
    assert raster.width == 4
    assert raster.height == 3
    assert raster.dimensions == (4, 3)

    raster.horizontal_offset = (5, 6)
    assert raster.horizontal_offset_x == 5
    assert raster.horizontal_offset_y == 6

    raster.vertical_offset = (7, 8)
    assert raster.vertical_offset_x == 7
    assert raster.vertical_offset_y == 8


def test_raster_2() -> None:
    raster = Raster()
    assert raster.horizontal_offset == (0, 0)
    assert raster.vertical_offset == (0, 0)
    assert raster.dimensions == (0, 0)
