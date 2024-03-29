import logging
from enum import StrEnum

from fontTools.fontBuilder import FontBuilder
from fontTools.misc import timeTools
from fontTools.misc.psCharStrings import T2CharString as OTFGlyph
from fontTools.pens.t2CharStringPen import T2CharStringPen as OTFGlyphPen
from fontTools.pens.ttGlyphPen import TTGlyphPen as TTFGlyphPen
from fontTools.ttLib import TTCollection
from fontTools.ttLib.tables._g_l_y_f import Glyph as TTFGlyph

import pixel_font_builder
from pixel_font_builder.glyph import Glyph
from pixel_font_builder.info import MetaInfo

logger = logging.getLogger('pixel_font_builder.opentype')

_CACHE_NAME_TAG = '_opentype_cache_tag'
_CACHE_NAME_OUTLINES = '_opentype_cache_outlines'
_CACHE_NAME_OTF_GLYPH = '_opentype_cache_otf_glyph'
_CACHE_NAME_TTF_GLYPH = '_opentype_cache_ttf_glyph'


class Config:
    def __init__(
            self,
            px_to_units: int = 100,
            cff_family_name: str = None,
    ):
        self.px_to_units = px_to_units
        self.cff_family_name = cff_family_name


class Flavor(StrEnum):
    WOFF = 'woff'
    WOFF2 = 'woff2'


def _create_name_strings(meta_info: MetaInfo) -> dict[str, str]:
    """
    https://learn.microsoft.com/en-us/typography/opentype/spec/name#name-ids
    copyright (nameID 0)
    familyName (nameID 1)
    styleName (nameID 2)
    uniqueFontIdentifier (nameID 3)
    fullName (nameID 4)
    version (nameID 5)
    psName (nameID 6)
    trademark (nameID 7)
    manufacturer (nameID 8)
    designer (nameID 9)
    description (nameID 10)
    vendorURL (nameID 11)
    designerURL (nameID 12)
    licenseDescription (nameID 13)
    licenseInfoURL (nameID 14)
    typographicFamily (nameID 16)
    typographicSubfamily (nameID 17)
    compatibleFullName (nameID 18)
    sampleText (nameID 19)
    postScriptCIDFindfontName (nameID 20)
    wwsFamilyName (nameID 21)
    wwsSubfamilyName (nameID 22)
    lightBackgroundPalette (nameID 23)
    darkBackgroundPalette (nameID 24)
    variationsPostScriptNamePrefix (nameID 25)
    """
    unique_name = meta_info.family_name.replace(' ', '-')
    name_strings = {
        'familyName': meta_info.family_name,
        'styleName': meta_info.style_name,
        'uniqueFontIdentifier': f'{unique_name}-{meta_info.style_name};{meta_info.version}',
        'fullName': f'{meta_info.family_name} {meta_info.style_name}',
        'version': meta_info.version,
        'psName': f'{unique_name}-{meta_info.style_name}',
    }
    if meta_info.copyright_info is not None:
        name_strings['copyright'] = meta_info.copyright_info
    if meta_info.manufacturer is not None:
        name_strings['manufacturer'] = meta_info.manufacturer
    if meta_info.designer is not None:
        name_strings['designer'] = meta_info.designer
    if meta_info.description is not None:
        name_strings['description'] = meta_info.description
    if meta_info.vendor_url is not None:
        name_strings['vendorURL'] = meta_info.vendor_url
    if meta_info.designer_url is not None:
        name_strings['designerURL'] = meta_info.designer_url
    if meta_info.license_info is not None:
        name_strings['licenseDescription'] = meta_info.license_info
    if meta_info.license_url is not None:
        name_strings['licenseInfoURL'] = meta_info.license_url
    if meta_info.sample_text is not None:
        name_strings['sampleText'] = meta_info.sample_text
    return name_strings


def _create_cff_strings(config: Config, meta_info: MetaInfo) -> tuple[str, dict[str, str]]:
    if config.cff_family_name is not None:
        cff_family_name = config.cff_family_name
    else:
        cff_family_name = meta_info.family_name
    cff_ps_name = f"{cff_family_name.replace(' ', '-')}-{meta_info.style_name}"
    cff_strings = {
        'FamilyName': cff_family_name,
        'FullName': f'{cff_family_name} {meta_info.style_name}',
        'Weight': meta_info.style_name,
    }
    if meta_info.copyright_info is not None:
        cff_strings['Notice'] = meta_info.copyright_info
    return cff_ps_name, cff_strings


