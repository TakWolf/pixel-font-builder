from collections.abc import Mapping, Sequence

from fontTools.ttLib.tables.E_B_D_T_ import ebdt_bitmap_format_1, ebdt_bitmap_format_2, ebdt_bitmap_format_5, ebdt_bitmap_format_6, ebdt_bitmap_format_7
from fontTools.ttLib.tables.E_B_L_C_ import Strike, eblc_index_sub_table_1, eblc_index_sub_table_2, eblc_index_sub_table_5

from pixel_font_builder.glyph import Glyph, MonoRaster
from pixel_font_builder.metric import FontMetric
from pixel_font_builder.opentype.bitmap.xbdt import RasterGlyph, create_bitmap_size_table, create_big_glyph_metrics, create_small_glyph_metrics

GlyphBitmapFormat = ebdt_bitmap_format_1 | ebdt_bitmap_format_2 | ebdt_bitmap_format_5 | ebdt_bitmap_format_6 | ebdt_bitmap_format_7
BigMetricsSignature = tuple[int, int, int, int, int, int, int, int]
GroupSignature = tuple[bool, int]


def _pack_bitmap_row(bitmap_row: list[int]) -> bytes:
    data = bytearray()
    b = 0
    bit_count = 0

    for pixel in bitmap_row:
        b = (b << 1) | (1 if pixel != 0 else 0)
        bit_count += 1
        if bit_count == 8:
            data.append(b)
            b = 0
            bit_count = 0

    if bit_count > 0:
        data.append(b << (8 - bit_count))

    return bytes(data)


def _create_bitmap_format(glyph: RasterGlyph[MonoRaster], image_format: int) -> GlyphBitmapFormat:
    big_metrics = create_big_glyph_metrics(glyph)
    rows = [_pack_bitmap_row(bitmap_row) for bitmap_row in glyph.raster.bitmap]
    match image_format:
        case 1:
            bitmap_glyph = ebdt_bitmap_format_1(None, None)
            bitmap_glyph.metrics = create_small_glyph_metrics(glyph)
        case 2:
            bitmap_glyph = ebdt_bitmap_format_2(None, None)
            bitmap_glyph.metrics = create_small_glyph_metrics(glyph)
        case 6:
            bitmap_glyph = ebdt_bitmap_format_6(None, None)
            bitmap_glyph.metrics = big_metrics
        case 7:
            bitmap_glyph = ebdt_bitmap_format_7(None, None)
            bitmap_glyph.metrics = big_metrics
        case _:
            bitmap_glyph = ebdt_bitmap_format_5(None, None)
    bitmap_glyph.setRows(rows, bitDepth=1, metrics=big_metrics)
    return bitmap_glyph


def _select_image_format(glyphs: Sequence[RasterGlyph[MonoRaster]], use_big_metrics: bool) -> int:
    byte_aligned = all(glyph.raster.width % 8 == 0 for glyph in glyphs)
    if use_big_metrics:
        return 6 if byte_aligned else 7
    return 1 if byte_aligned else 2


