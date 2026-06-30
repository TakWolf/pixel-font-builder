from __future__ import annotations

from enum import StrEnum, unique

from fontTools.fontBuilder import FontBuilder
from fontTools.misc import timeTools
from fontTools.misc.arrayTools import intRect
from fontTools.ttLib import TTCollection
from fontTools.ttLib.tables.E_B_D_T_ import table_E_B_D_T_
from fontTools.ttLib.tables.E_B_L_C_ import table_E_B_L_C_

import pixel_font_builder
from pixel_font_builder.opentype.bitmap import create_bitmap_strike_data
from pixel_font_builder.opentype.feature import build_kern_feature
from pixel_font_builder.opentype.name import create_name_strings
from pixel_font_builder.opentype.outline import create_normal_xtf_glyphs, create_blank_xtf_glyphs
from pixel_font_builder.opentype.patch.O_S_2f_2 import table_O_S_2f_2_apple
from pixel_font_builder.opentype.patch._b_d_a_t import table__b_d_a_t
from pixel_font_builder.opentype.patch._b_h_e_d import table__b_h_e_d
from pixel_font_builder.opentype.patch._b_l_o_c import table__b_l_o_c
from pixel_font_builder.opentype.patch._g_l_y_f import table__g_l_y_f_zero_length


@unique
class OutlineTableMode(StrEnum):
    # Generate standard outline data.
    # - TTF: write glyf/loca tables with full glyph outlines.
    # - OTF: write normal CFF table data.
    NORMAL = 'Normal'

    # Do not generate outline tables.
    OMIT = 'Omit'

    # Generate an outline table shell with zero-length table data.
    ZERO_LENGTH = 'Zero Length'

    # Generate outline tables for the full glyph order, but make glyph outlines empty.
    # Intended for fake scalable bitmap fonts where layout metrics still come from sfnt metrics tables.
    BLANK_GLYPHS = 'Blank Glyphs'


@unique
class BitmapTableMode(StrEnum):
    # Do not generate embedded bitmap tables.
    NONE = 'None'

    # Generate standard OpenType embedded bitmap tables.
    # Typically, EBLC + EBDT.
    STANDARD = 'Standard'

    # Generate Apple-style embedded bitmap tables.
    # Uses the same binary structure as EBLC/EBDT, but writes bloc/bdat tags instead.
    # Also generates a bhed table copied from head.
    APPLE = 'Apple'


@unique
class Flavor(StrEnum):
    WOFF = 'woff'
    WOFF2 = 'woff2'