def _create_outlines(glyph_data: list[list[int]], px_to_units: int) -> list[list[tuple[int, int]]]:
    """
    将字形数据转换为轮廓数据，左上角原点坐标系
    """
    # 相邻像素分组
    point_group_list = []
    for y, glyph_data_row in enumerate(glyph_data):
        for x, alpha in enumerate(glyph_data_row):
            if alpha != 0:
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
            point_outline = [
                (x * px_to_units, y * px_to_units),
                ((x + 1) * px_to_units, y * px_to_units),
                ((x + 1) * px_to_units, (y + 1) * px_to_units),
                (x * px_to_units, (y + 1) * px_to_units),
            ]
            # 一个像素有左右上下四条边，如果该边没有相邻像素，则该边线段有效
            if x <= 0 or glyph_data[y][x - 1] <= 0:  # 左
                pending_line_segments.append([point_outline[3], point_outline[0]])
            if x >= len(glyph_data[y]) - 1 or glyph_data[y][x + 1] <= 0:  # 右
                pending_line_segments.append([point_outline[1], point_outline[2]])
            if y <= 0 or glyph_data[y - 1][x] <= 0:  # 上
                pending_line_segments.append([point_outline[0], point_outline[1]])
            if y >= len(glyph_data) - 1 or glyph_data[y + 1][x] <= 0:  # 下
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


def _create_glyph(glyph: Glyph, outlines: list[list[tuple[int, int]]], px_to_units: int, is_ttf: bool) -> OTFGlyph | TTFGlyph:
    if is_ttf:
        pen = TTFGlyphPen()
    else:
        pen = OTFGlyphPen(glyph.advance_width * px_to_units, None)
    if len(outlines) > 0:
        for outline_index, outline in enumerate(outlines):
            for point_index, point in enumerate(outline):

                # 转换左上角原点坐标系为左下角原点坐标系
                x, y = point
                x += glyph.horizontal_origin_x * px_to_units
                y = (glyph.height + glyph.horizontal_origin_y) * px_to_units - y
                point = x, y

                if point_index == 0:
                    pen.moveTo(point)
                else:
                    pen.lineTo(point)
            if outline_index < len(outlines) - 1:
                pen.endPath()
            else:
                pen.closePath()
    else:
        pen.moveTo((0, 0))
        pen.closePath()
    if is_ttf:
        return pen.glyph()
    else:
        return pen.getCharString()


def _get_glyph_with_cache(glyph: Glyph, px_to_units: int, is_ttf: bool) -> OTFGlyph | TTFGlyph:
    cache_tag = f'{glyph.advance_width}#{glyph.horizontal_origin}#{glyph.data}'.replace(' ', '')
    if getattr(glyph, _CACHE_NAME_TAG, None) != cache_tag:
        setattr(glyph, _CACHE_NAME_OUTLINES, None)
        setattr(glyph, _CACHE_NAME_OTF_GLYPH, None)
        setattr(glyph, _CACHE_NAME_TTF_GLYPH, None)
        setattr(glyph, _CACHE_NAME_TAG, cache_tag)

    outlines = getattr(glyph, _CACHE_NAME_OUTLINES, None)
    if outlines is None:
        logger.debug("Create 'Outlines': %s", glyph.name)
        outlines = _create_outlines(glyph.data, px_to_units)
        setattr(glyph, _CACHE_NAME_OUTLINES, outlines)
    else:
        logger.debug("Use cached 'Outlines': %s", glyph.name)

    cache_name_xtf_glyph = _CACHE_NAME_TTF_GLYPH if is_ttf else _CACHE_NAME_OTF_GLYPH
    xtf_glyph = getattr(glyph, cache_name_xtf_glyph, None)
    if xtf_glyph is None:
        logger.debug("Create '%sGlyph': %s", 'TTF' if is_ttf else 'OTF', glyph.name)
        xtf_glyph = _create_glyph(glyph, outlines, px_to_units, is_ttf)
        setattr(glyph, cache_name_xtf_glyph, xtf_glyph)
    else:
        logger.debug("Use cached '%sGlyph': %s", 'TTF' if is_ttf else 'OTF', glyph.name)
    return xtf_glyph


