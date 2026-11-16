from collections.abc import Mapping, Sequence

from fontTools.ttLib.tables.C_B_D_T_ import cbdt_bitmap_format_17, cbdt_bitmap_format_18
from fontTools.ttLib.tables.E_B_L_C_ import Strike, eblc_index_sub_table_1

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.metric import FontMetric
from pixel_font_builder.opentype.bitmap.common import RasterGlyph, create_bitmap_size_table, create_big_glyph_metrics, create_small_glyph_metrics
from pixel_font_builder.utils.png import encode_png_rgba

ColorBitmapFormat = cbdt_bitmap_format_17 | cbdt_bitmap_format_18


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

    name_to_color_glyph = {
        glyph_name: RasterGlyph.create_color(
            name_to_glyph[glyph_name],
            ensure_non_empty_bitmap=True,
        )
        for glyph_name in glyph_order
    }

    strike = Strike()
    strike.bitmapSizeTable = create_bitmap_size_table(font_metric, name_to_color_glyph, has_vertical_metrics, 32)

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

        bitmap_glyph.imageData = encode_png_rgba(glyph.raster.width, glyph.raster.height, glyph.raster.bitmap)
        strike_data[glyph_name] = bitmap_glyph

    return strike, strike_data
