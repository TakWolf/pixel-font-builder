import logging
import math
import os
import tomllib
from copy import copy

import png

from examples import glyphs_dir, outputs_dir
from pixel_font_builder import FontBuilder, FontCollectionBuilder, Metrics, MetaInfos, Glyph, opentype

logging.basicConfig(level=logging.DEBUG)


def _load_config(file_path: str) -> tuple[Metrics, MetaInfos]:
    with open(file_path, 'rb') as file:
        config_data: dict = tomllib.load(file)['font']

    metrics = Metrics()
    metrics.size = config_data['size']
    metrics.ascent = config_data['ascent']
    metrics.descent = config_data['descent']
    metrics.x_height = config_data['x_height']
    metrics.cap_height = config_data['cap_height']

    meta_infos = MetaInfos()
    meta_infos.version = config_data['version']
    meta_infos.family_name = config_data['family_name']
    meta_infos.style_name = config_data['style_name']
    meta_infos.serif_mode = config_data['serif_mode']
    meta_infos.width_mode = config_data['width_mode']
    meta_infos.manufacturer = config_data['manufacturer']
    meta_infos.designer = config_data['designer']
    meta_infos.description = config_data['description']
    meta_infos.copyright_info = config_data['copyright_info']
    meta_infos.license_info = config_data['license_info']
    meta_infos.vendor_url = config_data['vendor_url']
    meta_infos.designer_url = config_data['designer_url']
    meta_infos.license_url = config_data['license_url']
    meta_infos.sample_text = config_data['sample_text']

    return metrics, meta_infos


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


def _format_glyph_files(root_dir: str):
    for glyph_file_dir, _, glyph_file_names in os.walk(root_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            glyph_data = _load_glyph_data_from_png(glyph_file_path)[0]
            _save_glyph_data_to_png(glyph_data, glyph_file_path)


def _collect_glyph_files(root_dir: str) -> tuple[dict[int, str], list[tuple[str, str]]]:
    registry = {}
    for glyph_file_dir, _, glyph_file_names in os.walk(root_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            if glyph_file_name == 'notdef.png':
                code_point = -1
            else:
                code_point = int(glyph_file_name.removesuffix('.png'), 16)
            registry[code_point] = glyph_file_path

    sequence = list(registry.keys())
    sequence.sort()

    character_mapping = {}
    glyph_file_infos = []
    for code_point in sequence:
        if code_point == -1:
            glyph_name = '.notdef'
        else:
            glyph_name = f'uni{code_point:04X}'
            character_mapping[code_point] = glyph_name
        glyph_file_infos.append((glyph_name, registry[code_point]))

    for code_point in range(ord('A'), ord('Z') + 1):
        fallback_code_point = code_point + ord('Ａ') - ord('A')
        character_mapping[fallback_code_point] = character_mapping[code_point]
    for code_point in range(ord('a'), ord('z') + 1):
        fallback_code_point = code_point + ord('ａ') - ord('a')
        character_mapping[fallback_code_point] = character_mapping[code_point]
    for code_point in range(ord('0'), ord('9') + 1):
        fallback_code_point = code_point + ord('０') - ord('0')
        character_mapping[fallback_code_point] = character_mapping[code_point]

    return character_mapping, glyph_file_infos


def _create_builder(
        metrics: Metrics,
        meta_infos: MetaInfos,
        glyph_cacher: dict[str, Glyph],
        character_mapping: dict[int, str],
        glyph_file_infos: list[tuple[str, str]],
        name_num: int = None,
) -> FontBuilder:
    builder = FontBuilder()

    builder.metrics = metrics

    builder.meta_infos = copy(meta_infos)
    if name_num is not None:
        builder.meta_infos.family_name += f' {name_num}'

    builder.character_mapping.update(character_mapping)

    for glyph_name, glyph_file_path in glyph_file_infos:
        if glyph_file_path in glyph_cacher:
            glyph = glyph_cacher[glyph_file_path]
        else:
            glyph_data, glyph_width, glyph_height = _load_glyph_data_from_png(glyph_file_path)
            offset_y = math.floor((metrics.ascent + metrics.descent - glyph_height) / 2)
            glyph = Glyph(
                name=glyph_name,
                advance_width=glyph_width,
                offset=(0, offset_y),
                data=glyph_data,
            )
            glyph_cacher[glyph_file_path] = glyph
        builder.glyphs.append(glyph)

    return builder


def main():
    metrics, meta_infos = _load_config(os.path.join(glyphs_dir, 'config.toml'))
    _format_glyph_files(glyphs_dir)
    character_mapping, glyph_file_infos = _collect_glyph_files(glyphs_dir)
    glyph_cacher = {}

    builder = _create_builder(metrics, meta_infos, glyph_cacher, character_mapping, glyph_file_infos)
    builder.save_otf(os.path.join(outputs_dir, 'demo.otf'))
    builder.save_otf(os.path.join(outputs_dir, 'demo.woff2'), flavor=opentype.Flavor.WOFF2)
    builder.save_ttf(os.path.join(outputs_dir, 'demo.ttf'))
    builder.save_bdf(os.path.join(outputs_dir, 'demo.bdf'))

    collection_builder = FontCollectionBuilder()
    for index in range(100):
        builder = _create_builder(metrics, meta_infos, glyph_cacher, character_mapping, glyph_file_infos, index)
        builder.opentype_configs.cff_family_name = meta_infos.family_name
        collection_builder.font_builders.append(builder)
    collection_builder.save_otc(os.path.join(outputs_dir, 'demo.otc'))
    collection_builder.save_ttc(os.path.join(outputs_dir, 'demo.ttc'))


if __name__ == '__main__':
    main()
