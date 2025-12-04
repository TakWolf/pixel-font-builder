from __future__ import annotations

from enum import StrEnum

from fontTools.fontBuilder import FontBuilder
from fontTools.misc import timeTools
from fontTools.ttLib import TTCollection

import pixel_font_builder
from pixel_font_builder.opentype.feature import build_kern_feature
from pixel_font_builder.opentype.metric import BoundingBox
from pixel_font_builder.opentype.name import create_name_strings
from pixel_font_builder.opentype.outline import create_xtf_glyphs


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
    builder.font.recalcBBoxes = False
    tb_head = builder.font['head']

    if meta_info.created_time is not None:
        setattr(tb_head, 'created', timeTools.timestampSinceEpoch(meta_info.created_time.timestamp()))

    if meta_info.modified_time is not None:
        setattr(tb_head, 'modified', timeTools.timestampSinceEpoch(meta_info.modified_time.timestamp()))

    name_strings = create_name_strings(meta_info)
    builder.setupNameTable(name_strings)

    xtf_glyphs, bounding_boxes, horizontal_metrics, vertical_metrics = create_xtf_glyphs(is_ttf, config.outlines_painter, name_to_glyph, config.px_to_units)

    builder.setupGlyphOrder(glyph_order)
    builder.setupGlyf(xtf_glyphs) if is_ttf else builder.setupCFF('', {}, xtf_glyphs, {})
    builder.setupHorizontalMetrics({glyph_name: (horizontal_metric.advance_width, horizontal_metric.left_side_bearing) for glyph_name, horizontal_metric in horizontal_metrics.items()})
    if config.has_vertical_metrics:
        builder.setupVerticalMetrics({glyph_name: (vertical_metric.advance_height, vertical_metric.top_side_bearing) for glyph_name, vertical_metric in vertical_metrics.items()})

    builder.setupCharacterMap(character_mapping)

    builder.setupHorizontalHeader(
        ascent=font_metric.horizontal_layout.ascent,
        descent=font_metric.horizontal_layout.descent,
        lineGap=font_metric.horizontal_layout.line_gap,
        advanceWidthMax=max((horizontal_metric.advance_width for horizontal_metric in horizontal_metrics.values()), default=0),
        minLeftSideBearing=min((horizontal_metric.left_side_bearing for horizontal_metric in horizontal_metrics.values()), default=0),
        minRightSideBearing=min((horizontal_metric.right_side_bearing for horizontal_metric in horizontal_metrics.values()), default=0),
        xMaxExtent=max((horizontal_metric.x_extent for horizontal_metric in horizontal_metrics.values()), default=0),
    )
    if config.has_vertical_metrics:
        builder.setupVerticalHeader(
            ascent=font_metric.vertical_layout.ascent,
            descent=font_metric.vertical_layout.descent,
            lineGap=font_metric.vertical_layout.line_gap,
            advanceHeightMax=max((vertical_metric.advance_height for vertical_metric in vertical_metrics.values()), default=0),
            minTopSideBearing=min((vertical_metric.top_side_bearing for vertical_metric in vertical_metrics.values()), default=0),
            minBottomSideBearing=min((vertical_metric.bottom_side_bearing for vertical_metric in vertical_metrics.values()), default=0),
            yMaxExtent=max((vertical_metric.y_extent for vertical_metric in vertical_metrics.values()), default=0),
        )
    builder.setupOS2(
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

    if config.head_bounding_box_override is None:
        head_bounding_box = BoundingBox(
            x_min=min((bounding_box.x_min for bounding_box in bounding_boxes.values()), default=0),
            y_min=min((bounding_box.y_min for bounding_box in bounding_boxes.values()), default=0),
            x_max=max((bounding_box.x_max for bounding_box in bounding_boxes.values()), default=0),
            y_max=max((bounding_box.y_max for bounding_box in bounding_boxes.values()), default=0),
        )
    else:
        head_bounding_box = config.head_bounding_box_override * config.px_to_units
    setattr(tb_head, 'xMin', head_bounding_box.x_min)
    setattr(tb_head, 'yMin', head_bounding_box.y_min)
    setattr(tb_head, 'xMax', head_bounding_box.x_max)
    setattr(tb_head, 'yMax', head_bounding_box.y_max)

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
