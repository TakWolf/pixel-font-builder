from enum import StrEnum

from fontTools.fontBuilder import FontBuilder
from fontTools.misc import timeTools
from fontTools.ttLib import TTCollection

import pixel_font_builder
from pixel_font_builder.opentype.feature import build_kern_feature
from pixel_font_builder.opentype.name import create_name_strings
from pixel_font_builder.opentype.pen import OutlinesPen


class Flavor(StrEnum):
    WOFF = 'woff'
    WOFF2 = 'woff2'


def create_builder(
        context: 'pixel_font_builder.FontBuilder',
        is_ttf: bool,
        flavor: Flavor | None = None,
) -> FontBuilder:
    config = context.opentype_config
    font_metric = context.font_metric * config.px_to_units
    meta_info = context.meta_info
    character_mapping = context.character_mapping
    glyph_order, name_to_glyph = context.prepare_glyphs()
    kerning_pairs = context.kerning_pairs

    builder = FontBuilder(font_metric.font_size, isTTF=is_ttf, glyphDataFormat=config.glyph_data_format)

    if meta_info.created_time is not None:
        setattr(builder.font['head'], 'created', timeTools.timestampSinceEpoch(meta_info.created_time.timestamp()))
    if meta_info.modified_time is not None:
        setattr(builder.font['head'], 'modified', timeTools.timestampSinceEpoch(meta_info.modified_time.timestamp()))

    name_strings = create_name_strings(meta_info)
    builder.setupNameTable(name_strings)

    xtf_glyphs = {}
    horizontal_metrics = {}
    vertical_metrics = {}
    for glyph_name, glyph in name_to_glyph.items():
        advance_width = glyph.advance_width * config.px_to_units
        left_side_bearing = (glyph.calculate_bitmap_left_padding() + glyph.horizontal_origin_x) * config.px_to_units
        horizontal_metrics[glyph_name] = advance_width, left_side_bearing

        advance_height = glyph.advance_height * config.px_to_units
        top_side_bearing = (glyph.calculate_bitmap_top_padding() + glyph.vertical_origin_y) * config.px_to_units
        vertical_metrics[glyph_name] = advance_height, top_side_bearing

        pen = OutlinesPen(is_ttf, not is_ttf or config.glyph_data_format == 1, advance_width)
        config.outlines_painter.draw_outlines(glyph, pen, config.px_to_units)
        xtf_glyphs[glyph_name] = pen.to_glyph()
    builder.setupGlyphOrder(glyph_order)
    builder.setupGlyf(xtf_glyphs) if is_ttf else builder.setupCFF('', {}, xtf_glyphs, {})
    builder.setupCharacterMap(character_mapping)
    builder.setupHorizontalMetrics(horizontal_metrics)
    builder.setupVerticalMetrics(vertical_metrics)

    builder.setupHorizontalHeader(
        ascent=font_metric.horizontal_layout.ascent,
        descent=font_metric.horizontal_layout.descent,
        lineGap=font_metric.horizontal_layout.line_gap,
    )
    builder.setupVerticalHeader(
        ascent=font_metric.vertical_layout.ascent,
        descent=font_metric.vertical_layout.descent,
        lineGap=font_metric.vertical_layout.line_gap,
    )
    builder.setupOS2(
        sTypoAscender=font_metric.horizontal_layout.ascent,
        sTypoDescender=font_metric.horizontal_layout.descent,
        sTypoLineGap=font_metric.horizontal_layout.line_gap,
        usWinAscent=max(font_metric.horizontal_layout.ascent, 0),
        usWinDescent=max(-font_metric.horizontal_layout.descent, 0),
        sxHeight=font_metric.x_height,
        sCapHeight=font_metric.cap_height,
    )
    builder.setupPost()

    if len(kerning_pairs) > 0:
        builder.addOpenTypeFeatures(build_kern_feature(kerning_pairs, config.px_to_units))

    for feature_file in config.feature_files:
        builder.addOpenTypeFeatures(feature_file.text, feature_file.file_path)

    if flavor is not None:
        builder.font.flavor = flavor

    return builder


def create_collection_builder(
        contexts: 'pixel_font_builder.FontCollectionBuilder',
        is_ttf: bool,
) -> TTCollection:
    collection_builder = TTCollection()
    collection_builder.fonts.extend(create_builder(context, is_ttf).font for context in contexts)
    return collection_builder
