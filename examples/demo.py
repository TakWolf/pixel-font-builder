from __future__ import annotations

import math
import shutil
from datetime import datetime
from pathlib import Path

from examples import glyphs_dir, build_dir
from pixel_font_builder import FontBuilder, FontCollectionBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, Glyph, opentype


def _load_bitmap(file_path: Path) -> tuple[list[list[int]], int, int]:
    bitmap = []
    width = 0
    height = 0
    with file_path.open('r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            line = line.strip().replace('##', '#').replace('..', '.')
            bitmap.append([1 if c == '#' else 0 for c in line])

            if i == 0:
                width = len(line)
            else:
                assert width == len(line)
            height += 1
    return bitmap, width, height


class GlyphFile:
    @staticmethod
    def load(file_path: Path) -> GlyphFile:
        hex_name = file_path.stem.strip()
        code_point = -1 if hex_name == 'notdef' else int(hex_name, 16)
        return GlyphFile(file_path, code_point)

    file_path: Path
    code_point: int
    bitmap: list[list[int]]
    width: int
    height: int

    def __init__(self, file_path: Path, code_point: int):
        self.file_path = file_path
        self.code_point = code_point
        self.bitmap, self.width, self.height = _load_bitmap(file_path)


def _get_glyph_name(code_point: int) -> str:
    return '.notdef' if code_point == -1 else f'u{code_point:04X}'


def _collect_glyph_files() -> tuple[list[GlyphFile], dict[int, str]]:
    glyph_files = []
    character_mapping = {}
    for file_path in glyphs_dir.iterdir():
        if file_path.suffix != '.txt':
            continue

        glyph_file = GlyphFile.load(file_path)
        glyph_files.append(glyph_file)
        if glyph_file.code_point != -1:
            character_mapping[glyph_file.code_point] = _get_glyph_name(glyph_file.code_point)
    glyph_files.sort(key=lambda x: x.code_point)
    return glyph_files, character_mapping


def _build_kerning_pairs() -> dict[tuple[str, str], int]:
    kerning_pairs = {}

    for left_letter in 'FTVY':
        for right_letter in 'acdefgjmnopqrstuvwxyz':
            kerning_pairs[(_get_glyph_name(ord(left_letter)), _get_glyph_name(ord(right_letter)))] = -1

    for left_letter in 'W':
        for right_letter in 'acdegoqs':
            kerning_pairs[(_get_glyph_name(ord(left_letter)), _get_glyph_name(ord(right_letter)))] = -1

    for left_letter, right_letter in (('A', 'T'), ('A', 'V'), ('A', 'W'), ('A', 'Y'), ('T', 'A'), ('V', 'A'), ('W', 'A'), ('Y', 'A')):
        kerning_pairs[(_get_glyph_name(ord(left_letter)), _get_glyph_name(ord(right_letter)))] = -1

    return kerning_pairs


def _create_builder(
        glyph_files: list[GlyphFile],
        character_mapping: dict[int, str],
        kerning_pairs: dict[tuple[str, str], int],
        name_num: int = 0,
) -> FontBuilder:
    builder = FontBuilder()
    builder.font_metric.font_size = 12
    builder.font_metric.horizontal_layout.ascent = 13
    builder.font_metric.horizontal_layout.descent = -3
    builder.font_metric.vertical_layout.ascent = 8
    builder.font_metric.vertical_layout.descent = -8
    builder.font_metric.x_height = 6
    builder.font_metric.cap_height = 9
    builder.font_metric.underline_position = -1
    builder.font_metric.underline_thickness = 1
    builder.font_metric.strikeout_position = 5
    builder.font_metric.strikeout_thickness = 1

    builder.meta_info.version = '1.0.0'
    builder.meta_info.created_time = datetime.fromisoformat('2024-01-01T00:00:00Z')
    builder.meta_info.modified_time = builder.meta_info.created_time
    builder.meta_info.family_name = f'Demo {name_num}'
    builder.meta_info.weight_name = WeightName.REGULAR
    builder.meta_info.serif_style = SerifStyle.SANS_SERIF
    builder.meta_info.slant_style = SlantStyle.NORMAL
    builder.meta_info.width_style = WidthStyle.PROPORTIONAL
    builder.meta_info.manufacturer = 'Pixel Font Studio'
    builder.meta_info.designer = 'TakWolf'
    builder.meta_info.description = 'A demo font'
    builder.meta_info.copyright_info = 'Copyright (c) TakWolf'
    builder.meta_info.license_info = 'This Font Software is licensed under the SIL Open Font License, Version 1.1'
    builder.meta_info.vendor_url = 'https://github.com/TakWolf/pixel-font-builder'
    builder.meta_info.designer_url = 'https://takwolf.com'
    builder.meta_info.license_url = 'https://openfontlicense.org'

    for glyph_file in glyph_files:
        horizontal_offset_x = 0
        horizontal_offset_y = (builder.font_metric.horizontal_layout.ascent + builder.font_metric.horizontal_layout.descent - glyph_file.height) // 2
        vertical_offset_x = -math.ceil(glyph_file.width / 2)
        vertical_offset_y = (builder.font_metric.font_size - glyph_file.height) // 2
        builder.glyphs.append(Glyph(
            name=_get_glyph_name(glyph_file.code_point),
            horizontal_offset=(horizontal_offset_x, horizontal_offset_y),
            advance_width=glyph_file.width,
            vertical_offset=(vertical_offset_x, vertical_offset_y),
            advance_height=builder.font_metric.font_size,
            bitmap=glyph_file.bitmap,
        ))

    builder.character_mapping.update(character_mapping)
    builder.kerning_pairs.update(kerning_pairs)

    return builder


def main():
    outputs_dir = build_dir.joinpath('demo')
    if outputs_dir.exists():
        shutil.rmtree(outputs_dir)
    outputs_dir.mkdir(parents=True)

    glyph_files, character_mapping = _collect_glyph_files()
    kerning_pairs = _build_kerning_pairs()

    builder = _create_builder(glyph_files, character_mapping, kerning_pairs)
    builder.save_otf(outputs_dir.joinpath('demo.otf'))
    builder.save_otf(outputs_dir.joinpath('demo.otf.woff'), flavor=opentype.Flavor.WOFF)
    builder.save_otf(outputs_dir.joinpath('demo.otf.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_ttf(outputs_dir.joinpath('demo.ttf'))
    builder.save_ttf(outputs_dir.joinpath('demo.ttf.woff'), flavor=opentype.Flavor.WOFF)
    builder.save_ttf(outputs_dir.joinpath('demo.ttf.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_bdf(outputs_dir.joinpath('demo.bdf'))
    builder.save_pcf(outputs_dir.joinpath('demo.pcf'))

    collection_builder = FontCollectionBuilder()
    for index in range(100):
        builder = _create_builder(glyph_files, character_mapping, kerning_pairs, index)
        collection_builder.append(builder)
    collection_builder.save_otc(outputs_dir.joinpath('demo.otc'))
    collection_builder.save_ttc(outputs_dir.joinpath('demo.ttc'))


if __name__ == '__main__':
    main()
