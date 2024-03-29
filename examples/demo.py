import datetime
import math
import os
import shutil

import png

from examples import glyphs_dir, build_dir
from pixel_font_builder import FontBuilder, FontCollectionBuilder, StyleName, SerifMode, WidthMode, Glyph, opentype


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


class GlyphFile:
    @staticmethod
    def load(file_path: str) -> 'GlyphFile':
        hex_name = os.path.basename(file_path).removesuffix('.png')
        if hex_name == 'notdef':
            code_point = -1
        else:
            code_point = int(hex_name, 16)
        return GlyphFile(file_path, code_point)

    def __init__(self, file_path: str, code_point: int):
        self.file_path = file_path
        self.code_point = code_point
        self.glyph_data, self.glyph_width, self.glyph_height = _load_glyph_data_from_png(file_path)

    @property
    def glyph_name(self) -> str:
        if self.code_point == -1:
            return '.notdef'
        else:
            return f'uni{self.code_point:04X}'

    def save(self):
        _save_glyph_data_to_png(self.glyph_data, self.file_path)


def _collect_glyph_files(root_dir: str) -> tuple[dict[int, str], list[GlyphFile]]:
    registry = {}
    for file_dir, _, file_names in os.walk(root_dir):
        for file_name in file_names:
            if not file_name.endswith('.png'):
                continue
            file_path = os.path.join(file_dir, file_name)
            glyph_file = GlyphFile.load(file_path)
            registry[glyph_file.code_point] = glyph_file

    character_mapping = {}
    glyph_files = []
    for glyph_file in registry.values():
        if glyph_file.code_point != -1:
            character_mapping[glyph_file.code_point] = glyph_file.glyph_name
        glyph_files.append(glyph_file)
    glyph_files.sort(key=lambda x: x.code_point)

    for code_point in range(ord('A'), ord('Z') + 1):
        fallback_code_point = code_point + ord('Ａ') - ord('A')
        character_mapping[fallback_code_point] = character_mapping[code_point]
    for code_point in range(ord('a'), ord('z') + 1):
        fallback_code_point = code_point + ord('ａ') - ord('a')
        character_mapping[fallback_code_point] = character_mapping[code_point]
    for code_point in range(ord('0'), ord('9') + 1):
        fallback_code_point = code_point + ord('０') - ord('0')
        character_mapping[fallback_code_point] = character_mapping[code_point]

    return character_mapping, glyph_files


def _create_builder(
        glyph_pool: dict[str, Glyph],
        character_mapping: dict[int, str],
        glyph_files: list[GlyphFile],
        name_num: int = None,
) -> FontBuilder:
    builder = FontBuilder(11)

    time = datetime.datetime.fromisoformat('2024-01-01T00:00:00Z')
    builder.created_time = time
    builder.modified_time = time

    builder.meta_info.version = '1.0.0'
    builder.meta_info.family_name = 'Demo Pixel'
    if name_num is not None:
        builder.opentype_config.cff_family_name = builder.meta_info.family_name
        builder.meta_info.family_name += f' {name_num}'
    builder.meta_info.style_name = StyleName.REGULAR
    builder.meta_info.serif_mode = SerifMode.SANS_SERIF
    builder.meta_info.width_mode = WidthMode.PROPORTIONAL
    builder.meta_info.manufacturer = 'Pixel Font Studio'
    builder.meta_info.designer = 'TakWolf'
    builder.meta_info.description = 'A demo pixel font.'
    builder.meta_info.copyright_info = 'Copyright (c) TakWolf'
    builder.meta_info.license_info = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
    builder.meta_info.vendor_url = 'https://github.com/TakWolf/pixel-font-builder'
    builder.meta_info.designer_url = 'https://takwolf.com'
    builder.meta_info.license_url = 'https://openfontlicense.org'
    builder.meta_info.sample_text = 'Hello World!'

    builder.horizontal_header.ascent = 11
    builder.horizontal_header.descent = -4

    builder.vertical_header.ascent = 11
    builder.vertical_header.descent = -4

    builder.os2_config.x_height = 5
    builder.os2_config.cap_height = 7

    builder.character_mapping.update(character_mapping)

    for glyph_file in glyph_files:
        if glyph_file.file_path in glyph_pool:
            glyph = glyph_pool[glyph_file.file_path]
        else:
            horizontal_origin_y = math.floor((builder.horizontal_header.ascent + builder.horizontal_header.descent - glyph_file.glyph_height) / 2)
            vertical_origin_y = (glyph_file.glyph_height - builder.size) // 2
            glyph = Glyph(
                name=glyph_file.glyph_name,
                advance_width=glyph_file.glyph_width,
                advance_height=builder.size,
                horizontal_origin=(0, horizontal_origin_y),
                vertical_origin_y=vertical_origin_y,
                data=glyph_file.glyph_data,
            )
            glyph_pool[glyph_file.file_path] = glyph
        builder.glyphs.append(glyph)

    return builder


def main():
    outputs_dir = os.path.join(build_dir, 'demo')
    if os.path.exists(outputs_dir):
        shutil.rmtree(outputs_dir)
    os.makedirs(outputs_dir)

    character_mapping, glyph_files = _collect_glyph_files(glyphs_dir)
    for glyph_file in glyph_files:
        glyph_file.save()
    glyph_pool = {}

    builder = _create_builder(glyph_pool, character_mapping, glyph_files)
    builder.save_otf(os.path.join(outputs_dir, 'demo.otf'))
    builder.save_otf(os.path.join(outputs_dir, 'demo.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_ttf(os.path.join(outputs_dir, 'demo.ttf'))
    builder.save_bdf(os.path.join(outputs_dir, 'demo.bdf'))

    collection_builder = FontCollectionBuilder()
    for index in range(100):
        builder = _create_builder(glyph_pool, character_mapping, glyph_files, index)
        collection_builder.font_builders.append(builder)
    collection_builder.save_otc(os.path.join(outputs_dir, 'demo.otc'))
    collection_builder.save_ttc(os.path.join(outputs_dir, 'demo.ttc'))


if __name__ == '__main__':
    main()
