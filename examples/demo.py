import logging
import math
import os
import tomllib

import png

from examples import glyphs_dir, outputs_dir
from pixel_font_builder import FontBuilder, FontCollectionBuilder, Glyph, opentype

logging.basicConfig(level=logging.DEBUG)


class FontConfig:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

        config_file_path = os.path.join(root_dir, 'config.toml')
        with open(config_file_path, 'rb') as file:
            config_data: dict = tomllib.load(file)['font']

        self.size: int = config_data['size']
        self.ascent: int = config_data['ascent']
        self.descent: int = config_data['descent']
        self.x_height: int = config_data['x_height']
        self.cap_height: int = config_data['cap_height']

        self.version: str = config_data['version']
        self.family_name: str = config_data['family_name']
        self.style_name: str = config_data['style_name']
        self.serif_mode: str = config_data['serif_mode']
        self.width_mode: str = config_data['width_mode']
        self.manufacturer: str = config_data['manufacturer']
        self.designer: str = config_data['designer']
        self.description: str = config_data['description']
        self.copyright_info: str = config_data['copyright_info']
        self.license_info: str = config_data['license_info']
        self.vendor_url: str = config_data['vendor_url']
        self.designer_url: str = config_data['designer_url']
        self.license_url: str = config_data['license_url']
        self.sample_text: str = config_data['sample_text']


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
    for glyph_file_dir, _, glyph_file_names in os.walk(font_config.root_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            glyph_data = _load_glyph_data_from_png(glyph_file_path)[0]
            _save_glyph_data_to_png(glyph_data, glyph_file_path)


def _collect_glyph_files(font_config: FontConfig) -> tuple[dict[int, str], dict[str, str]]:
    character_mapping = {}
    glyph_file_paths = {}
    for glyph_file_dir, _, glyph_file_names in os.walk(font_config.root_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            if glyph_file_name == 'notdef.png':
                glyph_file_paths['.notdef'] = glyph_file_path
            else:
                code_point = int(glyph_file_name.removesuffix('.png'), 16)
                glyph_name = f'uni{code_point:04X}'
                character_mapping[code_point] = glyph_name
                glyph_file_paths[glyph_name] = glyph_file_path
    return character_mapping, glyph_file_paths


def _create_builder(
        font_config: FontConfig,
        glyph_cacher: dict[str, Glyph],
        character_mapping: dict[int, str],
        glyph_file_paths: dict[str, str],
        name_num: int = None,
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
        builder.character_mapping[fallback_code_point] = builder.character_mapping[code_point]
    for code_point in range(ord('a'), ord('z') + 1):
        fallback_code_point = code_point + ord('ａ') - ord('a')
        builder.character_mapping[fallback_code_point] = builder.character_mapping[code_point]
    for code_point in range(ord('0'), ord('9') + 1):
        fallback_code_point = code_point + ord('０') - ord('0')
        builder.character_mapping[fallback_code_point] = builder.character_mapping[code_point]

    for glyph_name, glyph_file_path in glyph_file_paths.items():
        if glyph_file_path in glyph_cacher:
            glyph = glyph_cacher[glyph_file_path]
        else:
            glyph_data, glyph_width, glyph_height = _load_glyph_data_from_png(glyph_file_path)
            offset_y = math.floor((font_config.ascent + font_config.descent - glyph_height) / 2)
            glyph = Glyph(
                name=glyph_name,
                advance_width=glyph_width,
                offset=(0, offset_y),
                data=glyph_data,
            )
            glyph_cacher[glyph_file_path] = glyph
        builder.add_glyph(glyph)

    builder.meta_infos.version = font_config.version
    builder.meta_infos.family_name = font_config.family_name
    if name_num is not None:
        builder.meta_infos.family_name += f' {name_num}'
    builder.meta_infos.style_name = font_config.style_name
    builder.meta_infos.serif_mode = font_config.serif_mode
    builder.meta_infos.width_mode = font_config.width_mode
    builder.meta_infos.manufacturer = font_config.manufacturer
    builder.meta_infos.designer = font_config.designer
    builder.meta_infos.description = font_config.description
    builder.meta_infos.copyright_info = font_config.copyright_info
    builder.meta_infos.license_info = font_config.license_info
    builder.meta_infos.vendor_url = font_config.vendor_url
    builder.meta_infos.designer_url = font_config.designer_url
    builder.meta_infos.license_url = font_config.license_url
    builder.meta_infos.sample_text = font_config.sample_text

    return builder


def main():
    font_config = FontConfig(glyphs_dir)
    _format_glyph_files(font_config)
    character_mapping, glyph_file_paths = _collect_glyph_files(font_config)
    glyph_cacher = {}

    builder = _create_builder(font_config, glyph_cacher, character_mapping, glyph_file_paths)
    builder.save_otf(os.path.join(outputs_dir, 'demo.otf'))
    builder.save_otf(os.path.join(outputs_dir, 'demo.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_ttf(os.path.join(outputs_dir, 'demo.ttf'))
    builder.save_bdf(os.path.join(outputs_dir, 'demo.bdf'))

    collection_builder = FontCollectionBuilder()
    for index in range(100):
        builder = _create_builder(font_config, glyph_cacher, character_mapping, glyph_file_paths, index)
        builder.opentype_configs.cff_family_name = font_config.family_name
        collection_builder.font_builders.append(builder)
    collection_builder.save_otc(os.path.join(outputs_dir, 'demo.otc'))
    collection_builder.save_ttc(os.path.join(outputs_dir, 'demo.ttc'))


if __name__ == '__main__':
    main()
