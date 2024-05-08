import logging
import math
from collections import ChainMap

from bdffont import BdfFont, BdfGlyph

import pixel_font_builder
from pixel_font_builder.meta import SerifStyle, SlantStyle, WidthMode

logger = logging.getLogger('pixel_font_builder.bdf')

_DEFAULT_CHAR = 0xFFFE


class Configs:
    def __init__(
            self,
            resolution_x: int = 75,
            resolution_y: int = 75,
            only_basic_plane: bool = False,
    ):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.only_basic_plane = only_basic_plane


def create_builder(context: 'pixel_font_builder.FontBuilder') -> BdfFont:
    configs = context.bdf_configs
    font_metrics = context.font_metrics
    meta_info = context.meta_info
    character_mapping = ChainMap({_DEFAULT_CHAR: '.notdef'}, context.character_mapping)
    _, name_to_glyph = context.prepare_glyphs()

    logger.debug("Create 'BdfFont': %s", meta_info.family_name)
    font = BdfFont(
        point_size=font_metrics.font_size,
        resolution=(configs.resolution_x, configs.resolution_y),
        bounding_box=(font_metrics.font_size, font_metrics.horizontal_layout.line_height, 0, font_metrics.horizontal_layout.descent),
    )

    logger.debug("Setup 'Glyphs'")
    for code_point, glyph_name in sorted(character_mapping.items()):
        if code_point > 0xFFFF and configs.only_basic_plane:
            break
        logger.debug("Add 'Glyph': %s", glyph_name)
        glyph = name_to_glyph[glyph_name]
        font.glyphs.append(BdfGlyph(
            name=glyph_name,
            encoding=code_point,
            scalable_width=(math.ceil((glyph.advance_width / font_metrics.font_size) * (75 / configs.resolution_x) * 1000), 0),
            device_width=(glyph.advance_width, 0),
            bounding_box=(glyph.width, glyph.height, glyph.horizontal_origin_x, glyph.horizontal_origin_y),
            bitmap=glyph.bitmap,
        ))

    logger.debug("Setup 'Properties'")
    font.properties.foundry = meta_info.manufacturer
    font.properties.family_name = meta_info.family_name
    font.properties.weight_name = meta_info.weight_name
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
    if meta_info.serif_style == SerifStyle.SERIF:
        font.properties.add_style_name = 'Serif'
    elif meta_info.serif_style == SerifStyle.SANS_SERIF:
        font.properties.add_style_name = 'Sans Serif'
    else:
        font.properties.add_style_name = meta_info.serif_style
    font.properties.pixel_size = font_metrics.font_size
    font.properties.point_size = font_metrics.font_size * 10
    font.properties.resolution_x = configs.resolution_x
    font.properties.resolution_y = configs.resolution_y
    if meta_info.width_mode == WidthMode.MONOSPACED:
        font.properties.spacing = 'M'
    elif meta_info.width_mode == WidthMode.DUOSPACED:
        font.properties.spacing = 'D'
    elif meta_info.width_mode == WidthMode.PROPORTIONAL:
        font.properties.spacing = 'P'
    font.properties.average_width = round(sum([glyph.device_width_x * 10 for glyph in font.glyphs]) / len(font.glyphs))
    font.properties.charset_registry = 'ISO10646'
    font.properties.charset_encoding = '1'
    font.generate_name_as_xlfd()

    font.properties.default_char = _DEFAULT_CHAR
    font.properties.font_ascent = font_metrics.horizontal_layout.ascent
    font.properties.font_descent = -font_metrics.horizontal_layout.descent
    font.properties.x_height = font_metrics.x_height
    font.properties.cap_height = font_metrics.cap_height

    font.properties.font_version = meta_info.version
    font.properties.copyright = meta_info.copyright_info
    font.properties['LICENSE'] = meta_info.license_info

    logger.debug("Create 'BdfFont' finished")
    return font
