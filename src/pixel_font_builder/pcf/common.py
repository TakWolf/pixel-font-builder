from __future__ import annotations

import math
import statistics

from pcffont import PcfFontBuilder, PcfGlyph

import pixel_font_builder
from pixel_font_builder.meta import WeightName, SlantStyle, WidthStyle

_DEFAULT_CHAR = 0xFFFE


def create_font_builder(context: pixel_font_builder.FontBuilder) -> PcfFontBuilder:
    config = context.pcf_config
    font_metric = context.font_metric
    meta_info = context.meta_info
    glyph_order, name_to_glyph = context.prepare_glyphs()
    character_mapping = context.character_mapping

    if _DEFAULT_CHAR in character_mapping:
        raise RuntimeError(f'encoding 0x{_DEFAULT_CHAR:04X} is reserved for the PCF default glyph')

    builder = PcfFontBuilder()
    builder.config.font_ascent = font_metric.horizontal_layout.ascent
    builder.config.font_descent = -font_metric.horizontal_layout.descent
    builder.config.default_char = _DEFAULT_CHAR
    builder.config.draw_right_to_left = config.draw_right_to_left
    builder.config.ms_byte_first = config.ms_byte_first
    builder.config.ms_bit_first = config.ms_bit_first
    builder.config.glyph_pad = config.glyph_pad
    builder.config.scan_unit = config.scan_unit

    name_to_encodings = {
        '.notdef': {_DEFAULT_CHAR},
    }
    for code_point, glyph_name in character_mapping.items():
        if code_point > 0xFFFF:
            continue

        if glyph_name in name_to_encodings:
            encodings = name_to_encodings[glyph_name]
        else:
            encodings = set()
            name_to_encodings[glyph_name] = encodings
        encodings.add(code_point)

    for glyph_name in glyph_order:
        if glyph_name not in name_to_encodings:
            continue

        glyph = name_to_glyph[glyph_name]
        encodings = name_to_encodings[glyph_name]

        builder.glyphs.append(PcfGlyph(
            name=glyph.name,
            encodings=encodings,
            scalable_width=math.ceil((glyph.advance_width / font_metric.font_size) * (75 / config.resolution_x) * 1000),
            character_width=glyph.advance_width,
            dimensions=glyph.dimensions,
            offset=glyph.horizontal_offset,
            bitmap=glyph.bitmap,
        ))

    if meta_info.manufacturer is not None:
        builder.properties.foundry = meta_info.manufacturer.replace('-', '_')
    builder.properties.family_name = meta_info.family_name.replace('-', '_')
    builder.properties.weight_name = (meta_info.weight_name or WeightName.REGULAR).value
    match meta_info.slant_style:
        case None | SlantStyle.NORMAL | SlantStyle.ROMAN:
            builder.properties.slant = 'R'
        case SlantStyle.ITALIC:
            builder.properties.slant = 'I'
        case SlantStyle.OBLIQUE:
            builder.properties.slant = 'O'
        case SlantStyle.REVERSE_ITALIC:
            builder.properties.slant = 'RI'
        case SlantStyle.REVERSE_OBLIQUE:
            builder.properties.slant = 'RO'
        case SlantStyle.OTHER:
            builder.properties.slant = 'OT'
    builder.properties.setwidth_name = 'Normal'
    if meta_info.serif_style is not None:
        builder.properties.add_style_name = meta_info.serif_style.value
    builder.properties.pixel_size = font_metric.font_size
    builder.properties.point_size = font_metric.font_size * 10
    builder.properties.resolution_x = config.resolution_x
    builder.properties.resolution_y = config.resolution_y
    match meta_info.width_style:
        case WidthStyle.MONOSPACED:
            builder.properties.spacing = 'M'
        case WidthStyle.DUOSPACED:
            builder.properties.spacing = 'D'
        case WidthStyle.CHARACTER_CELL:
            builder.properties.spacing = 'C'
        case WidthStyle.PROPORTIONAL:
            builder.properties.spacing = 'P'
    builder.properties.average_width = round(statistics.fmean(glyph.character_width * 10 for glyph in builder.glyphs))
    builder.properties.charset_registry = 'ISO10646'
    builder.properties.charset_encoding = '1'
    builder.properties.generate_xlfd()

    if font_metric.x_height != 0:
        builder.properties.x_height = font_metric.x_height
    if font_metric.cap_height != 0:
        builder.properties.cap_height = font_metric.cap_height
    if font_metric.underline_thickness != 0:
        builder.properties.underline_position = font_metric.underline_position
        builder.properties.underline_thickness = font_metric.underline_thickness

    builder.properties.font_version = meta_info.version
    builder.properties.copyright = meta_info.copyright_info
    builder.properties['LICENSE'] = meta_info.license_info

    return builder
