import logging
import os
import tomllib

from examples.services.design_service import DesignContext
from pixel_font_builder import FontBuilder, Glyph, MetaInfos, OpenTypeConfigs, BdfConfigs

logger = logging.getLogger('font-service')


class FontConfig:
    def __init__(self, glyphs_dir: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
        self.glyphs_dir = glyphs_dir

        config_file_path = os.path.join(glyphs_dir, 'config.toml')
        with open(config_file_path, 'rb') as file:
            config_data = tomllib.load(file)['font']

        self.size = config_data['size']
        self.line_height = config_data['line_height']
        self.box_origin_y = config_data['box_origin_y']
        self.ascent = round((self.line_height - self.size) / 2 + self.box_origin_y)
        self.descent = self.ascent - self.line_height
        self.x_height = config_data['x_height']
        self.cap_height = config_data['cap_height']

    def calculate_offset(self, glyph_height: int) -> tuple[int, int]:
        y = round((glyph_height - self.size) / 2 + self.box_origin_y) - glyph_height
        return 0, y


def create_font_builder(font_config: FontConfig, design_context: DesignContext) -> FontBuilder:
    font_builder = FontBuilder(
        font_config.size,
        font_config.ascent,
        font_config.descent,
        font_config.x_height,
        font_config.cap_height,
    )

    character_mapping = {}
    glyphs = []
    # .notdef glyph
    glyph_data, glyph_width, glyph_height = design_context.get_glyph_data('.notdef')
    offset = font_config.calculate_offset(glyph_height)
    glyphs.append(Glyph(
        name='.notdef',
        advance_width=glyph_width,
        offset=offset,
        data=glyph_data,
    ))
    # normal glyphs
    for c in design_context.alphabet:
        code_point = ord(c)
        glyph_name = f'uni{code_point:04X}'
        glyph_data, glyph_width, glyph_height = design_context.get_glyph_data(code_point)
        offset = font_config.calculate_offset(glyph_height)
        glyph = Glyph(
            name=glyph_name,
            advance_width=glyph_width,
            offset=offset,
            data=glyph_data,
        )
        character_mapping[code_point] = glyph_name
        glyphs.append(glyph)
    font_builder.character_mapping = character_mapping
    font_builder.glyphs = glyphs
    # fallback fullwidth
    for code_point in range(ord('A'), ord('Z') + 1):
        fallback_code_point = code_point + ord('Ａ') - ord('A')
        glyph_name = f'uni{code_point:04X}'
        character_mapping[fallback_code_point] = glyph_name
    for code_point in range(ord('a'), ord('z') + 1):
        fallback_code_point = code_point + ord('ａ') - ord('a')
        glyph_name = f'uni{code_point:04X}'
        character_mapping[fallback_code_point] = glyph_name
    for code_point in range(ord('0'), ord('9') + 1):
        fallback_code_point = code_point + ord('０') - ord('0')
        glyph_name = f'uni{code_point:04X}'
        character_mapping[fallback_code_point] = glyph_name

    font_builder.meta_infos = MetaInfos(
        family_name='Demo Pixel',
        version='1.0.0',
        description='A demo pixel font.',
        copyright_info='Copyright (c) TakWolf (https://takwolf.com).',
        license_description='This Font Software is licensed under the SIL Open Font License, Version 1.1.',
        license_url='https://scripts.sil.org/OFL',
        manufacturer='TakWolf',
        designer='TakWolf',
        designer_url='https://takwolf.com',
        vendor_url='https://github.com/TakWolf/pixel-font-builder',
    )

    font_builder.opentype_configs = OpenTypeConfigs()

    font_builder.bdf_configs = BdfConfigs()

    return font_builder
