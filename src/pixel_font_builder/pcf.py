import logging
import math
from collections import ChainMap

from pcffont import PcfFontBuilder, PcfGlyph

import pixel_font_builder
from pixel_font_builder.info import SerifMode, WidthMode

logger = logging.getLogger('pixel_font_builder.pcf')

_DEFAULT_CHAR = 0xFFFE


class Configs:
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
    configs = context.pcf_configs
    font_metrics = context.font_metrics
    meta_info = context.meta_info
    character_mapping = ChainMap({_DEFAULT_CHAR: '.notdef'}, context.character_mapping)
    _, name_to_glyph = context.prepare_glyphs()

    logger.debug("Create 'PcfFont': %s", meta_info.family_name)
    builder = PcfFontBuilder()
    builder.configs.font_ascent = font_metrics.horizontal_layout.ascent
    builder.configs.font_descent = -font_metrics.horizontal_layout.descent
    builder.configs.default_char = _DEFAULT_CHAR
    builder.configs.draw_right_to_left = configs.draw_right_to_left
    builder.configs.ms_byte_first = configs.ms_byte_first
    builder.configs.ms_bit_first = configs.ms_bit_first
    builder.configs.glyph_pad_index = configs.glyph_pad_index
    builder.configs.scan_unit_index = configs.scan_unit_index

    logger.debug("Setup 'Glyphs'")
    for code_point, glyph_name in sorted(character_mapping.items()):
        if code_point > 0xFFFF:
            break
        logger.debug("Add 'Glyph': %s", glyph_name)
        glyph = name_to_glyph[glyph_name]
        builder.glyphs.append(PcfGlyph(
            name=glyph_name,
            encoding=code_point,
            scalable_width=math.ceil((glyph.advance_width / font_metrics.font_size) * (75 / configs.resolution_x) * 1000),
            character_width=glyph.advance_width,
            dimensions=glyph.dimensions,
            origin=glyph.horizontal_origin,
            bitmap=glyph.bitmap,
        ))

    logger.debug("Setup 'Properties'")
    builder.properties.foundry = meta_info.manufacturer
    builder.properties.family_name = meta_info.family_name
    builder.properties.weight_name = meta_info.style_name
    builder.properties.slant = 'R'
    builder.properties.setwidth_name = 'Normal'
    if meta_info.serif_mode == SerifMode.SERIF:
        builder.properties.add_style_name = 'Serif'
    elif meta_info.serif_mode == SerifMode.SANS_SERIF:
        builder.properties.add_style_name = 'Sans Serif'
    else:
        builder.properties.add_style_name = meta_info.serif_mode
    builder.properties.pixel_size = font_metrics.font_size
    builder.properties.point_size = font_metrics.font_size * 10
    builder.properties.resolution_x = configs.resolution_x
    builder.properties.resolution_y = configs.resolution_y
    if meta_info.width_mode == WidthMode.MONOSPACED:
        builder.properties.spacing = 'M'
    elif meta_info.width_mode == WidthMode.DUOSPACED:
        builder.properties.spacing = 'D'
    elif meta_info.width_mode == WidthMode.PROPORTIONAL:
        builder.properties.spacing = 'P'
    else:
        builder.properties.spacing = meta_info.width_mode
    builder.properties.average_width = round(sum([glyph.character_width * 10 for glyph in builder.glyphs]) / len(builder.glyphs))
    builder.properties.charset_registry = 'ISO10646'
    builder.properties.charset_encoding = '1'
    builder.properties.generate_xlfd()

    builder.properties.x_height = font_metrics.x_height
    builder.properties.cap_height = font_metrics.cap_height

    builder.properties.font_version = meta_info.version
    builder.properties.copyright = meta_info.copyright_info
    builder.properties['LICENSE'] = meta_info.license_info

    logger.debug("Create 'PcfFont' finished")
    return builder
