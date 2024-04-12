import logging
import math

from bdffont import BdfFont, BdfGlyph, xlfd

import pixel_font_builder
from pixel_font_builder.glyph import Glyph
from pixel_font_builder.info import SerifMode, WidthMode

logger = logging.getLogger('pixel_font_builder.bdf')


class Config:
    def __init__(
            self,
            resolution_x: int = 75,
            resolution_y: int = 75,
            only_basic_plane: bool = True,
    ):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.only_basic_plane = only_basic_plane


def _create_glyph(
        font_size: int,
        config: Config,
        code_point: int,
        glyph: Glyph,
) -> BdfGlyph:
    scalable_width_x = math.ceil((glyph.advance_width / font_size) * (75 / config.resolution_x) * 1000)
    return BdfGlyph(
        name=glyph.name,
        code_point=code_point,
        scalable_width=(scalable_width_x, 0),
        device_width=(glyph.advance_width, 0),
        bounding_box_size=glyph.dimensions,
        bounding_box_offset=glyph.horizontal_origin,
        bitmap=glyph.data,
    )


def create_font(context: 'pixel_font_builder.FontBuilder') -> BdfFont:
    config = context.bdf_config
    font_size = context.size
    meta_info = context.meta_info
    horizontal_header = context.horizontal_header
    os2_config = context.os2_config
    character_mapping = context.character_mapping
    _, name_to_glyph = context.prepare_glyphs()

    logger.debug("Create 'BdfFont': %s", meta_info.family_name)
    font = BdfFont(
        point_size=font_size,
        resolution_xy=(config.resolution_x, config.resolution_y),
        bounding_box_size=(font_size, horizontal_header.line_height),
        bounding_box_offset=(0, horizontal_header.descent),
    )

    logger.debug("Add 'Glyph': .notdef")
    font.glyphs.append(_create_glyph(font_size, config, -1, name_to_glyph['.notdef']))
    for code_point, glyph_name in sorted(character_mapping.items()):
        if code_point > 0xFFFF and config.only_basic_plane:
            break
        logger.debug("Add 'Glyph': %s", glyph_name)
        font.glyphs.append(_create_glyph(font_size, config, code_point, name_to_glyph[glyph_name]))

    logger.debug("Setup 'Properties'")
    font.properties.foundry = meta_info.manufacturer
    font.properties.family_name = meta_info.family_name
    font.properties.weight_name = meta_info.style_name
    font.properties.slant = xlfd.Slant.ROMAN
    font.properties.setwidth_name = xlfd.SetwidthName.NORMAL
    if meta_info.serif_mode == SerifMode.SERIF:
        font.properties.add_style_name = xlfd.AddStyleName.SERIF
    elif meta_info.serif_mode == SerifMode.SANS_SERIF:
        font.properties.add_style_name = xlfd.AddStyleName.SANS_SERIF
    else:
        font.properties.add_style_name = meta_info.serif_mode
    font.properties.pixel_size = font_size
    font.properties.point_size = font_size * 10
    font.properties.resolution_x = config.resolution_x
    font.properties.resolution_y = config.resolution_y
    if meta_info.width_mode == WidthMode.MONOSPACED:
        font.properties.spacing = xlfd.Spacing.MONOSPACED
    elif meta_info.width_mode == WidthMode.DUOSPACED:
        font.properties.spacing = 'D'
    elif meta_info.width_mode == WidthMode.PROPORTIONAL:
        font.properties.spacing = xlfd.Spacing.PROPORTIONAL
    else:
        font.properties.spacing = meta_info.width_mode
    font.properties.average_width = round(sum([glyph.device_width_x * 10 for glyph in font.glyphs]) / len(font.glyphs))
    font.properties.charset_registry = xlfd.CharsetRegistry.ISO10646
    font.properties.charset_encoding = '1'

    font.properties.default_char = -1
    font.properties.font_ascent = horizontal_header.ascent
    font.properties.font_descent = -horizontal_header.descent
    font.properties.x_height = os2_config.x_height
    font.properties.cap_height = os2_config.cap_height

    font.properties.font_version = meta_info.version
    font.properties.copyright = meta_info.copyright_info
    font.properties['LICENSE'] = meta_info.license_info

    font.generate_xlfd_font_name()

    logger.debug("Create 'BdfFont' finished")
    return font
