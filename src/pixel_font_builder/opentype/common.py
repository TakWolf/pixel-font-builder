from enum import StrEnum

from fontTools.fontBuilder import FontBuilder
from fontTools.misc import timeTools
from fontTools.misc.psCharStrings import T2CharString as OTFGlyph
from fontTools.pens.t2CharStringPen import T2CharStringPen as OTFGlyphPen
from fontTools.pens.ttGlyphPen import TTGlyphPen as TTFGlyphPen
from fontTools.ttLib import TTCollection
# noinspection PyProtectedMember
from fontTools.ttLib.tables._g_l_y_f import Glyph as TTFGlyph

import pixel_font_builder
from pixel_font_builder.glyph import Glyph
from pixel_font_builder.opentype.feature import build_kern_feature
from pixel_font_builder.opentype.name import create_name_strings


class Flavor(StrEnum):
    WOFF = 'woff'
    WOFF2 = 'woff2'


def _create_outlines(bitmap: list[list[int]]) -> list[list[tuple[int, int]]]:
    # 相邻像素分组
    point_group_list = []
    for y, bitmap_row in enumerate(bitmap):
        for x, color in enumerate(bitmap_row):
            if color != 0:
                new_point_group = {(x, y)}
                for i, point_group in enumerate(reversed(point_group_list)):
                    # 遍历方向为右下，因此只需检查左上
                    if (x - 1, y) in point_group or (x, y - 1) in point_group:
                        point_group_list.remove(point_group)
                        new_point_group = new_point_group.union(point_group)
                point_group_list.append(new_point_group)
    # 对每组生成轮廓
    outlines = []
    for point_group in point_group_list:
        # 按照像素拆分线段，注意绘制顺序
        pending_line_segments = []
        for (x, y) in point_group:
            point_outline = [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)]
            # 一个像素有左右上下四条边，如果该边没有相邻像素，则该边线段有效
            if x <= 0 or bitmap[y][x - 1] <= 0:  # 左
                pending_line_segments.append([point_outline[3], point_outline[0]])
            if x >= len(bitmap[y]) - 1 or bitmap[y][x + 1] <= 0:  # 右
                pending_line_segments.append([point_outline[1], point_outline[2]])
            if y <= 0 or bitmap[y - 1][x] <= 0:  # 上
                pending_line_segments.append([point_outline[0], point_outline[1]])
            if y >= len(bitmap) - 1 or bitmap[y + 1][x] <= 0:  # 下
                pending_line_segments.append([point_outline[2], point_outline[3]])
        # 连接所有的线段，注意绘制顺序
        solved_line_segments = []
        while len(pending_line_segments) > 0:
            pending_line_segment = pending_line_segments.pop()
            for i, solved_line_segment in enumerate(reversed(solved_line_segments)):
                left_line_segment = None
                right_line_segment = None
                # 一共4种连接情况
                if pending_line_segment[-1] == solved_line_segment[0]:
                    left_line_segment = pending_line_segment
                    right_line_segment = solved_line_segment
                elif pending_line_segment[-1] == solved_line_segment[-1]:
                    solved_line_segment.reverse()
                    left_line_segment = pending_line_segment
                    right_line_segment = solved_line_segment
                elif solved_line_segment[-1] == pending_line_segment[0]:
                    left_line_segment = solved_line_segment
                    right_line_segment = pending_line_segment
                elif solved_line_segment[-1] == pending_line_segment[-1]:
                    pending_line_segment.reverse()
                    left_line_segment = solved_line_segment
                    right_line_segment = pending_line_segment
                # 需要连接的情况
                if left_line_segment is not None and right_line_segment is not None:
                    solved_line_segments.remove(solved_line_segment)
                    # 连接的两个点是重复的
                    right_line_segment.pop(0)
                    # 判断连接的点是不是可省略
                    x, y = left_line_segment[-1]
                    xl, yl = left_line_segment[-2]
                    xr, yr = right_line_segment[0]
                    if (x == xl and x == xr) or (y == yl and y == yr):
                        left_line_segment.pop()
                    # 连接线段
                    pending_line_segment = left_line_segment + right_line_segment
            solved_line_segments.append(pending_line_segment)
        # 将连接好的线段添加到轮廓数组中，有多条线段的情况，是中间有镂空（绘制顺序与外边框相反）
        for solved_line_segment in solved_line_segments:
            # 首尾的两个点是重复的
            solved_line_segment.pop(0)
            # 判断尾点是不是可省略
            x, y = solved_line_segment[-1]
            xl, yl = solved_line_segment[-2]
            xr, yr = solved_line_segment[0]
            if (x == xl and x == xr) or (y == yl and y == yr):
                solved_line_segment.pop()
            # 添加到轮廓
            outlines.append(solved_line_segment)
    return outlines


