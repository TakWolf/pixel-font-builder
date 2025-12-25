from __future__ import annotations

from enum import StrEnum, unique

from fontTools.fontBuilder import FontBuilder
from fontTools.misc import timeTools
from fontTools.misc.arrayTools import intRect
from fontTools.ttLib import TTCollection
from fontTools.ttLib.tables.O_S_2f_2 import Panose

import pixel_font_builder
from pixel_font_builder.meta import WeightName
from pixel_font_builder.opentype.feature import build_kern_feature
from pixel_font_builder.opentype.name import create_name_strings
from pixel_font_builder.opentype.outline import create_xtf_glyphs

_OS2_US_WEIGHT_CLASS_VALUES = {
    WeightName.THIN: 100,
    WeightName.EXTRA_LIGHT: 200,
    WeightName.LIGHT: 300,
    WeightName.NORMAL: 400,
    WeightName.REGULAR: 400,
    WeightName.MEDIUM: 500,
    WeightName.SEMI_BOLD: 600,
    WeightName.BOLD: 700,
    WeightName.EXTRA_BOLD: 800,
    WeightName.BLACK: 900,
    WeightName.HEAVY: 900,
}


@unique
class Flavor(StrEnum):
    WOFF = 'woff'
    WOFF2 = 'woff2'


def create_font_builder(
        context: pixel_font_builder.FontBuilder,
        is_ttf: bool,
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

    xtf_glyphs, horizontal_metrics, vertical_metrics = create_xtf_glyphs(is_ttf, config.outlines_painter, name_to_glyph, config.px_to_units)
    builder.setupGlyphOrder(glyph_order)
    if is_ttf:
        builder.setupGlyf(xtf_glyphs)
    else:
        builder.setupCFF('', {}, xtf_glyphs, {})
    builder.setupHorizontalMetrics(horizontal_metrics)
    if config.has_vertical_metrics:
        builder.setupVerticalMetrics(vertical_metrics)

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
        usWeightClass=_OS2_US_WEIGHT_CLASS_VALUES.get(meta_info.weight_name, 400),
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
    tb_post = builder.font['post']

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

    if config.is_monospaced:
        if is_ttf:
            tb_os2.panose.bProportion = 9
        tb_post.isFixedPitch = 1

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

    if len(kerning_values) > 0:
        builder.addOpenTypeFeatures(build_kern_feature(glyph_order, kerning_values, config.px_to_units))

    for feature_file in config.feature_files:
        builder.addOpenTypeFeatures(feature_file.text, feature_file.file_path)

    if flavor is not None:
        builder.font.flavor = flavor

    return builder


def create_font_collection_builder(
        contexts: pixel_font_builder.FontCollectionBuilder,
        is_ttf: bool,
) -> TTCollection:
    collection_builder = TTCollection()
    collection_builder.fonts.extend(create_font_builder(context, is_ttf).font for context in contexts)
    return collection_builder
