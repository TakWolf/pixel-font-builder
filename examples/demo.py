import logging
import math
import os
import shutil

import png

from examples import glyphs_dir, build_dir
from pixel_font_builder import FontBuilder, FontCollectionBuilder, StyleName, SerifMode, WidthMode, Glyph, opentype

logging.basicConfig(level=logging.DEBUG)


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


class GlyphFileInfo:
    @staticmethod
    def load(file_dir: str, file_name: str) -> 'GlyphFileInfo':
        file_path = os.path.join(file_dir, file_name)
        if file_name == 'notdef.png':
            code_point = -1
        else:
            code_point = int(file_name.removesuffix('.png'), 16)
        return GlyphFileInfo(file_path, code_point)

    def __init__(self, file_path: str, code_point: int):
        self.file_path = file_path
        self.code_point = code_point
        self.glyph_data, self.glyph_width, self.glyph_height = _load_glyph_data_from_png(file_path)

    @property
    def glyph_name(self) -> str:
        if self.code_point == -1:
            glyph_name = '.notdef'
        else:
            glyph_name = f'uni{self.code_point:04X}'
        return glyph_name


def _collect_glyph_files(root_dir: str) -> tuple[dict[int, str], list[GlyphFileInfo]]:
    registry = {}
    for file_dir, _, file_names in os.walk(root_dir):
        for file_name in file_names:
            if not file_name.endswith('.png'):
                continue
            file_info = GlyphFileInfo.load(file_dir, file_name)
            registry[file_info.code_point] = file_info

    sequence = list(registry.keys())
    sequence.sort()

    character_mapping = {}
    file_infos = []
    for code_point in sequence:
        file_info = registry[code_point]
        if code_point != -1:
            character_mapping[code_point] = file_info.glyph_name
        file_infos.append(file_info)

    for code_point in range(ord('A'), ord('Z') + 1):
        fallback_code_point = code_point + ord('Ａ') - ord('A')
        character_mapping[fallback_code_point] = character_mapping[code_point]
    for code_point in range(ord('a'), ord('z') + 1):
        fallback_code_point = code_point + ord('ａ') - ord('a')
        character_mapping[fallback_code_point] = character_mapping[code_point]
    for code_point in range(ord('0'), ord('9') + 1):
        fallback_code_point = code_point + ord('０') - ord('0')
        character_mapping[fallback_code_point] = character_mapping[code_point]

    return character_mapping, file_infos


def _create_builder(
        glyph_cacher: dict[str, Glyph],
        character_mapping: dict[int, str],
        file_infos: list[GlyphFileInfo],
        name_num: int = None,
) -> FontBuilder:
    builder = FontBuilder(11)

    builder.meta_infos.version = "1.0.0"
    builder.meta_infos.family_name = "Demo Pixel"
    if name_num is not None:
        builder.opentype_configs.cff_family_name = builder.meta_infos.family_name
        builder.meta_infos.family_name += f' {name_num}'
    builder.meta_infos.style_name = StyleName.REGULAR
    builder.meta_infos.serif_mode = SerifMode.SANS_SERIF
    builder.meta_infos.width_mode = WidthMode.PROPORTIONAL
    builder.meta_infos.manufacturer = "Pixel Font Studio"
    builder.meta_infos.designer = "TakWolf"
    builder.meta_infos.description = "A demo pixel font."
    builder.meta_infos.copyright_info = "Copyright (c) TakWolf"
    builder.meta_infos.license_info = "This Font Software is licensed under the SIL Open Font License, Version 1.1."
    builder.meta_infos.vendor_url = "https://github.com/TakWolf/pixel-font-builder"
    builder.meta_infos.designer_url = "https://takwolf.com"
    builder.meta_infos.license_url = "https://scripts.sil.org/OFL"
    builder.meta_infos.sample_text = "Hello World!"

    builder.horizontal_header.ascent = 11
    builder.horizontal_header.descent = -4

    builder.vertical_header.ascent = 11
    builder.vertical_header.descent = -4

    builder.properties.x_height = 5
    builder.properties.cap_height = 7

    builder.character_mapping.update(character_mapping)

    for file_info in file_infos:
        if file_info.glyph_name in glyph_cacher:
            glyph = glyph_cacher[file_info.glyph_name]
        else:
            horizontal_origin_y = math.floor((builder.horizontal_header.ascent + builder.horizontal_header.descent - file_info.glyph_height) / 2)
            vertical_origin_y = (file_info.glyph_height - builder.size) // 2
            glyph = Glyph(
                name=file_info.glyph_name,
                advance_width=file_info.glyph_width,
                advance_height=builder.size,
                horizontal_origin=(0, horizontal_origin_y),
                vertical_origin_y=vertical_origin_y,
                data=file_info.glyph_data,
            )
            glyph_cacher[file_info.glyph_name] = glyph
        builder.glyphs.append(glyph)

    return builder


def main():
    outputs_dir = os.path.join(build_dir, 'demo')
    if os.path.exists(outputs_dir):
        shutil.rmtree(outputs_dir)
    os.makedirs(outputs_dir)

    character_mapping, file_infos = _collect_glyph_files(glyphs_dir)
    for file_info in file_infos:
        _save_glyph_data_to_png(file_info.glyph_data, file_info.file_path)
    glyph_cacher = {}

    builder = _create_builder(glyph_cacher, character_mapping, file_infos)
    builder.save_otf(os.path.join(outputs_dir, 'demo.otf'))
    builder.save_otf(os.path.join(outputs_dir, 'demo.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_ttf(os.path.join(outputs_dir, 'demo.ttf'))
    builder.save_bdf(os.path.join(outputs_dir, 'demo.bdf'))

    collection_builder = FontCollectionBuilder()
    for index in range(100):
        builder = _create_builder(glyph_cacher, character_mapping, file_infos, index)
        collection_builder.font_builders.append(builder)
    collection_builder.save_otc(os.path.join(outputs_dir, 'demo.otc'))
    collection_builder.save_ttc(os.path.join(outputs_dir, 'demo.ttc'))


if __name__ == '__main__':
    main()
