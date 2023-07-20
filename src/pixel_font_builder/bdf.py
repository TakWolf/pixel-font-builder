import logging
import math

from bdffont import BdfFont, BdfGlyph, xlfd

from pixel_font_builder import font
from pixel_font_builder.info import SerifMode, WidthMode

logger = logging.getLogger('pixel_font_builder.bdf')


class Configs:
    def __init__(
            self,
            resolution_x: int = 75,
            resolution_y: int = 75,
    ):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y


def _create_glyph(context: 'font.FontBuilder', code_point: int, glyph_name: str) -> BdfGlyph:
    glyph = context.get_glyph(glyph_name)
    scalable_width_x = math.ceil((glyph.advance_width / context.size) * (72 / context.bdf_configs.resolution_x) * 1000)
    return BdfGlyph(
        name=glyph.name,
        code_point=code_point,
        scalable_width=(scalable_width_x, 0),
        device_width=(glyph.advance_width, 0),
        bounding_box_size=glyph.size,
        bounding_box_offset=glyph.offset,
        bitmap=glyph.data,
    )


def create_builder(context: 'font.FontBuilder') -> BdfFont:
    logger.debug("Create 'BDFBuilder': %s", context.meta_infos.family_name)
    context.check_ready()

    builder = BdfFont(
        point_size=context.size,
        resolution_xy=(context.bdf_configs.resolution_x, context.bdf_configs.resolution_y),
        bounding_box_size=(context.size, context.line_height),
        bounding_box_offset=(0, context.descent),
    )

    logger.debug("Add 'Glyph': .notdef")
    builder.add_glyph(_create_glyph(context, -1, '.notdef'))
    for code_point, glyph_name in context.character_mapping.items():
        logger.debug("Add 'Glyph': %s", glyph_name)
        builder.add_glyph(_create_glyph(context, code_point, glyph_name))

    logger.debug("Setup 'Properties'")
    builder.properties.foundry = context.meta_infos.manufacturer
    builder.properties.family_name = context.meta_infos.family_name
    builder.properties.weight_name = context.meta_infos.style_name
    builder.properties.slant = xlfd.Slant.ROMAN
    builder.properties.setwidth_name = xlfd.SetwidthName.NORMAL
    if context.meta_infos.serif_mode == SerifMode.SERIF:
        builder.properties.add_style_name = xlfd.AddStyleName.SERIF
    elif context.meta_infos.serif_mode == SerifMode.SANS_SERIF:
        builder.properties.add_style_name = xlfd.AddStyleName.SANS_SERIF
    else:
        builder.properties.add_style_name = context.meta_infos.serif_mode
    builder.properties.pixel_size = context.size
    builder.properties.point_size = context.size * 10
    builder.properties.resolution_x = context.bdf_configs.resolution_x
    builder.properties.resolution_y = context.bdf_configs.resolution_y
    if context.meta_infos.width_mode == WidthMode.MONOSPACED:
        builder.properties.spacing = xlfd.Spacing.MONOSPACED
    elif context.meta_infos.width_mode == WidthMode.PROPORTIONAL:
        builder.properties.spacing = xlfd.Spacing.PROPORTIONAL
    else:
        builder.properties.spacing = context.meta_infos.width_mode
    builder.properties.average_width = round(sum([glyph.device_width_x * 10 for glyph in builder.code_point_to_glyph.values()]) / builder.get_glyphs_count())
    builder.properties.charset_registry = xlfd.CharsetRegistry.ISO10646
    builder.properties.charset_encoding = '1'

    builder.properties.default_char = -1
    builder.properties.font_ascent = context.ascent
    builder.properties.font_descent = context.descent
    builder.properties.x_height = context.x_height
    builder.properties.cap_height = context.cap_height

    builder.properties.font_version = context.meta_infos.version
    builder.properties.copyright = context.meta_infos.copyright_info
    builder.properties['LICENSE'] = context.meta_infos.license_info

    builder.generate_xlfd_font_name()

    logger.debug("Create 'BDFBuilder' finished")
    return builder
