import logging
import os
import tomllib

import png

from examples import glyphs_dir, outputs_dir
from pixel_font_builder import FontBuilder, Glyph, StyleName, SerifMode, WidthMode, opentype

logging.basicConfig(level=logging.DEBUG)


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


def _get_glyph_name(code_point: int) -> str:
    return f'uni{code_point:04X}'


def _load_glyph_data_from_png(file_path: str) -> tuple[list[list[int]], int, int]:
    width, height, bitmap, _ = png.Reader(filename=file_path).read()
    data = []
    for bitmap_row in bitmap:
        data_row = []
        for x in range(0, width * 4, 4):
            alpha = bitmap_row[x + 3]
            if alpha > 127:
                data_row.append(1)
            else:
                data_row.append(0)
        data.append(data_row)
    return data, width, height


def _save_glyph_data_to_png(data: list[list[int]], file_path: str):
    bitmap = []
    for data_row in data:
        bitmap_row = []
        for x in data_row:
            bitmap_row.append(0)
            bitmap_row.append(0)
            bitmap_row.append(0)
            if x == 0:
                bitmap_row.append(0)
            else:
                bitmap_row.append(255)
        bitmap.append(bitmap_row)
    png.from_array(bitmap, 'RGBA').save(file_path)


def _format_glyph_files(font_config: FontConfig):
    for glyph_file_dir, _, glyph_file_names in os.walk(font_config.glyphs_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            glyph_data = _load_glyph_data_from_png(glyph_file_path)[0]
            _save_glyph_data_to_png(glyph_data, glyph_file_path)


def _collect_glyph_files(font_config: FontConfig) -> tuple[dict[int, str], dict[str, str]]:
    character_mapping = {}
    glyph_file_paths = {}
    for glyph_file_dir, _, glyph_file_names in os.walk(font_config.glyphs_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            if glyph_file_name == 'notdef.png':
                glyph_file_paths['.notdef'] = glyph_file_path
            else:
                code_point = int(glyph_file_name.removesuffix('.png'), 16)
                glyph_name = _get_glyph_name(code_point)
                character_mapping[code_point] = glyph_name
                glyph_file_paths[glyph_name] = glyph_file_path
    return character_mapping, glyph_file_paths


def _create_builder(
        font_config: FontConfig,
        character_mapping: dict[int, str],
        glyph_file_paths: dict[str, str],
) -> FontBuilder:
    builder = FontBuilder(
        font_config.size,
        font_config.ascent,
        font_config.descent,
        font_config.x_height,
        font_config.cap_height,
    )

    builder.character_mapping.update(character_mapping)
    for code_point in range(ord('A'), ord('Z') + 1):
        fallback_code_point = code_point + ord('Ａ') - ord('A')
        builder.character_mapping[fallback_code_point] = _get_glyph_name(code_point)
    for code_point in range(ord('a'), ord('z') + 1):
        fallback_code_point = code_point + ord('ａ') - ord('a')
        builder.character_mapping[fallback_code_point] = _get_glyph_name(code_point)
    for code_point in range(ord('0'), ord('9') + 1):
        fallback_code_point = code_point + ord('０') - ord('0')
        builder.character_mapping[fallback_code_point] = _get_glyph_name(code_point)

    for glyph_name, glyph_file_path in glyph_file_paths.items():
        glyph_data, glyph_width, glyph_height = _load_glyph_data_from_png(glyph_file_path)
        offset_y = round((glyph_height - font_config.size) / 2 + font_config.box_origin_y) - glyph_height
        builder.add_glyph(Glyph(
            name=glyph_name,
            advance_width=glyph_width,
            offset=(0, offset_y),
            data=glyph_data,
        ))

    builder.meta_infos.version = '1.0.0'
    builder.meta_infos.family_name = 'Cute Pixel'
    builder.meta_infos.style_name = StyleName.REGULAR
    builder.meta_infos.serif_mode = SerifMode.SANS_SERIF
    builder.meta_infos.width_mode = WidthMode.PROPORTIONAL
    builder.meta_infos.manufacturer = 'TakWolf Studio'
    builder.meta_infos.designer = 'TakWolf'
    builder.meta_infos.description = 'A demo pixel font.'
    builder.meta_infos.copyright_info = 'Copyright (c) TakWolf'
    builder.meta_infos.license_info = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
    builder.meta_infos.vendor_url = 'https://github.com/TakWolf/pixel-font-builder'
    builder.meta_infos.designer_url = 'https://takwolf.com'
    builder.meta_infos.license_url = 'https://scripts.sil.org/OFL'

    return builder


def main():
    font_config = FontConfig(glyphs_dir)
    _format_glyph_files(font_config)
    character_mapping, glyph_file_paths = _collect_glyph_files(font_config)
    builder = _create_builder(font_config, character_mapping, glyph_file_paths)
    builder.save_otf(os.path.join(outputs_dir, 'cute.otf'))
    builder.save_otf(os.path.join(outputs_dir, 'cute.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_ttf(os.path.join(outputs_dir, 'cute.ttf'))
    builder.save_bdf(os.path.join(outputs_dir, 'cute.bdf'))


if __name__ == '__main__':
    main()