def _bitmap_data_size(glyph: RasterGlyph[MonoRaster], image_format: int) -> int:
    if image_format in (1, 6):
        return ((glyph.raster.width + 7) // 8) * glyph.raster.height
    return (glyph.raster.width * glyph.raster.height + 7) // 8


def _big_metrics_signature(glyph: RasterGlyph[MonoRaster]) -> BigMetricsSignature:
    metrics = create_big_glyph_metrics(glyph)
    return (
        metrics.height,
        metrics.width,
        metrics.horiBearingX,
        metrics.horiBearingY,
        metrics.horiAdvance,
        metrics.vertBearingX,
        metrics.vertBearingY,
        metrics.vertAdvance,
    )


def _group_signature(glyph: RasterGlyph[MonoRaster], use_big_metrics: bool) -> GroupSignature:
    image_format = _select_image_format([glyph], use_big_metrics)
    return use_big_metrics, image_format


def _uses_consecutive_glyph_ids(glyph_names: Sequence[str], name_to_glyph_id: Mapping[str, int]) -> bool:
    glyph_ids = [name_to_glyph_id[glyph_name] for glyph_name in glyph_names]
    return glyph_ids == list(range(glyph_ids[0], glyph_ids[-1] + 1))


def _append_index_sub_table(
        strike: Strike,
        glyphs: Sequence[RasterGlyph[MonoRaster]],
        glyph_names: Sequence[str],
        name_to_glyph_id: Mapping[str, int],
        use_big_metrics: bool,
) -> int:
    image_format = _select_image_format(glyphs, use_big_metrics)
    if use_big_metrics:
        first_big_metrics_signature = _big_metrics_signature(glyphs[0])
        can_share_big_metrics = all(_big_metrics_signature(glyph) == first_big_metrics_signature for glyph in glyphs[1:])
        first_image_size = _bitmap_data_size(glyphs[0], image_format)
        can_share_image_size = can_share_big_metrics and all(_bitmap_data_size(glyph, image_format) == first_image_size for glyph in glyphs[1:])
        if len(glyphs) > 1 and can_share_image_size:
            if _uses_consecutive_glyph_ids(glyph_names, name_to_glyph_id):
                index_sub_table = eblc_index_sub_table_2(None, None)
                index_sub_table.indexFormat = 2
            else:
                index_sub_table = eblc_index_sub_table_5(None, None)
                index_sub_table.indexFormat = 5
            index_sub_table.imageFormat = 5
            index_sub_table.imageDataOffset = 0
            index_sub_table.names = glyph_names
            index_sub_table.metrics = create_big_glyph_metrics(glyphs[0])
            index_sub_table.imageSize = first_image_size
        else:
            index_sub_table = eblc_index_sub_table_1(None, None)
            index_sub_table.indexFormat = 1
            index_sub_table.imageFormat = image_format
            index_sub_table.imageDataOffset = 0
            index_sub_table.names = glyph_names
    else:
        index_sub_table = eblc_index_sub_table_1(None, None)
        index_sub_table.indexFormat = 1
        index_sub_table.imageFormat = image_format
        index_sub_table.imageDataOffset = 0
        index_sub_table.names = glyph_names

    strike.indexSubTables.append(index_sub_table)
    return index_sub_table.imageFormat


def create_bitmap_strike_data(
        font_metric: FontMetric,
        glyph_order: Sequence[str],
        name_to_glyph: Mapping[str, Glyph],
        has_vertical_metrics: bool,
) -> tuple[Strike, dict[str, GlyphBitmapFormat]]:
    name_to_glyph_id = {
        glyph_name: glyph_id
        for glyph_id, glyph_name in enumerate(glyph_order)
    }
    glyph_order = [
        glyph_name
        for glyph_name in glyph_order
        if glyph_name == '.notdef' or not name_to_glyph[glyph_name].is_color_raster_only
    ]
    name_to_mono_glyph = {
        glyph_name: RasterGlyph.create_mono(name_to_glyph[glyph_name])
        for glyph_name in glyph_order
    }
    use_big_metrics = has_vertical_metrics

    strike = Strike()
    strike.bitmapSizeTable = create_bitmap_size_table(font_metric, name_to_mono_glyph, has_vertical_metrics, 1)

    strike_data = {}

    current_glyphs = []
    current_names = []
    current_signature = None
    name_to_image_format = {}

    for glyph_name in glyph_order:
        glyph = name_to_mono_glyph[glyph_name]
        signature = _group_signature(glyph, use_big_metrics)
        if current_signature is None or current_signature == signature:
            current_glyphs.append(glyph)
            current_names.append(glyph_name)
        else:
            image_format = _append_index_sub_table(strike, current_glyphs, current_names, name_to_glyph_id, use_big_metrics)
            for name in current_names:
                name_to_image_format[name] = image_format
            current_glyphs = [glyph]
            current_names = [glyph_name]
        current_signature = signature

    if current_names:
        image_format = _append_index_sub_table(strike, current_glyphs, current_names, name_to_glyph_id, use_big_metrics)
        for name in current_names:
            name_to_image_format[name] = image_format

    for glyph_name in glyph_order:
        glyph = name_to_mono_glyph[glyph_name]
        strike_data[glyph_name] = _create_bitmap_format(glyph, name_to_image_format[glyph_name])

    return strike, strike_data
