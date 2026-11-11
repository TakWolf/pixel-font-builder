from copy import copy, deepcopy

from pixel_font_builder import Glyph, MonoRaster, ColorRaster


def test_is_color_raster_only() -> None:
    glyph = Glyph(
        name='test',
        mono_raster=None,
        color_raster=None,
    )
    assert not glyph.is_color_raster_only

    glyph.mono_raster = MonoRaster()
    assert not glyph.is_color_raster_only

    glyph.color_raster = ColorRaster()
    assert not glyph.is_color_raster_only

    glyph.mono_raster = None
    assert glyph.is_color_raster_only


def test_copy() -> None:
    glyph_1 = Glyph(
        name='test',
        advance_width=1,
        advance_height=2,
        mono_raster=MonoRaster(
            horizontal_offset=(3, 4),
            vertical_offset=(5, 6),
            bitmap=[[1, 0, 0, 1]],
        ),
        color_raster=ColorRaster(
            horizontal_offset=(7, 8),
            vertical_offset=(9, 10),
            bitmap=[[(255, 0, 0, 255), (0, 0, 0, 0), (0, 255, 0, 128), (0, 0, 255, 255)]],
        ),
    )
    glyph_2 = copy(glyph_1)

    assert glyph_1 == glyph_2
    assert glyph_1 is not glyph_2
    assert glyph_1.mono_raster is glyph_2.mono_raster
    assert glyph_1.color_raster is glyph_2.color_raster


def test_deepcopy() -> None:
    glyph_1 = Glyph(
        name='test',
        advance_width=1,
        advance_height=2,
        mono_raster=MonoRaster(
            horizontal_offset=(3, 4),
            vertical_offset=(5, 6),
            bitmap=[[1, 0, 0, 1]],
        ),
        color_raster=ColorRaster(
            horizontal_offset=(7, 8),
            vertical_offset=(9, 10),
            bitmap=[[(255, 0, 0, 255), (0, 0, 0, 0), (0, 255, 0, 128), (0, 0, 255, 255)]],
        ),
    )
    glyph_2 = deepcopy(glyph_1)

    assert glyph_1 == glyph_2
    assert glyph_1 is not glyph_2
    assert glyph_1.mono_raster is not glyph_2.mono_raster
    assert glyph_1.color_raster is not glyph_2.color_raster


def test_eq() -> None:
    glyph_1 = Glyph(
        name='test',
        advance_width=1,
        advance_height=2,
        mono_raster=MonoRaster(
            horizontal_offset=(3, 4),
            vertical_offset=(5, 6),
            bitmap=[[1, 0, 0, 1]],
        ),
        color_raster=ColorRaster(
            horizontal_offset=(7, 8),
            vertical_offset=(9, 10),
            bitmap=[[(255, 0, 0, 255), (0, 0, 0, 0), (0, 255, 0, 128), (0, 0, 255, 255)]],
        ),
    )
    glyph_2 = Glyph(
        name='test',
        advance_width=1,
        advance_height=2,
        mono_raster=MonoRaster(
            horizontal_offset=(3, 4),
            vertical_offset=(5, 6),
            bitmap=[[1, 0, 0, 1]],
        ),
        color_raster=ColorRaster(
            horizontal_offset=(7, 8),
            vertical_offset=(9, 10),
            bitmap=[[(255, 0, 0, 255), (0, 0, 0, 0), (0, 255, 0, 128), (0, 0, 255, 255)]],
        ),
    )
    assert glyph_1 == glyph_2
