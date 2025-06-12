from __future__ import annotations

import math
import shutil
from datetime import datetime
from pathlib import Path

import png

from examples import glyphs_dir, build_dir
from pixel_font_builder import FontBuilder, FontCollectionBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, Glyph, opentype


def _load_bitmap_from_png(file_path: Path) -> tuple[list[list[int]], int, int]:
    width, height, pixels, _ = png.Reader(filename=file_path).read()
    bitmap = []
    for pixels_row in pixels:
        bitmap_row = []
        for i in range(0, width * 4, 4):
            alpha = pixels_row[i + 3]
            bitmap_row.append(1 if alpha > 127 else 0)
        bitmap.append(bitmap_row)
    return bitmap, width, height


def _save_bitmap_to_png(bitmap: list[list[int]], file_path: Path):
    pixels = []
    for bitmap_row in bitmap:
        pixels_row = []
        for color in bitmap_row:
            pixels_row.append(0)
            pixels_row.append(0)
            pixels_row.append(0)
            pixels_row.append(0 if color == 0 else 255)
        pixels.append(pixels_row)
    png.from_array(pixels, 'RGBA').save(file_path)


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
        self.bitmap, self.width, self.height = _load_bitmap_from_png(file_path)

    def save(self):
        _save_bitmap_to_png(self.bitmap, self.file_path)


def _get_glyph_name(code_point: int) -> str:
    return '.notdef' if code_point == -1 else f'u{code_point:04X}'


def _collect_glyph_files() -> tuple[dict[int, str], list[GlyphFile]]:
    character_mapping = {}
    glyph_files = []
    for file_path in glyphs_dir.iterdir():
        if file_path.suffix != '.png':
            continue
        glyph_file = GlyphFile.load(file_path)
        if glyph_file.code_point != -1:
            character_mapping[glyph_file.code_point] = _get_glyph_name(glyph_file.code_point)
        glyph_files.append(glyph_file)
    glyph_files.sort(key=lambda x: x.code_point)
    return character_mapping, glyph_files


def _build_kerning_pairs() -> dict[tuple[str, str], int]:
    kerning_pairs = {}
    for left_letter in 'FT':
        for right_letter in 'acdegmnopqrsuvwxyz':
            kerning_pairs[(_get_glyph_name(ord(left_letter)), _get_glyph_name(ord(right_letter)))] = -1
    return kerning_pairs


def _create_builder(
        character_mapping: dict[int, str],
        glyph_files: list[GlyphFile],
        kerning_pairs: dict[tuple[str, str], int],
        name_num: int = 0,
) -> FontBuilder:
    builder = FontBuilder()
    builder.font_metric.font_size = 11
    builder.font_metric.horizontal_layout.ascent = 11
    builder.font_metric.horizontal_layout.descent = -4
    builder.font_metric.vertical_layout.ascent = 8
    builder.font_metric.vertical_layout.descent = -7
    builder.font_metric.x_height = 5
    builder.font_metric.cap_height = 7
    builder.font_metric.underline_position = -3
    builder.font_metric.underline_thickness = 1
    builder.font_metric.strikeout_position = 4
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

    builder.character_mapping.update(character_mapping)

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

    builder.kerning_pairs.update(kerning_pairs)

    return builder


def main():
    outputs_dir = build_dir.joinpath('demo')
    if outputs_dir.exists():
        shutil.rmtree(outputs_dir)
    outputs_dir.mkdir(parents=True)

    character_mapping, glyph_files = _collect_glyph_files()
    for glyph_file in glyph_files:
        glyph_file.save()
    kerning_pairs = _build_kerning_pairs()

    builder = _create_builder(character_mapping, glyph_files, kerning_pairs)
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
        builder = _create_builder(character_mapping, glyph_files, kerning_pairs, index)
        collection_builder.append(builder)
    collection_builder.save_otc(outputs_dir.joinpath('demo.otc'))
    collection_builder.save_ttc(outputs_dir.joinpath('demo.ttc'))


if __name__ == '__main__':
    main()
