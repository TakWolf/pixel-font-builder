from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path

import pytest

from pixel_font_builder import FontBuilder, FontCollectionBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, Glyph


def _load_bitmap(file_path: Path) -> tuple[int, int, list[list[int]]]:
    width = 0
    height = 0
    bitmap = []
    with file_path.open('r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            line = line.strip().replace('##', '#').replace('..', '.')
            bitmap.append([1 if c == '#' else 0 for c in line])

            if i == 0:
                width = len(line)
            else:
                assert width == len(line)
            height += 1
    return width, height, bitmap


class GlyphInfo:
    @staticmethod
    def load(file_path: Path) -> GlyphInfo:
        hex_name = file_path.stem.strip()
        code_point = -1 if hex_name == 'notdef' else int(hex_name, 16)
        width, height, bitmap = _load_bitmap(file_path)
        return GlyphInfo(code_point, width, height, bitmap)

    code_point: int
    width: int
    height: int
    bitmap: list[list[int]]

    def __init__(
            self,
            code_point: int,
            width: int,
            height: int,
            bitmap: list[list[int]],
    ) -> None:
        self.code_point = code_point
        self.width = width
        self.height = height
        self.bitmap = bitmap


def _get_glyph_name(code_point: int) -> str:
    return '.notdef' if code_point == -1 else f'u{code_point:04X}'


def _collect_glyph_infos(glyphs_dir: Path) -> tuple[list[GlyphInfo], dict[int, str]]:
    glyph_infos = []
    character_mapping = {}

    for file_path in glyphs_dir.iterdir():
        if file_path.suffix != '.txt':
            continue

        glyph_info = GlyphInfo.load(file_path)
        glyph_infos.append(glyph_info)

        if glyph_info.code_point != -1:
            character_mapping[glyph_info.code_point] = _get_glyph_name(glyph_info.code_point)

    glyph_infos.sort(key=lambda x: x.code_point)
    return glyph_infos, character_mapping


def _build_kerning_values() -> dict[tuple[str, str], int]:
    kerning_values = {}

    for left_letter in 'FTVY':
        for right_letter in 'acdefgjmnopqrstuvwxyz':
            kerning_values[(_get_glyph_name(ord(left_letter)), _get_glyph_name(ord(right_letter)))] = -1

    for left_letter in 'W':
        for right_letter in 'acdegoqs':
            kerning_values[(_get_glyph_name(ord(left_letter)), _get_glyph_name(ord(right_letter)))] = -1

    for left_letter, right_letter in (('A', 'T'), ('A', 'V'), ('A', 'W'), ('A', 'Y'), ('T', 'A'), ('V', 'A'), ('W', 'A'), ('Y', 'A')):
        kerning_values[(_get_glyph_name(ord(left_letter)), _get_glyph_name(ord(right_letter)))] = -1

    return kerning_values


@pytest.fixture(scope='session')
def demo_builder(assets_dir: Path) -> FontBuilder:
    glyph_infos, character_mapping = _collect_glyph_infos(assets_dir.joinpath('glyphs'))
    kerning_values = _build_kerning_values()

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
    builder.meta_info.family_name = 'Demo'
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

    for glyph_info in glyph_infos:
        horizontal_offset_x = 0
        horizontal_offset_y = (builder.font_metric.horizontal_layout.ascent + builder.font_metric.horizontal_layout.descent - glyph_info.height) // 2
        vertical_offset_x = -math.ceil(glyph_info.width / 2)
        vertical_offset_y = (builder.font_metric.font_size - glyph_info.height) // 2
        builder.glyphs.append(Glyph(
            name=_get_glyph_name(glyph_info.code_point),
            horizontal_offset=(horizontal_offset_x, horizontal_offset_y),
            advance_width=glyph_info.width,
            vertical_offset=(vertical_offset_x, vertical_offset_y),
            advance_height=builder.font_metric.font_size,
            bitmap=glyph_info.bitmap,
        ))

    builder.character_mapping.update(character_mapping)
    builder.kerning_values.update(kerning_values)

    return builder


@pytest.fixture(scope='session')
def demo_collection_builder(demo_builder: FontBuilder) -> FontCollectionBuilder:
    collection_builder = FontCollectionBuilder()
    for index in range(100):
        builder = demo_builder.copy()
        builder.meta_info = builder.meta_info.copy()
        builder.meta_info.family_name = f'Demo {index}'
        collection_builder.append(builder)
    return collection_builder
