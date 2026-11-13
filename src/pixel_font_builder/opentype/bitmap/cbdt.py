from collections.abc import Mapping, Sequence

from fontTools.ttLib.tables.C_B_D_T_ import cbdt_bitmap_format_17, cbdt_bitmap_format_18
from fontTools.ttLib.tables.E_B_L_C_ import Strike, eblc_index_sub_table_1

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.metric import FontMetric
from pixel_font_builder.opentype.bitmap.xbdt import RasterGlyph, create_bitmap_size_table, create_big_glyph_metrics, create_small_glyph_metrics
from pixel_font_builder.utils.png import encode_png_rgba

ColorBitmapFormat = cbdt_bitmap_format_17 | cbdt_bitmap_format_18

_GLYPH_METRICS_UNSIGNED_FIELDS = {
    'height',
    'width',
    'horiAdvance',
    'vertAdvance',
    'Advance',
}

_GLYPH_METRICS_SIGNED_FIELDS = {
    'horiBearingX',
    'horiBearingY',
    'vertBearingX',
    'vertBearingY',
    'BearingX',
    'BearingY',
}


def _check_integer(value: int, minimum: int, maximum: int, field: str) -> None:
    if not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f'CBDT {field} must be an integer in [{minimum}, {maximum}], got {value!r}')


def create_color_bitmap_strike_data(
        font_metric: FontMetric,
        glyph_order: Sequence[str],
        name_to_glyph: Mapping[str, Glyph],
        has_vertical_metrics: bool,
) -> tuple[Strike, dict[str, ColorBitmapFormat]] | None:
    glyph_order = [
        glyph_name
        for glyph_name in glyph_order
        if name_to_glyph[glyph_name].color_raster is not None
    ]
    if not glyph_order:
        return None

    _check_integer(font_metric.font_size, 1, 255, 'pixels per em')

    name_to_color_glyph = {
        glyph_name: RasterGlyph.create_color(
            name_to_glyph[glyph_name],
            ensure_non_empty_bitmap=True,
        )
        for glyph_name in glyph_order
    }

    strike = Strike()
    strike.bitmapSizeTable = create_bitmap_size_table(font_metric, name_to_color_glyph, has_vertical_metrics, 32)

    for field, value in vars(strike.bitmapSizeTable.hori).items():
        minimum, maximum = (0, 255) if field == 'widthMax' else (-128, 127)
        _check_integer(value, minimum, maximum, f'horizontal sbit line metric {field}')

    if has_vertical_metrics:
        for field, value in vars(strike.bitmapSizeTable.vert).items():
            minimum, maximum = (0, 255) if field == 'widthMax' else (-128, 127)
            _check_integer(value, minimum, maximum, f'vertical sbit line metric {field}')

    index_sub_table = eblc_index_sub_table_1(None, None)
    index_sub_table.indexFormat = 1
    index_sub_table.imageFormat = 18 if has_vertical_metrics else 17
    index_sub_table.imageDataOffset = 0
    index_sub_table.names = glyph_order
    strike.indexSubTables.append(index_sub_table)

    strike_data = {}
    for glyph_name in glyph_order:
        glyph = name_to_color_glyph[glyph_name]

        if has_vertical_metrics:
            bitmap_glyph = cbdt_bitmap_format_18(None, None)
            bitmap_glyph.metrics = create_big_glyph_metrics(glyph)
        else:
            bitmap_glyph = cbdt_bitmap_format_17(None, None)
            bitmap_glyph.metrics = create_small_glyph_metrics(glyph)

        for field, value in vars(bitmap_glyph.metrics).items():
            if field in _GLYPH_METRICS_UNSIGNED_FIELDS:
                _check_integer(value, 0, 255, f'{field} for glyph {glyph_name!r}')

            if field in _GLYPH_METRICS_SIGNED_FIELDS:
                _check_integer(value, -128, 127, f'{field} for glyph {glyph_name!r}')

        bitmap_glyph.imageData = encode_png_rgba(glyph.raster.width, glyph.raster.height, glyph.raster.bitmap)
        strike_data[glyph_name] = bitmap_glyph

    return strike, strike_data
