from __future__ import annotations

import math
import statistics
from collections import ChainMap

from bdffont import BdfFont, BdfGlyph

import pixel_font_builder
from pixel_font_builder.meta import WeightName, SlantStyle, WidthStyle

_DEFAULT_CHAR = 0xFFFE


def create_font_builder(context: pixel_font_builder.FontBuilder) -> BdfFont:
    config = context.bdf_config
    font_metric = context.font_metric
    meta_info = context.meta_info
    _, name_to_glyph = context.prepare_glyphs()
    character_mapping = ChainMap({_DEFAULT_CHAR: '.notdef'}, context.character_mapping)

    font = BdfFont(
        point_size=font_metric.font_size,
        resolution=(config.resolution_x, config.resolution_y),
        bounding_box=(font_metric.font_size, font_metric.horizontal_layout.line_height, 0, font_metric.horizontal_layout.descent),
    )

    for code_point, glyph_name in sorted(character_mapping.items()):
        if code_point > 0xFFFF and config.only_basic_plane:
            break
        glyph = name_to_glyph[glyph_name]
        font.glyphs.append(BdfGlyph(
            name=glyph_name,
            encoding=code_point,
            scalable_width=(math.ceil((glyph.advance_width / font_metric.font_size) * (75 / config.resolution_x) * 1000), 0),
            device_width=(glyph.advance_width, 0),
            bounding_box=(glyph.width, glyph.height, glyph.horizontal_offset_x, glyph.horizontal_offset_y),
            bitmap=glyph.bitmap,
        ))

    if meta_info.manufacturer is not None:
        font.properties.foundry = meta_info.manufacturer.replace('-', '_')
    font.properties.family_name = meta_info.family_name.replace('-', '_')
    font.properties.weight_name = meta_info.weight_name or WeightName.REGULAR
    if meta_info.slant_style is None or meta_info.slant_style == SlantStyle.NORMAL:
        font.properties.slant = 'R'
    elif meta_info.slant_style == SlantStyle.ITALIC:
        font.properties.slant = 'I'
    elif meta_info.slant_style == SlantStyle.OBLIQUE:
        font.properties.slant = 'O'
    elif meta_info.slant_style == SlantStyle.REVERSE_ITALIC:
        font.properties.slant = 'RI'
    elif meta_info.slant_style == SlantStyle.REVERSE_OBLIQUE:
        font.properties.slant = 'RO'
    else:
        font.properties.slant = 'OT'
    font.properties.setwidth_name = 'Normal'
    if meta_info.serif_style is not None:
        font.properties.add_style_name = meta_info.serif_style
    font.properties.pixel_size = font_metric.font_size
    font.properties.point_size = font_metric.font_size * 10
    font.properties.resolution_x = config.resolution_x
    font.properties.resolution_y = config.resolution_y
    if meta_info.width_style == WidthStyle.MONOSPACED:
        font.properties.spacing = 'M'
    elif meta_info.width_style == WidthStyle.DUOSPACED:
        font.properties.spacing = 'D'
    elif meta_info.width_style == WidthStyle.CHARACTER_CELL:
        font.properties.spacing = 'C'
    elif meta_info.width_style == WidthStyle.PROPORTIONAL:
        font.properties.spacing = 'P'
    font.properties.average_width = round(statistics.fmean(glyph.device_width_x * 10 for glyph in font.glyphs))
    font.properties.charset_registry = 'ISO10646'
    font.properties.charset_encoding = '1'
    font.generate_name_as_xlfd()

    font.properties.default_char = _DEFAULT_CHAR
    font.properties.font_ascent = font_metric.horizontal_layout.ascent
    font.properties.font_descent = -font_metric.horizontal_layout.descent
    if font_metric.x_height != 0:
        font.properties.x_height = font_metric.x_height
    if font_metric.cap_height != 0:
        font.properties.cap_height = font_metric.cap_height
    if font_metric.underline_thickness != 0:
        font.properties.underline_position = font_metric.underline_position
        font.properties.underline_thickness = font_metric.underline_thickness

    font.properties.font_version = meta_info.version
    if meta_info.copyright_info is not None:
        font.properties.copyright = '<br>'.join(meta_info.copyright_info.splitlines())
    if meta_info.license_info is not None:
        font.properties['LICENSE'] = '<br>'.join(meta_info.license_info.splitlines())

    return font
