from fontTools.ttLib.tables.BitmapGlyphMetrics import BigGlyphMetrics, SmallGlyphMetrics
from fontTools.ttLib.tables.E_B_D_T_ import ebdt_bitmap_format_1, ebdt_bitmap_format_2, ebdt_bitmap_format_5, ebdt_bitmap_format_6, ebdt_bitmap_format_7
from fontTools.ttLib.tables.E_B_L_C_ import BitmapSizeTable, SbitLineMetrics, Strike, eblc_index_sub_table_1, eblc_index_sub_table_2, eblc_index_sub_table_5

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.metric import LineMetric, FontMetric

GlyphBitmapFormat = ebdt_bitmap_format_1 | ebdt_bitmap_format_2 | ebdt_bitmap_format_5 | ebdt_bitmap_format_6 | ebdt_bitmap_format_7
BigMetricsSignature = tuple[int, int, int, int, int, int, int, int]
GroupSignature = tuple[bool, int]


def _create_horizontal_sbit_line_metrics(
        horizontal_layout: LineMetric,
        name_to_glyph: dict[str, Glyph],
) -> SbitLineMetrics:
    line_metrics = SbitLineMetrics()
    line_metrics.ascender = horizontal_layout.ascent
    line_metrics.descender = horizontal_layout.descent
    line_metrics.widthMax = max((glyph.width for glyph in name_to_glyph.values()), default=0)
    line_metrics.caretSlopeNumerator = 1
    line_metrics.caretSlopeDenominator = 0
    line_metrics.caretOffset = 0
    line_metrics.minOriginSB = min((glyph.horizontal_offset_x for glyph in name_to_glyph.values()), default=0)
    line_metrics.minAdvanceSB = min((glyph.advance_width - glyph.horizontal_offset_x - glyph.width for glyph in name_to_glyph.values()), default=0)
    line_metrics.maxBeforeBL = max((glyph.height + glyph.horizontal_offset_y for glyph in name_to_glyph.values()), default=0)
    line_metrics.minAfterBL = min((glyph.horizontal_offset_y for glyph in name_to_glyph.values()), default=0)
    line_metrics.pad1 = 0
    line_metrics.pad2 = 0
    return line_metrics


def _create_vertical_sbit_line_metrics(
        vertical_layout: LineMetric,
        name_to_glyph: dict[str, Glyph],
) -> SbitLineMetrics:
    line_metrics = SbitLineMetrics()
    line_metrics.ascender = vertical_layout.ascent
    line_metrics.descender = vertical_layout.descent
    line_metrics.widthMax = max((glyph.height for glyph in name_to_glyph.values()), default=0)
    line_metrics.caretSlopeNumerator = 0
    line_metrics.caretSlopeDenominator = 1
    line_metrics.caretOffset = 0
    line_metrics.minOriginSB = min((glyph.vertical_offset_y for glyph in name_to_glyph.values()), default=0)
    line_metrics.minAdvanceSB = min((glyph.advance_height - glyph.vertical_offset_y - glyph.height for glyph in name_to_glyph.values()), default=0)
    line_metrics.maxBeforeBL = max((glyph.vertical_offset_x + glyph.width for glyph in name_to_glyph.values()), default=0)
    line_metrics.minAfterBL = min((glyph.vertical_offset_x for glyph in name_to_glyph.values()), default=0)
    line_metrics.pad1 = 0
    line_metrics.pad2 = 0
    return line_metrics


def _create_bitmap_size_table(
        font_metric: FontMetric,
        has_vertical_metrics: bool,
        name_to_glyph: dict[str, Glyph],
) -> BitmapSizeTable:
    bitmap_size_table = BitmapSizeTable()
    bitmap_size_table.colorRef = 0
    bitmap_size_table.hori = _create_horizontal_sbit_line_metrics(font_metric.horizontal_layout, name_to_glyph)
    bitmap_size_table.vert = _create_vertical_sbit_line_metrics(font_metric.vertical_layout, name_to_glyph)
    bitmap_size_table.ppemX = font_metric.font_size
    bitmap_size_table.ppemY = font_metric.font_size
    bitmap_size_table.bitDepth = 1
    bitmap_size_table.flags = 0b_11 if has_vertical_metrics else 0b_01
    return bitmap_size_table


def _create_big_metrics(glyph: Glyph) -> BigGlyphMetrics:
    metrics = BigGlyphMetrics()
    metrics.height = glyph.height
    metrics.width = glyph.width
    metrics.horiBearingX = glyph.horizontal_offset_x
    metrics.horiBearingY = glyph.height + glyph.horizontal_offset_y
    metrics.horiAdvance = glyph.advance_width
    metrics.vertBearingX = glyph.vertical_offset_x
    metrics.vertBearingY = glyph.vertical_offset_y
    metrics.vertAdvance = glyph.advance_height
    return metrics


