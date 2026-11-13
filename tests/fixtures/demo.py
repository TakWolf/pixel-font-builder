from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path

import pytest

from pixel_font_builder import FontBuilder, FontCollectionBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, Glyph, MonoRaster, ColorRaster, ColorRgba
from tests.fixtures.png import read_png


def _load_color_bitmap(file_path: Path) -> tuple[int, int, list[list[ColorRgba]]]:
    return read_png(file_path.read_bytes())


def _load_mono_bitmap(file_path: Path) -> tuple[int, int, list[list[int]]]:
    width, height, color_bitmap = _load_color_bitmap(file_path)
    mono_bitmap = [
        [
            int(pixel[3] >= 128)
            for pixel in row
        ]
        for row in color_bitmap
    ]
    return width, height, mono_bitmap


def _collect_glyphs(
        glyphs_dir: Path,
        font_size: int,
        horizontal_ascent: int,
        horizontal_descent: int,
) -> tuple[list[Glyph], dict[int, str]]:
    code_points = set[int]()
    for file_path in glyphs_dir.glob('*.png'):
        if not file_path.is_file():
            continue

        hex_name = file_path.stem.removesuffix('.color')
        code_point = -1 if hex_name == 'notdef' else int(hex_name, 16)
        code_points.add(code_point)

    glyphs = []
    character_mapping = {}
    for code_point in sorted(code_points):
        hex_name = 'notdef' if code_point == -1 else f'{code_point:04X}'
        glyph_name = '.notdef' if code_point == -1 else f'u{hex_name}'
        glyph = Glyph(
            name=glyph_name,
            advance_height=font_size,
        )

        mono_file_path = glyphs_dir.joinpath(f'{hex_name}.png')
        if mono_file_path.is_file():
            width, height, bitmap = _load_mono_bitmap(mono_file_path)

            horizontal_offset_x = 0
            horizontal_offset_y = (horizontal_ascent + horizontal_descent - height) // 2
            vertical_offset_x = -math.ceil(width / 2)
            vertical_offset_y = (font_size - height) // 2

            glyph.advance_width = width
            glyph.mono_raster = MonoRaster(
                horizontal_offset=(horizontal_offset_x, horizontal_offset_y),
                vertical_offset=(vertical_offset_x, vertical_offset_y),
                bitmap=bitmap,
            )

        color_file_path = glyphs_dir.joinpath(f'{hex_name}.color.png')
        if color_file_path.is_file():
            width, height, bitmap = _load_color_bitmap(color_file_path)

            horizontal_offset_x = 0
            horizontal_offset_y = (horizontal_ascent + horizontal_descent - height) // 2
            vertical_offset_x = -math.ceil(width / 2)
            vertical_offset_y = (font_size - height) // 2

            glyph.color_raster = ColorRaster(
                horizontal_offset=(horizontal_offset_x, horizontal_offset_y),
                vertical_offset=(vertical_offset_x, vertical_offset_y),
                bitmap=bitmap,
            )

            if glyph.mono_raster is None:
                glyph.advance_width = width
            else:
                assert width == glyph.mono_raster.width
                assert height == glyph.mono_raster.height

        glyphs.append(glyph)
        if code_point != -1:
            character_mapping[code_point] = glyph_name
    return glyphs, character_mapping