def create_builder(context: 'pixel_font_builder.FontBuilder', is_ttf: bool, flavor: Flavor = None) -> FontBuilder:
    config = context.opentype_config
    units_per_em = context.size * config.px_to_units
    meta_info = context.meta_info
    horizontal_header = context.horizontal_header * config.px_to_units
    vertical_header = context.vertical_header * config.px_to_units
    os2_config = context.os2_config * config.px_to_units
    character_mapping = context.character_mapping
    glyph_order, name_to_glyph = context.prepare_glyphs()

    logger.debug("Create '%sBuilder': %s", 'TTF' if is_ttf else 'OTF', meta_info.family_name)
    builder = FontBuilder(units_per_em, isTTF=is_ttf)

    if context.created_time is not None:
        setattr(builder.font['head'], 'created', timeTools.timestampSinceEpoch(context.created_time.timestamp()))
    if context.modified_time is not None:
        setattr(builder.font['head'], 'modified', timeTools.timestampSinceEpoch(context.modified_time.timestamp()))

    logger.debug("Setup 'Name Strings'")
    name_strings = _create_name_strings(meta_info)
    builder.setupNameTable(name_strings)

    logger.debug("Setup 'Glyph Order'")
    builder.setupGlyphOrder(glyph_order)

    logger.debug("Create 'Glyphs'")
    xtf_glyphs = {}
    for glyph_name, glyph in name_to_glyph.items():
        xtf_glyphs[glyph_name] = _get_glyph_with_cache(glyph, config.px_to_units, is_ttf)
    if is_ttf:
        logger.debug("Setup 'Glyf'")
        builder.setupGlyf(xtf_glyphs)
    else:
        logger.debug("Setup 'CFF'")
        cff_ps_name, cff_strings = _create_cff_strings(config, meta_info)
        builder.setupCFF(cff_ps_name, cff_strings, xtf_glyphs, {})

    logger.debug("Setup 'Character Mapping'")
    builder.setupCharacterMap(character_mapping)

    logger.debug("Setup 'Horizontal Metrics' and 'Vertical Metrics'")
    horizontal_metrics = {}
    vertical_metrics = {}
    for glyph_name in glyph_order:
        glyph = name_to_glyph[glyph_name]
        advance_width = glyph.advance_width * config.px_to_units
        advance_height = glyph.advance_height * config.px_to_units
        if is_ttf:
            lsb = xtf_glyphs[glyph_name].xMin
        else:
            lsb = xtf_glyphs[glyph_name].calcBounds(None)[0]
        tsb = glyph.calculate_top_side_bearing() * config.px_to_units
        horizontal_metrics[glyph_name] = advance_width, lsb
        vertical_metrics[glyph_name] = advance_height, tsb
    builder.setupHorizontalMetrics(horizontal_metrics)
    builder.setupVerticalMetrics(vertical_metrics)

    logger.debug("Setup 'Horizontal Header'")
    builder.setupHorizontalHeader(
        ascent=horizontal_header.ascent,
        descent=horizontal_header.descent,
        lineGap=horizontal_header.line_gap,
    )

    logger.debug("Setup 'Vertical Header'")
    builder.setupVerticalHeader(
        ascent=vertical_header.ascent,
        descent=vertical_header.descent,
        lineGap=vertical_header.line_gap,
    )

    logger.debug("Setup 'OS2'")
    builder.setupOS2(
        sTypoAscender=horizontal_header.ascent,
        sTypoDescender=horizontal_header.descent,
        sTypoLineGap=horizontal_header.line_gap,
        usWinAscent=horizontal_header.ascent,
        usWinDescent=-horizontal_header.descent,
        sxHeight=os2_config.x_height,
        sCapHeight=os2_config.cap_height,
    )

    logger.debug("Setup 'Post'")
    builder.setupPost()

    if flavor is not None:
        logger.debug("Setup 'Flavor': %s", flavor)
        builder.font.flavor = flavor

    logger.debug("Create '%sBuilder' finished", 'TTF' if is_ttf else 'OTF')
    return builder


def create_collection_builder(builders: list[FontBuilder]) -> TTCollection:
    collection_builder = TTCollection()
    for builder in builders:
        collection_builder.fonts.append(builder.font)
    return collection_builder