def create_font_builder(
        context: pixel_font_builder.FontBuilder,
        is_ttf: bool,
        outline_table_mode: OutlineTableMode = OutlineTableMode.NORMAL,
        bitmap_table_mode: BitmapTableMode = BitmapTableMode.NONE,
        flavor: Flavor | None = None,
) -> FontBuilder:
    config = context.opentype_config
    font_metric = context.font_metric * config.px_to_units
    meta_info = context.meta_info
    glyph_order, name_to_glyph = context.prepare_glyphs()
    character_mapping = context.character_mapping
    kerning_values = context.kerning_values

    builder = FontBuilder(font_metric.font_size, isTTF=is_ttf)

    name_strings = create_name_strings(meta_info)
    builder.setupNameTable(name_strings)

    if outline_table_mode == OutlineTableMode.NORMAL:
        xtf_glyphs, horizontal_metrics, vertical_metrics = create_normal_xtf_glyphs(is_ttf, config.outlines_painter, name_to_glyph, config.px_to_units)
    else:
        xtf_glyphs, horizontal_metrics, vertical_metrics = create_blank_xtf_glyphs(is_ttf, name_to_glyph, config.px_to_units)
    builder.setupGlyphOrder(glyph_order)
    if is_ttf:
        builder.setupGlyf(xtf_glyphs)
    else:
        builder.setupCFF('', {}, xtf_glyphs, {})
    builder.setupHorizontalMetrics(horizontal_metrics)
    if config.has_vertical_metrics:
        builder.setupVerticalMetrics(vertical_metrics)

    if bitmap_table_mode in (BitmapTableMode.STANDARD, BitmapTableMode.APPLE):
        strike, strike_data = create_bitmap_strike_data(context.font_metric, config.has_vertical_metrics, glyph_order, name_to_glyph)

        if bitmap_table_mode == BitmapTableMode.STANDARD:
            tb_eblc = table_E_B_L_C_()
            tb_ebdt = table_E_B_D_T_()
        else:
            tb_eblc = table__b_l_o_c()
            tb_ebdt = table__b_d_a_t()

        tb_eblc.version = 2.0
        tb_eblc.strikes = [strike]
        builder.font[tb_eblc.tableTag] = tb_eblc

        tb_ebdt.version = 2.0
        tb_ebdt.strikeData = [strike_data]
        builder.font[tb_ebdt.tableTag] = tb_ebdt

    builder.setupCharacterMap(character_mapping)

    builder.setupHorizontalHeader(
        ascent=font_metric.horizontal_layout.ascent,
        descent=font_metric.horizontal_layout.descent,
        lineGap=font_metric.horizontal_layout.line_gap,
    )
    if config.has_vertical_metrics:
        builder.setupVerticalHeader(
            ascent=font_metric.vertical_layout.ascent,
            descent=font_metric.vertical_layout.descent,
            lineGap=font_metric.vertical_layout.line_gap,
        )
    builder.setupOS2(
        xAvgCharWidth=0,
        usWeightClass=meta_info.weight_name.number if meta_info.weight_name is not None else 400,
        sTypoAscender=font_metric.horizontal_layout.ascent,
        sTypoDescender=font_metric.horizontal_layout.descent,
        sTypoLineGap=font_metric.horizontal_layout.line_gap,
        usWinAscent=max(font_metric.horizontal_layout.ascent, 0),
        usWinDescent=max(-font_metric.horizontal_layout.descent, 0),
        sxHeight=font_metric.x_height,
        sCapHeight=font_metric.cap_height,
        yStrikeoutPosition=font_metric.strikeout_position,
        yStrikeoutSize=font_metric.strikeout_thickness,
        ulCodePageRange1=0b_11100000_00111111_00000001_11111111,
        ulCodePageRange2=0b_11111111_11111111_00000000_00000000,
    )
    builder.setupPost(
        underlinePosition=font_metric.underline_position,
        underlineThickness=font_metric.underline_thickness,
    )

    tb_head = builder.font['head']
    tb_os2 = builder.font['OS/2']

    if meta_info.created_time is not None:
        tb_head.created = timeTools.timestampSinceEpoch(meta_info.created_time.timestamp())
    if meta_info.modified_time is not None:
        tb_head.modified = timeTools.timestampSinceEpoch(meta_info.modified_time.timestamp())

    builder.font.recalcBBoxes = False
    if is_ttf:
        tb_maxp = builder.font['maxp']
        tb_maxp.recalc(builder.font)
        tb_maxp.numGlyphs = len(glyph_order)
    else:
        cff = builder.font["CFF "].cff
        for top_dict in cff.topDictIndex:
            top_dict.recalcFontBBox()
        tb_head.xMin, tb_head.yMin, tb_head.xMax, tb_head.yMax = intRect(cff.topDictIndex[0].FontBBox)
    builder.font['hhea'].recalc(builder.font)
    if config.has_vertical_metrics:
        builder.font['vhea'].recalc(builder.font)

    if config.is_monospaced:
        if is_ttf:
            tb_os2.panose.bProportion = 9
        builder.font['post'].isFixedPitch = 1

    if config.fields_override.head_x_min is not None:
        tb_head.xMin = config.fields_override.head_x_min * config.px_to_units
    if config.fields_override.head_y_min is not None:
        tb_head.yMin = config.fields_override.head_y_min * config.px_to_units
    if config.fields_override.head_x_max is not None:
        tb_head.xMax = config.fields_override.head_x_max * config.px_to_units
    if config.fields_override.head_y_max is not None:
        tb_head.yMax = config.fields_override.head_y_max * config.px_to_units

    if config.fields_override.os2_x_avg_char_width is None:
        tb_os2.recalcAvgCharWidth(builder.font)
    else:
        tb_os2.xAvgCharWidth = config.fields_override.os2_x_avg_char_width * config.px_to_units

    match outline_table_mode:
        case OutlineTableMode.OMIT:
            if is_ttf:
                del builder.font['glyf']
                del builder.font['loca']
            else:
                del builder.font['CFF ']
        case OutlineTableMode.ZERO_LENGTH:
            if is_ttf:
                builder.font['glyf'] = table__g_l_y_f_zero_length()
            else:
                glyph_order_backup = builder.font.glyphOrder.copy()
                builder.font.glyphOrder.clear()
                builder.setupCFF('', {}, {}, {})
                builder.font.glyphOrder = glyph_order_backup

    if outline_table_mode in (OutlineTableMode.OMIT, OutlineTableMode.ZERO_LENGTH):
        del builder.font['hmtx']
        del builder.font['hhea']
        if config.has_vertical_metrics:
            del builder.font['vmtx']
            del builder.font['vhea']

    if bitmap_table_mode == BitmapTableMode.APPLE:
        tb_bhed = table__b_h_e_d.replace(tb_head)
        builder.font[tb_bhed.tableTag] = tb_bhed

        if outline_table_mode == OutlineTableMode.OMIT:
            tb_os2 = table_O_S_2f_2_apple.replace(tb_os2)
            builder.font[tb_os2.tableTag] = tb_os2

            del builder.font[tb_head.tableTag]

    if outline_table_mode == OutlineTableMode.NORMAL and len(kerning_values) > 0:
        builder.addOpenTypeFeatures(build_kern_feature(glyph_order, kerning_values, config.px_to_units))

    for feature_file in config.feature_files:
        builder.addOpenTypeFeatures(feature_file.text, feature_file.file_path)

    if flavor is not None:
        builder.font.flavor = flavor.value

    return builder


def create_font_collection_builder(
        contexts: pixel_font_builder.FontCollectionBuilder,
        is_ttf: bool,
        outline_table_mode: OutlineTableMode = OutlineTableMode.NORMAL,
        bitmap_table_mode: BitmapTableMode = BitmapTableMode.NONE,
) -> TTCollection:
    collection_builder = TTCollection()
    collection_builder.fonts.extend(
        create_font_builder(context, is_ttf, outline_table_mode, bitmap_table_mode).font
        for context in contexts
    )
    return collection_builder