@pytest.fixture(scope='session')
def demo_builder(assets_dir: Path) -> FontBuilder:
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
    builder.meta_info.manufacturer = 'TakWolf'
    builder.meta_info.designer = 'TakWolf'
    builder.meta_info.description = 'A demo font'
    builder.meta_info.copyright_info = 'Copyright (c) TakWolf'
    builder.meta_info.license_info = 'This Font Software is licensed under the SIL Open Font License, Version 1.1'
    builder.meta_info.vendor_url = 'https://github.com/TakWolf/pixel-font-builder'
    builder.meta_info.designer_url = 'https://takwolf.com'
    builder.meta_info.license_url = 'https://openfontlicense.org'

    glyphs, character_mapping = _collect_glyphs(
        assets_dir.joinpath('glyphs'),
        builder.font_metric.font_size,
        builder.font_metric.horizontal_layout.ascent,
        builder.font_metric.horizontal_layout.descent,
    )
    builder.glyphs = glyphs
    builder.character_mapping = character_mapping

    builder.kerning_values = {
        ('u002F', 'u002F'): -1,
        ('u0041', 'u0054'): -1,
        ('u0041', 'u0056'): -1,
        ('u0041', 'u0057'): -1,
        ('u0041', 'u0059'): -1,
        ('u0041', 'u0066'): -1,
        ('u0041', 'u006A'): -1,
        ('u0041', 'u006C'): -1,
        ('u0041', 'u0074'): -1,
        ('u0041', 'u0076'): -1,
        ('u0046', 'u002C'): -1,
        ('u0046', 'u002E'): -1,
        ('u0046', 'u0041'): -1,
        ('u0046', 'u0061'): -1,
        ('u0046', 'u0063'): -1,
        ('u0046', 'u0064'): -1,
        ('u0046', 'u0065'): -1,
        ('u0046', 'u0066'): -1,
        ('u0046', 'u0067'): -1,
        ('u0046', 'u0069'): -1,
        ('u0046', 'u006A'): -1,
        ('u0046', 'u006D'): -1,
        ('u0046', 'u006E'): -1,
        ('u0046', 'u006F'): -1,
        ('u0046', 'u0070'): -1,
        ('u0046', 'u0071'): -1,
        ('u0046', 'u0072'): -1,
        ('u0046', 'u0073'): -1,
        ('u0046', 'u0074'): -1,
        ('u0046', 'u0075'): -1,
        ('u0046', 'u0076'): -1,
        ('u0046', 'u0077'): -1,
        ('u0046', 'u0078'): -1,
        ('u0046', 'u0079'): -1,
        ('u0046', 'u007A'): -1,
        ('u004C', 'u0054'): -1,
        ('u004C', 'u0056'): -1,
        ('u004C', 'u0057'): -1,
        ('u004C', 'u0059'): -1,
        ('u004C', 'u0066'): -1,
        ('u004C', 'u006A'): -1,
        ('u004C', 'u006C'): -1,
        ('u004C', 'u0074'): -1,
        ('u004C', 'u0076'): -1,
        ('u004C', 'u0077'): -1,
        ('u004C', 'u0079'): -1,
        ('u0050', 'u002C'): -1,
        ('u0050', 'u002E'): -1,
        ('u0050', 'u0041'): -1,
        ('u0050', 'u0061'): -1,
        ('u0054', 'u002C'): -1,
        ('u0054', 'u002E'): -1,
        ('u0054', 'u0041'): -1,
        ('u0054', 'u0061'): -1,
        ('u0054', 'u0063'): -1,
        ('u0054', 'u0064'): -1,
        ('u0054', 'u0065'): -1,
        ('u0054', 'u0066'): -1,
        ('u0054', 'u0069'): -1,
        ('u0054', 'u006A'): -1,
        ('u0054', 'u006D'): -1,
        ('u0054', 'u006E'): -1,
        ('u0054', 'u006F'): -1,
        ('u0054', 'u0070'): -1,
        ('u0054', 'u0071'): -1,
        ('u0054', 'u0072'): -1,
        ('u0054', 'u0073'): -1,
        ('u0054', 'u0074'): -1,
        ('u0054', 'u0075'): -1,
        ('u0054', 'u0076'): -1,
        ('u0054', 'u0077'): -1,
        ('u0054', 'u0078'): -1,
        ('u0054', 'u0079'): -1,
        ('u0054', 'u007A'): -1,
        ('u0056', 'u002C'): -1,
        ('u0056', 'u002E'): -1,
        ('u0056', 'u0041'): -1,
        ('u0056', 'u0061'): -1,
        ('u0056', 'u0063'): -1,
        ('u0056', 'u0064'): -1,
        ('u0056', 'u0065'): -1,
        ('u0056', 'u0066'): -1,
        ('u0056', 'u0067'): -1,
        ('u0056', 'u0069'): -1,
        ('u0056', 'u006A'): -1,
        ('u0056', 'u006D'): -1,
        ('u0056', 'u006E'): -1,
        ('u0056', 'u006F'): -1,
        ('u0056', 'u0070'): -1,
        ('u0056', 'u0071'): -1,
        ('u0056', 'u0072'): -1,
        ('u0056', 'u0073'): -1,
        ('u0056', 'u0074'): -1,
        ('u0056', 'u0075'): -1,
        ('u0056', 'u0076'): -1,
        ('u0056', 'u0077'): -1,
        ('u0056', 'u0078'): -1,
        ('u0056', 'u0079'): -1,
        ('u0056', 'u007A'): -1,
        ('u0057', 'u002C'): -1,
        ('u0057', 'u002E'): -1,
        ('u0057', 'u0041'): -1,
        ('u0057', 'u0061'): -1,
        ('u0057', 'u0063'): -1,
        ('u0057', 'u0064'): -1,
        ('u0057', 'u0065'): -1,
        ('u0057', 'u0067'): -1,
        ('u0057', 'u006F'): -1,
        ('u0057', 'u0071'): -1,
        ('u0057', 'u0073'): -1,
        ('u0059', 'u002C'): -1,
        ('u0059', 'u002E'): -1,
        ('u0059', 'u0041'): -1,
        ('u0059', 'u0061'): -1,
        ('u0059', 'u0063'): -1,
        ('u0059', 'u0064'): -1,
        ('u0059', 'u0065'): -1,
        ('u0059', 'u0066'): -1,
        ('u0059', 'u0067'): -1,
        ('u0059', 'u0069'): -1,
        ('u0059', 'u006A'): -1,
        ('u0059', 'u006D'): -1,
        ('u0059', 'u006E'): -1,
        ('u0059', 'u006F'): -1,
        ('u0059', 'u0070'): -1,
        ('u0059', 'u0071'): -1,
        ('u0059', 'u0072'): -1,
        ('u0059', 'u0073'): -1,
        ('u0059', 'u0074'): -1,
        ('u0059', 'u0075'): -1,
        ('u0059', 'u0076'): -1,
        ('u0059', 'u0077'): -1,
        ('u0059', 'u0078'): -1,
        ('u0059', 'u0079'): -1,
        ('u0059', 'u007A'): -1,
        ('u005C', 'u005C'): -1,
        ('u0066', 'u002C'): -1,
        ('u0066', 'u002E'): -1,
        ('u0066', 'u0061'): -1,
        ('u0069', 'u006A'): -1,
        ('u006C', 'u006A'): -1,
        ('u0072', 'u002C'): -1,
        ('u0072', 'u002E'): -1,
        ('u0072', 'u0061'): -1,
        ('u0076', 'u002C'): -1,
        ('u0076', 'u002E'): -1,
        ('u0077', 'u002C'): -1,
        ('u0077', 'u002E'): -1,
        ('u0079', 'u002C'): -1,
        ('u0079', 'u002E'): -1,
    }

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
