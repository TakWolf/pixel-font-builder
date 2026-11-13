from __future__ import annotations

from fontTools.feaLib import ast
from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.fontBuilder import FontBuilder
from fontTools.misc import timeTools
from fontTools.misc.arrayTools import intRect
from fontTools.misc.roundTools import otRound
from fontTools.ttLib import TTCollection
from fontTools.ttLib.tables import DefaultTable
from fontTools.ttLib.tables.E_B_D_T_ import table_E_B_D_T_
from fontTools.ttLib.tables.E_B_L_C_ import table_E_B_L_C_
from fontTools.ttLib.tables._b_d_a_t import table__b_d_a_t
from fontTools.ttLib.tables._b_h_e_d import table__b_h_e_d
from fontTools.ttLib.tables._b_l_o_c import table__b_l_o_c

import pixel_font_builder
from pixel_font_builder.opentype.bitmap.ebdt import create_bitmap_strike_data
from pixel_font_builder.opentype.enum import OutlineTableMode, BitmapTableMode, Flavor
from pixel_font_builder.opentype.feature.kerning import add_generated_kern_feature
from pixel_font_builder.opentype.feature.source.parser import parse_feature_inputs
from pixel_font_builder.opentype.name import create_name_strings
from pixel_font_builder.opentype.outline.pen.otf import OtfOutlinePen
from pixel_font_builder.opentype.outline.pen.ttf import TtfOutlinePen


