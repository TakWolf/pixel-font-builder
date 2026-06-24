from __future__ import annotations

from collections.abc import Mapping
from typing import TypeAlias

from fontTools.ttLib.tables.BitmapGlyphMetrics import BigGlyphMetrics, SmallGlyphMetrics
from fontTools.ttLib.tables.E_B_D_T_ import ebdt_bitmap_format_1, ebdt_bitmap_format_2, ebdt_bitmap_format_5, ebdt_bitmap_format_6, ebdt_bitmap_format_7
from fontTools.ttLib.tables.E_B_L_C_ import BitmapSizeTable, SbitLineMetrics, Strike, eblc_index_sub_table_1, eblc_index_sub_table_2, eblc_index_sub_table_5

import pixel_font_builder
from pixel_font_builder.glyph import Glyph
from pixel_font_builder.opentype.patch._b_d_a_t import table__b_d_a_t
from pixel_font_builder.opentype.patch._b_l_o_c import table__b_l_o_c

BitmapGlyphData: TypeAlias = ebdt_bitmap_format_1 | ebdt_bitmap_format_2 | ebdt_bitmap_format_5 | ebdt_bitmap_format_6 | ebdt_bitmap_format_7
BitmapGroupSignature: TypeAlias = tuple[bool, int, tuple[int, ...] | None, int | None]


def _pack_bitmap_rows(bitmap: list[list[int]]) -> bytes:
    data = bytearray()
    for row in bitmap:
        byte = 0
        bit_count = 0
        for pixel in row:
            byte = (byte << 1) | (1 if pixel else 0)
            bit_count += 1
            if bit_count == 8:
                data.append(byte)
                byte = 0
                bit_count = 0
        if bit_count > 0:
            data.append(byte << (8 - bit_count))
    return bytes(data)



def _uses_byte_aligned_format(width: int) -> bool:
    return width % 8 == 0



def _create_sbit_line_metrics(context: pixel_font_builder.FontBuilder) -> SbitLineMetrics:
    line_metrics = SbitLineMetrics()
    line_metrics.ascender = context.font_metric.horizontal_layout.ascent
    line_metrics.descender = context.font_metric.horizontal_layout.descent
    line_metrics.widthMax = max((glyph.width for glyph in context.glyphs), default=0)
    line_metrics.caretSlopeNumerator = 1
    line_metrics.caretSlopeDenominator = 0
    line_metrics.caretOffset = 0
    line_metrics.minOriginSB = min((glyph.horizontal_offset_x for glyph in context.glyphs), default=0)
    line_metrics.minAdvanceSB = min(
        (glyph.advance_width - glyph.horizontal_offset_x - glyph.width for glyph in context.glyphs),
        default=0,
    )
    line_metrics.maxBeforeBL = max(
        (glyph.height + glyph.horizontal_offset_y for glyph in context.glyphs),
        default=0,
    )
    line_metrics.minAfterBL = min((context.font_metric.horizontal_layout.descent for _ in context.glyphs), default=0)
    line_metrics.pad1 = 0
    line_metrics.pad2 = 0
    return line_metrics



def _create_bitmap_size_table(context: pixel_font_builder.FontBuilder) -> BitmapSizeTable:
    bitmap_size_table = BitmapSizeTable()
    line_metrics = _create_sbit_line_metrics(context)
    bitmap_size_table.hori = line_metrics
    bitmap_size_table.vert = line_metrics
    bitmap_size_table.colorRef = 0
    bitmap_size_table.ppemX = context.font_metric.font_size
    bitmap_size_table.ppemY = context.font_metric.font_size
    bitmap_size_table.bitDepth = 1
    bitmap_size_table.flags = 0x03 if context.opentype_config.has_vertical_metrics else 0x01
    return bitmap_size_table



def _create_small_metrics(glyph: Glyph) -> SmallGlyphMetrics:
    metrics = SmallGlyphMetrics()
    metrics.height = glyph.height
    metrics.width = glyph.width
    metrics.BearingX = glyph.horizontal_offset_x
    metrics.BearingY = glyph.height + glyph.horizontal_offset_y
    metrics.Advance = glyph.advance_width
    return metrics



def _create_big_metrics(glyph: Glyph) -> BigGlyphMetrics:
    metrics = BigGlyphMetrics()
    metrics.height = glyph.height
    metrics.width = glyph.width
    metrics.horiBearingX = glyph.horizontal_offset_x
    metrics.horiBearingY = glyph.height + glyph.horizontal_offset_y
    metrics.horiAdvance = glyph.advance_width
    metrics.vertBearingX = glyph.vertical_offset_x
    metrics.vertBearingY = glyph.width + glyph.vertical_offset_y
    metrics.vertAdvance = glyph.advance_height
    return metrics



def _big_metrics_signature(glyph: Glyph) -> tuple[int, ...]:
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



def _select_image_format(glyphs: list[Glyph], use_big_metrics: bool) -> int:
    byte_aligned = all(_uses_byte_aligned_format(glyph.width) for glyph in glyphs)
    if use_big_metrics:
        return 6 if byte_aligned else 7
    return 1 if byte_aligned else 2



def _big_metrics_header_size(image_format: int) -> int:
    if image_format in {6, 7}:
        return 8
    raise ValueError(f'unsupported big-metrics image format: {image_format}')



