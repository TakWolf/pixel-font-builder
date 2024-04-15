import logging
import math

from pcffont import PcfFont, PcfMetric, PcfProperties, PcfAccelerators, PcfMetrics, PcfBitmaps, PcfBdfEncodings, PcfScalableWidths, PcfGlyphNames

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

    logger.debug("Setup 'Glyphs'")
    bdf_encodings = PcfBdfEncodings()
    glyph_names = PcfGlyphNames()
    metrics = PcfMetrics()
    scalable_widths = PcfScalableWidths()
    bitmaps = PcfBitmaps()

    min_bounds = None
    max_bounds = None
    bdf_encodings.default_char = 0xFFFE
    character_mapping[bdf_encodings.default_char] = '.notdef'
    for code_point, glyph_name in sorted(character_mapping.items()):
        if code_point > 0xFFFF:
            break
        glyph = name_to_glyph[glyph_name]
        logger.debug("Add 'Encoding': %04X", code_point)
        bdf_encodings[code_point] = len(glyph_names)
        glyph_names.append(f'U+{code_point:04X}')
        metric = PcfMetric(
            left_side_bearing=-glyph.horizontal_origin_x,
            right_side_bearing=glyph.width + glyph.horizontal_origin_x,
            character_width=glyph.advance_width,
            ascent=glyph.height + glyph.horizontal_origin_y,
            descent=-glyph.horizontal_origin_y,
        )
        if min_bounds is None or (metric.left_side_bearing + metric.right_side_bearing) < (min_bounds.left_side_bearing + min_bounds.right_side_bearing):
            min_bounds = metric
        if max_bounds is None or (metric.left_side_bearing + metric.right_side_bearing) > (max_bounds.left_side_bearing + max_bounds.right_side_bearing):
            max_bounds = metric
        metrics.append(metric)
        scalable_widths.append(math.ceil((glyph.advance_width / font_size) * (75 / config.resolution_x) * 1000))
        bitmaps.append(glyph.data)

    font.bdf_encodings = bdf_encodings
    font.glyph_names = glyph_names
    font.metrics = metrics
    font.ink_metrics = metrics
    font.scalable_widths = scalable_widths
    font.bitmaps = bitmaps

    logger.debug("Setup 'Accelerators'")
    accelerators = PcfAccelerators()
    accelerators.ink_inside = True
    accelerators.ink_metrics = True
    accelerators.font_ascent = horizontal_header.ascent
    accelerators.font_descent = -horizontal_header.descent
    accelerators.min_bounds = min_bounds
    accelerators.max_bounds = max_bounds
    accelerators.ink_min_bounds = min_bounds
    accelerators.ink_max_bounds = max_bounds
    font.accelerators = accelerators
    font.bdf_accelerators = accelerators

    logger.debug("Setup 'Properties'")
    properties = PcfProperties()
    properties.foundry = meta_info.manufacturer
    properties.family_name = meta_info.family_name
    properties.weight_name = meta_info.style_name
    properties.slant = 'R'
    properties.setwidth_name = 'Normal'
    if meta_info.serif_mode == SerifMode.SERIF:
        properties.add_style_name = 'Serif'
    elif meta_info.serif_mode == SerifMode.SANS_SERIF:
        properties.add_style_name = 'Sans Serif'
    else:
        properties.add_style_name = meta_info.serif_mode
    properties.pixel_size = font_size
    properties.point_size = font_size * 10
    properties.resolution_x = config.resolution_x
    properties.resolution_y = config.resolution_y
    if meta_info.width_mode == WidthMode.MONOSPACED:
        properties.spacing = 'M'
    elif meta_info.width_mode == WidthMode.DUOSPACED:
        properties.spacing = 'D'
    elif meta_info.width_mode == WidthMode.PROPORTIONAL:
        properties.spacing = 'P'
    else:
        properties.spacing = meta_info.width_mode
    properties.average_width = round(sum([metric.character_width * 10 for metric in font.metrics]) / len(font.metrics))
    properties.charset_registry = 'ISO10646'
    properties.charset_encoding = '1'
    properties.generate_xlfd()
    properties.x_height = os2_config.x_height
    properties.cap_height = os2_config.cap_height
    properties.font_version = meta_info.version
    properties.copyright = meta_info.copyright_info
    properties['LICENSE'] = meta_info.license_info
    font.properties = properties

    logger.debug("Create 'PcfFont' finished")
    return font