def create_font_builder(
        context: pixel_font_builder.FontBuilder,
        is_ttf: bool,
        outline_table_mode: OutlineTableMode = OutlineTableMode.NORMAL,
        bitmap_table_mode: BitmapTableMode = BitmapTableMode.NONE,
        flavor: Flavor | None = None,
) -> FontBuilder:
    emit_outlines = outline_table_mode in (OutlineTableMode.NORMAL, OutlineTableMode.BLANK_GLYPHS)
    emit_bitmaps = bitmap_table_mode != BitmapTableMode.NONE

    if not emit_outlines and not emit_bitmaps:
        raise RuntimeError("at least one of outlines or bitmaps must be emitted")

    config = context.opentype_config
    font_metric = context.font_metric * config.px_to_units
    meta_info = context.meta_info
    glyph_order, name_to_glyph = context.prepare_glyphs()
    character_mapping = context.character_mapping
    kerning_values = context.kerning_values

    if config.has_vertical_metrics:
        vertical_origins = {}
        for glyph_name, glyph in name_to_glyph.items():
            vertical_origin = (glyph.height + glyph.horizontal_offset_y + glyph.vertical_offset_y) * config.px_to_units
            vertical_origins[glyph_name] = vertical_origin
    else:
        vertical_origins = None

    builder = FontBuilder(font_metric.font_size, isTTF=is_ttf)

    name_strings = create_name_strings(meta_info)
    builder.setupNameTable(name_strings)

    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(character_mapping)

    if is_ttf:
        ttf_glyphs = {}
        for glyph_name, glyph in name_to_glyph.items():
            pen = TtfOutlinePen()
            if outline_table_mode == OutlineTableMode.NORMAL:
                config.outline_painter.draw_outlines(glyph, pen, config.px_to_units)
            ttf_glyphs[glyph_name] = pen.to_glyph()
        builder.setupGlyf(ttf_glyphs)

        horizontal_metrics = {}
        for glyph_name, glyph in name_to_glyph.items():
            ttf_glyph = ttf_glyphs[glyph_name]
            advance_width = glyph.advance_width * config.px_to_units
            left_side_bearing = ttf_glyph.xMin if ttf_glyph.numberOfContours > 0 else 0
            horizontal_metrics[glyph_name] = advance_width, left_side_bearing
        builder.setupHorizontalMetrics(horizontal_metrics)

        if config.has_vertical_metrics:
            vertical_metrics = {}
            for glyph_name, glyph in name_to_glyph.items():
                ttf_glyph = ttf_glyphs[glyph_name]
                advance_height = glyph.advance_height * config.px_to_units
                vertical_origin = vertical_origins[glyph_name]
                top_side_bearing = vertical_origin - ttf_glyph.yMax if ttf_glyph.numberOfContours > 0 else vertical_origin
                vertical_metrics[glyph_name] = advance_height, top_side_bearing
            builder.setupVerticalMetrics(vertical_metrics)
    else:
        otf_glyphs = {}
        for glyph_name, glyph in name_to_glyph.items():
            pen = OtfOutlinePen(glyph.advance_width * config.px_to_units)
            if outline_table_mode == OutlineTableMode.NORMAL:
                config.outline_painter.draw_outlines(glyph, pen, config.px_to_units)
            otf_glyphs[glyph_name] = pen.to_glyph()
        builder.setupCFF('', {
            'isFixedPitch': config.is_fixed_pitch,
        }, otf_glyphs, {})

        name_to_otf_bounds = {glyph_name: otf_glyph.calcBounds(None) for glyph_name, otf_glyph in otf_glyphs.items()}

        horizontal_metrics = {}
        for glyph_name, glyph in name_to_glyph.items():
            otf_bounds = name_to_otf_bounds[glyph_name]
            advance_width = glyph.advance_width * config.px_to_units
            left_side_bearing = otRound(otf_bounds[0]) if otf_bounds is not None else 0
            horizontal_metrics[glyph_name] = advance_width, left_side_bearing
        builder.setupHorizontalMetrics(horizontal_metrics)

        if config.has_vertical_metrics:
            vertical_metrics = {}
            for glyph_name, glyph in name_to_glyph.items():
                otf_bounds = name_to_otf_bounds[glyph_name]
                advance_height = glyph.advance_height * config.px_to_units
                vertical_origin = vertical_origins[glyph_name]
                top_side_bearing = otRound(vertical_origin - otf_bounds[3]) if otf_bounds is not None else vertical_origin
                vertical_metrics[glyph_name] = advance_height, top_side_bearing
            builder.setupVerticalMetrics(vertical_metrics)

            if emit_outlines:
                builder.setupVerticalOrigins(vertical_origins)

    if emit_bitmaps:
        strike, strike_data = create_bitmap_strike_data(context.font_metric, config.has_vertical_metrics, glyph_order, name_to_glyph)

        if bitmap_table_mode == BitmapTableMode.APPLE:
            tb_eblc = table__b_l_o_c()
            tb_ebdt = table__b_d_a_t()
        else:
            tb_eblc = table_E_B_L_C_()
            tb_ebdt = table_E_B_D_T_()

        tb_eblc.version = 2.0
        tb_eblc.strikes = [strike]
        builder.font[tb_eblc.tableTag] = tb_eblc

        tb_ebdt.version = 2.0
        tb_ebdt.strikeData = [strike_data]
        builder.font[tb_ebdt.tableTag] = tb_ebdt

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
        isFixedPitch=int(config.is_fixed_pitch),
    )

    tb_head = builder.font['head']
    tb_os2 = builder.font['OS/2']

    if meta_info.created_time is not None:
        tb_head.created = timeTools.timestampSinceEpoch(meta_info.created_time.timestamp())
    if meta_info.modified_time is not None:
        tb_head.modified = timeTools.timestampSinceEpoch(meta_info.modified_time.timestamp())

    builder.font.recalcBBoxes = False
    if is_ttf:
        builder.font['maxp'].recalc(builder.font)
    else:
        cff = builder.font["CFF "].cff
        for top_dict in cff.topDictIndex:
            top_dict.recalcFontBBox()
        tb_head.xMin, tb_head.yMin, tb_head.xMax, tb_head.yMax = intRect(cff.topDictIndex[0].FontBBox)
    builder.font['hhea'].recalc(builder.font)
    if config.has_vertical_metrics:
        builder.font['vhea'].recalc(builder.font)

    if config.field_overrides.head_x_min is not None:
        tb_head.xMin = config.field_overrides.head_x_min * config.px_to_units
    if config.field_overrides.head_y_min is not None:
        tb_head.yMin = config.field_overrides.head_y_min * config.px_to_units
    if config.field_overrides.head_x_max is not None:
        tb_head.xMax = config.field_overrides.head_x_max * config.px_to_units
    if config.field_overrides.head_y_max is not None:
        tb_head.yMax = config.field_overrides.head_y_max * config.px_to_units

    if config.field_overrides.os2_x_avg_char_width is None:
        tb_os2.recalcAvgCharWidth(builder.font)
    else:
        tb_os2.xAvgCharWidth = config.field_overrides.os2_x_avg_char_width * config.px_to_units

    match outline_table_mode:
        case OutlineTableMode.OMIT:
            if is_ttf:
                del builder.font['glyf']
                del builder.font['loca']
            else:
                del builder.font['CFF ']
        case OutlineTableMode.ZERO_LENGTH:
            if is_ttf:
                tb_glyf = DefaultTable.DefaultTable('glyf')
                tb_glyf.data = b''
                builder.font[tb_glyf.tableTag] = tb_glyf
                builder.font['loca'].set([0])
            else:
                glyph_order_backup = builder.font.glyphOrder.copy()
                builder.font.glyphOrder.clear()
                builder.setupCFF('', {}, {}, {})
                builder.font.glyphOrder = glyph_order_backup

    if not emit_outlines:
        del builder.font['hmtx']
        del builder.font['hhea']
        if config.has_vertical_metrics:
            del builder.font['vmtx']
            del builder.font['vhea']

    if bitmap_table_mode == BitmapTableMode.APPLE:
        tb_bhed = table__b_h_e_d()
        tb_bhed_props = tb_head.__dict__.copy()
        tb_bhed_props.pop('tableTag')
        tb_bhed.__dict__.update(tb_bhed_props)
        builder.font[tb_bhed.tableTag] = tb_bhed

        if outline_table_mode == OutlineTableMode.OMIT:
            del builder.font[tb_head.tableTag]

    feature_ast = parse_feature_inputs(config.features.create_inputs(), glyph_order) if config.features is not None else ast.FeatureFile()

    if outline_table_mode == OutlineTableMode.NORMAL and kerning_values:
        add_generated_kern_feature(feature_ast, kerning_values, config.px_to_units, config.user_kerning_mode)

    if feature_ast.statements:
        addOpenTypeFeatures(builder.font, feature_ast)

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
