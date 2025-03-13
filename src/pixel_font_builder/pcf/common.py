import math
import re
from collections import ChainMap

from pcffont import PcfFontBuilder, PcfGlyph

import pixel_font_builder
from pixel_font_builder.meta import WeightName, SlantStyle, WidthStyle

_DEFAULT_CHAR = 0xFFFE


def create_builder(context: 'pixel_font_builder.FontBuilder') -> PcfFontBuilder:
    config = context.pcf_config
    font_metric = context.font_metric
    meta_info = context.meta_info
    character_mapping = ChainMap({_DEFAULT_CHAR: '.notdef'}, context.character_mapping)
    _, name_to_glyph = context.prepare_glyphs()

    builder = PcfFontBuilder()
    builder.config.font_ascent = font_metric.horizontal_layout.ascent
    builder.config.font_descent = -font_metric.horizontal_layout.descent
    builder.config.default_char = _DEFAULT_CHAR
    builder.config.draw_right_to_left = config.draw_right_to_left
    builder.config.ms_byte_first = config.ms_byte_first
    builder.config.ms_bit_first = config.ms_bit_first
    builder.config.glyph_pad_index = config.glyph_pad_index
    builder.config.scan_unit_index = config.scan_unit_index

    for code_point, glyph_name in sorted(character_mapping.items()):
        if code_point > 0xFFFF:
            break
        glyph = name_to_glyph[glyph_name]
        builder.glyphs.append(PcfGlyph(
            name=glyph_name,
            encoding=code_point,
            scalable_width=math.ceil((glyph.advance_width / font_metric.font_size) * (75 / config.resolution_x) * 1000),
            character_width=glyph.advance_width,
            dimensions=glyph.dimensions,
            offset=glyph.horizontal_offset,
            bitmap=glyph.bitmap,
        ))

    if meta_info.manufacturer is not None:
        builder.properties.foundry = meta_info.manufacturer.replace('-', '_')
    builder.properties.family_name = meta_info.family_name.replace('-', '_')
    builder.properties.weight_name = meta_info.weight_name or WeightName.REGULAR
    if meta_info.slant_style is None or meta_info.slant_style == SlantStyle.NORMAL:
        builder.properties.slant = 'R'
    elif meta_info.slant_style == SlantStyle.ITALIC:
        builder.properties.slant = 'I'
    elif meta_info.slant_style == SlantStyle.OBLIQUE:
        builder.properties.slant = 'O'
    elif meta_info.slant_style == SlantStyle.REVERSE_ITALIC:
        builder.properties.slant = 'RI'
    elif meta_info.slant_style == SlantStyle.REVERSE_OBLIQUE:
        builder.properties.slant = 'RO'
    else:
        builder.properties.slant = 'OT'
    builder.properties.setwidth_name = 'Normal'
    if meta_info.serif_style is not None:
        builder.properties.add_style_name = meta_info.serif_style
    builder.properties.pixel_size = font_metric.font_size
    builder.properties.point_size = font_metric.font_size * 10
    builder.properties.resolution_x = config.resolution_x
    builder.properties.resolution_y = config.resolution_y
    if meta_info.width_style == WidthStyle.MONOSPACED:
        builder.properties.spacing = 'M'
    elif meta_info.width_style == WidthStyle.DUOSPACED:
        builder.properties.spacing = 'D'
    elif meta_info.width_style == WidthStyle.PROPORTIONAL:
        builder.properties.spacing = 'P'
    builder.properties.average_width = round(sum([glyph.character_width * 10 for glyph in builder.glyphs]) / len(builder.glyphs))
    builder.properties.charset_registry = 'ISO10646'
    builder.properties.charset_encoding = '1'
    builder.properties.generate_xlfd()

    builder.properties.x_height = font_metric.x_height
    builder.properties.cap_height = font_metric.cap_height

    builder.properties.font_version = meta_info.version
    if meta_info.copyright_info is not None:
        builder.properties.copyright = re.sub(r'\r\n|\r|\n', '<br>', meta_info.copyright_info)
    if meta_info.license_info is not None:
        builder.properties['LICENSE'] = re.sub(r'\r\n|\r|\n', '<br>', meta_info.license_info)

    return builder