def _create_glyph(glyph: Glyph, px_to_units: int, is_ttf: bool) -> OTFGlyph | TTFGlyph:
    pen = TTFGlyphPen() if is_ttf else OTFGlyphPen(glyph.advance_width * px_to_units, None)
    outlines = _create_outlines(glyph.bitmap)
    for outline in outlines:
        for index, (x, y) in enumerate(outline):
            x = (x + glyph.horizontal_origin_x) * px_to_units
            y = (glyph.height + glyph.horizontal_origin_y - y) * px_to_units

            if index == 0:
                pen.moveTo((x, y))
            else:
                pen.lineTo((x, y))
        pen.closePath()
    return pen.glyph() if is_ttf else pen.getCharString()


def create_builder(context: 'pixel_font_builder.FontBuilder', is_ttf: bool, flavor: Flavor | None = None) -> FontBuilder:
    config = context.opentype_config
    font_metric = context.font_metric * config.px_to_units
    meta_info = context.meta_info
    character_mapping = context.character_mapping
    glyph_order, name_to_glyph = context.prepare_glyphs()
    kerning_pairs = context.kerning_pairs

    builder = FontBuilder(font_metric.font_size, isTTF=is_ttf)

    if meta_info.created_time is not None:
        setattr(builder.font['head'], 'created', timeTools.timestampSinceEpoch(meta_info.created_time.timestamp()))
    if meta_info.modified_time is not None:
        setattr(builder.font['head'], 'modified', timeTools.timestampSinceEpoch(meta_info.modified_time.timestamp()))

    name_strings = create_name_strings(meta_info)
    builder.setupNameTable(name_strings)

    builder.setupGlyphOrder(glyph_order)
    xtf_glyphs = {}
    for glyph_name, glyph in name_to_glyph.items():
        xtf_glyphs[glyph_name] = _create_glyph(glyph, config.px_to_units, is_ttf)
    if is_ttf:
        builder.setupGlyf(xtf_glyphs)
    else:
        builder.setupCFF('', {}, xtf_glyphs, {})

    builder.setupCharacterMap(character_mapping)

    horizontal_metrics = {}
    vertical_metrics = {}
    for glyph_name in glyph_order:
        glyph = name_to_glyph[glyph_name]

        advance_width = glyph.advance_width * config.px_to_units
        left_side_bearing = (glyph.calculate_bitmap_left_padding() + glyph.horizontal_origin_x) * config.px_to_units
        horizontal_metrics[glyph_name] = advance_width, left_side_bearing

        advance_height = glyph.advance_height * config.px_to_units
        top_side_bearing = (glyph.calculate_bitmap_top_padding() + glyph.vertical_origin_y) * config.px_to_units
        vertical_metrics[glyph_name] = advance_height, top_side_bearing
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
        usWinAscent=font_metric.horizontal_layout.ascent,
        usWinDescent=-font_metric.horizontal_layout.descent,
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


def create_collection_builder(contexts: 'pixel_font_builder.FontCollectionBuilder', is_ttf: bool) -> TTCollection:
    collection_builder = TTCollection()
    for context in contexts:
        builder = create_builder(context, is_ttf)
        collection_builder.fonts.append(builder.font)
    return collection_builder