def _create_bitmap_glyph(glyph: Glyph, image_format: int) -> BitmapGlyphData:
    image_data = _pack_bitmap_rows(glyph.bitmap)
    if image_format == 6:
        bitmap_glyph = ebdt_bitmap_format_6(None, None)
        bitmap_glyph.metrics = _create_big_metrics(glyph)
    elif image_format == 7:
        bitmap_glyph = ebdt_bitmap_format_7(None, None)
        bitmap_glyph.metrics = _create_big_metrics(glyph)
    elif image_format == 1:
        bitmap_glyph = ebdt_bitmap_format_1(None, None)
        bitmap_glyph.metrics = _create_small_metrics(glyph)
    elif image_format == 2:
        bitmap_glyph = ebdt_bitmap_format_2(None, None)
        bitmap_glyph.metrics = _create_small_metrics(glyph)
    else:
        bitmap_glyph = ebdt_bitmap_format_5(None, None)
    bitmap_glyph.imageData = image_data
    return bitmap_glyph



def _build_group_signature(glyph: Glyph, use_big_metrics: bool) -> BitmapGroupSignature:
    image_data_size = len(_pack_bitmap_rows(glyph.bitmap))
    image_format = _select_image_format([glyph], use_big_metrics)
    if not use_big_metrics:
        return use_big_metrics, image_format, None, None
    return use_big_metrics, image_format, _big_metrics_signature(glyph), image_data_size



def _append_index_sub_table(strike: Strike, glyph_names: list[str], glyphs: list[Glyph], use_big_metrics: bool):
    image_format = _select_image_format(glyphs, use_big_metrics)
    if use_big_metrics:
        first_big_metrics_signature = _big_metrics_signature(glyphs[0])
        can_share_big_metrics = all(_big_metrics_signature(glyph) == first_big_metrics_signature for glyph in glyphs[1:])
        first_image_size = len(_pack_bitmap_rows(glyphs[0].bitmap))
        can_share_image_size = can_share_big_metrics and all(
            len(_pack_bitmap_rows(glyph.bitmap)) == first_image_size for glyph in glyphs[1:]
        )
        if can_share_image_size:
            index_sub_table = eblc_index_sub_table_5(None, None)
            index_sub_table.indexFormat = 5
            index_sub_table.imageFormat = 5
            index_sub_table.imageDataOffset = 0
            index_sub_table.names = glyph_names
            index_sub_table.metrics = _create_big_metrics(glyphs[0])
            index_sub_table.imageSize = first_image_size
        elif can_share_big_metrics and len(glyphs) > 1:
            index_sub_table = eblc_index_sub_table_2(None, None)
            index_sub_table.indexFormat = 2
            index_sub_table.imageFormat = image_format
            index_sub_table.imageDataOffset = 0
            index_sub_table.names = glyph_names
            index_sub_table.metrics = _create_big_metrics(glyphs[0])
            index_sub_table.imageSize = first_image_size + _big_metrics_header_size(image_format)
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



def create_bitmap_strikes(
        context: pixel_font_builder.FontBuilder,
        glyph_order: list[str],
        name_to_glyph: Mapping[str, Glyph],
) -> tuple[dict[str, BitmapGlyphData], Strike]:
    strike = Strike()
    strike.bitmapSizeTable = _create_bitmap_size_table(context)

    use_big_metrics = context.opentype_config.has_vertical_metrics
    strike_data: dict[str, BitmapGlyphData] = {}

    current_names: list[str] = []
    current_glyphs: list[Glyph] = []
    current_signature: BitmapGroupSignature | None = None
    subtable_image_formats: dict[str, int] = {}

    for glyph_name in glyph_order:
        glyph = name_to_glyph[glyph_name]
        signature = _build_group_signature(glyph, use_big_metrics)
        if current_signature is None or signature == current_signature:
            current_names.append(glyph_name)
            current_glyphs.append(glyph)
            current_signature = signature
        else:
            image_format = _append_index_sub_table(strike, current_names, current_glyphs, use_big_metrics)
            for name in current_names:
                subtable_image_formats[name] = image_format
            current_names = [glyph_name]
            current_glyphs = [glyph]
            current_signature = signature

    if current_names:
        image_format = _append_index_sub_table(strike, current_names, current_glyphs, use_big_metrics)
        for name in current_names:
            subtable_image_formats[name] = image_format

    for glyph_name in glyph_order:
        glyph = name_to_glyph[glyph_name]
        strike_data[glyph_name] = _create_bitmap_glyph(glyph, subtable_image_formats[glyph_name])

    return strike_data, strike



def create_ebdt_and_eblc(
        context: pixel_font_builder.FontBuilder,
        glyph_order: list[str],
        name_to_glyph: dict[str, pixel_font_builder.Glyph]
):
    from fontTools.ttLib import newTable
    from fontTools.ttLib.tables.E_B_D_T_ import table_E_B_D_T_
    from fontTools.ttLib.tables.E_B_L_C_ import table_E_B_L_C_

    table_ebdt = newTable('EBDT')
    table_ebdt.version = 2.0
    table_eblc = newTable('EBLC')
    table_eblc.version = 2.0

    strike_data, strike = create_bitmap_strikes(context, glyph_order, name_to_glyph)
    table_ebdt.strikeData = [strike_data]
    table_eblc.strikes = [strike]
    return table_ebdt, table_eblc



def create_bdat_and_bloc(
        context: pixel_font_builder.FontBuilder,
        glyph_order: list[str],
        name_to_glyph: dict[str, pixel_font_builder.Glyph]
) -> tuple[table__b_d_a_t, table__b_l_o_c]:
    table_bdat = table__b_d_a_t()
    table_bdat.version = 2.0
    table_bloc = table__b_l_o_c()
    table_bloc.version = 2.0

    strike_data, strike = create_bitmap_strikes(context, glyph_order, name_to_glyph)
    table_bdat.strikeData = [strike_data]
    table_bloc.strikes = [strike]
    return table_bdat, table_bloc
