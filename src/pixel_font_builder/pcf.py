import logging
import math

from pcffont import PcfFont, PcfTableFormat, PcfMetric, PcfProperties, PcfAccelerators, PcfMetrics, PcfBitmaps, PcfBdfEncodings, PcfScalableWidths, PcfGlyphNames

import pixel_font_builder
from pixel_font_builder.info import SerifMode, WidthMode

logger = logging.getLogger('pixel_font_builder.pcf')


class Config:
    def __init__(
            self,
            resolution_x: int = 75,
            resolution_y: int = 75,
    ):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y


def create_font(context: 'pixel_font_builder.FontBuilder') -> PcfFont:
    config = context.pcf_config
    font_size = context.size
    meta_info = context.meta_info
    horizontal_header = context.horizontal_header
    os2_config = context.os2_config
    character_mapping = context.character_mapping
    _, name_to_glyph = context.prepare_glyphs()

    logger.debug("Create 'PcfFont': %s", meta_info.family_name)
    font = PcfFont()
    font.bdf_encodings = PcfBdfEncodings()
    font.glyph_names = PcfGlyphNames()
    font.metrics = PcfMetrics()
    font.ink_metrics = PcfMetrics()
    font.scalable_widths = PcfScalableWidths()
    font.bitmaps = PcfBitmaps()
    font.accelerators = PcfAccelerators(PcfTableFormat(has_ink_bounds=True))
    font.bdf_accelerators = font.accelerators
    font.properties = PcfProperties()

    logger.debug("Setup 'Glyphs'")
    min_bounds = None
    max_bounds = None
    font.bdf_encodings.default_char = 0xFFFE
    character_mapping[font.bdf_encodings.default_char] = '.notdef'
    for code_point, glyph_name in sorted(character_mapping.items()):
        if code_point > 0xFFFF:
            break
        logger.debug("Add 'Glyph': %s", glyph_name)
        glyph = name_to_glyph[glyph_name]
        font.bdf_encodings[code_point] = len(font.glyph_names)
        font.glyph_names.append(glyph_name)
        metric = PcfMetric(
            left_side_bearing=glyph.horizontal_origin_x,
            right_side_bearing=glyph.horizontal_origin_x + glyph.width,
            character_width=glyph.advance_width,
            ascent=glyph.horizontal_origin_y + glyph.height,
            descent=-glyph.horizontal_origin_y,
        )
        if min_bounds is None or (metric.left_side_bearing + metric.right_side_bearing) < (min_bounds.left_side_bearing + min_bounds.right_side_bearing):
            min_bounds = metric
        if max_bounds is None or (metric.left_side_bearing + metric.right_side_bearing) > (max_bounds.left_side_bearing + max_bounds.right_side_bearing):
            max_bounds = metric
        font.metrics.append(metric)
        font.ink_metrics.append(metric)
        font.scalable_widths.append(math.ceil((glyph.advance_width / font_size) * (75 / config.resolution_x) * 1000))
        font.bitmaps.append(glyph.data)

    logger.debug("Setup 'Accelerators'")
    font.accelerators.ink_inside = True
    font.accelerators.ink_metrics = True
    font.accelerators.font_ascent = horizontal_header.ascent
    font.accelerators.font_descent = -horizontal_header.descent
    font.accelerators.min_bounds = min_bounds
    font.accelerators.max_bounds = max_bounds
    font.accelerators.ink_min_bounds = min_bounds
    font.accelerators.ink_max_bounds = max_bounds

    logger.debug("Setup 'Properties'")
    font.properties.foundry = meta_info.manufacturer
    font.properties.family_name = meta_info.family_name
    font.properties.weight_name = meta_info.style_name
    font.properties.slant = 'R'
    font.properties.setwidth_name = 'Normal'
    if meta_info.serif_mode == SerifMode.SERIF:
        font.properties.add_style_name = 'Serif'
    elif meta_info.serif_mode == SerifMode.SANS_SERIF:
        font.properties.add_style_name = 'Sans Serif'
    else:
        font.properties.add_style_name = meta_info.serif_mode
    font.properties.pixel_size = font_size
    font.properties.point_size = font_size * 10
    font.properties.resolution_x = config.resolution_x
    font.properties.resolution_y = config.resolution_y
    if meta_info.width_mode == WidthMode.MONOSPACED:
        font.properties.spacing = 'M'
    elif meta_info.width_mode == WidthMode.DUOSPACED:
        font.properties.spacing = 'D'
    elif meta_info.width_mode == WidthMode.PROPORTIONAL:
        font.properties.spacing = 'P'
    else:
        font.properties.spacing = meta_info.width_mode
    font.properties.average_width = round(sum([metric.character_width * 10 for metric in font.metrics]) / len(font.metrics))
    font.properties.charset_registry = 'ISO10646'
    font.properties.charset_encoding = '1'
    font.properties.generate_xlfd()

    font.properties.x_height = os2_config.x_height
    font.properties.cap_height = os2_config.cap_height

    font.properties.font_version = meta_info.version
    font.properties.copyright = meta_info.copyright_info
    font.properties['LICENSE'] = meta_info.license_info

    logger.debug("Create 'PcfFont' finished")
    return font
