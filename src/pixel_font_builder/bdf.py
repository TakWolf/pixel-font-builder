import logging
import math

from bdffont import BdfFont, BdfGlyph, xlfd

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.info import SerifMode, WidthMode, MetaInfos, HorizontalHeader

logger = logging.getLogger('pixel_font_builder.bdf')


class Configs:
    def __init__(
            self,
            resolution_x: int = 75,
            resolution_y: int = 75,
    ):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y


def _create_glyph(
        font_size: int,
        configs: Configs,
        code_point: int,
        glyph: Glyph,
) -> BdfGlyph:
    scalable_width_x = math.ceil((glyph.advance_width / font_size) * (72 / configs.resolution_x) * 1000)
    return BdfGlyph(
        name=glyph.name,
        code_point=code_point,
        scalable_width=(scalable_width_x, 0),
        device_width=(glyph.advance_width, 0),
        bounding_box_size=glyph.size,
        bounding_box_offset=glyph.offset,
        bitmap=glyph.data,
    )


def create_builder(
        font_size: int,
        configs: Configs,
        meta_infos: MetaInfos,
        horizontal_header: HorizontalHeader,
        character_mapping: dict[int, str],
        name_to_glyph: dict[str, Glyph],
) -> BdfFont:
    logger.debug("Create 'BdfFont': %s", meta_infos.family_name)
    font = BdfFont(
        point_size=font_size,
        resolution_xy=(configs.resolution_x, configs.resolution_y),
        bounding_box_size=(font_size, horizontal_header.line_height),
        bounding_box_offset=(0, horizontal_header.descent),
    )

    logger.debug("Add 'Glyph': .notdef")
    font.add_glyph(_create_glyph(font_size, configs, -1, name_to_glyph['.notdef']))
    for code_point, glyph_name in character_mapping.items():
        logger.debug("Add 'Glyph': %s", glyph_name)
        font.add_glyph(_create_glyph(font_size, configs, code_point, name_to_glyph[glyph_name]))

    logger.debug("Setup 'Properties'")
    font.properties.foundry = meta_infos.manufacturer
    font.properties.family_name = meta_infos.family_name
    font.properties.weight_name = meta_infos.style_name
    font.properties.slant = xlfd.Slant.ROMAN
    font.properties.setwidth_name = xlfd.SetwidthName.NORMAL
    if meta_infos.serif_mode == SerifMode.SERIF:
        font.properties.add_style_name = xlfd.AddStyleName.SERIF
    elif meta_infos.serif_mode == SerifMode.SANS_SERIF:
        font.properties.add_style_name = xlfd.AddStyleName.SANS_SERIF
    else:
        font.properties.add_style_name = meta_infos.serif_mode
    font.properties.pixel_size = font_size
    font.properties.point_size = font_size * 10
    font.properties.resolution_x = configs.resolution_x
    font.properties.resolution_y = configs.resolution_y
    if meta_infos.width_mode == WidthMode.MONOSPACED:
        font.properties.spacing = xlfd.Spacing.MONOSPACED
    elif meta_infos.width_mode == WidthMode.PROPORTIONAL:
        font.properties.spacing = xlfd.Spacing.PROPORTIONAL
    else:
        font.properties.spacing = meta_infos.width_mode
    font.properties.average_width = round(sum([glyph.device_width_x * 10 for glyph in font.code_point_to_glyph.values()]) / font.get_glyphs_count())
    font.properties.charset_registry = xlfd.CharsetRegistry.ISO10646
    font.properties.charset_encoding = '1'

    font.properties.default_char = -1
    font.properties.font_ascent = horizontal_header.ascent
    font.properties.font_descent = horizontal_header.descent
    font.properties.x_height = horizontal_header.x_height
    font.properties.cap_height = horizontal_header.cap_height

    font.properties.font_version = meta_infos.version
    font.properties.copyright = meta_infos.copyright_info
    font.properties['LICENSE'] = meta_infos.license_info

    font.generate_xlfd_font_name()

    logger.debug("Create 'BdfFont' finished")
    return font