def _create_small_metrics(glyph: Glyph) -> SmallGlyphMetrics:
    metrics = SmallGlyphMetrics()
    metrics.height = glyph.height
    metrics.width = glyph.width
    metrics.BearingX = glyph.horizontal_offset_x
    metrics.BearingY = glyph.height + glyph.horizontal_offset_y
    metrics.Advance = glyph.advance_width
    return metrics


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


def _pack_bitmap_rows(glyph: Glyph) -> list[bytes]:
    return [_pack_bitmap_row(bitmap_row) for bitmap_row in glyph.bitmap]


def _create_bitmap_format(glyph: Glyph, image_format: int) -> GlyphBitmapFormat:
    match image_format:
        case 1:
            bitmap_glyph = ebdt_bitmap_format_1(None, None)
            bitmap_glyph.metrics = _create_small_metrics(glyph)
        case 2:
            bitmap_glyph = ebdt_bitmap_format_2(None, None)
            bitmap_glyph.metrics = _create_small_metrics(glyph)
        case 6:
            bitmap_glyph = ebdt_bitmap_format_6(None, None)
            bitmap_glyph.metrics = _create_big_metrics(glyph)
        case 7:
            bitmap_glyph = ebdt_bitmap_format_7(None, None)
            bitmap_glyph.metrics = _create_big_metrics(glyph)
        case _:
            bitmap_glyph = ebdt_bitmap_format_5(None, None)
    bitmap_glyph.setRows(_pack_bitmap_rows(glyph), bitDepth=1, metrics=_create_big_metrics(glyph))
    return bitmap_glyph


def _select_image_format(glyphs: list[Glyph], use_big_metrics: bool) -> int:
    byte_aligned = all(glyph.width % 8 == 0 for glyph in glyphs)
    if use_big_metrics:
        return 6 if byte_aligned else 7
    return 1 if byte_aligned else 2


def _bitmap_data_size(glyph: Glyph, image_format: int) -> int:
    if image_format in (1, 6):
        return ((glyph.width + 7) // 8) * glyph.height
    return (glyph.width * glyph.height + 7) // 8


def _big_metrics_signature(glyph: Glyph) -> BigMetricsSignature:
    metrics = _create_big_metrics(glyph)
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


def _group_signature(glyph: Glyph, use_big_metrics: bool) -> GroupSignature:
    image_format = _select_image_format([glyph], use_big_metrics)
    return use_big_metrics, image_format


def _uses_consecutive_glyph_ids(glyph_names: list[str], name_to_glyph_id: dict[str, int]) -> bool:
    glyph_ids = [name_to_glyph_id[glyph_name] for glyph_name in glyph_names]
    return glyph_ids == list(range(glyph_ids[0], glyph_ids[-1] + 1))


def _append_index_sub_table(
        strike: Strike,
        use_big_metrics: bool,
        glyphs: list[Glyph],
        glyph_names: list[str],
        name_to_glyph_id: dict[str, int],
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
            index_sub_table.metrics = _create_big_metrics(glyphs[0])
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
        has_vertical_metrics: bool,
        glyph_order: list[str],
        name_to_glyph: dict[str, Glyph],
) -> tuple[Strike, dict[str, GlyphBitmapFormat]]:
    use_big_metrics = has_vertical_metrics
    name_to_glyph_id = {glyph_name: glyph_id for glyph_id, glyph_name in enumerate(glyph_order)}

    strike = Strike()
    strike.bitmapSizeTable = _create_bitmap_size_table(font_metric, has_vertical_metrics, name_to_glyph)

    strike_data = {}

    current_glyphs = []
    current_names = []
    current_signature = None
    name_to_image_format = {}

    for glyph_name in glyph_order:
        glyph = name_to_glyph[glyph_name]
        signature = _group_signature(glyph, use_big_metrics)
        if current_signature is None or current_signature == signature:
            current_glyphs.append(glyph)
            current_names.append(glyph_name)
        else:
            image_format = _append_index_sub_table(strike, use_big_metrics, current_glyphs, current_names, name_to_glyph_id)
            for name in current_names:
                name_to_image_format[name] = image_format
            current_glyphs = [glyph]
            current_names = [glyph_name]
        current_signature = signature

    if current_names:
        image_format = _append_index_sub_table(strike, use_big_metrics, current_glyphs, current_names, name_to_glyph_id)
        for name in current_names:
            name_to_image_format[name] = image_format

    for glyph_name in glyph_order:
        glyph = name_to_glyph[glyph_name]
        strike_data[glyph_name] = _create_bitmap_format(glyph, name_to_image_format[glyph_name])

    return strike, strike_data
