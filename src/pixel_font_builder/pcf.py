import math
from collections import ChainMap

from pcffont import PcfFontBuilder, PcfGlyph

import pixel_font_builder
from pixel_font_builder.meta import SerifStyle, SlantStyle, WidthStyle

_DEFAULT_CHAR = 0xFFFE


class Config:
    resolution_x: int
    resolution_y: int
    draw_right_to_left: bool
    ms_byte_first: bool
    ms_bit_first: bool
    glyph_pad_index: int
    scan_unit_index: int

    def __init__(
            self,
            resolution_x: int = 75,
            resolution_y: int = 75,
            draw_right_to_left: bool = False,
            ms_byte_first: bool = True,
            ms_bit_first: bool = True,
            glyph_pad_index: int = 0,
            scan_unit_index: int = 0,
    ):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.draw_right_to_left = draw_right_to_left
        self.ms_byte_first = ms_byte_first
        self.ms_bit_first = ms_bit_first
        self.glyph_pad_index = glyph_pad_index
        self.scan_unit_index = scan_unit_index


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
            origin=glyph.horizontal_origin,
            bitmap=glyph.bitmap,
        ))

    builder.properties.foundry = meta_info.manufacturer
    builder.properties.family_name = meta_info.family_name
    builder.properties.weight_name = meta_info.weight_name
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
    if meta_info.serif_style == SerifStyle.SERIF:
        builder.properties.add_style_name = 'Serif'
    elif meta_info.serif_style == SerifStyle.SANS_SERIF:
        builder.properties.add_style_name = 'Sans Serif'
    else:
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
    builder.properties.copyright = meta_info.copyright_info
    builder.properties['LICENSE'] = meta_info.license_info

    return builder
