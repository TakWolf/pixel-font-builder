import os
import tomllib

from examples.services.design_service import DesignContext
from pixel_font_builder import FontBuilder, Glyph, StyleName, SerifMode, WidthMode


class FontConfig:
    def __init__(self, glyphs_dir: str):
        self.glyphs_dir = glyphs_dir

        config_file_path = os.path.join(glyphs_dir, 'config.toml')
        with open(config_file_path, 'rb') as file:
            config_data = tomllib.load(file)['font']

        self.size: int = config_data['size']
        self.line_height: int = config_data['line_height']
        self.box_origin_y: int = config_data['box_origin_y']
        self.ascent: int = round((self.line_height - self.size) / 2 + self.box_origin_y)
        self.descent: int = self.ascent - self.line_height
        self.x_height: int = config_data['x_height']
        self.cap_height: int = config_data['cap_height']


def _get_glyph_name(code_point: int | str) -> str:
    if isinstance(code_point, int):
        return f'uni{code_point:04X}'
    else:
        return code_point


def _create_glyph(font_config: FontConfig, design_context: DesignContext, code_point: int | str) -> Glyph:
    glyph_data, glyph_width, glyph_height = design_context.get_glyph_data(code_point)
    offset_y = round((glyph_height - font_config.size) / 2 + font_config.box_origin_y) - glyph_height
    return Glyph(
        name=_get_glyph_name(code_point),
        advance_width=glyph_width,
        offset=(0, offset_y),
        data=glyph_data,
    )


def create_font_builder(font_config: FontConfig, design_context: DesignContext) -> FontBuilder:
    font_builder = FontBuilder(
        font_config.size,
        font_config.ascent,
        font_config.descent,
        font_config.x_height,
        font_config.cap_height,
    )

    font_builder.add_glyph(_create_glyph(font_config, design_context, '.notdef'))
    for c in design_context.alphabet:
        code_point = ord(c)
        font_builder.character_mapping[code_point] = _get_glyph_name(code_point)
        font_builder.add_glyph(_create_glyph(font_config, design_context, code_point))
    for code_point in range(ord('A'), ord('Z') + 1):
        fallback_code_point = code_point + ord('Ａ') - ord('A')
        font_builder.character_mapping[fallback_code_point] = _get_glyph_name(code_point)
    for code_point in range(ord('a'), ord('z') + 1):
        fallback_code_point = code_point + ord('ａ') - ord('a')
        font_builder.character_mapping[fallback_code_point] = _get_glyph_name(code_point)
    for code_point in range(ord('0'), ord('9') + 1):
        fallback_code_point = code_point + ord('０') - ord('0')
        font_builder.character_mapping[fallback_code_point] = _get_glyph_name(code_point)

    font_builder.meta_infos.version = '1.0.0'
    font_builder.meta_infos.family_name = 'Demo Pixel'
    font_builder.meta_infos.style_name = StyleName.REGULAR
    font_builder.meta_infos.serif_mode = SerifMode.SANS_SERIF
    font_builder.meta_infos.width_mode = WidthMode.PROPORTIONAL
    font_builder.meta_infos.manufacturer = 'TakWolf Studio'
    font_builder.meta_infos.designer = 'TakWolf'
    font_builder.meta_infos.description = 'A demo pixel font.'
    font_builder.meta_infos.copyright_info = 'Copyright (c) TakWolf'
    font_builder.meta_infos.license_info = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
    font_builder.meta_infos.vendor_url = 'https://github.com/TakWolf/pixel-font-builder'
    font_builder.meta_infos.designer_url = 'https://takwolf.com'
    font_builder.meta_infos.license_url = 'https://scripts.sil.org/OFL'

    return font_builder
