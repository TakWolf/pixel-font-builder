import logging
import math

from bdffont import BdfFont, BdfGlyph, xlfd

from pixel_font_builder.glyph import Glyph
from pixel_font_builder.info import Metrics, MetaInfos, SerifMode, WidthMode

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
        configs: Configs,
        metrics: Metrics,
        code_point: int,
        glyph: Glyph,
) -> BdfGlyph:
    scalable_width_x = math.ceil((glyph.advance_width / metrics.size) * (72 / configs.resolution_x) * 1000)
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
        configs: Configs,
        metrics: Metrics,
        meta_infos: MetaInfos,
        character_mapping: dict[int, str],
        name_to_glyph: dict[str, Glyph],
) -> BdfFont:
    logger.debug("Create 'BDFBuilder': %s", meta_infos.family_name)
    builder = BdfFont(
        point_size=metrics.size,
        resolution_xy=(configs.resolution_x, configs.resolution_y),
        bounding_box_size=(metrics.size, metrics.line_height),
        bounding_box_offset=(0, metrics.descent),
    )

    logger.debug("Add 'Glyph': .notdef")
    builder.add_glyph(_create_glyph(configs, metrics, -1, name_to_glyph['.notdef']))
    for code_point, glyph_name in character_mapping.items():
        logger.debug("Add 'Glyph': %s", glyph_name)
        builder.add_glyph(_create_glyph(configs, metrics, code_point, name_to_glyph[glyph_name]))

    logger.debug("Setup 'Properties'")
    builder.properties.foundry = meta_infos.manufacturer
    builder.properties.family_name = meta_infos.family_name
    builder.properties.weight_name = meta_infos.style_name
    builder.properties.slant = xlfd.Slant.ROMAN
    builder.properties.setwidth_name = xlfd.SetwidthName.NORMAL
    if meta_infos.serif_mode == SerifMode.SERIF:
        builder.properties.add_style_name = xlfd.AddStyleName.SERIF
    elif meta_infos.serif_mode == SerifMode.SANS_SERIF:
        builder.properties.add_style_name = xlfd.AddStyleName.SANS_SERIF
    else:
        builder.properties.add_style_name = meta_infos.serif_mode
    builder.properties.pixel_size = metrics.size
    builder.properties.point_size = metrics.size * 10
    builder.properties.resolution_x = configs.resolution_x
    builder.properties.resolution_y = configs.resolution_y
    if meta_infos.width_mode == WidthMode.MONOSPACED:
        builder.properties.spacing = xlfd.Spacing.MONOSPACED
    elif meta_infos.width_mode == WidthMode.PROPORTIONAL:
        builder.properties.spacing = xlfd.Spacing.PROPORTIONAL
    else:
        builder.properties.spacing = meta_infos.width_mode
    builder.properties.average_width = round(sum([glyph.device_width_x * 10 for glyph in builder.code_point_to_glyph.values()]) / builder.get_glyphs_count())
    builder.properties.charset_registry = xlfd.CharsetRegistry.ISO10646
    builder.properties.charset_encoding = '1'

    builder.properties.default_char = -1
    builder.properties.font_ascent = metrics.ascent
    builder.properties.font_descent = metrics.descent
    builder.properties.x_height = metrics.x_height
    builder.properties.cap_height = metrics.cap_height

    builder.properties.font_version = meta_infos.version
    builder.properties.copyright = meta_infos.copyright_info
    builder.properties['LICENSE'] = meta_infos.license_info

    builder.generate_xlfd_font_name()

    logger.debug("Create 'BDFBuilder' finished")
    return builder
